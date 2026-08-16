import { readFile, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const game = path.join(root, 'src/game.js');
for (const f of ['index.html','style.css','src/game.js','scripts/build.mjs']) await access(path.join(root,f));
const parse = spawnSync(process.execPath, ['--check', game], { encoding: 'utf8' });
if (parse.status !== 0) throw new Error(parse.stderr || 'JavaScript syntax check failed');
const src = await readFile(game, 'utf8');
const requirements = [
  "class InputManager", "class CustomerParty", "identifyRecipe", "openGeometryRescue",
  "stove", "fryer", "oven", "sink", "spawnParty", "interactTable",
  "ArrowUp", "KeyI", "navigator.getGamepads",
];
for (const token of requirements) if (!src.includes(token)) throw new Error(`Missing required mechanic token: ${token}`);
for (const recipe of ['burger','salad','fries','pizza','grill','toast']) if (!src.includes(`${recipe}: {`)) throw new Error(`Missing recipe ${recipe}`);
console.log('Static mechanics validation passed.');
