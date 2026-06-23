#!/usr/bin/env python3
"""Build a complete Spanish, grid-adapted Markdown edition from extracted PDF text."""

from __future__ import annotations

import html
import json
import math
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

SOURCE = Path("/tmp/childhood_source.txt")
CACHE = Path("/tmp/childhood_translation_cache.json")
OUTPUT = Path("childhood_es_grid.md")


GLOSSARY = {
    "Bad Guys": "Malos",
    "Bad Guy": "Malo",
    "Chores": "Tareas",
    "Chore": "Tarea",
    "Mood": "Ánimo",
    "Bottles": "Chapas",
    "Bottle": "Chapa",
    "Kids": "Peques",
    "Kid": "Peque",
    "Club": "Pandilla",
    "Chicken test": "prueba de Gallina",
    "Ranged": "A distancia",
    "Thrown": "Arrojadiza",
    "Body": "Cuerpo",
    "Mind": "Mente",
    "Heart": "Corazón",
    "Cool": "Molar",
}


GRID_RULES = """# CHILDHOOD

## Edición española para tablero de casillas

> **Regla de oro de esta adaptación.** Toda distancia se cuenta en casillas. Si una
> regla transcrita del original contradice este recuadro, manda este recuadro.

### Resumen de medición

- **Movimiento base:** `(5 + Cuerpo) / 2` casillas, redondeando hacia arriba.
- **Movimiento ortogonal:** una miniatura solo avanza arriba, abajo, a izquierda o a
  derecha. Cada cambio de casilla cuesta 1. No se permite movimiento diagonal.
- **Distancias y alcances:** cada distancia original en pulgadas se divide entre 2.
  Si el resultado no es entero, se redondea hacia arriba.
- **Distancias aleatorias:** tira primero los dados indicados, divide el resultado
  entre 2 y redondea hacia arriba para obtener las casillas.
- **Cuerpo a cuerpo:** un objetivo está trabado si ocupa cualquiera de las ocho
  casillas adyacentes; las diagonales cuentan únicamente para determinar esta
  adyacencia, no para mover.
- **Línea de visión:** puede trazarse en cualquier dirección, incluidas diagonales,
  desde el centro de la casilla atacante al centro de la casilla objetivo. Queda
  bloqueada si atraviesa cualquier casilla ocupada o terreno que bloquee visión.
  Las casillas de origen y destino no bloquean su propio disparo.
- **Apariciones:** los Malos aparecen en las **Casillas de Borde (Spawns)** señaladas
  por la aventura. Cuando se indique un borde aleatorio, elige o sortea uno de esos
  Spawns.
- **Empujón o retroceso:** desplaza al objetivo 1 casilla ortogonal directamente en
  sentido opuesto al origen del efecto. Si hay dos direcciones válidas, quien causa
  el empujón elige. No atraviesa casillas ocupadas ni terreno infranqueable.
- **Áreas:** convierte su radio o dimensiones dividiendo las pulgadas entre 2. Una
  casilla queda afectada si su centro está dentro del área.

### Referencia rápida de conversiones

| Original | Cuadrícula |
|---:|---:|
| 1\"–2\" | 1 casilla |
| 3\"–4\" | 2 casillas |
| 5\"–6\" | 3 casillas |
| 8\" | 4 casillas |
| 12\" | 6 casillas |
| 18\" | 9 casillas |
| 24\" | 12 casillas |

![PROMPT_PLACEHOLDER](images/childhood-apertura.png)

---
"""


