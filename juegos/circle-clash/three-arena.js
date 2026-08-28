const PRIMARY_THREE = "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";
const FALLBACK_THREE = "https://unpkg.com/three@0.180.0/build/three.module.js";
const WORLD_SIZE = 64;
const HALF_WORLD = WORLD_SIZE / 2;
const AVATAR_COLORS = ["#2f7450","#9b2934","#31597a","#9a6a1f","#6f4b8b","#287a7d","#92573d","#4f6d2e","#7b3d69","#37658c","#8a6a28","#5a5550"];

const state = {
  THREE: null,
  field: null,
  canvas: null,
  renderer: null,
  scene: null,
  camera: null,
  raycaster: null,
  pointer: null,
  players: new Map(),
  projectileJobs: new Set(),
  raf: 0,
  resizeObserver: null,
  avatarObserver: null,
  projectileObserver: null,
  uiObserver: null,
  running: false,
  failed: false,
  yaw: Math.PI * 0.25,
  pitch: 0.52,
  distance: 22,
  dragging: false,
  dragMoved: false,
  pointerStart: { x: 0, y: 0 },
  lastPointer: { x: 0, y: 0 },
  cameraFocus: null,
  reducedMotion: matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false,
  lastFrame: performance.now(),
  labelCache: new Map(),
  contextLost: false,
  currentTargetId: "",
  bootMessage: null,
  selectedMarker: null,
};

function hasWebGL() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(window.WebGL2RenderingContext && canvas.getContext("webgl2", { failIfMajorPerformanceCaveat: true })) ||
      Boolean(window.WebGLRenderingContext && canvas.getContext("webgl", { failIfMajorPerformanceCaveat: true }));
  } catch { return false; }
}

async function loadThree() {
  try { return await import(PRIMARY_THREE); }
  catch (primaryError) {
    console.warn("Circle Clash 3D: primary Three.js CDN unavailable, using fallback.", primaryError);
    return import(FALLBACK_THREE);
  }
}

function showBoot(text, mode = "loading") {
  if (!state.field) return;
  let node = state.bootMessage;
  if (!node) {
    node = document.createElement("div");
    node.className = "three-boot";
    node.setAttribute("role", "status");
    node.setAttribute("aria-live", "polite");
    state.field.append(node);
    state.bootMessage = node;
  }
  node.dataset.mode = mode;
  node.textContent = text;
}

function failGracefully(message, error) {
  state.failed = true;
  state.running = false;
  cancelAnimationFrame(state.raf);
  state.field?.classList.remove("three-ready");
  state.field?.classList.add("three-fallback");
  showBoot(message, "fallback");
  if (error) console.warn("Circle Clash 3D fallback:", error);
}

function percentToWorld(xPct, yPct) {
  const x = ((Number(xPct) - 50) / 50) * HALF_WORLD;
  const z = ((Number(yPct) - 50) / 50) * HALF_WORLD;
  return { x, z };
}

function worldFromAvatar(node) {
  const xPct = parseFloat(node.style.left || "50");
  const yPct = parseFloat(node.style.top || "50");
  return percentToWorld(Number.isFinite(xPct) ? xPct : 50, Number.isFinite(yPct) ? yPct : 50);
}

function getDeviceTier() {
  const memory = Number(navigator.deviceMemory || 4);
  const cores = Number(navigator.hardwareConcurrency || 4);
  const mobile = matchMedia?.("(max-width: 760px)")?.matches ?? false;
  if (mobile || memory <= 4 || cores <= 4) return "low";
  if (memory <= 8 || cores <= 8) return "medium";
  return "high";
}

function adaptivePixelRatio() {
  const tier = getDeviceTier();
  const cap = tier === "low" ? 1.15 : tier === "medium" ? 1.45 : 1.8;
  return Math.min(window.devicePixelRatio || 1, cap);
}

function makeRenderer(THREE) {
  const tier = getDeviceTier();
  const canvas = document.createElement("canvas");
  canvas.id = "threeArenaCanvas";
  canvas.className = "three-arena-canvas";
  canvas.setAttribute("aria-label", "Arena tridimensional multijugador. Usa WASD o las flechas para moverte; arrastra para girar la cámara y haz clic sobre un rival para apuntar.");
  canvas.tabIndex = 0;
  state.field.append(canvas);
  state.canvas = canvas;

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: tier !== "low",
    alpha: false,
    powerPreference: tier === "low" ? "low-power" : "high-performance",
    preserveDrawingBuffer: false,
    stencil: false,
  });
  renderer.setPixelRatio(adaptivePixelRatio());
  renderer.setClearColor(0xeef4ef, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = false;
  return renderer;
}

