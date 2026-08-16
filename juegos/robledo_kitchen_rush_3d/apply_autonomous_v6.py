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

# Transport normalization: V6 has one Grocery Market + Freezer fixture, not legacy crates.
text = text.replace("kitchen'1", 'grocery:1')

# Service Captain gets strict first refusal on waiter work when one is autonomous.
old = "chooseTask(){const g=this.game,m=this.member,role=ROLE_META[m.role];const ready=g.parties.filter(p=>p.state==='readyToOrder'&&!p.orderClaim).sort((a,b)=>b.orderWaitElapsed-a.orderWaitElapsed);if(ready.length&&(role.botBias==='service'||ready[0].orderWaitElapsed>3)){"
new = "chooseTask(){const g=this.game,m=this.member,role=ROLE_META[m.role],hasServiceBot=g.players.some(p=>!p.human&&ROLE_META[p.role]?.botBias==='service');const ready=g.parties.filter(p=>p.state==='readyToOrder'&&!p.orderClaim).sort((a,b)=>b.orderWaitElapsed-a.orderWaitElapsed);if(ready.length&&(role.botBias==='service'||(!hasServiceBot&&ready[0].orderWaitElapsed>3))){"
if old not in text:
    raise SystemExit('Could not apply V6 waiter-priority correction')
text = text.replace(old, new, 1)
old_fallback = "if(ready.length){const party=ready[0];party.orderClaim=this.id;this.task={kind:'order',party,table:party.table,actions:[{kind:'takeOrder',table:party.table,duration:.8}]};this.record('bot-order-claim',{table:party.table.id+1});}"
new_fallback = "if(ready.length&&(role.botBias==='service'||!hasServiceBot)){const party=ready[0];party.orderClaim=this.id;this.task={kind:'order',party,table:party.table,actions:[{kind:'takeOrder',table:party.table,duration:.8}]};this.record('bot-order-claim',{table:party.table.id+1});}"
if old_fallback not in text:
    raise SystemExit('Could not apply V6 waiter-priority fallback correction')
text = text.replace(old_fallback, new_fallback, 1)

# Physical-navigation correction: bots approach a reachable service point outside each fixture
# AABB instead of trying to walk through the table/station center. Interactions still target the
# actual fixture and therefore execute the exact same state machine as a human interaction.
old_near = "  near(target,dt){const m=this.member,g=this.game,pos=target?.pos||target?.group?.position;if(!pos)return false;const v=new THREE.Vector3(pos.x-m.group.position.x,0,pos.z-m.group.position.z),d=v.length(),stop=target.type==='table'?1.46:target.type==='storage'?.92:1.18;if(d>stop){v.normalize();m.facing.copy(v);m.group.rotation.y=Math.atan2(v.x,v.z);const before=m.group.position.clone();g.moveCrew(m,v.clone().multiplyScalar(m.speed*.9*dt));if(before.distanceToSquared(m.group.position)<1e-7){const side=new THREE.Vector3(-v.z,0,v.x).multiplyScalar(this.avoidSign);g.moveCrew(m,side.multiplyScalar(m.speed*.72*dt));if(before.distanceToSquared(m.group.position)<1e-7){this.avoidSign*=-1;}}m.animate(dt,true,.95);return false;}m.animate(dt,false);return true;}"
new_near = "  approachPoint(target){const m=this.member,g=this.game,pos=target?.pos||target?.group?.position;if(!pos||target.type==='storage')return pos;const o=g.obstacles.find(x=>x.type===target.type&&Math.abs(x.x-pos.x)<.08&&Math.abs(x.z-pos.z)<.08);if(!o)return pos;const pad=m.radius+.18,candidates=[new THREE.Vector3(o.x,0,o.z-o.d/2-pad),new THREE.Vector3(o.x+o.w/2+pad,0,o.z),new THREE.Vector3(o.x,0,o.z+o.d/2+pad),new THREE.Vector3(o.x-o.w/2-pad,0,o.z)];const valid=candidates.filter(p=>!g.blocked(m,p));const pool=valid.length?valid:candidates;pool.sort((a,b)=>a.distanceToSquared(m.group.position)-b.distanceToSquared(m.group.position));return pool[0];}\n  near(target,dt){const m=this.member,g=this.game,raw=target?.pos||target?.group?.position;if(!raw)return false;const pos=this.approachPoint(target)||raw,v=new THREE.Vector3(pos.x-m.group.position.x,0,pos.z-m.group.position.z),d=v.length(),stop=target.type==='storage'?.72:.24;if(d>stop){v.normalize();m.facing.copy(v);m.group.rotation.y=Math.atan2(v.x,v.z);const before=m.group.position.clone();g.moveCrew(m,v.clone().multiplyScalar(m.speed*.9*dt));if(before.distanceToSquared(m.group.position)<1e-7){const side=new THREE.Vector3(-v.z,0,v.x).multiplyScalar(this.avoidSign);g.moveCrew(m,side.multiplyScalar(m.speed*.72*dt));if(before.distanceToSquared(m.group.position)<1e-7)this.avoidSign*=-1;}m.animate(dt,true,.95);return false;}m.animate(dt,false);return true;}"
if old_near not in text:
    raise SystemExit('Could not apply V6 collision-aware navigation correction')
