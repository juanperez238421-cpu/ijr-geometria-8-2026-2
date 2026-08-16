from __future__ import annotations

import base64
import hashlib
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).resolve().parent / '.v6_payload'
EXPECTED_SHA256 = '6fb6170dfbc3bd40ff13180971809919fe1a509ff6efddf480a56b84b21e460b'

parts = sorted(PAYLOAD.glob('part_*.b64'))
if len(parts) != 11:
    raise SystemExit(f'Expected 11 Autonomous V6 payload parts, found {len(parts)}')
encoded = ''.join(p.read_text(encoding='utf-8').strip() for p in parts)
archive = base64.b64decode(encoded, validate=True)
digest = hashlib.sha256(archive).hexdigest()
if digest != EXPECTED_SHA256:
    raise SystemExit(f'Autonomous V6 payload checksum mismatch: {digest}')
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tf:
    for member in tf.getmembers():
        target = (ROOT / member.name).resolve()
        if ROOT.resolve() not in target.parents and target != ROOT.resolve():
            raise SystemExit(f'Unsafe archive path: {member.name}')
    tf.extractall(ROOT)
print(f'Applied Robledo Kitchen Rush Autonomous Service V6 ({len(archive)} bytes, sha256={digest}).')
