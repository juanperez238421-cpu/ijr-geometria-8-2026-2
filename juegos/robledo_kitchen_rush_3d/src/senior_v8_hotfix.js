import * as THREE from 'three';
import './senior_v8.js';

const game = window.__rkrGame;
if (!game?.__seniorV8) throw new Error('Senior V8 hotfix loaded before Senior V8.');
const v8 = game.__seniorV8;
const mouse = v8.mouse;

// -----------------------------------------------------------------------------
// SENIOR V8.1 INPUT / UX HARDENING
// -----------------------------------------------------------------------------
// Service HUD layers used to sit visually above the WebGL canvas. A click on a
// grocery compartment could therefore land on HUD DOM instead of the canvas,
// which made both left and right mouse interaction appear dead. During service
// these overlays are informational only, so make them transparent to input and
// also accept capture-phase gestures anywhere inside the canvas rectangle.
const PASSIVE_SERVICE_UI = ['hud','orders','player-hud','message','interaction-hint','v8-service-board'];
function makeServiceUiPassive(){
  for(const id of PASSIVE_SERVICE_UI){const el=document.getElementById(id);if(el)el.style.pointerEvents='none';}
}
makeServiceUiPassive();

const targetPoint = target => target?.pos || target?.group?.position || null;
const targetDistance = (player,target) => { const p=targetPoint(target); return p?Math.hypot(player.group.position.x-p.x,player.group.position.z-p.z):Infinity; };
const isContinuous = target => target?.type==='prep'||target?.type==='sink';
const countInteraction = () => { if(game.v8Shift) game.v8Shift.interactions=(Number(game.v8Shift.interactions)||0)+1; };

function pointerNdc(event){const r=game.canvas.getBoundingClientRect();return new THREE.Vector2(((event.clientX-r.left)/r.width)*2-1,-(((event.clientY-r.top)/r.height)*2-1));}
function floorPointFromEvent(event){game.raycaster.setFromCamera(pointerNdc(event),game.camera);const point=new THREE.Vector3();return game.raycaster.ray.intersectPlane(game.floorPlane,point)?point:null;}
function insideCanvas(event){const r=game.canvas.getBoundingClientRect();return event.clientX>=r.left&&event.clientX<=r.right&&event.clientY>=r.top&&event.clientY<=r.bottom;}
function interactiveDomTarget(target){return !!target?.closest?.('button,input,select,textarea,a,[role="button"]');}
function validServiceGesture(event){return game.state==='playing'&&insideCanvas(event)&&!interactiveDomTarget(event.target);}

// A grocery wall is one shared 3D model with several logical compartments.
// Resolve those logical anchors in screen space before mesh raycasting. This
// gives each ingredient a generous and deterministic click target.
function screenTargetFromPointer(event,player){
  const r=game.canvas.getBoundingClientRect(),candidates=[];
  for(const s of game.stations)candidates.push({target:s,pos:s.pos,y:s.type==='storage'?1.0:1.04,max:s.type==='storage'?116:94,priority:s.type==='storage'?0:1});
  for(const t of game.tables)candidates.push({target:t,pos:t.pos,y:.82,max:106,priority:2});
  for(const item of game.items){if(item===player.held||item.dead||item.airborne||item.onSurface)continue;candidates.push({target:item,pos:item.group.position,y:item.group.position.y,max:72,priority:3});}
  let best=null,bestD=Infinity,bestPriority=99;
  for(const c of candidates){
    const v=new THREE.Vector3(c.pos.x,c.y,c.pos.z).project(game.camera);if(v.z<-1||v.z>1)continue;
    const sx=r.left+(v.x+1)*r.width/2,sy=r.top+(1-v.y)*r.height/2,d=Math.hypot(event.clientX-sx,event.clientY-sy);
    if(d<c.max&&(d<bestD-1||(Math.abs(d-bestD)<=1&&c.priority<bestPriority))){bestD=d;bestPriority=c.priority;best=c.target;}
  }
  return best;
}
function resolvePointerTarget(event,player){return screenTargetFromPointer(event,player)||v8.targetFromPointer(event,player);}