def clean_page(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line or re.fullmatch(r"\d{1,3}", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def chunks(text: str, limit: int = 4200):
    blocks = text.splitlines()
    current = []
    size = 0
    for block in blocks:
        if len(block) > limit:
            pieces = [block[i:i + limit] for i in range(0, len(block), limit)]
        else:
            pieces = [block]
        for piece in pieces:
            needed = len(piece) + 1
            if current and size + needed > limit:
                yield "\n".join(current)
                current, size = [], 0
            current.append(piece)
            size += needed
    if current:
        yield "\n".join(current)


def translate(text: str, cache: dict[str, str]) -> str:
    if text in cache:
        return cache[text]
    translator = GoogleTranslator(source="en", target="es")
    for attempt in range(6):
        try:
            result = translator.translate(text)
            cache[text] = result
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            return result
        except Exception:
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def localize_terms(text: str) -> str:
    replacements = {
        r"\bchicos malos\b": "Malos",
        r"\bmalos chicos\b": "Malos",
        r"\bchico malo\b": "Malo",
        r"\bniños\b": "peques",
        r"\bniño\b": "peque",
        r"\bbotellas\b": "chapas",
        r"\bbotella\b": "chapa",
        r"\bestado de ánimo\b": "Ánimo",
        r"\bclub\b": "pandilla",
        r"\bCuerpo\b": "Cuerpo",
        r"\bMente\b": "Mente",
        r"\bCorazón\b": "Corazón",
    }
    for pattern, value in replacements.items():
        text = re.sub(pattern, value, text, flags=re.IGNORECASE)
    return text


def convert_measurements(text: str) -> str:
    # Variable movement: roll first, halve and round up.
    text = re.sub(
        r"\b(?:(\d+)\s*)?[dD]\s*(\d+)\s*(?:pulgadas?|[\"”])",
        lambda m: f"tira {m.group(1) or '1'}D{m.group(2)}, divide entre 2 y redondea hacia arriba (casillas)",
        text,
    )

    def fixed(m: re.Match[str]) -> str:
        value = float(m.group(1).replace(",", "."))
        cells = math.ceil(value / 2)
        return f"{cells} {'casilla' if cells == 1 else 'casillas'}"

    text = re.sub(r"(?<![\w.])(\d+(?:[.,]\d+)?)\s*(?:pulgadas?|[\"”])", fixed, text, flags=re.IGNORECASE)
    text = re.sub(
        r"5\s*\+\s*(?:su\s+)?Cuerpo",
        "(5 + Cuerpo) / 2 casillas, redondeando hacia arriba",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Los peques pueden mover una cantidad de pulgadas igual a \(5 \+ Cuerpo\) / 2 casillas, redondeando hacia arriba\.?",
        "Los peques pueden mover (5 + Cuerpo) / 2 casillas, redondeando hacia arriba. "
        "El movimiento es exclusivamente ortogonal; nunca diagonal.",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Los peques pueden mover una cantidad de pulgadas igual a 5\+ de su Cuerpo\.?",
        "Los peques pueden mover (5 + Cuerpo) / 2 casillas, redondeando hacia arriba. "
        "El movimiento es exclusivamente ortogonal; nunca diagonal.",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Las medidas están en pulgadas y puedes medir previamente\.?",
        "Todas las medidas de juego están en casillas y se puede medir antes de actuar.",
        text,
        flags=re.IGNORECASE,
    )
    # Fragments damaged by the untagged source PDF cannot always retain their number.
    # Make the unit unambiguous and defer to the normative conversion table.
    text = re.sub(
        r"\bpulgadas?\b",
        "casillas (valor convertido según la tabla)",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bBad Guys\b", "Malos", text, flags=re.IGNORECASE)
    text = re.sub(r"\bBad Guy\b", "Malo", text, flags=re.IGNORECASE)
    text = re.sub(r"\bRanged\b", "A distancia", text, flags=re.IGNORECASE)
    text = re.sub(r"\bThrown\b", "Arrojadiza", text, flags=re.IGNORECASE)
    return text


def image_prompt(page: int) -> str:
    return (
        "Prompt: editorial spot illustration for a 1995 kids adventure tabletop RPG, "
        "hand-drawn school notebook doodle, chunky black ink outlines, photocopied zine "
        "texture, neon magenta cyan and yellow marker accents, playful suburban mystery, "
        f"visual motif inspired by the content of original page {page}, no readable text, "
        "white background, print-ready, high detail, portrait composition, original characters"
    )


def main() -> None:
    pages = SOURCE.read_text(encoding="utf-8", errors="replace").split("\f")
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    output = [GRID_RULES.replace("PROMPT_PLACEHOLDER", image_prompt(1))]
    for page_no, raw in enumerate(pages, 1):
        source = clean_page(raw)
        if not source:
            continue
        translated = "\n".join(translate(chunk, cache) for chunk in chunks(source))
        translated = convert_measurements(localize_terms(translated))
        output.extend([
            f"\n## Página {page_no} del original\n",
            translated,
            "",
            f"![{image_prompt(page_no)}](images/childhood-pagina-{page_no:03d}.png)",
            "\n---\n",
        ])
        OUTPUT.write_text("\n".join(output), encoding="utf-8")
        print(f"{page_no}/{len(pages)}", flush=True)


if __name__ == "__main__":
    main()
