from __future__ import annotations
import base64, mimetypes, re, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "juegos" / "gestion"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
index = (GAME / "index.html").read_text(encoding="utf-8")
css = (GAME / "style.css").read_text(encoding="utf-8")
js = (GAME / "game.js").read_text(encoding="utf-8")

def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"

# Real school logo.
logo = ROOT / "assets" / "logo_colegio_transparente.png"
logo_uri = data_uri(logo)
index = index.replace("../../assets/logo_colegio_transparente.png", logo_uri)
js = js.replace("../../assets/logo_colegio_transparente.png", logo_uri)

# Original game SVG assets referenced by HTML or JS.
asset_dir = GAME / "assets"
for asset in sorted(asset_dir.glob("*.svg")):
    rel = f"assets/{asset.name}"
    uri = data_uri(asset)
    index = index.replace(rel, uri)
    js = js.replace(rel, uri)

standalone = index.replace('<link rel="stylesheet" href="style.css" />', f"<style>\n{css}\n</style>")
standalone = standalone.replace('<script src="game.js"></script>', f"<script>\n{js}\n</script>")
html_path = DIST / "Robledo_Bistro_3D_SENIOR_OFFLINE.html"
html_path.write_text(standalone, encoding="utf-8")
readme = """ROBLEDO BISTRO 3D SENIOR — OFFLINE\n\n1. Extrae el ZIP.\n2. Abre Robledo_Bistro_3D_SENIOR_OFFLINE.html en Chrome, Edge o Firefox.\n3. No requiere servidor, instalación ni Internet.\n4. El progreso y mejor puntaje se guardan localmente en el navegador.\n\nControles: WASD/flechas mover, Shift correr, E interactuar, Q desechar, M carta, Tab mapa.\nLos clientes se sientan, leen el menú y eligen platos. La geometría aparece únicamente al perder una vida.\n"""
readme_path = DIST / "LEEME.txt"
readme_path.write_text(readme, encoding="utf-8")
zip_path = DIST / "Robledo_Bistro_3D_SENIOR_OFFLINE_Package.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    zf.write(html_path, html_path.name); zf.write(readme_path, readme_path.name)
print(html_path); print(zip_path)
