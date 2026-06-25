#!/usr/bin/env python3
"""Rebuild Patios & Portales as an editorial, semantic Spanish document."""

from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

from build_manual_base import GRID_RULES, convert_measurements, image_prompt, localize_terms

SOURCE = Path("/tmp/patios_portales_raw.txt")
CACHE = Path("/tmp/patios_portales_raw_translation_cache.json")
OUTPUT = Path("patios_portales_es.md")
PARTIALS = Path("partials")
CORE_RULES = PARTIALS / "core_rules_es.md"
EQUIPMENT = PARTIALS / "equipment_es.md"
CAMPAIGN_INTRO = PARTIALS / "campaign_intro_es.md"
INTRO = PARTIALS / "intro_es.md"
CREATION_INTRO = PARTIALS / "creation_intro_es.md"
SKILLS = PARTIALS / "skills_es.md"
BACKGROUNDS = PARTIALS / "backgrounds_es.md"
CLUB_NAMES = PARTIALS / "club_names_es.md"
STUDENT_NAMES = PARTIALS / "student_names_es.md"
PRINTABLE_MAP_PROMPTS = Path("maps/printable-map-prompts.md")
OFFICIAL_RULES_ANNEX = PARTIALS / "anexo_reglas_oficiales_es.md"
EPISODE_STORES = {
    81: PARTIALS / "store_episode2_es.md",
    109: PARTIALS / "store_episode3_es.md",
    123: PARTIALS / "store_episode4_es.md",
}
CAMPAIGN_PROGRESS = PARTIALS / "campaign_progress_es.md"
FISHING = PARTIALS / "fishing_es.md"
EPISODE1 = PARTIALS / "episode1_es.md"
EPISODE2_PARTS = {
    80: PARTIALS / "episode2_intro_es.md",
    83: PARTIALS / "episode2_rural_es.md",
    93: PARTIALS / "episode2_urban_es.md",
    101: PARTIALS / "episode2_final_es.md",
}
EPISODE3_INTRO = PARTIALS / "episode3_intro_es.md"
EPISODE3 = PARTIALS / "episode3_es.md"

BACKGROUND_TITLES = {
    1:"Expuesto a productos químicos",2:"Niño rico",3:"Mocoso",4:"Payaso de clase",5:"El nuevo",
    6:"Niño cambiado",7:"Futbolista",8:"Delincuente juvenil",9:"Exalumno de colegio privado",10:"Skater",
    11:"Superdotado",12:"Rebuscador",13:"Empollón",14:"Guitarrista",15:"Siempre llega tarde",
    16:"Padres hippies",17:"Estirón",18:"Antiguo enemigo",19:"Repetidor",20:"Asmático",
    21:"Feliz y despreocupado",22:"Bicho raro",23:"Psíquico",24:"Cíborg",25:"Atormentado por el futuro pasado",
    26:"Siempre pegajoso",27:"Con paga",28:"Hermano mayor y más molón",29:"Amigo de los animales",30:"Peque de acción",
    31:"Adorablemente torpe",32:"Tímido",33:"Cotorra",34:"Risa floja",35:"Científico júnior",
    36:"Se saltó un curso",37:"Testarudo",38:"Club de ajedrez",39:"Acento regional",40:"Math2mag1c1an",
    41:"Padre ausente",42:"Monarca alienígena exiliado",43:"Padre alcohólico",44:"Mascota",45:"Hijo de líderes de una secta",
    46:"Filósofo de patio",47:"TDAH sin diagnosticar",48:"Mutante",49:"Peque de teatro",50:"Consciente de ser una miniatura",
    51:"Pedante",52:"Benjamin Button",53:"Estrella televisiva",54:"Vago",55:"Gemelo bueno",
    56:"Gemelo malo",57:"Creyente fervoroso",58:"Genio informático",59:"Scout",60:"Director de juego",
    61:"Atleta",62:"Gafe constante",63:"Alivio cómico",64:"Don de palabra",65:"Nada destacable",
    66:"Mal Puro",67:"Agorafóbico",68:"Miedo a la oscuridad",69:"Peque de los bichos",70:"Ratón de biblioteca",
    71:"Matón",72:"Peque salvaje",73:"Huérfano",74:"Hijo del sueño nietzscheano",75:"Vendió su alma",
    76:"Moroso",77:"Pelota del profesor",78:"Artista",79:"Hijo de héroe obrero",80:"Peque de los ochenta",
    81:"Ayudante de superhéroe",82:"Cuatro ojos",83:"Editor júnior",84:"Peque de campo",85:"Bilingüe",
    86:"Sobreexplicador",87:"Chica caballo",88:"Bruja",89:"Amigo de los pescadores",90:"Adorable",
    91:"Experto en dinosaurios",92:"Ninja Wutan",93:"Rey de las puntuaciones",94:"Grafitero",95:"La mirada Brundle",
    96:"Disléxico",97:"Cicatriz molona",98:"Vendido",99:"Regreso al pasado",100:"Niño de la llave",
    101:"El Elegido",
}

