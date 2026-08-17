import { readFile, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const game = path.join(root, 'src/game.js');
const v8 = path.join(root, 'src/senior_v8.js');
for (const f of ['index.html','style.css','src/game.js','src/senior_v8.js','scripts/build.mjs','scripts/senior_v8_smoke.mjs']) await access(path.join(root,f));

for (const f of [game,v8,path.join(root,'scripts/senior_v8_smoke.mjs')]) {
  const parse = spawnSync(process.execPath, ['--check', f], { encoding: 'utf8' });
  if (parse.status !== 0) throw new Error(parse.stderr || `JavaScript syntax check failed: ${f}`);
}

const src = await readFile(game, 'utf8');
const senior = await readFile(v8, 'utf8');
const html = await readFile(path.join(root, 'index.html'), 'utf8');
const css = await readFile(path.join(root, 'style.css'), 'utf8');

// Preserve the stable physical restaurant engine underneath V8.
const mechanicTokens = [
  'class InputManager','class CameraRig','class CrewMember','class BotBrain','class CustomerParty',
  'PerspectiveCamera','identifyRecipe','openGeometryRescue','enterBuildMode','autoLayout','planRequirements',
  'BUSINESS_DEFAULT','EXPANSION_TIERS','FAST_SERVICE_SECONDS','completeTable','upgradeRestaurant','saveBusiness',
  'fixtureCap','customerCap','menuSlots','satisfaction','expansionTier','entrancePoint','currentBounds',
  'stove','fryer','oven','sink','spawnParty','interactTable','updateStations','navigator.getGamepads',
  "grocery:{id:'grocery'",'grocery(kinds=[])',"type:'storage'",'Grocery Market + Freezer','LEGACY_GROCERY_KEYS',
  "state='readyToOrder'",'confirmOrder(server=null)','orderWaitElapsed','qaRecord',
  'robledo_kitchen_rush_business_v6',
];
for (const token of mechanicTokens) if (!src.includes(token)) throw new Error(`Missing required base mechanic token: ${token}`);
for (const recipe of ['burger','salad','fries','pizza','grill','toast']) if (!src.includes(`${recipe}: {`)) throw new Error(`Missing base recipe ${recipe}`);
for (const role of ['Head Chef','Prep Specialist','Service Captain']) if (!src.includes(role)) throw new Error(`Missing crew role: ${role}`);
if (!src.includes("recipes:['salad','burger']")) throw new Error('Starter tier must begin with two recipes');
if (src.includes('Tomato Crate') || src.includes('Lettuce Crate') || src.includes('Meat Crate')) throw new Error('Legacy grocery crates must not return');

// Senior V8 requirements from the current QA brief.
const v8Tokens = [
  "const V8_VERSION = '8.0.0'",
  'game.__seniorV8',
  'spawnPlayersV8',
  'this.players=keep',
  'bots:0',
  'queueAction',
  "event.button===0",
  "event.button===2",
  "mode='smart'",
  "queueAction(p1,target,'hold')",
  'targetFromPointer',
  'approachPoint',
  'ergonomicLayout',
  'v8-customization',
  "gender:'neutral'",
  'SKIN_TONES',
  'UNIFORM_COLORS',
  'APRON_COLORS',
  'RECIPE_BOOK',
  'v8-flow',
  'identifyRecipeV8',
  'v8Stock',
  'Restocked',
  'v8Shift',
  'CLEANLINESS',
  'chefXP',
  'loyalty',
  'decorateParty',
  'partyBubbleText',
  'v8-human-interact',
  'Both mouse buttons now perform a real action',
];
for (const token of v8Tokens) if (!senior.includes(token)) throw new Error(`Missing Senior V8 token: ${token}`);
for (const recipe of ['burger','salad','fries','pizza','grill','toast']) if (!senior.includes(`${recipe}:{id:'${recipe}'`)) throw new Error(`Missing V8 recipe route: ${recipe}`);
if (!senior.includes("if(humans===1)return{...t,customerCap:")) throw new Error('Solo customer scaling is missing');
if (!senior.includes("game.flash(this.players.length===1?'SOLO SHIFT")) throw new Error('True solo shift messaging is missing');
if (!senior.includes("Left click object:</b> approach + interact automatically")) throw new Error('P1 left-click action copy is missing');
if (!senior.includes("Right click / hold:</b> interact / work manually")) throw new Error('P1 right-click action copy is missing');

const uiIds = ['menu-screen','crew-screen','human-count','crew-slots','menu-toggle-grid','tutorial-screen','build-ui','fixture-palette','open-restaurant-btn','camera-mode-label','cash','satisfaction','growth-tier','upgrade-restaurant-btn','capacity-summary','business-preview'];
for (const id of uiIds) if (!html.includes(`id="${id}"`)) throw new Error(`Missing required UI element #${id}`);
if (!css.includes('#menu-screen.hidden{display:none!important}')) throw new Error('Missing menu visibility regression guard in stylesheet');

console.log('Static Senior V8 validation passed.');