function makeLineLoop(THREE, radius, color, opacity = 0.5, segments = 96) {
  const pts = [];
  for (let i = 0; i < segments; i += 1) {
    const a = (i / segments) * Math.PI * 2;
    pts.push(new THREE.Vector3(Math.cos(a) * radius, 0.035, Math.sin(a) * radius));
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(pts);
  return new THREE.LineLoop(geometry, new THREE.LineBasicMaterial({ color, transparent: true, opacity }));
}

function createArenaScene(THREE) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeef4ef);
  scene.fog = new THREE.Fog(0xeef4ef, 45, 95);

  const hemi = new THREE.HemisphereLight(0xffffff, 0x42634f, 2.25);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xffffff, 2.1);
  sun.position.set(18, 34, 12);
  scene.add(sun);

  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(34.8, 96),
    new THREE.MeshStandardMaterial({ color: 0xdceade, roughness: 0.94, metalness: 0.02 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.02;
  scene.add(ground);

  const grid = new THREE.GridHelper(68, 34, 0x789884, 0xb9cebe);
  grid.position.y = 0.01;
  const gridMaterials = Array.isArray(grid.material) ? grid.material : [grid.material];
  gridMaterials.forEach((m) => { m.transparent = true; m.opacity = 0.34; });
  scene.add(grid);

  scene.add(makeLineLoop(THREE, 10.5, 0x2f7450, 0.5));
  scene.add(makeLineLoop(THREE, 20.5, 0x2f7450, 0.32));
  scene.add(makeLineLoop(THREE, 30.5, 0x9b2934, 0.28));

  const diameter = new THREE.Mesh(
    new THREE.BoxGeometry(61, 0.08, 0.11),
    new THREE.MeshStandardMaterial({ color: 0x31597a, transparent: true, opacity: 0.52 })
  );
  diameter.position.y = 0.06;
  scene.add(diameter);

  const radius = new THREE.Mesh(
    new THREE.BoxGeometry(0.11, 0.08, 30.5),
    new THREE.MeshStandardMaterial({ color: 0x9a6a1f, transparent: true, opacity: 0.52 })
  );
  radius.position.set(0, 0.065, -15.25);
  scene.add(radius);

  const core = new THREE.Group();
  const base = new THREE.Mesh(
    new THREE.CylinderGeometry(3.25, 4.1, 1.2, 32),
    new THREE.MeshStandardMaterial({ color: 0x163f2d, roughness: 0.55, metalness: 0.12 })
  );
  base.position.y = 0.6;
  core.add(base);
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(4.6, 0.34, 10, 48),
    new THREE.MeshStandardMaterial({ color: 0xd5af3e, roughness: 0.42, metalness: 0.38 })
  );
  ring.rotation.x = Math.PI / 2;
  ring.position.y = 1.1;
  core.add(ring);
  const pi = createTextSprite(THREE, "π", { fontSize: 92, width: 256, height: 256, bg: "rgba(22,63,45,.94)", fg: "#ffffff", border: "#d5af3e" });
  pi.scale.set(3.1, 3.1, 1);
  pi.position.set(0, 3.4, 0);
  core.add(pi);
  scene.add(core);

  const archMaterial = new THREE.MeshStandardMaterial({ color: 0x7d9886, roughness: 0.72, metalness: 0.06 });
  const accents = [
    [-27, -27, 0], [27, -27, Math.PI / 2], [27, 27, Math.PI], [-27, 27, -Math.PI / 2]
  ];
  accents.forEach(([x, z, r]) => {
    const tower = new THREE.Group();
    const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 1, 5.4, 10), archMaterial);
    pillar.position.y = 2.7;
    tower.add(pillar);
    const torus = new THREE.Mesh(new THREE.TorusGeometry(2.1, 0.25, 8, 28, Math.PI), archMaterial);
    torus.rotation.z = Math.PI;
    torus.position.y = 5.4;
    tower.add(torus);
    tower.position.set(x, 0, z);
    tower.rotation.y = r;
    scene.add(tower);
  });

  const axisMaterialX = new THREE.LineBasicMaterial({ color: 0x9b2934, transparent: true, opacity: 0.72 });
  const axisMaterialZ = new THREE.LineBasicMaterial({ color: 0x31597a, transparent: true, opacity: 0.72 });
  const makeAxis = (a, b, material) => new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]), material);
  scene.add(makeAxis(new THREE.Vector3(-33, 0.14, 31.8), new THREE.Vector3(-25, 0.14, 31.8), axisMaterialX));
  scene.add(makeAxis(new THREE.Vector3(-31.8, 0.14, 33), new THREE.Vector3(-31.8, 0.14, 25), axisMaterialZ));

  return scene;
}

