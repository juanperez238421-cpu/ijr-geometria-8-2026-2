import { build } from 'esbuild';
import { readFile, writeFile, mkdir, rm, copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const dist = path.join(root, 'dist');
await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

// Senior V8 imports the stable production game and replaces the human-facing
// control/service layer with reliable click actions, true solo play, richer NPCs,
// character customization and additional management systems.
await build({
  entryPoints: [path.join(root, 'src/senior_v8.js')],
  bundle: true,
  format: 'iife',
  platform: 'browser',
  target: ['chrome110', 'edge110', 'firefox115'],
  minify: true,
  sourcemap: false,
  outfile: path.join(dist, 'game.bundle.js'),
  legalComments: 'none',
});

let html = await readFile(path.join(root, 'index.html'), 'utf8');
const css = await readFile(path.join(root, 'style.css'), 'utf8');
const bundledGame = await readFile(path.join(dist, 'game.bundle.js'), 'utf8');

const portableHeartbeat = `if(location.hostname==='127.0.0.1'&&new URLSearchParams(location.search).get('portable')==='1'){const __rkrHeartbeat=()=>fetch('/__heartbeat',{method:'POST',cache:'no-store'}).catch(()=>{});__rkrHeartbeat();setInterval(__rkrHeartbeat,10000);}`;
const js = portableHeartbeat + bundledGame;

html = html.replace('<link rel="stylesheet" href="./style.css" />', () => `<style>${css}</style>`);
html = html.replace('<script src="./game.js"></script>', () => `<script>${js}</script>`);

const logoPath = path.resolve(root, '../../assets/logo_colegio_transparente.png');
try {
  const logo = await readFile(logoPath);
  const data = `data:image/png;base64,${logo.toString('base64')}`;
  html = html.replaceAll('../../assets/logo_colegio_transparente.png', data);
} catch {
  console.warn('School logo not found at repository asset path; build continues with source path.');
}

const standalone = path.join(dist, 'Robledo_Kitchen_Rush_3D_SENIOR_V8_OFFLINE.html');
await writeFile(standalone, html, 'utf8');
// Canonical + legacy aliases keep old launchers/bookmarks functional.
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_INTERACTION_V7_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_AUTONOMOUS_V6_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'index.html'));
await rm(path.join(dist, 'game.bundle.js'), { force: true });

await writeFile(path.join(dist, 'README_FIRST.txt'), `ROBLEDO KITCHEN RUSH 3D — SENIOR V8

RECOMMENDED ON WINDOWS
1. Extract the complete ZIP before playing.
2. Open PLAY/RobledoKitchenRush3D_SeniorV8_Windows.exe.
3. The launcher serves the complete game only on 127.0.0.1 and opens it in your browser. Everything remains local/offline.

TRUE SOLO / LOCAL CO-OP
- 1 human player means exactly one chef. No AI cooks, waiters or cleaners are spawned.
- The solo customer cap, party size and patience are balanced so the single chef personally takes every order, collects every ingredient, cooks, serves and cleans.
- 2 or 3 human players use the same physical kitchen with no hidden AI helpers.

PLAYER 1 — MOUSE
- Left click floor: move there.
- Left click a kitchen object, table or ingredient: approach it and perform the appropriate interaction automatically.
- Right click / hold: approach and manually interact/work. Prep boards and sinks support continuous work while held.
- Middle click: throw the held item.
- During service, right mouse belongs to P1 interaction. Camera presets use C, Home and wheel zoom.

PLAYER 2 — KEYBOARD
- Move: W A S D
- Select / cycle nearby target: F
- Interact / work: E
- Throw: Q
- Dash: Left Shift

PLAYER 3 — KEYBOARD
- Move: Arrow keys
- Select / cycle nearby target: Period (.)
- Interact / work: Enter
- Throw: Slash (/)
- Dash: Right Shift

SENIOR V8 GAMEPLAY SYSTEMS
- Exact recipe routes define grocery, prep, cooking, assembly and serving steps for all six recipes.
- Contextual action card tells the player the next useful station for the held item.
- Physical ingredients have animated pickup, idle presentation, station feedback, particles and clearer state changes.
- Grocery stock is finite per shift. Empty compartments automatically restock four units for a small business cost when interacted with.
- Shift goals reward service volume, fast service and no burned food.
- Kitchen cleanliness tracks dirty tables, dirty sink plates, burned food and dropped items.
- Persistent chef XP and customer loyalty add longer-term progression.
- Regular customers can return with loyalty bonuses.
- Customers display dynamic speech/mood bubbles and stronger waiting/eating gestures.

CHARACTER PERSONALIZATION
- Name
- Gender / presentation
- Six skin tones
- Four hair styles + six hair colors
- Six uniform colors
- Six apron colors
- Body build
- Glasses, bandana, neckerchief or no accessory
- Gender never restricts hair, clothes, colors or accessories.

IMPROVED RECOMMENDED LAYOUT
- Grocery wall at the back of the kitchen.
- Sink and plate rack grouped into a cleaning zone.
- Prep/cook/assembly stations form a readable production line.
- Dining tables use wider service aisles and tier-aware spacing.

RECIPE BOOK
Open the Recipe Book to see the exact physical station path for every dish. Pin a recipe to keep its route visible on the live service board. Clicking an active order card also pins that table's next dish.

HTML FALLBACK
Robledo_Kitchen_Rush_3D_SENIOR_V8_OFFLINE.html is fully standalone. Managed browsers can restrict file:// pages, so the Windows launcher is preferred.
`);

console.log(`Built ${standalone}`);