function immediateAction(player,target,mode){
  if(!target)return false;
  v8.queueAction(player,target,mode);
  const action=mouse.action;
  if(targetDistance(player,target)>2.08)return true;
  const before=player.held?.kind||player.held?.description?.()||null;
  game.interact(player,target,.018,true);
  const after=player.held?.kind||player.held?.description?.()||null;
  countInteraction();
  if(action)action.didFire=true;
  game.qaRecord('v8-pointer-immediate',{button:mode,target:target.type||target.kind||'item',kind:target.kind||null,player:1,before,after});
  if(mode==='smart'&&!isContinuous(target))mouse.action=null;
  return true;
}

const lastPressByButton=new Map();
function handleServicePress(event,source){
  if(!validServiceGesture(event))return;
  const now=performance.now(),last=lastPressByButton.get(event.button)||-999;if(now-last<72)return;lastPressByButton.set(event.button,now);
  const p1=game.players?.[0];if(!p1?.human)return;game.cameraRig.dragging=false;
  if(event.button===0){
    mouse.leftDown=true;const target=resolvePointerTarget(event,p1);
    if(target)immediateAction(p1,target,'smart');
    else{v8.selectTarget(p1,null);mouse.action=null;const floor=floorPointFromEvent(event);if(floor)mouse.moveTarget=floor.clone();}
  }else if(event.button===2){
    mouse.rightDown=true;const target=resolvePointerTarget(event,p1)||p1.selectedTarget||game.nearestInteractable(p1.group.position,4.6);
    if(target)immediateAction(p1,target,'hold');
  }else if(event.button===1){if(p1.held)p1.throwItem();}
  else return;
  game.qaRecord('v8-service-gesture',{source,button:event.button,target:resolvePointerTarget(event,p1)?.type||resolvePointerTarget(event,p1)?.kind||null});
  event.preventDefault();event.stopImmediatePropagation();
}
function handleServiceRelease(event){
  if(game.state!=='playing')return;
  if(event.button===0)mouse.leftDown=false;
  if(event.button===2){mouse.rightDown=false;game.cameraRig.dragging=false;if(mouse.action?.mode==='hold')mouse.action=null;}
  if(insideCanvas(event)){event.preventDefault();event.stopImmediatePropagation();}
}
window.addEventListener('pointerdown',e=>handleServicePress(e,'pointerdown'),true);
window.addEventListener('mousedown',e=>handleServicePress(e,'mousedown-fallback'),true);
window.addEventListener('pointerup',handleServiceRelease,true);
window.addEventListener('mouseup',handleServiceRelease,true);
window.addEventListener('pointercancel',()=>{mouse.leftDown=false;mouse.rightDown=false;if(mouse.action?.mode==='hold')mouse.action=null;},true);
window.addEventListener('contextmenu',event=>{if(game.state==='playing'&&insideCanvas(event)){event.preventDefault();event.stopImmediatePropagation();}},true);

// Contextual hover guidance makes the physical kitchen readable before clicking.
const hint=document.getElementById('interaction-hint');
let hoverTarget=null;
window.addEventListener('pointermove',event=>{
  if(game.state!=='playing'||!insideCanvas(event)||interactiveDomTarget(event.target)){hoverTarget=null;if(hint)hint.classList.add('hidden');return;}
  const p1=game.players?.[0];if(!p1?.human)return;hoverTarget=resolvePointerTarget(event,p1);
  if(!hint)return;
  if(!hoverTarget){hint.classList.add('hidden');return;}
  const name=hoverTarget.type==='storage'?(hoverTarget.kind||'ingredient').toUpperCase():String(hoverTarget.type||hoverTarget.kind||'OBJECT').toUpperCase();
  hint.textContent=`${name} • LEFT ACTION • RIGHT HOLD`;
  hint.style.position='fixed';hint.style.left=`${Math.min(innerWidth-245,event.clientX+18)}px`;hint.style.top=`${Math.max(14,event.clientY-38)}px`;hint.style.zIndex='80';hint.style.pointerEvents='none';hint.classList.remove('hidden');
},true);

