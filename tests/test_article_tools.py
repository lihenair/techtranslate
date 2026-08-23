#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import article_tools  # noqa: E402


ISSUE_BODY = """
### Article URL

https://medium.com/mobile-app-development-publication/android-jetpack-compose-compositionlocal-made-easy-8632b201bfcd.

### Additional URLs

https://www.baeldung.com/kotlin/contracts
https://github.com/lihenair/techtranslate/assets/123/image.png
"""


class IssueRequestTest(unittest.TestCase):
    def test_parses_form_url_and_chinese_title(self) -> None:
        body = """### 原文链接

https://www.jacobpeake.com/ai-chip-architectures

### 中文标题

AI 芯片架构

### 更多文章

_No response_
"""
        reqs = article_tools.parse_issue_requests(body, issue_title="[Translate] ignored")
        self.assertEqual(
            reqs,
            [
                {
                    "url": "https://www.jacobpeake.com/ai-chip-architectures",
                    "title_zh": "AI 芯片架构",
                }
            ],
        )

    def test_parses_extra_lines_with_optional_title(self) -> None:
        body = """### 原文链接

https://example.com/one

### 中文标题

第一篇

### 更多文章

https://example.com/two | 第二篇
https://example.com/three
"""
        reqs = article_tools.parse_issue_requests(body)
        self.assertEqual(
            [item["url"] for item in reqs],
            ["https://example.com/one", "https://example.com/two", "https://example.com/three"],
        )
        self.assertEqual([item["title_zh"] for item in reqs], ["第一篇", "第二篇", None])

    def test_uses_issue_title_when_form_title_missing(self) -> None:
        body = """### Article URL

https://www.jacobpeake.com/ai-chip-architectures

### Additional URLs

_No response_
"""
        reqs = article_tools.parse_issue_requests(
            body, issue_title="[Translate] AI Chip Architectures"
        )
        self.assertEqual(reqs[0]["title_zh"], "AI Chip Architectures")

    def test_format_round_trips_through_the_issue_parser(self) -> None:
        requests = [
            {"url": "https://example.com/one", "title_zh": "第一篇"},
            {"url": "https://example.com/two", "title_zh": "第二篇"},
            {"url": "https://example.com/three", "title_zh": None},
        ]
        title, body = article_tools.format_translate_issue(requests, notes="keep API names")
        self.assertEqual(title, "[Translate] 第一篇")
        parsed = article_tools.parse_issue_requests(body, issue_title=title)
        self.assertEqual(parsed, requests)
        self.assertIn("keep API names", body)

    def test_queue_script_prints_issue_without_creating(self) -> None:
        out = subprocess.check_output(
            [
                sys.executable,
                str(ROOT / "scripts" / "queue_translation.py"),
                "--url",
                "https://example.com/a",
                "--title-zh",
                "甲",
                "--pair",
                "https://example.com/b | 乙",
            ],
            text=True,
        )
        data = json.loads(out)
        self.assertEqual(data["title"], "[Translate] 甲")
        self.assertEqual(
            [item["url"] for item in data["requests"]],
            ["https://example.com/a", "https://example.com/b"],
        )
        parsed = article_tools.parse_issue_requests(data["body"], issue_title=data["title"])
        self.assertEqual(parsed[0]["title_zh"], "甲")
        self.assertEqual(parsed[1]["title_zh"], "乙")

    def test_old_additional_urls_still_work(self) -> None:
        reqs = article_tools.parse_issue_requests(ISSUE_BODY)
        self.assertEqual(
            [item["url"] for item in reqs],
            [
                "https://medium.com/mobile-app-development-publication/android-jetpack-compose-compositionlocal-made-easy-8632b201bfcd",
                "https://www.baeldung.com/kotlin/contracts",
            ],
        )


