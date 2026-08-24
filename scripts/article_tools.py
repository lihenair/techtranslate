#!/usr/bin/env python3
"""Extract article URLs, fetch readable source, and write inbox files."""

from __future__ import annotations

import json
import re
import ssl
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import translation_format

USER_AGENT = (
    "Mozilla/5.0 (compatible; techtranslate-bot/1.0; +https://github.com/lihenair/techtranslate)"
)
URL_RE = re.compile(r"https?://[^\s<>\]\)\"'`]+", re.IGNORECASE)
TRAILING_PUNCT_RE = re.compile(r"[),.;:!?。，、；：！？]+$")
UNSAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\u4e00-\u9fff-]+")
LINK_STYLESHEET_RE = re.compile(
    r"<link\b[^>]*rel=[\"'][^\"']*stylesheet[^\"']*[\"'][^>]*>",
    re.I,
)
HREF_RE = re.compile(r"""\bhref=["']([^"']+)["']""", re.I)
CSS_URL_RE = re.compile(r"""url\(\s*(["']?)([^)'"]+)\1\s*\)""", re.I)
CSS_ANIM_PROP_RE = re.compile(r"""(?:^|[;\s"'])animation(?:-[a-z]+)?\s*:""", re.I)
MEDIA_COMMENT_RE = re.compile(r"<!--\s*media:[^>]+-->")
IMAGE_MD_RE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")
MEDIA_CONTAINER_TAGS = {"section", "figure", "div"}
MAX_SECTION_SNIPPET_CHARS = 16_384
MAX_SECTION_STYLE_RATIO = 0.4
ASPECT_RE = re.compile(r"aspect-\[(\d+)/(\d+)\]")
IFRAME_SKIP_HOSTS = (
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "platform.twitter.com",
    "facebook.com",
    "doubleclick.net",
    "googletagmanager.com",
)


class FetchError(RuntimeError):
    pass


@dataclass
class FetchedArticle:
    url: str
    title: str
    markdown: str
    method: str
    author: str | None = None
    published_at: str | None = None
    cover_image: str | None = None
    media_comments: list[str] | None = None
    section_snippets: list[str] | None = None
    title_zh: str | None = None


EMPTY_FORM_VALUES = {
    "",
    "_no response_",
    "no response",
    "无",
    "没有",
    "n/a",
    "none",
}
TITLE_FIELD_NAMES = {"中文标题", "translation title", "article title"}
URL_FIELD_NAMES = {"原文链接", "article url"}
EXTRA_FIELD_NAMES = {"更多文章", "additional urls"}
TRANSLATE_TITLE_RE = re.compile(r"^\[translate\]\s*", re.I)


def _is_empty_form_value(text: str | None) -> bool:
    return (text or "").strip().lower() in EMPTY_FORM_VALUES


def parse_issue_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    parts = re.split(r"^### ", text or "", flags=re.MULTILINE)
    for part in parts[1:]:
        heading, _, rest = part.partition("\n")
        sections[heading.strip()] = rest.strip()
    return sections


def _title_from_issue_title(issue_title: str | None) -> str | None:
    if not issue_title:
        return None
    cleaned = TRANSLATE_TITLE_RE.sub("", issue_title).strip()
    return cleaned or None


def parse_issue_requests(body: str, issue_title: str | None = None) -> list[dict[str, str | None]]:
    """Read URLs and optional Chinese titles from a Translate-article issue."""
    sections = parse_issue_sections(body)
    named = ""
    primary = ""
    extra = ""
    for heading, value in sections.items():
        key = heading.strip().lower()
        if key in TITLE_FIELD_NAMES:
            named = value
        elif key in URL_FIELD_NAMES:
            primary = value
        elif key in EXTRA_FIELD_NAMES:
            extra = value

    requests: list[dict[str, str | None]] = []
    seen: set[str] = set()

    def add_blob(blob: str, default_title: str | None = None) -> None:
        if _is_empty_form_value(blob):
            return
        for raw_line in blob.splitlines():
            line = raw_line.strip()
            if not line or _is_empty_form_value(line):
                continue
            title = default_title
            url_part = line
            if "|" in line:
                left, right = line.split("|", 1)
                url_part = left.strip()
                title = right.strip() or default_title
            found = extract_urls(url_part) or extract_urls(line)
            if not found:
                continue
            url = found[0]
            if url in seen:
                continue
            seen.add(url)
            requests.append({"url": url, "title_zh": title or None})

    add_blob(primary, None if _is_empty_form_value(named) else named.strip())
    add_blob(extra)
    if not requests:
        add_blob(body)

    hint = _title_from_issue_title(issue_title)
    if requests and not requests[0]["title_zh"] and hint:
        requests[0]["title_zh"] = hint
    return requests


