import * as THREE from 'three';
import './game.js';

const game = window.__rkrGame;
if (!game) throw new Error('Robledo Kitchen Rush game instance was not created before Controls V7.');
if (game.__controlsV7) throw new Error('Controls V7 loaded twice.');

const INTERACT_RANGE = 1.88;
const SELECT_RANGE = 3.25;
const COLORS = [0xe34f51, 0x4387db, 0xf2bd3f];
const mouse = {
  rightDown: false,
  moveTarget: null,
  selectedTarget: null,
  lastPointer: { x: 0, y: 0 },
};

const distanceXZ = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
const pointOf = target => target?.pos || target?.group?.position || null;
const validTarget = target => !!target && !target.dead && (!target.group || target.group.parent || target.type === 'storage' || target.type === 'table');
const labelOf = target => {
  if (!target) return 'NONE';
  if (target.type === 'storage') return `${String(target.kind).toUpperCase()} • GROCERY`;
  if (target.type === 'table') return `TABLE ${target.id + 1}`;
  if (typeof target.description === 'function') return target.description().toUpperCase();
  return String(target.type || target.kind || 'TARGET').toUpperCase();
};

function heldByPlayerNear(pos) {
  return game.players.find(p => p.held && distanceXZ(p.group.position, pos) < 0.12)?.held || null;
}

// Critical human-interaction regression fix: a carried ingredient used to be the
// nearest WorldItem, so humans would repeatedly interact with their own held item
// instead of the prep board, stove, counter, sink, table, or grocery fixture.
game.nearestInteractable = function nearestInteractableV7(pos, range) {
  let best = null;
  let bestDistance = range;
  const held = heldByPlayerNear(pos);
  for (const station of this.stations) {
    const d = distanceXZ(pos, station.pos);
    if (d < bestDistance) { best = station; bestDistance = d; }
  }
  for (const table of this.tables) {
    const d = distanceXZ(pos, table.pos);
    if (d < bestDistance) { best = table; bestDistance = d; }
  }
  for (const item of this.items) {
    if (item === held || item.dead || item.airborne || item.onSurface) continue;
    const d = distanceXZ(pos, item.group.position);
    if (d < bestDistance) { best = item; bestDistance = d; }
  }
  return best;
};

function targetsFor(player, range = SELECT_RANGE) {
  const pos = player.group.position;
  const out = [];
  for (const station of game.stations) {
    if (distanceXZ(pos, station.pos) <= range) out.push(station);
  }
  for (const table of game.tables) {
    if (distanceXZ(pos, table.pos) <= range) out.push(table);
  }
  for (const item of game.items) {
    if (item === player.held || item.dead || item.airborne || item.onSurface) continue;
    if (distanceXZ(pos, item.group.position) <= range) out.push(item);
  }
  out.sort((a, b) => distanceXZ(pos, pointOf(a)) - distanceXZ(pos, pointOf(b)));
  return out;
}

function targetStillExists(target) {
  if (!validTarget(target)) return false;
  if (target.type === 'table') return game.tables.includes(target);
  if (target.type === 'storage' || target.type) {
    if (game.stations.includes(target)) return true;
    if (target.type === 'table') return game.tables.includes(target);
  }
  if (game.items.includes(target)) return true;
  return false;
}

function selectTarget(player, target) {
  player.selectedTarget = target || null;
  if (player.index === 0) mouse.selectedTarget = player.selectedTarget;
  const ring = player.__v7SelectionRing;
  if (!ring) return;
  if (!target) { ring.visible = false; return; }
  const p = pointOf(target);
  if (!p) { ring.visible = false; return; }
  ring.position.set(p.x, 0.065, p.z);
  ring.visible = true;
}

function cycleNearest(player) {
  const candidates = targetsFor(player);
  if (!candidates.length) { selectTarget(player, null); return; }
  const current = candidates.indexOf(player.selectedTarget);
  selectTarget(player, candidates[(current + 1) % candidates.length]);
}

function makeSelectionRing(player) {
  const geo = new THREE.RingGeometry(0.46, 0.58, 32);
  const material = new THREE.MeshBasicMaterial({ color: COLORS[player.index], transparent: true, opacity: 0.9, side: THREE.DoubleSide, depthTest: false });
  const ring = new THREE.Mesh(geo, material);
  ring.rotation.x = -Math.PI / 2;
  ring.visible = false;
  ring.renderOrder = 100;
  game.scene.add(ring);
  player.__v7SelectionRing = ring;
}

