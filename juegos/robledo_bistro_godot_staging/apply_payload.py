from __future__ import annotations
import base64, io, shutil, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "juegos" / "robledo_bistro_godot_staging"
TARGET = ROOT / "juegos" / "robledo_bistro_godot"

# Expand the complete Godot source from deterministic text-safe payload parts.
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

# Install a validated, optimized copy of the real Instituto Jorge Robledo logo.
logo_parts = STAGING / "logo_payload"
logo_dst = TARGET / "assets" / "ui" / "school_logo.webp"
if logo_parts.is_dir() and all((logo_parts / f"l{i}.txt").is_file() for i in range(4)):
    logo_b64 = "".join((logo_parts / f"l{i}.txt").read_text(encoding="utf-8").strip() for i in range(4))
    logo_dst.parent.mkdir(parents=True, exist_ok=True)
    logo_dst.write_bytes(base64.b64decode(logo_b64))
else:
    raise FileNotFoundError("Validated school logo payload is missing")

# Godot 4.3 requires explicit Variant/float typing in several dynamic game-state paths.
main_path = TARGET / "scripts" / "main.gd"
main_text = main_path.read_text(encoding="utf-8")
patches = {
    'var action := null': 'var action: Variant = null',
    'var current_quiz := null': 'var current_quiz: Variant = null',
    'var tip_rate:=clamp((g["patience"]-20.0)/220.0,0.02,0.28)+game["rep"]/1000.0': 'var tip_rate: float = float(clamp((float(g["patience"])-20.0)/220.0,0.02,0.28)) + float(game["rep"])/1000.0',
    'var total:=subtotal*(1.0+tip_rate)': 'var total: float = subtotal * (1.0 + tip_rate)',
    'var bonus:=game["staff"]["host"]*3.0': 'var bonus: float = float(game["staff"]["host"]) * 3.0',
    'var o=_order_by_id(id)\n\tif o!=null:\n\t\to["state"]="cancelled"': 'var o: Variant = _order_by_id(id)\n\tif o != null:\n\t\to["state"] = "cancelled"',
    'res://assets/ui/school_logo.png': 'res://assets/ui/school_logo.webp',
}
for old, new in patches.items():
    if old not in main_text:
        print("Patch already applied or source changed:", old[:70])
    else:
        main_text = main_text.replace(old, new)
main_path.write_text(main_text, encoding="utf-8")

required = [
    TARGET / "project.godot",
    TARGET / "Main.tscn",
    TARGET / "scripts" / "main.gd",
    TARGET / "scripts" / "customer_actor.gd",
    TARGET / "data" / "recipes.json",
    TARGET / "data" / "questions.json",
    logo_dst,
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
if missing:
    raise FileNotFoundError("Expanded payload is incomplete: " + ", ".join(missing))
print("Applied Robledo Bistro Godot full project payload to", TARGET.relative_to(ROOT))
