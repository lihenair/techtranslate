#!/usr/bin/env python3
"""Archive layout and README catalog for translations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from translation_format import FRONTMATTER_RE, TECH_DOMAINS, _parse_simple_yaml

EARLIER_BUCKET = "earlier"
NEW_ARCHIVE_START = "2026-08-01"
GITHUB_BLOB = "https://github.com/lihenair/techtranslate/blob/master"
DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DOMAIN_ORDER = (
    "ai",
    "security",
    "android",
    "mobile",
    "frontend",
    "backend",
    "devops",
    "systems",
    "other",
)
DOMAIN_HEADINGS = {
    "ai": "AI",
    "security": "安全",
    "android": "Android",
    "mobile": "移动",
    "frontend": "前端",
    "backend": "后端",
    "devops": "DevOps",
    "systems": "系统",
    "other": "其他",
}
README_TITLES = {
    "10-Claude-Code-Steering-Mechanisms-That-Stop-Agents-From-Ignoring-Instructions.md": "阻止 Agent 忽略指令的 10 种 Claude Code 引导机制",
    "Android 7.1静态快捷方式.md": "Android 7.1 Static Shortcut",
    "Android Security-Welcome To Shell.md": "Android安全性: 欢迎来到Shell(权限)",
    "Android support Annotation.md": "Android support Annotation",
    "Android原生支持Java8的Lambdas表达式.md": "Android原生支持Java8的Lambdas表达式",
    "Annotation Processing in Android Studio.md": "Annotation Processing in Android Studio",
    "CompositionLocal-Made-Easy.md": "CompositionLocal-Made-Easy",
    "DI101-Part1.md": "DI101-第一部分",
    "Dagger 2 on producton—reducing methods count.md": "产品使用Dagger 2——减少方法数",
    "How JPG Works.md": "JPG如何工作的",
    "How WebP Works.md": "WebP是如何工作的(有损模式)",
    "I-Built-a-10-MB-GPU-Accelerated-Terminal-in-Rust-Metal.md": "我用 Rust + Metal 做了个 10 MB 的 GPU 加速终端",
    "Jack和Jill的阴暗面.md": "Jack和Jill的阴暗面",
    "Java注解.md": "Java注解",
    "Keeping Android runtime permissions from cluttering your app (Headless Dialog Fragments!).md": "Keeping Android runtime permissions from cluttering your app (Headless Dialog Fragments!)",
    "Kotlin Contract.md": "Kotlin Contracts",
    "No More findViewById.md": "No More findViewById",
    "NoBuzz.md": "NoBuzz",
    "Playing with Java annotation processing.md": "把玩Java注解处理",
    "Recomposition-Made-Easy.md": "Recomposition-Made-Easy",
    "Using Dagger 2.md": "Android项目使用Dagger2进行依赖注入",
    "annotation.html": "Annotation",
    "使用Dagger 2进行依赖注入.md": "使用Dagger 2进行依赖注入 - API介绍",
    "使用Gradle额外属性管理Android依赖版本.md": "使用Gradle额外属性管理Android依赖版本",
    "使用Picasso加载图片.md": "使用Picasso加载图片",
    "展现模式比较.md": "展示模式架构比较MVP(SC)，MVP(PV)，PM，MVVM和MVC",
    "异步布局加载.md": "异步布局加载",
    "探索Android ConstraintLayout.md": "探索Android ConstraintLayout",
    "有效地减少方法数.md": "有效地减少方法数",
    "路由器.md": "Router——一切都在正确的位置 映射功能到应用的组件",
    "鼓捣RxAnroid-介绍.md": "鼓捣RxAndroid--介绍",
}
LEGACY_DOMAINS = {
    "Android Security-Welcome To Shell.md": "security",
    "How JPG Works.md": "systems",
    "How WebP Works.md": "systems",
    "I-Built-a-10-MB-GPU-Accelerated-Terminal-in-Rust-Metal.md": "systems",
    "Java注解.md": "backend",
    "从SQLite压缩性能：插入.md": "backend",
    "潜入字节码操作：使用ASM和Javassist创建审核日志.md": "backend",
    "理解协程，JVM线程和并发问题.md": "backend",
    "10-Claude-Code-Steering-Mechanisms-That-Stop-Agents-From-Ignoring-Instructions.md": "ai",
    "NoBuzz.md": "ai",
}
SKIP_ROOT_NAMES = {"README.md", "AGENTS.md"}
CATALOG_START = "<!-- catalog:start -->"
CATALOG_END = "<!-- catalog:end -->"


@dataclass(frozen=True)
class CatalogEntry:
    title: str
    relpath: str
    date: str
    domain: str


def archive_relpath(translated_at: str | None, tech_domain: str, filename: str) -> str:
    domain = tech_domain if tech_domain in TECH_DOMAINS else "other"
    date_dir = EARLIER_BUCKET
    if translated_at and DATE_DIR_RE.match(translated_at) and translated_at >= NEW_ARCHIVE_START:
        date_dir = translated_at
    return str(Path("archive") / date_dir / domain / filename)


def github_blob_url(relpath: str) -> str:
    encoded = "/".join(quote(part, safe="") for part in Path(relpath).parts)
    return f"{GITHUB_BLOB}/{encoded}"


def _title_from_text(text: str, filename: str) -> str:
    if filename in README_TITLES:
        return README_TITLES[filename]
    match = FRONTMATTER_RE.match(text)
    if match:
        title = _parse_simple_yaml(match.group(1)).get("title", "").strip()
        if title:
            return title
    heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if heading:
        return heading.group(1).strip().rstrip("#").strip()
    return Path(filename).stem


def _load_earlier_meta(earlier_dir: Path) -> dict[str, tuple[str, str]]:
    dates_file = earlier_dir / "dates.tsv"
    meta: dict[str, tuple[str, str]] = {}
    if not dates_file.is_file():
        return meta
    for raw in dates_file.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        key, date = parts[0], parts[1]
        title = parts[2] if len(parts) > 2 else ""
        meta[key] = (date, title)
    return meta


def scan_archive(repo_root: Path) -> list[CatalogEntry]:
    archive = repo_root / "archive"
    if not archive.is_dir():
        return []
    earlier_meta = _load_earlier_meta(archive / EARLIER_BUCKET)
    entries: list[CatalogEntry] = []
    for path in sorted(archive.rglob("*")):
        if path.suffix not in {".md", ".html"} or not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        parts = rel.parts
        if len(parts) < 4:
            continue
        date_dir, domain, filename = parts[1], parts[2], parts[-1]
        if domain not in TECH_DOMAINS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        title = _title_from_text(text, filename)
        if DATE_DIR_RE.match(date_dir):
            date = date_dir
        else:
            key = f"{domain}/{filename}"
            date, extra_title = earlier_meta.get(key, ("较早", ""))
            if extra_title:
                title = extra_title
        entries.append(CatalogEntry(title=title, relpath=str(rel), date=date, domain=domain))
    return entries


def _date_sort_key(date: str) -> tuple[int, str]:
    if DATE_DIR_RE.match(date):
        return (1, date)
    return (0, date)


def render_catalog(entries: list[CatalogEntry]) -> str:
    by_domain: dict[str, list[CatalogEntry]] = {domain: [] for domain in DOMAIN_ORDER}
    for item in entries:
        by_domain.setdefault(item.domain, []).append(item)
    blocks: list[str] = []
    for domain in DOMAIN_ORDER:
        group = by_domain.get(domain) or []
        if not group:
            continue
        group = sorted(group, key=lambda item: (_date_sort_key(item.date), item.title), reverse=True)
        lines = [f"### {DOMAIN_HEADINGS.get(domain, domain)}", ""]
        for item in group:
            lines.append(f"- {item.date} [{item.title}]({github_blob_url(item.relpath)})")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def replace_catalog(readme: str, catalog: str) -> str:
    pattern = re.compile(
        re.escape(CATALOG_START) + r".*?" + re.escape(CATALOG_END),
        re.DOTALL,
    )
    block = f"{CATALOG_START}\n\n{catalog.rstrip()}\n\n{CATALOG_END}"
    if not pattern.search(readme):
        return readme.rstrip() + "\n\n" + block + "\n"
    return pattern.sub(block, readme)


def write_readme_catalog(repo_root: Path) -> None:
    readme_path = repo_root / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    readme_path.write_text(
        replace_catalog(text, render_catalog(scan_archive(repo_root))),
        encoding="utf-8",
    )


def domain_for_filename(filename: str) -> str:
    return LEGACY_DOMAINS.get(filename, "android")
