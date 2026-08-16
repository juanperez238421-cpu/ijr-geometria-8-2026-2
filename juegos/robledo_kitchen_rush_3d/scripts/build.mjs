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

const standalone = path.join(dist, 'Robledo_Kitchen_Rush_3D_DYNAMIC_V4_OFFLINE.html');
await writeFile(standalone, html, 'utf8');
// Keep canonical aliases for launcher/CI compatibility.
await copyFile(standalone, path.join(dist, 'Robledo_Kitchen_Rush_3D_OFFLINE.html'));
await copyFile(standalone, path.join(dist, 'index.html'));
await rm(path.join(dist, 'game.bundle.js'), { force: true });

await writeFile(path.join(dist, 'README_FIRST.txt'), `ROBLEDO KITCHEN RUSH 3D — SENIOR DYNAMIC V4\n\nRECOMMENDED ON WINDOWS\n1. Extract the complete ZIP before playing.\n2. Open PLAY/RobledoKitchenRush3D_Windows.exe.\n3. The launcher starts a private server only on 127.0.0.1 and opens the game in your default browser.\n4. Keep the launcher running while the game tab is open. Everything remains local/offline.\n\nNEW SHIFT FLOW\n1. Choose 1, 2 or 3 human players.\n2. Every unused crew slot becomes an autonomous bot.\n3. Assign Head Chef, Prep Specialist or Service Captain to all three crew members.\n4. Select 3–5 dishes for the active menu.\n5. Complete or skip the seven-step control/mechanics tutorial.\n6. Build the restaurant from the starting budget: place tables, ingredient crates, preparation/cooking stations, sink, plates, trash and counters.\n7. Open the restaurant and run the real-time service.\n\nBUILD MODE\nLeft click: place selected fixture\nRight mouse drag: orbit camera\nMouse wheel: zoom\nR: rotate fixture\nDelete: remove highlighted fixture and refund its cost\nRecommended Layout: instantly creates a valid editable starter kitchen\n\nCAMERA\nDynamic mode follows the crew centroid and adds a subtle gyroscope-style lean.\nRight mouse drag: orbit\nMouse wheel: zoom\nC: cycle Dynamic / Classic / Top presets\nHome: reset camera\n\nHUMAN CONTROLS\nP1: WASD / E interact / Q throw / Left Shift dash\nP2: Arrows / Enter interact / Slash throw / Right Shift dash\nP3: IJKL / O interact / U throw / P dash\nGamepads: left stick / A interact / X throw / B dash. One controller per human is recommended.\n\nROLES\nHead Chef: faster hot-station work and larger burn window.\nPrep Specialist: much faster chopping and slightly faster movement.\nService Captain: faster movement/washing and better service tips.\n\nCOOKING LOOP\nCustomers enter -> sit -> browse the selected menu -> order -> wait.\nIngredients -> prep -> cook/fry/bake -> assemble on plate -> deliver to correct table -> collect dirty dishes -> sink.\nBots physically move through your installed kitchen and complete role-biased cooking/cleaning task chains.\n\nHTML FALLBACK\nRobledo_Kitchen_Rush_3D_DYNAMIC_V4_OFFLINE.html is fully standalone. Direct file:// execution can be restricted by managed browsers, so the Windows launcher is the preferred entry point.\n`);

console.log(`Built ${standalone}`);