function createTextSprite(THREE, text, opts = {}) {
  const width = opts.width || 512;
  const height = opts.height || 128;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  if (opts.bg) {
    ctx.fillStyle = opts.bg;
    roundRect(ctx, 4, 4, width - 8, height - 8, Math.min(30, height * 0.24));
    ctx.fill();
  }
  if (opts.border) {
    ctx.strokeStyle = opts.border;
    ctx.lineWidth = 5;
    roundRect(ctx, 4, 4, width - 8, height - 8, Math.min(30, height * 0.24));
    ctx.stroke();
  }
  ctx.fillStyle = opts.fg || "#ffffff";
  ctx.font = `800 ${opts.fontSize || 44}px system-ui, -apple-system, Segoe UI, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(String(text), width / 2, height / 2 + 1, width - 24);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false, depthWrite: false });
  const sprite = new THREE.Sprite(material);
  sprite.userData.texture = texture;
  return sprite;
}

function roundRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

function createRobot(THREE, color, teamId) {
  const group = new THREE.Group();
  group.userData.teamId = teamId;
  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.54, metalness: 0.17 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x15241b, roughness: 0.72, metalness: 0.08 });
  const lightMat = new THREE.MeshStandardMaterial({ color: 0xe8f4ea, emissive: 0x355f45, emissiveIntensity: 0.6, roughness: 0.38 });

  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.72, 1.15, 4, 8), bodyMat);
  body.position.y = 1.55;
  body.userData.pickTeamId = teamId;
  group.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.58, 12, 8), bodyMat);
  head.scale.y = 0.78;
  head.position.y = 2.86;
  head.userData.pickTeamId = teamId;
  group.add(head);

  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.19, 0.14), lightMat);
  visor.position.set(0, 2.9, -0.53);
  visor.userData.pickTeamId = teamId;
  group.add(visor);

  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.82, 0.92, 0.38, 12), darkMat);
  base.position.y = 0.34;
  base.userData.pickTeamId = teamId;
  group.add(base);

  const armGeo = new THREE.CapsuleGeometry(0.16, 0.74, 3, 6);
  const leftArm = new THREE.Mesh(armGeo, bodyMat);
  leftArm.position.set(-0.88, 1.62, 0);
  leftArm.rotation.z = 0.18;
  leftArm.userData.pickTeamId = teamId;
  group.add(leftArm);
  const rightArm = leftArm.clone();
  rightArm.position.x = 0.88;
  rightArm.rotation.z = -0.18;
  rightArm.userData.pickTeamId = teamId;
  group.add(rightArm);

  const shield = new THREE.Mesh(
    new THREE.SphereGeometry(1.55, 18, 12),
    new THREE.MeshBasicMaterial({ color: 0x5b91c6, transparent: true, opacity: 0.13, wireframe: true, depthWrite: false })
  );
  shield.position.y = 1.55;
  shield.visible = false;
  group.add(shield);
  group.userData.shield = shield;

  const targetRing = new THREE.Mesh(
    new THREE.TorusGeometry(1.22, 0.075, 8, 32),
    new THREE.MeshBasicMaterial({ color: 0xa22634, transparent: true, opacity: 0.95 })
  );
  targetRing.rotation.x = Math.PI / 2;
  targetRing.position.y = 0.07;
  targetRing.visible = false;
  group.add(targetRing);
  group.userData.targetRing = targetRing;

  const meRing = new THREE.Mesh(
    new THREE.TorusGeometry(1.08, 0.09, 8, 32),
    new THREE.MeshBasicMaterial({ color: 0xd5af3e, transparent: true, opacity: 0.95 })
  );
  meRing.rotation.x = Math.PI / 2;
  meRing.position.y = 0.06;
  meRing.visible = false;
  group.add(meRing);
  group.userData.meRing = meRing;

  group.userData.bodyMaterial = bodyMat;
  group.userData.targetPosition = new THREE.Vector3();
  group.userData.lastPosition = new THREE.Vector3();
  group.userData.hitPulse = 0;
  group.userData.shieldPulse = 0;
  return group;
}

function disposeSprite(sprite) {
  try { sprite?.material?.map?.dispose?.(); } catch {}
  try { sprite?.material?.dispose?.(); } catch {}
}

function updateLabel(THREE, player, node) {
  const name = node.querySelector(".nameplate")?.textContent?.replace(" · TÚ", "") || "Equipo";
  const hpWidth = parseFloat(node.querySelector(".hp>i")?.style?.width || "100") || 0;
  const points = Math.round(hpWidth);
  const me = node.classList.contains("me");
  const offline = node.classList.contains("offline");
  const key = `${name}|${points}|${me}|${offline}`;
  if (player.userData.labelKey === key) return;
  player.userData.labelKey = key;
  disposeSprite(player.userData.label);
  if (player.userData.label) player.remove(player.userData.label);
  const labelText = `${me ? "★ " : ""}${name} · ${points} pts`;
  const label = createTextSprite(THREE, labelText, {
    width: 640,
    height: 116,
    fontSize: 40,
    bg: offline ? "rgba(52,63,56,.72)" : "rgba(18,41,29,.90)",
    fg: "#ffffff",
    border: me ? "#d5af3e" : "rgba(255,255,255,.28)",
  });
  label.position.set(0, 4.1, 0);
  label.scale.set(5.4, 0.98, 1);
  player.add(label);
  player.userData.label = label;
}

function syncPlayers() {
  if (!state.THREE || !state.scene) return;
  const THREE = state.THREE;
  const nodes = [...document.querySelectorAll("#avatarLayer .arena-avatar")];
  const ids = new Set(nodes.map((n) => n.dataset.teamId).filter(Boolean));

  for (const [id, player] of state.players) {
    if (!ids.has(id)) {
      disposeSprite(player.userData.label);
      state.scene.remove(player);
      state.players.delete(id);
    }
  }

  nodes.forEach((node, index) => {
    const id = node.dataset.teamId;
    if (!id) return;
    let player = state.players.get(id);
    if (!player) {
      let color = getComputedStyle(node).getPropertyValue("--avatar").trim() || AVATAR_COLORS[index % AVATAR_COLORS.length];
      if (!/^#[0-9a-f]{6}$/i.test(color)) color = AVATAR_COLORS[index % AVATAR_COLORS.length];
      player = createRobot(THREE, color, id);
      const p = worldFromAvatar(node);
      player.position.set(p.x, 0, p.z);
      player.userData.targetPosition.set(p.x, 0, p.z);
      player.userData.lastPosition.copy(player.position);
      state.scene.add(player);
      state.players.set(id, player);
    }
    const p = worldFromAvatar(node);
    player.userData.targetPosition.set(p.x, 0, p.z);
    player.userData.isMe = node.classList.contains("me");
    player.userData.isOffline = node.classList.contains("offline");
    player.userData.targetRing.visible = node.classList.contains("target");
    player.userData.meRing.visible = player.userData.isMe;
    player.userData.shield.visible = node.classList.contains("shielded");
    player.userData.bodyMaterial.opacity = player.userData.isOffline ? 0.5 : 1;
    player.userData.bodyMaterial.transparent = player.userData.isOffline;
    updateLabel(THREE, player, node);
    if (node.classList.contains("target")) state.currentTargetId = id;
    if (node.classList.contains("hit")) player.userData.hitPulse = Math.max(player.userData.hitPulse, 0.48);
    if (node.classList.contains("shield-flash")) player.userData.shieldPulse = Math.max(player.userData.shieldPulse, 0.72);
  });
}

function inferProjectile(child) {
  if (!(child instanceof HTMLElement) || !child.classList.contains("projectile")) return;
  const startLeft = parseFloat(child.style.left || "50");
  const startTop = parseFloat(child.style.top || "50");
  const action = child.classList.contains("pi") ? "pi" : "arc";
  const job = { child, startLeft, startTop, action };
  state.projectileJobs.add(job);
  setTimeout(() => {
    if (!state.projectileJobs.has(job) || !state.THREE || !state.scene) return;
    const endLeft = parseFloat(child.style.left || String(startLeft));
    const endTop = parseFloat(child.style.top || String(startTop));
    spawnProjectile(startLeft, startTop, endLeft, endTop, action);
    state.projectileJobs.delete(job);
  }, 90);
}

function spawnProjectile(sx, sy, ex, ey, action) {
  const THREE = state.THREE;
  const start = percentToWorld(sx, sy);
  const end = percentToWorld(ex, ey);
  const material = new THREE.MeshBasicMaterial({ color: action === "pi" ? 0x9b2934 : 0x2f7450 });
  const geometry = action === "pi" ? new THREE.IcosahedronGeometry(0.42, 1) : new THREE.SphereGeometry(0.28, 10, 8);
  const projectile = new THREE.Mesh(geometry, material);
  projectile.position.set(start.x, 2.0, start.z);
  const halo = new THREE.Mesh(
    new THREE.TorusGeometry(action === "pi" ? 0.75 : 0.52, 0.06, 6, 22),
    new THREE.MeshBasicMaterial({ color: action === "pi" ? 0xe7a5ad : 0x8dd0ab, transparent: true, opacity: 0.72 })
  );
  halo.rotation.x = Math.PI / 2;
  projectile.add(halo);
  state.scene.add(projectile);
  const startTime = performance.now();
  const duration = state.reducedMotion ? 180 : 520;
  const animate = (now) => {
    const t = Math.min(1, (now - startTime) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    projectile.position.x = start.x + (end.x - start.x) * eased;
    projectile.position.z = start.z + (end.z - start.z) * eased;
    projectile.position.y = 2 + Math.sin(Math.PI * t) * (action === "pi" ? 3.0 : 1.9);
    projectile.rotation.y += 0.25;
    halo.rotation.z += 0.12;
    if (t < 1) requestAnimationFrame(animate);
    else {
      state.scene.remove(projectile);
      geometry.dispose(); material.dispose(); halo.geometry.dispose(); halo.material.dispose();
      const nearest = nearestPlayer(end.x, end.z);
      if (nearest) nearest.userData.hitPulse = 0.52;
    }
  };
  requestAnimationFrame(animate);
}

function nearestPlayer(x, z) {
  let best = null;
  let dist = Infinity;
  for (const player of state.players.values()) {
    const d = Math.hypot(player.position.x - x, player.position.z - z);
    if (d < dist) { dist = d; best = player; }
  }
  return dist < 4 ? best : null;
}

function setupObservers() {
  const avatarLayer = document.getElementById("avatarLayer");
  const projectileLayer = document.getElementById("projectileLayer");
  const panel = state.field?.closest(".live-arena-panel");
  if (avatarLayer) {
    state.avatarObserver = new MutationObserver(() => syncPlayers());
    state.avatarObserver.observe(avatarLayer, { childList: true, subtree: true, attributes: true, attributeFilter: ["style", "class"] });
  }
  if (projectileLayer) {
    state.projectileObserver = new MutationObserver((mutations) => {
      for (const mutation of mutations) for (const node of mutation.addedNodes) inferProjectile(node);
    });
    state.projectileObserver.observe(projectileLayer, { childList: true });
  }
  if (panel) {
    state.uiObserver = new MutationObserver(() => updateCombatLighting());
    state.uiObserver.observe(panel, { attributes: true, attributeFilter: ["class"] });
  }
}

function updateCombatLighting() {
  if (!state.scene) return;
  const combat = state.field?.closest(".live-arena-panel")?.classList.contains("combat-ready");
  state.scene.background?.set(combat ? 0xf3e9e9 : 0xeef4ef);
  if (state.scene.fog) state.scene.fog.color.set(combat ? 0xf3e9e9 : 0xeef4ef);
  state.renderer?.setClearColor(combat ? 0xf3e9e9 : 0xeef4ef, 1);
}

function setupInput() {
  const canvas = state.canvas;
  if (!canvas) return;

  canvas.addEventListener("pointerdown", (event) => {
    state.dragging = true;
    state.dragMoved = false;
    state.pointerStart = { x: event.clientX, y: event.clientY };
    state.lastPointer = { x: event.clientX, y: event.clientY };
    try { canvas.setPointerCapture(event.pointerId); } catch {}
    canvas.focus({ preventScroll: true });
  });

  canvas.addEventListener("pointermove", (event) => {
    if (!state.dragging) return;
    const dx = event.clientX - state.lastPointer.x;
    const dy = event.clientY - state.lastPointer.y;
    if (Math.hypot(event.clientX - state.pointerStart.x, event.clientY - state.pointerStart.y) > 5) state.dragMoved = true;
    if (state.dragMoved) {
      state.yaw -= dx * 0.006;
      state.pitch = Math.max(0.24, Math.min(1.08, state.pitch + dy * 0.0045));
    }
    state.lastPointer = { x: event.clientX, y: event.clientY };
  });

  const finishPointer = (event) => {
    if (!state.dragging) return;
    state.dragging = false;
    try { canvas.releasePointerCapture(event.pointerId); } catch {}
    if (!state.dragMoved) selectByRaycast(event);
  };
  canvas.addEventListener("pointerup", finishPointer);
  canvas.addEventListener("pointercancel", () => { state.dragging = false; });
  canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    state.distance = Math.max(10, Math.min(38, state.distance + Math.sign(event.deltaY) * 1.4));
  }, { passive: false });

  canvas.addEventListener("dblclick", () => {
    state.yaw = Math.PI * 0.25;
    state.pitch = 0.52;
    state.distance = 22;
  });

  canvas.addEventListener("webglcontextlost", (event) => {
    event.preventDefault();
    state.contextLost = true;
    showBoot("El contexto 3D se está recuperando…", "warning");
  });
  canvas.addEventListener("webglcontextrestored", () => {
    state.contextLost = false;
    state.bootMessage?.remove();
    state.bootMessage = null;
    syncPlayers();
  });
}

function selectByRaycast(event) {
  if (!state.raycaster || !state.camera || !state.canvas) return;
  const rect = state.canvas.getBoundingClientRect();
  state.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  state.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  state.raycaster.setFromCamera(state.pointer, state.camera);
  const pickables = [];
  for (const player of state.players.values()) player.traverse((obj) => { if (obj.isMesh && obj.userData.pickTeamId) pickables.push(obj); });
  const hit = state.raycaster.intersectObjects(pickables, false)[0];
  const teamId = hit?.object?.userData?.pickTeamId;
  if (!teamId) return;
  const avatar = document.querySelector(`#avatarLayer .arena-avatar[data-team-id="${CSS.escape(teamId)}"]`);
  if (!avatar || avatar.classList.contains("me")) return;
  avatar.click();
}

