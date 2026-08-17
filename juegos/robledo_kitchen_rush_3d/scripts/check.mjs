import { readFile, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const files=['index.html','style.css','src/game.js','src/senior_v8.js','src/senior_v9.js','src/senior_v9_final.js','scripts/build.mjs','scripts/senior_v9_smoke.mjs'];
for(const f of files)await access(path.join(root,f));
for(const f of ['src/game.js','src/senior_v8.js','src/senior_v9.js','src/senior_v9_final.js','scripts/build.mjs','scripts/senior_v9_smoke.mjs']){const p=path.join(root,f),r=spawnSync(process.execPath,['--check',p],{encoding:'utf8'});if(r.status!==0)throw new Error(r.stderr||`JavaScript syntax check failed: ${f}`);}

const base=await readFile(path.join(root,'src/game.js'),'utf8');
const v8=await readFile(path.join(root,'src/senior_v8.js'),'utf8');
const v9=await readFile(path.join(root,'src/senior_v9.js'),'utf8');
const final=await readFile(path.join(root,'src/senior_v9_final.js'),'utf8');
const build=await readFile(path.join(root,'scripts/build.mjs'),'utf8');
const html=await readFile(path.join(root,'index.html'),'utf8');
const css=await readFile(path.join(root,'style.css'),'utf8');

for(const token of ['class InputManager','class CameraRig','class CrewMember','class BotBrain','class CustomerParty','PerspectiveCamera','identifyRecipe','openGeometryRescue','enterBuildMode','autoLayout','planRequirements','BUSINESS_DEFAULT','EXPANSION_TIERS','completeTable','upgradeRestaurant','saveBusiness',"grocery:{id:'grocery'",'Grocery Market + Freezer',"type:'storage'",'interactPrep','interactCookStation','interactSink','interactTable'])if(!base.includes(token))throw new Error(`Missing base mechanic token: ${token}`);
for(const recipe of ['burger','salad','fries','pizza','grill','toast'])if(!base.includes(`${recipe}: {`))throw new Error(`Missing base recipe: ${recipe}`);

for(const token of ['game.__seniorV8','spawnPlayersV8','this.players=keep','bots:0','ergonomicLayout','v8-customization','RECIPE_BOOK','v8Stock','CLEANLINESS','chefXP','loyalty','decorateParty','partyBubbleText','SOLO SHIFT — you are alone'])if(!v8.includes(token))throw new Error(`Inherited Senior V8 system missing: ${token}`);

const v9Tokens=[
  "const VERSION = '9.0.0'",'game.__seniorV9','v9-input-layer','Right click = cancel only','queueTask','cancelTask','startOrAdvanceWork','automatic timed work','installPrimaryPlayer','player.updateHuman=function updateHumanV9','player.pick=function pickV9','v9-task-start','v9-task-complete','v9-right-cancel','stationStatus','v9Layout','compact work triangle','game.canvas.style.pointerEvents',
];
for(const token of v9Tokens)if(!v9.includes(token))throw new Error(`Missing Senior V9 token: ${token}`);
if(v9.includes("queueAction(p1,target,'hold')"))throw new Error('V9 must not reintroduce right-hold service interaction.');
if(!final.includes("game.canvas.style.pointerEvents=playing?'none':'auto'"))throw new Error('V9 pointer ownership restoration is missing.');
if(!final.includes("game.__seniorV8.mouse.rightDown=false"))throw new Error('Legacy right-hold state is not neutralized.');
if(!build.includes("entryPoints:[path.join(root,'src/senior_v9_final.js')]"))throw new Error('Build entry point is not Senior V9 final.');
if(!build.includes('Robledo_Kitchen_Rush_3D_SENIOR_V9_OFFLINE.html'))throw new Error('V9 standalone output name missing.');
if(!build.includes('Right click: CANCEL ONLY'))throw new Error('V9 player instructions missing cancellation-only right click.');

for(const id of ['menu-screen','crew-screen','human-count','crew-slots','menu-toggle-grid','tutorial-screen','build-ui','fixture-palette','open-restaurant-btn','camera-mode-label','cash','satisfaction','growth-tier','upgrade-restaurant-btn','capacity-summary','business-preview'])if(!html.includes(`id="${id}"`))throw new Error(`Missing UI element #${id}`);
if(!css.includes('#menu-screen.hidden{display:none!important}'))throw new Error('Missing menu visibility regression guard.');

console.log('Static Senior V9 validation passed.');
