import './senior_v9.js';

const game=window.__rkrGame;
const v9=game?.__seniorV9;
if(!game||!v9)throw new Error('Senior V9 final layer loaded before Senior V9.');

function applyPointerOwnership(){
  const playing=game.state==='playing';
  const layer=document.getElementById('v9-input-layer');
  if(layer)layer.classList.toggle('active',playing);
  game.canvas.style.pointerEvents=playing?'none':'auto';
  if(game.__seniorV8){game.__seniorV8.mouse.leftDown=false;game.__seniorV8.mouse.rightDown=false;game.__seniorV8.mouse.action=null;game.__seniorV8.mouse.moveTarget=null;}
}

const openRestaurantV9=game.openRestaurant.bind(game);
game.openRestaurant=function openRestaurantV904(...args){const result=openRestaurantV9(...args);applyPointerOwnership();return result;};
const enterBuildV9=game.enterBuildMode.bind(game);
game.enterBuildMode=function enterBuildModeV904(...args){const result=enterBuildV9(...args);applyPointerOwnership();return result;};
const toMenuV9=game.toMenu.bind(game);
game.toMenu=function toMenuV904(...args){const result=toMenuV9(...args);applyPointerOwnership();return result;};
function pointerOwnershipLoop(){applyPointerOwnership();requestAnimationFrame(pointerOwnershipLoop);}
applyPointerOwnership();requestAnimationFrame(pointerOwnershipLoop);

// Single-click timed jobs own their complete lifecycle here. Once a prep/sink
// station is selected and the chef reaches it, V9 places the eligible item,
// advances the station clock and returns the completed item automatically. The
// user never has to hold or repeat a mouse button.
let lastServiceClock=performance.now();
function serviceJobLoop(now){
  const dt=Math.min(.08,Math.max(.016,(now-lastServiceClock)/1000));lastServiceClock=now;
  const task=v9.state?.task,player=game.players?.[0],target=task?.target;
  if(game.state==='playing'&&player?.human&&task&&target&&(target.type==='prep'||target.type==='sink')){
    const p=target.pos||target.group?.position;
    const near=p&&Math.hypot(player.group.position.x-p.x,player.group.position.z-p.z)<=2.08;
    if(near){
      // Start the job ourselves if the movement/update frame has not done it yet.
      if(task.phase!=='work'){
        if(!target.slot&&player.held)game.interact(player,target,.018,true);
        if(target.slot){task.phase='work';task.progress=0;game.qaRecord('v9-timed-job-start',{target:target.type,kind:target.slot.kind||'plate'});}
      }
      if(task.phase==='work'&&target.slot){
        const slotBefore=target.slot,stateBefore=slotBefore.state,dirtyBefore=!!slotBefore.dirty;
        game.interact(player,target,Math.max(.06,dt),true);
        task.progress=target.type==='prep'?Math.min(1,(target.progress||0)/1.7):Math.min(1,(target.progress||0)/1.8);
        const readyPrep=target.type==='prep'&&target.slot&&target.slot.state!=='raw';
        const readyWash=target.type==='sink'&&target.slot&&!target.slot.dirty;
        if((readyPrep||readyWash)&&!player.held)game.interact(player,target,.018,true);
        const returned=!target.slot&&!!player.held&&(
          (target.type==='prep'&&stateBefore==='raw')||
          (target.type==='sink'&&dirtyBefore)||
          player.held===slotBefore
        );
        if(returned){v9.state.task=null;game.qaRecord('v9-timed-job-complete',{target:target.type,kind:player.held.kind||'plate',state:player.held.state||null});game.flash(target.type==='prep'?'PREP COMPLETE — ingredient returned to chef.':'WASH COMPLETE — clean plate returned to chef.');}
      }
    }
  }
  requestAnimationFrame(serviceJobLoop);
}
requestAnimationFrame(serviceJobLoop);

function suppressLegacyInteractionDecoration(){
  for(const item of game.items||[])if(item?.__v8Halo)item.__v8Halo.visible=false;
  for(const player of game.players||[])if(player?.__v8SelectionRing)player.__v8SelectionRing.visible=false;
  requestAnimationFrame(suppressLegacyInteractionDecoration);
}
requestAnimationFrame(suppressLegacyInteractionDecoration);

v9.applyPointerOwnership=applyPointerOwnership;
v9.patchLevel='9.0.4-self-starting-single-click-jobs';
console.info('Senior V9.0.4 final layer active: cancel-only right click and self-starting single-click prep/wash lifecycle.');
