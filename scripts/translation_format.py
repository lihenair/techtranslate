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
