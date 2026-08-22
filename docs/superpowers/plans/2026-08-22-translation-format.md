# Translation Format And 15s GIF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** New translations match the Juejin sample (YAML meta + body header + heading anchors), and only source clips ≤15 seconds become GIFs under `assets/<slug>/`.

**Architecture:** Pure format helpers live in `scripts/translation_format.py`. Fetch still goes through `scripts/article_tools.py`, which now writes optional inbox meta and HTML comment media markers. `scripts/capture_media.py` reads those markers, applies the 15-second gate, and runs ffmpeg. Agents follow an updated skill; no old posts are rewritten.

**Tech Stack:** Python 3 stdlib (`unittest`, `html.parser`), `ffmpeg` / `ffprobe` on PATH, optional `yt-dlp` for YouTube duration only.

## Global Constraints

- GitHub filename and H1 must not contain `【翻译】`.
- Frontmatter fields are only: `title`, `title_en`, `source_url`, `author`, `published_at`, `translated_at`, `tech_domain`, `tags`, `cover_image`.
- `tech_domain` is one of: `android`, `frontend`, `backend`, `security`, `mobile`, `devops`, `other`.
- Source media with duration `> 15` seconds or unknown duration is not converted (no frames, no first-15-seconds clip).
- Do not commit `mp4` files. Do not write `iframe` tags. Do not write Juejin signed image hosts (`p9-xtjj-sign`, `link.juejin.cn`).
- Do not migrate existing root `*.md` translations.
- Missing `ffmpeg` skips conversion and must not fail the inbox fetch.

## File map

| File | Responsibility |
| --- | --- |
| `scripts/translation_format.py` | Constants, YouTube id/url, embed link text, heading markdown, duration gate, translation validator |
| `scripts/article_tools.py` | Inbox YAML extras + HTML/Jina media markers |
| `scripts/capture_media.py` | Read markers, probe duration, encode GIF, write `assets/<slug>/` |
| `tests/test_translation_format.py` | Format helper tests |
| `tests/test_article_tools.py` | Inbox meta + parser marker tests |
| `tests/test_capture_media.py` | 15s gate + ffmpeg GIF tests |
| `.github/skills/translating-articles/SKILL.md` | Agent-facing output template |
| `.github/agents/article-translator.agent.md` | Point at new format and `assets/` |
| `docs/translating-articles.md`, `AGENTS.md`, `.github/copilot-instructions.md` | Human/agent docs |
| `.github/workflows/article-tools.yml` | Run all new unit tests |
| `.github/workflows/translate-article.yml` | Run capture after fetch; commit `assets/` |

---

### Task 1: Format helpers and duration gate

**Files:**
- Create: `scripts/translation_format.py`
- Test: `tests/test_translation_format.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `TECH_DOMAINS: frozenset[str]`
  - `MAX_SOURCE_SECONDS: float` = `15.0`
  - `MAX_GIF_BYTES: int` = `1500000`
  - `MAX_MEDIA_FILES: int` = `8`
  - `MAX_SEQUENCE_FRAMES: int` = `120`
  - `youtube_id_from_url(url: str) -> str | None`
  - `youtube_watch_url(video_id: str) -> str`
  - `embed_link(platform: str, url: str) -> str`
  - `heading_md(level: int, title_zh: str, slug: str) -> str`
  - `should_convert_source(duration_s: float | None) -> bool`
  - `validate_translation(markdown: str) -> list[str]`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_translation_format.py`:

