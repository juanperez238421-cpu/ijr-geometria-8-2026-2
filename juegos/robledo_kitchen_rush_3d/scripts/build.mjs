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
const js = await readFile(path.join(dist, 'game.bundle.js'), 'utf8');
html = html.replace('<link rel="stylesheet" href="./style.css" />', `<style>${css}</style>`);
html = html.replace('<script src="./game.js"></script>', `<script>${js}</script>`);

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
await writeFile(path.join(dist, 'README_FIRST.txt'), `ROBLEDO KITCHEN RUSH 3D — FULL LOCAL THREE.JS EDITION\n\n1. Open Robledo_Kitchen_Rush_3D_OFFLINE.html in Chrome, Edge or Firefox.\n2. No web server and no Internet connection are required after download.\n3. Three people can play simultaneously on the same PC. Three gamepads are recommended; keyboard layouts are also built in.\n\nP1: WASD / E interact / Q throw / Left Shift dash\nP2: Arrows / Enter interact / Slash throw / Right Shift dash\nP3: IJKL / O interact / U throw / P dash\n\nGamepads: left stick / A interact / X throw / B dash.\n\nCooking loop: ingredients → prep → cook/fry/bake → plate → customer table → dirty dishes → sink.\nCustomers physically arrive, sit, browse the menu, order, wait, eat and leave.\n`);

console.log(`Built ${standalone}`);
