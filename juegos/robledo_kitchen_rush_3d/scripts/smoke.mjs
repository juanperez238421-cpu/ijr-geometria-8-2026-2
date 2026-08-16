const port = Number(process.env.CDP_PORT || 9333);
const endpoint = `http://127.0.0.1:${port}/json`;
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function waitForPage() {
  for (let i = 0; i < 140; i++) {
    try {
      const pages = await fetch(endpoint).then(r => r.json());
      const page = pages.find(p => p.type === 'page' && p.url.includes('127.0.0.1'));
      if (page) return page;
    } catch {}
    await sleep(100);
  }
  throw new Error('Chrome DevTools page did not become available');
}

class CDP {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.next = 1;
    this.pending = new Map();
    this.exceptions = [];
    this.consoleErrors = [];
    this.ws.onmessage = event => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result);
      } else if (msg.method === 'Runtime.exceptionThrown') {
        this.exceptions.push(msg.params?.exceptionDetails?.exception?.description || msg.params?.exceptionDetails?.text || 'Runtime exception');
      } else if (msg.method === 'Runtime.consoleAPICalled' && msg.params?.type === 'error') {
        this.consoleErrors.push((msg.params.args || []).map(x => x.value ?? x.description ?? '').join(' '));
      }
    };
  }
  async open() { if (this.ws.readyState !== WebSocket.OPEN) await new Promise((resolve, reject) => { this.ws.onopen = resolve; this.ws.onerror = reject; }); }
  send(method, params = {}) { const id = this.next++; return new Promise((resolve, reject) => { this.pending.set(id, { resolve, reject }); this.ws.send(JSON.stringify({ id, method, params })); }); }
  async eval(expression) { const result = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }); if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text || 'Evaluation failed'); return result.result?.value; }
}

const page = await waitForPage();
const cdp = new CDP(page.webSocketDebuggerUrl);
await cdp.open();
await cdp.send('Runtime.enable');
await cdp.send('Page.enable');

for (let i = 0; i < 120; i++) {
  if (await cdp.eval(`document.readyState === 'complete' && !!document.getElementById('start-btn')`)) break;
  await sleep(100);
}

const preflight = await cdp.eval(`(() => {
  const canvas = document.getElementById('game-canvas');
  const start = document.getElementById('start-btn');
  const menu = document.getElementById('menu-screen');
  return {
    title: document.title,
    startExists: !!start,
    startEnabled: !!start && !start.disabled,
    menuDisplay: getComputedStyle(menu).display,
    canvasExists: !!canvas,
    webgl: !!(canvas && (canvas.getContext('webgl2') || canvas.getContext('webgl'))),
    crewScreenExists: !!document.getElementById('crew-screen'),
    buildUiExists: !!document.getElementById('build-ui'),
  };
})()`);
if (!preflight.startExists || !preflight.startEnabled || preflight.menuDisplay === 'none' || !preflight.canvasExists || !preflight.webgl || !preflight.crewScreenExists || !preflight.buildUiExists) {
  throw new Error(`Preflight failed: ${JSON.stringify(preflight)}`);
}

await cdp.eval(`document.getElementById('start-btn').click()`);
await sleep(350);
const crew = await cdp.eval(`(() => {
  const menu = document.getElementById('menu-screen');
  const screen = document.getElementById('crew-screen');
  return {
    menuHidden: getComputedStyle(menu).display === 'none' && menu.getClientRects().length === 0,
    crewVisible: getComputedStyle(screen).display !== 'none' && screen.getClientRects().length > 0,
    slots: document.querySelectorAll('#crew-slots .crew-slot').length,
    bots: document.querySelectorAll('#crew-slots .crew-slot.bot').length,
    roleSelectors: document.querySelectorAll('#crew-slots select').length,
    menuChoices: document.querySelectorAll('#menu-toggle-grid .menu-toggle.active').length,
  };
})()`);
if (!crew.menuHidden || !crew.crewVisible || crew.slots !== 3 || crew.bots !== 2 || crew.roleSelectors !== 3 || crew.menuChoices < 3) {
  throw new Error(`Crew configuration failed: ${JSON.stringify(crew)}`);
}

