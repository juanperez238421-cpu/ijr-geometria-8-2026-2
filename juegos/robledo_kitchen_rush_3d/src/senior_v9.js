import * as THREE from 'three';
import './senior_v8.js';

const game = window.__rkrGame;
const v8 = game?.__seniorV8;
if (!game || !v8) throw new Error('Senior V9 requires the stable Senior V8 systems layer.');
if (game.__seniorV9) throw new Error('Senior V9 loaded twice.');

const VERSION = '9.0.0';
const INTERACT_RANGE = 2.02;
const SELECT_RANGE = 5.0;
const WORK_TIME = { prep: 1.7, sink: 1.8 };
const state = {
  moveTarget: null,
  task: null,
  hover: null,
  selected: null,
  lastPointer: { x: 0, y: 0 },
  statusText: 'LEFT CLICK TO MOVE OR USE A STATION',
  uiTick: 0,
};

const clamp = (v,a,b) => Math.max(a,Math.min(b,v));
const dist = (a,b) => Math.hypot(a.x-b.x,a.z-b.z);
const pointOf = target => target?.pos || target?.group?.position || null;
const carried = () => new Set(game.players.map(p=>p.held).filter(Boolean));
const validTarget = target => !!target && !target.dead && (target.type==='table' ? game.tables.includes(target) : game.stations.includes(target) || game.items.includes(target) || !!target.group?.parent);

function targetName(target){
  if(!target)return 'Floor';
  if(target.type==='storage')return `${String(target.kind||'ingredient').replace(/^./,c=>c.toUpperCase())} grocery`;
  if(target.type==='table')return `Table ${target.id+1}`;
  if(typeof target.description==='function')return target.description();
  return String(target.type||target.kind||'object').replace(/\b\w/g,c=>c.toUpperCase());
}

function predictedAction(player,target){
  if(!target)return 'Move';
  if(target.type==='storage')return player.held?'Hands full':'Pick ingredient';
  if(target.type==='plate')return player.held?.isPlate?'Return clean plate':player.held?'Hands full':'Take clean plate';
  if(target.type==='trash')return player.held?'Discard held item':'Trash empty';
  if(target.type==='prep'){
    if(target.slot?.state==='raw')return 'Prep automatically';
    if(target.slot)return player.held?'Station occupied':'Collect prepared ingredient';
    return player.held&&!player.held.isPlate?'Place ingredient and prep':'Prep board';
  }
  if(target.type==='sink'){
    if(target.slot?.dirty)return 'Wash automatically';
    if(target.slot)return player.held?'Sink occupied':'Collect clean plate';
    return player.held?.isPlate&&player.held.dirty?'Place plate and wash':'Sink';
  }
  if(['stove','fryer','oven'].includes(target.type)){
    if(target.slot)return player.held?(target.ready?'Ready item waiting':'Station occupied'):(target.ready?'Collect ready food':'Check cooking food');
    return player.held?`Place on ${target.type}`:`${target.type} empty`;
  }
  if(target.type==='counter')return target.slot?(player.held?'Combine / assemble':'Pick up'):(player.held?'Place on counter':'Counter empty');
  if(target.type==='table'){
    if(target.party?.state==='readyToOrder')return 'Take customer order';
    if(target.party?.state==='waiting')return player.held?.isPlate?'Serve dish':'Dish needed';
    if(!target.party&&target.dirty>0)return player.held?'Hands full':'Clear dirty plate';
    return 'Table';
  }
  if(game.items.includes(target))return player.held?'Hands full':'Pick up';
  return 'Interact';
}

