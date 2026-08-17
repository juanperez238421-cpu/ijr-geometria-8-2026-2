import { build } from 'esbuild';
import { readFile, writeFile, mkdir, rm, copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'..');
const dist=path.join(root,'dist');
await rm(dist,{recursive:true,force:true});
await mkdir(dist,{recursive:true});

await build({
  entryPoints:[path.join(root,'src/senior_v9_final.js')],
  bundle:true,
  format:'iife',
  platform:'browser',
  target:['chrome110','edge110','firefox115'],
  minify:true,
  sourcemap:false,
  outfile:path.join(dist,'game.bundle.js'),
  legalComments:'none',
});

let html=await readFile(path.join(root,'index.html'),'utf8');
const css=await readFile(path.join(root,'style.css'),'utf8');
const bundledGame=await readFile(path.join(dist,'game.bundle.js'),'utf8');
const portableHeartbeat=`if(location.hostname==='127.0.0.1'&&new URLSearchParams(location.search).get('portable')==='1'){const __rkrHeartbeat=()=>fetch('/__heartbeat',{method:'POST',cache:'no-store'}).catch(()=>{});__rkrHeartbeat();setInterval(__rkrHeartbeat,10000);}`;
const js=portableHeartbeat+bundledGame;
html=html.replace('<link rel="stylesheet" href="./style.css" />',()=>`<style>${css}</style>`);
html=html.replace('<script src="./game.js"></script>',()=>`<script>${js}</script>`);

const logoPath=path.resolve(root,'../../assets/logo_colegio_transparente.png');
try{const logo=await readFile(logoPath);html=html.replaceAll('../../assets/logo_colegio_transparente.png',`data:image/png;base64,${logo.toString('base64')}`);}catch{console.warn('School logo not found; source path retained.');}

const standalone=path.join(dist,'Robledo_Kitchen_Rush_3D_SENIOR_V9_OFFLINE.html');
await writeFile(standalone,html,'utf8');
await copyFile(standalone,path.join(dist,'Robledo_Kitchen_Rush_3D_OFFLINE.html'));
await copyFile(standalone,path.join(dist,'index.html'));
await rm(path.join(dist,'game.bundle.js'),{force:true});

await writeFile(path.join(dist,'README_FIRST.txt'),`ROBLEDO KITCHEN RUSH 3D — SENIOR V9\n\nRECOMMENDED ON WINDOWS\n1. Extract the ZIP completely.\n2. Open PLAY/RobledoKitchenRush3D_SeniorV9_Windows.exe.\n3. The launcher serves the game locally on 127.0.0.1. No internet is required.\n\nPLAYER 1 — REBUILT SERVICE MODEL\n- Left click floor: move.\n- Left click a kitchen object/table/ingredient: approach it and perform ONE contextual action.\n- Prep and sink are now single-click timed jobs. No mouse-button holding is required.\n- Right click: CANCEL ONLY. It never chops, washes, cooks, picks up food or rotates the service camera.\n- Middle click: throw the held item.\n- E or Space: use the currently selected/nearest target.\n- Wheel: zoom. C cycles camera presets. Home resets camera.\n- Build mode restores normal right-drag camera orbit.\n\nWHY V9 CHANGED\nSenior QA found that V8.1 had too many overlapping interaction paths: canvas pointer handlers, window fallbacks, right-hold state, auxclick recovery, watchdog interaction and visual pulse/particle feedback. Although the QA made those paths reliable, the result felt mechanical and over-engineered. V9 replaces that service layer with one explicit state machine.\n\nSERVICE FLOW\n1. Click a table to take an order.\n2. Click the required grocery ingredient.\n3. Click prep once when chopping is required; the job finishes automatically and returns the prepared ingredient to the chef.\n4. Click stove/fryer/oven once to place food. Cooking continues in real time while you perform other work.\n5. Click ready food to collect it.\n6. Click a counter to place/combine ingredients with a clean plate.\n7. Click the matching table to serve.\n8. Click dirty tables, then click the sink once to wash automatically.\n\nPRESENTATION\n- No right-click hold animation.\n- No interaction particle burst or pulsing selection spam for Player 1.\n- One static target ring shows the current target.\n- A compact action panel explains what a click will do.\n- Prep/wash use a clean progress bar.\n- The service board reports active station states such as COOKING, READY and BURNED.\n\nSOLO / LOCAL CO-OP\n- 1 player = exactly one human chef and zero AI helpers.\n- 2/3-player modes contain only the selected human players.\n- Existing recipe, stock, business, loyalty, cleanliness, NPC, customization and expansion systems remain active.\n\nCHARACTER CUSTOMIZATION\nName, gender/presentation, six skin tones, body build, hair style/color, uniform/apron colors, accessories and extended appearance options remain available.\n\nLAYOUT\nThe V9 recommended layout uses a compact work triangle: grocery wall at the back, cleaning on the left, production wings around the kitchen, central pass/counters and wider dining/service lanes.\n\nHTML FALLBACK\nRobledo_Kitchen_Rush_3D_SENIOR_V9_OFFLINE.html is a complete single-file offline build.\n`);

console.log(`Built ${standalone}`);
