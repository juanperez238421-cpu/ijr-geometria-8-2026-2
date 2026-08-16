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

game_js = ROOT / 'juegos/robledo_kitchen_rush_3d/src/game.js'
text = game_js.read_text(encoding='utf-8')

# Transport normalization detected by CI. V6 uses one Grocery Market + Freezer fixture.
text = text.replace("kitchen'1", 'grocery:1')

# Service Captain has strict first refusal on waiter work when an autonomous service bot exists.
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

# Software-WebGL CI can render at only a few frames per second. Keep normal gameplay unchanged,
# but expose an opt-in QA-only process multiplier so unattended stove/fryer/oven state transitions
# can still be exercised through the real station state machine in a deterministic CI window.
old_station = "updateStations(dt){for(const s of this.stations){if(!['stove','fryer','oven'].includes(s.type)||!s.slot)continue;s.cook+=dt;"
new_station = "updateStations(dt){const processDt=dt*(this.qaProcessScale||1);for(const s of this.stations){if(!['stove','fryer','oven'].includes(s.type)||!s.slot)continue;s.cook+=processDt;"
if old_station not in text:
    raise SystemExit('Could not apply V6 QA process-scale hook')
text = text.replace(old_station, new_station, 1)
game_js.write_text(text, encoding='utf-8')

# Deterministic professional E2E under SwiftShader: navigation remains physical/collision-aware;
# only bot walking speed, crew work multipliers and unattended process timers are accelerated.
smoke = ROOT / 'juegos/robledo_kitchen_rush_3d/scripts/smoke.mjs'
s = smoke.read_text(encoding='utf-8')
old_started = "g.spawnTimer=999;g.players.filter(p=>!p.human).forEach(p=>p.speed=7.8);return{hud:"
new_started = "g.spawnTimer=999;g.qaProcessScale=10;g.players.filter(p=>!p.human).forEach(p=>{p.speed=14;const base=p.workMultiplier.bind(p);p.workMultiplier=k=>base(k)*8;});return{hud:"
if old_started not in s:
    raise SystemExit('Could not configure deterministic V6 browser QA acceleration')
s = s.replace(old_started, new_started, 1)

needle = "await waitEval(cdp,`window.__rkrGame.qaEvents.some(e=>e.type==='bot-order-taken')`,9000);"
diag = "await sleep(1800);const waiterDiag=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.parties[0];return{party:{state:p?.state,claim:p?.orderClaim,table:p?.table?.id+1,pos:p?.table?.pos&&{x:p.table.pos.x,z:p.table.pos.z}},bots:g.players.filter(x=>!x.human).map(x=>({i:x.index,role:x.role,pos:{x:+x.group.position.x.toFixed(2),z:+x.group.position.z.toFixed(2)},task:x.bot?.task?.kind||null,action:x.bot?.task?.actions?.[x.bot?.actionIndex]?.kind||null})),events:g.qaEvents.map(e=>e.type)};})()`);console.log('V6 waiter diagnostic:',JSON.stringify(waiterDiag));\nawait waitEval(cdp,`window.__rkrGame.qaEvents.some(e=>e.type==='bot-order-taken')`,15000);"
if needle not in s:
    raise SystemExit('Could not add V6 waiter QA diagnostic')
s = s.replace(needle, diag, 1)
s = s.replace("e.recipe==='salad')`,26000,150", "e.recipe==='salad')`,45000,150")
s = s.replace("e.type==='bot-order-taken')`,9000);", "e.type==='bot-order-taken')`,15000);")
s = s.replace("e.recipe==='burger')`,28000,150", "e.recipe==='burger')`,60000,150")
s = s.replace("e.type==='bot-clean-cycle')`,15000,150", "e.type==='bot-clean-cycle')`,30000,150")
smoke.write_text(s, encoding='utf-8')

print(f'Applied Robledo Kitchen Rush Autonomous Service V6 ({len(archive)} bytes, sha256={digest}).')