```python
#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import translation_format as tf  # noqa: E402


SAMPLE = """---
title: "CSS：收件箱里的炸弹"
title_en: "CSS: the bomb inside your inbox"
source_url: https://portswigger.net/research/css-the-bomb-inside-your-inbox
author: Gareth Heyes
published_at: 2026-08-06
translated_at: 2026-08-22
tech_domain: security
tags: [security, web, frontend]
cover_image: https://portswigger.net/cms/images/97/ed/a919-twittercard-article.png
---

# CSS：收件箱里的炸弹

原文链接：<https://portswigger.net/research/css-the-bomb-inside-your-inbox>

原文作者：Gareth Heyes

**导语。**

## [引言](#introduction)
"""


class YoutubeAndLinksTest(unittest.TestCase):
    def test_parses_watch_and_embed_urls(self) -> None:
        self.assertEqual(
            tf.youtube_id_from_url("https://www.youtube.com/watch?v=fG8xWTHnlLY&rel=0"),
            "fG8xWTHnlLY",
        )
        self.assertEqual(
            tf.youtube_id_from_url("https://www.youtube.com/embed/fG8xWTHnlLY?origin=x"),
            "fG8xWTHnlLY",
        )
        self.assertEqual(
            tf.youtube_id_from_url("https://youtu.be/fG8xWTHnlLY"),
            "fG8xWTHnlLY",
        )
        self.assertIsNone(tf.youtube_id_from_url("https://example.com/video"))

    def test_embed_link_and_heading(self) -> None:
        self.assertEqual(
            tf.embed_link("YouTube", "https://www.youtube.com/watch?v=fG8xWTHnlLY"),
            "[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=fG8xWTHnlLY)",
        )
        self.assertEqual(
            tf.heading_md(2, "引言", "introduction"),
            "## [引言](#introduction)",
        )


class DurationGateTest(unittest.TestCase):
    def test_converts_only_known_short_clips(self) -> None:
        self.assertTrue(tf.should_convert_source(0.5))
        self.assertTrue(tf.should_convert_source(15.0))
        self.assertFalse(tf.should_convert_source(15.01))
        self.assertFalse(tf.should_convert_source(None))


class ValidateTranslationTest(unittest.TestCase):
    def test_sample_passes(self) -> None:
        self.assertEqual(tf.validate_translation(SAMPLE), [])

    def test_rejects_old_link_style_and_prefix(self) -> None:
        bad = SAMPLE.replace(
            "原文链接：<https://portswigger.net/research/css-the-bomb-inside-your-inbox>",
            "[原文链接](https://portswigger.net/research/css-the-bomb-inside-your-inbox)",
        )
        errors = tf.validate_translation(bad)
        self.assertTrue(any("原文链接" in e for e in errors))

        prefixed = SAMPLE.replace('title: "CSS：收件箱里的炸弹"', 'title: "【翻译】CSS：收件箱里的炸弹"')
        prefixed = prefixed.replace("# CSS：收件箱里的炸弹", "# 【翻译】CSS：收件箱里的炸弹")
        errors = tf.validate_translation(prefixed)
        self.assertTrue(any("【翻译】" in e for e in errors))

    def test_rejects_iframe_and_juejin_hosts(self) -> None:
        dirty = SAMPLE + "\n<iframe src=\"https://www.youtube.com/embed/x\"></iframe>\n"
        errors = tf.validate_translation(dirty)
        self.assertTrue(any("iframe" in e for e in errors))
        dirty = SAMPLE + "\n![](https://p9-xtjj-sign.byteimg.com/x)\n"
        errors = tf.validate_translation(dirty)
        self.assertTrue(any("juejin" in e.lower() or "xtjj" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_translation_format -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'translation_format'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/translation_format.py`:

```python
#!/usr/bin/env python3
"""Shared translation-format constants and checks."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

TECH_DOMAINS = frozenset(
    {"android", "frontend", "backend", "security", "mobile", "devops", "other"}
)
MAX_SOURCE_SECONDS = 15.0
MAX_GIF_BYTES = 1_500_000
MAX_MEDIA_FILES = 8
MAX_SEQUENCE_FRAMES = 120
REQUIRED_FRONTMATTER = (
    "title",
    "title_en",
    "source_url",
    "translated_at",
    "tech_domain",
    "tags",
)
YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def youtube_id_from_url(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if host in {"youtu.be", "www.youtu.be"}:
        candidate = parsed.path.lstrip("/").split("/")[0]
    elif "youtube.com" in host:
        if parsed.path.startswith("/embed/") or parsed.path.startswith("/shorts/"):
            candidate = parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else ""
        else:
            candidate = parse_qs(parsed.query).get("v", [""])[0]
    else:
        return None
    candidate = candidate.split("?")[0]
    return candidate if YOUTUBE_ID_RE.match(candidate) else None


def youtube_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def embed_link(platform: str, url: str) -> str:
    return f"[嵌入内容（原站 {platform}）]({url})"


def heading_md(level: int, title_zh: str, slug: str) -> str:
    hashes = "#" * max(1, min(level, 6))
    return f"{hashes} [{title_zh}](#{slug})"


def should_convert_source(duration_s: float | None) -> bool:
    if duration_s is None:
        return False
    return duration_s <= MAX_SOURCE_SECONDS


def _parse_simple_yaml(block: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in block.splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_translation(markdown: str) -> list[str]:
    errors: list[str] = []
    match = FRONTMATTER_RE.match(markdown)
    if not match:
        return ["missing YAML frontmatter"]
    meta = _parse_simple_yaml(match.group(1))
    for key in REQUIRED_FRONTMATTER:
        if not meta.get(key):
            errors.append(f"missing frontmatter field {key}")
    title = meta.get("title", "")
    if "【翻译】" in title:
        errors.append("title must not contain 【翻译】")
    domain = meta.get("tech_domain", "")
    if domain and domain not in TECH_DOMAINS:
        errors.append(f"invalid tech_domain {domain}")
    body = markdown[match.end() :]
    h1 = re.search(r"^# (.+)$", body, re.MULTILINE)
    if not h1:
        errors.append("missing H1")
    else:
        if h1.group(1).strip() != title:
            errors.append("H1 must match title")
        if "【翻译】" in h1.group(1):
            errors.append("H1 must not contain 【翻译】")
    if not re.search(r"^原文链接：<https?://[^>]+>$", body, re.MULTILINE):
        errors.append("missing 原文链接：<URL> line")
    if "<iframe" in markdown.lower():
        errors.append("iframe is not allowed")
    if "p9-xtjj-sign" in markdown or "link.juejin.cn" in markdown:
        errors.append("juejin signed or redirect host is not allowed")
    return errors
```

