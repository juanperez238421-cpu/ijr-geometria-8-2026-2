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

// When the native portable launcher opens the game through 127.0.0.1 it expects
// a lightweight heartbeat. Keeping this inside the single embedded script avoids
// adding extra script tags and lets the launcher close after the browser tab exits.
const portableHeartbeat = `if(location.hostname==='127.0.0.1'&&new URLSearchParams(location.search).get('portable')==='1'){const __rkrHeartbeat=()=>fetch('/__heartbeat',{method:'POST',cache:'no-store'}).catch(()=>{});__rkrHeartbeat();setInterval(__rkrHeartbeat,10000);}`;
const js = portableHeartbeat + bundledGame;

// Callback replacements insert minified bytes literally. Replacement strings can
// reinterpret valid "$&" sequences from Three.js and corrupt the standalone.
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

const standalone = path.join(dist, 'Robledo_Kitchen_Rush_3D_OFFLINE.html');
await writeFile(standalone, html, 'utf8');
await copyFile(standalone, path.join(dist, 'index.html'));
await rm(path.join(dist, 'game.bundle.js'), { force: true });
await writeFile(path.join(dist, 'README_FIRST.txt'), `ROBLEDO KITCHEN RUSH 3D — SENIOR STARTUP EDITION\n\nRECOMMENDED ON WINDOWS\n1. Double-click RobledoKitchenRush3D_Windows.exe.\n2. The launcher starts a private local server at 127.0.0.1 and opens the game in your browser.\n3. Keep the launcher open while playing. It closes automatically after the game tab is closed.\n\nWHY THIS LAUNCHER EXISTS\nSome school/enterprise browser policies block file:// pages even when the HTML is valid. The portable launcher avoids file:// entirely while remaining offline and local.\n\nHTML FALLBACK\nRobledo_Kitchen_Rush_3D_OFFLINE.html is still included. Open it directly only on PCs where local file pages are allowed.\n\nTHREE PLAYERS\nP1: WASD / E interact / Q throw / Left Shift dash\nP2: Arrows / Enter interact / Slash throw / Right Shift dash\nP3: IJKL / O interact / U throw / P dash\nGamepads: left stick / A interact / X throw / B dash. Three controllers are recommended.\n\nCOOKING LOOP\nIngredients → prep → cook/fry/bake → plate → customer table → dirty dishes → sink.\nCustomers physically arrive, sit, browse the menu, order, wait, eat and leave.\n`);

console.log(`Built ${standalone}`);