def format_translate_issue(
    requests: list[dict[str, str | None]],
    notes: str | None = None,
) -> tuple[str, str]:
    """Build the same GitHub form body Cursor or a human would submit."""
    if not requests:
        raise ValueError("Need at least one article URL")
    first = requests[0]
    first_url = first.get("url") or ""
    first_title = first.get("title_zh") or None
    issue_title = f"[Translate] {first_title or slug_from_url(first_url)}"
    extras: list[str] = []
    for item in requests[1:]:
        url = item.get("url") or ""
        if not url:
            continue
        title = item.get("title_zh")
        extras.append(f"{url} | {title}" if title else url)
    body = "\n".join(
        [
            "### 原文链接",
            "",
            first_url,
            "",
            "### 中文标题",
            "",
            first_title or "_No response_",
            "",
            "### 更多文章",
            "",
            "\n".join(extras) if extras else "_No response_",
            "",
            "### 备注",
            "",
            notes.strip() if notes and not _is_empty_form_value(notes) else "_No response_",
            "",
        ]
    )
    return issue_title, body


def extract_urls(text: str) -> list[str]:
    """Return unique http(s) article URLs, skipping GitHub attachment noise when possible."""
    seen: set[str] = set()
    urls: list[str] = []
    for raw in URL_RE.findall(text or ""):
        url = TRAILING_PUNCT_RE.sub("", raw.rstrip(").,]\"'"))
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        host = parsed.netloc.lower()
        if host in {"user-images.githubusercontent.com", "private-user-images.githubusercontent.com"}:
            continue
        if host.endswith("github.com") and re.search(r"/(issues|pulls?|assets)/", parsed.path):
            continue
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def slug_from_url(url: str, title: str | None = None, max_len: int = 80) -> str:
    source = (title or "").strip() or Path(urlparse(url).path).name or urlparse(url).netloc
    source = re.sub(r"\.(html?|md|markdown)$", "", source, flags=re.IGNORECASE)
    slug = UNSAFE_FILENAME_RE.sub("-", source).strip("-._")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        slug = "article"
    return slug[:max_len].rstrip("-._")


def section_snippet_is_recordable(markup: str, styles: list[str] | None = None) -> bool:
    """Drop X/Twitter page chrome and other bloated HTML before section GIF capture."""
    if len(markup) > MAX_SECTION_SNIPPET_CHARS:
        return False
    style_len = sum(len(block) for block in styles or [])
    style_len += sum(
        len(block)
        for block in re.findall(r"<style[^>]*>.*?</style>", markup, flags=re.I | re.S)
    )
    body_len = len(re.sub(r"<style[^>]*>.*?</style>", "", markup, flags=re.I | re.S))
    # Tiny extracted fragment plus page-wide CSS (common on x.com) is not a real demo.
    if style_len > 8192 and body_len < 512:
        return False
    if body_len > 4096 and style_len > body_len * MAX_SECTION_STYLE_RATIO:
        return False
    return True


def inbox_filename(url: str, title: str | None = None) -> str:
    return f"{slug_from_url(url, title)}.source.md"


def format_media_comment(kind: str, **attrs: str) -> str:
    parts = [f"media:{kind}"]
    for key, value in attrs.items():
        if value:
            parts.append(f'{key}="{value}"')
    return "<!-- " + " ".join(parts) + " -->"


def aspect_viewport(class_name: str, width: int = 800) -> tuple[int, int]:
    match = ASPECT_RE.search(class_name or "")
    if not match:
        return width, int(width * 9 / 16)
    num, den = int(match.group(1)), int(match.group(2))
    if num <= 0 or den <= 0:
        return width, int(width * 9 / 16)
    return width, max(80, int(width * den / num))


