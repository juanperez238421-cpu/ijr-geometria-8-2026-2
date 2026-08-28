import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const index = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');
const arenaCss = fs.readFileSync(path.join(root, 'arena-v2.css'), 'utf8');
const threeArena = fs.readFileSync(path.join(root, 'three-arena.js'), 'utf8');
const threeCss = fs.readFileSync(path.join(root, 'three-arena.css'), 'utf8');
const cadPython = fs.readFileSync(path.join(root, 'cad', 'arena_spec.py'), 'utf8');

const checks = [];
function check(name, condition) {
  checks.push({ name, ok: Boolean(condition) });
  if (!condition) throw new Error(`FAIL: ${name}`);
  console.log(`PASS: ${name}`);
}

check('HTML has join form', index.includes('id="joinForm"'));
check('HTML has answer options container', index.includes('id="optionsGrid"'));
check('HTML has battle panel', index.includes('id="attackPanel"'));
check('HTML has live leaderboard', index.includes('id="leaderboard"'));
check('HTML has connection state badge', index.includes('id="connectionBadge"'));
check('HTML declares full 3D Three.js arena', index.includes('ARENA 3D') && index.includes('THREE.JS') && index.includes('id="battlefield"'));
check('HTML loads dedicated 3D stylesheet', index.includes('three-arena.css'));
check('HTML loads dedicated 3D module', index.includes('three-arena.js'));
check('HTML retains keyboard/touch movement controls', index.includes('data-move="up"') && index.includes('data-move="left"') && index.includes('data-move="right"'));
check('HTML exposes 3D camera controls', index.includes('arrastrar cámara') && index.includes('Wheel') && index.includes('fijar rival'));
check('Hidden UI state cannot be overridden by component display rules', index.includes('[hidden]{display:none!important}'));
check('Game screen starts hidden', /id="gameScreen"[^>]*hidden/.test(index));
check('Final overlay starts hidden', /id="finalOverlay"[^>]*hidden/.test(index));
check('Attack panel starts hidden', /id="attackPanel"[^>]*hidden/.test(index));
check('Frontend points to Circle Clash Edge Function', app.includes('/functions/v1/geo8-circle-clash'));
check('Frontend persists reconnect session', app.includes('geo8-circle-clash-session-v1'));
check('Frontend uses idempotent UUID event IDs', app.includes('client_event_id') && app.includes('crypto.randomUUID'));
check('Frontend uses high-entropy team token', app.includes('randomHex(48)'));
check('Frontend has retry/timeout handling', app.includes('AbortController') && app.includes('retries'));
check('Frontend resumes on online event', app.includes('window.addEventListener("online"'));
check('Frontend resynchronizes when tab returns', app.includes('visibilitychange'));
check('Frontend synchronizes authoritative movement', app.includes('action:"move"') && app.includes('arena_x') && app.includes('arena_y'));
check('Frontend supports WASD and arrow keys', app.includes('ArrowUp') && app.includes('ArrowLeft') && app.includes('movementStep'));
check('Frontend supports click-to-target opponents', app.includes('selectTarget') && app.includes('selectedTargetId'));
check('Authoritative combat events remain enabled', app.includes('animateCombatEvents') && app.includes('projectile'));
check('Three.js version is pinned and has CDN fallback', threeArena.includes('three@0.180.0') && threeArena.includes('cdn.jsdelivr.net') && threeArena.includes('unpkg.com'));
check('3D renderer uses WebGLRenderer and PerspectiveCamera', threeArena.includes('new THREE.WebGLRenderer') && threeArena.includes('new THREE.PerspectiveCamera'));
check('3D arena uses raycasting for direct player targeting', threeArena.includes('new THREE.Raycaster') && threeArena.includes('intersectObjects'));
check('3D scene contains CAD-like parametric geometry', threeArena.includes('THREE.GridHelper') && threeArena.includes('TorusGeometry') && threeArena.includes('CircleGeometry'));
check('3D scene bridges authoritative DOM multiplayer positions', threeArena.includes('worldFromAvatar') && threeArena.includes('#avatarLayer .arena-avatar'));
check('3D scene animates authoritative combat projectiles', threeArena.includes('inferProjectile') && threeArena.includes('spawnProjectile'));
check('3D scene adapts rendering load to device capability', threeArena.includes('navigator.deviceMemory') && threeArena.includes('navigator.hardwareConcurrency') && threeArena.includes('adaptivePixelRatio'));
check('3D scene handles WebGL context loss', threeArena.includes('webglcontextlost') && threeArena.includes('webglcontextrestored'));
check('3D scene uses ResizeObserver for responsive stability', threeArena.includes('new ResizeObserver'));
check('3D scene preserves a 2.5D fallback', threeArena.includes('three-fallback') && threeArena.includes('failGracefully'));
check('3D CSS keeps fallback layers available until renderer is ready', threeCss.includes('.battlefield.three-ready') && threeCss.includes('.battlefield.three-fallback'));
check('Base CSS has mobile breakpoint', css.includes('@media(max-width:760px)'));
check('Arena CSS has mobile breakpoint', arenaCss.includes('@media(max-width:760px)'));
check('3D CSS has mobile breakpoint', threeCss.includes('@media(max-width:760px)'));
check('3D CSS supports reduced motion', threeCss.includes('prefers-reduced-motion'));
check('Question UI includes circle formulas', index.includes('A = πr²') && index.includes('C = πd'));
check('Python CAD specification exposes parametric circle geometry', cadPython.includes('class ArenaSpec') && cadPython.includes('playable_circumference') && cadPython.includes('playable_area'));
check('No service-role secret in browser frontend', !(app + threeArena).toLowerCase().includes('service_role'));

console.log(`\nCircle Clash 3D static QA: ${checks.length}/${checks.length} PASS`);
