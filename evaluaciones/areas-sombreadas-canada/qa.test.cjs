#!/usr/bin/env node
// Static contract checks. Not a replacement for browser E2E or backend security tests.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const base = __dirname;
const html = fs.readFileSync(path.join(base, "index.html"), "utf8");
const js = fs.readFileSync(path.join(base, "app.js"), "utf8");
const css = fs.readFileSync(path.join(base, "styles.css"), "utf8");
const data = JSON.parse(fs.readFileSync(path.join(base, "manifest.json"), "utf8"));
test("three slots pending from Opus", () => {
  assert.equal(data.public_exam_enabled, false);
  assert.equal(data.problems.length, 3);
  assert.deepEqual(data.problems.map(p => p.id), ["P01", "P02", "P03"]);
  data.problems.forEach(p => assert.equal(p.ready, false));
  assert.equal(data.figures_per_problem.min, 3);
  assert.equal(data.figures_per_problem.max, 5);
});
test("safe official launch status and teacher preview", () => {
  assert.match(html, /id="previewStart"/);
  assert.match(html, /id="previewStart"[\s\S]*?id="[^"]+"/); // whole hero remains reachable
  assert.match(html, /id="areaValue"/);
  assert.match(html, /id="reasoning"/);
  assert.match(html, /Iniciar evaluación oficial[\s\S]*?<\/button>/);
  assert.match(html, /button class="btn btn-disabled" type="button" disabled/);
});
test("all app IDs resolve in HTML or are created intentionally", () => {
  const ids = Array.from(js.matchAll(/\$\("([A-Za-z][A-Za-z0-9]+)"\)/g), m => m[1]);
  const generated = new Set(["runtimeNotice"]);
  for (const id of ids) {
    assert.ok(html.includes('id="' + id + '"') || generated.has(id), "missing id=" + id);
  }
});
test("anti-exit events, 3 strikes and deduplication", () => {
  assert.match(js, /STRIKE_LIMIT = 3/);
  assert.match(js, /document\.addEventListener\("fullscreenchange"/);
  assert.match(js, /document\.addEventListener\("visibilitychange"/);
  assert.match(js, /window\.addEventListener\("blur"/);
  assert.match(js, /state\.armed = false/);
  assert.match(js, /state\.strikes >= STRIKE_LIMIT/);
});
test("safe DOM rendering, responsive UI, no public answer key", () => {
  assert.match(js, /questionStatement"\)\.textContent/);
  assert.match(css, /@media\(max-width:580px\)/);
  assert.doesNotMatch(JSON.stringify(data), /correct_answer|answer_key|solution_video/);
});
