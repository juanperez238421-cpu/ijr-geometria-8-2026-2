import './senior_v8_hotfix.js';

const game = window.__rkrGame;
const v8 = game?.__seniorV8;
if (!game || !v8) throw new Error('Senior V8.1 final layer loaded before the game.');

const distanceXZ=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
function nearestStorage(player,max=1.6){
  if(!player?.human)return null;let best=null,bd=max;
  for(const s of game.stations){if(s.type!=='storage')continue;const d=distanceXZ(player.group.position,s.pos);if(d<bd){best=s;bd=d;}}
  return best;
}
function targetDistance(player,target){const p=target?.pos||target?.group?.position;return p?distanceXZ(player.group.position,p):Infinity;}
function correctedTarget(player,target){
  const near=nearestStorage(player,1.6);if(!near)return target;
  // When the chef is standing directly at a grocery compartment, physical
  // proximity is more reliable than a moving perspective camera. This makes
  // each ingredient behave like a real station even if the pointer lands on a
  // neighboring shelf mesh or a screen-space HUD edge.
  if(!target||target.type==='storage'||targetDistance(player,target)>1.9)return near;
  return target;
}

const baseQueue=v8.queueAction.bind(v8);
v8.queueAction=function queueActionV811(player,target,mode='smart'){
  const resolved=correctedTarget(player,target);if(resolved!==target)game.qaRecord('v8-storage-target-corrected',{from:target?.kind||target?.type||null,to:resolved?.kind||null,phase:'queue'});
  return baseQueue(player,resolved,mode);
};

const baseInteract=game.interact.bind(game);
game.interact=function interactV811(player,target,dt,held){
  const resolved=correctedTarget(player,target);if(resolved!==target){v8.selectTarget(player,resolved);game.qaRecord('v8-storage-target-corrected',{from:target?.kind||target?.type||null,to:resolved?.kind||null,phase:'interact'});}return baseInteract(player,resolved,dt,held);
};

function insideCanvas(event){const r=game.canvas.getBoundingClientRect();return event.clientX>=r.left&&event.clientX<=r.right&&event.clientY>=r.top&&event.clientY<=r.bottom;}
function recentRightGesture(){const now=performance.now();for(let i=game.qaEvents.length-1;i>=Math.max(0,game.qaEvents.length-18);i--){const e=game.qaEvents[i];if(now-e.time>520)break;if((e.type==='v8-service-gesture'&&e.button===2)||(e.type==='v8-pointer-immediate'&&e.button==='hold'))return true;}return false;}

// Chrome/Edge, embedded portable launchers and remote browser automation do not
// all emit the same right-button pointer sequence. `auxclick` is the standards-
// level completion event for a non-primary button and is not consumed by the
// camera/context-menu guards. It is therefore the final redundant input path:
// if the normal pointer/mousedown path already interacted, this stays dormant;
// otherwise it performs the same contextual service action.
window.addEventListener('auxclick',event=>{
  if(event.button!==2||game.state!=='playing'||!insideCanvas(event)||recentRightGesture())return;
  const player=game.players?.[0];if(!player?.human)return;
  const pointerTarget=v8.resolvePointerTarget?.(event,player)||player.selectedTarget||game.nearestInteractable(player.group.position,4.6);
  const target=correctedTarget(player,pointerTarget);if(!target)return;
  v8.selectTarget(player,target);game.cameraRig.dragging=false;
  if(targetDistance(player,target)<=2.08){const before=player.held?.kind||player.held?.description?.()||null;game.interact(player,target,.018,true);const after=player.held?.kind||player.held?.description?.()||null;game.qaRecord('v8-auxclick-fallback',{target:target.type||target.kind||'item',kind:target.kind||null,before,after,immediate:true});}
  else{v8.queueAction(player,target,'smart');game.qaRecord('v8-auxclick-fallback',{target:target.type||target.kind||'item',kind:target.kind||null,immediate:false});}
  event.preventDefault();event.stopImmediatePropagation();
},true);

// Expose deterministic helpers for QA and future accessibility controls.
v8.nearestStorage=nearestStorage;
v8.correctedTarget=correctedTarget;
console.info('Senior V8.1 final layer active: proximity-safe ingredient compartments and auxclick right-mouse fallback.');
