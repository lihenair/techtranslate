#!/usr/bin/env python3
"""Convert short inbox media into GIFs. Skip clips longer than 15s."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, url2pathname, urlopen

import article_tools
import translation_format

COMMENT_RE = re.compile(r"<!--\s*media:([a-z0-9-]+)([^>]*)-->")
ATTR_RE = re.compile(r'([a-z0-9_]+)="([^"]*)"')
DIRECT_MEDIA_RE = re.compile(r"\.(mp4|webm|mov|m4v|ogv)(?:[?#]|$)", re.I)
USER_AGENT = (
    "Mozilla/5.0 (compatible; techtranslate-bot/1.0; +https://github.com/lihenair/techtranslate)"
)
GIF_ENCODE_STEPS = (
    {"fps": 8, "width": 640},
    {"fps": 6, "width": 480},
    {"fps": 6, "width": 320},
    {"fps": 4, "width": 320, "max_colors": 64},
    {"fps": 4, "width": 240, "max_colors": 48, "dither": "none"},
)
COOKIES_ENV = "TECHTRANSLATE_YTDLP_COOKIES"
YOUTUBE_API_KEY_ENV = "YOUTUBE_API_KEY"
YOUTUBE_THUMB_URL = "https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
YOUTUBE_PAGE_DURATION_RES = (
    re.compile(r'"lengthSeconds"\s*:\s*"(\d+)"'),
    re.compile(r'"approxDurationMs"\s*:\s*"(\d+)"'),
)


def parse_media_comments(markdown: str) -> list[dict[str, str]]:
    markers: list[dict[str, str]] = []
    for match in COMMENT_RE.finditer(markdown or ""):
        item = {"kind": match.group(1)}
        for key, value in ATTR_RE.findall(match.group(2) or ""):
            item[key] = value
        markers.append(item)
    return markers


def probe_duration_seconds(path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not path.is_file():
        return None
    try:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return float(proc.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def encode_gif(
    src: Path,
    dest: Path,
    fps: int = 8,
    width: int = 640,
    max_colors: int | None = None,
    dither: str | None = None,
) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    palette = "palettegen" if not max_colors else f"palettegen=max_colors={max_colors}"
    use = "paletteuse" if not dither else f"paletteuse=dither={dither}"
    filt = f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]{palette}[p];[s1][p]{use}"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-vf", filt, "-loop", "0", str(dest)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        return False
    return dest.is_file() and dest.stat().st_size > 0


def encode_gif_under_limit(src: Path, dest: Path, max_bytes: int) -> bool:
    for step in GIF_ENCODE_STEPS:
        if encode_gif(src, dest, **step) and dest.is_file() and dest.stat().st_size <= max_bytes:
            return True
        dest.unlink(missing_ok=True)
    return False


def convert_local_video(
    src: Path,
    dest: Path,
    duration_s: float | None = None,
    require_existing_src: bool = True,
    max_bytes: int | None = None,
) -> str:
    if duration_s is None and require_existing_src:
        duration_s = probe_duration_seconds(src)
    if not translation_format.should_convert_source(duration_s):
        return "skipped-unknown" if duration_s is None else "skipped-long"
    if not shutil.which("ffmpeg"):
        return "skipped-no-ffmpeg"
    if require_existing_src and not src.is_file():
        return "skipped-unknown"
    if max_bytes is None:
        if encode_gif(src, dest):
            return "converted"
        dest.unlink(missing_ok=True)
        return "skipped-unknown"
    if encode_gif_under_limit(src, dest, max_bytes):
        return "converted"
    dest.unlink(missing_ok=True)
    return "skipped-too-large"


def _ytdlp_cmd() -> list[str] | None:
    binary = shutil.which("yt-dlp")
    if binary:
        return [binary]
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        return None
    return [sys.executable, "-m", "yt_dlp"]


def ytdlp_extra_args() -> list[str]:
    args: list[str] = []
    cookies = os.environ.get(COOKIES_ENV, "").strip()
    if cookies and Path(cookies).is_file():
        args.extend(["--cookies", cookies])
    return args


def _http_get_text(url: str, timeout: int = 20) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/plain,*/*"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read()
        final_url = response.geturl()
    return final_url, raw.decode(charset, errors="replace")


def probe_youtube_api_duration(video_id: str, api_key: str, getter=None) -> float | None:
    if not video_id or not api_key:
        return None
    get = getter or _http_get_text
    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?part=contentDetails&id={video_id}&key={api_key}"
    )
    try:
        _final, body = get(url, timeout=20)
        data = json.loads(body)
        items = data.get("items") or []
        duration = ((items[0] or {}).get("contentDetails") or {}).get("duration")
        return translation_format.parse_iso8601_duration(duration or "")
    except (OSError, ValueError, IndexError, TypeError, json.JSONDecodeError):
        return None


def probe_remote_duration(
    url: str,
    runner=None,
    youtube_api_key: str | None = None,
    http_get=None,
) -> float | None:
    run = runner or subprocess.run
    cmd = _ytdlp_cmd()
    if runner is not None or cmd:
        prefix = cmd or ["yt-dlp"]
        try:
            proc = run(
                [
                    *prefix,
                    *ytdlp_extra_args(),
                    "--print",
                    "%(duration)s",
                    "--skip-download",
                    "--no-warnings",
                    "--no-playlist",
                    url,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            line = (proc.stdout or "").strip().splitlines()[-1]
            if line.upper() not in {"", "NA", "NONE", "NULL", "N/A"}:
                return float(line)
        except (subprocess.CalledProcessError, ValueError, IndexError, FileNotFoundError, OSError):
            pass
    video_id = translation_format.youtube_id_from_url(url)
    key = (youtube_api_key if youtube_api_key is not None else os.environ.get(YOUTUBE_API_KEY_ENV, "")).strip()
    if video_id and key:
        api_duration = probe_youtube_api_duration(video_id, key, getter=http_get)
        if api_duration is not None:
            return api_duration
    if video_id:
        return probe_youtube_page_duration(video_id, http_get=http_get)
    return None


def download_remote_video(url: str, dest_dir: Path, runner=None) -> Path | None:
    run = runner or subprocess.run
    cmd = _ytdlp_cmd()
    if runner is None and not cmd:
        return None
    prefix = cmd or ["yt-dlp"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(dest_dir / "dl.%(ext)s")
    try:
        run(
            [
                *prefix,
                *ytdlp_extra_args(),
                "-f",
                "mp4/best[ext=mp4]/best",
                "-o",
                out_tmpl,
                "--no-warnings",
                "--no-playlist",
                url,
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    matches = sorted(dest_dir.glob("dl.*"))
    return matches[0] if matches else None


def looks_like_direct_media(url: str) -> bool:
    return bool(DIRECT_MEDIA_RE.search(urlparse(url).path))


def convert_remote_video(
    url: str,
    dest_gif: Path,
    probe=probe_remote_duration,
    download=download_remote_video,
) -> str:
    duration_s = probe(url)
    if duration_s is not None and not translation_format.should_convert_source(duration_s):
        return "skipped-long"
    if duration_s is None and not looks_like_direct_media(url):
        return "skipped-unknown"
    with tempfile.TemporaryDirectory() as tmp:
        downloaded = download(url, Path(tmp))
        if downloaded is None:
            return "skipped-unknown"
        return convert_local_video(downloaded, dest_gif, duration_s=duration_s)


def stitch_image_sequence(paths: list[Path], dest: Path) -> str:
    existing = [path for path in paths if path.is_file()]
    if len(existing) < 2:
        return "skipped-unknown"
    if len(existing) > translation_format.MAX_SEQUENCE_FRAMES:
        return "skipped-long"
    if not shutil.which("ffmpeg"):
        return "skipped-no-ffmpeg"
    with tempfile.TemporaryDirectory() as tmp:
        seq_dir = Path(tmp)
        for index, path in enumerate(existing):
            suffix = path.suffix if path.suffix else ".png"
            target = seq_dir / f"frame-{index:03d}{suffix}"
            shutil.copyfile(path, target)
        pattern = seq_dir / f"frame-%03d{existing[0].suffix if existing[0].suffix else '.png'}"
        src_pattern = seq_dir / "input.mp4"
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-framerate",
                    "8",
                    "-i",
                    str(pattern),
                    "-vf",
                    "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
                    str(src_pattern),
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            return "skipped-unknown"
        return convert_local_video(src_pattern, dest, duration_s=len(existing) / 8.0)


def _source_to_path(src: str) -> Path | None:
    if src.startswith("file://"):
        return Path(url2pathname(urlparse(src).path))
    path = Path(src)
    return path if path.is_file() else None


def _download_http_file(url: str, dest: Path) -> Path | None:
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=30) as response:
            dest.write_bytes(response.read())
        return dest if dest.is_file() and dest.stat().st_size > 0 else None
    except OSError:
        return None


def probe_youtube_page_duration(
    video_id: str,
    http_get=None,
) -> float | None:
    if not video_id:
        return None
    get = http_get or _http_get_text
    url = translation_format.youtube_watch_url(video_id)
    try:
        _final, body = get(url, timeout=20)
    except OSError:
        return None
    for index, pattern in enumerate(YOUTUBE_PAGE_DURATION_RES):
        match = pattern.search(body)
        if not match:
            continue
        value = float(match.group(1))
        return value / 1000.0 if index else value
    return None


def save_youtube_thumbnail(video_id: str, dest: Path) -> bool:
    if not video_id:
        return False
    thumb = dest if dest.suffix.lower() == ".jpg" else dest.with_suffix(".jpg")
    downloaded = _download_http_file(YOUTUBE_THUMB_URL.format(video_id=video_id), thumb)
    return downloaded is not None


def _write_recorded_frames(frames: list[Path], dest: Path) -> str:
    existing = [path for path in frames if path.is_file() and path.stat().st_size > 0]
    if not existing:
        return "skipped-unknown"
    dest = dest.with_suffix(".gif")
    return stitch_image_sequence(existing, dest)


def record_page_visual(
    url: str,
    dest: Path,
    seconds: float = 4.0,
    width: int = 800,
    height: int = 400,
    playwright_factory=...,
) -> str:
    duration = min(max(seconds, 0.2), translation_format.MAX_SOURCE_SECONDS)
    if playwright_factory is None:
        return "skipped-no-browser"
    factory = playwright_factory
    if factory is ...:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return "skipped-no-browser"
        factory = sync_playwright
    if not url:
        return "skipped-unknown"
    try:
        with factory() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": int(width), "height": int(height)})
            try:
                page.goto(url, wait_until="networkidle", timeout=60_000)
            except Exception:
                page.goto(url, wait_until="load", timeout=60_000)
            page.wait_for_timeout(400)
            target = page.locator("#app, svg, canvas, body > *").first
            with tempfile.TemporaryDirectory() as tmp:
                frames: list[Path] = []
                count = max(2, int(duration * 8))
                for index in range(count):
                    frame = Path(tmp) / f"{index:03d}.png"
                    try:
                        if target.count() > 0:
                            target.screenshot(path=str(frame))
                        else:
                            page.screenshot(path=str(frame))
                    except Exception:
                        page.screenshot(path=str(frame))
                    frames.append(frame)
                    page.wait_for_timeout(125)
                browser.close()
                return _write_recorded_frames(frames, dest)
    except Exception:  # noqa: BLE001 - recording is best-effort
        dest.unlink(missing_ok=True)
        dest.with_suffix(".png").unlink(missing_ok=True)
        return "skipped-no-browser"


def convert_svg(
    src: str,
    dest: Path,
    playwright_factory=...,
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        local = _source_to_path(src)
        if local is None and src.startswith(("http://", "https://")):
            local = _download_http_file(src, Path(tmp) / "in.svg")
        if local is None or not local.is_file():
            return "skipped-unknown"
        text = local.read_text(encoding="utf-8", errors="replace")
        animated = bool(re.search(r"<animate|animation(?:-)|@keyframes", text, re.I))
        html_path = Path(tmp) / "svg.html"
        html_path.write_text(
            "<!doctype html><html><head><meta charset=\"utf-8\"></head>"
            f"<body>{text}</body></html>",
            encoding="utf-8",
        )
        seconds = 4.0 if animated else 0.3
        return record_page_visual(
            html_path.as_uri(),
            dest,
            seconds=seconds,
            playwright_factory=playwright_factory,
        )


def record_section_html(
    html: str,
    dest: Path,
    seconds: float = 4.0,
    playwright_factory=...,
) -> str:
    duration = min(max(seconds, 0.2), translation_format.MAX_SOURCE_SECONDS)
    if playwright_factory is None:
        return "skipped-no-browser"
    factory = playwright_factory
    if factory is ...:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return "skipped-no-browser"
        factory = sync_playwright
    try:
        with factory() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(
                viewport={"width": 640, "height": 360},
                java_script_enabled=False,
            )
            try:
                page.set_content(html, wait_until="networkidle")
            except Exception:
                page.set_content(html, wait_until="load")
            target = page.locator("body > *").first
            with tempfile.TemporaryDirectory() as tmp:
                frames: list[Path] = []
                count = max(2, int(duration * 8))
                for index in range(count):
                    frame = Path(tmp) / f"{index:03d}.png"
                    try:
                        if target.count() > 0:
                            target.screenshot(path=str(frame))
                        else:
                            page.screenshot(path=str(frame))
                    except Exception:
                        page.screenshot(path=str(frame))
                    frames.append(frame)
                    page.wait_for_timeout(125)
                browser.close()
                return stitch_image_sequence(frames, dest)
    except Exception:  # noqa: BLE001 - recording is best-effort
        dest.unlink(missing_ok=True)
        return "skipped-no-browser"


def _inbox_slug(text: str, source: Path) -> str:
    url_match = re.search(r"^source_url:\s+(\S+)", text, re.MULTILINE)
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return article_tools.slug_from_url(
        url_match.group(1) if url_match else source.stem,
        title_match.group(1) if title_match else None,
    )


def process_inbox(inbox_dir: Path, repo_root: Path) -> dict:
    report: dict = {"items": []}
    if not inbox_dir.is_dir():
        return report
    media_count = 0
    for source in sorted(inbox_dir.glob("*.source.md")):
        text = source.read_text(encoding="utf-8")
        slug = _inbox_slug(text, source)
        video_index = 0
        section_index = 0
        svg_index = 0
        for marker in parse_media_comments(text):
            if media_count >= translation_format.MAX_MEDIA_FILES:
                report["items"].append({"file": source.name, "kind": marker.get("kind"), "status": "skipped-limit"})
                continue
            kind = marker.get("kind")
            status = "skipped-unknown"
            dest = Path()
            if kind == "youtube":
                video_id = marker.get("id") or translation_format.youtube_id_from_url(marker.get("url") or "") or "video"
                dest = repo_root / "assets" / slug / f"yt-{video_id}.gif"
                url = marker.get("url") or translation_format.youtube_watch_url(video_id)
                status = convert_remote_video(url, dest)
                thumb_dest = repo_root / "assets" / slug / f"yt-{video_id}.jpg"
                item: dict[str, str] = {"file": source.name, "kind": kind, "status": status, "dest": ""}
                if status == "converted":
                    media_count += 1
                    written = dest
                    item["dest"] = str(written.relative_to(repo_root))
                elif save_youtube_thumbnail(video_id, thumb_dest):
                    item["status"] = "thumbnail"
                    item["dest"] = str(thumb_dest.relative_to(repo_root))
                report["items"].append(item)
                continue
            elif kind == "twitter":
                status_id = marker.get("id") or translation_format.twitter_status_from_url(marker.get("url") or "") or "tweet"
                dest = repo_root / "assets" / slug / f"tw-{status_id}.gif"
                url = marker.get("url") or translation_format.twitter_status_url(status_id)
                status = convert_remote_video(url, dest)
            elif kind == "video-gif":
                video_index += 1
                dest = repo_root / "assets" / slug / f"video-{video_index}.gif"
                src = marker.get("src") or ""
                local = _source_to_path(src)
                if local is not None:
                    status = convert_local_video(local, dest)
                elif src.startswith(("http://", "https://")):
                    status = convert_remote_video(src, dest)
                else:
                    status = "skipped-unknown"
            elif kind == "frames":
                section_index += 1
                dest = repo_root / "assets" / slug / f"section-{section_index}.gif"
                urls = [part for part in (marker.get("src") or "").split("|") if part]
                with tempfile.TemporaryDirectory() as tmp:
                    frames: list[Path] = []
                    for index, url in enumerate(urls):
                        local = _source_to_path(url)
                        if local is None and url.startswith(("http://", "https://")):
                            guessed = Path(urlparse(url).path).suffix or ".png"
                            local_path = Path(tmp) / f"{index:03d}{guessed}"
                            local = _download_http_file(url, local_path)
                        if local is not None:
                            frames.append(local)
                    status = stitch_image_sequence(frames, dest)
            elif kind == "section-anim":
                section_index += 1
                dest = repo_root / "assets" / slug / f"section-{section_index}.gif"
                rel = marker.get("file") or f"media/{slug}-{marker.get('index') or section_index}.html"
                snippet = inbox_dir / rel
                seconds = 4.0
                try:
                    seconds = float(marker.get("duration_s") or "4")
                except ValueError:
                    seconds = 4.0
                if snippet.is_file():
                    status = record_section_html(snippet.read_text(encoding="utf-8"), dest, seconds=seconds)
                else:
                    status = "skipped-no-browser"
            elif kind == "page-visual":
                section_index += 1
                visual_id = re.sub(
                    r"[^A-Za-z0-9._-]+",
                    "-",
                    marker.get("id") or str(section_index),
                ).strip("-._") or str(section_index)
                dest = repo_root / "assets" / slug / f"visual-{visual_id}.gif"
                seconds = 4.0
                try:
                    seconds = float(marker.get("duration_s") or "4")
                except ValueError:
                    seconds = 4.0
                width = 800
                height = 400
                try:
                    width = int(marker.get("width") or "800")
                    height = int(marker.get("height") or "400")
                except ValueError:
                    width, height = 800, 400
                status = record_page_visual(
                    marker.get("url") or "",
                    dest,
                    seconds=seconds,
                    width=width,
                    height=height,
                )
            elif kind == "svg":
                svg_index += 1
                dest = repo_root / "assets" / slug / f"svg-{svg_index}.gif"
                status = convert_svg(marker.get("src") or "", dest)
            else:
                report["items"].append({"file": source.name, "kind": kind, "status": "skipped-unknown"})
                continue
            if status == "converted":
                media_count += 1
            written = dest if dest.is_file() else dest.with_suffix(".png")
            report["items"].append(
                {
                    "file": source.name,
                    "kind": kind,
                    "status": status,
                    "dest": str(written.relative_to(repo_root))
                    if status == "converted" and written.is_file()
                    else "",
                }
            )
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Convert short inbox media to GIFs")
    parser.add_argument("--inbox", default="_inbox")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    report = process_inbox((repo_root / args.inbox).resolve(), repo_root)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
