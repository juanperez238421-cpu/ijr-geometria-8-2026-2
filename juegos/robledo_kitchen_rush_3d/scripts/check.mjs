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
  "grocery:{id:'grocery'",'grocery(kinds=[])',"type:'storage'",'Grocery Market + Freezer','LEGACY_GROCERY_KEYS',
  "state='readyToOrder'",'confirmOrder(server=null)','orderWaitElapsed','bot-order-taken','bot-storage-pick',
  'bot-prep-complete','bot-cook-start','bot-cook-ready','bot-assemble','bot-dish-served','bot-clean-cycle','qaRecord',
  'robledo_kitchen_rush_business_v6',
];
for (const token of mechanicTokens) if (!src.includes(token)) throw new Error(`Missing required V6 mechanic token: ${token}`);
for (const recipe of ['burger','salad','fries','pizza','grill','toast']) if (!src.includes(`${recipe}: {`)) throw new Error(`Missing recipe ${recipe}`);
for (const role of ['Head Chef','Prep Specialist','Service Captain']) if (!src.includes(role)) throw new Error(`Missing crew role: ${role}`);
if (!src.includes("recipes:['salad','burger']")) throw new Error('Starter tier must begin with only two recipes');
if (!src.includes('tableCap:2,customerCap:2,partySize:2,menuSlots:2')) throw new Error('Starter tier progression limits are missing');
if (!src.includes('this.lives++')) throw new Error('Fast-service life restoration path is missing');
if (src.includes('Tomato Crate') || src.includes('Lettuce Crate') || src.includes('Meat Crate')) throw new Error('Legacy per-ingredient grocery crates must not remain in the active fixture model');
if (src.includes('showCarry(') || src.includes('buildSteps(recipeId')) throw new Error('Legacy simulated bot cooking path is still present');
if (!src.includes("g.interact(m,t,dt,true)")) throw new Error('Bots must execute the same physical interaction functions as humans');
if (!src.includes("fixtureCaps:{table:2,counter:1,prep:1,stove:1,fryer:0,oven:0,sink:1,plate:1,trash:1,grocery:1}")) throw new Error('Starter grocery capacity is incorrect');

const uiIds = ['menu-screen','crew-screen','human-count','crew-slots','menu-toggle-grid','tutorial-screen','build-ui','fixture-palette','open-restaurant-btn','camera-mode-label','cash','satisfaction','growth-tier','upgrade-restaurant-btn','capacity-summary','business-preview'];
for (const id of uiIds) if (!html.includes(`id="${id}"`)) throw new Error(`Missing required UI element #${id}`);
if (!html.includes('grocery market/freezer wall')) throw new Error('V6 management UI must explain the grocery market/freezer wall');
if (!css.includes('#menu-screen.hidden{display:none!important}')) throw new Error('Missing menu visibility regression guard in stylesheet');
for (const token of ['.growth-card','.menu-toggle.locked','.fixture-btn.locked','.order-card.fast','.order-card.needs-waiter']) if (!css.includes(token)) throw new Error(`Missing V6 style ${token}`);

console.log('Static Autonomous Service V6 validation passed.');
