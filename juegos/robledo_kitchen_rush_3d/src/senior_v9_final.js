import './senior_v9.js';

const game=window.__rkrGame;
const v9=game?.__seniorV9;
if(!game||!v9)throw new Error('Senior V9 final layer loaded before Senior V9.');

// During service the transparent V9 interaction surface owns the mouse, so the
// legacy canvas listeners cannot reintroduce hold-to-work or camera drag. In
// build/menu screens the canvas is restored immediately for normal editor/camera
// behavior.
function syncPointerOwnership(){
  const playing=game.state==='playing';
  const layer=document.getElementById('v9-input-layer');
  if(layer)layer.classList.toggle('active',playing);
  game.canvas.style.pointerEvents=playing?'none':'auto';
  if(game.__seniorV8){game.__seniorV8.mouse.leftDown=false;game.__seniorV8.mouse.rightDown=false;game.__seniorV8.mouse.action=null;game.__seniorV8.mouse.moveTarget=null;}
  requestAnimationFrame(syncPointerOwnership);
}
requestAnimationFrame(syncPointerOwnership);

// V8 food halos remain part of the inherited presentation layer. V9 removes
// them from active interaction because the new interaction design uses a single
// quiet target ring and HUD progress instead of pulses/halos/particle feedback.
function suppressLegacyInteractionDecoration(){
  for(const item of game.items||[])if(item?.__v8Halo)item.__v8Halo.visible=false;
  for(const player of game.players||[])if(player?.__v8SelectionRing)player.__v8SelectionRing.visible=false;
  requestAnimationFrame(suppressLegacyInteractionDecoration);
}
requestAnimationFrame(suppressLegacyInteractionDecoration);

v9.patchLevel='9.0.1-pointer-ownership';
console.info('Senior V9.0.1 final layer active: service mouse ownership isolated from legacy hold/camera mechanics.');