function updateSelectionRing(player) {
  const target = player.selectedTarget;
  if (!targetStillExists(target)) {
    selectTarget(player, null);
    return;
  }
  const p = pointOf(target);
  if (!p || !player.__v7SelectionRing) return;
  player.__v7SelectionRing.position.set(p.x, 0.065, p.z);
  player.__v7SelectionRing.visible = true;
}

function keyboardState(index) {
  const keys = game.input.keys;
  const gp = game.input.pollGamepad(index);
  const map = index === 1
    ? { up:'KeyW', down:'KeyS', left:'KeyA', right:'KeyD', interact:'KeyE', select:'KeyF', throw:'KeyQ', dash:'ShiftLeft' }
    : { up:'ArrowUp', down:'ArrowDown', left:'ArrowLeft', right:'ArrowRight', interact:'Enter', select:'Period', throw:'Slash', dash:'ShiftRight' };
  let x = (keys.has(map.right) ? 1 : 0) - (keys.has(map.left) ? 1 : 0);
  let y = (keys.has(map.down) ? 1 : 0) - (keys.has(map.up) ? 1 : 0);
  if (gp && Math.abs(gp.x) + Math.abs(gp.y) > 0.05) { x = gp.x; y = gp.y; }
  return {
    x, y,
    interact: keys.has(map.interact) || !!gp?.interact,
    select: keys.has(map.select) || !!gp?.select,
    throw: keys.has(map.throw) || !!gp?.throw,
    dash: keys.has(map.dash) || !!gp?.dash,
  };
}

const originalInputState = game.input.state.bind(game.input);
game.input.state = function stateV7(index) {
  if (index === 0) {
    const gp = this.pollGamepad(0);
    return {
      x: gp?.x || 0,
      y: gp?.y || 0,
      interact: mouse.rightDown || !!gp?.interact,
      select: false,
      throw: false,
      dash: !!gp?.dash,
    };
  }
  if (index === 1 || index === 2) return keyboardState(index);
  return originalInputState(index);
};

function installHumanController(player) {
  if (!player.human || player.__v7Installed) return;
  player.__v7Installed = true;
  player.prevSelect = false;
  player.prevInteract = false;
  player.prevThrow = false;
  makeSelectionRing(player);

  player.updateHuman = function updateHumanV7(dt, input) {
    this.dashCooldown = Math.max(0, this.dashCooldown - dt);
    let dx = input.x || 0;
    let dz = input.y || 0;

    if (this.index === 0 && (!dx && !dz) && mouse.moveTarget) {
      const movePoint = this.selectedTarget && targetStillExists(this.selectedTarget) ? pointOf(this.selectedTarget) : mouse.moveTarget;
      if (movePoint) {
        const v = new THREE.Vector3(movePoint.x - this.group.position.x, 0, movePoint.z - this.group.position.z);
        const stop = this.selectedTarget ? INTERACT_RANGE - 0.08 : 0.16;
        if (v.length() > stop) {
          v.normalize();
          dx = v.x;
          dz = v.z;
        } else if (!this.selectedTarget) {
          mouse.moveTarget = null;
        }
      }
    }

    const len = Math.hypot(dx, dz);
    if (len > 0.001) {
      dx /= Math.max(1, len);
      dz /= Math.max(1, len);
      this.facing.set(dx, 0, dz);
      this.group.rotation.y = Math.atan2(dx, dz);
    }
    const boost = input.dash && this.dashCooldown <= 0 ? 1.72 : 1;
    if (boost > 1) this.dashCooldown = 0.2;
    game.moveCrew(this, new THREE.Vector3(dx, 0, dz).multiplyScalar(this.speed * boost * dt));
    this.animate(dt, len > 0.05, boost);

    if (input.select && !this.prevSelect) cycleNearest(this);
    this.prevSelect = !!input.select;

    if (input.throw && !this.prevThrow) this.throwItem();
    this.prevThrow = !!input.throw;

    let target = this.selectedTarget;
    if (!targetStillExists(target) || !pointOf(target) || distanceXZ(this.group.position, pointOf(target)) > INTERACT_RANGE) {
      target = game.nearestInteractable(this.group.position, INTERACT_RANGE);
    }

    // Prep and sink are true hold-to-work stations. Every other station is edge
    // triggered, which prevents plate racks/counters/cookers from immediately
    // undoing the interaction on the very next frame while the button is held.
    const continuousWork = target && (target.type === 'prep' || target.type === 'sink');
    const shouldInteract = !!input.interact && !!target && (continuousWork || !this.prevInteract);
    if (shouldInteract) game.interact(this, target, dt, true);
    this.prevInteract = !!input.interact;
    updateSelectionRing(this);
  };
}