- [ ] **Step 4: Run tests and make sure they pass**

Run: `python3 -m unittest tests.test_translation_format -v`

Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/translation_format.py tests/test_translation_format.py
git commit -m "feat: add translation format helpers and 15s gate"
```

---

### Task 2: Inbox frontmatter extras

**Files:**
- Modify: `scripts/article_tools.py` (`FetchedArticle`, `format_source_markdown`)
- Test: `tests/test_article_tools.py`

**Interfaces:**
- Consumes: none from Task 1
- Produces: `FetchedArticle` fields `author: str | None`, `published_at: str | None`, `cover_image: str | None`, `media_comments: list[str]`. `format_source_markdown` writes those YAML keys when set.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_article_tools.py` inside `InboxFormatTest`:

```python
    def test_source_markdown_writes_optional_meta(self) -> None:
        article = article_tools.FetchedArticle(
            url="https://example.com/a",
            title="Hello Compose",
            markdown="Body text here.",
            method="html",
            author="Ada",
            published_at="2026-01-02",
            cover_image="https://example.com/cover.png",
        )
        text = article_tools.format_source_markdown(article, issue="12")
        self.assertIn("author: Ada", text)
        self.assertIn("published_at: 2026-01-02", text)
        self.assertIn("cover_image: https://example.com/cover.png", text)

    def test_source_markdown_omits_empty_optional_meta(self) -> None:
        article = article_tools.FetchedArticle(
            url="https://example.com/a",
            title="Hello Compose",
            markdown="Body text here.",
            method="jina",
        )
        text = article_tools.format_source_markdown(article)
        self.assertNotIn("\nauthor:", text)
        self.assertNotIn("published_at:", text)
        self.assertNotIn("cover_image:", text)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_article_tools.InboxFormatTest.test_source_markdown_writes_optional_meta -v`

Expected: FAIL with `TypeError: FetchedArticle.__init__() got an unexpected keyword argument 'author'`

- [ ] **Step 3: Write minimal implementation**

In `scripts/article_tools.py`, change `FetchedArticle` to:

```python
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
```

Replace `format_source_markdown` with:

```python
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
```

- [ ] **Step 4: Run tests and make sure they pass**

Run: `python3 -m unittest tests.test_article_tools -v`

Expected: PASS (old tests still pass; new optional-meta tests pass)

- [ ] **Step 5: Commit**

```bash
git add scripts/article_tools.py tests/test_article_tools.py
git commit -m "feat: write author date and cover into inbox source"
```

---

### Task 3: Extract YouTube, video, and page meta from HTML

**Files:**
- Modify: `scripts/article_tools.py` (`_HTMLArticleParser`, `fetch_via_html`, `fetch_via_jina`)
- Test: `tests/test_article_tools.py`

