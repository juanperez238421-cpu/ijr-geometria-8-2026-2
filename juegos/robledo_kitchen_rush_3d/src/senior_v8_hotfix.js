import * as THREE from 'three';
import './senior_v8.js';

const game = window.__rkrGame;
if (!game?.__seniorV8) throw new Error('Senior V8 hotfix loaded before Senior V8.');
const v8 = game.__seniorV8;
const mouse = v8.mouse;

const board = document.getElementById('v8-service-board');
if (board) board.style.pointerEvents = 'none';

const targetPoint = target => target?.pos || target?.group?.position || null;
const targetDistance = (player,target) => { const p=targetPoint(target); return p?Math.hypot(player.group.position.x-p.x,player.group.position.z-p.z):Infinity; };
const isContinuous = target => target?.type==='prep'||target?.type==='sink';
const countInteraction = () => { if(game.v8Shift) game.v8Shift.interactions=(Number(game.v8Shift.interactions)||0)+1; };

function floorPointFromEvent(event){
  const r=game.canvas.getBoundingClientRect();
  const ndc=new THREE.Vector2(((event.clientX-r.left)/r.width)*2-1,-(((event.clientY-r.top)/r.height)*2-1));
  game.raycaster.setFromCamera(ndc,game.camera);const point=new THREE.Vector3();
  return game.raycaster.ray.intersectPlane(game.floorPlane,point)?point:null;
}
function immediateAction(player,target,mode){
  if(!target)return false;
  v8.queueAction(player,target,mode);
  const action=mouse.action;
  if(targetDistance(player,target)>2.08)return true;
  game.interact(player,target,.018,true);
  countInteraction();
  if(action)action.didFire=true;
  game.qaRecord('v8-pointer-immediate',{button:mode,target:target.type||target.kind||'item',player:1});
  if(mode==='smart'&&!isContinuous(target))mouse.action=null;
  return true;
}

// Own the service gesture at Window capture so it runs before the legacy canvas
// capture listener. Both buttons execute the first kitchen action on pointer-down,
// so a short click cannot be lost between WebGL frames.
window.addEventListener('pointerdown',event=>{
  if(game.state!=='playing'||event.target!==game.canvas)return;
  const p1=game.players?.[0];if(!p1?.human)return;game.cameraRig.dragging=false;
  if(event.button===0){mouse.leftDown=true;const target=v8.targetFromPointer(event,p1);if(target)immediateAction(p1,target,'smart');else{v8.selectTarget(p1,null);mouse.action=null;const floor=floorPointFromEvent(event);if(floor)mouse.moveTarget=floor.clone();}}
  else if(event.button===2){mouse.rightDown=true;const target=v8.targetFromPointer(event,p1)||p1.selectedTarget||game.nearestInteractable(p1.group.position,4.6);if(target)immediateAction(p1,target,'hold');}
  else if(event.button===1){if(p1.held)p1.throwItem();}
  else return;
  event.preventDefault();event.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',event=>{
  if(game.state!=='playing'||event.target!==game.canvas)return;if(event.button===0)mouse.leftDown=false;if(event.button===2){mouse.rightDown=false;game.cameraRig.dragging=false;if(mouse.action?.mode==='hold')mouse.action=null;}event.preventDefault();event.stopImmediatePropagation();
},true);
window.addEventListener('pointercancel',()=>{mouse.leftDown=false;mouse.rightDown=false;if(mouse.action?.mode==='hold')mouse.action=null;},true);
window.addEventListener('contextmenu',event=>{if(game.state==='playing'&&event.target===game.canvas){event.preventDefault();event.stopImmediatePropagation();}},true);

// Use wall-clock input delta for humans so low-FPS WebGL rendering does not make
// movement artificially slow. Physical-world dt remains safely capped.
const baseSpawnPlayersV8=game.spawnPlayers.bind(game);
game.spawnPlayers=function spawnPlayersSeniorV807(){baseSpawnPlayersV8();for(const player of this.players){if(!player.human||player.__v8LowFpsWrapped)continue;player.__v8LowFpsWrapped=true;const baseHuman=player.updateHuman.bind(player);let last=performance.now();player.updateHuman=function updateHumanLowFps(dt,input){const now=performance.now(),wallDt=Math.min(.10,Math.max(.001,(now-last)/1000));last=now;return baseHuman(Math.max(dt,wallDt),input);};}};

