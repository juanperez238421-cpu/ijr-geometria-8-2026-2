import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const index = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');

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
check('HTML declares 2D arena', index.includes('ARENA 2D'));
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
check('No service-role secret in frontend', !app.toLowerCase().includes('service_role'));
check('No Three.js dependency', !index.toLowerCase().includes('three.js') && !app.toLowerCase().includes('three.js'));
check('No WebGL dependency', !index.toLowerCase().includes('webgl') && !app.toLowerCase().includes('webgl'));
check('No canvas game loop', !index.toLowerCase().includes('<canvas'));
check('CSS has mobile breakpoint', css.includes('@media(max-width:760px)'));
check('CSS supports reduced motion', css.includes('prefers-reduced-motion'));
check('Question UI includes circle formulas', index.includes('A = πr²') && index.includes('C = πd'));

console.log(`\nCircle Clash static QA: ${checks.length}/${checks.length} PASS`);