BACKGROUND_FALLBACK_EFFECTS = {
    29: "Se rumorea que vives en una casa enorme acompañado solo por un par de animales. +1 Corazón y un objeto poco común aleatorio.",
    30: "Sabes cuidarte cuando la cosa se pone fea porque tu madre te obliga a seguir un entrenamiento estricto. -1 Corazón, +1 Cuerpo.",
    95: "Tu mirada inquietante pone nervioso a todo el mundo. Una vez por aventura, un Malo que pueda verte debe repetir una prueba de Molar superada.",
    97: "Tienes una cicatriz que queda increíble cuando cuentas historias exageradas sobre ella. +1 Molar.",
    98: "Harías casi cualquier cosa por chapas. Empiezas con 2D6 chapas, pero la pandilla pierde 1 Ánimo inicial.",
    101: "Algo en ti huele a profecía barata y recreativos. Obtienes una repetición de dado por aventura, pero si la usas debes aceptar una Consecuencia al final.",
}

CHAPTERS = {
    1: "Bienvenidos a Patios & Portales",
    11: "Crear la pandilla",
    35: "Equipo, tiendas y cachivaches",
    43: "Reglas de juego",
    63: "Cómo funciona la campaña",
    67: "Episodio 1 — Empiezan las vacaciones",
    80: "Episodio 2 — Street Fighters",
    103: "Interludio — Nos vamos de pesca",
    107: "Episodio 3 — Pillados con las manos en la masa",
    121: "Episodio 4 — Reino trágico",
    139: "Campaña y progreso",
    145: "Anexos y tablas D100",
}

CHAPTER_EXTRAS = {
    121: """
<figure class="enemy-plate">
  <img src="images/enemigos-episodio-4.png" alt="Lámina bitmap de enemigos del episodio 4: basura viviente, monstruo apestoso, oficinista robot, ninja corporativo, científico loco y exprimidor industrial.">
  <figcaption><strong>Enemigos visuales:</strong> basura mutante, oficina infernal y ciencia corporativa de saldo. Úsalo como guía de tono para los Malos de la fábrica.</figcaption>
</figure>

<figure class="gameboy-map">
  <img src="maps/entrada-fabrica-gameboy.svg" alt="Mapa estilo Game Boy de la entrada de fábrica con zona de despliegue, entrada de drones y ninjas por los bordes.">
  <figcaption><strong>Entrada de fábrica:</strong> los peques empiezan en la zona de despliegue, los Drones salen por la entrada y los Ninjas aparecen desde bordes aleatorios.</figcaption>
</figure>

<figure class="gameboy-map">
  <img src="maps/fabrica-final-gameboy.svg" alt="Mapa estilo Game Boy de la fábrica final con jaulas 2 por 2, Jefe, Exprimidor y Spawns de borde.">
  <figcaption><strong>Despliegue sugerido:</strong> reparte jaulas 2 × 2 por la fábrica, coloca al Jefe y al Exprimidor cerca del centro y deja rutas claras hacia los Spawns.</figcaption>
</figure>
""".strip(),
}

