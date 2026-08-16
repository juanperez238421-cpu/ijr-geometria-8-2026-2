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
text = text.replace("kitchen'1", 'grocery:1')

# Service Captain gets strict first refusal on waiter work when one is autonomous.
old = "chooseTask(){const g=this.game,m=this.member,role=ROLE_META[m.role];const ready=g.parties.filter(p=>p.state==='readyToOrder'&&!p.orderClaim).sort((a,b)=>b.orderWaitElapsed-a.orderWaitElapsed);if(ready.length&&(role.botBias==='service'||ready[0].orderWaitElapsed>3)){"
new = "chooseTask(){const g=this.game,m=this.member,role=ROLE_META[m.role],hasServiceBot=g.players.some(p=>!p.human&&ROLE_META[p.role]?.botBias==='service');const ready=g.parties.filter(p=>p.state==='readyToOrder'&&!p.orderClaim).sort((a,b)=>b.orderWaitElapsed-a.orderWaitElapsed);if(ready.length&&(role.botBias==='service'||(!hasServiceBot&&ready[0].orderWaitElapsed>3))){"
if old not in text: raise SystemExit('Could not apply V6 waiter-priority correction')
text = text.replace(old, new, 1)
old_fallback = "if(ready.length){const party=ready[0];party.orderClaim=this.id;this.task={kind:'order',party,table:party.table,actions:[{kind:'takeOrder',table:party.table,duration:.8}]};this.record('bot-order-claim',{table:party.table.id+1});}"
new_fallback = "if(ready.length&&(role.botBias==='service'||!hasServiceBot)){const party=ready[0];party.orderClaim=this.id;this.task={kind:'order',party,table:party.table,actions:[{kind:'takeOrder',table:party.table,duration:.8}]};this.record('bot-order-claim',{table:party.table.id+1});}"
if old_fallback not in text: raise SystemExit('Could not apply V6 waiter-priority fallback correction')
text = text.replace(old_fallback, new_fallback, 1)

# Collision-aware approach points for all physical rectangular fixtures.
old_near = "  near(target,dt){const m=this.member,g=this.game,pos=target?.pos||target?.group?.position;if(!pos)return false;const v=new THREE.Vector3(pos.x-m.group.position.x,0,pos.z-m.group.position.z),d=v.length(),stop=target.type==='table'?1.46:target.type==='storage'?.92:1.18;if(d>stop){v.normalize();m.facing.copy(v);m.group.rotation.y=Math.atan2(v.x,v.z);const before=m.group.position.clone();g.moveCrew(m,v.clone().multiplyScalar(m.speed*.9*dt));if(before.distanceToSquared(m.group.position)<1e-7){const side=new THREE.Vector3(-v.z,0,v.x).multiplyScalar(this.avoidSign);g.moveCrew(m,side.multiplyScalar(m.speed*.72*dt));if(before.distanceToSquared(m.group.position)<1e-7){this.avoidSign*=-1;}}m.animate(dt,true,.95);return false;}m.animate(dt,false);return true;}"
new_near = "  approachPoint(target){const m=this.member,g=this.game,pos=target?.pos||target?.group?.position;if(!pos||target.type==='storage')return pos;const o=g.obstacles.find(x=>x.type===target.type&&Math.abs(x.x-pos.x)<.08&&Math.abs(x.z-pos.z)<.08);if(!o)return pos;const pad=m.radius+.18,candidates=[new THREE.Vector3(o.x,0,o.z-o.d/2-pad),new THREE.Vector3(o.x+o.w/2+pad,0,o.z),new THREE.Vector3(o.x,0,o.z+o.d/2+pad),new THREE.Vector3(o.x-o.w/2-pad,0,o.z)];const valid=candidates.filter(p=>!g.blocked(m,p));const pool=valid.length?valid:candidates;pool.sort((a,b)=>a.distanceToSquared(m.group.position)-b.distanceToSquared(m.group.position));return pool[0];}\n  near(target,dt){const m=this.member,g=this.game,raw=target?.pos||target?.group?.position;if(!raw)return false;const pos=this.approachPoint(target)||raw,v=new THREE.Vector3(pos.x-m.group.position.x,0,pos.z-m.group.position.z),d=v.length(),stop=target.type==='storage'?.72:.24;if(d>stop){v.normalize();m.facing.copy(v);m.group.rotation.y=Math.atan2(v.x,v.z);const before=m.group.position.clone();g.moveCrew(m,v.clone().multiplyScalar(m.speed*.9*dt));if(before.distanceToSquared(m.group.position)<1e-7){const side=new THREE.Vector3(-v.z,0,v.x).multiplyScalar(this.avoidSign);g.moveCrew(m,side.multiplyScalar(m.speed*.72*dt));if(before.distanceToSquared(m.group.position)<1e-7)this.avoidSign*=-1;}m.animate(dt,true,.95);return false;}m.animate(dt,false);return true;}"
if old_near not in text: raise SystemExit('Could not apply V6 collision-aware navigation correction')
text = text.replace(old_near, new_near, 1)

