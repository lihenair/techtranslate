#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import capture_media  # noqa: E402


def _have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def _write_rgb_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    import struct
    import zlib

    raw = b"".join(b"\x00" + (bytes(rgb) * width) for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _make_color_mp4(path: Path, seconds: float) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=red:s=64x64:d={seconds}",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ],
        check=True,
        capture_output=True,
    )


class ParseCommentsTest(unittest.TestCase):
    def test_parses_youtube_and_video_markers(self) -> None:
        text = """
<!-- media:youtube id="fG8xWTHnlLY" url="https://www.youtube.com/watch?v=fG8xWTHnlLY" -->
<!-- media:video-gif src="https://example.com/loop.webm" -->
"""
        markers = capture_media.parse_media_comments(text)
        self.assertEqual(markers[0]["kind"], "youtube")
        self.assertEqual(markers[0]["id"], "fG8xWTHnlLY")
        self.assertEqual(markers[1]["kind"], "video-gif")
        self.assertEqual(markers[1]["src"], "https://example.com/loop.webm")


@unittest.skipUnless(_have_ffmpeg(), "ffmpeg/ffprobe required")
class GifEncodeTest(unittest.TestCase):
    def test_converts_short_clip_and_skips_long_clip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            short = Path(tmp) / "short.mp4"
            long = Path(tmp) / "long.mp4"
            short_gif = Path(tmp) / "short.gif"
            long_gif = Path(tmp) / "long.gif"
            _make_color_mp4(short, 1)
            _make_color_mp4(long, 16)
            self.assertEqual(capture_media.convert_local_video(short, short_gif), "converted")
            self.assertTrue(short_gif.is_file())
            self.assertGreater(short_gif.stat().st_size, 0)
            self.assertEqual(capture_media.convert_local_video(long, long_gif), "skipped-long")
            self.assertFalse(long_gif.exists())


