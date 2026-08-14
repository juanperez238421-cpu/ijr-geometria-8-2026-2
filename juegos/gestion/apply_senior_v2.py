from __future__ import annotations

import base64
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "juegos" / "gestion" / ".senior_payload"
WORKFLOW = ROOT / ".github" / "workflows" / "package-management-game.yml"

# Preserve the staging workflow. GitHub Actions' GITHUB_TOKEN may update repository
# contents, but it cannot replace workflow files unless it has workflow permission.
workflow_before = WORKFLOW.read_bytes()

payload = "".join((PARTS / f"p{i}.txt").read_text(encoding="utf-8").strip() for i in range(5))
data = base64.b64decode(payload)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
    tf.extractall(ROOT)

WORKFLOW.write_bytes(workflow_before)
print("Applied Robledo Bistro 3D Senior V2 payload (workflow preserved)")
