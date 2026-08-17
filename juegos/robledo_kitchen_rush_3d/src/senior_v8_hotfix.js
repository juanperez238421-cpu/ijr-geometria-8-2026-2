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

game.__seniorV8.hotfix = '8.0.1-input-overlay';
console.info('Senior V8.0.1 input overlay hotfix active: service HUD cannot block kitchen clicks.');
