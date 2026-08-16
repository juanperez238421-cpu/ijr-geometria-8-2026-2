from __future__ import annotations
import base64, io, shutil, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "juegos" / "robledo_bistro_godot_staging"
TARGET = ROOT / "juegos" / "robledo_bistro_godot"
parts_dir = STAGING / "fixed_payload"
if parts_dir.is_dir() and all((parts_dir / n).is_file() for n in ("p0a.txt", "p0b.txt", "p0c.txt", "p0d.txt", "p1.txt", "p2.txt", "p3.txt")):
    names = ("p0a.txt", "p0b.txt", "p0c.txt", "p0d.txt", "p1.txt", "p2.txt", "p3.txt")
    payload = "".join((parts_dir / name).read_text(encoding="utf-8").strip() for name in names)
elif parts_dir.is_dir():
    payload = "".join((parts_dir / f"p{i}.txt").read_text(encoding="utf-8").strip() for i in range(4))
else:
    payload = (STAGING / "payload.b64").read_text(encoding="utf-8").strip()
print("Payload characters:", len(payload))
data = base64.b64decode(payload)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
    tf.extractall(ROOT)

if not (TARGET / "project.godot").is_file():
    candidates = [p for p in ROOT.rglob("project.godot") if ".git" not in p.parts]
    print("Godot project candidates:", [str(p.relative_to(ROOT)) for p in candidates])
    source_root = next((p.parent for p in candidates if p.parent != TARGET), None)
    if source_root is None:
        raise FileNotFoundError("No project.godot found after expanding Godot payload")
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_root), str(TARGET))

logo_src = ROOT / "assets" / "logo_colegio_transparente.png"
logo_dst = TARGET / "assets" / "ui" / "school_logo.png"
logo_dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(logo_src, logo_dst)

required = [
    TARGET / "project.godot",
    TARGET / "Main.tscn",
    TARGET / "scripts" / "main.gd",
    TARGET / "scripts" / "customer_actor.gd",
    TARGET / "data" / "recipes.json",
    TARGET / "data" / "questions.json",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
if missing:
    raise FileNotFoundError("Expanded payload is incomplete: " + ", ".join(missing))
print("Applied Robledo Bistro Godot full project payload to", TARGET.relative_to(ROOT))
