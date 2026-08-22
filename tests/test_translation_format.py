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

    def test_parses_twitter_and_x_status_urls(self) -> None:
        self.assertEqual(
            tf.twitter_status_from_url("https://twitter.com/garethheyes/status/1680555380416577536"),
            "1680555380416577536",
        )
        self.assertEqual(
            tf.twitter_status_from_url("https://x.com/i/status/1680555380416577536"),
            "1680555380416577536",
        )
        self.assertEqual(
            tf.twitter_status_from_url(
                "https://platform.twitter.com/embed/Tweet.html?id=1680555380416577536"
            ),
            "1680555380416577536",
        )
        self.assertIsNone(tf.twitter_status_from_url("https://twitter.com/garethheyes"))
        self.assertEqual(
            tf.twitter_status_url("1680555380416577536"),
            "https://x.com/i/status/1680555380416577536",
        )
        self.assertTrue(tf.looks_like_twitter_class("twitter-tweet"))

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
        dirty = SAMPLE + '\n<iframe src="https://www.youtube.com/embed/x"></iframe>\n'
        errors = tf.validate_translation(dirty)
        self.assertTrue(any("iframe" in e for e in errors))
        dirty = SAMPLE + "\n![](https://p9-xtjj-sign.byteimg.com/x)\n"
        errors = tf.validate_translation(dirty)
        self.assertTrue(any("juejin" in e.lower() or "xtjj" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