class GifEncodeFallbackTest(unittest.TestCase):
    def test_default_convert_keeps_gif_over_old_byte_cap(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.mp4"
            dest = Path(tmp) / "out.gif"
            _make_color_mp4(src, 1)
            original = capture_media.encode_gif

            def fat_encode(src_path, dest_path, **_kwargs):
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_bytes(b"GIF89a" + b"x" * 2_000_000)
                return True

            capture_media.encode_gif = fat_encode
            try:
                status = capture_media.convert_local_video(src, dest, duration_s=1)
            finally:
                capture_media.encode_gif = original
            self.assertEqual(status, "converted")
            self.assertTrue(dest.is_file())
            self.assertGreater(dest.stat().st_size, 1_500_000)

    def test_encode_ladder_shrinks_until_under_limit(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.mp4"
            dest = Path(tmp) / "out.gif"
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc=size=640x360:rate=25:duration=4",
                    "-pix_fmt",
                    "yuv420p",
                    str(src),
                ],
                check=True,
                capture_output=True,
            )
            status = capture_media.convert_local_video(src, dest, max_bytes=200_000)
            self.assertEqual(status, "converted")
            self.assertTrue(dest.is_file())
            self.assertLessEqual(dest.stat().st_size, 200_000)

    def test_encode_ladder_skips_when_every_step_is_too_large(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.mp4"
            dest = Path(tmp) / "out.gif"
            _make_color_mp4(src, 1)
            status = capture_media.convert_local_video(src, dest, max_bytes=10)
            self.assertEqual(status, "skipped-too-large")
            self.assertFalse(dest.exists())

    def test_unknown_duration_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "x.gif"
            status = capture_media.convert_local_video(
                Path(tmp) / "missing.mp4",
                dest,
                duration_s=None,
                require_existing_src=False,
            )
            self.assertEqual(status, "skipped-unknown")
            self.assertFalse(dest.exists())


class RemoteVideoTest(unittest.TestCase):
    def test_probe_and_skip_use_injected_runner(self) -> None:
        def fake_run(cmd, **kwargs):
            if "--print" in cmd:
                class R:
                    stdout = "9.0\n"
                    returncode = 0

                return R()
            raise AssertionError(cmd)

        self.assertEqual(
            capture_media.probe_remote_duration("https://youtu.be/aaaaaaaaaaa", runner=fake_run),
            9.0,
        )
        status = capture_media.convert_remote_video(
            "https://youtu.be/aaaaaaaaaaa",
            Path("/tmp/no-such-yt.gif"),
            probe=lambda url: 40.0,
            download=lambda url, dest_dir: Path("/tmp/missing.mp4"),
        )
        self.assertEqual(status, "skipped-long")

    def test_probe_falls_back_to_youtube_api(self) -> None:
        def fail_run(*_args, **_kwargs):
            raise FileNotFoundError("yt-dlp blocked")

        def fake_get(url: str, timeout: int = 20):
            self.assertIn("googleapis.com/youtube/v3/videos", url)
            self.assertIn("key=test-key", url)
            self.assertIn("fG8xWTHnlLY", url)
            payload = {"items": [{"contentDetails": {"duration": "PT9S"}}]}
            return url, json.dumps(payload)

        duration = capture_media.probe_remote_duration(
            "https://www.youtube.com/watch?v=fG8xWTHnlLY",
            runner=fail_run,
            youtube_api_key="test-key",
            http_get=fake_get,
        )
        self.assertEqual(duration, 9.0)

    def test_ytdlp_args_include_cookies_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cookies = Path(tmp) / "cookies.txt"
            cookies.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
            old = os.environ.get("TECHTRANSLATE_YTDLP_COOKIES")
            os.environ["TECHTRANSLATE_YTDLP_COOKIES"] = str(cookies)
            try:
                args = capture_media.ytdlp_extra_args()
            finally:
                if old is None:
                    os.environ.pop("TECHTRANSLATE_YTDLP_COOKIES", None)
                else:
                    os.environ["TECHTRANSLATE_YTDLP_COOKIES"] = old
        self.assertIn("--cookies", args)
        self.assertIn(str(cookies), args)

    def test_unknown_remote_duration_is_skipped(self) -> None:
        status = capture_media.convert_remote_video(
            "https://youtu.be/aaaaaaaaaaa",
            Path("/tmp/no-such-yt.gif"),
            probe=lambda url: None,
            download=lambda url, dest_dir: None,
        )
        self.assertEqual(status, "skipped-unknown")

    def test_probe_youtube_page_duration_reads_length_seconds(self) -> None:
        def fake_get(url: str, timeout: int = 20):
            return url, '{"videoDetails":{"lengthSeconds":"612"}}'

        duration = capture_media.probe_youtube_page_duration("abc123", http_get=fake_get)
        self.assertEqual(duration, 612.0)

    def test_save_youtube_thumbnail_downloads_hqdefault(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "yt-abc.gif"

            def fake_download(url: str, path: Path) -> Path | None:
                self.assertIn("/vi/abc/hqdefault.jpg", url)
                path.write_bytes(b"jpeg")
                return path

            old = capture_media._download_http_file
            capture_media._download_http_file = fake_download
            try:
                self.assertTrue(capture_media.save_youtube_thumbnail("abc", dest))
                self.assertTrue(dest.with_suffix(".jpg").is_file())
            finally:
                capture_media._download_http_file = old

    def test_direct_mp4_converts_when_remote_duration_missing(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            dest = Path(tmp) / "out.gif"
            _make_color_mp4(clip, 1)
            status = capture_media.convert_remote_video(
                "https://example.com/loop.mp4",
                dest,
                probe=lambda url: None,
                download=lambda url, dest_dir: Path(shutil.copy(clip, Path(dest_dir) / "dl.mp4")),
            )
            self.assertEqual(status, "converted")
            self.assertTrue(dest.is_file())
            self.assertGreater(dest.stat().st_size, 0)


class ProcessInboxTest(unittest.TestCase):
    def test_process_inbox_converts_short_local_marker(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inbox = root / "_inbox"
            inbox.mkdir()
            clip = inbox / "clip.mp4"
            _make_color_mp4(clip, 1)
            (inbox / "Demo-Post.source.md").write_text(
                "---\nsource_url: https://example.com/demo-post\n---\n\n"
                f'<!-- media:video-gif src="{clip.as_uri()}" -->\n'
                '<!-- media:youtube id="fG8xWTHnlLY" url="https://www.youtube.com/watch?v=fG8xWTHnlLY" -->\n',
                encoding="utf-8",
            )
            report = capture_media.process_inbox(inbox, root)
            gif = root / "assets" / "demo-post" / "video-1.gif"
            statuses = {item["status"] for item in report["items"]}
            self.assertIn("converted", statuses)
            self.assertTrue(
                any(
                    item["status"] in {"skipped-unknown", "skipped-long", "thumbnail"}
                    for item in report["items"]
                    if item.get("kind") == "youtube"
                )
            )
            self.assertTrue(gif.is_file())


class StitchFramesTest(unittest.TestCase):
    def test_stitches_short_sequence_and_skips_long(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg required")
        with tempfile.TemporaryDirectory() as tmp:
            frames = []
            for i in range(3):
                png = Path(tmp) / f"{i}.png"
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "lavfi",
                        "-i",
                        "color=c=blue:s=32x32:d=0.1",
                        "-frames:v",
                        "1",
                        str(png),
                    ],
                    check=True,
                    capture_output=True,
                )
                frames.append(png)
            dest = Path(tmp) / "seq.gif"
            self.assertEqual(capture_media.stitch_image_sequence(frames, dest), "converted")
            self.assertTrue(dest.is_file())
            too_many = frames * 50
            self.assertGreater(len(too_many), 120)
            self.assertEqual(
                capture_media.stitch_image_sequence(too_many, Path(tmp) / "long.gif"),
                "skipped-long",
            )

    def test_stitches_frames_with_odd_height(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg required")
        with tempfile.TemporaryDirectory() as tmp:
            frames = []
            for i in range(3):
                png = Path(tmp) / f"{i}.png"
                _write_rgb_png(png, 80, 267, (0, 128, i * 40))
                frames.append(png)
            dest = Path(tmp) / "odd.gif"
            self.assertEqual(capture_media.stitch_image_sequence(frames, dest), "converted")
            self.assertTrue(dest.is_file())
            self.assertGreater(dest.stat().st_size, 0)


class RecordSectionTest(unittest.TestCase):
    def test_missing_playwright_is_skipped(self) -> None:
        status = capture_media.record_section_html(
            "<html><body><div>x</div></body></html>",
            Path("/tmp/no-section.gif"),
            playwright_factory=None,
        )
        self.assertEqual(status, "skipped-no-browser")

    def test_missing_playwright_skips_page_visual(self) -> None:
        status = capture_media.record_page_visual(
            "https://example.com/iframe#servers",
            Path("/tmp/no-visual.gif"),
            playwright_factory=None,
        )
        self.assertEqual(status, "skipped-no-browser")


class ProcessInboxVisualTest(unittest.TestCase):
    def test_process_inbox_converts_page_visual_and_svg(self) -> None:
        if not _have_ffmpeg():
            self.skipTest("ffmpeg/ffprobe required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inbox = root / "_inbox"
            inbox.mkdir()
            html = inbox / "servers.html"
            html.write_text(
                "<!doctype html><html><body><div id='app'>"
                "<svg width='80' height='40'><rect width='80' height='40' fill='navy'/></svg>"
                "</div></body></html>",
                encoding="utf-8",
            )
            svg = inbox / "cluster.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40">'
                '<rect width="80" height="40" fill="teal"/></svg>',
                encoding="utf-8",
            )
            (inbox / "Making-768-servers-look-like-1.source.md").write_text(
                "---\nsource_url: https://planetscale.com/blog/making-768-servers-look-like-1\n---\n\n"
                "# Making 768 servers look like 1\n\n"
                f'<!-- media:page-visual url="{html.as_uri()}" id="servers" duration_s="0.5" width="160" height="80" -->\n'
                f'<!-- media:svg src="{svg.as_uri()}" -->\n',
                encoding="utf-8",
            )
            report = capture_media.process_inbox(inbox, root)
            statuses = {item["kind"]: item["status"] for item in report["items"]}
            self.assertEqual(statuses.get("page-visual"), "converted")
            self.assertEqual(statuses.get("svg"), "converted")
            visual = root / "assets" / "Making-768-servers-look-like-1"
            self.assertTrue(any(visual.glob("visual-servers.*")))
            self.assertTrue(any(visual.glob("svg-1.*")))


if __name__ == "__main__":
    unittest.main()
