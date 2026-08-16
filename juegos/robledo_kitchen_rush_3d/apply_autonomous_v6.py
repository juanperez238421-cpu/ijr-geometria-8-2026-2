from __future__ import annotations

import base64
import hashlib
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).resolve().parent / '.v6_payload'
EXPECTED_SHA256 = 'b73036b38938f1d13c78e580873145e3dbfb8d8535ade2ec250b83b7c3f6914e'

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

# Normalize one transport-only token corruption detected by CI in the compressed source.
# The active V6 fixture is Grocery Market + Freezer; there is no `kitchen` fixture-cap key.
game_js = ROOT / 'juegos/robledo_kitchen_rush_3d/src/game.js'
text = game_js.read_text(encoding='utf-8')
text = text.replace("kitchen'1", 'grocery:1')

# Senior QA correction: a Prep bot was able to claim a waiter task before the Service Captain
# simply because player updates run in index order. Give an available Service bot strict first
# refusal; non-service bots only cover waiter duty when there is no autonomous Service Captain.
old = "chooseTask(){const g=this.game,m=this.member,role=ROLE_META[m.role];const ready=g.parties.filter(p=>p.state==='readyToOrder'&&!p.orderClaim).sort((a,b)=>b.orderWaitElapsed-a.orderWaitElapsed);if(ready.length&&(role.botBias==='service'||ready[0].orderWaitElapsed>3)){"
new = "chooseTask(){const g=this.game,m=this.member,role=ROLE_META[m.role],hasServiceBot=g.players.some(p=>!p.human&&ROLE_META[p.role]?.botBias==='service');const ready=g.parties.filter(p=>p.state==='readyToOrder'&&!p.orderClaim).sort((a,b)=>b.orderWaitElapsed-a.orderWaitElapsed);if(ready.length&&(role.botBias==='service'||(!hasServiceBot&&ready[0].orderWaitElapsed>3))){"
if old not in text:
    raise SystemExit('Could not apply V6 waiter-priority correction: chooseTask signature not found')
text = text.replace(old, new, 1)
old_fallback = "if(ready.length){const party=ready[0];party.orderClaim=this.id;this.task={kind:'order',party,table:party.table,actions:[{kind:'takeOrder',table:party.table,duration:.8}]};this.record('bot-order-claim',{table:party.table.id+1});}"
new_fallback = "if(ready.length&&(role.botBias==='service'||!hasServiceBot)){const party=ready[0];party.orderClaim=this.id;this.task={kind:'order',party,table:party.table,actions:[{kind:'takeOrder',table:party.table,duration:.8}]};this.record('bot-order-claim',{table:party.table.id+1});}"
if old_fallback not in text:
    raise SystemExit('Could not apply V6 waiter-priority correction: fallback not found')
text = text.replace(old_fallback, new_fallback, 1)
game_js.write_text(text, encoding='utf-8')

print(f'Applied Robledo Kitchen Rush Autonomous Service V6 ({len(archive)} bytes, sha256={digest}).')
