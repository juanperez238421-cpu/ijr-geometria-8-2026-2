const port = Number(process.env.CDP_PORT || 9333);
const endpoint = `http://127.0.0.1:${port}/json`;

async function waitForPage() {
  for (let i = 0; i < 120; i++) {
    try {
      const pages = await fetch(endpoint).then(r => r.json());
      const page = pages.find(p => p.type === 'page' && p.url.includes('127.0.0.1'));
      if (page) return page;
    } catch {}
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error('Chrome DevTools page did not become available');
}

class CDP {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.next = 1;
    this.pending = new Map();
    this.exceptions = [];
    this.ws.onmessage = event => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result);
      } else if (msg.method === 'Runtime.exceptionThrown') {
        this.exceptions.push(msg.params?.exceptionDetails?.text || 'Runtime exception');
      }
    };
  }
  async open() {
    if (this.ws.readyState === WebSocket.OPEN) return;
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
  }
  send(method, params = {}) {
    const id = this.next++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  async eval(expression) {
    const result = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Evaluation failed');
    return result.result?.value;
  }
}

const page = await waitForPage();
const cdp = new CDP(page.webSocketDebuggerUrl);
await cdp.open();
await cdp.send('Runtime.enable');
await cdp.send('Page.enable');

for (let i = 0; i < 100; i++) {
  if (await cdp.eval(`document.readyState === 'complete' && !!document.getElementById('start-btn')`)) break;
  await new Promise(r => setTimeout(r, 100));
}

const preflight = await cdp.eval(`(() => {
  const canvas = document.getElementById('game-canvas');
  const start = document.getElementById('start-btn');
  return {
    title: document.title,
    startExists: !!start,
    startEnabled: !!start && !start.disabled,
    canvasExists: !!canvas,
    menuVisible: !document.getElementById('menu-screen').classList.contains('hidden'),
    webgl: !!(canvas && (canvas.getContext('webgl2') || canvas.getContext('webgl'))),
  };
})()`);
if (!preflight.startExists || !preflight.startEnabled || !preflight.canvasExists || !preflight.menuVisible || !preflight.webgl) {
  throw new Error(`Preflight failed: ${JSON.stringify(preflight)}`);
}

await cdp.eval(`document.getElementById('start-btn').click()`);
await new Promise(r => setTimeout(r, 1400));

const started = await cdp.eval(`(() => ({
  menuHidden: document.getElementById('menu-screen').classList.contains('hidden'),
  hudVisible: !document.getElementById('hud').classList.contains('hidden'),
  playerHudVisible: !document.getElementById('player-hud').classList.contains('hidden'),
  timer: document.getElementById('timer').textContent,
  lives: document.getElementById('lives').textContent,
  canvasWidth: document.getElementById('game-canvas').width,
  canvasHeight: document.getElementById('game-canvas').height,
}))()`);

if (!started.menuHidden || !started.hudVisible || !started.playerHudVisible) {
  throw new Error(`Start button did not enter gameplay: ${JSON.stringify(started)}`);
}
if (!started.timer || started.timer === '03:00') {
  throw new Error(`Gameplay timer did not advance: ${JSON.stringify(started)}`);
}
if (started.canvasWidth < 640 || started.canvasHeight < 360) {
  throw new Error(`3D canvas is unexpectedly small: ${JSON.stringify(started)}`);
}
if (cdp.exceptions.length) {
  throw new Error(`Runtime exceptions detected: ${cdp.exceptions.join(' | ')}`);
}

console.log('Browser startup smoke test passed:', JSON.stringify({ preflight, started }));
cdp.ws.close();
