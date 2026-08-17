import './senior_v8.js';

const game = window.__rkrGame;
if (!game?.__seniorV8) throw new Error('Senior V8 hotfix loaded before Senior V8.');

// The live service board is informational. It must never sit above the WebGL
// canvas as an input-capturing layer, otherwise kitchen objects projected into
// the lower-right portion of the screen cannot receive Player 1 mouse clicks.
const board = document.getElementById('v8-service-board');
if (board) board.style.pointerEvents = 'none';

// Keep pointer ownership explicit during restaurant service. The legacy camera
// listener may still exist on the canvas from the base engine, but V8's capture
// listener owns right-click interaction while playing.
game.canvas.addEventListener('pointerdown', event => {
  if (game.state === 'playing' && (event.button === 0 || event.button === 2)) {
    game.cameraRig.dragging = false;
  }
}, true);

// Continuous work needs stronger semantics than a one-frame interaction. A
// click on Prep/Sink creates a persistent service action; this post-player pass
// guarantees that action advances once every simulation frame even if an input
// device reports a transient axis/button state. It also ends the action as soon
// as the work state is complete, preventing the next frame from picking the
// finished item straight back up.
const baseUpdateStations = game.updateStations.bind(game);
game.updateStations = function updateStationsSeniorV802(dt) {
  const p1 = this.players?.[0];
  const action = this.__seniorV8?.mouse?.action;
  if (this.state === 'playing' && p1?.human && action?.mode === 'smart' && action.target) {
    const target = action.target;
    const pos = target.pos || target.group?.position;
    const distance = pos ? Math.hypot(p1.group.position.x - pos.x, p1.group.position.z - pos.z) : Infinity;
    if (distance <= 2.08 && (target.type === 'prep' || target.type === 'sink')) {
      const before = target.type === 'prep'
        ? `${p1.held?.kind || ''}|${target.slot?.kind || ''}|${target.slot?.state || ''}|${target.progress || 0}`
        : `${p1.held?.dirty || false}|${target.slot?.dirty || false}|${target.progress || 0}`;

      if (target.type === 'prep') {
        if (!target.slot && p1.held && !p1.held.isPlate) this.interact(p1, target, dt, true);
        else if (target.slot?.state === 'raw') this.interact(p1, target, dt, true);
      } else if (target.type === 'sink') {
        if (!target.slot && p1.held?.isPlate && p1.held.dirty) this.interact(p1, target, dt, true);
        else if (target.slot?.dirty) this.interact(p1, target, dt, true);
      }

      const finished = target.type === 'prep'
        ? !!target.slot && target.slot.state !== 'raw'
        : !!target.slot && !target.slot.dirty;
      const after = target.type === 'prep'
        ? `${p1.held?.kind || ''}|${target.slot?.kind || ''}|${target.slot?.state || ''}|${target.progress || 0}`
        : `${p1.held?.dirty || false}|${target.slot?.dirty || false}|${target.progress || 0}`;
      if (before !== after) this.qaRecord('v8-continuous-work', { target: target.type, before, after });
      if (finished) this.__seniorV8.mouse.action = null;
    }
  }
  return baseUpdateStations(dt);
};

// Keep the stable external hotfix identifier used by the deterministic test while
// exposing the actual patch level separately for diagnostics.
game.__seniorV8.hotfix = '8.0.1-input-overlay';
game.__seniorV8.patchLevel = '8.0.2-continuous-work';
console.info('Senior V8.0.2 active: service HUD cannot block clicks and smart Prep/Sink work persists deterministically.');
