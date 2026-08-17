import * as THREE from 'three';
import './senior_v8.js';

const game = window.__rkrGame;
if (!game?.__seniorV8) throw new Error('Senior V8 hotfix loaded before Senior V8.');
const v8 = game.__seniorV8;
const mouse = v8.mouse;

// The live service board is informational and must never capture WebGL input.
const board = document.getElementById('v8-service-board');
if (board) board.style.pointerEvents = 'none';

const targetPoint = target => target?.pos || target?.group?.position || null;
const targetDistance = (player,target) => { const p=targetPoint(target); return p?Math.hypot(player.group.position.x-p.x,player.group.position.z-p.z):Infinity; };
const isContinuous = target => target?.type==='prep'||target?.type==='sink';

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
  // Execute the first interaction synchronously on pointer-down. This is the
  // critical reliability fix: a short click works even when the WebGL frame is
  // throttled and no requestAnimationFrame occurs before pointer-up.
  game.interact(player,target,.018,true);
  if(action)action.didFire=true;
  game.qaRecord('v8-pointer-immediate',{button:mode,target:target.type||target.kind||'item',player:1});
  if(mode==='smart'&&!isContinuous(target))mouse.action=null;
  return true;
}

// Window capture fires before the old canvas capture listener in the DOM event
// path. During service we own the complete mouse gesture here and stop it before
// legacy camera/control listeners can consume it. Build mode still uses the old
// right-drag camera behavior unchanged.
window.addEventListener('pointerdown',event=>{
  if(game.state!=='playing'||event.target!==game.canvas)return;
  const p1=game.players?.[0];if(!p1?.human)return;
  game.cameraRig.dragging=false;
  if(event.button===0){
    mouse.leftDown=true;
    const target=v8.targetFromPointer(event,p1);
    if(target)immediateAction(p1,target,'smart');
    else{v8.selectTarget(p1,null);mouse.action=null;const floor=floorPointFromEvent(event);if(floor)mouse.moveTarget=floor.clone();}
  }else if(event.button===2){
    mouse.rightDown=true;
    const target=v8.targetFromPointer(event,p1)||p1.selectedTarget||game.nearestInteractable(p1.group.position,4.6);
    if(target)immediateAction(p1,target,'hold');
  }else if(event.button===1){
    if(p1.held)p1.throwItem();
  }else return;
  event.preventDefault();event.stopImmediatePropagation();
},true);

window.addEventListener('pointerup',event=>{
  if(game.state!=='playing'||event.target!==game.canvas)return;
  if(event.button===0)mouse.leftDown=false;
  if(event.button===2){mouse.rightDown=false;game.cameraRig.dragging=false;if(mouse.action?.mode==='hold')mouse.action=null;}
  event.preventDefault();event.stopImmediatePropagation();
},true);
window.addEventListener('pointercancel',()=>{mouse.leftDown=false;mouse.rightDown=false;if(mouse.action?.mode==='hold')mouse.action=null;},true);
window.addEventListener('contextmenu',event=>{if(game.state==='playing'&&event.target===game.canvas){event.preventDefault();event.stopImmediatePropagation();}},true);

// The base renderer caps simulation dt for physics safety. On low-FPS WebGL
// machines that cap made human chefs artificially slow. Human control gets a
// wall-clock delta capped at 100 ms while the physical world keeps its safe dt.
const baseSpawnPlayersV8 = game.spawnPlayers.bind(game);
game.spawnPlayers = function spawnPlayersSeniorV805() {
  baseSpawnPlayersV8();
  for (const player of this.players) {
    if (!player.human || player.__v8LowFpsWrapped) continue;
    player.__v8LowFpsWrapped = true;
    const baseHuman = player.updateHuman.bind(player);
    let last = performance.now();
    player.updateHuman = function updateHumanLowFps(dt, input) {
      const now = performance.now();
      const wallDt = Math.min(.10, Math.max(.001, (now-last)/1000));last=now;
      return baseHuman(Math.max(dt,wallDt),input);
    };
  }
};

function continuousSnapshot(player,target){
  if(target?.type==='prep')return`${player?.held?.kind||''}|${target.slot?.kind||''}|${target.slot?.state||''}|${Number(target.progress||0).toFixed(4)}`;
  if(target?.type==='sink')return`${player?.held?.dirty||false}|${target.slot?.dirty||false}|${Number(target.progress||0).toFixed(4)}`;
  return'';
}
function continuousFinished(target){if(target?.type==='prep')return!!target.slot&&target.slot.state!=='raw';if(target?.type==='sink')return!!target.slot&&!target.slot.dirty;return true;}
function advanceContinuousWork(player,action,dt,source){
  const target=action?.target;if(!player?.human||!target||!isContinuous(target)||targetDistance(player,target)>2.08)return false;
  const before=continuousSnapshot(player,target);
  if(target.type==='prep'){
    if(!target.slot&&player.held&&!player.held.isPlate)game.interact(player,target,dt,true);else if(target.slot?.state==='raw')game.interact(player,target,dt,true);
  }else{
    if(!target.slot&&player.held?.isPlate&&player.held.dirty)game.interact(player,target,dt,true);else if(target.slot?.dirty)game.interact(player,target,dt,true);
  }
  const after=continuousSnapshot(player,target);if(before!==after)game.qaRecord('v8-continuous-work',{target:target.type,source,before,after});if(continuousFinished(target))mouse.action=null;return before!==after;
}

const baseUpdateStations=game.updateStations.bind(game);
game.updateStations=function updateStationsSeniorV805(dt){const action=mouse.action;if(this.state==='playing'&&action?.mode==='smart')advanceContinuousWork(this.players?.[0],action,dt,'simulation');return baseUpdateStations(dt);};

// Fallback if an embedded browser throttles animation frames after a click. It
// only advances work after observing no state change, so normal 60-FPS play is
// not accelerated.
const continuousWatchdog=window.setInterval(()=>{
  if(game.state!=='playing')return;const action=mouse.action,p1=game.players?.[0];if(!action||action.mode!=='smart'||!isContinuous(action.target)||!p1?.human)return;
  const snapshot=continuousSnapshot(p1,action.target);if(action.__watchdogSnapshot===snapshot)advanceContinuousWork(p1,action,.14,'watchdog');action.__watchdogSnapshot=continuousSnapshot(p1,action.target);
},120);
window.addEventListener('pagehide',()=>window.clearInterval(continuousWatchdog),{once:true});

game.__seniorV8.hotfix='8.0.1-input-overlay';
game.__seniorV8.patchLevel='8.0.5-immediate-pointer-service';
console.info('Senior V8.0.5 active: both mouse buttons execute immediately, low-FPS control is responsive, and Prep/Sink work is deterministic.');
