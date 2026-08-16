from __future__ import annotations

import base64
import hashlib
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).resolve().parent / '.v5_payload'
EXPECTED_SHA256 = 'ccb7f35dfcdb453766e97130f5e6c9318591e825dcdf3963498c86b9b1746f0c'

parts = sorted(PAYLOAD.glob('part_*.b64'))
if len(parts) != 7:
    raise SystemExit(f'Expected 7 Progressive V5 payload parts, found {len(parts)}')

encoded = ''.join(p.read_text(encoding='utf-8').strip() for p in parts)
archive = base64.b64decode(encoded, validate=True)
digest = hashlib.sha256(archive).hexdigest()
if digest != EXPECTED_SHA256:
    raise SystemExit(f'Progressive V5 payload checksum mismatch: {digest}')

with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tf:
    members = tf.getmembers()
    for member in members:
        target = (ROOT / member.name).resolve()
        if ROOT.resolve() not in target.parents and target != ROOT.resolve():
            raise SystemExit(f'Unsafe archive path: {member.name}')
    tf.extractall(ROOT)

print(f'Applied Robledo Kitchen Rush 3D Progressive V5 ({len(archive)} archive bytes, sha256={digest}).')