function resize() {
  if (!state.renderer || !state.camera || !state.field) return;
  const rect = state.field.getBoundingClientRect();
  const width = Math.max(1, Math.round(rect.width));
  const height = Math.max(1, Math.round(rect.height));
  state.renderer.setPixelRatio(adaptivePixelRatio());
  state.renderer.setSize(width, height, false);
  state.camera.aspect = width / height;
  state.camera.updateProjectionMatrix();
}

function updatePlayers(dt) {
  for (const player of state.players.values()) {
    const target = player.userData.targetPosition;
    const previousX = player.position.x;
    const previousZ = player.position.z;
    const alpha = player.userData.isMe ? Math.min(1, dt * 18) : Math.min(1, dt * 7.5);
    player.position.x += (target.x - player.position.x) * alpha;
    player.position.z += (target.z - player.position.z) * alpha;
    const dx = player.position.x - previousX;
    const dz = player.position.z - previousZ;
    if (Math.hypot(dx, dz) > 0.002) player.rotation.y = Math.atan2(dx, dz);

    const moving = Math.hypot(target.x - player.position.x, target.z - player.position.z) > 0.08;
    const bob = state.reducedMotion ? 0 : (moving ? Math.sin(performance.now() * 0.012) * 0.08 : Math.sin(performance.now() * 0.003 + player.id) * 0.025);
    player.position.y = bob;

    if (player.userData.hitPulse > 0) {
      player.userData.hitPulse = Math.max(0, player.userData.hitPulse - dt);
      const k = 1 + Math.sin((0.52 - player.userData.hitPulse) * 42) * 0.11;
      player.scale.set(k, Math.max(0.82, 2 - k), k);
    } else player.scale.set(1, 1, 1);

    if (player.userData.shieldPulse > 0) {
      player.userData.shieldPulse = Math.max(0, player.userData.shieldPulse - dt);
      const shield = player.userData.shield;
      shield.visible = true;
      shield.material.opacity = 0.12 + Math.sin(performance.now() * 0.02) * 0.08;
      if (player.userData.shieldPulse === 0 && !document.querySelector(`#avatarLayer .arena-avatar[data-team-id="${CSS.escape(player.userData.teamId)}"]`)?.classList.contains("shielded")) shield.visible = false;
    }

    if (player.userData.targetRing?.visible && !state.reducedMotion) player.userData.targetRing.rotation.z += dt * 1.8;
  }
}

