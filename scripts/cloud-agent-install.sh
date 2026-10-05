#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the techtranslate tooling.
#
# The base image already ships python3, ffmpeg and google-chrome. This script
# only adds the optional media-capture dependencies used by
# scripts/capture_media.py so the full test suite (tests/test_capture_media.py)
# and the article translation pipeline can run end-to-end.
set -euo pipefail

python3 -m pip install --quiet --disable-pip-version-check --upgrade playwright yt-dlp

# Download the Playwright Chromium build used for page-visual capture. This is a
# no-op when the browser is already present in ~/.cache/ms-playwright.
python3 -m playwright install chromium

echo "cloud-agent install complete"
