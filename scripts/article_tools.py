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
    lines.extend(
        [
            "---",
            "",
            f"# {article.title}",
            "",
            article.markdown.strip(),
            "",
        ]
    )
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
    return FetchedArticle(url=url, title=title, markdown=markdown.strip(), method="jina")


class _HTMLArticleParser(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "aside", "form"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False
        self._skip_depth = 0
        self._chunks: list[str] = []
        self._in_pre = False
        self._link_hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._skip_depth or tag in self.SKIP_TAGS:
            if tag in self.SKIP_TAGS:
                self._skip_depth += 1
            return
        attr = dict(attrs)
        if tag == "title":
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
        elif tag == "img" and attr.get("src"):
            alt = attr.get("alt") or ""
            self._chunks.append(f"![{alt}]({attr['src']})")
        elif tag == "a":
            self._link_hrefs.append(attr.get("href") or "")
            self._chunks.append("[")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
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
        if self._skip_depth:
            return
        if self._in_title:
            self.title_parts.append(data)
            return
        text = data if self._in_pre else re.sub(r"[ \t]+", " ", data)
        if text:
            self._chunks.append(text)

    def result(self, page_url: str) -> tuple[str, str]:
        title = re.sub(r"\s+", " ", "".join(self.title_parts)).strip() or slug_from_url(page_url)
        markdown = "".join(self._chunks)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
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
    return FetchedArticle(url=url, title=title, markdown=markdown, method="html")


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
