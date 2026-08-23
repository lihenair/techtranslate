#!/usr/bin/env python3
"""Rebuild the README translation catalog from archive/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from translation_archive import write_readme_catalog  # noqa: E402

if __name__ == "__main__":
    write_readme_catalog(Path(__file__).resolve().parents[1])