// -----------------------------------------------------------------------------
// LOW-FPS INPUT DETERMINISM
// -----------------------------------------------------------------------------
const baseSpawnPlayersV8=game.spawnPlayers.bind(game);
game.spawnPlayers=function spawnPlayersSeniorV810(){
  baseSpawnPlayersV8();
  for(const player of this.players){
    if(!player.human||player.__v8LowFpsWrapped)continue;
    player.__v8LowFpsWrapped=true;const baseHuman=player.updateHuman.bind(player);let last=performance.now();
    player.updateHuman=function updateHumanLowFps(dt,input){const now=performance.now(),wallDt=Math.min(.10,Math.max(.001,(now-last)/1000));last=now;return baseHuman(Math.max(dt,wallDt),input);};
  }
};

function continuousSnapshot(player,target){if(target?.type==='prep')return`${player?.held?.kind||''}|${target.slot?.kind||''}|${target.slot?.state||''}|${Number(target.progress||0).toFixed(4)}`;if(target?.type==='sink')return`${player?.held?.dirty||false}|${target.slot?.dirty||false}|${Number(target.progress||0).toFixed(4)}`;return'';}
function continuousSemantic(player,target){if(target?.type==='prep')return`${player?.held?.kind||''}|${target.slot?.kind||''}|${target.slot?.state||''}`;if(target?.type==='sink')return`${player?.held?.dirty||false}|${target.slot?.dirty||false}`;return'';}
function continuousFinished(target){if(target?.type==='prep')return!!target.slot&&target.slot.state!=='raw';if(target?.type==='sink')return!!target.slot&&!target.slot.dirty;return true;}
function advanceContinuousWork(player,action,dt,source){
  const target=action?.target;if(!player?.human||!target||!isContinuous(target)||targetDistance(player,target)>2.08)return false;
  const before=continuousSnapshot(player,target),beforeSemantic=continuousSemantic(player,target);
  if(target.type==='prep'){if(!target.slot&&player.held&&!player.held.isPlate)game.interact(player,target,dt,true);else if(target.slot?.state==='raw')game.interact(player,target,dt,true);}else{if(!target.slot&&player.held?.isPlate&&player.held.dirty)game.interact(player,target,dt,true);else if(target.slot?.dirty)game.interact(player,target,dt,true);}
  const after=continuousSnapshot(player,target),afterSemantic=continuousSemantic(player,target);if(before!==after)game.qaRecord('v8-continuous-work',{target:target.type,source,before,after});if(beforeSemantic!==afterSemantic)countInteraction();if(continuousFinished(target))mouse.action=null;return before!==after;
}
const baseUpdateStations=game.updateStations.bind(game);
game.updateStations=function updateStationsSeniorV810(dt){const action=mouse.action;if(this.state==='playing'&&action?.mode==='smart')advanceContinuousWork(this.players?.[0],action,dt,'simulation');return baseUpdateStations(dt);};
const continuousWatchdog=window.setInterval(()=>{if(game.state!=='playing')return;const action=mouse.action,p1=game.players?.[0];if(!action||action.mode!=='smart'||!isContinuous(action.target)||!p1?.human)return;const snapshot=continuousSnapshot(p1,action.target);if(action.__watchdogSnapshot===snapshot)advanceContinuousWork(p1,action,.14,'watchdog');action.__watchdogSnapshot=continuousSnapshot(p1,action.target);},120);

