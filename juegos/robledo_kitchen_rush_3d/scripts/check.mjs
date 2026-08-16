import { readFile, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const game = path.join(root, 'src/game.js');
for (const f of ['index.html','style.css','src/game.js','scripts/build.mjs','scripts/smoke.mjs']) await access(path.join(root,f));

for (const f of [game,path.join(root,'scripts/smoke.mjs')]) {
  const parse = spawnSync(process.execPath, ['--check', f], { encoding: 'utf8' });
  if (parse.status !== 0) throw new Error(parse.stderr || `JavaScript syntax check failed: ${f}`);
}

const src = await readFile(game, 'utf8');
const html = await readFile(path.join(root, 'index.html'), 'utf8');
const css = await readFile(path.join(root, 'style.css'), 'utf8');
const mechanicTokens = [
  'class InputManager','class CameraRig','class CrewMember','class BotBrain','class CustomerParty',
  'PerspectiveCamera','identifyRecipe','openGeometryRescue','enterBuildMode','autoLayout','planRequirements',
  'BUSINESS_DEFAULT','EXPANSION_TIERS','FAST_SERVICE_SECONDS','completeTable','upgradeRestaurant','saveBusiness',
  'fixtureCap','customerCap','menuSlots','satisfaction','expansionTier','entrancePoint','currentBounds',
  'stove','fryer','oven','sink','spawnParty','interactTable','updateStations','navigator.getGamepads',
];
for (const token of mechanicTokens) if (!src.includes(token)) throw new Error(`Missing required mechanic token: ${token}`);
for (const recipe of ['burger','salad','fries','pizza','grill','toast']) if (!src.includes(`${recipe}: {`)) throw new Error(`Missing recipe ${recipe}`);
for (const role of ['Head Chef','Prep Specialist','Service Captain']) if (!src.includes(role)) throw new Error(`Missing crew role: ${role}`);
if (!src.includes("recipes:['salad','burger']")) throw new Error('Starter tier must begin with only two recipes');
if (!src.includes('tableCap:2,customerCap:2,partySize:2,menuSlots:2')) throw new Error('Starter tier progression limits are missing');
if (!src.includes('this.lives++')) throw new Error('Fast-service life restoration path is missing');

const uiIds = ['menu-screen','crew-screen','human-count','crew-slots','menu-toggle-grid','tutorial-screen','build-ui','fixture-palette','open-restaurant-btn','camera-mode-label','cash','satisfaction','growth-tier','upgrade-restaurant-btn','capacity-summary','business-preview'];
for (const id of uiIds) if (!html.includes(`id="${id}"`)) throw new Error(`Missing required UI element #${id}`);
if (!css.includes('#menu-screen.hidden{display:none!important}')) throw new Error('Missing menu visibility regression guard in stylesheet');
for (const token of ['.growth-card','.menu-toggle.locked','.fixture-btn.locked','.order-card.fast']) if (!css.includes(token)) throw new Error(`Missing progression style ${token}`);

console.log('Static Progressive Growth V5 validation passed.');
