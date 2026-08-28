const API_URL = "https://rlfxnjbqxbozjdzkbwlz.supabase.co/functions/v1/geo8-circle-clash";
const SESSION_KEY = "geo8-circle-clash-session-v1";
const CLIENT_VERSION = "2026.08.28-circle-clash-web-v3-arena";
const ORIGIN_HINT = "https://juanperez238421-cpu.github.io";

const $ = (id) => document.getElementById(id);
const els = {
  joinScreen: $("joinScreen"), gameScreen: $("gameScreen"), joinForm: $("joinForm"), teamName: $("teamName"),
  groupCode: $("groupCode"), joinCode: $("joinCode"), joinButton: $("joinButton"), joinMessage: $("joinMessage"),
  connectionBadge: $("connectionBadge"), connectionText: $("connectionText"), roomLabel: $("roomLabel"),
  phaseLabel: $("phaseLabel"), roundLabel: $("roundLabel"), timerLabel: $("timerLabel"), timerBar: $("timerBar"),
  leaveButton: $("leaveButton"), gradePoints: $("gradePoints"), gradeValue: $("gradeValue"), chargeValue: $("chargeValue"),
  chargeBar: $("chargeBar"), shieldValue: $("shieldValue"), shieldBar: $("shieldBar"), correctValue: $("correctValue"),
  streakValue: $("streakValue"), teamCount: $("teamCount"), teamGrid: $("teamGrid"), skillLabel: $("skillLabel"),
  questionTitle: $("questionTitle"), answerState: $("answerState"), visualLabel: $("visualLabel"), questionPrompt: $("questionPrompt"),
  expressionBox: $("expressionBox"), optionsGrid: $("optionsGrid"), explanationBox: $("explanationBox"), attackPanel: $("attackPanel"),
  attackHint: $("attackHint"), targetSelect: $("targetSelect"), leaderboard: $("leaderboard"), eventFeed: $("eventFeed"),
  toast: $("toast"), finalOverlay: $("finalOverlay"), finalRanking: $("finalRanking"), closeFinal: $("closeFinal"),
  battlefield: $("battlefield"), avatarLayer: $("avatarLayer"), projectileLayer: $("projectileLayer"),
  arenaStatus: $("arenaStatus"), movementHint: $("movementHint")
};

let session = loadSession();
let snapshot = null;
let lastEventId = 0;
let pollTimer = null;
let timerTicker = null;
let serverOffsetMs = 0;
let pollFailures = 0;
let pollInFlight = false;
let answerInFlight = false;
let actionInFlight = false;
let moveInFlight = false;
let finalShown = false;
let finalClosed = false;
let toastTimer = null;
let movementFrame = null;
let movementLastTime = 0;
let lastMoveSentAt = 0;
let localPos = null;
let selectedTargetId = "";
const pressedDirections = new Set();
const avatarNodes = new Map();
const animatedEvents = new Set();

function loadSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed?.team_id || !parsed?.team_token) return null;
    return parsed;
  } catch { return null; }
}

function saveSession(value) {
  session = value;
  if (value) localStorage.setItem(SESSION_KEY, JSON.stringify(value));
  else localStorage.removeItem(SESSION_KEY);
}

function randomHex(bytes = 48) {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  return Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join("");
}

