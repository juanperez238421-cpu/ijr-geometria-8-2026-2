#!/usr/bin/env node
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const read=f=>fs.readFileSync(path.join(__dirname,f),"utf8");
const html=read("index.html"),css=read("styles.css"),js=read("app.js"),manifest=JSON.parse(read("manifest.json"));
test("manifest exposes exactly four complete prompt-only problems",()=>{
 assert.equal(manifest.public_exam_enabled,true);
 assert.equal(manifest.problems.length,4);
 assert.deepEqual(manifest.problems.map(x=>x.id),["P01","P02","P03","P04"]);
 assert(manifest.problems.every(x=>x.ready && x.title && x.statement && /^assets\/.+\.svg$/.test(x.diagram)));
 assert.doesNotMatch(JSON.stringify(manifest),/correct_answer|solution|answer_key|paso\s*1/i);
});
test("all referenced diagrams present and valid SVG",()=>{
 for(const p of manifest.problems){
  const svg=read(p.diagram);
  assert.match(svg,/<svg /);assert.match(svg,/<\/svg>/);
  assert.match(svg,/viewBox="0 0 1120 760"/);
  assert.match(svg,/fill="#a8c9e3"/);
 }
});
test("functional online form, navigation and private submission wiring",()=>{
 for(const id of ["studentName","studentGroup","studentAgree","previewStart","problemNavigation","finishButton","receipt","areaValue","reasoning"]){
  assert(html.includes('id="'+id+'"'),"missing "+id);
 }
 assert.equal((html.match(/data-problem="[0-3]"/g)||[]).length,4);
 assert.match(js,/COUNT=4/);
 for(const op of ['"start"','"status"','"answer"','"incident"','"submit"'])assert(js.includes(op));
 assert.match(js,/functions\/v1\/geometry8-canada-quiz/);
});
test("3 exit incident signals, modal and meaningful mobile layouts",()=>{
 for(const e of ["fullscreenchange","visibilitychange","blur","MAX=3","sessionStorage","incidentBusy"])assert(js.includes(e));
 assert(css.includes("@media(max-width:580px)"));
 assert(html.includes('id="incidentModal"'));
});
test("JavaScript syntax and literal DOM references",()=>{
 new Function(js);
 const missing=[...js.matchAll(/\$\("([A-Za-z0-9]+)"\)/g)].map(x=>x[1]).filter(id=>id!=="runtimeNotice"&&!html.includes('id="'+id+'"'));
 assert.deepEqual(missing,[]);
});