function installStyles(){
  if(document.getElementById('v9-style'))return;
  const style=document.createElement('style');style.id='v9-style';style.textContent=`
    #v9-input-layer{position:absolute;inset:0;z-index:7;pointer-events:none;cursor:default;background:transparent;touch-action:none}
    #v9-input-layer.active{pointer-events:auto}
    #v9-interaction-panel{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:55;width:min(620px,calc(100vw - 34px));padding:11px 14px;border-radius:15px;background:rgba(25,39,45,.93);color:#fff;box-shadow:0 14px 36px rgba(0,0,0,.24);pointer-events:none;backdrop-filter:blur(10px);font:700 12px/1.35 system-ui}
    #v9-interaction-panel.hidden{display:none}#v9-interaction-panel .v9-main{display:flex;justify-content:space-between;align-items:center;gap:14px}.v9-target{font-weight:900;letter-spacing:.02em}.v9-action{color:#f6d76f;text-align:right}.v9-sub{margin-top:5px;font-size:10px;opacity:.74}.v9-progress{height:6px;margin-top:8px;border-radius:999px;background:rgba(255,255,255,.12);overflow:hidden}.v9-progress i{display:block;height:100%;width:0;background:#f2bd3f;border-radius:999px;transition:width .08s linear}
    #v9-crosshair{position:fixed;z-index:54;width:14px;height:14px;border:2px solid rgba(255,255,255,.9);border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;display:none;box-shadow:0 0 0 2px rgba(31,48,55,.35)}
    #v9-station-strip{margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,.12);display:flex;flex-wrap:wrap;gap:5px}.v9-station-chip{font-size:9px;padding:4px 6px;border-radius:8px;background:rgba(255,255,255,.07)}.v9-station-chip.ready{background:rgba(77,154,103,.32)}.v9-station-chip.risk{background:rgba(227,79,81,.30)}.v9-station-chip.work{background:rgba(242,189,63,.23)}
    #v8-action-card{display:none!important}
    #interaction-hint{display:none!important}
  `;document.head.appendChild(style);
}
installStyles();

function installInputSurface(){
  let shell=document.getElementById('game-shell')||game.canvas.parentElement;if(getComputedStyle(shell).position==='static')shell.style.position='relative';
  let layer=document.getElementById('v9-input-layer');if(!layer){layer=document.createElement('div');layer.id='v9-input-layer';shell.appendChild(layer);}
  game.canvas.style.pointerEvents='none';
  let panel=document.getElementById('v9-interaction-panel');if(!panel){panel=document.createElement('div');panel.id='v9-interaction-panel';panel.className='hidden';document.body.appendChild(panel);}
  let cross=document.getElementById('v9-crosshair');if(!cross){cross=document.createElement('div');cross.id='v9-crosshair';document.body.appendChild(cross);}
  return {layer,panel,cross};
}
const ui=installInputSurface();

function pointerNdc(event){const r=game.canvas.getBoundingClientRect();return new THREE.Vector2(((event.clientX-r.left)/r.width)*2-1,-(((event.clientY-r.top)/r.height)*2-1));}
function floorPoint(event){game.raycaster.setFromCamera(pointerNdc(event),game.camera);const p=new THREE.Vector3();return game.raycaster.ray.intersectPlane(game.floorPlane,p)?p:null;}
function belongsTo(object,group){for(let n=object;n;n=n.parent)if(n===group)return true;return false;}

function projectedTarget(event,player){
  const r=game.canvas.getBoundingClientRect(),candidates=[];
  for(const s of game.stations)candidates.push({target:s,pos:s.pos,y:s.type==='storage'?1.05:1.0,max:s.type==='storage'?78:60,priority:s.type==='storage'?0:1});
  for(const t of game.tables)candidates.push({target:t,pos:t.pos,y:.82,max:72,priority:2});
  for(const item of game.items){if(item===player.held||item.dead||item.airborne||item.onSurface)continue;candidates.push({target:item,pos:item.group.position,y:item.group.position.y,max:48,priority:3});}
  let best=null,bestD=Infinity,bestPriority=99;
  for(const c of candidates){const v=new THREE.Vector3(c.pos.x,c.y,c.pos.z).project(game.camera);if(v.z<-1||v.z>1)continue;const sx=r.left+(v.x+1)*r.width/2,sy=r.top+(1-v.y)*r.height/2,d=Math.hypot(event.clientX-sx,event.clientY-sy);if(d<c.max&&(d<bestD-1||(Math.abs(d-bestD)<=1&&c.priority<bestPriority))){best=c.target;bestD=d;bestPriority=c.priority;}}
  return best;
}
function rayTarget(event,player){
  game.raycaster.setFromCamera(pointerNdc(event),game.camera);const roots=[...game.fixtureRoot.children,...game.itemRoot.children],hits=game.raycaster.intersectObjects(roots,true);
  for(const hit of hits){const item=game.items.find(i=>i!==player.held&&!i.dead&&belongsTo(hit.object,i.group));if(item)return item;const table=game.tables.find(t=>belongsTo(hit.object,t.group));if(table)return table;const stations=game.stations.filter(s=>belongsTo(hit.object,s.group));if(stations.length){stations.sort((a,b)=>hit.point.distanceToSquared(a.pos)-hit.point.distanceToSquared(b.pos));return stations[0];}}
  return null;
}
function resolveTarget(event,player){return projectedTarget(event,player)||rayTarget(event,player);}

