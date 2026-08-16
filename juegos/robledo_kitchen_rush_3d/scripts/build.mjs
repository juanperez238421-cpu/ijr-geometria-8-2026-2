import { build } from 'esbuild';
import { readFile, writeFile, mkdir, rm, copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const dist = path.join(root, 'dist');
await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

await build({
  entryPoints: [path.join(root, 'src/game.js')],
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

// The native portable launcher serves the complete build on 127.0.0.1. A tiny
// heartbeat lets the launcher shut down after the browser tab is closed without
// adding another external runtime dependency or script tag.
const portableHeartbeat = `if(location.hostname==='127.0.0.1'&&new URLSearchParams(location.search).get('portable')==='1'){const __rkrHeartbeat=()=>fetch('/__heartbeat',{method:'POST',cache:'no-store'}).catch(()=>{});__rkrHeartbeat();setInterval(__rkrHeartbeat,10000);}`;
const js = portableHeartbeat + bundledGame;

// Callback replacements insert minified bytes literally. Using replacement
// strings here could reinterpret valid "$&" byte sequences inside Three.js.
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

const standalone = path.join(dist, 'Robledo_Kitchen_Rush_3D_AUTONOMOUS_V6_OFFLINE.html');
await writeFile(standalone, html, 'utf8');
// Keep canonical aliases for launcher/CI compatibility.
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'index.html'));
await rm(path.join(dist, 'game.bundle.js'), { force: true });

await writeFile(path.join(dist, 'README_FIRST.txt'), `ROBLEDO KITCHEN RUSH 3D — SENIOR AUTONOMOUS SERVICE V6

RECOMMENDED ON WINDOWS
1. Extract the complete ZIP before playing.
2. Open PLAY/RobledoKitchenRush3D_AutonomousV6_Windows.exe.
3. The launcher serves the complete game only on 127.0.0.1 and opens it in your browser. Everything remains local/offline.

PROGRESSIVE BUSINESS LOOP
- Start in a compact Starter Bistro with only 2 tables, 2 active customer parties and 2 menu recipes.
- Business cash persists between shifts. Tables, counters, production stations and the grocery market/freezer wall are permanent investments.
- Customer satisfaction persists and is required together with cash to expand.
- Expansion tiers unlock more floor area, higher table/customer limits, duplicate kitchen stations and more recipes/menu slots.
- A crew member must take each customer order. The 30-second fast-service clock starts only after the order is taken.
- Bots physically collect groceries, prep, cook, assemble, serve and clean through the same live station logic as humans.
- Walkouts cost one life, reduce satisfaction and impose a small cash penalty.

BUILD MODE
Left click: place selected unlocked fixture
Right mouse drag: orbit camera
Mouse wheel: zoom
R: rotate fixture
Delete: remove highlighted fixture and refund its purchase cost
Recommended Layout: creates a compact valid layout for the current restaurant tier
Expand Restaurant: available only when both the cash and satisfaction requirements are met

HUMAN CONTROLS
P1: WASD / E interact / Q throw / Left Shift dash
P2: Arrows / Enter interact / Slash throw / Right Shift dash
P3: IJKL / O interact / U throw / P dash
Gamepads: left stick / A interact / X throw / B dash

CAMERA
Right mouse drag: orbit
Mouse wheel: zoom
C: cycle Dynamic / Classic / Top
Home: reset
The camera distance scales with restaurant expansion so the starter bistro stays readable and later restaurants fit naturally.

HTML FALLBACK
Robledo_Kitchen_Rush_3D_AUTONOMOUS_V6_OFFLINE.html is fully standalone. Managed browsers can restrict file:// pages, so the Windows launcher is preferred.
`);

console.log(`Built ${standalone}`);
