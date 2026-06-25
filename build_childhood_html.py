#!/usr/bin/env python3
"""Build the HTML edition and keep CSS in external files."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


OUTPUT = Path("childhood_es_grid.html")


def main() -> None:
    subprocess.run(
        [
            "pandoc",
            "childhood_es_grid.md",
            "--from=gfm",
            "--to=html5",
            "--standalone",
            "--toc",
            "--toc-depth=2",
            "--metadata",
            "lang=es-ES",
            "--metadata",
            "title=Childhood — Edición española para cuadrícula",
            "--css",
            "styles/manual.css",
            "--output",
            str(OUTPUT),
        ],
        check=True,
    )

    html = OUTPUT.read_text(encoding="utf-8")
    html = re.sub(r"\n  <style>.*?\n  </style>", "", html, count=1, flags=re.S)
    html = html.replace(' style="text-align: right;"', ' class="numeric"')
    OUTPUT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