const movementSamples=new Map();
function fallbackMove(player,dx,dz,dt=.07){const len=Math.hypot(dx,dz);if(!player?.human||len<.001)return false;dx/=len;dz/=len;player.facing.set(dx,0,dz);player.group.rotation.y=Math.atan2(dx,dz);const before=player.group.position.clone();game.moveCrew(player,new THREE.Vector3(dx,0,dz).multiplyScalar(player.speed*dt));const moved=before.distanceToSquared(player.group.position)>1e-8;if(moved)game.qaRecord('v8-input-watchdog',{player:player.index+1,dx,dz});return moved;}
function keyboardVector(index){const k=game.input.keys;if(index===1)return{x:(k.has('KeyD')?1:0)-(k.has('KeyA')?1:0),z:(k.has('KeyS')?1:0)-(k.has('KeyW')?1:0)};if(index===2)return{x:(k.has('ArrowRight')?1:0)-(k.has('ArrowLeft')?1:0),z:(k.has('ArrowDown')?1:0)-(k.has('ArrowUp')?1:0)};return{x:0,z:0};}
function fallbackToward(player,destination,dt=.07){if(!player?.human||!destination)return false;const dx=destination.x-player.group.position.x,dz=destination.z-player.group.position.z;if(Math.hypot(dx,dz)<.12)return false;return fallbackMove(player,dx,dz,dt);}
const movementWatchdog=window.setInterval(()=>{
  if(game.state!=='playing')return;
  for(const player of game.players){
    if(!player.human)continue;const prev=movementSamples.get(player.index),now={x:player.group.position.x,z:player.group.position.z},stalled=prev&&Math.hypot(now.x-prev.x,now.z-prev.z)<.003;
    if(stalled){
      if(player.index===1||player.index===2){const vec=keyboardVector(player.index);if(Math.hypot(vec.x,vec.z)>.001)fallbackMove(player,vec.x,vec.z,.075);}
      else if(player.index===0){const destination=mouse.action?.destination||mouse.moveTarget;if(destination)fallbackToward(player,destination,.075);const action=mouse.action;if(action&&targetDistance(player,action.target)<=2.08&&!action.didFire&&!isContinuous(action.target)){game.interact(player,action.target,.018,true);countInteraction();action.didFire=true;game.qaRecord('v8-pointer-watchdog-interact',{target:action.target.type||action.target.kind||'item'});if(action.mode==='smart')mouse.action=null;}}
    }
    movementSamples.set(player.index,{x:player.group.position.x,z:player.group.position.z});
  }
},80);

// -----------------------------------------------------------------------------
// PHYSICAL INGREDIENT READABILITY / ANIMATION
// -----------------------------------------------------------------------------
const storageMarkers=[];
function makeIngredientBadge(kind){
  const meta={tomato:['🍅','TOMATO'],lettuce:['🥬','LETTUCE'],meat:['🥩','MEAT'],potato:['🥔','POTATO'],dough:['🫓','DOUGH'],cheese:['🧀','CHEESE'],bun:['🥯','BUN']}[kind]||['•',String(kind).toUpperCase()];
  const canvas=document.createElement('canvas');canvas.width=360;canvas.height=92;const ctx=canvas.getContext('2d');ctx.fillStyle='rgba(25,39,45,.90)';ctx.beginPath();ctx.roundRect(4,4,352,84,20);ctx.fill();ctx.fillStyle='#fff';ctx.font='800 27px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(`${meta[0]}  ${meta[1]}`,180,46);const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false}));sprite.scale.set(1.62,.41,1);sprite.userData.v8StorageBadge=true;return sprite;
}
function clearStorageMarkers(){for(const m of storageMarkers){m.ring?.removeFromParent();m.badge?.removeFromParent();m.ring?.geometry?.dispose?.();m.ring?.material?.dispose?.();m.badge?.material?.map?.dispose?.();m.badge?.material?.dispose?.();}storageMarkers.length=0;}
function refreshStorageMarkers(){
  clearStorageMarkers();if(game.state!=='playing')return;
  let i=0;for(const s of game.stations.filter(x=>x.type==='storage')){
    const ring=new THREE.Mesh(new THREE.RingGeometry(.25,.39,28),new THREE.MeshBasicMaterial({color:0xf2bd3f,transparent:true,opacity:.64,side:THREE.DoubleSide,depthTest:false}));ring.rotation.x=-Math.PI/2;ring.position.set(s.pos.x,.055,s.pos.z);ring.renderOrder=90;game.fixtureRoot.add(ring);
    const badge=makeIngredientBadge(s.kind);badge.position.set(s.pos.x,1.82,s.pos.z);badge.renderOrder=95;game.fixtureRoot.add(badge);storageMarkers.push({station:s,ring,badge,phase:i++*.7});
  }
}
function animateStorageMarkers(){const t=performance.now()/1000;for(const m of storageMarkers){if(!m.ring?.parent)continue;const selected=game.players?.[0]?.selectedTarget===m.station;m.ring.material.opacity=selected?.96:.48+.18*Math.sin(t*3.2+m.phase);m.ring.scale.setScalar(selected?1.25:1+.05*Math.sin(t*2.4+m.phase));m.badge.position.y=1.82+.035*Math.sin(t*2.2+m.phase);}}

