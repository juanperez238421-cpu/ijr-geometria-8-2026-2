import { readFile, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const game = path.join(root, 'src/game.js');
for (const f of ['index.html','style.css','src/game.js','scripts/build.mjs','scripts/smoke.mjs']) await access(path.join(root,f));

const parse = spawnSync(process.execPath, ['--check', game], { encoding: 'utf8' });
if (parse.status !== 0) throw new Error(parse.stderr || 'JavaScript syntax check failed');
const smokeParse = spawnSync(process.execPath, ['--check', path.join(root, 'scripts/smoke.mjs')], { encoding: 'utf8' });
if (smokeParse.status !== 0) throw new Error(smokeParse.stderr || 'Smoke-test syntax check failed');

const src = await readFile(game, 'utf8');
const html = await readFile(path.join(root, 'index.html'), 'utf8');
const css = await readFile(path.join(root, 'style.css'), 'utf8');

const mechanicTokens = [
  'class InputManager', 'class CameraRig', 'class CrewMember', 'class BotBrain', 'class CustomerParty',
  'PerspectiveCamera', 'identifyRecipe', 'openGeometryRescue', 'enterBuildMode', 'autoLayout',
  'planRequirements', 'createFixtureVisual', 'requiredIngredients', 'humanCount', 'ROLE_META',
  'stove', 'fryer', 'oven', 'sink', 'spawnParty', 'interactTable', 'updateStations',
  'ArrowUp', 'KeyI', 'navigator.getGamepads', 'pointerdown', 'wheel',
];
for (const token of mechanicTokens) if (!src.includes(token)) throw new Error(`Missing required mechanic token: ${token}`);
for (const recipe of ['burger','salad','fries','pizza','grill','toast']) if (!src.includes(`${recipe}: {`)) throw new Error(`Missing recipe ${recipe}`);
for (const role of ['Head Chef','Prep Specialist','Service Captain']) if (!src.includes(role)) throw new Error(`Missing crew role: ${role}`);

const uiIds = ['menu-screen','crew-screen','human-count','crew-slots','menu-toggle-grid','tutorial-screen','build-ui','fixture-palette','open-restaurant-btn','camera-mode-label'];
for (const id of uiIds) if (!html.includes(`id="${id}"`)) throw new Error(`Missing required UI element #${id}`);
if (html.includes('id="menu-screen" class="overlay screen visible"')) throw new Error('Menu must not carry the legacy visible class');
if (!css.includes('#menu-screen.hidden{display:none!important}')) throw new Error('Missing menu visibility regression guard in stylesheet');
if (!css.includes('.fixture-palette') || !css.includes('.crew-slots') || !css.includes('.tutorial-card')) throw new Error('Missing planner/crew/tutorial presentation styles');

console.log('Static dynamic-crew, planner, camera, cooking and startup validation passed.');
