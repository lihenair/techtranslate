#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import translation_archive as ta  # noqa: E402


class ArchivePathTest(unittest.TestCase):
    def test_dated_posts_go_under_date_then_domain(self) -> None:
        self.assertEqual(
            ta.archive_relpath("2026-08-23", "ai", "Claude.md"),
            "archive/2026-08-23/ai/Claude.md",
        )
        self.assertEqual(
            ta.archive_relpath("2026-08-23", "systems", "Arch.md"),
            "archive/2026-08-23/systems/Arch.md",
        )

    def test_undated_posts_share_the_earlier_bucket(self) -> None:
        self.assertEqual(
            ta.archive_relpath(None, "android", "How JPG Works.md"),
            "archive/earlier/android/How JPG Works.md",
        )
        self.assertEqual(
            ta.archive_relpath("2016-08-17", "android", "How JPG Works.md"),
            "archive/earlier/android/How JPG Works.md",
        )


class CatalogTest(unittest.TestCase):
    def test_groups_by_domain_and_sorts_newest_first(self) -> None:
        entries = [
            ta.CatalogEntry("旧安卓", "archive/earlier/android/old.md", "2016-08-17", "android"),
            ta.CatalogEntry("新 AI", "archive/2026-08-23/ai/new.md", "2026-08-23", "ai"),
            ta.CatalogEntry("较早 AI", "archive/earlier/ai/old-ai.md", "较早", "ai"),
            ta.CatalogEntry("终端", "archive/2026-08-22/other/term.md", "2026-08-22", "other"),
            ta.CatalogEntry("体系结构", "archive/2026-08-23/systems/arch.md", "2026-08-23", "systems"),
        ]
        text = ta.render_catalog(entries)
        ai = text.index("### AI")
        android = text.index("### Android")
        systems = text.index("### 系统")
        other = text.index("### 其他")
        self.assertLess(ai, android)
        self.assertLess(android, systems)
        self.assertLess(systems, other)
        ai_block = text[ai:android]
        self.assertLess(ai_block.index("2026-08-23"), ai_block.index("较早"))
        self.assertIn(
            "- 2026-08-23 [新 AI](https://github.com/lihenair/techtranslate/blob/master/archive/2026-08-23/ai/new.md)",
            text,
        )

    def test_scan_reads_dated_folders_and_earlier_dates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dated = root / "archive" / "2026-08-23" / "ai"
            dated.mkdir(parents=True)
            (dated / "post.md").write_text("# 新文\n", encoding="utf-8")
            old = root / "archive" / "earlier" / "android"
            old.mkdir(parents=True)
            (old / "legacy.md").write_text("# 旧文\n", encoding="utf-8")
            (root / "archive" / "earlier" / "dates.tsv").write_text(
                "android/legacy.md\t2016-08-17\t旧安卓标题\n",
                encoding="utf-8",
            )
            entries = ta.scan_archive(root)
            by_path = {item.relpath: item for item in entries}
            self.assertEqual(by_path["archive/2026-08-23/ai/post.md"].date, "2026-08-23")
            self.assertEqual(by_path["archive/2026-08-23/ai/post.md"].title, "新文")
            self.assertEqual(by_path["archive/earlier/android/legacy.md"].date, "2016-08-17")
            self.assertEqual(by_path["archive/earlier/android/legacy.md"].title, "旧安卓标题")


class RepoLayoutTest(unittest.TestCase):
    def test_translations_live_under_archive(self) -> None:
        leftover = [
            path.name
            for path in ROOT.iterdir()
            if path.is_file() and path.suffix in {".md", ".html"} and path.name not in {"README.md", "AGENTS.md"}
        ]
        self.assertEqual(leftover, [])
        claude = (
            ROOT
            / "archive"
            / "2026-08-23"
            / "ai"
            / "10-Claude-Code-Steering-Mechanisms-That-Stop-Agents-From-Ignoring-Instructions.md"
        )
        self.assertTrue(claude.is_file())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("### AI", readme)
        self.assertIn("2026-08-23", readme)
        self.assertIn("archive/2026-08-23/ai/", readme)


if __name__ == "__main__":
    unittest.main()
