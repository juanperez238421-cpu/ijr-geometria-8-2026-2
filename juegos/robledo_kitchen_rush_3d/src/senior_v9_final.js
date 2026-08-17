import './senior_v9.js';

const game=window.__rkrGame;
const v9=game?.__seniorV9;
if(!game||!v9)throw new Error('Senior V9 final layer loaded before Senior V9.');

// During service the transparent V9 interaction surface owns the mouse, so the
// legacy canvas listeners cannot reintroduce hold-to-work or camera drag. This
// is applied synchronously on every gameplay/build transition and then guarded
// every frame. That removes the one-frame race where a freshly opened service
// could still expose the legacy canvas input layer.
function applyPointerOwnership(){
  const playing=game.state==='playing';
  const layer=document.getElementById('v9-input-layer');
  if(layer)layer.classList.toggle('active',playing);
  game.canvas.style.pointerEvents=playing?'none':'auto';
  if(game.__seniorV8){
    game.__seniorV8.mouse.leftDown=false;
    game.__seniorV8.mouse.rightDown=false;
    game.__seniorV8.mouse.action=null;
    game.__seniorV8.mouse.moveTarget=null;
  }
}

const openRestaurantV9=game.openRestaurant.bind(game);
game.openRestaurant=function openRestaurantV902(...args){const result=openRestaurantV9(...args);applyPointerOwnership();return result;};
const enterBuildV9=game.enterBuildMode.bind(game);
game.enterBuildMode=function enterBuildModeV902(...args){const result=enterBuildV9(...args);applyPointerOwnership();return result;};
const toMenuV9=game.toMenu.bind(game);
game.toMenu=function toMenuV902(...args){const result=toMenuV9(...args);applyPointerOwnership();return result;};

function pointerOwnershipLoop(){applyPointerOwnership();requestAnimationFrame(pointerOwnershipLoop);}
applyPointerOwnership();
requestAnimationFrame(pointerOwnershipLoop);

// V9 timed work is intentionally a single-click job. The inherited station
// implementation was originally designed for a held interact key, so this
// independent service clock keeps prep/washing progressing even when a browser
// drops frames or an input device never emits a held-button stream. It uses the
// existing station rules/sounds/state changes; it only supplies the work time.
let lastServiceClock=performance.now();
function serviceJobLoop(now){
  const dt=Math.min(.08,Math.max(.016,(now-lastServiceClock)/1000));lastServiceClock=now;
  const task=v9.state?.task,player=game.players?.[0],target=task?.target;
  if(game.state==='playing'&&player?.human&&task&&target&&(target.type==='prep'||target.type==='sink')){
    const p=target.pos||target.group?.position;
    const near=p&&Math.hypot(player.group.position.x-p.x,player.group.position.z-p.z)<=2.08;
    if(near&&task.phase==='work'){
      const slotBefore=target.slot,kindBefore=slotBefore?.kind||null,stateBefore=slotBefore?.state||null,dirtyBefore=!!slotBefore?.dirty;
      // A stronger fixed service quantum makes the action readable but brisk:
      // roughly 0.7–1.0 s for a normal chef instead of requiring a button hold.
      game.interact(player,target,Math.max(.06,dt),true);
      if(target.type==='prep')task.progress=Math.min(1,(target.progress||0)/1.7);
      else task.progress=Math.min(1,(target.progress||0)/1.8);
      const completedPrep=target.type==='prep'&&slotBefore&&stateBefore==='raw'&&(!target.slot||target.slot.state!=='raw');
      const completedWash=target.type==='sink'&&slotBefore&&dirtyBefore&&(!target.slot||!target.slot.dirty);
      if((completedPrep||completedWash)&&target.slot&&!player.held)game.interact(player,target,.018,true);
      const returned=!target.slot&&!!player.held&&(completedPrep||completedWash||kindBefore===player.held.kind);
      if(returned){
        v9.state.task=null;
        game.qaRecord('v9-timed-job-complete',{target:target.type,kind:player.held.kind||'plate',state:player.held.state||null});
        game.flash(target.type==='prep'?'PREP COMPLETE — ingredient returned to chef.':'WASH COMPLETE — clean plate returned to chef.');
      }
    }
  }
  requestAnimationFrame(serviceJobLoop);
}
requestAnimationFrame(serviceJobLoop);

// V8 food halos remain part of the inherited presentation layer. V9 removes
// them from active interaction because the new interaction design uses a single
// quiet target ring and HUD progress instead of pulses/halos/particle feedback.
function suppressLegacyInteractionDecoration(){
  for(const item of game.items||[])if(item?.__v8Halo)item.__v8Halo.visible=false;
  for(const player of game.players||[])if(player?.__v8SelectionRing)player.__v8SelectionRing.visible=false;
  requestAnimationFrame(suppressLegacyInteractionDecoration);
}
requestAnimationFrame(suppressLegacyInteractionDecoration);

v9.applyPointerOwnership=applyPointerOwnership;
v9.patchLevel='9.0.3-single-click-work-clock';
console.info('Senior V9.0.3 final layer active: synchronous pointer ownership plus deterministic single-click prep/wash jobs.');
