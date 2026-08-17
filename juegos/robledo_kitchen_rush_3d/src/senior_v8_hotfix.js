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
  if (game.state === 'playing' && (event.button === 0 || event.button === 2)) game.cameraRig.dragging = false;
}, true);

function continuousSnapshot(player, target) {
  if (target?.type === 'prep') return `${player?.held?.kind || ''}|${target.slot?.kind || ''}|${target.slot?.state || ''}|${Number(target.progress || 0).toFixed(4)}`;
  if (target?.type === 'sink') return `${player?.held?.dirty || false}|${target.slot?.dirty || false}|${Number(target.progress || 0).toFixed(4)}`;
  return '';
}

function continuousFinished(target) {
  if (target?.type === 'prep') return !!target.slot && target.slot.state !== 'raw';
  if (target?.type === 'sink') return !!target.slot && !target.slot.dirty;
  return true;
}

function advanceContinuousWork(player, action, dt, source) {
  const target = action?.target;
  if (!player?.human || !target || !['prep','sink'].includes(target.type)) return false;
  const pos = target.pos || target.group?.position;
  const distance = pos ? Math.hypot(player.group.position.x - pos.x, player.group.position.z - pos.z) : Infinity;
  if (distance > 2.08) return false;

  const before = continuousSnapshot(player, target);
  if (target.type === 'prep') {
    if (!target.slot && player.held && !player.held.isPlate) game.interact(player, target, dt, true);
    else if (target.slot?.state === 'raw') game.interact(player, target, dt, true);
  } else {
    if (!target.slot && player.held?.isPlate && player.held.dirty) game.interact(player, target, dt, true);
    else if (target.slot?.dirty) game.interact(player, target, dt, true);
  }
  const after = continuousSnapshot(player, target);
  if (before !== after) game.qaRecord('v8-continuous-work', { target: target.type, source, before, after });
  if (continuousFinished(target)) game.__seniorV8.mouse.action = null;
  return before !== after;
}

// Primary continuous-work pass: runs in the normal simulation immediately after
// human movement/interaction. This gives smart click actions deterministic work
// semantics without relying on a key remaining pressed.
const baseUpdateStations = game.updateStations.bind(game);
game.updateStations = function updateStationsSeniorV803(dt) {
  const action = this.__seniorV8?.mouse?.action;
  if (this.state === 'playing' && action?.mode === 'smart') advanceContinuousWork(this.players?.[0], action, dt, 'simulation');
  return baseUpdateStations(dt);
};

// Watchdog fallback: some browsers/embedded launchers can briefly throttle the
// animation frame loop after a pointer event. If a smart Prep/Sink action has not
// changed state across two watchdog samples, advance one deterministic work tick.
// If the normal game loop is progressing, this does nothing and therefore does
// not double the work speed.
const continuousWatchdog = window.setInterval(() => {
  if (game.state !== 'playing') return;
  const action = game.__seniorV8?.mouse?.action;
  const p1 = game.players?.[0];
  if (!action || action.mode !== 'smart' || !['prep','sink'].includes(action.target?.type) || !p1?.human) return;
  const snapshot = continuousSnapshot(p1, action.target);
  if (action.__watchdogSnapshot === snapshot) advanceContinuousWork(p1, action, .14, 'watchdog');
  action.__watchdogSnapshot = continuousSnapshot(p1, action.target);
}, 120);

window.addEventListener('pagehide', () => window.clearInterval(continuousWatchdog), { once:true });

// Keep the stable external hotfix identifier used by existing V8 QA while
// exposing the actual patch level separately for diagnostics.
game.__seniorV8.hotfix = '8.0.1-input-overlay';
game.__seniorV8.patchLevel = '8.0.3-continuous-watchdog';
console.info('Senior V8.0.3 active: click ownership fixed and smart Prep/Sink work has a deterministic watchdog.');
