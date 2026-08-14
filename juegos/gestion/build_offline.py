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
logo = (ROOT / "assets" / "logo_colegio_transparente.png").read_bytes()
logo64 = base64.b64encode(logo).decode("ascii")
logo_uri = f"data:image/png;base64,{logo64}"

standalone = index.replace(
    '<link rel="stylesheet" href="style.css" />',
    f"<style>\n{css}\n</style>",
)
standalone = standalone.replace(
    '<script src="game.js"></script>',
    f"<script>\n{js}\n</script>",
)
standalone = standalone.replace(
    '../../assets/logo_colegio_transparente.png',
    logo_uri,
)

html_path = DIST / "Robledo_Bistro_3D_OFFLINE.html"
html_path.write_text(standalone, encoding="utf-8")

readme = """ROBLEDO BISTRO 3D — OFFLINE PACKAGE

1. Extrae el ZIP.
2. Abre Robledo_Bistro_3D_OFFLINE.html en Chrome, Edge o Firefox.
3. No requiere Internet, servidor, instalación ni librerías externas.
4. Controles: WASD/flechas para moverse, Shift para correr, E para interactuar y Q para desechar el plato actual.
5. El juego utiliza un entorno low-poly 3D renderizado directamente en Canvas y funciona desde un único archivo HTML.
6. El logo oficial del Instituto Jorge Robledo está incrustado dentro del archivo offline.
7. El cuestionario de Geometría aparece únicamente cuando el jugador pierde una vida.

Flujo principal: refrigerador -> preparación -> cocción (según receta) -> pase de servicio. Entre días se compran mejoras de cocina, decoración y personal.
"""
readme_path = DIST / "LEEME.txt"
readme_path.write_text(readme, encoding="utf-8")

zip_path = DIST / "Robledo_Bistro_3D_OFFLINE_Package.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    zf.write(html_path, html_path.name)
    zf.write(readme_path, readme_path.name)

print(html_path)
print(zip_path)