# QA-only process acceleration; normal gameplay remains multiplier 1.
old_station = "updateStations(dt){for(const s of this.stations){if(!['stove','fryer','oven'].includes(s.type)||!s.slot)continue;s.cook+=dt;"
new_station = "updateStations(dt){const processDt=dt*(this.qaProcessScale||1);for(const s of this.stations){if(!['stove','fryer','oven'].includes(s.type)||!s.slot)continue;s.cook+=processDt;"
if old_station not in text: raise SystemExit('Could not apply V6 QA process-scale hook')
text = text.replace(old_station, new_station, 1)
game_js.write_text(text, encoding='utf-8')

smoke = ROOT / 'juegos/robledo_kitchen_rush_3d/scripts/smoke.mjs'
s = smoke.read_text(encoding='utf-8')
s = s.replace("for(let i=0;i<160;i++)", "for(let i=0;i<600;i++)", 1)
old_started = "g.spawnTimer=999;g.players.filter(p=>!p.human).forEach(p=>p.speed=7.8);return{hud:"
new_started = "g.spawnTimer=999;g.qaProcessScale=15;g.players.filter(p=>!p.human).forEach(p=>{p.speed=20;const base=p.workMultiplier.bind(p);p.workMultiplier=k=>base(k)*12;});return{hud:"
if old_started not in s: raise SystemExit('Could not configure deterministic V6 browser QA acceleration')
s = s.replace(old_started, new_started, 1)
needle = "await waitEval(cdp,`window.__rkrGame.qaEvents.some(e=>e.type==='bot-order-taken')`,9000);"
diag = "await sleep(1800);const waiterDiag=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.parties[0];return{party:{state:p?.state,claim:p?.orderClaim,table:p?.table?.id+1,pos:p?.table?.pos&&{x:p.table.pos.x,z:p.table.pos.z}},bots:g.players.filter(x=>!x.human).map(x=>({i:x.index,role:x.role,pos:{x:+x.group.position.x.toFixed(2),z:+x.group.position.z.toFixed(2)},task:x.bot?.task?.kind||null,action:x.bot?.task?.actions?.[x.bot?.actionIndex]?.kind||null})),events:g.qaEvents.map(e=>e.type)};})()`);console.log('V6 waiter diagnostic:',JSON.stringify(waiterDiag));\nawait waitEval(cdp,`window.__rkrGame.qaEvents.some(e=>e.type==='bot-order-taken')`,25000);"
if needle not in s: raise SystemExit('Could not add V6 waiter QA diagnostic')
s = s.replace(needle, diag, 1)

order_assert = "if(orderTaken.state!=='waiting'||!String(orderTaken.by).startsWith('BOT'))throw new Error(`Bot waiter did not take order: ${JSON.stringify(orderTaken)}`);"
salad_diag = order_assert + "\nawait sleep(15000);const saladDiag=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.parties[0];return{party:{state:p?.state,orders:p?.orders?.map(o=>({recipe:o.recipeId,claim:o.claimedBy}))},bots:g.players.filter(x=>!x.human).map(x=>({i:x.index,role:x.role,pos:{x:+x.group.position.x.toFixed(2),z:+x.group.position.z.toFixed(2)},held:x.held?.description?.()||null,task:x.bot?.task?.kind||null,recipe:x.bot?.task?.recipeId||null,actionIndex:x.bot?.actionIndex||0,action:x.bot?.task?.actions?.[x.bot?.actionIndex]?.kind||null,process:x.bot?.processStation?.type||null})),stations:g.stations.filter(x=>x.type!=='storage').map(x=>({type:x.type,pos:{x:x.pos.x,z:x.pos.z},reserved:x.reservedBy||null,slot:x.slot?.description?.()||null,state:x.slot?.state||null,progress:+(x.progress||0).toFixed(2),cook:+(x.cook||0).toFixed(2),ready:!!x.ready})),events:g.qaEvents.map(e=>({type:e.type,ingredient:e.ingredient||null,recipe:e.recipe||null,station:e.station||null}))};})()`);console.log('V6 salad-chain diagnostic:',JSON.stringify(saladDiag));"
if order_assert not in s: raise SystemExit('Could not add V6 salad-chain diagnostic')
s = s.replace(order_assert, salad_diag, 1)
s = s.replace("e.recipe==='salad')`,26000,150", "e.recipe==='salad')`,75000,150")
s = s.replace("e.type==='bot-order-taken')`,9000);", "e.type==='bot-order-taken')`,25000);")
s = s.replace("e.recipe==='burger')`,28000,150", "e.recipe==='burger')`,90000,150")
s = s.replace("e.type==='bot-clean-cycle')`,15000,150", "e.type==='bot-clean-cycle')`,60000,150")
smoke.write_text(s, encoding='utf-8')

print(f'Applied Robledo Kitchen Rush Autonomous Service V6 ({len(archive)} bytes, sha256={digest}).')