function interactionPoint(player,target){
  const center=pointOf(target);if(!center)return null;const radius=target.type==='table'?1.68:target.type==='storage'?1.28:1.46,candidates=[];
  for(let i=0;i<20;i++){const a=i*Math.PI/10,p=new THREE.Vector3(center.x+Math.cos(a)*radius,0,center.z+Math.sin(a)*radius);if(!game.blocked(player,p))candidates.push(p);}
  if(!candidates.length)return new THREE.Vector3(center.x,0,center.z);candidates.sort((a,b)=>a.distanceToSquared(player.group.position)-b.distanceToSquared(player.group.position));return candidates[0];
}
function steer(player,destination,dt){
  if(!destination)return false;const delta=destination.clone().sub(player.group.position);delta.y=0;if(delta.length()<.10)return false;delta.normalize();player.facing.copy(delta);player.group.rotation.y=Math.atan2(delta.x,delta.z);const step=player.speed*dt,before=player.group.position.clone();game.moveCrew(player,delta.clone().multiplyScalar(step));if(before.distanceToSquared(player.group.position)<1e-8){const side=new THREE.Vector3(-delta.z,0,delta.x);game.moveCrew(player,side.multiplyScalar(step*.82));if(before.distanceToSquared(player.group.position)<1e-8)game.moveCrew(player,new THREE.Vector3(delta.z,0,-delta.x).multiplyScalar(step*.82));}return before.distanceToSquared(player.group.position)>1e-8;
}

function clearSelection(){state.selected=null;if(game.__v9Ring)game.__v9Ring.visible=false;}
function selectTarget(target){
  state.selected=validTarget(target)?target:null;if(!state.selected){clearSelection();return;}
  if(!game.__v9Ring){game.__v9Ring=new THREE.Mesh(new THREE.RingGeometry(.48,.57,40),new THREE.MeshBasicMaterial({color:0xf2bd3f,transparent:true,opacity:.72,side:THREE.DoubleSide,depthTest:false}));game.__v9Ring.rotation.x=-Math.PI/2;game.__v9Ring.renderOrder=110;game.scene.add(game.__v9Ring);}
  const p=pointOf(state.selected);game.__v9Ring.position.set(p.x,.06,p.z);game.__v9Ring.visible=true;
}
function updateSelection(){if(!validTarget(state.selected)){clearSelection();return;}const p=pointOf(state.selected);if(p&&game.__v9Ring){game.__v9Ring.position.set(p.x,.06,p.z);game.__v9Ring.visible=true;}}

function cancelTask(reason='CANCELLED'){
  if(state.task)game.qaRecord('v9-task-cancel',{target:state.task.target?.type||state.task.target?.kind||null,reason});state.task=null;state.moveTarget=null;state.statusText=reason;
}
function queueTask(player,target){
  if(!validTarget(target))return;selectTarget(target);state.moveTarget=null;state.task={target,phase:'approach',destination:interactionPoint(player,target),started:performance.now(),progress:0,action:predictedAction(player,target)};state.statusText=`${targetName(target)} • ${state.task.action}`;game.qaRecord('v9-task-start',{target:target.type||target.kind,kind:target.kind||null,action:state.task.action});
}