class ExtractUrlsTest(unittest.TestCase):
    def test_extracts_unique_http_urls_and_strips_punctuation(self) -> None:
        urls = article_tools.extract_urls(ISSUE_BODY)
        self.assertEqual(
            urls,
            [
                "https://medium.com/mobile-app-development-publication/android-jetpack-compose-compositionlocal-made-easy-8632b201bfcd",
                "https://www.baeldung.com/kotlin/contracts",
            ],
        )

    def test_html_parser_keeps_links_and_code(self) -> None:
        html = """<html><head><title>Hello Compose</title></head><body>
        <h1>Hello Compose</h1>
        <p>See <a href="https://example.com">site</a> and <code>foo()</code>.</p>
        <pre>keep this</pre>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        title, markdown = parser.result("https://example.com/a")
        self.assertEqual(title, "Hello Compose")
        self.assertIn("[site](https://example.com)", markdown)
        self.assertIn("`foo()`", markdown)
        self.assertIn("keep this", markdown)

    def test_skips_github_issue_and_asset_urls(self) -> None:
        urls = article_tools.extract_urls(
            "\n".join(
                [
                    "https://github.com/lihenair/techtranslate/issues/12",
                    "https://github.com/lihenair/techtranslate/assets/1/x.png",
                    "https://example.com/real-article",
                ]
            )
        )
        self.assertEqual(urls, ["https://example.com/real-article"])


class SlugTest(unittest.TestCase):
    def test_slug_from_title_and_url(self) -> None:
        self.assertEqual(
            article_tools.slug_from_url(
                "https://example.com/posts/foo-bar.html",
                title="CompositionLocal Made Easy",
            ),
            "CompositionLocal-Made-Easy",
        )
        self.assertEqual(
            article_tools.inbox_filename("https://example.com/posts/kotlin-contracts"),
            "kotlin-contracts.source.md",
        )


class InboxFormatTest(unittest.TestCase):
    def test_source_markdown_contains_url_and_title(self) -> None:
        article = article_tools.FetchedArticle(
            url="https://example.com/a",
            title="Hello Compose",
            markdown="Body text here.",
            method="jina",
        )
        text = article_tools.format_source_markdown(article, issue="12")
        self.assertIn("source_url: https://example.com/a", text)
        self.assertIn("issue: 12", text)
        self.assertIn("# Hello Compose", text)
        self.assertIn("Body text here.", text)

    def test_source_markdown_writes_requested_chinese_title(self) -> None:
        article = article_tools.FetchedArticle(
            url="https://example.com/a",
            title="Hello Compose",
            markdown="Body text here.",
            method="jina",
            title_zh="你好 Compose",
        )
        text = article_tools.format_source_markdown(article, issue="8")
        self.assertIn("title_zh: 你好 Compose", text)

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

    def test_already_translated_detects_readme_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "[x](https://example.com/already)\n", encoding="utf-8"
            )
            self.assertTrue(article_tools.already_translated(root, "https://example.com/already"))
            self.assertFalse(article_tools.already_translated(root, "https://example.com/new"))

    def test_already_translated_detects_archive_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# index\n", encoding="utf-8")
            dest = root / "archive" / "2026-08-23" / "ai"
            dest.mkdir(parents=True)
            (dest / "post.md").write_text(
                "原文链接：<https://example.com/archived>\n", encoding="utf-8"
            )
            self.assertTrue(article_tools.already_translated(root, "https://example.com/archived"))
            self.assertFalse(article_tools.already_translated(root, "https://example.com/new"))


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

    def test_html_parser_emits_twitter_status_comment(self) -> None:
        html = """<html><head><title>Tweet embed</title></head><body>
        <h1>Tweet embed</h1>
        <blockquote class="twitter-tweet">
          <p>demo</p>
          <a href="https://twitter.com/garethheyes/status/1680555380416577536">June 2023</a>
        </blockquote>
        <iframe src="https://platform.twitter.com/embed/Tweet.html?id=1680555380416577536"></iframe>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        _title, markdown = parser.result("https://example.com/tweet-post")
        self.assertIn(
            '<!-- media:twitter id="1680555380416577536" url="https://x.com/i/status/1680555380416577536" -->',
            markdown,
        )
        self.assertEqual(markdown.count("media:twitter"), 1)

    def test_plain_twitter_citation_is_not_a_media_marker(self) -> None:
        html = """<html><head><title>Cite</title></head><body>
        <h1>Cite</h1>
        <p>See <a href="https://x.com/slonser_/status/1912060415296835961">Slonser</a> for details.</p>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        _title, markdown = parser.result("https://example.com/cite")
        self.assertNotIn("media:twitter", markdown)
        text = article_tools.inject_media_comments(
            "See https://x.com/slonser_/status/1912060415296835961 for details"
        )
        self.assertNotIn("media:twitter", text)

    def test_section_with_three_images_emits_frames_comment(self) -> None:
        html = """<html><head><title>Frames</title></head><body>
        <h1>Frames</h1>
        <section class="gif-demo">
          <img src="/a.png"><img src="/b.png"><img src="/c.png">
        </section>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        _title, markdown = parser.result("https://example.com/a")
        self.assertIn("media:frames", markdown)
        self.assertIn("https://example.com/a.png", markdown)
        self.assertIn("https://example.com/b.png", markdown)

    def test_css_section_emits_section_anim_comment(self) -> None:
        html = """<html><head><title>Anim</title>
        <style>.box{animation:x 1s infinite}@keyframes x{to{opacity:0}}</style>
        </head><body>
        <h1>Anim</h1>
        <section class="demo"><div class="box">Hi</div></section>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        _title, markdown = parser.result("https://example.com/anim")
        self.assertIn("media:section-anim", markdown)
        self.assertTrue(parser.section_snippets)

    def test_wrapper_section_does_not_steal_inner_demo(self) -> None:
        html = """<html><head><title>Anim</title>
        <style>.box{animation:x 1s infinite}@keyframes x{to{opacity:0}}</style>
        </head><body>
        <h1>Anim</h1>
        <section class="page-content">
          <p>This article discusses animation techniques with diagrams.</p>
          <img src="/a.png"><img src="/b.png"><img src="/c.png">
          <section class="demo"><div class="box">Hi</div></section>
        </section>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        _title, markdown = parser.result("https://example.com/anim")
        self.assertIn("media:section-anim", markdown)
        self.assertNotIn("media:frames", markdown)
        self.assertEqual(len(parser.section_snippets), 1)

    def test_prose_animation_word_is_not_section_anim(self) -> None:
        html = """<html><head><title>Cite</title></head><body>
        <h1>Cite</h1>
        <section>
          <p>This animation is cool and uses several frames.</p>
          <img src="/a.png"><img src="/b.png">
        </section>
        <p>Enough article text so the extract is not considered empty padding padding padding padding.</p>
        </body></html>"""
        parser = article_tools._HTMLArticleParser()
        parser.feed(html)
        _title, markdown = parser.result("https://example.com/cite")
        self.assertNotIn("media:section-anim", markdown)
        self.assertNotIn("media:frames", markdown)

    def test_inline_linked_stylesheets_rewrites_relative_urls(self) -> None:
        html = (
            '<html><head><link rel="stylesheet" href="/css/a.css">'
            "</head><body>Hi</body></html>"
        )

        def fake_get(url: str, timeout: int = 45) -> tuple[str, str]:
            self.assertEqual(url, "https://example.com/css/a.css")
            return url, "body{background:url(/img/x.png)}"

        out = article_tools.inline_linked_stylesheets(
            "https://example.com/page", html, getter=fake_get
        )
        self.assertIn("<style>", out)
        self.assertIn("https://example.com/img/x.png", out)

    def test_inline_linked_stylesheets_keeps_css_backslashes(self) -> None:
        html = (
            '<html><head><link rel="stylesheet" href="/css/a.css">'
            "</head><body>Hi</body></html>"
        )

        def fake_get(url: str, timeout: int = 45) -> tuple[str, str]:
            return url, r'.icon::before{content:"\21"}'

        out = article_tools.inline_linked_stylesheets(
            "https://example.com/page", html, getter=fake_get
        )
        self.assertIn(r'content:"\21"', out)


