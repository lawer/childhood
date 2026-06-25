#!/usr/bin/env python3
"""One-time structuring pass for translated background records."""

from pathlib import Path
import re

text = Path("childhood_es_grid.md").read_text(encoding="utf-8")
end = text.index("## Habilidades")
block = text[:end]
start = block.rfind("| 100 |")
start = block.find("\n", start) + 1
block = block[start:]

entries: dict[int, list[str]] = {}
current: int | None = None
for raw in block.splitlines():
    line = raw.strip()
    if not line:
        if current is not None:
            entries[current].append("")
        continue
    match = re.match(r"^(\d{1,3})[.)]?\s*(.*)$", line)
    if match:
        number = int(match.group(1))
        if number == 666:
            number = 66
        if 1 <= number <= 101:
            current = number
            entries.setdefault(number, []).append(match.group(2).strip())
            continue
    if current is not None:
        entries[current].append(line)

out = ["## Tabla de Trasfondos", ""]
for number in sorted(entries):
    value = "\n".join(entries[number]).strip()
    value = re.sub(r"\n{3,}", "\n\n", value)
    first, sep, rest = value.partition(".")
    if sep and len(first) <= 70:
        title = first.strip()
        body = rest.strip()
    else:
        words = value.split()
        title = " ".join(words[:5])
        body = " ".join(words[5:])
    out.extend([f"### {number}. {title}", "", body, ""])

Path("partials/backgrounds_es.md").write_text("\n".join(out).strip() + "\n", encoding="utf-8")