const baseOpenRestaurantHotfix=game.openRestaurant.bind(game);
game.openRestaurant=function openRestaurantSeniorV810(){const result=baseOpenRestaurantHotfix();makeServiceUiPassive();if(this.state==='playing'){refreshStorageMarkers();if(this.config.humanCount===1)this.flash('SOLO SHIFT — you are the only chef. Take every order, prep, cook, serve and clean personally.');}return result;};
const visualTick=window.setInterval(()=>{if(game.state==='playing')animateStorageMarkers();},90);

// -----------------------------------------------------------------------------
// CHARACTER PERSONALIZATION EXTENSIONS
// -----------------------------------------------------------------------------
function ensureAvatarExtensions(){for(const a of game.config.avatars||[]){if(!a.hat)a.hat='none';if(!a.pattern)a.pattern='plain';if(!a.facialHair)a.facialHair='none';}}
function saveExtendedConfig(){try{localStorage.setItem('robledo_kitchen_rush_config',JSON.stringify(game.config));}catch(_){} }
ensureAvatarExtensions();

function addSelect(card,field,label,options,value){
  if(card.querySelector(`[data-v8x="${field}"]`))return;const wrap=document.createElement('label');wrap.dataset.v8x=field;wrap.textContent=label;const select=document.createElement('select');select.dataset.fieldExt=field;for(const [v,l] of options){const o=document.createElement('option');o.value=v;o.textContent=l;o.selected=String(v)===String(value);select.appendChild(o);}select.addEventListener('change',()=>{const i=Number(card.closest('[data-avatar]')?.dataset.avatar);if(!Number.isFinite(i)||!game.config.avatars?.[i])return;game.config.avatars[i][field]=select.value;saveExtendedConfig();});wrap.appendChild(select);card.appendChild(wrap);
}
function enhanceCustomizer(){
  ensureAvatarExtensions();for(const avatarCard of document.querySelectorAll('#v8-customization [data-avatar]')){const i=Number(avatarCard.dataset.avatar),fields=avatarCard.querySelector('.v8-fields'),a=game.config.avatars?.[i];if(!fields||!a)continue;addSelect(fields,'hat','Headwear',[['none','None'],['chefhat','Chef hat'],['cap','Kitchen cap'],['beanie','Beanie']],a.hat);addSelect(fields,'pattern','Uniform detail',[['plain','Plain'],['stripe','Stripe'],['double','Double stripe']],a.pattern);addSelect(fields,'facialHair','Facial hair',[['none','None'],['moustache','Moustache'],['beard','Short beard']],a.facialHair);}
}
enhanceCustomizer();
const customizePanel=document.getElementById('v8-customization');if(customizePanel)new MutationObserver(()=>queueMicrotask(enhanceCustomizer)).observe(customizePanel,{subtree:true,childList:true});