function uuid() {
  if (crypto.randomUUID) return crypto.randomUUID();
  const a = new Uint8Array(16); crypto.getRandomValues(a); a[6] = (a[6] & 15) | 64; a[8] = (a[8] & 63) | 128;
  const h = Array.from(a, b => b.toString(16).padStart(2, "0")).join("");
  return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`;
}

function setConnection(state, text) {
  els.connectionBadge.dataset.state = state;
  els.connectionText.textContent = text;
}

function showToast(message, ms = 2600) {
  clearTimeout(toastTimer);
  els.toast.textContent = message;
  els.toast.hidden = false;
  toastTimer = setTimeout(() => { els.toast.hidden = true; }, ms);
}

async function api(payload, { timeout = 8500, retries = 1 } = {}) {
  let lastError;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Client-Version": CLIENT_VERSION },
        body: JSON.stringify(payload), cache: "no-store", signal: controller.signal
      });
      clearTimeout(timer);
      let data = {};
      try { data = await response.json(); } catch { /* handled below */ }
      if (!response.ok) {
        const error = new Error(data?.error || `http_${response.status}`);
        error.status = response.status; error.data = data; throw error;
      }
      return data;
    } catch (error) {
      clearTimeout(timer); lastError = error;
      const retryable = !error?.status || error.status >= 500 || error.name === "AbortError";
      if (!retryable || attempt === retries) break;
      await new Promise(r => setTimeout(r, 220 * (attempt + 1)));
    }
  }
  throw lastError || new Error("network_error");
}

function errorText(code) {
  const map = {
    invalid_join_data: "Revisa el nombre, grupo y código de sala.", team_name_taken: "Ese nombre ya está usado en esta sala.",
    game_in_progress: "La partida ya comenzó. Usa otra sala.", room_full: "La sala llegó al máximo de 12 equipos.",
    invalid_session: "La sesión ya no es válida. Vuelve a entrar.", already_submitted: "Tu equipo ya respondió esta ronda.",
    already_acted: "Tu equipo ya usó una acción esta ronda.", correct_answer_required: "Solo una respuesta correcta desbloquea la fase de ataque.",
    solve_phase_closed: "La fase de respuesta ya terminó.", attack_phase_closed: "La fase de ataque ya terminó.",
    not_enough_charge: "No tienes suficiente carga para esa acción.", invalid_target: "Selecciona otro equipo como objetivo.",
    invalid_position: "No se pudo sincronizar ese movimiento.", origin_denied: "Este juego solo acepta conexiones desde la página oficial del curso.",
    request_failed: "El servidor rechazó la solicitud."
  };
  return map[code] || "No fue posible completar la acción. Comprueba tu conexión e inténtalo otra vez.";
}

function syncServerClock(serverTime) {
  const parsed = Date.parse(serverTime || "");
  if (Number.isFinite(parsed)) serverOffsetMs = parsed - Date.now();
}
function serverNow() { return Date.now() + serverOffsetMs; }
function phaseEndMs(room) {
  const raw = room?.phase === "lobby" ? room?.lobby_ends_at : room?.phase_ends_at;
  const parsed = Date.parse(raw || "");
  return Number.isFinite(parsed) ? parsed : 0;
}

function updateTimer() {
  if (!snapshot?.room) { els.timerLabel.textContent = "--"; els.timerBar.style.width = "0%"; return; }
  const room = snapshot.room; const end = phaseEndMs(room);
  if (!end || room.phase === "finished") {
    els.timerLabel.textContent = room.phase === "lobby" ? "∞" : "0.0";
    els.timerBar.style.width = room.phase === "finished" ? "0%" : "100%"; return;
  }
  const remaining = Math.max(0, end - serverNow());
  const total = room.phase === "solve" ? 40000 : room.phase === "attack" ? 12000 : 15000;
  els.timerLabel.textContent = `${(remaining / 1000).toFixed(1)}s`;
  els.timerBar.style.width = `${Math.max(0, Math.min(100, (remaining / total) * 100))}%`;
}

function phaseName(phase) { return ({ lobby: "Lobby", solve: "Resolver", attack: "Batalla", finished: "Final" })[phase] || phase || "—"; }
function grade(points) { return Math.max(1, Math.min(5, Number(points || 0) / 20)); }
function clamp(v, min, max) { return Math.max(min, Math.min(max, Number(v))); }
function isOnline(team) {
  const t = Date.parse(team?.last_seen_at || "");
  return Number.isFinite(t) && Math.abs(serverNow() - t) < 8000;
}

function updateStats() {
  const me = snapshot?.me || {}; const pts = Number(me.grade_points || 0);
  els.gradePoints.textContent = String(pts); els.gradeValue.textContent = grade(pts).toFixed(1);
  els.chargeValue.textContent = String(me.attack_charge || 0); els.chargeBar.style.width = `${Math.min(100, (Number(me.attack_charge || 0) / 60) * 100)}%`;
  els.shieldValue.textContent = String(me.shield || 0); els.shieldBar.style.width = `${Math.min(100, (Number(me.shield || 0) / 20) * 100)}%`;
  const total = Number(me.correct_count || 0) + Number(me.wrong_count || 0);
  els.correctValue.textContent = `${me.correct_count || 0} / ${total}`; els.streakValue.textContent = `Racha: ${me.streak || 0}`;
}

function renderTeams() {
  const teams = snapshot?.teams || [];
  els.teamCount.textContent = `${teams.length} ${teams.length === 1 ? "equipo" : "equipos"}`;
  els.teamGrid.textContent = "";
  for (const team of teams) {
    const card = document.createElement("article"); card.className = `team-card${team.id === snapshot?.me?.id ? " me" : ""}`;
    const line = document.createElement("div"); line.className = "team-name-line";
    const name = document.createElement("span"); name.className = "team-name"; name.textContent = team.team_name;
    const dot = document.createElement("span"); dot.className = `online-dot${isOnline(team) ? " online" : ""}`; dot.title = isOnline(team) ? "Conectado" : "Reconectando";
    line.append(name, dot);
    const meta = document.createElement("div"); meta.className = "team-meta";
    const left = document.createElement("span"); left.textContent = `${team.grade_points} pts · ${grade(team.grade_points).toFixed(1)}`;
    const right = document.createElement("span"); right.textContent = `✓ ${team.correct_count} · ◉ ${team.shield}`; meta.append(left, right);
    const track = document.createElement("div"); track.className = "grade-track";
    const fill = document.createElement("div"); fill.className = "grade-fill"; fill.style.width = `${clamp(team.grade_points, 0, 100)}%`;
    track.append(fill); card.append(line, meta, track); els.teamGrid.append(card);
  }
}

function renderLeaderboard(target = els.leaderboard) {
  const teams = [...(snapshot?.teams || [])].sort((a,b) => b.grade_points - a.grade_points || b.correct_count - a.correct_count || b.knowledge_score - a.knowledge_score);
  target.textContent = "";
  teams.forEach((team, index) => {
    const li = document.createElement("li"); if (team.id === snapshot?.me?.id) li.classList.add("me");
    const r = document.createElement("span"); r.className = "rank"; r.textContent = String(index + 1);
    const n = document.createElement("span"); n.className = "rank-name"; n.textContent = team.team_name;
    const p = document.createElement("span"); p.className = "rank-grade"; p.textContent = `${team.grade_points} pts`;
    const g = document.createElement("span"); g.className = "rank-note"; g.textContent = grade(team.grade_points).toFixed(1);
    li.append(r,n,p,g); target.append(li);
  });
}

const AVATAR_COLORS = ["#2f7450","#9b2934","#31597a","#9a6a1f","#6f4b8b","#287a7d","#92573d","#4f6d2e","#7b3d69","#37658c","#8a6a28","#5a5550"];
function ensureAvatar(team, index) {
  let node = avatarNodes.get(team.id);
  if (node) return node;
  node = document.createElement("button"); node.type = "button"; node.className = "arena-avatar"; node.dataset.teamId = team.id;
  node.style.setProperty("--avatar", AVATAR_COLORS[index % AVATAR_COLORS.length]);
  const hp = document.createElement("span"); hp.className = "hp"; const hpi = document.createElement("i"); hp.append(hpi);
  const body = document.createElement("span"); body.className = "body";
  const label = document.createElement("span"); label.className = "nameplate";
  node.append(hp, body, label);
  node.addEventListener("click", () => {
    if (team.id === snapshot?.me?.id) { els.battlefield?.focus(); return; }
    selectTarget(team.id, true);
  });
  avatarNodes.set(team.id, node); els.avatarLayer.append(node); return node;
}

function selectTarget(teamId, announce = false) {
  const valid = (snapshot?.teams || []).some(t => t.id === teamId && t.id !== snapshot?.me?.id);
  if (!valid) return;
  selectedTargetId = teamId;
  if ([...els.targetSelect.options].some(o => o.value === teamId)) els.targetSelect.value = teamId;
  renderArena();
  if (announce) {
    const team = (snapshot?.teams || []).find(t => t.id === teamId);
    showToast(`Objetivo fijado: ${team?.team_name || "equipo rival"}`);
  }
}

function renderArena() {
  if (!els.avatarLayer) return;
  const teams = snapshot?.teams || []; const activeIds = new Set(teams.map(t => t.id));
  for (const [id,node] of avatarNodes) if (!activeIds.has(id)) { node.remove(); avatarNodes.delete(id); }
  const meId = snapshot?.me?.id;
  const meServer = teams.find(t => t.id === meId) || snapshot?.me;
  if (!localPos && meServer) localPos = { x: clamp(meServer.arena_x ?? 50, 4, 96), y: clamp(meServer.arena_y ?? 50, 6, 94) };
  if (localPos && pressedDirections.size === 0 && !moveInFlight && meServer) {
    const sx = clamp(meServer.arena_x ?? localPos.x,4,96), sy = clamp(meServer.arena_y ?? localPos.y,6,94);
    if (Math.hypot(sx-localPos.x,sy-localPos.y) > 4) localPos = {x:sx,y:sy};
  }
  teams.forEach((team,index) => {
    const node = ensureAvatar(team,index); const isMe = team.id === meId;
    const x = isMe && localPos ? localPos.x : clamp(team.arena_x ?? 50,4,96);
    const y = isMe && localPos ? localPos.y : clamp(team.arena_y ?? 50,6,94);
    node.style.left = `${x}%`; node.style.top = `${y}%`;
    node.classList.toggle("me",isMe); node.classList.toggle("target",team.id === selectedTargetId);
    node.classList.toggle("offline",!isOnline(team)); node.classList.toggle("shielded",Number(team.shield||0)>0);
    node.querySelector(".nameplate").textContent = isMe ? `${team.team_name} · TÚ` : team.team_name;
    node.querySelector(".hp>i").style.width = `${clamp(team.grade_points,0,100)}%`;
    node.title = `${team.team_name} · ${team.grade_points} pts${isMe ? " · Tu equipo" : " · Clic para apuntar"}`;
  });
  els.battlefield.closest(".live-arena-panel")?.classList.toggle("combat-ready",snapshot?.room?.phase === "attack");
  if (snapshot?.room?.phase === "attack") els.arenaStatus.textContent = selectedTargetId ? "Objetivo fijado · elige tu ataque" : "Haz clic en un rival para apuntar";
  else if (pressedDirections.size) els.arenaStatus.textContent = "Moviéndote en la arena…";
  else els.arenaStatus.textContent = "WASD / flechas para moverte";
}

function renderLocalAvatarPosition() {
  const node = snapshot?.me?.id ? avatarNodes.get(snapshot.me.id) : null;
  if (!node || !localPos) return;
  node.style.left = `${localPos.x}%`; node.style.top = `${localPos.y}%`;
}

async function sendMove() {
  if (!session || !localPos || moveInFlight || snapshot?.room?.phase === "finished") return;
  moveInFlight = true; lastMoveSentAt = performance.now();
  const sent = {x:localPos.x,y:localPos.y};
  try {
    await api({ action:"move", team_id:session.team_id, team_token:session.team_token, x:Number(sent.x.toFixed(2)), y:Number(sent.y.toFixed(2)) }, {timeout:3500,retries:0});
  } catch (error) {
    if (error?.status === 401) showToast("Tu sesión de movimiento expiró. Reconectando…");
  } finally { moveInFlight = false; }
}

function movementVector() {
  let dx = 0, dy = 0;
  if (pressedDirections.has("left")) dx -= 1; if (pressedDirections.has("right")) dx += 1;
  if (pressedDirections.has("up")) dy -= 1; if (pressedDirections.has("down")) dy += 1;
  if (dx && dy) { const k = Math.SQRT1_2; dx *= k; dy *= k; }
  return {dx,dy};
}

function movementStep(now) {
  if (!session) { movementFrame = null; return; }
  if (!movementLastTime) movementLastTime = now;
  const dt = Math.min(.05,(now-movementLastTime)/1000); movementLastTime = now;
  const {dx,dy} = movementVector();
  if ((dx || dy) && snapshot?.room?.phase !== "finished") {
    if (!localPos) localPos = {x:50,y:50};
    const speed = 26;
    localPos.x = clamp(localPos.x + dx*speed*dt,4,96); localPos.y = clamp(localPos.y + dy*speed*dt,6,94);
    renderLocalAvatarPosition();
    if (now-lastMoveSentAt >= 220) sendMove();
  }
  movementFrame = requestAnimationFrame(movementStep);
}
function startMovementLoop() { if (!movementFrame) { movementLastTime = performance.now(); movementFrame = requestAnimationFrame(movementStep); } }
function stopMovementLoop() { if (movementFrame) cancelAnimationFrame(movementFrame); movementFrame = null; movementLastTime = 0; pressedDirections.clear(); }

function setQuestionVisual(question) { els.visualLabel.textContent = question?.visual?.label || "r · d · π"; }
function renderQuestion() {
  const room = snapshot?.room || {}; const q = snapshot?.question; const submission = snapshot?.submission; const solving = room.phase === "solve";
  if (!q) {
    els.skillLabel.textContent = room.phase === "lobby" ? "PREPARACIÓN" : "CÍRCULO";
    els.questionTitle.textContent = room.phase === "lobby" ? "Esperando equipos…" : "Sin pregunta";
    els.questionPrompt.textContent = room.phase === "lobby" ? "Muévete por la arena mientras entra el segundo equipo." : "Esperando al servidor.";
    els.expressionBox.textContent = "C = πd = 2πr · A = πr²"; els.optionsGrid.textContent = ""; els.explanationBox.hidden = true;
    els.answerState.textContent = "Sin respuesta"; els.answerState.className = "pill neutral"; return;
  }
  els.skillLabel.textContent = q.skill || "CÍRCULO"; els.questionTitle.textContent = `Ronda ${q.round}`;
  els.questionPrompt.textContent = q.prompt || ""; els.expressionBox.textContent = q.expression || ""; setQuestionVisual(q);
  els.optionsGrid.textContent = ""; const selected = submission?.selected_option || ""; const revealed = Boolean(q.correct_option);
  for (const key of ["A","B","C","D"]) {
    const button = document.createElement("button"); button.type = "button"; button.className = "option-button"; button.dataset.option = key;
    const k = document.createElement("span"); k.className = "option-key"; k.textContent = key;
    const text = document.createElement("span"); text.textContent = q.options?.[key] || ""; button.append(k,text);
    if (selected === key) button.classList.add("selected"); if (revealed && q.correct_option === key) button.classList.add("correct");
    if (revealed && selected === key && selected !== q.correct_option) button.classList.add("wrong");
    button.disabled = !solving || Boolean(submission) || answerInFlight; button.addEventListener("click",()=>submitAnswer(key)); els.optionsGrid.append(button);
  }
  if (submission) {
    if (revealed) { const ok = Boolean(submission.correct); els.answerState.textContent = ok ? "Correcta" : "Incorrecta"; els.answerState.className = `pill ${ok ? "correct-state" : "wrong-state"}`; }
    else { els.answerState.textContent = "Respuesta enviada"; els.answerState.className = "pill"; }
  } else { els.answerState.textContent = solving ? "Elige una opción" : "Sin respuesta"; els.answerState.className = "pill neutral"; }
  if (revealed && q.explanation) { els.explanationBox.textContent = q.explanation; els.explanationBox.hidden = false; } else els.explanationBox.hidden = true;
}

function renderTargets() {
  const current = selectedTargetId || els.targetSelect.value; els.targetSelect.textContent = "";
  const others = (snapshot?.teams || []).filter(t => t.id !== snapshot?.me?.id);
  for (const team of others) { const option = document.createElement("option"); option.value = team.id; option.textContent = `${team.team_name} · ${team.grade_points} pts`; els.targetSelect.append(option); }
  if (others.some(t=>t.id===current)) { els.targetSelect.value = current; selectedTargetId = current; }
  else if (others[0]) { els.targetSelect.value = others[0].id; selectedTargetId = others[0].id; }
}

function renderAttack() {
  const room = snapshot?.room || {}; const submission = snapshot?.submission; const action = snapshot?.action; const show = room.phase === "attack";
  els.attackPanel.hidden = !show; if (!show) return; renderTargets();
  const canAttack = Boolean(submission?.correct) && !action; const charge = Number(snapshot?.me?.attack_charge || 0); const costs = {arc:10,pi:16,shield:12};
  document.querySelectorAll(".action-button").forEach(button=>{const type=button.dataset.action;button.disabled=!canAttack||actionInFlight||charge<costs[type];});
  if (!submission) els.attackHint.textContent = "No respondiste esta ronda";
  else if (!submission.correct) els.attackHint.textContent = "Respuesta incorrecta · sin ataque";
  else if (action) els.attackHint.textContent = "Acción realizada";
  else els.attackHint.textContent = selectedTargetId ? "Objetivo fijado · dispara" : "Selecciona un rival en la arena";
}

function eventMessage(event) {
  const p = event?.payload || {};
  switch (event?.event_type) {
    case "team_joined": return `${p.team_name || "Un equipo"} entró a la arena.`;
    case "lobby_countdown": return "La partida inicia en 15 segundos.";
    case "round_start": return `Comienza la ronda ${event.round_no}.`;
    case "attack_phase": return `Ronda ${event.round_no}: se abre la fase de batalla.`;
    case "answer_correct": return `${p.team_name || "Equipo"} respondió correctamente.`;
    case "answer_wrong": return `${p.team_name || "Equipo"} falló y perdió puntos.`;
    case "attack": return `${p.team_name || "Equipo"} atacó a ${p.target_name || "otro equipo"}: −${p.damage || 0} pts.`;
    case "shield": return `${p.team_name || "Equipo"} activó escudo: +${p.shield_added || 0}.`;
    case "game_finished": return "La partida terminó. Clasificación final disponible.";
    default: return "Evento de partida actualizado.";
  }
}

function animateCombatEvents(events = []) {
  for (const event of events) {
    const id = Number(event?.id || 0); if (!id || animatedEvents.has(id)) continue; animatedEvents.add(id);
    if (event.event_type === "attack" && event.actor_team_id && event.target_team_id) {
      const actor = (snapshot?.teams || []).find(t=>t.id===event.actor_team_id); const target = (snapshot?.teams || []).find(t=>t.id===event.target_team_id);
      if (!actor || !target || !els.projectileLayer) continue;
      const projectile = document.createElement("span"); const action = event?.payload?.action === "pi" ? "pi" : "arc";
      projectile.className = `projectile ${action}`; projectile.style.left = `${clamp(actor.arena_x,4,96)}%`; projectile.style.top = `${clamp(actor.arena_y,6,94)}%`; els.projectileLayer.append(projectile);
      requestAnimationFrame(()=>requestAnimationFrame(()=>{ projectile.style.left = `${clamp(target.arena_x,4,96)}%`; projectile.style.top = `${clamp(target.arena_y,6,94)}%`; }));
      setTimeout(()=>{ projectile.remove(); const node=avatarNodes.get(target.id); if(node){node.classList.add("hit");setTimeout(()=>node.classList.remove("hit"),500);} },520);
    }
    if (event.event_type === "shield" && event.actor_team_id) {
      const node = avatarNodes.get(event.actor_team_id); if (node) { node.classList.add("shield-flash"); setTimeout(()=>node.classList.remove("shield-flash"),750); }
    }
  }
  if (animatedEvents.size > 300) animatedEvents.clear();
}

function renderEvents(newEvents = []) {
  for (const event of newEvents) {
    if (Number(event.id || 0) <= lastEventId) continue;
    lastEventId = Math.max(lastEventId, Number(event.id || 0));
    const div = document.createElement("div"); const type = event.event_type === "attack" ? "attack" : event.event_type === "answer_correct" ? "correct" : event.event_type === "answer_wrong" ? "wrong" : "";
    div.className = `event ${type}`.trim(); div.textContent = eventMessage(event); els.eventFeed.append(div);
  }
  while (els.eventFeed.children.length > 60) els.eventFeed.firstChild.remove(); els.eventFeed.scrollTop = els.eventFeed.scrollHeight;
}

function renderRoom() {
  const room = snapshot?.room || {}; els.roomLabel.textContent = `Sala ${room.join_code || session?.join_code || "—"} · ${room.group_code || session?.group_code || "—"}`;
  els.phaseLabel.textContent = phaseName(room.phase); els.roundLabel.textContent = `Ronda ${room.current_round || 0} / ${room.round_count || 12}`;
}
function renderFinal() {
  if (snapshot?.room?.phase !== "finished") return; renderLeaderboard(els.finalRanking);
  if (!finalShown && !finalClosed) { finalShown = true; els.finalOverlay.hidden = false; }
}
function renderAll(newEvents = []) {
  renderRoom(); updateStats(); renderTeams(); renderArena(); renderLeaderboard(); renderQuestion(); renderAttack(); animateCombatEvents(newEvents); renderEvents(newEvents); renderFinal(); updateTimer();
}

async function submitAnswer(option) {
  if (!session || answerInFlight || snapshot?.room?.phase !== "solve" || snapshot?.submission) return;
  answerInFlight = true; renderQuestion(); const eventId = uuid();
  try {
    const result = await api({action:"submit",team_id:session.team_id,team_token:session.team_token,client_event_id:eventId,round_no:snapshot.room.current_round,selected_option:option},{retries:2});
    if (result.correct) showToast(`¡Correcto! +${result.awarded_charge || 0} carga. Prepárate para atacar.`);
    else showToast(`Respuesta incorrecta. −${result.grade_penalty || 0} puntos.`);
    await pollSnapshot({immediate:true});
  } catch (error) { showToast(errorText(error?.data?.error || error?.message)); }
  finally { answerInFlight = false; renderQuestion(); }
}

async function performAction(type) {
  if (!session || actionInFlight || snapshot?.room?.phase !== "attack" || snapshot?.action) return;
  actionInFlight = true; renderAttack(); const target = type === "shield" ? null : (selectedTargetId || els.targetSelect.value); const eventId = uuid();
  try {
    const result = await api({action:"battle_action",team_id:session.team_id,team_token:session.team_token,client_event_id:eventId,round_no:snapshot.room.current_round,battle_action:type,target_team_id:target},{retries:2});
    if (type === "shield") showToast(`Escudo activado: +${result.shield_added || 0}.`); else showToast(`Impacto confirmado: −${result.damage || 0} puntos.`);
    await pollSnapshot({immediate:true});
  } catch (error) { showToast(errorText(error?.data?.error || error?.message)); }
  finally { actionInFlight = false; renderAttack(); }
}

function nextPollDelay() {
  if (document.hidden) return 3000; if (!snapshot?.room) return 1300;
  if (snapshot.room.phase === "solve" || snapshot.room.phase === "attack") return 650;
  if (snapshot.room.phase === "finished") return 2500; return 850;
}
function schedulePoll(delay = nextPollDelay()) { clearTimeout(pollTimer); if (!session) return; pollTimer = setTimeout(()=>pollSnapshot(),delay); }
async function pollSnapshot({immediate=false}={}) {
  if (!session || pollInFlight) { if (!immediate) schedulePoll(); return; }
  pollInFlight = true;
  try {
    const data = await api({action:"snapshot",team_id:session.team_id,team_token:session.team_token,last_event_id:lastEventId},{retries:immediate?1:0});
    snapshot = data; syncServerClock(data.server_time); pollFailures = 0; setConnection("ok","Servidor sincronizado"); renderAll(data.events || []);
  } catch (error) {
    pollFailures += 1; setConnection(pollFailures < 3 ? "warn" : "bad", navigator.onLine ? "Reconectando…" : "Sin Internet");
    if (error?.status === 401 || error?.data?.error === "invalid_session") { stopPolling(); saveSession(null); snapshot=null; showJoin(); els.joinMessage.textContent="La sesión expiró. Vuelve a entrar."; return; }
  } finally { pollInFlight = false; }
  const backoff = Math.min(5500,nextPollDelay()*Math.max(1,2**Math.min(3,pollFailures))); schedulePoll(backoff);
}

function startPolling() { stopPolling(); timerTicker = setInterval(updateTimer,100); startMovementLoop(); pollSnapshot({immediate:true}); }
function stopPolling() { clearTimeout(pollTimer); pollTimer=null; clearInterval(timerTicker); timerTicker=null; pollInFlight=false; stopMovementLoop(); }
function showGame() { els.joinScreen.hidden=true; els.gameScreen.hidden=false; }
function showJoin() { els.joinScreen.hidden=false; els.gameScreen.hidden=true; setConnection("idle","Sin conexión"); }

async function joinGame(event) {
  event.preventDefault(); els.joinMessage.textContent=""; const teamName=els.teamName.value.trim(); const groupCode=els.groupCode.value; const joinCode=els.joinCode.value.trim().toUpperCase(); els.joinCode.value=joinCode;
  const teamToken=randomHex(48); const clientJoinId=uuid(); els.joinButton.disabled=true; setConnection("warn","Conectando…");
  try {
    const data=await api({action:"join",join_code:joinCode,group_code:groupCode,team_name:teamName,team_token:teamToken,client_join_id:clientJoinId},{retries:2});
    saveSession({team_id:data.session.team_id,team_token:teamToken,client_join_id:clientJoinId,join_code:joinCode,group_code:groupCode,team_name:teamName,origin_hint:ORIGIN_HINT});
    snapshot=data.snapshot; lastEventId=0; syncServerClock(snapshot.server_time); finalShown=false; finalClosed=false; selectedTargetId="";
    localPos={x:clamp(snapshot?.me?.arena_x ?? 50,4,96),y:clamp(snapshot?.me?.arena_y ?? 50,6,94)};
    showGame(); setConnection("ok","Servidor sincronizado"); renderAll(snapshot.events||[]); startPolling(); setTimeout(()=>els.battlefield?.focus(),80);
  } catch(error) { els.joinMessage.textContent=errorText(error?.data?.error||error?.message); setConnection("bad","No conectado"); }
  finally { els.joinButton.disabled=false; }
}

function leaveGame() {
  stopPolling(); saveSession(null); snapshot=null; localPos=null; selectedTargetId=""; lastEventId=0; finalShown=false; finalClosed=false; els.eventFeed.textContent="";
  for (const node of avatarNodes.values()) node.remove(); avatarNodes.clear(); els.projectileLayer.textContent=""; showJoin();
}
async function resume() {
  if (!session) { showJoin(); return; }
  showGame(); setConnection("warn","Recuperando sesión…"); startPolling(); setTimeout(()=>els.battlefield?.focus(),100);
}

function editableTarget(target) { return target instanceof HTMLInputElement || target instanceof HTMLSelectElement || target instanceof HTMLTextAreaElement || target instanceof HTMLButtonElement || target?.isContentEditable; }
const KEY_TO_DIR = {ArrowUp:"up",w:"up",W:"up",ArrowDown:"down",s:"down",S:"down",ArrowLeft:"left",a:"left",A:"left",ArrowRight:"right",d:"right",D:"right"};
window.addEventListener("keydown",event=>{ const dir=KEY_TO_DIR[event.key]; if(!dir||!session||editableTarget(event.target))return; event.preventDefault(); pressedDirections.add(dir); document.querySelector(`.move-button[data-move="${dir}"]`)?.classList.add("active"); });
window.addEventListener("keyup",event=>{ const dir=KEY_TO_DIR[event.key]; if(!dir)return; pressedDirections.delete(dir); document.querySelector(`.move-button[data-move="${dir}"]`)?.classList.remove("active"); if(pressedDirections.size===0) sendMove(); });
window.addEventListener("blur",()=>{ pressedDirections.clear(); document.querySelectorAll(".move-button.active").forEach(b=>b.classList.remove("active")); });

document.querySelectorAll(".move-button").forEach(button=>{
  const dir=button.dataset.move;
  const press=event=>{event.preventDefault();pressedDirections.add(dir);button.classList.add("active");els.battlefield?.focus();};
  const release=event=>{event.preventDefault();pressedDirections.delete(dir);button.classList.remove("active");if(pressedDirections.size===0)sendMove();};
  button.addEventListener("pointerdown",press); button.addEventListener("pointerup",release); button.addEventListener("pointercancel",release); button.addEventListener("pointerleave",event=>{if(event.buttons)release(event);});
});

els.joinForm.addEventListener("submit",joinGame);
els.leaveButton.addEventListener("click",leaveGame);
els.closeFinal.addEventListener("click",()=>{finalClosed=true;els.finalOverlay.hidden=true;});
document.querySelectorAll(".action-button").forEach(button=>button.addEventListener("click",()=>performAction(button.dataset.action)));
els.targetSelect.addEventListener("change",()=>{selectedTargetId=els.targetSelect.value;renderArena();});
els.joinCode.addEventListener("input",()=>{els.joinCode.value=els.joinCode.value.toUpperCase().replace(/[^A-Z0-9-]/g,"").slice(0,12);});
window.addEventListener("online",()=>{setConnection("warn","Reconectando…");pollSnapshot({immediate:true});});
window.addEventListener("offline",()=>setConnection("bad","Sin Internet"));
document.addEventListener("visibilitychange",()=>{if(!document.hidden&&session)pollSnapshot({immediate:true});});
window.addEventListener("beforeunload",stopPolling);

resume();
