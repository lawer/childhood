# Patis i Portals — Edició catalana per a quadrícula

Repositori estàtic amb l’adaptació editorial de **Patis i Portals** al català i a tauler de caselles.

## Entrada principal

Obre `index.html` per navegar pel projecte:

- Manual HTML complet: `patios_portales_es.html`
- Font Markdown per exportar a PDF: `patios_portales_es.md`
- Versió catalana: `index_ca.html`, `patis_portals_ca.html`, `patis_portals_ca.md`
- Parcials font: `partials/`
- Fulls d’estil: `styles/`
- Utilitats JavaScript: `tools/` i `scripts/`
- Mapes imprimibles: `maps/printable/`
- Prompts de mapes: `maps/printable-map-prompts.md`
- Mapes tàctics SVG: `maps/`
- Imatges editorials: `images/`

Les utilitats de `tools/` estan fetes amb Alpine.js local i taules incrustades a `scripts/tools.js`, així que també funcionen obrint l’HTML com a fitxer local.

## Publicar a GitHub Pages

Hi ha dues formes vàlides.

### Opció A: desplegament des d’una branca

1. Puja el repositori a GitHub.
2. Ves a `Settings → Pages`.
3. A `Build and deployment`, selecciona `Deploy from a branch`.
4. Tria la branca principal (`main` o `master`) i la carpeta `/root`.
5. Desa.

GitHub Pages farà servir `index.html` com a punt d’entrada.

### Opció B: GitHub Actions

El repositori inclou `.github/workflows/pages.yml`.

1. Ves a `Settings → Pages`.
2. A `Build and deployment`, selecciona `GitHub Actions`.
3. Fes push a `main`.

El workflow publica una còpia estàtica neta amb HTML, Markdown, imatges i mapes.

## Regenerar el manual

Si modifiques els fragments Markdown font, pots regenerar el document editorial amb:

```bash
python3 build_manual_editorial.py
python3 build_catalan_versions.py
python3 polish_catalan.py
python3 build_manual_html.py
```

> Ajusta la ruta de Python si fas servir un altre entorn virtual.