function installAllHumans() {
  for (const player of game.players) installHumanController(player);
}

const originalSpawnPlayers = game.spawnPlayers.bind(game);
game.spawnPlayers = function spawnPlayersV7() {
  originalSpawnPlayers();
  installAllHumans();
};

function belongsTo(object, group) {
  for (let node = object; node; node = node.parent) if (node === group) return true;
  return false;
}

function pointerNdc(event) {
  const rect = game.canvas.getBoundingClientRect();
  return new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -(((event.clientY - rect.top) / rect.height) * 2 - 1),
  );
}

function targetFromPointer(event, player) {
  game.raycaster.setFromCamera(pointerNdc(event), game.camera);
  const roots = [...game.fixtureRoot.children, ...game.itemRoot.children];
  const hits = game.raycaster.intersectObjects(roots, true);
  for (const hit of hits) {
    const item = game.items.find(i => i !== player.held && !i.dead && belongsTo(hit.object, i.group));
    if (item) return item;
    const table = game.tables.find(t => belongsTo(hit.object, t.group));
    if (table) return table;
    const stations = game.stations.filter(s => belongsTo(hit.object, s.group));
    if (stations.length) {
      stations.sort((a, b) => hit.point.distanceToSquared(a.pos) - hit.point.distanceToSquared(b.pos));
      return stations[0];
    }
  }
  return null;
}

function floorFromPointer(event) {
  game.raycaster.setFromCamera(pointerNdc(event), game.camera);
  const point = new THREE.Vector3();
  return game.raycaster.ray.intersectPlane(game.floorPlane, point) ? point : null;
}

// Service mode mouse ownership for Player 1. Build mode intentionally keeps the
// existing left-click placement and right-drag camera behavior.
game.canvas.addEventListener('pointerdown', event => {
  if (game.state !== 'playing') return;
  const p1 = game.players[0];
  if (!p1?.human) return;
  mouse.lastPointer = { x: event.clientX, y: event.clientY };

  if (event.button === 0) {
    const target = targetFromPointer(event, p1);
    if (target) {
      selectTarget(p1, target);
      mouse.moveTarget = pointOf(target)?.clone?.() || pointOf(target);
      game.flash(`P1 selected ${labelOf(target)} — RIGHT CLICK / HOLD TO INTERACT`);
    } else {
      selectTarget(p1, null);
      const floor = floorFromPointer(event);
      if (floor) mouse.moveTarget = floor.clone();
    }
    event.preventDefault();
    event.stopImmediatePropagation();
  }

  if (event.button === 2) {
    const target = targetFromPointer(event, p1);
    if (target) {
      selectTarget(p1, target);
      mouse.moveTarget = pointOf(target)?.clone?.() || pointOf(target);
    } else if (!p1.selectedTarget) {
      selectTarget(p1, game.nearestInteractable(p1.group.position, SELECT_RANGE));
    }
    mouse.rightDown = true;
    game.cameraRig.dragging = false;
    event.preventDefault();
    event.stopImmediatePropagation();
  }

  if (event.button === 1) {
    if (p1.held) p1.throwItem();
    event.preventDefault();
    event.stopImmediatePropagation();
  }
}, true);

game.canvas.addEventListener('pointerup', event => {
  if (game.state !== 'playing') return;
  if (event.button === 2) {
    mouse.rightDown = false;
    game.cameraRig.dragging = false;
    event.preventDefault();
    event.stopImmediatePropagation();
  }
}, true);