const baseChefAssetHotfix=game.assets.chef.bind(game.assets);
game.assets.chef=function chefSeniorV810(color,role='chef',index=0,isBot=false){
  ensureAvatarExtensions();const group=baseChefAssetHotfix(color,role,index,isBot);if(isBot)return group;const a=game.config.avatars?.[index]||{};const dark=new THREE.MeshStandardMaterial({color:0x30383c,roughness:.65});const cloth=new THREE.MeshStandardMaterial({color:0xf4eee3,roughness:.72});
  if(a.hat==='chefhat'){const brim=new THREE.Mesh(new THREE.CylinderGeometry(.33,.33,.12,22),cloth);brim.position.set(0,1.92,0);const crown=new THREE.Mesh(new THREE.CylinderGeometry(.27,.33,.34,22),cloth);crown.position.set(0,2.12,0);group.add(brim,crown);}else if(a.hat==='cap'){const cap=new THREE.Mesh(new THREE.SphereGeometry(.31,18,10,0,Math.PI*2,0,Math.PI/2),dark);cap.position.set(0,1.86,0);const brim=new THREE.Mesh(new THREE.BoxGeometry(.34,.035,.18),dark);brim.position.set(0,1.83,.28);group.add(cap,brim);}else if(a.hat==='beanie'){const beanie=new THREE.Mesh(new THREE.CylinderGeometry(.30,.31,.24,20),dark);beanie.position.set(0,1.9,0);group.add(beanie);}
  if(a.pattern==='stripe'||a.pattern==='double'){const stripe=new THREE.Mesh(new THREE.BoxGeometry(.5,.045,.055),dark);stripe.position.set(0,.89,.302);group.add(stripe);if(a.pattern==='double'){const stripe2=stripe.clone();stripe2.position.y=.78;group.add(stripe2);}}
  if(a.facialHair==='moustache'){const m=new THREE.Mesh(new THREE.BoxGeometry(.19,.035,.035),dark);m.position.set(0,1.51,.325);group.add(m);}else if(a.facialHair==='beard'){const b=new THREE.Mesh(new THREE.SphereGeometry(.19,14,8,0,Math.PI*2,Math.PI/2,Math.PI/2),dark);b.scale.set(1,.72,.55);b.position.set(0,1.43,.28);group.add(b);}
  return group;
};

// -----------------------------------------------------------------------------
// NPC TRAIT MECHANICS
// -----------------------------------------------------------------------------
function applyTraitMechanics(party){
  if(!party?.v8||party.v8.traitApplied)return;party.v8.traitApplied=true;const trait=party.v8.traits;let factor=1;
  if(trait==='Patient')factor=1.20;else if(trait==='In a hurry')factor=.84;else if(trait==='Food critic')factor=.94;else if(trait==='Chatty')factor=1.08;else if(trait==='Celebrating')factor=1.12;
  party.patience*=factor;party.patienceMax*=factor;game.qaRecord('v8-npc-trait-mechanic',{party:party.id,trait,patienceFactor:factor});
}
const baseSpawnPartyHotfix=game.spawnParty.bind(game);
game.spawnParty=function spawnPartySeniorV810(){const before=new Set(this.parties);const result=baseSpawnPartyHotfix();for(const p of this.parties)if(!before.has(p))applyTraitMechanics(p);return result;};
const baseCompleteTableHotfix=game.completeTable.bind(game);
game.completeTable=function completeTableSeniorV810(party,server,tip){const result=baseCompleteTableHotfix(party,server,tip);if(party?.v8&&!party.__v8TraitPaid){party.__v8TraitPaid=true;const fast=party.waitElapsed<=30,trait=party.v8.traits;let bonus=0;if(trait==='Celebrating')bonus=fast?14:7;else if(trait==='Food critic'&&fast)bonus=11;else if(trait==='In a hurry'&&fast)bonus=9;else if(trait==='Patient')bonus=4;if(bonus){this.business.cash+=bonus;this.business.loyalty=Math.min(100,(Number(this.business.loyalty)||0)+1);this.saveBusiness();this.flash(`${trait} guest bonus +$${bonus}`);this.qaRecord('v8-npc-trait-bonus',{party:party.id,trait,bonus,fast});}}return result;};

window.addEventListener('pagehide',()=>{window.clearInterval(continuousWatchdog);window.clearInterval(movementWatchdog);window.clearInterval(visualTick);clearStorageMarkers();},{once:true});

game.__seniorV8.hotfix='8.1.0-service-input';
game.__seniorV8.patchLevel='8.1.0-overlay-proof-clicks-and-ux';
game.__seniorV8.resolvePointerTarget=resolvePointerTarget;
game.__seniorV8.refreshStorageMarkers=refreshStorageMarkers;
game.__seniorV8.enhanceCustomizer=enhanceCustomizer;
console.info('Senior V8.1.0 active: overlay-proof left/right clicks, ingredient anchors, true solo service, richer customization, NPC trait mechanics, and low-FPS deterministic controls.');