function updateCamera(dt) {
  if (!state.camera || !state.THREE) return;
  const THREE = state.THREE;
  const me = [...state.players.values()].find((p) => p.userData.isMe);
  const desiredFocus = me ? new THREE.Vector3(me.position.x, 1.6, me.position.z) : new THREE.Vector3(0, 1.2, 0);
  if (!state.cameraFocus) state.cameraFocus = desiredFocus.clone();
  state.cameraFocus.lerp(desiredFocus, Math.min(1, dt * 6));

  const horizontal = Math.cos(state.pitch) * state.distance;
  const offset = new THREE.Vector3(
    Math.sin(state.yaw) * horizontal,
    Math.sin(state.pitch) * state.distance + 3.2,
    Math.cos(state.yaw) * horizontal
  );
  const desiredPos = state.cameraFocus.clone().add(offset);
  state.camera.position.lerp(desiredPos, Math.min(1, dt * 5.5));
  state.camera.lookAt(state.cameraFocus);
}

function animate(now) {
  if (!state.running) return;
  state.raf = requestAnimationFrame(animate);
  if (document.hidden || state.contextLost) return;
  const dt = Math.min(0.05, Math.max(0.001, (now - state.lastFrame) / 1000));
  state.lastFrame = now;
  updatePlayers(dt);
  updateCamera(dt);
  state.renderer.render(state.scene, state.camera);
}