def is_article_visual_iframe(src: str, page_url: str | None = None) -> bool:
    if not src or src.startswith(("javascript:", "data:")):
        return False
    if translation_format.youtube_id_from_url(src):
        return False
    if translation_format.twitter_status_from_url(src):
        return False
    host = urlparse(src).netloc.lower()
    if any(skip in host for skip in IFRAME_SKIP_HOSTS):
        return False
    if page_url and host:
        page_host = urlparse(page_url).netloc.lower()
        if page_host and host != page_host:
            return False
    return True


def is_svg_url(src: str) -> bool:
    path = urlparse(src or "").path.lower()
    return path.endswith(".svg")


def _svg_dimension(raw: str | None) -> float | None:
    if not raw:
        return None
    cleaned = re.sub(r"px$", "", raw.strip(), flags=re.I)
    try:
        return float(cleaned)
    except ValueError:
        return None


def is_tiny_svg(attrs: dict[str, str | None]) -> bool:
    width = _svg_dimension(attrs.get("width"))
    height = _svg_dimension(attrs.get("height"))
    return width is not None and height is not None and width <= 48 and height <= 48


def extract_media_comments(markdown: str) -> list[str]:
    return [match.group(0) for match in MEDIA_COMMENT_RE.finditer(markdown or "")]


def image_url_key(url: str) -> str:
    path = urlparse(url or "").path
    name = path.rsplit("/", 1)[-1]
    return re.sub(r":(?:large|orig|small|thumb)$", "", name, flags=re.I)


def markdown_image_urls(text: str) -> list[str]:
    return [match.group(2) for match in IMAGE_MD_RE.finditer(text or "")]


def merge_inline_images(target: str, source: str) -> str:
    """Copy markdown images from source that target is missing, after the matching prior paragraph."""
    if not source:
        return target or ""
    out = target or ""
    existing = {image_url_key(url) for url in markdown_image_urls(out)}
    last = 0
    for match in IMAGE_MD_RE.finditer(source):
        url = match.group(2)
        key = image_url_key(url)
        if not key or key in existing:
            last = match.end()
            continue
        before = source[last : match.start()]
        needle = last_paragraph_needle(before)
        snippet = match.group(0)
        if needle and needle in out:
            at = out.index(needle) + len(needle)
            out = out[:at].rstrip() + "\n\n" + snippet + "\n\n" + out[at:].lstrip()
        else:
            out = out.rstrip() + "\n\n" + snippet + "\n"
        existing.add(key)
        last = match.end()
    return out


def last_paragraph_needle(text: str) -> str:
    cleaned = MEDIA_COMMENT_RE.sub("", text or "")
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", cleaned)
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", cleaned)]
    paragraphs = [part for part in paragraphs if part]
    if not paragraphs:
        return ""
    needle = paragraphs[-1]
    return needle[-80:] if len(needle) > 80 else needle


def place_media_comments(target: str, html_markdown: str) -> str:
    """Put HTML media markers after the matching Jina paragraph when possible."""
    if not html_markdown:
        return target
    comments = extract_media_comments(html_markdown)
    if not comments:
        return target
    pieces = MEDIA_COMMENT_RE.split(html_markdown)
    out = target or ""
    for index, comment in enumerate(comments):
        if comment in out:
            continue
        before = pieces[index] if index < len(pieces) else ""
        needle = last_paragraph_needle(before)
        if needle and needle in out:
            at = out.index(needle) + len(needle)
            out = out[:at].rstrip() + "\n\n" + comment + "\n\n" + out[at:].lstrip()
        else:
            out = out.rstrip() + "\n\n" + comment + "\n"
    return out


def inject_youtube_comments(markdown: str) -> str:
    return inject_media_comments(markdown)


def inject_media_comments(markdown: str) -> str:
    found: list[str] = []
    for raw in URL_RE.findall(markdown):
        video_id = translation_format.youtube_id_from_url(raw)
        if video_id:
            comment = format_media_comment(
                "youtube",
                id=video_id,
                url=translation_format.youtube_watch_url(video_id),
            )
        else:
            continue
        if comment not in markdown and comment not in found:
            found.append(comment)
    if not found:
        return markdown
    return markdown.rstrip() + "\n\n" + "\n".join(found) + "\n"


