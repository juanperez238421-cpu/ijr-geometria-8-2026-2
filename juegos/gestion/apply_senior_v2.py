from __future__ import annotations

import base64
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "juegos" / "gestion" / ".senior_payload"
payload = "".join((PARTS / f"p{i}.txt").read_text(encoding="utf-8").strip() for i in range(5))
data = base64.b64decode(payload)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
    tf.extractall(ROOT)
print("Applied Robledo Bistro 3D Senior V2 payload")
