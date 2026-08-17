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

// The base renderer caps simulation dt for physics safety. On machines where
// WebGL falls below ~25 FPS that cap made human chefs feel artificially slow.
// Wrap each human controller with a separate wall-clock movement/work delta,
// capped at 100 ms to remain stable while preserving real-world responsiveness.
const baseSpawnPlayersV8 = game.spawnPlayers.bind(game);
game.spawnPlayers = function spawnPlayersSeniorV804() {
  baseSpawnPlayersV8();
  for (const player of this.players) {
    if (!player.human || player.__v8LowFpsWrapped) continue;
    player.__v8LowFpsWrapped = true;
    const baseHuman = player.updateHuman.bind(player);
    let last = performance.now();
    player.updateHuman = function updateHumanLowFps(dt, input) {
      const now = performance.now();
      const wallDt = Math.min(.10, Math.max(.001, (now - last) / 1000));
      last = now;
      return baseHuman(Math.max(dt, wallDt), input);
    };
  }
};

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
// human movement/interaction. Smart clicks therefore have persistent work
// semantics instead of behaving like a one-frame key press.
const baseUpdateStations = game.updateStations.bind(game);
game.updateStations = function updateStationsSeniorV804(dt) {
  const action = this.__seniorV8?.mouse?.action;
  if (this.state === 'playing' && action?.mode === 'smart') advanceContinuousWork(this.players?.[0], action, dt, 'simulation');
  return baseUpdateStations(dt);
};

// Watchdog fallback: embedded launchers/browsers may briefly throttle animation
// frames after pointer events. If Prep/Sink state has not changed across two
// samples, advance a deterministic work tick. Normal 60-FPS play is unaffected.
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

// Keep the stable external identifier used by existing V8 QA while exposing the
// actual patch level separately for diagnostics.
game.__seniorV8.hotfix = '8.0.1-input-overlay';
game.__seniorV8.patchLevel = '8.0.4-responsive-continuous-work';
console.info('Senior V8.0.4 active: reliable mouse ownership, low-FPS human response and deterministic Prep/Sink work.');