**Interfaces:**
- Consumes: `translation_format.youtube_id_from_url`, `translation_format.youtube_watch_url`
- Produces:
  - `format_media_comment(kind: str, **attrs: str) -> str`
  - parser fills `author`, `published_at`, `cover_image`, `media_comments`
  - Jina markdown also gains YouTube comments via `inject_youtube_comments(markdown: str) -> str`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_article_tools.py`:

```python
class MediaExtractTest(unittest.TestCase):
    def test_html_parser_emits_youtube_and_video_comments(self) -> None:
        html = """<html><head>
        <title>Demo</title>
        <meta property="og:image" content="https://example.com/og.png">
        <meta name="author" content="Ada">
        <meta property="article:published_time" content="2026-03-04T10:00:00Z">
        </head><body>
        <h1>Demo</h1>
        <p class="youtube-wrapper"><iframe src="https://www.youtube.com/embed/fG8xWTHnlLY?rel=0"></iframe></p>
        <section><video autoplay loop muted playsinline src="https://example.com/loop.webm"></video></section>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        title, markdown = parser.result("https://example.com/a")
        self.assertEqual(title, "Demo")
        self.assertEqual(parser.author, "Ada")
        self.assertEqual(parser.published_at, "2026-03-04")
        self.assertEqual(parser.cover_image, "https://example.com/og.png")
        self.assertIn(
            '<!-- media:youtube id="fG8xWTHnlLY" url="https://www.youtube.com/watch?v=fG8xWTHnlLY" -->',
            markdown,
        )
        self.assertIn(
            '<!-- media:video-gif src="https://example.com/loop.webm" -->',
            markdown,
        )

    def test_inject_youtube_comments_from_jina_text(self) -> None:
        text = "Watch https://www.youtube.com/watch?v=fG8xWTHnlLY now"
        out = article_tools.inject_youtube_comments(text)
        self.assertIn(
            '<!-- media:youtube id="fG8xWTHnlLY" url="https://www.youtube.com/watch?v=fG8xWTHnlLY" -->',
            out,
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_article_tools.MediaExtractTest -v`

Expected: FAIL with `AttributeError: 'article_tools' object has no attribute 'inject_youtube_comments'` (or parser has no `author`)

- [ ] **Step 3: Write minimal implementation**

At the top of `scripts/article_tools.py` add:

```python
import translation_format
```

Add these functions (above the parser class). Use the existing `URL_RE` in `article_tools.py`.

```python
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
```

Change `_HTMLArticleParser.__init__` to also set:

```python
        self.author: str | None = None
        self.published_at: str | None = None
        self.cover_image: str | None = None
        self._pending_video = False
```

In `handle_starttag`, after `attr = dict(attrs)`, handle meta / iframe / video / source. Insert these branches **before** the existing `title` branch, and do not skip `video` (it is not in `SKIP_TAGS`):

```python
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
            else:
                self._pending_video = True
            return
        if tag == "source" and self._pending_video and attr.get("src"):
            self._chunks.append(
                "\n\n" + format_media_comment("video-gif", src=attr.get("src") or "") + "\n"
            )
            self._pending_video = False
            return
```

In `handle_endtag`, add:

```python
        if tag == "video":
            self._pending_video = False
```

Change `fetch_via_html` to copy parser meta onto the article:

```python
def fetch_via_html(url: str, timeout: int = 45) -> FetchedArticle:
    final_url, html = _http_get(url, timeout=timeout)
    parser = _HTMLArticleParser()
    parser.feed(html)
    title, markdown = parser.result(final_url)
    if len(markdown) < 80:
        raise FetchError("Direct HTML extract returned too little article text")
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
    )
```

At the end of `fetch_via_jina`, before return, set `markdown = inject_youtube_comments(markdown.strip())` and return that markdown.

- [ ] **Step 4: Run tests and make sure they pass**

Run: `python3 -m unittest tests.test_article_tools tests.test_translation_format -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/article_tools.py tests/test_article_tools.py
git commit -m "feat: extract inbox media markers and page meta"
```

---

### Task 4: GIF encoder with 15-second gate

**Files:**
- Create: `scripts/capture_media.py`
- Test: `tests/test_capture_media.py`

**Interfaces:**
- Consumes: `translation_format.should_convert_source`, `MAX_GIF_BYTES`, `MAX_SOURCE_SECONDS`
- Produces:
  - `probe_duration_seconds(path: Path) -> float | None`
  - `encode_gif(src: Path, dest: Path, fps: int = 8, width: int = 640) -> bool`
  - `convert_local_video(src: Path, dest: Path) -> str` return values: `"converted"`, `"skipped-long"`, `"skipped-unknown"`, `"skipped-no-ffmpeg"`, `"skipped-too-large"`
  - `parse_media_comments(markdown: str) -> list[dict]`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_capture_media.py`:

```python
#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import capture_media  # noqa: E402


def _have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def _make_color_mp4(path: Path, seconds: float) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=red:s=64x64:d={seconds}",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ],
        check=True,
        capture_output=True,
    )


class ParseCommentsTest(unittest.TestCase):
    def test_parses_youtube_and_video_markers(self) -> None:
        text = """
