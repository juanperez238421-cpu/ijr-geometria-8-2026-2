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
  assert.match(svg,/viewBox="160 55 800 555"/);
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


test("original school crest present and valid embedded WebP",()=>{
 assert.match(html,/assets\/escudo-institucional-original\.svg/);
 const crest=read("assets/escudo-institucional-original.svg");
 assert.match(crest,/<svg /);
 const b64=crest.match(/data:image\/webp;base64,([A-Za-z0-9+/=]+)/);
 assert(b64 && b64[1].length>3000,"missing real school crest pixels");
 const bytes=Buffer.from(b64[1],"base64");
 assert.equal(bytes.subarray(0,4).toString("ascii"),"RIFF");
 assert.equal(bytes.subarray(8,12).toString("ascii"),"WEBP");
});

const calculator = require("./calculator-core.js");
test("calculator respects exam pi rule and arithmetic precedence",()=>{
 assert.equal(calculator.PI,3.14);
 assert.equal(calculator.evaluate("3×(2+1)"),9);
 assert.equal(calculator.evaluate("π×2"),6.28);
 assert.equal(calculator.evaluate("100×20%"),20);
 assert.equal(calculator.evaluate("12,5÷2"),6.25);
 assert.equal(calculator.evaluate("-3^2"),-9);
 assert.equal(calculator.evaluate("2^3^2"),512);
 assert.equal(calculator.evaluate("(5−2)^2"),9);
 assert.equal(calculator.format(calculator.evaluate("1÷8")),"0.125");
 assert.equal(calculator.format(calculator.evaluate("1,5+2,5")),"4");
});
test("calculator rejects unsafe or malformed input",()=>{
 for(const input of ["","1÷0","2(3)","1+alert(1)","window","1;2","ππ","1+","(1+2","2^^2","10/0"]){
  assert.throws(()=>calculator.evaluate(input), input);
 }
 assert.throws(()=>calculator.evaluate("1".repeat(121)));
});
test("accessibility and answer-autosave integration",()=>{
 const c=read("calculator.js");
 const refinement=read("refinement.css");
 for(const id of ["calculatorPanel","calcExpression","calcResult","calcTransfer","calculatorHelp","calcHint"])assert(html.includes('id="'+id+'"'));
 assert.match(html,/aria-live="polite"/);
 assert.match(html,/aria-label="Teclado de la calculadora"/);
 assert.match(html,/aria-readonly="true"/);
 assert.equal((html.match(/data-calc="/g)||[]).length,24);
 assert.match(c,/dispatchEvent\(new Event\("input"/);
 assert.match(c,/panel\.addEventListener\("keydown"/);
 assert.doesNotMatch(c,/\beval\s*\(/);
 assert.match(refinement,/\.instruction-text p\{/);
 assert.match(refinement,/\.question-statement\{/);
 assert.match(refinement,/\.calculator-card\{/);
 for(const size of ["1450","1240","990","760","450"])assert(refinement.includes("@media(max-width:"+size+"px)"));
});

test("all diagrams are fully visible and responsive in source",()=>{
 const repaired=read("visual-qa.css");
 assert.match(html,/visual-qa\.css\?v=20261016-r3/);
 assert.match(js,/p\.diagram\+"\?v=20261016-qa-r3"/);
 assert.match(repaired,/grid-template-areas:/);
 assert.match(repaired,/"nav nav"/);
 assert.match(repaired,/height:auto!important/);
 assert.match(repaired,/overflow:visible!important/);
 assert.match(repaired,/aspect-ratio:800\/555/);
 assert.match(repaired,/@media\(max-width:680px\)/);
 assert.match(repaired,/\.diagram-frame > img/);
 assert.doesNotMatch(repaired,/\.diagram-frame\{[^}]*height:clamp/);
 for(const p of manifest.problems){
  const svg=read(p.diagram);
  assert.match(svg,/viewBox="160 55 800 555"/);
  assert.match(svg,/x="168" y="63" width="784" height="539"/);
  assert(!svg.includes('viewBox="0 0 1120 760"'));
  // All footer dimensions are inside the corrected SVG viewport (bottom=710).
  assert(!/y="(?:667|677|682)"/.test(svg),"dimension footer must not remain embedded");
 }
});

test("math dimensions are presented outside SVG and do not clip",()=>{
 const h=read("index.html");
 const j=read("app.js");
 const style=read("visual-qa.css");
 assert(h.includes('id="dimensionCaption"'));
 assert(j.includes('$("dimensionCaption").textContent=p.dimensions'));
 assert.match(style,/\.dimension-caption\{/);
 assert.equal(manifest.problems.length,4);
 for(const p of manifest.problems){
   assert.ok(p.dimensions && p.dimensions.includes("cm"),p.id);
   const svg=read(p.diagram);
   assert.match(svg,/viewBox="160 55 800 555"/);
   assert.doesNotMatch(svg,/y="(?:667|677|682)"/);
 }
});
