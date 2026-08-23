#!/usr/bin/env python3
"""Shared translation-format constants and checks."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

TECH_DOMAINS = frozenset(
    {
        "android",
        "frontend",
        "backend",
        "security",
        "mobile",
        "devops",
        "ai",
        "systems",
        "other",
    }
)
# Title-weighted. Generic words such as agent/prompt/compose are not signals.
_DOMAIN_SIGNALS = (
    (
        "ai",
        (
            r"\bclaude\b",
            r"\bgpt[- ]?\d",
            r"\bllms?\b",
            r"anthropic",
            r"openai",
            r"langchain",
            r"\bai agents?\b",
            r"coding agents?",
            r"\bai chip",
            r"^ai\b",
            r"\bai [a-z]",
            r"transformer",
            r"neural network",
            r"machine learning",
            r"大模型",
            r"提示词工程",
        ),
    ),
    (
        "security",
        (
            r"\bxss\b",
            r"exploit",
            r"cve-\d",
            r"sanitiz",
            r"\brce\b",
            r"\bcsrf\b",
            r"\bcsp\b",
            r"vulnerabilit",
            r"\boauth\b",
            r"\bjwt\b",
            r"漏洞",
        ),
    ),
    (
        "android",
        (r"\bandroid\b", r"jetpack", r"\bdagger\b", r"recyclerview", r"jetpack compose"),
    ),
    (
        "mobile",
        (r"\bios\b", r"swiftui", r"\bflutter\b", r"react native", r"kotlin multiplatform"),
    ),
    (
        "frontend",
        (
            r"\bcss\b",
            r"\breact\b",
            r"\bvue\b",
            r"\bdom\b",
            r"\bbrowser\b",
            r"\bjavascript\b",
            r"\btypescript\b",
            r"\bhtml5\b",
            r"\bflexbox\b",
            r"\bwebpack\b",
        ),
    ),
    (
        "devops",
        (
            r"kubernetes",
            r"\bk8s\b",
            r"ci/?cd",
            r"terraform",
            r"\bhelm\b",
            r"github actions",
            r"\bdocker\b",
            r"prometheus",
        ),
    ),
    (
        "systems",
        (
            r"computer architecture",
            r"microarchitecture",
            r"体系结构",
            r"\bisa\b",
            r"\bcpi\b",
            r"\bilp\b",
            r"roofline",
            r"amdahls?",
            r"tomasulo",
            r"\bmesi\b",
            r"pipelining",
            r"out-of-order",
            r"instruction set",
            r"cache coherence",
            r"memory hierarchy",
            r"\bhbm\b",
            r"\bsystolic\b",
            r"\bgpu-accelerated\b",
            r"\bmetal shader\b",
            r"terminal emulator",
            r"operating systems?",
            r"操作系统",
            r"\bcompilers?\b",
            r"编译器",
            r"filesystems?",
            r"virtual memory",
            r"\btlb\b",
            r"page tables?",
            r"register allocation",
            r"\blexing\b",
            r"\bcodegen\b",
            r"\brisc-v\b",
            r"\bx86[-_]?64\b",
            r"\bmicroprocessor\b",
            r"\bjp[e]?g\b",
            r"\bwebp\b",
            r"\bavif\b",
            r"image codec",
            r"\bcodecs?\b",
            r"lossy compression",
            r"图像编码",
            r"编解码",
        ),
    ),
    (
        "backend",
        (
            r"\bjvm\b",
            r"postgres",
            r"\bredis\b",
            r"\bgrpc\b",
            r"\bspring\b",
            r"\bapi\b server",
            r"\bmicroservices?\b",
            r"\bmysql\b",
            r"\bmongodb\b",
            r"\bsharding\b",
            r"pgbouncer",
            r"\bvitess\b",
        ),
    ),
)
_TITLE_WEIGHT = 3
_TIE_BREAK = (
    "security",
    "ai",
    "android",
    "mobile",
    "devops",
    "systems",
    "frontend",
    "backend",
    "other",
)
MAX_SOURCE_SECONDS = 15.0
MAX_GIF_BYTES = 1_500_000
MAX_MEDIA_FILES = 16
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
TWITTER_STATUS_RE = re.compile(r"/status(?:es)?/(\d+)")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ANIM_CLASS_RE = re.compile(r"\b(gif|animat|demo|frames|loop)\b", re.I)
TWITTER_CLASS_RE = re.compile(r"\b(twitter-tweet|twitter-embed|tweet)\b", re.I)


def youtube_id_from_url(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if host in {"youtu.be", "www.youtu.be"}:
        candidate = parsed.path.lstrip("/").split("/")[0]
    elif "youtube.com" in host:
        parts = parsed.path.split("/")
        if parsed.path.startswith("/embed/") or parsed.path.startswith("/shorts/"):
            candidate = parts[2] if len(parts) > 2 else ""
        else:
            candidate = parse_qs(parsed.query).get("v", [""])[0]
    else:
        return None
    candidate = candidate.split("?")[0]
    return candidate if YOUTUBE_ID_RE.match(candidate) else None


def youtube_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def twitter_status_from_url(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    twitter_hosts = {
        "twitter.com",
        "www.twitter.com",
        "mobile.twitter.com",
        "x.com",
        "www.x.com",
        "platform.twitter.com",
        "syndication.twitter.com",
    }
    if host not in twitter_hosts:
        return None
    match = TWITTER_STATUS_RE.search(parsed.path)
    if match:
        return match.group(1)
    tweet_id = parse_qs(parsed.query).get("id", [""])[0]
    return tweet_id if tweet_id.isdigit() else None


def twitter_status_url(status_id: str) -> str:
    return f"https://x.com/i/status/{status_id}"


def looks_like_twitter_class(class_name: str) -> bool:
    return bool(TWITTER_CLASS_RE.search(class_name or ""))


def embed_link(platform: str, url: str) -> str:
    return f"[嵌入内容（原站 {platform}）]({url})"


def heading_md(level: int, title_zh: str, slug: str) -> str:
    hashes = "#" * max(1, min(level, 6))
    return f"{hashes} [{title_zh}](#{slug})"


ISO8601_DURATION_RE = re.compile(
    r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?$",
    re.I,
)


def _domain_score(patterns: tuple[str, ...], title: str, body: str) -> int:
    title_l = title.lower()
    body_l = body.lower()
    score = 0
    for pattern in patterns:
        if re.search(pattern, title_l):
            score += _TITLE_WEIGHT
        elif re.search(pattern, body_l):
            score += 1
    return score


def classify_tech_domain(title: str, body: str = "") -> str:
    """Infer tech_domain from the primary topic. Return other only when nothing matches."""
    scored = [
        (_domain_score(patterns, title, body), domain)
        for domain, patterns in _DOMAIN_SIGNALS
    ]
    scored = [(score, domain) for score, domain in scored if score > 0]
    if not scored:
        return "other"
    best = max(score for score, _ in scored)
    tied = [domain for score, domain in scored if score == best]
    if len(tied) == 1:
        return tied[0]
    return min(tied, key=lambda domain: _TIE_BREAK.index(domain))


def parse_iso8601_duration(text: str) -> float | None:
    match = ISO8601_DURATION_RE.fullmatch((text or "").strip())
    if not match or not any(match.groups()):
        return None
    hours = float(match.group(1) or 0)
    minutes = float(match.group(2) or 0)
    seconds = float(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def should_convert_source(duration_s: float | None) -> bool:
    if duration_s is None:
        return False
    return duration_s <= MAX_SOURCE_SECONDS


def looks_like_anim_class(class_name: str) -> bool:
    return bool(ANIM_CLASS_RE.search(class_name or ""))


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