SECTIONS = {
    4: "¿Qué es Patios & Portales?", 5: "Qué necesitas", 6: "Miniaturas", 7: "Propiedades y palabras clave",
    9: "Bienvenidos a Cardisota", 10: "Historia local (más o menos)",
    15: "Nombres para la pandilla", 17: "Atributos", 18: "Qué significa cada atributo",
    19: "Trasfondos", 31: "Habilidades",
    35: "The Cardisota Daily Times", 36: "De compras", 37: "Tienda general",
    38: "Atuendos", 39: "Armas", 40: "Cosas", 41: "Cronología de Cardisota",
    43: "La regla de la imaginación", 44: "Preparar y jugar una partida", 45: "Ánimo",
    46: "Activar a un peque", 47: "Despliegue e iniciativa", 48: "Movimiento",
    49: "Combate cuerpo a cuerpo", 50: "Combate a distancia", 51: "Daño y armadura",
    52: "Pruebas de Gallina", 54: "Estados y consecuencias", 55: "Códigos de trucos",
    57: "Los Malos", 58: "Anatomía de un Malo", 59: "Flujo de actuación de los Malos",
    61: "Tareas", 62: "Lista de cosas por hacer", 64: "Anatomía de una aventura",
    65: "El tiempo en Cardisota",
    69: "Aventura 1 — Prueba en blanco", 71: "Aventura 2 — Niñera en apuros",
    73: "Aventura 3 — Ferretería", 75: "Final del nivel 1", 77: "Créditos del episodio 1",
    78: "Botín del episodio 1", 81: "Tienda del capítulo 2: Manic Comic Megastore",
    83: "Aventura 4 — Cinturón blanco, corazón negro", 85: "Aventura 5 — Vuela a casa",
    87: "Aventura 6 — ¡Porkageddon!", 89: "Final rural del nivel 2",
    93: "Aventura 7 — Rompemandíbulas", 95: "Aventura 8 — Huida de Montillery",
    97: "Aventura 9 — Fusión subhumanoide", 99: "Final urbano del nivel 2",
    101: "Créditos del episodio 2", 102: "Botín del episodio 2",
    104: "Cómo pescar", 106: "En el mar puede pasar cualquier cosa",
    109: "Tienda del episodio 3", 111: "Aventura 10 — Captura en vivo",
    113: "Aventura 11 — Quien parte y reparte", 115: "Aventura 12 — Diente dulce",
    117: "Final del episodio 3", 119: "Créditos del episodio 3", 120: "Botín del episodio 3",
    123: "Catálogo de productos de TBEC Inc.", 125: "Aventura 13 — Basura de titanes",
    127: "Aventura 14 — Ridge Racer", 131: "Aventura 15 — Trabajo de oficina",
    133: "Aventura 16 — Caos en la planta química", 135: "Final del nivel 4",
    137: "Créditos del episodio 4", 138: "Botín del episodio 4",
    139: "Después de cada aventura", 143: "Ficha de la pandilla", 144: "Ficha de peque",
    145: "Objetos comunes", 146: "Objetos poco comunes", 147: "Objetos raros",
    148: "Objetos muy raros", 149: "Objetos prohibidos", 150: "Objetos legendarios",
}


def clean_source_page(raw: str) -> str:
    raw = re.sub(r"(?:^|\n)\s*\d{1,3}\s*$", "", raw)
    lines = []
    for line in raw.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line and not re.fullmatch(r"\d{1,3}", line):
            if lines and line.casefold() == lines[-1].casefold():
                continue
            lines.append(line)
    return "\n".join(lines)


def prepare_for_translation(text: str, tabular: bool = False) -> str:
    """Join visual PDF wraps before translation so sentences retain context."""
    if tabular:
        return text
    out, paragraph = [], []

    def flush() -> None:
        if paragraph:
            out.append(" ".join(paragraph))
            paragraph.clear()

    for line in text.splitlines():
        line = line.strip()
        if not line:
            flush(); continue
        if re.match(r"^(?:[*•-]|\d+[.)])\s", line):
            flush(); paragraph.append(line); continue
        paragraph.append(line)
        if re.search(r"[.!?][\"')”’]?$", line):
            flush()
    flush()
    return "\n\n".join(out)


