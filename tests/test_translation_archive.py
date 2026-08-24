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
        self.assertEqual(
            ta.archive_relpath("2026-08-23", "graphics", "3DGS.md"),
            "archive/2026-08-23/graphics/3DGS.md",
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

    def test_scan_skips_duplicate_names_and_strips_translation_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            android = root / "archive" / "earlier" / "android"
            android.mkdir(parents=True)
            (android / "keep.md").write_text("# 【翻译】保留标题\n", encoding="utf-8")
            (android / "DI101 - 第一部分.md").write_text("# 重复条目\n", encoding="utf-8")
            entries = ta.scan_archive(root)
            names = [Path(item.relpath).name for item in entries]
            self.assertEqual(names, ["keep.md"])
            self.assertEqual(entries[0].title, "保留标题")


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

    def test_readme_explains_inbox_vs_translation_pr_and_lists_ci(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("| **inbox PR**", readme)
        self.assertIn("| **译文 PR**", readme)
        self.assertIn(".github/workflows/article-tools.yml", readme)
        self.assertIn("close-inbox-pr.yml", readme)

    def test_catalog_uses_chinese_titles_and_skips_duplicate_di101(self) -> None:
        entries = ta.scan_archive(ROOT)
        by_name = {Path(item.relpath).name: item.title for item in entries}
        self.assertEqual(by_name["Android 7.1静态快捷方式.md"], "Android 7.1 静态快捷方式")
        self.assertEqual(by_name["Recomposition-Made-Easy.md"], "轻松理解 Jetpack Compose 的 Recomposition")
        self.assertEqual(by_name["CompositionLocal-Made-Easy.md"], "轻松理解 Jetpack Compose 的 CompositionLocal")
        self.assertEqual(
            by_name["Keeping Android runtime permissions from cluttering your app (Headless Dialog Fragments!).md"],
            "别让运行时权限把应用搞乱（Headless Dialog Fragment）",
        )
        self.assertEqual(by_name["Andro使用AnimatedVectorDrawables处理线路转换.md"], "用 AnimatedVectorDrawable 做路径形变")
        self.assertEqual(
            by_name["[译]Android架构组件 – 查看ViewModel – 第二部分.md"],
            "Android架构组件 – 查看ViewModel – 第二部分",
        )
        self.assertEqual(by_name["NoBuzz.md"], "NoBuzz：把 Claude 的腔调译回人话")
        names = [Path(item.relpath).name for item in entries]
        self.assertIn("DI101-Part1.md", names)
        self.assertNotIn("DI101 - 第一部分.md", names)
        for title in by_name.values():
            self.assertFalse(title.startswith("[译]"), title)
            self.assertFalse(title.startswith("【翻译】"), title)


if __name__ == "__main__":
    unittest.main()