text = text.replace(old_near, new_near, 1)

# Refactor the gameplay update into a deterministic fixed-step entry point. Normal gameplay uses
# exactly the same method from requestAnimationFrame. CI can temporarily disable RAF-driven logic
# and call stepPlaying(0.05), which validates real game time/state transitions without depending on
# hosted software-WebGL frame rate.
old_loop = "  loop(ts){const dt=Math.min(.04,Math.max(.001,(ts-this.lastTs)/1000));this.lastTs=ts;if(this.state==='playing'){for(const p of this.players)p.update(dt);this.updateStations(dt);this.updateThrown(dt);for(const p of this.parties)p.update(dt);this.parties=this.parties.filter(p=>p.state!=='gone');this.spawnTimer-=dt;if(this.spawnTimer<=0){this.spawnParty();const tierFactor=1+this.business.expansionTier*.05;this.spawnTimer=LEVELS[this.levelIndex].spawnEvery/tierFactor*(.9+Math.random()*.32);}this.timeLeft-=dt;if(this.timeLeft<=0)this.endLevel(false);this.updateUI();const p1=this.players.find(p=>p.human);if(p1){const n=this.nearestInteractable(p1.group.position,1.55);if(n){this.ui.hint.textContent=`P${p1.index+1} • ${n.type==='table'?`TABLE ${n.id+1}${n.party?.state==='readyToOrder'?' • TAKE ORDER':''}`:n.type==='storage'?`${INGREDIENT_META[n.kind]?.name||n.kind} • GROCERY MARKET`:n instanceof WorldItem?n.description().toUpperCase():(FIXTURES[n.type]?.label||n.type).toUpperCase()} • INTERACT`;this.ui.hint.classList.remove('hidden');}else this.ui.hint.classList.add('hidden');}}\n    if(this.state==='build')this.updateBuildHoverHint();if(this.messageTimer>0){this.messageTimer-=dt;if(this.messageTimer<=0)this.ui.message.classList.add('hidden');}this.cameraRig.update(dt);this.renderer.render(this.scene,this.camera);requestAnimationFrame(t=>this.loop(t));}"
new_loop = "  stepPlaying(dt){for(const p of this.players)p.update(dt);this.updateStations(dt);this.updateThrown(dt);for(const p of this.parties)p.update(dt);this.parties=this.parties.filter(p=>p.state!=='gone');this.spawnTimer-=dt;if(this.spawnTimer<=0){this.spawnParty();const tierFactor=1+this.business.expansionTier*.05;this.spawnTimer=LEVELS[this.levelIndex].spawnEvery/tierFactor*(.9+Math.random()*.32);}this.timeLeft-=dt;if(this.timeLeft<=0)this.endLevel(false);this.updateUI();const p1=this.players.find(p=>p.human);if(p1){const n=this.nearestInteractable(p1.group.position,1.55);if(n){this.ui.hint.textContent=`P${p1.index+1} • ${n.type==='table'?`TABLE ${n.id+1}${n.party?.state==='readyToOrder'?' • TAKE ORDER':''}`:n.type==='storage'?`${INGREDIENT_META[n.kind]?.name||n.kind} • GROCERY MARKET`:n instanceof WorldItem?n.description().toUpperCase():(FIXTURES[n.type]?.label||n.type).toUpperCase()} • INTERACT`;this.ui.hint.classList.remove('hidden');}else this.ui.hint.classList.add('hidden');}}}\n  loop(ts){const dt=Math.min(.04,Math.max(.001,(ts-this.lastTs)/1000));this.lastTs=ts;if(this.state==='playing'&&!this.qaManualClock)this.stepPlaying(dt);if(this.state==='build')this.updateBuildHoverHint();if(this.messageTimer>0){this.messageTimer-=dt;if(this.messageTimer<=0)this.ui.message.classList.add('hidden');}this.cameraRig.update(dt);this.renderer.render(this.scene,this.camera);requestAnimationFrame(t=>this.loop(t));}"
if old_loop not in text:
    raise SystemExit('Could not refactor V6 loop into deterministic stepPlaying')
