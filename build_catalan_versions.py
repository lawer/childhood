#!/usr/bin/env python3
"""Create Catalan document variants without external translation services.

This is intentionally local/offline. It applies a curated project glossary and
common sentence/term transformations so the repository has parallel CA files
that can be edited by hand over time.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(".")
PARTIALS = ROOT / "partials"


FILES = [
    ROOT / "patios_portales_es.md",
    ROOT / "maps/printable-map-prompts.md",
    ROOT / "README.md",
    *sorted(PARTIALS.glob("*_es.md")),
]


TARGETS = {
    ROOT / "patios_portales_es.md": ROOT / "patis_portals_ca.md",
    ROOT / "maps/printable-map-prompts.md": ROOT / "maps/printable-map-prompts_ca.md",
    ROOT / "README.md": ROOT / "README_CA.md",
}


PHRASES = {
    "Edición española para tablero de casillas": "Edició catalana per a tauler de caselles",
    "Edición española para cuadrícula": "Edició catalana per a quadrícula",
    "edición española para cuadrícula": "edició catalana per a quadrícula",
    "Regla de oro": "Regla d'or",
    "tablero de casillas": "tauler de caselles",
    "tablero": "tauler",
    "cuadrícula": "quadrícula",
    "casillas": "caselles",
    "casilla": "casella",
    "redondeando hacia arriba": "arrodonint cap amunt",
    "Movimiento base": "Moviment base",
    "Movimiento ortogonal": "Moviment ortogonal",
    "Distancias y alcances": "Distàncies i abasts",
    "Cuerpo a cuerpo": "Cos a cos",
    "Línea de visión": "Línia de visió",
    "Apariciones": "Aparicions",
    "Empujón o retroceso": "Empenta o retrocés",
    "Áreas": "Àrees",
    "Referencia rápida de conversiones": "Referència ràpida de conversions",
    "Bienvenidos a Patios & Portales": "Benvinguts a Patis i Portals",
    "Patios & Portales": "Patis i Portals",
    "Crear la pandilla": "Crear la colla",
    "Formar la pandilla": "Formar la colla",
    "Nombres para la pandilla": "Noms per a la colla",
    "Registro escolar": "Registre escolar",
    "nombres y apellidos": "noms i cognoms",
    "Nombre o apodo": "Nom o malnom",
    "Apellido": "Cognom",
    "Tabla de Trasfondos": "Taula de rerefons",
    "Trasfondos": "Rerefons",
    "Trasfondo": "Rerefons",
    "Habilidades": "Habilitats",
    "Habilidad": "Habilitat",
    "Equipo, tiendas y cachivaches": "Equip, botigues i rampoines",
    "Reglas de juego": "Regles de joc",
    "Cómo funciona la campaña": "Com funciona la campanya",
    "Campaña y progreso": "Campanya i progrés",
    "Anexos y tablas": "Annexos i taules",
    "Interludio": "Interludi",
    "Nos vamos de pesca": "Anem a pescar",
    "Normas oficiales sin adaptar a casillas": "Normes oficials sense adaptar a caselles",
    "normas oficiales sin adaptar a casillas": "normes oficials sense adaptar a caselles",
    "Preparar y jugar una partida": "Preparar i jugar una partida",
    "Preparar la partida": "Preparar la partida",
    "Secuencia de la ronda": "Seqüència de la ronda",
    "Activar a un peque": "Activar un menut",
    "Despliegue e iniciativa": "Desplegament i iniciativa",
    "Movimiento oficial": "Moviment oficial",
    "Combate cuerpo a cuerpo oficial": "Combat cos a cos oficial",
    "Combate a distancia oficial": "Combat a distància oficial",
    "Armas arrojadizas": "Armes llancívoles",
    "Daño y armadura": "Dany i armadura",
    "Abandonar combate": "Abandonar el combat",
    "Pruebas de Gallina": "Proves de Gallina",
    "Consecuencias y estados": "Conseqüències i estats",
    "Aparición oficial de Malos": "Aparició oficial de Dolents",
    "Tareas oficiales": "Tasques oficials",
    "Prompts para mapas imprimibles": "Prompts per a mapes imprimibles",
    "Archivo sugerido": "Fitxer suggerit",
    "Recomendación de salida": "Recomanació de sortida",
    "Mapas imprimibles": "Mapes imprimibles",
    "Mapas tácticos": "Mapes tàctics",
    "Imágenes editoriales": "Imatges editorials",
    "Utilidades JavaScript": "Utilitats JavaScript",
    "Repositorio estático": "Repositori estàtic",
    "Entrada principal": "Entrada principal",
    "Publicar en GitHub Pages": "Publicar a GitHub Pages",
    "Regenerar el manual": "Regenerar el manual",
}


TERMS = {
    "pandilla": "colla",
    "pandillas": "colles",
    "peques": "menuts",
    "peque": "menut",
    "Malos": "Dolents",
    "Malo": "Dolent",
    "Tareas": "Tasques",
    "Tarea": "Tasca",
    "Ánimo": "Ànim",
    "Mente": "Ment",
    "Corazón": "Cor",
    "Cuerpo": "Cos",
    "Molar": "Molar",
    "Salud": "Salut",
    "Defensa": "Defensa",
    "Daño": "Dany",
    "chapas": "xapes",
    "chapa": "xapa",
    "botín": "botí",
    "arma": "arma",
    "armas": "armes",
    "alcance": "abast",
    "distancia": "distància",
    "movimiento": "moviment",
    "Movimiento": "Moviment",
    "prueba": "prova",
    "pruebas": "proves",
    "tirada": "tirada",
    "tiradas": "tirades",
    "éxito": "èxit",
    "éxitos": "èxits",
    "pifia": "pífia",
    "pifias": "pífies",
    "crítico": "crític",
    "críticos": "crítics",
    "ronda": "ronda",
    "aventura": "aventura",
    "campaña": "campanya",
    "mesa": "taula",
    "borde": "vora",
    "bordes": "vores",
    "objetivo": "objectiu",
    "objetivos": "objectius",
    "adyacente": "adjacent",
    "adyacentes": "adjacents",
    "diagonal": "diagonal",
    "diagonales": "diagonals",
    "cobertura": "cobertura",
    "terreno": "terreny",
    "infranqueable": "infranquejable",
    "recompensa": "recompensa",
    "consecuencia": "conseqüència",
    "consecuencias": "conseqüències",
    "niños": "nens",
    "niño": "nen",
    "chavales": "canalla",
    "jugadores": "jugadors",
    "jugador": "jugador",
    "miniatura": "miniatura",
    "miniaturas": "miniatures",
    "mapas": "mapes",
    "mapa": "mapa",
    "imágenes": "imatges",
    "imagen": "imatge",
    "fuente": "font",
    "fuentes": "fonts",
    "fichero": "fitxer",
    "archivo": "fitxer",
    "archivos": "fitxers",
    "enlace": "enllaç",
    "enlaces": "enllaços",
}


INFLECTIONS = [
    (r"\bEl\b", "El"),
    (r"\bLa\b", "La"),
    (r"\bLos\b", "Els"),
    (r"\bLas\b", "Les"),
    (r"\bel\b", "el"),
    (r"\bla\b", "la"),
    (r"\blos\b", "els"),
    (r"\blas\b", "les"),
    (r"\bde la\b", "de la"),
    (r"\bdel\b", "del"),
    (r"\bpara\b", "per a"),
    (r"\bcon\b", "amb"),
    (r"\bsin\b", "sense"),
    (r"\bdesde\b", "des de"),
    (r"\bhasta\b", "fins a"),
    (r"\bcuando\b", "quan"),
    (r"\bporque\b", "perquè"),
    (r"\bpuede\b", "pot"),
    (r"\bpueden\b", "poden"),
    (r"\bdebe\b", "ha de"),
    (r"\bdeben\b", "han de"),
    (r"\bobtiene\b", "obté"),
    (r"\bobtienen\b", "obtenen"),
    (r"\bgana\b", "guanya"),
    (r"\bganan\b", "guanyen"),
    (r"\bpierde\b", "perd"),
    (r"\bpierden\b", "perden"),
    (r"\btira\b", "tira"),
    (r"\btirad\b", "tireu"),
    (r"\belige\b", "tria"),
    (r"\beligid\b", "trieu"),
    (r"\bcoloca\b", "col·loca"),
    (r"\bcolocad\b", "col·loqueu"),
    (r"\bconsulta\b", "consulta"),
    (r"\busa\b", "fes servir"),
    (r"\busar\b", "fer servir"),
    (r"\bdivide\b", "divideix"),
    (r"\bsuma\b", "suma"),
    (r"\bresta\b", "resta"),
    (r"\bsi\b", "si"),
]


def translate_text(text: str) -> str:
    out: list[str] = []
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
        else:
            out.append(translate_line(line))
    return "\n".join(out).replace("Patios & Portales — Edición", "Patis i Portals — Edició")


def translate_line(line: str) -> str:
    # Keep file paths stable.
    protected: list[str] = []

    def keep(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"§§{len(protected) - 1}§§"

    line = re.sub(r"`[^`]+`", keep, line)
    line = re.sub(r"\]\([^)]+\)", keep, line)
    line = re.sub(r'src="[^"]+"', keep, line)
    line = re.sub(r'href="[^"]+"', keep, line)

    for src, dst in sorted(PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        line = line.replace(src, dst)

    for src, dst in sorted(TERMS.items(), key=lambda item: len(item[0]), reverse=True):
        line = re.sub(rf"\b{re.escape(src)}\b", dst, line)

    for pattern, repl in INFLECTIONS:
        line = re.sub(pattern, repl, line)

    fixes = {
        "per a a": "per a",
        "a el ": "al ",
        "de el ": "del ",
        "els Dolents": "els Dolents",
        "les Dolents": "els Dolents",
        "la colla": "la colla",
        "del colla": "de la colla",
        "el colla": "la colla",
        "un menut": "un menut",
        "una menut": "un menut",
        "els menuts": "els menuts",
        "les menuts": "els menuts",
        "a caselles": "a caselles",
        "per a caselles": "per a caselles",
        "GitHub Pages": "GitHub Pages",
    }
    for src, dst in fixes.items():
        line = line.replace(src, dst)

    for index, value in enumerate(protected):
        line = line.replace(f"§§{index}§§", value)
    return line


def target_for(path: Path) -> Path:
    if path in TARGETS:
        return TARGETS[path]
    name = path.name
    if name.endswith("_es.md"):
        return path.with_name(name[:-6] + "_ca.md")
    raise ValueError(path)


def main() -> None:
    for path in FILES:
        if not path.exists():
            continue
        target = target_for(path)
        translated = translate_text(path.read_text(encoding="utf-8"))
        target.write_text(translated.rstrip() + "\n", encoding="utf-8")
        print(f"{path} -> {target}")


if __name__ == "__main__":
    main()