<!-- media:youtube id="fG8xWTHnlLY" url="https://www.youtube.com/watch?v=fG8xWTHnlLY" -->
<!-- media:video-gif src="https://example.com/loop.webm" -->
"""
        markers = capture_media.parse_media_comments(text)
        self.assertEqual(markers[0]["kind"], "youtube")
        self.assertEqual(markers[0]["id"], "fG8xWTHnlLY")
        self.assertEqual(markers[1]["kind"], "video-gif")
        self.assertEqual(markers[1]["src"], "https://example.com/loop.webm")


@unittest.skipUnless(_have_ffmpeg(), "ffmpeg/ffprobe required")
class GifEncodeTest(unittest.TestCase):
    def test_converts_short_clip_and_skips_long_clip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            short = Path(tmp) / "short.mp4"
            long = Path(tmp) / "long.mp4"
            short_gif = Path(tmp) / "short.gif"
            long_gif = Path(tmp) / "long.gif"
            _make_color_mp4(short, 1)
            _make_color_mp4(long, 16)
            self.assertEqual(capture_media.convert_local_video(short, short_gif), "converted")
            self.assertTrue(short_gif.is_file())
            self.assertGreater(short_gif.stat().st_size, 0)
            self.assertEqual(capture_media.convert_local_video(long, long_gif), "skipped-long")
            self.assertFalse(long_gif.exists())


class GifEncodeFallbackTest(unittest.TestCase):
    def test_unknown_duration_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "x.gif"
            status = capture_media.convert_local_video(
                Path(tmp) / "missing.mp4",
                dest,
                duration_s=None,
                require_existing_src=False,
            )
            self.assertEqual(status, "skipped-unknown")
            self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_capture_media -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'capture_media'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/capture_media.py`:

```python
#!/usr/bin/env python3
"""Convert short inbox media into GIFs. Skip clips longer than 15s."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import translation_format

COMMENT_RE = re.compile(r"<!--\s*media:([a-z0-9-]+)([^>]*)-->")
ATTR_RE = re.compile(r'([a-z0-9_]+)="([^"]*)"')


def parse_media_comments(markdown: str) -> list[dict[str, str]]:
    markers: list[dict[str, str]] = []
    for match in COMMENT_RE.finditer(markdown or ""):
        item = {"kind": match.group(1)}
        for key, value in ATTR_RE.findall(match.group(2) or ""):
            item[key] = value
        markers.append(item)
    return markers