text = text.replace(old_loop, new_loop, 1)
game_js.write_text(text, encoding='utf-8')

# Professional browser QA. This opens the actual WebGL build, drives the UI, then switches only
# the gameplay clock to deterministic fixed 50 ms steps. No bot action is mocked or teleported:
# movement, collision, grocery pickup, prep, cooking, assembly, waiter delivery, sink washing and
# customer state transitions all execute through production code.
smoke = ROOT / 'juegos/robledo_kitchen_rush_3d/scripts/smoke.mjs'
smoke.write_text(r'''const port = Number(process.env.CDP_PORT || 9333);
const endpoint = `http://127.0.0.1:${port}/json`;
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function waitForPage(){for(let i=0;i<600;i++){try{const pages=await fetch(endpoint).then(r=>r.json());const page=pages.find(p=>p.type==='page'&&p.url.includes('127.0.0.1'));if(page)return page;}catch{}await sleep(100);}throw new Error('Chrome DevTools page did not become available');}
class CDP{constructor(url){this.ws=new WebSocket(url);this.next=1;this.pending=new Map();this.exceptions=[];this.consoleErrors=[];this.ws.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id&&this.pending.has(msg.id)){const{resolve,reject}=this.pending.get(msg.id);this.pending.delete(msg.id);msg.error?reject(new Error(JSON.stringify(msg.error))):resolve(msg.result);}else if(msg.method==='Runtime.exceptionThrown')this.exceptions.push(msg.params?.exceptionDetails?.exception?.description||msg.params?.exceptionDetails?.text||'Runtime exception');else if(msg.method==='Runtime.consoleAPICalled'&&msg.params?.type==='error')this.consoleErrors.push((msg.params.args||[]).map(x=>x.value??x.description??'').join(' '));};}async open(){if(this.ws.readyState!==WebSocket.OPEN)await new Promise((resolve,reject)=>{this.ws.onopen=resolve;this.ws.onerror=reject;});}send(method,params={}){const id=this.next++;return new Promise((resolve,reject)=>{this.pending.set(id,{resolve,reject});this.ws.send(JSON.stringify({id,method,params}));});}async eval(expression){const result=await this.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text||'Evaluation failed');return result.result?.value;}}
async function waitEval(cdp, expression, timeout=12000, step=120){const until=Date.now()+timeout;let last;while(Date.now()<until){last=await cdp.eval(expression);if(last)return last;await sleep(step);}throw new Error(`Timed out waiting for: ${expression}; last=${JSON.stringify(last)}`);}
async function advance(cdp, seconds){const total=Math.ceil(seconds/.05);for(let done=0;done<total;done+=20){const n=Math.min(20,total-done);await cdp.eval(`(()=>{const g=window.__rkrGame;for(let i=0;i<${n};i++)g.stepPlaying(.05);return true;})()`);}}
async function advanceUntil(cdp, expression, maxSeconds=60){for(let t=0;t<maxSeconds;t+=1){await advance(cdp,1);if(await cdp.eval(expression))return t+1;}const snap=await cdp.eval(`(()=>{const g=window.__rkrGame;return{state:g.state,lives:g.lives,time:g.timeLeft,parties:g.parties.map(p=>({state:p.state,claim:p.orderClaim,taken:p.orderTakenBy,orders:p.orders.map(o=>({r:o.recipeId,c:o.claimedBy})),table:p.table?.id+1})),bots:g.players.filter(p=>!p.human).map(p=>({i:p.index,role:p.role,pos:{x:+p.group.position.x.toFixed(2),z:+p.group.position.z.toFixed(2)},held:p.held?.description?.()||null,task:p.bot?.task?.kind||null,recipe:p.bot?.task?.recipeId||null,action:p.bot?.task?.actions?.[p.bot?.actionIndex]?.kind||null,actionIndex:p.bot?.actionIndex||0,process:p.bot?.processStation?.type||null})),stations:g.stations.filter(s=>s.type!=='storage').map(s=>({type:s.type,pos:{x:s.pos.x,z:s.pos.z},reserved:s.reservedBy||null,slot:s.slot?.description?.()||null,state:s.slot?.state||null,progress:+(s.progress||0).toFixed(2),cook:+(s.cook||0).toFixed(2),ready:!!s.ready})),events:g.qaEvents.slice(-40)};})()`);throw new Error(`Simulated ${maxSeconds}s without satisfying ${expression}; snapshot=${JSON.stringify(snap)}`);}

const page=await waitForPage();const cdp=new CDP(page.webSocketDebuggerUrl);await cdp.open();await cdp.send('Runtime.enable');await cdp.send('Page.enable');
await waitEval(cdp,`document.readyState==='complete'&&!!document.getElementById('start-btn')&&!!window.__rkrGame`,20000);
await cdp.eval(`localStorage.clear();location.reload();true`);await sleep(350);await waitEval(cdp,`document.readyState==='complete'&&!!window.__rkrGame`,20000);

const preflight=await cdp.eval(`(()=>{const canvas=document.getElementById('game-canvas'),g=window.__rkrGame;return{title:document.title,start:!!document.getElementById('start-btn'),webgl:!!(canvas&&(canvas.getContext('webgl2')||canvas.getContext('webgl'))),tier:g.business.expansionTier,bounds:g.currentBounds().xMax,cash:g.business.cash,sat:g.business.satisfaction,tableCap:g.tier().tableCap,customerCap:g.tier().customerCap,menuSlots:g.tier().menuSlots};})()`);
if(!preflight.start||!preflight.webgl||preflight.tier!==0||preflight.bounds>8||preflight.tableCap!==2||preflight.customerCap!==2||preflight.menuSlots!==2)throw new Error(`V6 progressive preflight failed: ${JSON.stringify(preflight)}`);

await cdp.eval(`document.getElementById('start-btn').click()`);await sleep(250);
const crew=await cdp.eval(`(()=>({visible:getComputedStyle(document.getElementById('crew-screen')).display!=='none',slots:document.querySelectorAll('#crew-slots .crew-slot').length,bots:document.querySelectorAll('#crew-slots .crew-slot.bot').length,activeMenu:document.querySelectorAll('#menu-toggle-grid .menu-toggle.active').length,lockedMenu:document.querySelectorAll('#menu-toggle-grid .menu-toggle.locked').length,business:document.getElementById('business-preview').textContent}))()`);
if(!crew.visible||crew.slots!==3||crew.bots!==2||crew.activeMenu!==2||crew.lockedMenu<4)throw new Error(`V6 starter crew/menu failed: ${JSON.stringify(crew)}`);

await cdp.eval(`document.getElementById('crew-continue-btn').click()`);await sleep(150);await waitEval(cdp,`getComputedStyle(document.getElementById('tutorial-screen')).display!=='none'`,5000);await cdp.eval(`document.getElementById('tutorial-skip-btn').click()`);await sleep(250);
const buildInitial=await cdp.eval(`(()=>({visible:getComputedStyle(document.getElementById('build-ui')).display!=='none',cash:document.getElementById('build-budget').textContent,tier:document.getElementById('business-tier-name').textContent,capacity:document.getElementById('capacity-summary').textContent,openDisabled:document.getElementById('open-restaurant-btn').disabled,groceryButtons:[...document.querySelectorAll('#fixture-palette .fixture-btn')].filter(x=>x.textContent.includes('Grocery Market')).length,legacyCrates:[...document.querySelectorAll('#fixture-palette .fixture-btn')].filter(x=>/Tomato Crate|Lettuce Crate|Meat Crate|Bun Crate/.test(x.textContent)).length}))()`);
if(!buildInitial.visible||!buildInitial.openDisabled||buildInitial.groceryButtons!==1||buildInitial.legacyCrates!==0)throw new Error(`V6 grocery build palette failed: ${JSON.stringify(buildInitial)}`);

await cdp.eval(`document.getElementById('auto-layout-btn').click()`);await sleep(250);
const built=await cdp.eval(`(()=>{const g=window.__rkrGame;return{openDisabled:document.getElementById('open-restaurant-btn').disabled,req:[...document.querySelectorAll('#build-requirements .req')].map(x=>x.className),tables:g.plan.filter(x=>x.key==='table').length,grocery:g.plan.filter(x=>x.key==='grocery').length,legacy:g.plan.filter(x=>['tomato','lettuce','meat','potato','bun','cheese','dough'].includes(x.key)).length,cash:g.business.cash};})()`);
if(built.openDisabled||built.req.some(x=>!x.includes('ok'))||built.tables!==2||built.grocery!==1||built.legacy!==0||built.cash>=preflight.cash)throw new Error(`V6 recommended layout failed: ${JSON.stringify(built)}`);

await cdp.eval(`document.getElementById('open-restaurant-btn').click()`);await sleep(600);
const started=await cdp.eval(`(()=>{const g=window.__rkrGame;g.qaManualClock=true;g.spawnTimer=9999;g.timeLeft=9999;return{hud:getComputedStyle(document.getElementById('hud')).display!=='none',crew:g.players.length,bots:g.players.filter(p=>!p.human).length,roles:g.players.map(p=>p.role),storage:g.stations.filter(s=>s.type==='storage').map(s=>s.kind).sort(),timer:document.getElementById('timer').textContent};})()`);
for(const k of ['bun','lettuce','meat','tomato'])if(!started.storage.includes(k))throw new Error(`Grocery wall missing logical compartment ${k}: ${JSON.stringify(started)}`);
if(!started.hud||started.crew!==3||started.bots!==2||started.storage.length!==4||!started.roles.includes('service'))throw new Error(`V6 service start failed: ${JSON.stringify(started)}`);

// Scenario A — actual waiter + grocery + prep + plate/counter + table delivery.
const saladSeed=await cdp.eval(`(()=>{const g=window.__rkrGame;g.lives=2;g.spawnParty();const p=g.parties[0];p.state='readyToOrder';p.browse=0;p.orderWaitElapsed=4;p.waitElapsed=0;p.patience=120;p.patienceMax=120;p.orders=[{id:'qa-salad',recipeId:'salad',claimedBy:null}];p.originalRecipes=['salad'];p.size=1;p.orderClaim=null;p.orderTakenBy=null;p.customers.forEach((c,i)=>{c.group.position.copy(p.table.seats[i]);c.group.position.y=-.08;});g.qaEvents=[];return{table:p.table.id+1,state:p.state,lives:g.lives};})()`);
await advanceUntil(cdp,`window.__rkrGame.qaEvents.some(e=>e.type==='bot-order-taken')`,20);
const orderTaken=await cdp.eval(`(()=>{const g=window.__rkrGame,p=g.parties[0];return{state:p.state,by:p.orderTakenBy,events:g.qaEvents.filter(e=>e.type.includes('order')).map(e=>e.type)};})()`);
if(orderTaken.state!=='waiting'||!String(orderTaken.by).startsWith('BOT'))throw new Error(`Bot waiter did not take order: ${JSON.stringify(orderTaken)}`);
await advanceUntil(cdp,`window.__rkrGame.qaEvents.some(e=>e.type==='bot-dish-served'&&e.recipe==='salad')`,55);
const salad=await cdp.eval(`(()=>{const g=window.__rkrGame;return{storage:g.qaEvents.filter(e=>e.type==='bot-storage-pick').map(e=>e.ingredient),prep:g.qaEvents.filter(e=>e.type==='bot-prep-complete').map(e=>e.ingredient),assembled:g.qaEvents.filter(e=>e.type==='bot-assemble').map(e=>e.ingredient),served:g.qaEvents.filter(e=>e.type==='bot-dish-served').map(e=>e.recipe),lives:g.lives,successful:g.successfulTables,cash:g.business.cash,sat:g.business.satisfaction,aborts:g.qaEvents.filter(e=>e.type==='bot-task-abort')};})()`);
for(const k of ['tomato','lettuce'])if(!salad.storage.includes(k)||!salad.prep.includes(k)||!salad.assembled.includes(k))throw new Error(`Real salad chain incomplete for ${k}: ${JSON.stringify(salad)}`);
if(!salad.served.includes('salad')||salad.successful<1||salad.lives!==3||salad.aborts.length)throw new Error(`Bot salad delivery / fast-life failed: ${JSON.stringify(salad)}`);

// Scenario B — real meat/bun storage + actual stove state transitions + physical delivery.
await cdp.eval(`(()=>{const g=window.__rkrGame;const marker=g.qaEvents.length;g.spawnParty();const p=g.parties[g.parties.length-1];p.state='readyToOrder';p.browse=0;p.orderWaitElapsed=4;p.waitElapsed=0;p.patience=160;p.patienceMax=160;p.orders=[{id:'qa-burger',recipeId:'burger',claimedBy:null}];p.originalRecipes=['burger'];p.size=1;p.orderClaim=null;p.orderTakenBy=null;p.customers.forEach((c,i)=>{c.group.position.copy(p.table.seats[i]);c.group.position.y=-.08;});g.__qaMarker=marker;return true;})()`);
await advanceUntil(cdp,`window.__rkrGame.qaEvents.slice(window.__rkrGame.__qaMarker).some(e=>e.type==='bot-order-taken')`,20);
await advanceUntil(cdp,`window.__rkrGame.qaEvents.slice(window.__rkrGame.__qaMarker).some(e=>e.type==='bot-dish-served'&&e.recipe==='burger')`,80);
const burger=await cdp.eval(`(()=>{const g=window.__rkrGame,e=g.qaEvents.slice(g.__qaMarker);return{cookStart:e.filter(x=>x.type==='bot-cook-start').map(x=>x.station),cookReady:e.filter(x=>x.type==='bot-cook-ready').map(x=>x.station),storage:e.filter(x=>x.type==='bot-storage-pick').map(x=>x.ingredient),assembled:e.filter(x=>x.type==='bot-assemble').map(x=>x.ingredient),served:e.filter(x=>x.type==='bot-dish-served').map(x=>x.recipe),aborts:e.filter(x=>x.type==='bot-task-abort')};})()`);
if(!burger.cookStart.includes('stove')||!burger.cookReady.includes('stove')||!burger.storage.includes('meat')||!burger.storage.includes('bun')||!burger.assembled.includes('meat')||!burger.served.includes('burger')||burger.aborts.length)throw new Error(`Real burger/stove bot chain failed: ${JSON.stringify(burger)}`);

// Scenario C — actual dirty plate -> sink -> clean rack cycle.
await cdp.eval(`(()=>{const g=window.__rkrGame;for(const p of g.parties){for(const c of p.customers)c.group.removeFromParent();p.table.party=null;}g.parties=[];for(const p of g.players.filter(x=>!x.human))p.bot.abort('qa reset before cleaning');for(const p of g.players.filter(x=>!x.human)){if(p.held){p.held.group.removeFromParent();p.held=null;}}g.tables[0].dirty=1;g.tables[0].cleanClaim=null;g.__qaCleanMarker=g.qaEvents.length;return true;})()`);
await advanceUntil(cdp,`window.__rkrGame.qaEvents.slice(window.__rkrGame.__qaCleanMarker).some(e=>e.type==='bot-clean-cycle')`,45);
const cleaning=await cdp.eval(`(()=>{const g=window.__rkrGame,e=g.qaEvents.slice(g.__qaCleanMarker);return{dirty:g.tables[0].dirty,events:e.map(x=>x.type),sinkDirty:g.stations.filter(s=>s.type==='sink').some(s=>s.slot?.dirty),held:g.players.filter(p=>!p.human).map(p=>p.held?.description?.()||null)};})()`);
if(cleaning.dirty!==0||cleaning.sinkDirty||!cleaning.events.includes('bot-dirty-pick')||!cleaning.events.includes('bot-wash-complete')||!cleaning.events.includes('bot-clean-cycle'))throw new Error(`Physical bot cleaning chain failed: ${JSON.stringify(cleaning)}`);

if(cdp.exceptions.length)throw new Error(`Runtime exceptions detected: ${cdp.exceptions.join(' | ')}`);
if(cdp.consoleErrors.length)throw new Error(`Console errors detected: ${cdp.consoleErrors.join(' | ')}`);
console.log('Autonomous Service V6 deterministic browser E2E passed:',JSON.stringify({preflight,crew,buildInitial,built,started,saladSeed,orderTaken,salad,burger,cleaning}));
cdp.ws.close();
''', encoding='utf-8')

print(f'Applied Robledo Kitchen Rush Autonomous Service V6 ({len(archive)} bytes, sha256={digest}).')
