#!/usr/bin/env python3
"""Build the HTML edition and keep CSS in external files."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


CONFIGS = [
    {
        "source": Path("patios_portales_es.md"),
        "output": Path("patios_portales_es.html"),
        "lang": "es-ES",
        "title": "Patios & Portales — Edición española para cuadrícula",
        "switch": '<a aria-current="page" href="patios_portales_es.html">Castellano</a><a href="patis_portals_ca.html">Català</a>',
    },
    {
        "source": Path("patis_portals_ca.md"),
        "output": Path("patis_portals_ca.html"),
        "lang": "ca",
        "title": "Patis i Portals — Edició catalana per a quadrícula",
        "switch": '<a href="patios_portales_es.html">Castellano</a><a aria-current="page" href="patis_portals_ca.html">Català</a>',
    },
]


def build(config: dict[str, object]) -> None:
    subprocess.run(
        [
            "pandoc",
            str(config["source"]),
            "--from=gfm",
            "--to=html5",
            "--standalone",
            "--toc",
            "--toc-depth=2",
            "--metadata",
            f"lang={config['lang']}",
            "--metadata",
            f"title={config['title']}",
            "--css",
            "styles/manual.css",
            "--output",
            str(config["output"]),
        ],
        check=True,
    )

    output = Path(config["output"])
    html = output.read_text(encoding="utf-8")
    html = re.sub(r"\n  <style>.*?\n  </style>", "", html, count=1, flags=re.S)
    html = html.replace(' style="text-align: right;"', ' class="numeric"')
    html = html.replace(
        "<body>",
        f'<body>\n<nav class="language-switch" aria-label="Selector de idioma">{config["switch"]}</nav>',
        1,
    )
    output.write_text(html, encoding="utf-8")


def main() -> None:
    for config in CONFIGS:
        source = Path(config["source"])
        if source.exists():
            build(config)


if __name__ == "__main__":
    main()
