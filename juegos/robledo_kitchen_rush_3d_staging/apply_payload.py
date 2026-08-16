from __future__ import annotations

import base64
import io
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "juegos" / "robledo_kitchen_rush_3d_staging"
PARTS = STAGING / "payload"
TARGET = ROOT / "juegos" / "robledo_kitchen_rush_3d"
TMP = STAGING / "_expanded"

names = [f"p{i:02d}.txt" for i in range(6)]
missing = [name for name in names if not (PARTS / name).is_file()]
if missing:
    raise FileNotFoundError("Missing payload parts: " + ", ".join(missing))

payload = "".join((PARTS / name).read_text(encoding="utf-8").strip() for name in names)
print("Three.js payload characters:", len(payload))
data = base64.b64decode(payload)

if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
    tf.extractall(TMP)

source = TMP / "robledo_kitchen_rush_3d"
if not (source / "src" / "game.js").is_file():
    raise FileNotFoundError("Expanded payload does not contain src/game.js")
if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.parent.mkdir(parents=True, exist_ok=True)
shutil.move(str(source), str(TARGET))
shutil.rmtree(TMP, ignore_errors=True)

required = [
    TARGET / "index.html",
    TARGET / "style.css",
    TARGET / "package.json",
    TARGET / "README.md",
    TARGET / "src" / "game.js",
    TARGET / "scripts" / "build.mjs",
    TARGET / "scripts" / "check.mjs",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
if missing:
    raise FileNotFoundError("Expanded Three.js source is incomplete: " + ", ".join(missing))
print("Applied full Robledo Kitchen Rush 3D source to", TARGET.relative_to(ROOT))
