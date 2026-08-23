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


class IsoDurationTest(unittest.TestCase):
    def test_parses_youtube_iso8601_durations(self) -> None:
        self.assertEqual(tf.parse_iso8601_duration("PT15S"), 15.0)
        self.assertEqual(tf.parse_iso8601_duration("PT1M2S"), 62.0)
        self.assertEqual(tf.parse_iso8601_duration("PT1H"), 3600.0)
        self.assertIsNone(tf.parse_iso8601_duration("bad"))


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


class TechDomainTest(unittest.TestCase):
    def test_ai_is_an_allowed_domain(self) -> None:
        self.assertIn("ai", tf.TECH_DOMAINS)
        accepted = SAMPLE.replace("tech_domain: security", "tech_domain: ai")
        self.assertEqual(tf.validate_translation(accepted), [])

    def test_systems_is_an_allowed_domain(self) -> None:
        self.assertIn("systems", tf.TECH_DOMAINS)
        accepted = SAMPLE.replace("tech_domain: security", "tech_domain: systems")
        self.assertEqual(tf.validate_translation(accepted), [])

    def test_classify_uses_primary_topic_not_side_mentions(self) -> None:
        self.assertEqual(
            tf.classify_tech_domain(
                "10 Claude Code Steering Mechanisms",
                "hooks permissions deploy staging MCP subagents",
            ),
            "ai",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "CSS: the bomb inside your inbox",
                "XSS sanitization exploit whitelist HTML",
            ),
            "security",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "CompositionLocal Made Easy",
                "Jetpack Compose Android remember",
            ),
            "android",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "Building a Kubernetes deploy pipeline",
                "CI/CD terraform helm rollout",
            ),
            "devops",
        )
        self.assertEqual(
            tf.classify_tech_domain("How JPG Works", "lossy compression blocks"),
            "systems",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "How WebP Works",
                "lossy mode quantization chroma blocks",
            ),
            "systems",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "Writing a C Compiler from Scratch",
                "lexing parsing codegen register allocation",
            ),
            "systems",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "Virtual Memory in Operating Systems",
                "page tables TLB swapping",
            ),
            "systems",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "Principles of Computer Architecture",
                "Amdahl Roofline ISA CPI pipelining Tomasulo MESI LLM kernel intensities",
            ),
            "systems",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "AI Chip Architectures",
                "GPUs TPUs systolic arrays HBM NVLink CUDA XLA",
            ),
            "ai",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "I Built a 10 MB GPU-Accelerated Terminal in Rust + Metal",
                "GPU rasterizer Metal shader terminal emulator",
            ),
            "systems",
        )

    def test_classify_ignores_generic_words_that_are_not_the_topic(self) -> None:
        self.assertEqual(
            tf.classify_tech_domain(
                "Scaling Kubernetes cluster agents",
                "helm terraform CI/CD rollout replica agents",
            ),
            "devops",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "How to write better git commit prompts",
                "commit message template",
            ),
            "other",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "How to compose CSS layouts",
                "flexbox browser HTML DOM",
            ),
            "frontend",
        )
        self.assertEqual(
            tf.classify_tech_domain(
                "Making 768 servers look like 1",
                "Postgres MySQL sharding PgBouncer Vitess Neki "
                "OpenAI replicas AI agents AI infrastructure",
            ),
            "backend",
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


class ClaudeSteeringTranslationTest(unittest.TestCase):
    PATH = (
        ROOT
        / "archive"
        / "2026-08-23"
        / "ai"
        / "10-Claude-Code-Steering-Mechanisms-That-Stop-Agents-From-Ignoring-Instructions.md"
    )

    def test_real_translation_matches_format_and_source_structure(self) -> None:
        text = self.PATH.read_text(encoding="utf-8")
        self.assertEqual(tf.validate_translation(text), [])
        self.assertIn("published_at: 2026-06-28", text)
        self.assertIn("发布于 2026 年 6 月 28 日。", text)
        self.assertNotIn("嵌入内容（原站 Twitter）", text)
        for slug in (
            "why-this-matters-now",
            "the-10-steering-mechanisms",
            "1-project-memory-index-claudemd",
            "2-path-scoped-constraint-rules",
            "3-just-in-time-procedure-skills",
            "4-human-triggered-workflow-manual-skills-and-slash-commands",
            "5-isolated-investigator-subagents",
            "6-session-posture-output-styles",
            "7-one-run-overlay-append-system-prompt",
            "8-live-capability-boundary-mcp-servers",
            "9-event-gate-hooks",
            "10-hard-boundary-permissions",
            "the-decision-tree",
            "what-changes-in-long-sessions",
            "final-takeaway",
        ):
            self.assertIn(f"](#{slug})", text)
        for excerpt in (
            "Package manager: pnpm",
            'paths:\n  - "src/api/**/*.ts"',
            "name: release-notes",
            "disable-model-invocation: true",
            "name: security-reviewer",
            "keep-coding-instructions: true",
            "claude --append-system-prompt-file",
            '"PreToolUse"',
            '"Read(./secrets/**)"',
        ):
            self.assertIn(excerpt, text)


if __name__ == "__main__":
    unittest.main()