def format_source_markdown(article: FetchedArticle, issue: str | None = None) -> str:
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f"source_url: {article.url}",
        f"fetched_at: {fetched_at}",
        f"fetch_method: {article.method}",
    ]
    if issue:
        lines.append(f"issue: {issue}")
    if article.author:
        lines.append(f"author: {article.author}")
    if article.published_at:
        lines.append(f"published_at: {article.published_at}")
    if article.cover_image:
        lines.append(f"cover_image: {article.cover_image}")
    if article.title_zh:
        lines.append(f"title_zh: {article.title_zh}")
    lines.append(
        f"tech_domain: {translation_format.classify_tech_domain(article.title, article.markdown)}"
    )
    body = article.markdown.strip()
    extras = [c.strip() for c in (article.media_comments or []) if c.strip()]
    for comment in extras:
        if comment not in body:
            body = f"{body}\n\n{comment}"
    lines.extend(["---", "", f"# {article.title}", "", body, ""])
    return "\n".join(lines)


def already_translated(repo_root: Path, url: str) -> bool:
    needle = url.strip()
    if not needle:
        return False
    paths = [repo_root / "README.md", *repo_root.glob("*.md")]
    archive = repo_root / "archive"
    if archive.is_dir():
        paths.extend(archive.rglob("*.md"))
        paths.extend(archive.rglob("*.html"))
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if needle in text:
            return True
    return False


