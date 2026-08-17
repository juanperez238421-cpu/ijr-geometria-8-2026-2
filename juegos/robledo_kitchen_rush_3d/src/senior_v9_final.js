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
game.openRestaurant=function openRestaurantV901(...args){const result=openRestaurantV9(...args);applyPointerOwnership();return result;};
const enterBuildV9=game.enterBuildMode.bind(game);
game.enterBuildMode=function enterBuildModeV901(...args){const result=enterBuildV9(...args);applyPointerOwnership();return result;};
const toMenuV9=game.toMenu.bind(game);
game.toMenu=function toMenuV901(...args){const result=toMenuV9(...args);applyPointerOwnership();return result;};

function pointerOwnershipLoop(){applyPointerOwnership();requestAnimationFrame(pointerOwnershipLoop);}
applyPointerOwnership();
requestAnimationFrame(pointerOwnershipLoop);

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
v9.patchLevel='9.0.2-synchronous-pointer-ownership';
console.info('Senior V9.0.2 final layer active: synchronous service pointer ownership, no legacy right-hold/camera race.');
