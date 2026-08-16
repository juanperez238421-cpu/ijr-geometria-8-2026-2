from __future__ import annotations
import base64, io, shutil, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "juegos" / "robledo_bistro_godot_staging"
payload = (STAGING / "payload.b64").read_text(encoding="utf-8").strip()
data = base64.b64decode(payload)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
    tf.extractall(ROOT)
logo_src = ROOT / "assets" / "logo_colegio_transparente.png"
logo_dst = ROOT / "juegos" / "robledo_bistro_godot" / "assets" / "ui" / "school_logo.png"
logo_dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(logo_src, logo_dst)
print("Applied Robledo Bistro Godot full project payload")
