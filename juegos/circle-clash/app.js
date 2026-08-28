const API_URL = "https://rlfxnjbqxbozjdzkbwlz.supabase.co/functions/v1/geo8-circle-clash";
const SESSION_KEY = "geo8-circle-clash-session-v1";
const CLIENT_VERSION = "2026.08.28-circle-clash-web-v1";
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
  toast: $("toast"), finalOverlay: $("finalOverlay"), finalRanking: $("finalRanking"), closeFinal: $("closeFinal")
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
let finalShown = false;
let finalClosed = false;
let toastTimer = null;

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
        body: JSON.stringify(payload),
        cache: "no-store",
        signal: controller.signal
      });
      clearTimeout(timer);
      let data = {};
      try { data = await response.json(); } catch { /* handled below */ }
      if (!response.ok) {
        const error = new Error(data?.error || `http_${response.status}`);
        error.status = response.status;
        error.data = data;
        throw error;
      }
      return data;
    } catch (error) {
      clearTimeout(timer);
      lastError = error;
      const retryable = !error?.status || error.status >= 500 || error.name === "AbortError";
      if (!retryable || attempt === retries) break;
      await new Promise(r => setTimeout(r, 250 * (attempt + 1)));
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
    origin_denied: "Este juego solo acepta conexiones desde la página oficial del curso.", request_failed: "El servidor rechazó la solicitud."
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
  if (!snapshot?.room) {
    els.timerLabel.textContent = "--";
    els.timerBar.style.width = "0%";
    return;
  }
  const room = snapshot.room;
  const end = phaseEndMs(room);
  if (!end || room.phase === "finished") {
    els.timerLabel.textContent = room.phase === "lobby" ? "∞" : "0.0";
    els.timerBar.style.width = room.phase === "finished" ? "0%" : "100%";
    return;
  }
  const remaining = Math.max(0, end - serverNow());
  const total = room.phase === "solve" ? 40000 : room.phase === "attack" ? 12000 : 15000;
  els.timerLabel.textContent = `${(remaining / 1000).toFixed(1)}s`;
  els.timerBar.style.width = `${Math.max(0, Math.min(100, (remaining / total) * 100))}%`;
}

function phaseName(phase) {
  return ({ lobby: "Lobby", solve: "Resolver", attack: "Batalla", finished: "Final" })[phase] || phase || "—";
}

function grade(points) { return Math.max(1, Math.min(5, Number(points || 0) / 20)); }

function updateStats() {
  const me = snapshot?.me || {};
  const pts = Number(me.grade_points || 0);
  els.gradePoints.textContent = String(pts);
  els.gradeValue.textContent = grade(pts).toFixed(1);
  els.chargeValue.textContent = String(me.attack_charge || 0);
  els.chargeBar.style.width = `${Math.min(100, (Number(me.attack_charge || 0) / 60) * 100)}%`;
  els.shieldValue.textContent = String(me.shield || 0);
  els.shieldBar.style.width = `${Math.min(100, (Number(me.shield || 0) / 20) * 100)}%`;
  const total = Number(me.correct_count || 0) + Number(me.wrong_count || 0);
  els.correctValue.textContent = `${me.correct_count || 0} / ${total}`;
  els.streakValue.textContent = `Racha: ${me.streak || 0}`;
}

function isOnline(team) {
  const t = Date.parse(team?.last_seen_at || "");
  return Number.isFinite(t) && Math.abs(serverNow() - t) < 8000;
}

