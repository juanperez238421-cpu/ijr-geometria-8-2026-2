import { build } from 'esbuild';
import { readFile, writeFile, mkdir, rm, copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const dist = path.join(root, 'dist');
await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

// Controls V7 imports the production V6 game first, then installs the dedicated
// three-player input/interaction layer. This keeps the proven autonomous kitchen
// mechanics untouched while fixing human station targeting and control ownership.
await build({
  entryPoints: [path.join(root, 'src/controls_v7.js')],
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

html = html.replace(
  '<link rel="stylesheet" href="./style.css" />',
  () => `<style>${css}</style>`,
);
html = html.replace(
  '<script src="./game.js"></script>',
  () => `<script>${js}</script>`,
);

const logoPath = path.resolve(root, '../../assets/logo_colegio_transparente.png');
try {
  const logo = await readFile(logoPath);
  const data = `data:image/png;base64,${logo.toString('base64')}`;
  html = html.replaceAll('../../assets/logo_colegio_transparente.png', data);
} catch {
  console.warn('School logo not found at repository asset path; build continues with source path.');
}

const standalone = path.join(dist, 'Robledo_Kitchen_Rush_3D_INTERACTION_V7_OFFLINE.html');
await writeFile(standalone, html, 'utf8');
// Canonical and legacy aliases remain available for launcher/test compatibility.
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_AUTONOMOUS_V6_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'index.html'));
await rm(path.join(dist, 'game.bundle.js'), { force: true });

await writeFile(path.join(dist, 'README_FIRST.txt'), `ROBLEDO KITCHEN RUSH 3D — INTERACTION CONTROLS V7

RECOMMENDED ON WINDOWS
1. Extract the complete ZIP before playing.
2. Open PLAY/RobledoKitchenRush3D_InteractionV7_Windows.exe.
3. The launcher serves the complete game only on 127.0.0.1 and opens it in your browser. Everything remains local/offline.

THREE HUMAN PLAYERS — DEDICATED CONTROLS
PLAYER 1 — MOUSE
- Left click on floor: move there.
- Left click on a kitchen object/table/item: select it and approach it.
- Right click / hold: interact or work with the selected/nearby object.
- Middle click: throw the held item.
- During service, right mouse belongs to P1 interaction; camera presets use C, Home and wheel zoom.

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

HUMAN INTERACTION FIXES
- A carried ingredient/plate is excluded from nearest-target detection, so holding food no longer blocks interaction with counters, prep boards, stove, fryer, oven, sink, grocery compartments or tables.
- Prep boards and sinks are true hold-to-work stations.
- Plate rack, counter, grocery, table and cooking stations are edge-triggered: one deliberate press/click performs one action. Holding the button no longer immediately undoes the previous action.
- Every human player has a visible selection ring and HUD target label.
- P1 can click a fixture from a distance and will approach until it is inside the interaction radius.

AUTONOMOUS SERVICE V6 SYSTEMS RETAINED
- Grocery Market + Freezer with real ingredient compartments.
- Autonomous waiter takes orders.
- Bots collect groceries, prep, cook, assemble, serve and clean through physical stations.
- Progressive restaurant expansion, persistent cash/satisfaction, Fast Service life restoration and Geometry Rescue.

BUILD MODE
- Left click: place selected fixture.
- Right mouse drag: orbit camera.
- Mouse wheel: zoom.
- R: rotate fixture.
- Delete: remove highlighted fixture and refund its purchase cost.
- Recommended Layout: creates a compact valid layout for the current restaurant tier.

HTML FALLBACK
Robledo_Kitchen_Rush_3D_INTERACTION_V7_OFFLINE.html is fully standalone. Managed browsers can restrict file:// pages, so the Windows launcher is preferred.
`);

console.log(`Built ${standalone}`);