function finishTask(player,target,result='DONE'){
  state.task=null;state.statusText=`${targetName(target)} • ${result}`;game.v8Shift.interactions=(Number(game.v8Shift.interactions)||0)+1;game.qaRecord('v9-task-complete',{target:target.type||target.kind,kind:target.kind||null,result,held:player.held?.description?.()||null});
}
function startOrAdvanceWork(player,target,dt){
  if(target.type==='prep'){
    if(!target.slot){game.interact(player,target,.018,true);if(!target.slot){finishTask(player,target,'NO VALID PREP ITEM');return;}}
    if(target.slot.state==='raw'){state.task.phase='work';game.interact(player,target,dt,true);state.task.progress=clamp((target.progress||0)/WORK_TIME.prep,0,1);return;}
    if(!player.held){game.interact(player,target,.018,true);finishTask(player,target,'PREP COMPLETE');return;}
    finishTask(player,target,'PREP COMPLETE');return;
  }
  if(target.type==='sink'){
    if(!target.slot){game.interact(player,target,.018,true);if(!target.slot){finishTask(player,target,'NO DIRTY PLATE');return;}}
    if(target.slot.dirty){state.task.phase='work';game.interact(player,target,dt,true);state.task.progress=clamp((target.progress||0)/WORK_TIME.sink,0,1);return;}
    if(!player.held){game.interact(player,target,.018,true);finishTask(player,target,'WASH COMPLETE');return;}
    finishTask(player,target,'WASH COMPLETE');return;
  }
}
function executeTask(player,dt){
  const task=state.task,target=task?.target;if(!task||!validTarget(target)){cancelTask('TARGET LOST');return;}
  if(target.type==='prep'||target.type==='sink'){startOrAdvanceWork(player,target,Math.max(.025,dt));return;}
  const before=player.held?.description?.()||null;game.interact(player,target,.018,true);const after=player.held?.description?.()||null;finishTask(player,target,before===after?'ACTION CHECKED':'ACTION COMPLETE');
}

function workPose(player,dt){
  const l=player.group.userData.limbs;if(!l)return;const working=state.task?.phase==='work';if(working){const t=performance.now()/1000;const swing=Math.sin(t*9)*.28;l.rightSleeve.rotation.x=-.55+swing;l.rightHand.rotation.x=-.55+swing;l.leftSleeve.rotation.x=-.35-swing*.6;l.leftHand.rotation.x=-.35-swing*.6;player.group.position.y=0;}else{for(const p of Object.values(l))p.rotation.x*=Math.max(0,1-dt*7);}}

function installPrimaryPlayer(player){
  if(!player?.human||player.index!==0)return;player.__v8SelectionRing?.removeFromParent();player.__v8SelectionRing=null;player.__v9Installed=true;
  player.pick=function pickV9(item){if(this.held||!item||item.dead)return false;this.held=item;item.onSurface=false;this.game.sfx.pickup();if(item.__v8Halo)item.__v8Halo.visible=false;this.game.qaRecord('v9-pick',{kind:item.kind||'plate',state:item.state||null});return true;};
  player.updateHuman=function updateHumanV9(dt){
    let moving=false;if(state.task&&validTarget(state.task.target)){const target=state.task.target,p=pointOf(target),d=p?dist(this.group.position,p):999;if(d>INTERACT_RANGE){state.task.phase='approach';state.task.destination=interactionPoint(this,target);moving=steer(this,state.task.destination,dt);}else executeTask(this,dt);}else if(state.moveTarget){if(dist(this.group.position,state.moveTarget)>.14)moving=steer(this,state.moveTarget,dt);else state.moveTarget=null;}
    this.animate(dt,moving,1);workPose(this,dt);if(this.held?.__v8Halo)this.held.__v8Halo.visible=false;
  };
}
const baseSpawnPlayers=game.spawnPlayers.bind(game);game.spawnPlayers=function spawnPlayersV9(){baseSpawnPlayers();installPrimaryPlayer(this.players[0]);this.qaRecord('v9-control-roster',{players:this.players.length,bots:this.players.filter(p=>!p.human).length});};