game.canvas.addEventListener('pointercancel', () => { mouse.rightDown = false; game.cameraRig.dragging = false; }, true);
game.canvas.addEventListener('mouseleave', () => { mouse.rightDown = false; game.cameraRig.dragging = false; }, true);

// Keep the controls visible and unambiguous in every screen generated by V6.
function refreshControlCopy() {
  const cards = document.querySelectorAll('#controls-screen .controls-grid article');
  if (cards[0]) cards[0].innerHTML = '<h3>PLAYER 1 • MOUSE</h3><p><b>Move / select:</b> Left click floor or object<br/><b>Interact / work:</b> Right click / hold<br/><b>Throw:</b> Middle click<br/><b>Camera:</b> C presets + wheel zoom</p>';
  if (cards[1]) cards[1].innerHTML = '<h3>PLAYER 2 • KEYBOARD</h3><p><b>Move:</b> WASD<br/><b>Select / cycle target:</b> F<br/><b>Interact / work:</b> E<br/><b>Throw:</b> Q • <b>Dash:</b> Left Shift</p>';
  if (cards[2]) cards[2].innerHTML = '<h3>PLAYER 3 • KEYBOARD</h3><p><b>Move:</b> Arrow keys<br/><b>Select / cycle target:</b> . (Period)<br/><b>Interact / work:</b> Enter<br/><b>Throw:</b> / • <b>Dash:</b> Right Shift</p>';
  if (cards[3]) cards[3].innerHTML = '<h3>CAMERA</h3><p><b>Service:</b> C cycles presets • Home resets • wheel zoom<br/><b>Build mode:</b> right mouse drag orbits camera<br/><b>P1 right mouse:</b> reserved for interaction during service</p>';
}
refreshControlCopy();

const originalRenderCrewSetup = game.renderCrewSetup.bind(game);
game.renderCrewSetup = function renderCrewSetupV7() {
  originalRenderCrewSetup();
  const lines = document.querySelectorAll('#crew-slots .device-line');
  const copy = [
    '🖱 P1 • Left click move/select • Right click/hold interact',
    '⌨ P2 • WASD • F select • E interact • Q throw',
    '⌨ P3 • Arrows • . select • Enter interact • / throw',
  ];
  lines.forEach((line, i) => {
    const human = i < game.config.humanCount;
    if (human && !navigator.getGamepads?.()[i]) line.textContent = copy[i];
  });
};

const originalRenderTutorial = game.renderTutorial.bind(game);
game.renderTutorial = function renderTutorialV7() {
  originalRenderTutorial();
  if (document.getElementById('tutorial-title')?.textContent === 'Move, interact and throw') {
    document.getElementById('tutorial-visual').innerHTML = '<div class="keys"><kbd>P1 🖱 LEFT</kbd><kbd>P1 🖱 RIGHT</kbd><kbd>P2 WASD/F/E</kbd><kbd>P3 ↑↓←→/./ENTER</kbd></div>';
    document.getElementById('tutorial-body').textContent = 'P1 uses left click to move/select and right click or hold to interact/work. P2 uses WASD, F to select, E to interact. P3 uses arrow keys, Period to select, Enter to interact. Prep boards and sinks support hold-to-work; other fixtures use one deliberate interaction per press.';
  }
};

const originalUpdateUI = game.updateUI.bind(game);
game.updateUI = function updateUIV7() {
  originalUpdateUI();
  for (const p of game.players) {
    if (!p.human) continue;
    const el = document.getElementById(`p${p.index + 1}-held`);
    if (!el) continue;
    const held = p.held ? p.held.description() : 'empty hands';
    const target = p.selectedTarget && targetStillExists(p.selectedTarget) ? ` • TARGET: ${labelOf(p.selectedTarget)}` : '';
    el.textContent = `${held}${target}`;
  }
};

installAllHumans();
game.__controlsV7 = {
  version: '7.0.0',
  mouse,
  interactRange: INTERACT_RANGE,
  selectRange: SELECT_RANGE,
  installAllHumans,
  selectTarget,
  cycleNearest,
  targetFromPointer,
  floorFromPointer,
};

console.info('Robledo Kitchen Rush Controls V7 active: P1 mouse, P2 WASD/F/E, P3 arrows/Period/Enter.');