class MergeHtmlEnrichmentTest(unittest.TestCase):
    def test_jina_keeps_text_and_gains_html_media_and_meta(self) -> None:
        jina = article_tools.FetchedArticle(
            url="https://example.com/anim",
            title="Readable title",
            markdown="Readable body from Jina with enough text.",
            method="jina",
        )
        html = article_tools.FetchedArticle(
            url="https://example.com/anim",
            title="HTML title",
            markdown=(
                "lossy html body\n\n"
                '<!-- media:twitter id="1680555380416577536" url="https://x.com/i/status/1680555380416577536" -->\n'
                '<!-- media:section-anim index="1" duration_s="4" -->\n'
            ),
            method="html",
            author="Ada",
            published_at="2026-01-02",
            cover_image="https://example.com/cover.png",
            section_snippets=["<!doctype html><html></html>"],
        )
        merged = article_tools.merge_html_enrichment(jina, html)
        self.assertEqual(merged.method, "jina")
        self.assertEqual(merged.title, "Readable title")
        self.assertEqual(merged.markdown, "Readable body from Jina with enough text.")
        self.assertEqual(merged.author, "Ada")
        self.assertEqual(merged.published_at, "2026-01-02")
        self.assertEqual(merged.cover_image, "https://example.com/cover.png")
        self.assertEqual(merged.section_snippets, ["<!doctype html><html></html>"])
        self.assertTrue(
            any("media:twitter" in comment for comment in (merged.media_comments or []))
        )
        self.assertTrue(
            any("media:section-anim" in comment for comment in (merged.media_comments or []))
        )
        text = article_tools.format_source_markdown(merged)
        self.assertIn("Readable body from Jina with enough text.", text)
        self.assertIn("media:twitter", text)
        self.assertIn("media:section-anim", text)

    def test_merge_does_not_overwrite_existing_jina_meta(self) -> None:
        jina = article_tools.FetchedArticle(
            url="https://example.com/a",
            title="T",
            markdown="body",
            method="jina",
            author="From Jina",
            published_at="2025-12-01",
            cover_image="https://example.com/jina.png",
        )
        html = article_tools.FetchedArticle(
            url="https://example.com/a",
            title="T",
            markdown="html",
            method="html",
            author="From HTML",
            published_at="2026-01-02",
            cover_image="https://example.com/html.png",
        )
        merged = article_tools.merge_html_enrichment(jina, html)
        self.assertEqual(merged.author, "From Jina")
        self.assertEqual(merged.published_at, "2025-12-01")
        self.assertEqual(merged.cover_image, "https://example.com/jina.png")


if __name__ == "__main__":
    unittest.main()
