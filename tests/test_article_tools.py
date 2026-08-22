#!/usr/bin/env python3
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

    def test_already_translated_detects_readme_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "[x](https://example.com/already)\n", encoding="utf-8"
            )
            self.assertTrue(article_tools.already_translated(root, "https://example.com/already"))
            self.assertFalse(article_tools.already_translated(root, "https://example.com/new"))


if __name__ == "__main__":
    unittest.main()
