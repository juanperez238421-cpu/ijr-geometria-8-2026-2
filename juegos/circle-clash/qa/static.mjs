import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const index = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');
const arenaCss = fs.readFileSync(path.join(root, 'arena-v2.css'), 'utf8');

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
check('HTML declares interactive 2.5D arena', index.includes('ARENA 2.5D') && index.includes('id="battlefield"'));
check('HTML has keyboard/touch movement controls', index.includes('data-move="up"') && index.includes('data-move="left"') && index.includes('data-move="right"'));
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
check('Combat events animate attacks', app.includes('animateCombatEvents') && app.includes('projectile'));
check('No service-role secret in frontend', !app.toLowerCase().includes('service_role'));
check('No Three.js dependency', !index.toLowerCase().includes('three.js') && !app.toLowerCase().includes('three.js'));
check('No WebGL dependency', !index.toLowerCase().includes('webgl') && !app.toLowerCase().includes('webgl'));
check('No canvas game loop', !index.toLowerCase().includes('<canvas'));
check('Base CSS has mobile breakpoint', css.includes('@media(max-width:760px)'));
check('Arena CSS has mobile breakpoint', arenaCss.includes('@media(max-width:760px)'));
check('Arena CSS supports reduced motion', arenaCss.includes('prefers-reduced-motion'));
check('Question UI includes circle formulas', index.includes('A = πr²') && index.includes('C = πd'));

console.log(`\nCircle Clash static QA: ${checks.length}/${checks.length} PASS`);