await cdp.eval(`document.getElementById('crew-continue-btn').click()`);
await sleep(250);
const tutorialVisible = await cdp.eval(`getComputedStyle(document.getElementById('tutorial-screen')).display !== 'none' && document.getElementById('tutorial-title').textContent.length > 3`);
if (!tutorialVisible) throw new Error('Crew setup did not enter tutorial');
await cdp.eval(`document.getElementById('tutorial-skip-btn').click()`);
await sleep(350);

const buildInitial = await cdp.eval(`(() => ({
  buildVisible: getComputedStyle(document.getElementById('build-ui')).display !== 'none',
  budget: document.getElementById('build-budget').textContent,
  palette: document.querySelectorAll('#fixture-palette .fixture-btn').length,
  openDisabled: document.getElementById('open-restaurant-btn').disabled,
}))()`);
if (!buildInitial.buildVisible || buildInitial.palette < 14 || !buildInitial.openDisabled) {
  throw new Error(`Build mode initial state failed: ${JSON.stringify(buildInitial)}`);
}

await cdp.eval(`document.getElementById('auto-layout-btn').click()`);
await sleep(400);
const built = await cdp.eval(`(() => ({
  openDisabled: document.getElementById('open-restaurant-btn').disabled,
  requirements: [...document.querySelectorAll('#build-requirements .req')].map(x => x.className),
  budget: document.getElementById('build-budget').textContent,
  selected: document.getElementById('selected-fixture-label').textContent,
}))()`);
if (built.openDisabled || !built.requirements.length || built.requirements.some(x => !x.includes('ok'))) {
  throw new Error(`Recommended kitchen does not satisfy requirements: ${JSON.stringify(built)}`);
}

await cdp.eval(`document.getElementById('open-restaurant-btn').click()`);
await sleep(1700);
const started = await cdp.eval(`(() => {
  const hud = document.getElementById('hud');
  const playerHud = document.getElementById('player-hud');
  const build = document.getElementById('build-ui');
  const canvas = document.getElementById('game-canvas');
  return {
    buildHidden: getComputedStyle(build).display === 'none',
    hudVisible: getComputedStyle(hud).display !== 'none',
    playerHudVisible: getComputedStyle(playerHud).display !== 'none',
    crewChips: document.querySelectorAll('#player-hud .player-chip').length,
    botChips: document.querySelectorAll('#player-hud .player-chip.bot').length,
    timer: document.getElementById('timer').textContent,
    lives: document.getElementById('lives').textContent,
    cameraMode: document.getElementById('camera-mode-label').textContent,
    canvasWidth: canvas.width,
    canvasHeight: canvas.height,
  };
})()`);
if (!started.buildHidden || !started.hudVisible || !started.playerHudVisible || started.crewChips !== 3 || started.botChips !== 2) {
  throw new Error(`Service did not start correctly: ${JSON.stringify(started)}`);
}
if (!started.timer || started.timer === '03:30') throw new Error(`Gameplay timer did not advance: ${JSON.stringify(started)}`);
if (started.canvasWidth < 640 || started.canvasHeight < 360) throw new Error(`3D canvas is unexpectedly small: ${JSON.stringify(started)}`);
if (cdp.exceptions.length) throw new Error(`Runtime exceptions detected: ${cdp.exceptions.join(' | ')}`);
if (cdp.consoleErrors.length) throw new Error(`Console errors detected: ${cdp.consoleErrors.join(' | ')}`);

console.log('Dynamic crew/build/service browser E2E passed:', JSON.stringify({ preflight, crew, buildInitial, built, started }));
cdp.ws.close();