async function boot() {
  state.field = document.getElementById("battlefield");
  if (!state.field) return;
  state.field.dataset.renderer = "threejs";
  if (!hasWebGL()) {
    failGracefully("Este dispositivo no ofrece WebGL estable. Se mantiene la arena 2.5D de respaldo.");
    return;
  }
  showBoot("Cargando arena 3D…");
  try {
    const THREE = await loadThree();
    state.THREE = THREE;
    state.scene = createArenaScene(THREE);
    state.camera = new THREE.PerspectiveCamera(52, 1, 0.1, 180);
    state.camera.position.set(16, 18, 20);
    state.raycaster = new THREE.Raycaster();
    state.pointer = new THREE.Vector2();
    state.renderer = makeRenderer(THREE);
    resize();
    setupObservers();
    setupInput();
    syncPlayers();
    updateCombatLighting();
    state.resizeObserver = new ResizeObserver(resize);
    state.resizeObserver.observe(state.field);
    state.field.classList.add("three-ready");
    state.field.classList.remove("three-fallback");
    state.bootMessage?.remove();
    state.bootMessage = null;
    state.running = true;
    state.lastFrame = performance.now();
    state.raf = requestAnimationFrame(animate);
  } catch (error) {
    failGracefully("No fue posible iniciar Three.js. Se mantiene la arena 2.5D de respaldo.", error);
  }
}

window.addEventListener("pageshow", () => {
  if (!state.running && !state.failed && document.getElementById("battlefield")) boot();
});
window.addEventListener("beforeunload", () => {
  state.running = false;
  cancelAnimationFrame(state.raf);
  state.resizeObserver?.disconnect();
  state.avatarObserver?.disconnect();
  state.projectileObserver?.disconnect();
  state.uiObserver?.disconnect();
});

boot();
