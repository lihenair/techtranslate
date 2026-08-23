#!/usr/bin/env python3
"""Queue translations the same way a GitHub Issue form would."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import article_tools  # noqa: E402


def _requests_from_args(urls: list[str], pairs: list[str], title_zh: str | None) -> list[dict[str, str | None]]:
    requests: list[dict[str, str | None]] = []
    for index, url in enumerate(urls):
        parsed = article_tools.parse_issue_requests(url)
        if not parsed:
            continue
        if index == 0 and title_zh and not parsed[0]["title_zh"]:
            parsed[0]["title_zh"] = title_zh
        requests.extend(parsed)
    for raw in pairs:
        parsed = article_tools.parse_issue_requests(raw)
        requests.extend(parsed)
    seen: set[str] = set()
    unique: list[dict[str, str | None]] = []
    for item in requests:
        url = item.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        unique.append(item)
    return unique


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Format or create a [Translate] GitHub issue from URLs"
    )
    parser.add_argument("--url", action="append", default=[], help="Article URL (repeatable)")
    parser.add_argument(
        "--pair",
        action="append",
        default=[],
        help="One line: URL or URL | 中文标题",
    )
    parser.add_argument("--title-zh", help="Chinese title for the first --url")
    parser.add_argument("--notes")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create the GitHub issue with gh (triggers the Translate article Action)",
    )
    parser.add_argument("--repo", default="lihenair/techtranslate")
    args = parser.parse_args(argv)

    requests = _requests_from_args(args.url, args.pair, args.title_zh)
    if not requests:
        print("No article URLs found.", file=sys.stderr)
        return 1
    title, body = article_tools.format_translate_issue(requests, notes=args.notes)
    payload = {"title": title, "body": body, "requests": requests}
    if not args.create:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        args.repo,
        "--title",
        title,
        "--body",
        body,
    ]
    try:
        created = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        print(detail.strip() or "gh issue create failed", file=sys.stderr)
        json.dump({**payload, "created": False}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 1
    url = created.stdout.strip()
    json.dump({**payload, "created": True, "issue_url": url}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