function continuousSnapshot(player,target){
  if(target?.type==='prep')return`${player?.held?.kind||''}|${target.slot?.kind||''}|${target.slot?.state||''}|${Number(target.progress||0).toFixed(4)}`;
  if(target?.type==='sink')return`${player?.held?.dirty||false}|${target.slot?.dirty||false}|${Number(target.progress||0).toFixed(4)}`;
  return'';
}
function continuousSemantic(player,target){
  if(target?.type==='prep')return`${player?.held?.kind||''}|${target.slot?.kind||''}|${target.slot?.state||''}`;
  if(target?.type==='sink')return`${player?.held?.dirty||false}|${target.slot?.dirty||false}`;
  return'';
}
function continuousFinished(target){if(target?.type==='prep')return!!target.slot&&target.slot.state!=='raw';if(target?.type==='sink')return!!target.slot&&!target.slot.dirty;return true;}
function advanceContinuousWork(player,action,dt,source){
  const target=action?.target;if(!player?.human||!target||!isContinuous(target)||targetDistance(player,target)>2.08)return false;
  const before=continuousSnapshot(player,target),beforeSemantic=continuousSemantic(player,target);
  if(target.type==='prep'){
    if(!target.slot&&player.held&&!player.held.isPlate)game.interact(player,target,dt,true);else if(target.slot?.state==='raw')game.interact(player,target,dt,true);
  }else{
    if(!target.slot&&player.held?.isPlate&&player.held.dirty)game.interact(player,target,dt,true);else if(target.slot?.dirty)game.interact(player,target,dt,true);
  }
  const after=continuousSnapshot(player,target),afterSemantic=continuousSemantic(player,target);
  if(before!==after)game.qaRecord('v8-continuous-work',{target:target.type,source,before,after});
  if(beforeSemantic!==afterSemantic)countInteraction();
  if(continuousFinished(target))mouse.action=null;
  return before!==after;
}

const baseUpdateStations=game.updateStations.bind(game);
game.updateStations=function updateStationsSeniorV807(dt){const action=mouse.action;if(this.state==='playing'&&action?.mode==='smart')advanceContinuousWork(this.players?.[0],action,dt,'simulation');return baseUpdateStations(dt);};

// Prep/Sink watchdog: embedded launchers may briefly throttle animation frames.
// It only advances after observing no state change, so normal 60-FPS play is not
// accelerated.
const continuousWatchdog=window.setInterval(()=>{if(game.state!=='playing')return;const action=mouse.action,p1=game.players?.[0];if(!action||action.mode!=='smart'||!isContinuous(action.target)||!p1?.human)return;const snapshot=continuousSnapshot(p1,action.target);if(action.__watchdogSnapshot===snapshot)advanceContinuousWork(p1,action,.14,'watchdog');action.__watchdogSnapshot=continuousSnapshot(p1,action.target);},120);

// Input watchdog: keyboard and click-to-move must remain responsive even if the
// render loop temporarily drops frames. The watchdog only moves a chef when the
// requested input is active AND the chef has not moved since the previous sample.
// At normal frame rates it stays dormant, avoiding double movement.
const movementSamples=new Map();
function fallbackMove(player,dx,dz,dt=.07){
  const len=Math.hypot(dx,dz);if(!player?.human||len<.001)return false;dx/=len;dz/=len;
  player.facing.set(dx,0,dz);player.group.rotation.y=Math.atan2(dx,dz);
  const before=player.group.position.clone();game.moveCrew(player,new THREE.Vector3(dx,0,dz).multiplyScalar(player.speed*dt));
  const moved=before.distanceToSquared(player.group.position)>1e-8;if(moved)game.qaRecord('v8-input-watchdog',{player:player.index+1,dx,dz});return moved;
}
function keyboardVector(index){
  const k=game.input.keys;
  if(index===1)return{x:(k.has('KeyD')?1:0)-(k.has('KeyA')?1:0),z:(k.has('KeyS')?1:0)-(k.has('KeyW')?1:0)};
  if(index===2)return{x:(k.has('ArrowRight')?1:0)-(k.has('ArrowLeft')?1:0),z:(k.has('ArrowDown')?1:0)-(k.has('ArrowUp')?1:0)};
  return{x:0,z:0};
}
function fallbackToward(player,destination,dt=.07){
  if(!player?.human||!destination)return false;const dx=destination.x-player.group.position.x,dz=destination.z-player.group.position.z;if(Math.hypot(dx,dz)<.12)return false;return fallbackMove(player,dx,dz,dt);
}
const movementWatchdog=window.setInterval(()=>{
  if(game.state!=='playing')return;
  for(const player of game.players){
    if(!player.human)continue;
    const prev=movementSamples.get(player.index),now={x:player.group.position.x,z:player.group.position.z};
    const stalled=prev&&Math.hypot(now.x-prev.x,now.z-prev.z)<.003;
    if(stalled){
      if(player.index===1||player.index===2){const v=keyboardVector(player.index);if(Math.hypot(v.x,v.z)>.001)fallbackMove(player,v.x,v.z,.075);}
      else if(player.index===0){const destination=mouse.action?.destination||mouse.moveTarget;if(destination)fallbackToward(player,destination,.075);const action=mouse.action;if(action&&targetDistance(player,action.target)<=2.08&&!action.didFire&&!isContinuous(action.target)){game.interact(player,action.target,.018,true);countInteraction();action.didFire=true;game.qaRecord('v8-pointer-watchdog-interact',{target:action.target.type||action.target.kind||'item'});if(action.mode==='smart')mouse.action=null;}}
    }
    movementSamples.set(player.index,{x:player.group.position.x,z:player.group.position.z});
  }
},80);

window.addEventListener('pagehide',()=>{window.clearInterval(continuousWatchdog);window.clearInterval(movementWatchdog);},{once:true});

game.__seniorV8.hotfix='8.0.1-input-overlay';
game.__seniorV8.patchLevel='8.0.7-input-watchdog';
console.info('Senior V8.0.7 active: immediate mouse actions, low-FPS movement watchdog, and deterministic Prep/Sink work.');