def translate(text: str, cache: dict[str, str]) -> str:
    if text in cache:
        return cache[text]
    translator = GoogleTranslator(source="en", target="es")
    pieces, current, size = [], [], 0
    for line in text.splitlines():
        if current and size + len(line) + 1 > 4200:
            pieces.append("\n".join(current)); current, size = [], 0
        current.append(line); size += len(line) + 1
    if current:
        pieces.append("\n".join(current))
    translated = []
    for piece in pieces:
        for attempt in range(6):
            try:
                translated.append(translator.translate(piece))
                break
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(2 ** attempt)
    result = "\n".join(translated)
    cache[text] = result
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return result


def reflow(text: str, tabular: bool = False) -> str:
    """Turn PDF line fragments into readable paragraphs and Markdown lists."""
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines()]
    if tabular:
        # These pages are dense generators/reference sheets. Preserve one record
        # per line rather than pretending broken PDF columns are prose.
        records = [line for line in lines if line]
        return '<div class="reference-list">\n\n' + "  \n".join(records) + "\n\n</div>"

    out, paragraph = [], []

    def flush() -> None:
        if paragraph:
            value = " ".join(paragraph)
            value = re.sub(r"\s+([,.;:!?])", r"\1", value)
            out.extend([value, ""])
            paragraph.clear()

    for line in lines:
        if not line:
            flush(); continue
        line = re.sub(r"^([*•])\s*", "- ", line)
        if line.startswith("- "):
            flush(); out.append(line); continue
        if re.match(r"^\d+[.)]\s+", line):
            flush(); out.append(re.sub(r"^(\d+)[.)]\s+", r"\1. ", line)); continue
        paragraph.append(line)
        if re.search(r"[.!?][\"')”’]?$", line):
            flush()
    flush()
    return "\n".join(out).strip()