const baseSpawnItem=game.spawnItem.bind(game);game.spawnItem=function spawnItemV9(...args){const item=baseSpawnItem(...args);if(item?.__v8Halo)item.__v8Halo.visible=false;return item;};

function syncLayer(){ui.layer.classList.toggle('active',game.state==='playing');ui.panel.classList.toggle('hidden',game.state!=='playing');if(game.state!=='playing')ui.cross.style.display='none';}
function contextMenu(event){if(game.state==='playing'){event.preventDefault();event.stopPropagation();}}
ui.layer.addEventListener('contextmenu',contextMenu);
ui.layer.addEventListener('pointermove',event=>{
  state.lastPointer={x:event.clientX,y:event.clientY};if(game.state!=='playing')return;const p=game.players[0];state.hover=p?.human?resolveTarget(event,p):null;ui.cross.style.display=state.hover?'block':'none';ui.cross.style.left=`${event.clientX}px`;ui.cross.style.top=`${event.clientY}px`;ui.layer.style.cursor=state.hover?'pointer':'crosshair';
});
ui.layer.addEventListener('pointerleave',()=>{state.hover=null;ui.cross.style.display='none';});
ui.layer.addEventListener('pointerdown',event=>{
  if(game.state!=='playing')return;const p=game.players[0];if(!p?.human)return;
  if(event.button===0){const target=resolveTarget(event,p);if(target)queueTask(p,target);else{cancelTask('MOVE');clearSelection();const floor=floorPoint(event);if(floor){state.moveTarget=floor;state.statusText='Moving';game.qaRecord('v9-move-click',{x:floor.x,z:floor.z});}}}
  else if(event.button===2){cancelTask('ACTION CANCELLED');game.qaRecord('v9-right-cancel',{held:p.held?.description?.()||null});}
  else if(event.button===1){p.throwItem();state.statusText='Item thrown';game.qaRecord('v9-middle-throw',{held:p.held?.description?.()||null});}
  event.preventDefault();event.stopPropagation();
});
ui.layer.addEventListener('wheel',event=>{if(game.state!=='playing')return;game.cameraRig.distance=clamp(game.cameraRig.distance+event.deltaY*.012,16,34);event.preventDefault();},{passive:false});

window.addEventListener('keydown',event=>{
  if(game.state!=='playing')return;const p=game.players[0];if(!p?.human)return;
  if(event.code==='Space'||event.code==='KeyE'){const t=state.selected&&validTarget(state.selected)?state.selected:game.nearestInteractable(p.group.position,SELECT_RANGE);if(t)queueTask(p,t);event.preventDefault();}
  if(event.code==='Backspace'){cancelTask('ACTION CANCELLED');event.preventDefault();}
});

