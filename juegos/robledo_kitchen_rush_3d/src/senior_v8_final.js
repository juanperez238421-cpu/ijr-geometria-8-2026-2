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

// Expose a deterministic helper for QA and future accessibility controls.
v8.nearestStorage=nearestStorage;
v8.correctedTarget=correctedTarget;
v8.patchLevel='8.1.1-proximity-safe-grocery';
console.info('Senior V8.1.1 final layer active: proximity-safe ingredient compartments for left/right mouse interaction.');
