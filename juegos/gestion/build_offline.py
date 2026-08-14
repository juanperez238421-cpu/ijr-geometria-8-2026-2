from __future__ import annotations

import base64
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "juegos" / "gestion"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

index = (GAME / "index.html").read_text(encoding="utf-8")
css = (GAME / "style.css").read_text(encoding="utf-8")
js = (GAME / "game.js").read_text(encoding="utf-8")
logo = (ROOT / "assets" / "logo_ijr.svg").read_bytes()
logo64 = base64.b64encode(logo).decode("ascii")

standalone = index.replace(
    '<link rel="stylesheet" href="style.css" />',
    f"<style>\n{css}\n</style>",
)
standalone = standalone.replace(
    '<script src="game.js"></script>',
    f"<script>\n{js}\n</script>",
)
standalone = standalone.replace(
    '../../assets/logo_ijr.svg',
    f'data:image/svg+xml;base64,{logo64}',
)

html_path = DIST / "Pixel_Plaza_Manager_OFFLINE.html"
html_path.write_text(standalone, encoding="utf-8")

readme = """PIXEL PLAZA MANAGER — OFFLINE PACKAGE\n\n1. Extrae el ZIP.\n2. Abre Pixel_Plaza_Manager_OFFLINE.html en Chrome, Edge o Firefox.\n3. No requiere Internet, servidor ni instalación.\n4. El progreso se guarda en localStorage del navegador.\n\nEl cuestionario de Geometría aparece únicamente al perder una vida.\n"""
readme_path = DIST / "LEEME.txt"
readme_path.write_text(readme, encoding="utf-8")

zip_path = DIST / "Pixel_Plaza_Manager_OFFLINE_Package.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    zf.write(html_path, html_path.name)
    zf.write(readme_path, readme_path.name)

print(html_path)
print(zip_path)