function serviceHint(player){
  const h=player?.held;if(!h)return 'Click a customer table for an order, or click a grocery ingredient to start a recipe.';
  if(h.isPlate){if(h.dirty)return 'Click the sink once. Washing runs automatically and returns the clean plate.';if(h.components?.length)return 'Continue assembly at the counter, bake if required, or click the matching table to serve.';return 'Take prepared ingredients to a counter and combine them with this plate.';}
  if(h.kind==='meat'&&h.state==='raw')return 'Click the stove once to start cooking.';
  if(h.kind==='potato'&&h.state==='raw')return 'Click the prep board once; chopping is automatic.';
  if(h.kind==='potato'&&h.state==='chopped')return 'Click the fryer once to start frying.';
  if(['tomato','lettuce'].includes(h.kind)&&h.state==='raw')return 'Click the prep board once; chopping is automatic.';
  return 'Click a counter to place or assemble this ingredient.';
}
function updatePanel(){
  if(game.state!=='playing')return;const p=game.players[0];if(!p)return;const target=state.hover||state.selected;const action=target?predictedAction(p,target):state.task?.action||'Move';const title=target?targetName(target):(state.task?targetName(state.task.target):'Service');const progress=state.task?.phase==='work'?Math.round((state.task.progress||0)*100):0;
  ui.panel.innerHTML=`<div class="v9-main"><span class="v9-target">${title}</span><span class="v9-action">${action}</span></div><div class="v9-sub">${serviceHint(p)} • Left click = move / primary action • Right click = cancel only • Middle click = throw • E/Space = selected action</div>${state.task?.phase==='work'?`<div class="v9-progress"><i style="width:${progress}%"></i></div>`:''}`;
}
function stationStatus(){
  const out=[];for(const s of game.stations){if(!s.slot)continue;if(s.type==='prep')out.push({text:`PREP ${s.slot.state==='raw'?Math.round(clamp((s.progress||0)/1.7,0,1)*100)+'%':s.slot.state.toUpperCase()}`,cls:s.slot.state==='raw'?'work':'ready'});else if(s.type==='sink')out.push({text:`SINK ${s.slot.dirty?Math.round(clamp((s.progress||0)/1.8,0,1)*100)+'%':'CLEAN'}`,cls:s.slot.dirty?'work':'ready'});else if(['stove','fryer','oven'].includes(s.type)){const risk=s.slot.burnt,ready=s.ready&&!risk;out.push({text:`${s.type.toUpperCase()} ${risk?'BURNED':ready?'READY':Math.round(clamp((s.cook||0)/(s.type==='oven'?4.1:3.5),0,1)*100)+'%'}`,cls:risk?'risk':ready?'ready':'work'});}}
  return out;
}
function updateStationStrip(){const board=document.getElementById('v8-service-board');if(!board||game.state!=='playing')return;let strip=document.getElementById('v9-station-strip');if(!strip){strip=document.createElement('div');strip.id='v9-station-strip';board.appendChild(strip);}const statuses=stationStatus();strip.innerHTML=statuses.length?statuses.map(s=>`<span class="v9-station-chip ${s.cls}">${s.text}</span>`).join(''):'<span class="v9-station-chip">ALL STATIONS CLEAR</span>';}

function v9Layout(){
  const base=game.__v9BaseLayout;base();const b=game.currentBounds(),by={};for(const q of game.plan)(by[q.key]??=[]).push(q);const set=(key,i,x,z,rot=0)=>{const q=by[key]?.[i];if(!q)return;q.x=clamp(x,-b.xMax+.9,b.xMax-.9);q.z=clamp(z,b.zMin+.9,b.zMax-.9);q.rot=rot;};
  const back=b.zMin+1.25;set('grocery',0,0,back,0);set('sink',0,-b.xMax+1.35,back+.15,0);set('plate',0,-b.xMax+3.15,back+.15,0);set('trash',0,b.xMax-1.25,back+.15,0);
  const prod=['prep','stove','fryer','oven'].flatMap(k=>(by[k]||[]).map((q,i)=>({k,i})));const left=-Math.min(4.6,b.xMax-2.0),right=Math.min(4.6,b.xMax-2.0),z1=Math.min(-1.9,back+3.0);prod.forEach((e,i)=>{const side=i%2===0?left:right,row=Math.floor(i/2);set(e.k,e.i,side,z1+row*2.05,side<0?Math.PI/2:-Math.PI/2);});
  (by.counter||[]).forEach((q,i)=>set('counter',i,(i-(by.counter.length-1)/2)*2.0,.15,0));
  const tables=by.table||[],cols=Math.min(3,Math.max(2,Math.ceil(Math.sqrt(tables.length)))),gapX=Math.min(4.4,(b.xMax*2-4)/Math.max(1,cols-1));tables.forEach((q,i)=>{const row=Math.floor(i/cols),col=i%cols,count=Math.min(cols,tables.length-row*cols);q.x=(col-(count-1)/2)*gapX;q.z=3.0+row*3.4;q.rot=row%2?Math.PI/2:0;});
  game.business.plan=game.plan.map(q=>({...q}));game.saveBusiness();game.renderPlanVisuals();game.updateBuildUI();game.updateGhost();game.flash('SENIOR V9 LAYOUT — compact work triangle, central pass and clear dining lanes.');
}
game.__v9BaseLayout=game.autoLayout.bind(game);game.autoLayout=v9Layout;