function renderTeams() {
  const teams = snapshot?.teams || [];
  els.teamCount.textContent = `${teams.length} ${teams.length === 1 ? "equipo" : "equipos"}`;
  els.teamGrid.textContent = "";
  for (const team of teams) {
    const card = document.createElement("article");
    card.className = `team-card${team.id === snapshot?.me?.id ? " me" : ""}`;
    const line = document.createElement("div"); line.className = "team-name-line";
    const name = document.createElement("span"); name.className = "team-name"; name.textContent = team.team_name;
    const dot = document.createElement("span"); dot.className = `online-dot${isOnline(team) ? " online" : ""}`; dot.title = isOnline(team) ? "Conectado" : "Reconectando";
    line.append(name, dot);
    const meta = document.createElement("div"); meta.className = "team-meta";
    const left = document.createElement("span"); left.textContent = `${team.grade_points} pts · ${grade(team.grade_points).toFixed(1)}`;
    const right = document.createElement("span"); right.textContent = `✓ ${team.correct_count} · ◉ ${team.shield}`;
    meta.append(left, right);
    const track = document.createElement("div"); track.className = "grade-track";
    const fill = document.createElement("div"); fill.className = "grade-fill"; fill.style.width = `${Math.max(0, Math.min(100, team.grade_points))}%`;
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

function setQuestionVisual(question) {
  const label = question?.visual?.label || "r · d · π";
  els.visualLabel.textContent = label;
}

function renderQuestion() {
  const room = snapshot?.room || {};
  const q = snapshot?.question;
  const submission = snapshot?.submission;
  const phase = room.phase;
  const solving = phase === "solve";

  if (!q) {
    els.skillLabel.textContent = phase === "lobby" ? "PREPARACIÓN" : "CÍRCULO";
    els.questionTitle.textContent = phase === "lobby" ? "Esperando equipos…" : "Sin pregunta";
    els.questionPrompt.textContent = phase === "lobby" ? "La partida inicia automáticamente cuando hay al menos dos equipos." : "Esperando al servidor.";
    els.expressionBox.textContent = "C = πd = 2πr · A = πr²";
    els.optionsGrid.textContent = "";
    els.explanationBox.hidden = true;
    els.answerState.textContent = "Sin respuesta";
    els.answerState.className = "pill neutral";
    return;
  }

  els.skillLabel.textContent = q.skill || "CÍRCULO";
  els.questionTitle.textContent = `Ronda ${q.round}`;
  els.questionPrompt.textContent = q.prompt || "";
  els.expressionBox.textContent = q.expression || "";
  setQuestionVisual(q);
  els.optionsGrid.textContent = "";
  const selected = submission?.selected_option || "";
  const revealed = Boolean(q.correct_option);

  for (const key of ["A","B","C","D"]) {
    const button = document.createElement("button");
    button.type = "button"; button.className = "option-button"; button.dataset.option = key;
    const k = document.createElement("span"); k.className = "option-key"; k.textContent = key;
    const text = document.createElement("span"); text.textContent = q.options?.[key] || "";
    button.append(k, text);
    if (selected === key) button.classList.add("selected");
    if (revealed && q.correct_option === key) button.classList.add("correct");
    if (revealed && selected === key && selected !== q.correct_option) button.classList.add("wrong");
    button.disabled = !solving || Boolean(submission) || answerInFlight;
    button.addEventListener("click", () => submitAnswer(key));
    els.optionsGrid.append(button);
  }

  if (submission) {
    if (revealed) {
      const ok = Boolean(submission.correct);
      els.answerState.textContent = ok ? "Correcta" : "Incorrecta";
      els.answerState.className = `pill ${ok ? "correct-state" : "wrong-state"}`;
    } else {
      els.answerState.textContent = "Respuesta enviada";
      els.answerState.className = "pill";
    }
  } else {
    els.answerState.textContent = solving ? "Elige una opción" : "Sin respuesta";
    els.answerState.className = "pill neutral";
  }

  if (revealed && q.explanation) {
    els.explanationBox.textContent = q.explanation;
    els.explanationBox.hidden = false;
  } else {
    els.explanationBox.hidden = true;
  }
}

function renderTargets() {
  const current = els.targetSelect.value;
  els.targetSelect.textContent = "";
  const others = (snapshot?.teams || []).filter(t => t.id !== snapshot?.me?.id);
  for (const team of others) {
    const option = document.createElement("option");
    option.value = team.id;
    option.textContent = `${team.team_name} · ${team.grade_points} pts`;
    els.targetSelect.append(option);
  }
  if (others.some(t => t.id === current)) els.targetSelect.value = current;
}

function renderAttack() {
  const room = snapshot?.room || {};
  const submission = snapshot?.submission;
  const action = snapshot?.action;
  const show = room.phase === "attack";
  els.attackPanel.hidden = !show;
  if (!show) return;
  renderTargets();
  const canAttack = Boolean(submission?.correct) && !action;
  const charge = Number(snapshot?.me?.attack_charge || 0);
  const costs = { arc: 10, pi: 16, shield: 12 };
  document.querySelectorAll(".action-button").forEach(button => {
    const type = button.dataset.action;
    button.disabled = !canAttack || actionInFlight || charge < costs[type];
  });
  if (!submission) els.attackHint.textContent = "No respondiste esta ronda";
  else if (!submission.correct) els.attackHint.textContent = "Respuesta incorrecta · sin ataque";
  else if (action) els.attackHint.textContent = "Acción realizada";
  else els.attackHint.textContent = "Respuesta correcta · ataca o protege";
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

function renderEvents(newEvents = []) {
  for (const event of newEvents) {
    if (Number(event.id || 0) <= lastEventId) continue;
    lastEventId = Math.max(lastEventId, Number(event.id || 0));
    const div = document.createElement("div");
    const type = event.event_type === "attack" ? "attack" : event.event_type === "answer_correct" ? "correct" : event.event_type === "answer_wrong" ? "wrong" : "";
    div.className = `event ${type}`.trim();
    div.textContent = eventMessage(event);
    els.eventFeed.append(div);
  }
  while (els.eventFeed.children.length > 60) els.eventFeed.firstChild.remove();
  els.eventFeed.scrollTop = els.eventFeed.scrollHeight;
}

function renderRoom() {
  const room = snapshot?.room || {};
  els.roomLabel.textContent = `Sala ${room.join_code || session?.join_code || "—"} · ${room.group_code || session?.group_code || "—"}`;
  els.phaseLabel.textContent = phaseName(room.phase);
  els.roundLabel.textContent = `Ronda ${room.current_round || 0} / ${room.round_count || 12}`;
}

function renderFinal() {
  if (snapshot?.room?.phase !== "finished") return;
  renderLeaderboard(els.finalRanking);
  if (!finalShown && !finalClosed) {
    finalShown = true;
    els.finalOverlay.hidden = false;
  }
}

function renderAll(newEvents = []) {
  renderRoom(); updateStats(); renderTeams(); renderLeaderboard(); renderQuestion(); renderAttack(); renderEvents(newEvents); renderFinal(); updateTimer();
}

async function submitAnswer(option) {
  if (!session || answerInFlight || snapshot?.room?.phase !== "solve" || snapshot?.submission) return;
  answerInFlight = true;
  renderQuestion();
  const eventId = uuid();
  try {
    const result = await api({
      action: "submit", team_id: session.team_id, team_token: session.team_token,
      client_event_id: eventId, round_no: snapshot.room.current_round, selected_option: option
    }, { retries: 2 });
    if (result.correct) showToast(`¡Correcto! +${result.awarded_charge || 0} de carga de ataque.`);
    else showToast(`Respuesta incorrecta. −${result.grade_penalty || 0} puntos.`);
    await pollSnapshot({ immediate: true });
  } catch (error) {
    showToast(errorText(error?.data?.error || error?.message));
  } finally {
    answerInFlight = false;
    renderQuestion();
  }
}

async function performAction(type) {
  if (!session || actionInFlight || snapshot?.room?.phase !== "attack" || snapshot?.action) return;
  actionInFlight = true; renderAttack();
  const target = type === "shield" ? null : els.targetSelect.value;
  const eventId = uuid();
  try {
    const result = await api({
      action: "battle_action", team_id: session.team_id, team_token: session.team_token,
      client_event_id: eventId, round_no: snapshot.room.current_round,
      battle_action: type, target_team_id: target
    }, { retries: 2 });
    if (type === "shield") showToast(`Escudo activado: +${result.shield_added || 0}.`);
    else showToast(`Ataque confirmado: −${result.damage || 0} puntos al objetivo.`);
    await pollSnapshot({ immediate: true });
  } catch (error) {
    showToast(errorText(error?.data?.error || error?.message));
  } finally {
    actionInFlight = false; renderAttack();
  }
}

function nextPollDelay() {
  if (document.hidden) return 3500;
  if (!snapshot?.room) return 1600;
  if (snapshot.room.phase === "solve" || snapshot.room.phase === "attack") return 900;
  if (snapshot.room.phase === "finished") return 3000;
  return 1400;
}

function schedulePoll(delay = nextPollDelay()) {
  clearTimeout(pollTimer);
  if (!session) return;
  pollTimer = setTimeout(() => pollSnapshot(), delay);
}

async function pollSnapshot({ immediate = false } = {}) {
  if (!session || pollInFlight) {
    if (!immediate) schedulePoll();
    return;
  }
  pollInFlight = true;
  try {
    const data = await api({ action: "snapshot", team_id: session.team_id, team_token: session.team_token, last_event_id: lastEventId }, { retries: immediate ? 1 : 0 });
    snapshot = data; syncServerClock(data.server_time); pollFailures = 0;
    setConnection("ok", "Servidor sincronizado");
    renderAll(data.events || []);
  } catch (error) {
    pollFailures += 1;
    setConnection(pollFailures < 3 ? "warn" : "bad", navigator.onLine ? "Reconectando…" : "Sin Internet");
    if (error?.status === 401 || error?.data?.error === "invalid_session") {
      stopPolling(); saveSession(null); snapshot = null; showJoin(); els.joinMessage.textContent = "La sesión expiró. Vuelve a entrar."; return;
    }
  } finally {
    pollInFlight = false;
  }
  const backoff = Math.min(6000, nextPollDelay() * Math.max(1, 2 ** Math.min(3, pollFailures)));
  schedulePoll(backoff);
}

function startPolling() {
  stopPolling();
  timerTicker = setInterval(updateTimer, 100);
  pollSnapshot({ immediate: true });
}

function stopPolling() {
  clearTimeout(pollTimer); pollTimer = null;
  clearInterval(timerTicker); timerTicker = null;
  pollInFlight = false;
}

function showGame() {
  els.joinScreen.hidden = true; els.gameScreen.hidden = false;
}

function showJoin() {
  els.joinScreen.hidden = false; els.gameScreen.hidden = true;
  setConnection("idle", "Sin conexión");
}

async function joinGame(event) {
  event.preventDefault();
  els.joinMessage.textContent = "";
  const teamName = els.teamName.value.trim();
  const groupCode = els.groupCode.value;
  const joinCode = els.joinCode.value.trim().toUpperCase();
  els.joinCode.value = joinCode;
  const teamToken = randomHex(48);
  const clientJoinId = uuid();
  els.joinButton.disabled = true;
  setConnection("warn", "Conectando…");
  try {
    const data = await api({ action: "join", join_code: joinCode, group_code: groupCode, team_name: teamName, team_token: teamToken, client_join_id: clientJoinId }, { retries: 2 });
    saveSession({
      team_id: data.session.team_id, team_token: teamToken, client_join_id: clientJoinId,
      join_code: joinCode, group_code: groupCode, team_name: teamName, origin_hint: ORIGIN_HINT
    });
    snapshot = data.snapshot; lastEventId = 0; syncServerClock(snapshot.server_time); finalShown = false; finalClosed = false;
    showGame(); setConnection("ok", "Servidor sincronizado"); renderAll(snapshot.events || []); startPolling();
  } catch (error) {
    els.joinMessage.textContent = errorText(error?.data?.error || error?.message);
    setConnection("bad", "No conectado");
  } finally {
    els.joinButton.disabled = false;
  }
}

function leaveGame() {
  stopPolling(); saveSession(null); snapshot = null; lastEventId = 0; finalShown = false; finalClosed = false;
  els.eventFeed.textContent = ""; showJoin();
}

async function resume() {
  if (!session) { showJoin(); return; }
  showGame(); setConnection("warn", "Recuperando sesión…"); startPolling();
}

els.joinForm.addEventListener("submit", joinGame);
els.leaveButton.addEventListener("click", leaveGame);
els.closeFinal.addEventListener("click", () => { finalClosed = true; els.finalOverlay.hidden = true; });
document.querySelectorAll(".action-button").forEach(button => button.addEventListener("click", () => performAction(button.dataset.action)));
els.joinCode.addEventListener("input", () => { els.joinCode.value = els.joinCode.value.toUpperCase().replace(/[^A-Z0-9-]/g, "").slice(0,12); });
window.addEventListener("online", () => { setConnection("warn", "Reconectando…"); pollSnapshot({ immediate: true }); });
window.addEventListener("offline", () => setConnection("bad", "Sin Internet"));
document.addEventListener("visibilitychange", () => { if (!document.hidden && session) pollSnapshot({ immediate: true }); });
window.addEventListener("beforeunload", stopPolling);

resume();
