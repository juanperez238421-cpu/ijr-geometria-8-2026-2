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
game.openRestaurant=function openRestaurantV905(...args){const result=openRestaurantV9(...args);applyPointerOwnership();return result;};
const enterBuildV9=game.enterBuildMode.bind(game);
game.enterBuildMode=function enterBuildModeV905(...args){const result=enterBuildV9(...args);applyPointerOwnership();return result;};
const toMenuV9=game.toMenu.bind(game);
game.toMenu=function toMenuV905(...args){const result=toMenuV9(...args);applyPointerOwnership();return result;};
function pointerOwnershipLoop(){applyPointerOwnership();requestAnimationFrame(pointerOwnershipLoop);}
applyPointerOwnership();requestAnimationFrame(pointerOwnershipLoop);

// V9 prep/wash is a true one-click job, driven by wall-clock time rather than a
// held input or frame-count accumulation. That keeps the mechanic consistent at
// low FPS and makes the interaction feel like a deliberate kitchen action:
// click once, watch progress, receive the completed item.
function workDuration(player,type){const role=type==='prep'?'prep':'service';const multiplier=Math.max(.7,Number(player?.workMultiplier?.(role))||1);return (type==='prep'?1550:1650)/multiplier;}
function finishTimedJob(task,player,target){
  if(v9.state.task!==task||!target.slot)return;
  if(target.type==='prep'){
    if(target.slot.state==='raw')target.slot.setState('chopped');
    target.progress=0;if(target.bar)target.bar.scale.x=.001;game.sfx.chop();
  }else{
    if(target.slot.dirty){target.slot.setDirty(false);target.slot.components=[];target.slot.baked=false;target.slot.burnt=false;game.score+=15;game.sfx.serve();}
    target.progress=0;if(target.bar)target.bar.scale.x=.001;
  }
  if(!player.held){const item=target.slot;player.pick(item);item.onSurface=false;target.slot=null;}
  const held=player.held;v9.state.task=null;game.v8Shift.interactions=(Number(game.v8Shift.interactions)||0)+1;
  game.qaRecord('v9-timed-job-complete',{target:target.type,kind:held?.kind||'plate',state:held?.state||null});
  game.flash(target.type==='prep'?'PREP COMPLETE — ingredient returned to chef.':'WASH COMPLETE — clean plate returned to chef.');
}
function superviseTimedJob(){
  const task=v9.state?.task,player=game.players?.[0],target=task?.target;
  if(game.state!=='playing'||!player?.human||!task||!target||!['prep','sink'].includes(target.type))return;
  const p=target.pos||target.group?.position;if(!p||Math.hypot(player.group.position.x-p.x,player.group.position.z-p.z)>2.08)return;
  if(!target.slot){
    if(!player.held)return;
    game.interact(player,target,.018,true);
    if(!target.slot)return;
  }
  const valid=target.type==='prep'?target.slot.state==='raw':!!target.slot.dirty;
  if(!valid){
    if(!player.held){const item=target.slot;player.pick(item);item.onSurface=false;target.slot=null;}
    v9.state.task=null;return;
  }
  if(task.phase!=='work'||!task.workStarted){task.phase='work';task.workStarted=performance.now();task.workDuration=workDuration(player,target.type);task.progress=0;target.progress=0;game.qaRecord('v9-timed-job-start',{target:target.type,kind:target.slot.kind||'plate',duration:Math.round(task.workDuration)});}
  const elapsed=performance.now()-task.workStarted;task.progress=Math.min(1,elapsed/task.workDuration);target.progress=task.progress*(target.type==='prep'?1.7:1.8);if(target.bar)target.bar.scale.x=Math.max(.001,task.progress);
  if(elapsed>=task.workDuration)finishTimedJob(task,player,target);
}
const timedJobInterval=setInterval(superviseTimedJob,45);

function suppressLegacyInteractionDecoration(){
  for(const item of game.items||[])if(item?.__v8Halo)item.__v8Halo.visible=false;
  for(const player of game.players||[])if(player?.__v8SelectionRing)player.__v8SelectionRing.visible=false;
  requestAnimationFrame(suppressLegacyInteractionDecoration);
}
requestAnimationFrame(suppressLegacyInteractionDecoration);

v9.applyPointerOwnership=applyPointerOwnership;
v9.superviseTimedJob=superviseTimedJob;
v9.timedJobInterval=timedJobInterval;
v9.patchLevel='9.0.5-wall-clock-single-click-jobs';
console.info('Senior V9.0.5 final layer active: cancel-only right click and wall-clock single-click prep/wash jobs.');