const baseOpen=game.openRestaurant.bind(game);game.openRestaurant=function openRestaurantV9(){cancelTask('READY');clearSelection();baseOpen();syncLayer();if(this.state==='playing'){installPrimaryPlayer(this.players[0]);this.flash('SENIOR V9 — left-click service. Right click only cancels; no hold-to-work mechanics.');}};
const baseClear=game.clearGameplay.bind(game);game.clearGameplay=function clearGameplayV9(...args){cancelTask('READY');clearSelection();return baseClear(...args);};
const baseEnd=game.endLevel.bind(game);game.endLevel=function endLevelV9(...args){cancelTask('SHIFT ENDED');const out=baseEnd(...args);syncLayer();return out;};

const baseLoop=game.loop.bind(game);game.loop=function loopV9(ts){const now=performance.now();if(this.__v9Last==null)this.__v9Last=now;const dt=Math.min(.05,Math.max(.001,(now-this.__v9Last)/1000));this.__v9Last=now;state.uiTick+=dt;syncLayer();updateSelection();if(state.uiTick>.08){state.uiTick=0;updatePanel();updateStationStrip();}return baseLoop(ts);};

function refreshCopy(){
  const hero=document.querySelector('#menu-screen .hero-card p');if(hero)hero.textContent='Run the restaurant with a cleaner service model: click to move, click a station once to use it, let timed prep/washing finish automatically, then keep serving. Solo remains truly solo with no hidden AI staff.';
  const note=document.querySelector('#menu-screen .controller-note');if(note)note.innerHTML='<b>Senior V9:</b> Player 1 no longer uses right-click hold interactions. Left click is the complete primary service control; right click only cancels a queued action.';
  const cards=document.querySelectorAll('#controls-screen .controls-grid article');if(cards[0])cards[0].innerHTML='<h3>PLAYER 1 • MOUSE — V9</h3><p><b>Left click floor:</b> move<br/><b>Left click object:</b> approach + perform one contextual action<br/><b>Prep / sink:</b> one click starts automatic timed work<br/><b>Right click:</b> cancel current action only<br/><b>Middle click:</b> throw held item<br/><b>E / Space:</b> use selected target</p>';if(cards[3])cards[3].innerHTML='<h3>CAMERA</h3><p><b>Service:</b> wheel zoom • C cycles camera • Home resets<br/><b>Build mode:</b> normal right-drag orbit remains available<br/><b>Service right click:</b> cancellation only — it never triggers cooking or work.</p>';
}
refreshCopy();

const baseTutorial=game.renderTutorial.bind(game);game.renderTutorial=function renderTutorialV9(){baseTutorial();const title=document.getElementById('tutorial-title')?.textContent;if(title==='Move, interact and throw'){document.getElementById('tutorial-visual').innerHTML='<div class="keys"><kbd>LEFT CLICK = MOVE / ACTION</kbd><kbd>RIGHT CLICK = CANCEL</kbd><kbd>MIDDLE = THROW</kbd></div>';document.getElementById('tutorial-body').textContent='Senior V9 removes hold-to-work. Click a station once: the chef approaches it and performs the contextual action. Chopping and washing continue as short timed jobs with a visible progress bar. Right click only cancels a queued action.';}};

v8.mouse.leftDown=false;v8.mouse.rightDown=false;v8.mouse.action=null;v8.mouse.moveTarget=null;
game.__seniorV9={version:VERSION,state,resolveTarget,queueTask,cancelTask,predictedAction,stationStatus,installPrimaryPlayer,v9Layout};
console.info('Senior V9 active: single-click contextual service, automatic timed prep/wash, right-click cancel, quiet interaction feedback and compact work-triangle layout.');