def _http_get(url: str, timeout: int = 45) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,*/*"})
    context = ssl.create_default_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read()
        final_url = response.geturl()
    try:
        text = raw.decode(charset, errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    return final_url, text


def fetch_via_jina(url: str, timeout: int = 45) -> FetchedArticle:
    _, body = _http_get(f"https://r.jina.ai/{url}", timeout=timeout)
    if not body.strip():
        raise FetchError("Jina reader returned empty content")
    title = ""
    markdown = body
    title_match = re.search(r"^Title:\s*(.+)$", body, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    content_match = re.search(r"Markdown Content:\s*\n", body)
    if content_match:
        markdown = body[content_match.end() :]
    if not title:
        heading = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        title = heading.group(1).strip() if heading else slug_from_url(url)
    if len(markdown.strip()) < 80:
        raise FetchError("Jina reader returned too little article text")
    markdown = inject_youtube_comments(markdown.strip())
    return FetchedArticle(url=url, title=title, markdown=markdown, method="jina")


def _attr_html(attrs: list[tuple[str, str | None]]) -> str:
    parts = []
    for key, value in attrs:
        if value is None:
            parts.append(key)
        else:
            parts.append(f'{key}="{value}"')
    return (" " + " ".join(parts)) if parts else ""


class _HTMLArticleParser(HTMLParser):
    SKIP_TAGS = {"script", "noscript", "svg", "nav", "footer", "header", "aside", "form"}
    SECTION_TAGS = {"section", "figure"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False
        self._in_style = False
        self._skip_depth = 0
        self._chunks: list[str] = []
        self._in_pre = False
        self._link_hrefs: list[str] = []
        self.author: str | None = None
        self.published_at: str | None = None
        self.cover_image: str | None = None
        self.styles: list[str] = []
        self.section_snippets: list[str] = []
        self._style_parts: list[str] = []
        self._pending_video = False
        self._records: list[dict] = []
        self._seen_twitter: set[str] = set()
        self._in_twitter_embed = 0
        self._svg_depth = 0
        self._svg_parts: list[str] = []
        self._svg_attr: dict[str, str | None] = {}

    def _start_record(self, tag: str, attrs: list[tuple[str, str | None]], class_name: str) -> None:
        self._records.append(
            {
                "tag": tag,
                "class_name": class_name,
                "depth": 1,
                "imgs": [],
                "videos": [],
                "parts": [f"<{tag}{_attr_html(attrs)}>"],
            }
        )

    def _append_record(self, text: str) -> None:
        for record in self._records:
            record["parts"].append(text)

    def _finish_record(self, page_url: str | None = None) -> None:
        record = self._records.pop()
        imgs = record["imgs"]
        videos = record["videos"]
        markup = "".join(record["parts"])
        is_anim = translation_format.looks_like_anim_class(record["class_name"])
        has_css_anim = bool(CSS_ANIM_PROP_RE.search(markup)) or "@keyframes" in markup.lower()
        if videos:
            return
        if is_anim and 2 <= len(imgs) <= translation_format.MAX_SEQUENCE_FRAMES:
            self._chunks.append("\n\n" + format_media_comment("frames", src="|".join(imgs)) + "\n")
            return
        if is_anim or has_css_anim:
            if not section_snippet_is_recordable(markup, self.styles):
                return
            style_html = "".join(f"<style>{block}</style>" for block in self.styles)
            snippet = (
                "<!doctype html><html><head><meta charset=\"utf-8\">"
                f"{style_html}</head><body>{markup}</body></html>"
            )
            self.section_snippets.append(snippet)
            self._chunks.append(
                "\n\n"
                + format_media_comment(
                    "section-anim",
                    index=str(len(self.section_snippets)),
                    duration_s="4",
                )
                + "\n"
            )

    def _finish_svg(self) -> None:
        if is_tiny_svg(self._svg_attr):
            return
        markup = "".join(self._svg_parts)
        if "<svg" not in markup.lower():
            return
        if not section_snippet_is_recordable(markup, self.styles):
            return
        style_html = "".join(f"<style>{block}</style>" for block in self.styles)
        snippet = (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            f"{style_html}</head><body>{markup}</body></html>"
        )
        self.section_snippets.append(snippet)
        self._chunks.append(
            "\n\n"
            + format_media_comment(
                "section-anim",
                index=str(len(self.section_snippets)),
                duration_s="4",
            )
            + "\n"
        )

    def _emit_page_visual(self, src: str, class_name: str) -> None:
        if not is_article_visual_iframe(src):
            return
        width, height = aspect_viewport(class_name)
        fragment = urlparse(src).fragment
        attrs = {"url": src, "duration_s": "4", "width": str(width), "height": str(height)}
        if fragment:
            attrs["id"] = fragment
        self._chunks.append("\n\n" + format_media_comment("page-visual", **attrs) + "\n")

    def _emit_twitter(self, url: str) -> None:
        status_id = translation_format.twitter_status_from_url(url)
        if not status_id or status_id in self._seen_twitter:
            return
        self._seen_twitter.add(status_id)
        self._chunks.append(
            "\n\n"
            + format_media_comment(
                "twitter",
                id=status_id,
                url=translation_format.twitter_status_url(status_id),
            )
            + "\n"
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._svg_depth:
            self._svg_parts.append(f"<{tag}{_attr_html(attrs)}>")
            if tag == "svg":
                self._svg_depth += 1
            return
        if tag == "svg":
            self._svg_depth = 1
            self._svg_attr = dict(attrs)
            self._svg_parts = [f"<svg{_attr_html(attrs)}>"]
            return
        if tag == "style":
            self._in_style = True
            self._style_parts = []
            return
        if translation_format.looks_like_twitter_class(dict(attrs).get("class") or ""):
            self._in_twitter_embed += 1
        if self._skip_depth or tag in self.SKIP_TAGS:
            if tag in self.SKIP_TAGS:
                self._skip_depth += 1
            return
        attr = dict(attrs)
        class_name = attr.get("class") or ""
        if tag in MEDIA_CONTAINER_TAGS and translation_format.looks_like_anim_class(class_name):
            self._start_record(tag, attrs, class_name)
            return
        start_html = f"<{tag}{_attr_html(attrs)}>"
        if self._records:
            self._append_record(start_html)
            if tag == self._records[-1]["tag"]:
                self._records[-1]["depth"] += 1

        if tag == "meta":
            name = (attr.get("property") or attr.get("name") or "").lower()
            content = (attr.get("content") or "").strip()
            if content and name in {"og:image", "twitter:image"} and not self.cover_image:
                self.cover_image = content
            if content and name in {"author", "article:author", "citation_author"} and not self.author:
                self.author = content.split(",")[0].strip()
            if content and name in {"article:published_time", "article:published", "date", "publish-date"}:
                if not self.published_at:
                    self.published_at = content[:10]
            return
        if tag == "iframe":
            src = attr.get("src") or ""
            video_id = translation_format.youtube_id_from_url(src)
            if video_id:
                self._chunks.append(
                    "\n\n"
                    + format_media_comment(
                        "youtube",
                        id=video_id,
                        url=translation_format.youtube_watch_url(video_id),
                    )
                    + "\n"
                )
            elif is_article_visual_iframe(src):
                self._emit_page_visual(src, class_name)
            else:
                self._emit_twitter(src)
            return
        if tag == "video":
            src = attr.get("src") or ""
            if src:
                self._chunks.append("\n\n" + format_media_comment("video-gif", src=src) + "\n")
                if self._records:
                    self._records[-1]["videos"].append(src)
            else:
                self._pending_video = True
            return
        if tag == "source" and self._pending_video and attr.get("src"):
            src = attr.get("src") or ""
            self._chunks.append("\n\n" + format_media_comment("video-gif", src=src) + "\n")
            if self._records:
                self._records[-1]["videos"].append(src)
            self._pending_video = False
            return
        if tag == "img" and attr.get("src"):
            src = attr.get("src") or ""
            if self._records:
                self._records[-1]["imgs"].append(src)
            alt = attr.get("alt") or ""
            self._chunks.append(f"![{alt}]({src})")
            if is_svg_url(src):
                self._chunks.append("\n\n" + format_media_comment("svg", src=src) + "\n")
        elif tag == "title":
            self._in_title = True
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._chunks.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "p":
            self._chunks.append("\n\n")
        elif tag in {"br", "hr"}:
            self._chunks.append("\n")
        elif tag in {"li"}:
            self._chunks.append("\n- ")
        elif tag == "pre":
            self._in_pre = True
            self._chunks.append("\n\n```\n")
        elif tag == "code" and not self._in_pre:
            self._chunks.append("`")
        elif tag == "a":
            href = attr.get("href") or ""
            self._link_hrefs.append(href)
            if self._in_twitter_embed:
                self._emit_twitter(href)
            self._chunks.append("[")

    def handle_endtag(self, tag: str) -> None:
        if self._svg_depth:
            self._svg_parts.append(f"</{tag}>")
            if tag == "svg":
                self._svg_depth -= 1
                if self._svg_depth == 0:
                    self._finish_svg()
            return
        if tag == "style":
            self._in_style = False
            text = "".join(self._style_parts).strip()
            if text:
                self.styles.append(text)
            self._style_parts = []
            return
        if self._in_twitter_embed and tag in {"blockquote", "div", "figure", "section"}:
            self._in_twitter_embed = max(0, self._in_twitter_embed - 1)
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "video":
            self._pending_video = False
        if self._records:
            self._append_record(f"</{tag}>")
            if tag == self._records[-1]["tag"]:
                self._records[-1]["depth"] -= 1
                if self._records[-1]["depth"] <= 0:
                    self._finish_record()
                    return
        if tag == "title":
            self._in_title = False
        elif tag == "pre":
            self._in_pre = False
            self._chunks.append("\n```\n")
        elif tag == "code" and not self._in_pre:
            self._chunks.append("`")
        elif tag == "a" and self._link_hrefs:
            href = self._link_hrefs.pop()
            self._chunks.append(f"]({href})")

    def handle_data(self, data: str) -> None:
        if self._svg_depth:
            self._svg_parts.append(data)
            return
        if self._in_style:
            self._style_parts.append(data)
            return
        if self._skip_depth:
            return
        if self._in_title:
            self.title_parts.append(data)
            return
        if self._records:
            self._append_record(data)
        text = data if self._in_pre else re.sub(r"[ \t]+", " ", data)
        if text:
            self._chunks.append(text)

    def result(self, page_url: str) -> tuple[str, str]:
        while self._records:
            self._finish_record(page_url)
        title = re.sub(r"\s+", " ", "".join(self.title_parts)).strip() or slug_from_url(page_url)
        markdown = "".join(self._chunks)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

        markdown = re.sub(
            r"(!\[[^\]]*\]\()(?!https?://)([^)]+)\)",
            lambda m: f"{m.group(1)}{urljoin(page_url, m.group(2))})",
            markdown,
        )

        def abs_src_list(match: re.Match[str]) -> str:
            urls = []
            for raw in match.group(2).split("|"):
                raw = raw.strip()
                if raw.startswith(("http://", "https://", "file:")):
                    urls.append(raw)
                else:
                    urls.append(urljoin(page_url, raw))
            return f"{match.group(1)}{'|'.join(urls)}{match.group(3)}"

        markdown = re.sub(r'(<!-- media:(?:frames|video-gif|svg) src=")([^"]+)(" -->)', abs_src_list, markdown)

        def rewrite_page_visual(match: re.Match[str]) -> str:
            comment = match.group(0)
            url_match = re.search(r'url="([^"]+)"', comment)
            if not url_match:
                return ""
            abs_url = urljoin(page_url, url_match.group(1))
            if not is_article_visual_iframe(abs_url, page_url):
                return ""
            return comment.replace(url_match.group(1), abs_url, 1)

        markdown = re.sub(r"<!-- media:page-visual[^>]+-->", rewrite_page_visual, markdown)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
        self.cover_image = (
            urljoin(page_url, self.cover_image)
            if self.cover_image and not self.cover_image.startswith(("http://", "https://"))
            else self.cover_image
        )
        return title, markdown


def rewrite_css_urls(css: str, base_url: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = (match.group(2) or "").strip()
        if not raw or raw.startswith(("data:", "http://", "https://")):
            return match.group(0)
        if raw.startswith("//"):
            return f'url("{urlparse(base_url).scheme}:{raw}")'
        return f'url("{urljoin(base_url, raw)}")'

    return CSS_URL_RE.sub(repl, css or "")


def inline_linked_stylesheets(
    page_url: str,
    html: str,
    getter=None,
    max_sheets: int = 8,
) -> str:
    get = getter or (lambda url, timeout=45: _http_get(url, timeout=timeout))
    injected: list[str] = []
    for match in LINK_STYLESHEET_RE.finditer(html or ""):
        href_match = HREF_RE.search(match.group(0))
        if not href_match:
            continue
        href = href_match.group(1)
        if href.startswith("data:"):
            continue
        abs_url = urljoin(page_url, href)
        try:
            final, css = get(abs_url)
        except (FetchError, HTTPError, URLError, TimeoutError, ssl.SSLError, OSError, ValueError):
            continue
        if not css or len(css) > 800_000:
            continue
        css = rewrite_css_urls(css, final or abs_url)
        injected.append(f"<style>{css}</style>")
        if len(injected) >= max_sheets:
            break
    if not injected:
        return html
    extra = "".join(injected)
    if re.search(r"</head>", html, re.I):
        return re.sub(r"</head>", lambda _: extra + "</head>", html, count=1, flags=re.I)
    return extra + html


def merge_html_enrichment(article: FetchedArticle, html_article: FetchedArticle) -> FetchedArticle:
    """Keep Jina readable text; copy HTML media markers, snippets, and missing meta."""
    comments = list(article.media_comments or [])
    existing = set(comments)
    existing.update(extract_media_comments(article.markdown or ""))
    for comment in extract_media_comments(html_article.markdown or ""):
        if comment not in existing:
            comments.append(comment)
            existing.add(comment)
    for comment in html_article.media_comments or []:
        if comment not in existing:
            comments.append(comment)
            existing.add(comment)
    article.media_comments = comments or None
    article.markdown = place_media_comments(article.markdown or "", html_article.markdown or "")
    article.markdown = merge_inline_images(article.markdown or "", html_article.markdown or "")
    if html_article.section_snippets and not article.section_snippets:
        article.section_snippets = list(html_article.section_snippets)
    if not article.author:
        article.author = html_article.author
    if not article.published_at:
        article.published_at = html_article.published_at
    if not article.cover_image:
        article.cover_image = html_article.cover_image
    return article


def fetch_via_html(url: str, timeout: int = 45) -> FetchedArticle:
    final_url, html = _http_get(url, timeout=timeout)
    html = inline_linked_stylesheets(final_url, html)
    parser = _HTMLArticleParser()
    parser.feed(html)
    title, markdown = parser.result(final_url)
    if len(markdown) < 80:
        raise FetchError("Direct HTML extract returned too little article text")
    # Rewrite relative images if possible.
    markdown = re.sub(
        r"!\[([^\]]*)\]\((?!https?://)([^)]+)\)",
        lambda m: f"![{m.group(1)}]({urljoin(final_url, m.group(2))})",
        markdown,
    )
    markdown = inject_youtube_comments(markdown)
    return FetchedArticle(
        url=url,
        title=title,
        markdown=markdown,
        method="html",
        author=parser.author,
        published_at=parser.published_at,
        cover_image=parser.cover_image,
        section_snippets=parser.section_snippets or None,
    )


def fetch_article(url: str, timeout: int = 45) -> FetchedArticle:
    errors: list[str] = []
    jina_article: FetchedArticle | None = None
    html_article: FetchedArticle | None = None
    try:
        jina_article = fetch_via_jina(url, timeout=timeout)
    except (FetchError, HTTPError, URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        errors.append(f"fetch_via_jina: {exc}")
    try:
        html_article = fetch_via_html(url, timeout=timeout)
    except (FetchError, HTTPError, URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        errors.append(f"fetch_via_html: {exc}")
    if jina_article and html_article:
        merged = merge_html_enrichment(jina_article, html_article)
        merged.markdown = merge_inline_images(merged.markdown or "", jina_article.markdown or "")
        return merged
    if jina_article:
        return jina_article
    if html_article:
        return html_article
    raise FetchError("All fetch methods failed: " + " | ".join(errors))


def write_inbox(article: FetchedArticle, outdir: Path, issue: str | None = None) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    slug = slug_from_url(article.url, article.title)
    for index, snippet in enumerate(article.section_snippets or [], start=1):
        snippet_path = outdir / "media" / f"{slug}-{index}.html"
        snippet_path.parent.mkdir(parents=True, exist_ok=True)
        snippet_path.write_text(snippet, encoding="utf-8")
    path = outdir / inbox_filename(article.url, article.title)
    path.write_text(format_source_markdown(article, issue=issue), encoding="utf-8")
    return path


def inbox_git_add_paths(repo_root: Path) -> list[str]:
    """Paths the queue Action may commit. Skip missing dirs so git add does not fail."""
    paths: list[str] = []
    for name in ("_inbox", "assets"):
        if (repo_root / name).exists():
            paths.append(name)
    return paths


def stage_inbox_paths(repo_root: Path) -> list[str]:
    paths = inbox_git_add_paths(repo_root)
    if paths:
        subprocess.run(["git", "add", "--", *paths], cwd=repo_root, check=True)
    return paths


def prepare_inbox(
    body: str,
    outdir: Path,
    repo_root: Path,
    issue: str | None = None,
    urls: Iterable[str] | None = None,
    issue_title: str | None = None,
) -> dict:
    requests = parse_issue_requests(body, issue_title=issue_title)
    for extra in urls or []:
        extra = extra.strip()
        if extra and extra not in {item["url"] for item in requests}:
            requests.append({"url": extra, "title_zh": None})
    found = [item["url"] for item in requests if item.get("url")]
    results: dict = {"urls": found, "files": [], "skipped": [], "errors": []}
    if not found:
        results["errors"].append("No http(s) article URLs found.")
        return results

    for item in requests:
        url = item["url"]
        if already_translated(repo_root, url):
            results["skipped"].append({"url": url, "reason": "already present in repo markdown"})
            continue
        try:
            article = fetch_article(url)
            article.title_zh = item.get("title_zh")
            path = write_inbox(article, outdir, issue=issue)
            results["files"].append(
                {
                    "url": url,
                    "title": article.title,
                    "title_zh": article.title_zh,
                    "path": str(path.relative_to(repo_root)),
                    "method": article.method,
                    "tech_domain": translation_format.classify_tech_domain(
                        article.title, article.markdown
                    ),
                }
            )
            # Be polite when fetching several articles in one issue.
            time.sleep(0.4)
        except Exception as exc:  # noqa: BLE001 - surface every fetch failure to the Action
            results["errors"].append(f"{url}: {exc}")
    return results


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Prepare translation inbox files from URLs")
    parser.add_argument("--body-file", help="Issue body or notes containing URLs")
    parser.add_argument("--url", action="append", default=[], help="Explicit article URL (repeatable)")
    parser.add_argument("--outdir", default="_inbox")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--issue")
    parser.add_argument("--issue-title")
    parser.add_argument(
        "--stage-inbox",
        action="store_true",
        help="git add _inbox and assets only when those paths exist",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if args.stage_inbox:
        stage_inbox_paths(repo_root)
        return 0
    outdir = (repo_root / args.outdir).resolve()
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else ""
    result = prepare_inbox(
        body,
        outdir,
        repo_root,
        issue=args.issue,
        urls=args.url,
        issue_title=args.issue_title,
    )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if result["errors"] and not result["files"]:
        return 1
    if not result["files"] and not result["skipped"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
