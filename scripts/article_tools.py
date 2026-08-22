#!/usr/bin/env python3
"""Extract article URLs, fetch readable source, and write inbox files."""

from __future__ import annotations

import json
import re
import ssl
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


def inbox_filename(url: str, title: str | None = None) -> str:
    return f"{slug_from_url(url, title)}.source.md"


def format_media_comment(kind: str, **attrs: str) -> str:
    parts = [f"media:{kind}"]
    for key, value in attrs.items():
        if value:
            parts.append(f'{key}="{value}"')
    return "<!-- " + " ".join(parts) + " -->"


def inject_youtube_comments(markdown: str) -> str:
    found: list[str] = []
    for raw in URL_RE.findall(markdown):
        video_id = translation_format.youtube_id_from_url(raw)
        if not video_id:
            continue
        comment = format_media_comment(
            "youtube",
            id=video_id,
            url=translation_format.youtube_watch_url(video_id),
        )
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
    for path in [repo_root / "README.md", *repo_root.glob("*.md")]:
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
        has_css_anim = "animation" in markup.lower()
        if 2 <= len(imgs) <= translation_format.MAX_SEQUENCE_FRAMES:
            self._chunks.append("\n\n" + format_media_comment("frames", src="|".join(imgs)) + "\n")
            return
        if videos:
            return
        if is_anim or has_css_anim:
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "style":
            self._in_style = True
            self._style_parts = []
            return
        if self._skip_depth or tag in self.SKIP_TAGS:
            if tag in self.SKIP_TAGS:
                self._skip_depth += 1
            return
        attr = dict(attrs)
        class_name = attr.get("class") or ""
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
            video_id = translation_format.youtube_id_from_url(attr.get("src") or "")
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
        elif not self._records and (
            tag in self.SECTION_TAGS or (tag == "div" and translation_format.looks_like_anim_class(class_name))
        ):
            self._start_record(tag, attrs, class_name)
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
            self._link_hrefs.append(attr.get("href") or "")
            self._chunks.append("[")

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False
            text = "".join(self._style_parts).strip()
            if text:
                self.styles.append(text)
            self._style_parts = []
            return
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

        markdown = re.sub(r'(<!-- media:(?:frames|video-gif) src=")([^"]+)(" -->)', abs_src_list, markdown)
        self.cover_image = (
            urljoin(page_url, self.cover_image)
            if self.cover_image and not self.cover_image.startswith(("http://", "https://"))
            else self.cover_image
        )
        return title, markdown


def fetch_via_html(url: str, timeout: int = 45) -> FetchedArticle:
    final_url, html = _http_get(url, timeout=timeout)
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
    for fetcher in (fetch_via_jina, fetch_via_html):
        try:
            return fetcher(url, timeout=timeout)
        except (FetchError, HTTPError, URLError, TimeoutError, ssl.SSLError, OSError) as exc:
            errors.append(f"{fetcher.__name__}: {exc}")
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


def prepare_inbox(
    body: str,
    outdir: Path,
    repo_root: Path,
    issue: str | None = None,
    urls: Iterable[str] | None = None,
) -> dict:
    found = extract_urls(body)
    for extra in urls or []:
        extra = extra.strip()
        if extra and extra not in found:
            found.append(extra)
    results: dict = {"urls": found, "files": [], "skipped": [], "errors": []}
    if not found:
        results["errors"].append("No http(s) article URLs found.")
        return results

    for url in found:
        if already_translated(repo_root, url):
            results["skipped"].append({"url": url, "reason": "already present in repo markdown"})
            continue
        try:
            article = fetch_article(url)
            path = write_inbox(article, outdir, issue=issue)
            results["files"].append(
                {
                    "url": url,
                    "title": article.title,
                    "path": str(path.relative_to(repo_root)),
                    "method": article.method,
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
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    outdir = (repo_root / args.outdir).resolve()
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else ""
    result = prepare_inbox(body, outdir, repo_root, issue=args.issue, urls=args.url)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if result["errors"] and not result["files"]:
        return 1
    if not result["files"] and not result["skipped"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
