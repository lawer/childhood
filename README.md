# Childhood — Edición española para cuadrícula

Repositorio estático con la adaptación editorial de **Childhood** al castellano de España y a tablero de casillas.

## Entrada principal

Abre `index.html` para navegar el proyecto:

- Manual HTML completo: `childhood_es_grid.html`
- Fuente Markdown para exportar a PDF: `childhood_es_grid.md`
- Mapas imprimibles: `maps/printable/`
- Prompts de mapas: `maps/printable-map-prompts.md`
- Mapas tácticos SVG: `maps/`
- Imágenes editoriales: `images/`

## Publicar en GitHub Pages

Hay dos formas válidas.

### Opción A: Deploy from branch

1. Sube el repositorio a GitHub.
2. Ve a `Settings → Pages`.
3. En `Build and deployment`, selecciona `Deploy from a branch`.
4. Elige la rama principal (`main` o `master`) y la carpeta `/root`.
5. Guarda.

GitHub Pages usará `index.html` como punto de entrada.

### Opción B: GitHub Actions

El repositorio incluye `.github/workflows/pages.yml`.

1. Ve a `Settings → Pages`.
2. En `Build and deployment`, selecciona `GitHub Actions`.
3. Haz push a `main`.

El workflow publica una copia estática limpia con HTML, Markdown, imágenes y mapas.

## Regenerar el manual

Si modificas los fragmentos Markdown fuente, puedes regenerar el documento editorial con:

```bash
/tmp/childhood-venv/bin/python build_childhood_editorial.py
pandoc childhood_es_grid.md \
  --from=gfm \
  --to=html5 \
  --standalone \
  --toc \
  --toc-depth=2 \
  --metadata lang=es-ES \
  --metadata title='Childhood — Edición española para cuadrícula' \
  --include-in-header=childhood_header.html \
  --output=childhood_es_grid.html
```

> Ajusta la ruta de Python si usas otro entorno virtual.