def probe_duration_seconds(path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not path.is_file():
        return None
    try:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return float(proc.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def encode_gif(src: Path, dest: Path, fps: int = 8, width: int = 640) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    filt = f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-vf", filt, "-loop", "0", str(dest)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        return False
    return dest.is_file() and dest.stat().st_size > 0


def convert_local_video(
    src: Path,
    dest: Path,
    duration_s: float | None = None,
    require_existing_src: bool = True,
) -> str:
    if duration_s is None and require_existing_src:
        duration_s = probe_duration_seconds(src)
    if not translation_format.should_convert_source(duration_s):
        return "skipped-unknown" if duration_s is None else "skipped-long"
    if not shutil.which("ffmpeg"):
        return "skipped-no-ffmpeg"
    if require_existing_src and not src.is_file():
        return "skipped-unknown"
    if not encode_gif(src, dest, fps=8, width=640):
        return "skipped-too-large"
    if dest.stat().st_size > translation_format.MAX_GIF_BYTES:
        dest.unlink(missing_ok=True)
        if encode_gif(src, dest, fps=6, width=480) and dest.stat().st_size <= translation_format.MAX_GIF_BYTES:
            return "converted"
        dest.unlink(missing_ok=True)
        return "skipped-too-large"
    return "converted"
```

- [ ] **Step 4: Run tests and make sure they pass**

Run: `python3 -m unittest tests.test_capture_media -v`

Expected: PASS. `GifEncodeTest` runs because this environment has ffmpeg.

- [ ] **Step 5: Commit**

```bash
git add scripts/capture_media.py tests/test_capture_media.py
git commit -m "feat: convert local clips under 15s to gif"
```

---

### Task 5: Inbox capture CLI and workflow hook

**Files:**
- Modify: `scripts/capture_media.py` (add `process_inbox`, `main`)
- Modify: `.github/workflows/translate-article.yml` (run capture; `git add _inbox assets`)
- Modify: `.github/workflows/article-tools.yml` (run all three test modules)
- Test: `tests/test_capture_media.py`

**Interfaces:**
- Consumes: `parse_media_comments`, `convert_local_video`, inbox `source_url` slug via `article_tools.slug_from_url`
- Produces: `process_inbox(inbox_dir: Path, repo_root: Path) -> dict` with `processed` / `skipped` lists; writes `assets/<slug>/video-N.gif` for local/short files only. YouTube markers are listed but not downloaded in CI (duration unknown ⇒ skip). CLI: `python3 scripts/capture_media.py --inbox _inbox --repo-root .`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_capture_media.py`:

```python
class ProcessInboxTest(unittest.TestCase):
    def test_process_inbox_converts_short_local_marker(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inbox = root / "_inbox"
            inbox.mkdir()
            clip = inbox / "clip.mp4"
            _make_color_mp4(clip, 1)
            (inbox / "Demo-Post.source.md").write_text(
                "---\nsource_url: https://example.com/demo-post\n---\n\n"
                f"<!-- media:video-gif src=\"{clip.as_uri()}\" -->\n"
                "<!-- media:youtube id=\"fG8xWTHnlLY\" url=\"https://www.youtube.com/watch?v=fG8xWTHnlLY\" -->\n",
                encoding="utf-8",
            )
            report = capture_media.process_inbox(inbox, root)
            gif = root / "assets" / "demo-post" / "video-1.gif"
            statuses = {item["status"] for item in report["items"]}
            self.assertIn("converted", statuses)
            self.assertTrue(any(item["status"] in {"skipped-unknown", "skipped-long"} for item in report["items"] if item.get("kind") == "youtube"))
            self.assertTrue(gif.is_file())
```

`Path.as_uri()` yields `file:///...`. `process_inbox` must accept `file://` src by converting it to a local path. YouTube without duration is skipped.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_capture_media.ProcessInboxTest -v`

Expected: FAIL with `AttributeError: module 'capture_media' has no attribute 'process_inbox'`

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/capture_media.py`:

```python
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

import article_tools


def _source_to_path(src: str) -> Path | None:
    if src.startswith("file://"):
        return Path(url2pathname(urlparse(src).path))
    path = Path(src)
    return path if path.is_file() else None


def process_inbox(inbox_dir: Path, repo_root: Path) -> dict:
    report: dict = {"items": []}
    if not inbox_dir.is_dir():
        return report
    media_count = 0
    for source in sorted(inbox_dir.glob("*.source.md")):
        text = source.read_text(encoding="utf-8")
        url_match = re.search(r"^source_url:\s+(\S+)", text, re.MULTILINE)
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        slug = article_tools.slug_from_url(
            url_match.group(1) if url_match else source.stem,
            title_match.group(1) if title_match else None,
        )
        video_index = 0
        for marker in parse_media_comments(text):
            if media_count >= translation_format.MAX_MEDIA_FILES:
                report["items"].append({"file": source.name, "kind": marker.get("kind"), "status": "skipped-limit"})
                continue
            kind = marker.get("kind")
            if kind == "youtube":
                report["items"].append(
                    {
                        "file": source.name,
                        "kind": "youtube",
                        "id": marker.get("id"),
                        "status": "skipped-unknown",
                    }
                )
                continue
            if kind != "video-gif":
                report["items"].append({"file": source.name, "kind": kind, "status": "skipped-unknown"})
                continue
            src_path = _source_to_path(marker.get("src") or "")
            video_index += 1
            dest = repo_root / "assets" / slug / f"video-{video_index}.gif"
            if src_path is None:
                report["items"].append({"file": source.name, "kind": kind, "status": "skipped-unknown"})
                continue
            status = convert_local_video(src_path, dest)
            if status == "converted":
                media_count += 1
            report["items"].append(
                {
                    "file": source.name,
                    "kind": kind,
                    "status": status,
                    "dest": str(dest.relative_to(repo_root)) if status == "converted" else "",
                }
            )
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Convert short inbox media to GIFs")
    parser.add_argument("--inbox", default="_inbox")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    report = process_inbox((repo_root / args.inbox).resolve(), repo_root)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

YouTube is not downloaded in this task. Duration is unknown, so it is skipped. That matches the spec. Translators still write the text link.

In `.github/workflows/translate-article.yml`, after the `Prepare inbox from URLs` step (after `cat /tmp/prepare.json`), add a new step **before** push:

```yaml
      - name: Convert short inbox media
        if: steps.guard.outputs.skip != 'true' && steps.prepare.outputs.has_files == 'true'
        run: python3 scripts/capture_media.py --inbox _inbox --repo-root .
```

In the push step, change `git add _inbox` to `git add _inbox assets`.

Change the commit message to `Add translation inbox source and short media`.

In `.github/workflows/article-tools.yml`, replace the test command and path filters:

```yaml
    paths:
      - scripts/**
      - tests/**
      - .github/workflows/article-tools.yml
...
        run: python3 -m unittest tests.test_article_tools tests.test_translation_format tests.test_capture_media -v
```

- [ ] **Step 4: Run tests and make sure they pass**

Run: `python3 -m unittest tests.test_capture_media tests.test_article_tools tests.test_translation_format -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/capture_media.py tests/test_capture_media.py .github/workflows/translate-article.yml .github/workflows/article-tools.yml
git commit -m "feat: process inbox media markers into assets gifs"
```

---

### Task 6: Rewrite the translating-articles skill and agent docs

**Files:**
- Modify: `.github/skills/translating-articles/SKILL.md` (replace entire body after frontmatter)
- Modify: `.github/agents/article-translator.agent.md`
- Modify: `docs/translating-articles.md`
- Modify: `AGENTS.md`
- Modify: `.github/copilot-instructions.md`
- Modify: `_inbox/README.md`

**Interfaces:**
- Consumes: the output template and completion checklist from `docs/superpowers/specs/2026-08-22-translation-format-design.md`
- Produces: agents write root markdown + `assets/<slug>/` + README using the new format

- [ ] **Step 1: Replace the skill body**

Write `.github/skills/translating-articles/SKILL.md` as:

```markdown
---
name: translating-articles
description: Use when translating an English technical article into this repo from a URL, GitHub issue labeled translate, _inbox/*.source.md file, Copilot article-translator agent, or a request to 翻译 / translate an article.
---

# Translating articles

Turn an English article URL into a Simplified Chinese markdown post that matches `docs/superpowers/specs/2026-08-22-translation-format-design.md`.

## Inputs

Use the first source that exists:

1. `_inbox/*.source.md` (Action already fetched the article)
2. URLs in the GitHub issue / user message
3. Fetch with `python scripts/article_tools.py --url URL --outdir _inbox`

Then run `python scripts/capture_media.py --inbox _inbox --repo-root .` if `assets/<slug>/` is missing and the inbox has `<!-- media:... -->` markers.

Do not invent article text. If fetch fails, comment on the issue and stop.

Skip a URL if it already appears in `README.md` or an existing root `*.md` file.

## Output file

- Path: repo root, filename from the English title slug (`CSS-the-bomb-inside-your-inbox.md`).
- Do **not** put `【翻译】` in the filename or H1.
- Short GIFs: `assets/<slug>/video-N.gif` or `yt-<id>.gif`.

Copy inbox `author` / `published_at` / `cover_image` when present. You still write `title`, `title_en`, `tech_domain`, `tags`, `translated_at`.

```yaml
---
title: "中文标题"
title_en: "English title"
source_url: https://example.com/article
author: Ada Lovelace
published_at: 2026-01-02
translated_at: 2026-08-22
tech_domain: security
tags: [security, web, frontend]
cover_image: https://example.com/cover.png
---
```

`tech_domain` must be one of: `android`, `frontend`, `backend`, `security`, `mobile`, `devops`, `other`.
Omit `author`, `published_at`, and `cover_image` when unknown. Do not invent them.

Body header, in this order, blank line between blocks:

```markdown
# 中文标题

原文链接：<https://example.com/article>

原文作者：Ada Lovelace

![文章头图](https://example.com/cover.png)

作者：[Ada Lovelace](https://example.com/ada)

发布于 2026 年 1 月 2 日。

**加粗导语。术语第一次写成 中文（English）。**
```

Omit any header line you cannot fill. Do not use `[原文链接](URL)`.

## Body rules

- Simplified Chinese. Keep code, commands, API names, and original image URLs.
- Headings: `## [引言](#introduction)` — Chinese title, original slug.
- First use of a term: `消毒（sanitization）`.
- No `iframe`. No `p9-xtjj-sign` / `link.juejin.cn` URLs.
- Videos:

```markdown
[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=ID)
```

If `assets/<slug>/` has a GIF for that clip (only when source duration ≤ 15s), add:

```markdown
![嵌入内容（原站 YouTube）](assets/slug/yt-ID.gif)
```

If duration is missing or over 15 seconds, write the link only.

## README

```markdown
[中文标题](https://github.com/lihenair/techtranslate/blob/master/File-Name.md)
```

## Cleanup

Delete the matching `_inbox/*.source.md`. Keep `assets/<slug>/` GIFs that the translation references. Do not commit leftover English inbox files.

## Done

Open or update a pull request with the translation, README, and any `assets/<slug>/` files. Run `python3 -c "import sys; sys.path.insert(0,'scripts'); import translation_format,pathlib; print(translation_format.validate_translation(pathlib.Path('FILE.md').read_text()))"` and fix any errors before you finish.
```

- [ ] **Step 2: Update the other agent-facing docs**

`.github/agents/article-translator.agent.md`:

```markdown
---
name: article-translator
description: Fetches English technical-article URLs (or uses _inbox source files) and adds Simplified Chinese translations using the Juejin-style markdown template
tools: ["read", "search", "edit", "execute"]
---

You translate English software articles into this `techtranslate` repository.

Always load and follow the skill `.github/skills/translating-articles/SKILL.md`.

When assigned an issue or pull request:

1. Collect article URLs from the issue body and any `_inbox/*.source.md` files.
2. Prefer inbox source files — GitHub Actions fetches them because you may not be able to browse the live page.
3. If inbox files are missing, run `python scripts/article_tools.py --url <URL> --outdir _inbox`.
4. Run `python scripts/capture_media.py --inbox _inbox --repo-root .` when media comments exist.
5. Write one root-level Chinese markdown file per article (YAML meta + body header, no `【翻译】` on GitHub), update `README.md`, keep `assets/<slug>/` GIFs, and delete the inbox source.
6. Do not change unrelated translations.

If a URL cannot be fetched and there is no inbox file, comment on the issue with the error and stop. Do not guess the article body.
```

`AGENTS.md`:

```markdown
# Agent notes

This repository publishes Simplified Chinese translations of English software articles.

When the user (or a GitHub issue) provides an article URL, follow `.github/skills/translating-articles/SKILL.md`. Prefer `_inbox/*.source.md` if the GitHub Action already fetched the page. Output must match `docs/superpowers/specs/2026-08-22-translation-format-design.md`.

Use the Copilot custom agent `.github/agents/article-translator.agent.md` when working from GitHub.com.
```

`.github/copilot-instructions.md`:

```markdown
This repository is a collection of Simplified Chinese translations of English technical articles.

When asked to translate an article from a URL or a GitHub issue:

- Follow `.github/skills/translating-articles/SKILL.md`
- Prefer `_inbox/*.source.md` over re-fetching the live page
- Use YAML frontmatter + the body header from the skill (no `【翻译】` on GitHub)
- Keep code, API names, and original image URLs
- Add a `README.md` link for every new translation
```

In `docs/translating-articles.md`, after the first paragraph add:

```markdown
New posts use the template in [the translation format spec](superpowers/specs/2026-08-22-translation-format-design.md): YAML meta, Chinese H1, and GIF assets only for source clips that last 15 seconds or less.
```

Add a row to its Files table:

```markdown
| `scripts/capture_media.py` | Convert inbox media ≤15s into `assets/<slug>/` GIFs |
```

`_inbox/README.md` — replace the numbered list with:

```markdown
1. Translate each file into a root-level Chinese markdown post using `.github/skills/translating-articles/SKILL.md`
2. Keep any `assets/<slug>/` GIFs the capture step wrote
3. Link the post from `README.md`
4. Delete the inbox source from the pull request
```

- [ ] **Step 3: Run the existing unit tests (docs have no test runner)**

Run: `python3 -m unittest tests.test_article_tools tests.test_translation_format tests.test_capture_media -v`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add .github/skills/translating-articles/SKILL.md .github/agents/article-translator.agent.md AGENTS.md .github/copilot-instructions.md docs/translating-articles.md _inbox/README.md
git commit -m "docs: switch translators to Juejin-style template"
```

---

## Self-review

**Spec coverage**

| Spec section | Task |
| --- | --- |
| Frontmatter fields + omit empty | Task 1 validator + Task 2 inbox extras + Task 6 skill |
| Body header / `原文链接：<URL>` / no `【翻译】` | Task 1 + Task 6 |
| Heading `## [中文](#slug)` | Task 1 `heading_md` + Task 6 |
| YouTube text link | Task 1 `embed_link` + Task 6 |
| HTML media comments | Task 3 |
| ≤15s convert / >15s or unknown skip | Task 1 gate + Task 4 encoder + Task 5 inbox |
| `assets/<slug>/` + workflow commit | Task 5 |
| No iframe / no Juejin hosts | Task 1 validator + Task 6 |
| Do not migrate old posts | Task 6 skill (new posts only); no rewrite task |
| CSS Playwright recording | Not automated in CI. Skill says write「原文为网页动画」when no GIF. Matches spec fallback. |
| Image-sequence ≤120 frames | Constant `MAX_SEQUENCE_FRAMES` in Task 1; stitch loop can be added later without changing the gate. Inbox HTML with only `<img>` sequences is not auto-stitched in this plan (YAGNI until a real article needs it). Translator can still run ffmpeg locally. |

**Intentionally not in this plan (spec allows fallback):** Playwright CSS recording; YouTube download via yt-dlp; Bilibili/Vimeo download; image-sequence stitch; Juejin auto-publish.

**Placeholder scan:** none.

**Type consistency:** `should_convert_source(duration_s: float | None) -> bool`, `convert_local_video(...) -> str` status strings, `parse_media_comments -> list[dict]`, `format_media_comment(kind, **attrs)`, `FetchedArticle.author/published_at/cover_image`.