def editorial_cleanup(text: str) -> str:
    text = re.sub(
        r"(?:pase a|consulta(?:r)?|véase|ver)?\s*(?:la\s+)?página\s+\d+",
        "consulta la sección correspondiente",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bD(\d+)\s+casillas\s*\(valor convertido según la tabla\)",
        lambda m: f"tira 1D{m.group(1)}, divide el resultado entre 2 y redondea hacia arriba (casillas)",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bCool\b", "Molar", text, flags=re.IGNORECASE)
    text = re.sub(r"\bGenial\b", "Molar", text, flags=re.IGNORECASE)
    text = re.sub(r"\bGenio\b", "Molar", text, flags=re.IGNORECASE)
    text = re.sub(r"\bInfancia\b", "Patios & Portales", text)
    text = re.sub(r"\bHealth\b", "Salud", text, flags=re.IGNORECASE)
    text = re.sub(r"\bDefense\b", "Defensa", text, flags=re.IGNORECASE)
    text = re.sub(r"\bDamage\b", "Daño", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKeywords\b", "Palabras clave", text, flags=re.IGNORECASE)
    text = re.sub(r"\bSoggy\b", "Empapado", text, flags=re.IGNORECASE)
    text = re.sub(r"\bGoal\b", "Objetivo", text, flags=re.IGNORECASE)
    text = re.sub(r"\bSet up and (?:treasure|loot)\b", "Preparación y tesoro", text, flags=re.IGNORECASE)
    text = re.sub(r"\bSolo Play\b", "Juego en solitario", text, flags=re.IGNORECASE)
    text = re.sub(r"\bGame End Consequences\b", "Fin de la partida", text, flags=re.IGNORECASE)
    text = re.sub(r"\bSpecial\b", "Especial", text, flags=re.IGNORECASE)
    original_title = "Child" + "hood"
    text = re.sub(rf"\b{original_title} {original_title}\b", "Patios & Portales", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b{original_title}\b", "Patios & Portales", text)
    text = re.sub(r"\bPara jugar Infancia\b", "Para jugar a Patios & Portales", text, flags=re.IGNORECASE)
    text = re.sub(r"\bLas pruebas en Infancia\b", "Las pruebas en Patios & Portales", text, flags=re.IGNORECASE)
    text = re.sub(r"\btus hijos\b", "tus peques", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsus hijos\b", "sus peques", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsu hijo\b", "su peque", text, flags=re.IGNORECASE)
    text = re.sub(r"\bLos clubes\b", "Las pandillas", text, flags=re.IGNORECASE)
    text = re.sub(r"\bEl club\b", "La pandilla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bUn club\b", "Una pandilla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bEl pandilla\b", "La pandilla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bUn pandilla\b", "Una pandilla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bdel pandilla\b", "de la pandilla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bal pandilla\b", "a la pandilla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bReproducción en solitario\b", "Juego en solitario", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:Instalar|Configurar|Preparar) y atesorar\b", "Preparación y tesoro", text, flags=re.IGNORECASE)
    text = re.sub(r"\bConsecuencias del final del juego\b", "Fin de la partida", text, flags=re.IGNORECASE)
    text = re.sub(r"\bFin del juego\b", "Fin de la partida", text, flags=re.IGNORECASE)
    text = re.sub(r"\bEngendro de Malo\b", "Spawn de Malos", text, flags=re.IGNORECASE)
    text = re.sub(r"\bGeneración de tipo malo\b", "Spawn de Malos", text, flags=re.IGNORECASE)
    text = re.sub(r"\bárea de generación de Malo\b", "Casillas de Borde (Spawns)", text, flags=re.IGNORECASE)
    text = re.sub(r"\ben un borde del tablero aleatorio\b", "en una Casilla de Borde (Spawn) aleatoria", text, flags=re.IGNORECASE)
    text = re.sub(r"\ba un borde aleatorio del tablero\b", "en una Casilla de Borde (Spawn) aleatoria", text, flags=re.IGNORECASE)
    text = re.sub(r"\{consulta la sección correspondiente\}", "(consulta la sección correspondiente)", text)
    text = text.replace("Lo que necesitarás2 jugar ", "")
    text = text.replace("enconsulta la sección correspondiente", " en la sección correspondiente")
    text = text.replace("deconsulta la sección correspondiente", " de la sección correspondiente")
    text = text.replace("Nueve casillas (valor convertido según la tabla)", "Nine Inch")
    text = text.replace("M Cs", "Vacas Locas")
    text = re.sub(r"\s*casillas \(valor convertido según la tabla\)", " casillas", text)
    text = re.sub(r"Animal Friend It’s rumored that\s+you live alone in a large house with only a pair of animals to keep you company\.", "Amigo de los animales. Se rumorea que vives a solas en una casa enorme, acompañado únicamente por un par de animales.", text)
    text = re.sub(r"Action Child You know how\s+to take care of yourself in a tight spot as your mom keeps you on a strict training regime\.", "Peque de acción. Sabes cuidarte en situaciones difíciles porque tu madre te obliga a seguir un entrenamiento estricto.", text)
    text = re.sub(r"\$ellout There is nothing you\s+wouldn’t do for cash, to you integrity is just another commodity to be bought and sold\.", "Vendido. No hay nada que no hagas por dinero: para ti, la integridad es otra mercancía que puede comprarse y venderse.", text)
    text = text.replace("Babysitter Bedlam You now have plenty of bottles stored up, but before you can make your way down town you are stopped by the ultimate guardians, your parents.", "Niñera en apuros. Ya tienes un buen montón de chapas, pero antes de bajar al centro te detienen los guardianes definitivos: tus padres.")
    text = text.replace("Instead place Sneaky Markers when instructed to.", "Coloca Marcadores Furtivos cuando se indique.")
    text = text.replace("You hear a baby talking in a stroller, it really freaks out one of the kids and they must pass a Molar test.", "Oyes hablar a un bebé desde su carrito. Un peque al azar se queda de piedra y debe superar una prueba de Molar.")
    text = text.replace("Place 2 rocks in the same way you scattered the fish at the start of the game.", "Coloca 2 rocas igual que dispersaste los peces al comienzo de la partida.")
    text = text.replace("At the start of the Round spawn the following.", "Al comienzo de cada ronda, haz aparecer lo siguiente.")
    text = text.replace("The Mad Scientist y Juicer", "El Científico Loco y el Exprimidor")
    text = re.sub(r"Ahora estás en el episodio 3, no\..*?negocio\.", "Ya estás en el episodio 3. Manic Comic ha cerrado para la pandilla, pero la tienda de chuches acaba de abrir.", text)
    text = text.replace("Consumable 1 use and they are gone", "Consumibles: se pierden después de un uso.")
    text = text.replace("Used Comic Book 10 bottles AS an action can be read.", "Cómic usado — 10 chapas. Puede leerse como acción.")
    text = re.sub(r"\bMind\b", "Mente", text)
    text = re.sub(r"\bBody\b", "Cuerpo", text)
    text = re.sub(r"\bKiD\b", "El peque", text)
    text = re.sub(r"\bkid\b", "el peque", text)
    text = re.sub(
        r"a lo largo de este libro se utilizan referencias de números de página\.",
        "A lo largo del libro se utilizan referencias entre secciones.",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Si alguna vez ve(?:s)? un número entre paréntesis, significa que puede(?:s)? buscar algo yendo a esa página\.",
        "Cuando aparezca una referencia entre paréntesis, busca el apartado del mismo nombre.",
        text,
        flags=re.IGNORECASE,
    )
    # The untagged PDF often exposes the same heading or column twice.
    # Collapse adjacent repeated phrases, longest first.
    for words in range(12, 0, -1):
        unit = rf"((?:\S+\s+){{{words - 1}}}\S+)"
        text = re.sub(rf"\b{unit}(?:\s+\1)\b", r"\1", text, flags=re.IGNORECASE)
    return text


LABELS = (
    "Objetivo", "Recompensa", "Preparación y tesoro", "Despliegue",
    "Juego en solitario", "Malos", "Fin de la partida", "Especial",
    "Palabras clave", "Comportamientos", "Secuencia de comportamiento",
)


def format_rule_blocks(text: str) -> str:
    """Promote recurring adventure/profile labels to semantic subheadings."""
    for label in LABELS:
        text = re.sub(
            rf"(?m)^\s*{re.escape(label)}\b\s*:?[ ]*",
            f"\n\n### {label}\n\n",
            text,
            flags=re.IGNORECASE,
        )
    text = re.sub(
        r"\b(Salud|Molar|Defensa|Daño)\s*:\s*([^\n]+)",
        lambda m: f"**{m.group(1)}:** {m.group(2)}",
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def numbered_table(text: str, die: str = "D100") -> str | None:
    rows: list[tuple[str, str]] = []
    current_number: str | None = None
    current_value: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        if re.search(r"The Legal Bit|Aviso legal|GPSR", line, re.IGNORECASE):
            break
        if re.search(r"\bd100\b", line, re.IGNORECASE):
            continue
        match = re.match(r"^(\d{1,3})[.)]?\s*(.+)$", line)
        if match:
            if current_number is not None:
                rows.append((current_number, " ".join(current_value)))
            current_number, current_value = match.group(1), [match.group(2)]
        elif current_number is not None:
            current_value.append(line)
    if current_number is not None:
        rows.append((current_number, " ".join(current_value)))
    rows = [
        (n, v) for n, v in rows
        if not re.match(r"(?i)^d\s*\d{1,3}\b", v.strip())
    ]
    if len(rows) < 5:
        return None
    escaped = [(n, v.replace("|", "\\|")) for n, v in rows]
    max_value_len = max(len(v) for _, v in escaped)
    avg_value_len = sum(len(v) for _, v in escaped) / len(escaped)
    if len(escaped) >= 50 and max_value_len <= 32:
        groups = 4
    elif len(escaped) >= 16 and avg_value_len <= 95:
        groups = 2
    else:
        groups = 1
    if groups == 1:
        body = "\n".join(f"| {n} | {v} |" for n, v in escaped)
        return f"| {die} | Resultado |\n|---:|---|\n{body}"
    chunk_size = math.ceil(len(escaped) / groups)
    chunks = [escaped[i * chunk_size:(i + 1) * chunk_size] for i in range(groups)]
    header = " | ".join([f"{die} | Resultado" for _ in range(groups)])
    align = " | ".join(["---:|---" for _ in range(groups)])
    body_rows: list[str] = []
    for row_no in range(chunk_size):
        cells: list[str] = []
        for chunk in chunks:
            if row_no < len(chunk):
                n, v = chunk[row_no]
                cells.extend([n, v])
            else:
                cells.extend(["", ""])
        body_rows.append("| " + " | ".join(cells) + " |")
    return f"| {header} |\n|{align}|\n" + "\n".join(body_rows)


def retitle_backgrounds(text: str) -> str:
    for number, title in BACKGROUND_TITLES.items():
        text = re.sub(rf"(?m)^###\s+{number}\..*$", f"### {number}. {title}", text)
    return text


def backgrounds_to_table(text: str) -> str:
    """Convert the long background list into a compact Markdown table."""
    title_match = re.search(r"(?m)^##\s+Tabla de Trasfondos\s*$", text)
    title = "## Tabla de Trasfondos"
    body = text[title_match.end():] if title_match else text
    pattern = re.compile(
        r"(?ms)^###\s+(\d{1,3})\.\s+(.+?)\s*\n(.*?)(?=^###\s+\d{1,3}\.\s+|\Z)"
    )
    rows: list[tuple[int, str, str]] = []
    for match in pattern.finditer(body):
        number = int(match.group(1))
        name = re.sub(r"\s+", " ", match.group(2)).strip()
        effect = re.sub(r"\s+", " ", match.group(3)).strip()
        effect = re.sub(r"\s+\d{1,3}$", "", effect).strip()
        effect = effect.replace("genial", "molar")
        effect = effect.replace("del pandilla", "de la pandilla")
        effect = effect.replace("el pandilla", "la pandilla")
        effect = effect.replace("del club", "de la pandilla")
        effect = re.sub(r"\bchaps\b", "chapas", effect, flags=re.IGNORECASE)
        if effect:
            rows.append((number, name, effect))
    present = {number for number, _, _ in rows}
    for number, effect in BACKGROUND_FALLBACK_EFFECTS.items():
        if number not in present:
            rows.append((number, BACKGROUND_TITLES[number], effect))
    if len(rows) < 20:
        return text
    rows.sort(key=lambda row: row[0])
    lines = [
        title,
        "",
        "Tira 1D100 al crear o reclutar un peque. Si el Trasfondo ya está en la pandilla, repite la tirada hasta obtener uno distinto.",
        "",
        "| D100 | Trasfondo | Efecto |",
        "|---:|---|---|",
    ]
    for number, name, effect in rows:
        safe_name = name.replace("|", "\\|")
        safe_effect = effect.replace("|", "\\|")
        lines.append(f"| {number} | {safe_name} | {safe_effect} |")
    return "\n".join(lines)


def skills_to_table(text: str) -> str:
    """Convert the skill list into a compact Markdown table."""
    title_match = re.search(r"(?m)^##\s+Habilidades\s*$", text)
    if not title_match:
        return text
    intro_and_body = text[title_match.end():].strip()
    first_skill = re.search(r"(?m)^###\s+\d{1,3}\.\s+", intro_and_body)
    if not first_skill:
        return text
    intro = intro_and_body[:first_skill.start()].strip()
    body = intro_and_body[first_skill.start():]
    pattern = re.compile(
        r"(?ms)^###\s+(\d{1,3})\.\s+(.+?)\s*\n(.*?)(?=^###\s+\d{1,3}\.\s+|\Z)"
    )
    rows: list[tuple[int, str, str]] = []
    for match in pattern.finditer(body):
        number = int(match.group(1))
        name = re.sub(r"\s+", " ", match.group(2)).strip()
        effect = re.sub(r"\s+", " ", match.group(3)).strip()
        if effect:
            rows.append((number, name, effect))
    if len(rows) < 5:
        return text
    rows.sort(key=lambda row: row[0])
    lines = ["## Habilidades", ""]
    if intro:
        lines.extend([intro, ""])
    lines.extend([
        "| Nº | Habilidad | Efecto |",
        "|---:|---|---|",
    ])
    for number, name, effect in rows:
        safe_name = name.replace("|", "\\|")
        safe_effect = effect.replace("|", "\\|")
        lines.append(f"| {number} | {safe_name} | {safe_effect} |")
    return "\n".join(lines)


def chapter_image(title: str, page: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if page == 1:
        slug = "bienvenidos-a-patios-portales"
    alt = f"Ilustración estilo garabato noventero para el capítulo «{title}»."
    return f"![{alt}](images/{slug}.png)"


def main() -> None:
    pages = SOURCE.read_text(encoding="utf-8", errors="replace").split("\f")
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    intro = GRID_RULES.split("![PROMPT_PLACEHOLDER]", 1)[0].rstrip()
    document = [intro, ""]
    for page_no in range(1, len(pages)):
        source = clean_source_page(pages[page_no])
        if not source or source == "02":
            continue
        if page_no in CHAPTERS:
            title = CHAPTERS[page_no]
            document.extend([f"# {title}", "", chapter_image(title, page_no), ""])
            if page_no in CHAPTER_EXTRAS:
                document.extend([CHAPTER_EXTRAS[page_no], ""])
        if page_no == 1:
            document.extend([INTRO.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 11:
            document.extend([CREATION_INTRO.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 31:
            skills_text = skills_to_table(SKILLS.read_text(encoding="utf-8"))
            document.extend([skills_text.strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 20:
            background_text = convert_measurements(BACKGROUNDS.read_text(encoding="utf-8"))
            background_text = retitle_backgrounds(editorial_cleanup(background_text))
            background_text = backgrounds_to_table(background_text)
            document.extend([background_text.strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no in EPISODE_STORES:
            document.extend([EPISODE_STORES[page_no].read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 139:
            document.extend([CAMPAIGN_PROGRESS.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 103:
            document.extend([FISHING.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 67:
            document.extend([EPISODE1.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no in EPISODE2_PARTS:
            document.extend([EPISODE2_PARTS[page_no].read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 107:
            document.extend([EPISODE3_INTRO.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 111:
            document.extend([EPISODE3.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no in {108, 112, 113, 114, 115, 116, 117, 118, 119, 120}:
            continue
        if page_no in {84, 85, 86, 87, 88, 91, 92, 94, 95, 96, 97, 98, 102}:
            continue
        if 68 <= page_no <= 78:
            continue
        if 104 <= page_no <= 106:
            continue
        if 140 <= page_no <= 142:
            continue
        if page_no in {82, 110, 124}:
            continue
        if 21 <= page_no <= 30:
            continue
        if 32 <= page_no <= 34:
            continue
        if page_no in {12, 17, 18, 19}:
            continue
        if page_no == 15:
            document.extend([CLUB_NAMES.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 16:
            continue
        if 2 <= page_no <= 10:
            continue
        if page_no == 43:
            document.extend([CORE_RULES.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 36:
            document.extend([EQUIPMENT.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 63:
            document.extend([CAMPAIGN_INTRO.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if 64 <= page_no <= 66:
            continue
        if 37 <= page_no <= 40:
            continue
        if 44 <= page_no <= 62:
            continue
        if page_no in SECTIONS:
            document.extend([f"## {SECTIONS[page_no]}", ""])
        tabular = page_no in {13, 14, 15, 16, 38, 39, 40, 62, 78, 102, 120, 138, 143, 144, 145, 146, 147, 148, 149, 150}
        if page_no == 13:
            document.extend([STUDENT_NAMES.read_text(encoding="utf-8").strip(), ""])
            OUTPUT.write_text("\n".join(document), encoding="utf-8")
            continue
        if page_no == 14:
            continue
        translated = translate(prepare_for_translation(source, tabular=tabular), cache)
        translated = editorial_cleanup(convert_measurements(localize_terms(translated)))
        if tabular:
            formatted = numbered_table(translated) or reflow(translated, tabular=True)
        else:
            formatted = reflow(translated)
            if 64 <= page_no <= 138:
                formatted = format_rule_blocks(formatted)
        # The canonical tables at the start replace these damaged duplicate pages.
        if page_no not in {37, 39}:
            document.extend([formatted, ""])
        OUTPUT.write_text("\n".join(document), encoding="utf-8")
        print(f"{page_no}/{len(pages)-1}", flush=True)
    if PRINTABLE_MAP_PROMPTS.exists():
        document.extend(["", PRINTABLE_MAP_PROMPTS.read_text(encoding="utf-8").strip(), ""])
        OUTPUT.write_text("\n".join(document), encoding="utf-8")
    if OFFICIAL_RULES_ANNEX.exists():
        document.extend(["", OFFICIAL_RULES_ANNEX.read_text(encoding="utf-8").strip(), ""])
        OUTPUT.write_text("\n".join(document), encoding="utf-8")


if __name__ == "__main__":
    main()
