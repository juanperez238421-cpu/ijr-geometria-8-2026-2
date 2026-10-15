"use strict";

/**
 * IJR Geometry 8 - Shaded Areas / Canada quiz shell
 * PREVIEW ONLY. No official exam or identity/grades are stored here.
 * Never put answer keys, student records or privileged credentials in static assets.
 */
(function () {
  const STORAGE_KEY = "ijr-geo8-canada-preview-v1";
  const STRIKE_LIMIT = 3;
  const INCIDENT_DEBOUNCE_MS = 2200;
  const DEFAULT_STATEMENT = "Aquí se integrará el enunciado definitivo cuando estén aprobados los problemas diseñados en Opus. Cada ejercicio tendrá entre 3 y 5 figuras.";
  const $ = (id) => document.getElementById(id);
  const state = {
    status: "welcome",
    problem: 0,
    strikes: 0,
    startAt: null,
    lastIncidentAt: 0,
    answers: [{value: "", unit: "", reasoning: ""}, {value: "", unit: "", reasoning: ""}, {value: "", unit: "", reasoning: ""}],
    incidents: [],
    armed: false
  };
  let problems = Array.from({length: 3}, (_, index) => ({
    id: "P0" + (index + 1), ready: false, title: null,
    statement: null, diagram: null, figure_count: null
  }));
  let lastFocusTimeout = null;

  function show(viewId) {
    ["welcomeView", "examView", "resultView"].forEach((id) => $(id).classList.toggle("hidden", id !== viewId));
  }

  function save() {
    try {
      const snapshot = {
        status: state.status, problem: state.problem, strikes: state.strikes,
        startAt: state.startAt, lastIncidentAt: state.lastIncidentAt,
        answers: state.answers, incidents: state.incidents
      };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    } catch (_) {
      // Storage can be disabled or exhausted. Preview still works in memory.
    }
  }

  function load() {
    try {
      const snapshot = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "null");
      if (!snapshot || !Array.isArray(snapshot.answers) || snapshot.answers.length !== 3) return false;
      if (!["active", "paused", "locked", "finished"].includes(snapshot.status)) return false;
      state.status = snapshot.status;
      state.problem = Number.isInteger(snapshot.problem) && snapshot.problem >= 0 && snapshot.problem < 3 ? snapshot.problem : 0;
      state.strikes = Math.min(STRIKE_LIMIT, Math.max(0, Number(snapshot.strikes) || 0));
      state.startAt = Number(snapshot.startAt) > 0 ? snapshot.startAt : Date.now();
      state.answers = snapshot.answers.map((a) => ({
        value: String(a && a.value || "").slice(0, 50),
        unit: ["", "cm²", "mm²", "m²", "u²"].includes(a && a.unit) ? a.unit : "",
        reasoning: String(a && a.reasoning || "").slice(0, 5000)
      }));
      state.incidents = Array.isArray(snapshot.incidents) ? snapshot.incidents.slice(-3) : [];
      state.armed = false;
      return true;
    } catch (_) { return false; }
  }

  function updateStatus() {
    const element = $("topStatus");
    const label = ({
      welcome: "EN PREPARACIÓN", active: "VISTA PREVIA",
      paused: "SESIÓN PAUSADA", locked: "SESIÓN BLOQUEADA", finished: "SIMULACIÓN TERMINADA"
    })[state.status] || "EN PREPARACIÓN";
    element.innerHTML = '<span class="status-dot"></span> ' + label;
  }

  function formattedTime(ms) {
    const seconds = Math.max(0, Math.floor(ms / 1000));
    const h = Math.floor(seconds / 3600);
    const m = Math.floor(seconds / 60) % 60;
    const s = seconds % 60;
    const pair = (n) => String(n).padStart(2, "0");
    return h ? pair(h) + ":" + pair(m) + ":" + pair(s) : pair(m) + ":" + pair(s);
  }

  function tickClock() {
    if (state.startAt && ["active", "paused"].includes(state.status)) {
      $("clock").textContent = formattedTime(Date.now() - state.startAt);
    }
  }

  function numericValid(value) {
    if (!/^\d+(?:[.,]\d+)?$/.test(value.trim())) return false;
    return Number.isFinite(Number(value.replace(",", ".")));
  }

  function completedCount() {
    return state.answers.filter((answer) => numericValid(answer.value) && !!answer.unit && answer.reasoning.trim().length >= 10).length;
  }

  function updateProgress() {
    $("progress").textContent = completedCount() + " / 3";
    $("strikeDots").setAttribute("aria-label", state.strikes + " de 3 incidencias");
    Array.from($("strikeDots").children).forEach((node, i) => node.classList.toggle("active", i < state.strikes));
    document.querySelectorAll(".rail-item").forEach((button, i) => {
      const answer = state.answers[i];
      const done = numericValid(answer.value) && !!answer.unit && answer.reasoning.trim().length >= 10;
      const isSelected = i === state.problem;
      button.classList.toggle("selected", isSelected);
      button.classList.toggle("complete", done);
      button.querySelector(".rail-state").textContent = done ? "✓" : "○";
      if (isSelected) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
    });
  }

  function defaultDiagram(frame) {
    frame.innerHTML =
      '<div class="diagram-placeholder">' +
      '<div class="placeholder-glyph" aria-hidden="true">▱</div>' +
      '<strong>Espacio reservado para la figura</strong>' +
      '<span>SVG / animación de enunciado · pendiente de Opus</span>' +
      '<span class="placeholder-footnote">No se muestran soluciones durante el examen.</span>' +
      '</div>';
    frame.setAttribute("aria-label", "Diagrama pendiente de incorporar");
  }

  function renderDiagram(problem) {
    const frame = $("diagramFrame");
    frame.replaceChildren();
    // Same-origin, versioned public diagram assets only. Never use inline HTML from the manifest.
    const src = problem && typeof problem.diagram === "string" ? problem.diagram : "";
    const valid = /^assets\/[a-zA-Z0-9/_-]+\.(svg|png|webp|mp4|webm)$/.test(src);
    if (!problem.ready || !valid) { defaultDiagram(frame); return; }
    const video = /\.(mp4|webm)$/.test(src);
    const node = document.createElement(video ? "video" : "img");
    node.src = src;
    node.className = "problem-media";
    node.setAttribute("aria-label", "Diagrama del problema " + (state.problem + 1));
    if (video) {
      node.controls = true;
      node.preload = "metadata";
      node.playsInline = true;
      node.loop = false;
    } else {
      node.alt = "Figura geométrica del problema " + (state.problem + 1);
      node.loading = "eager";
    }
    node.addEventListener("error", () => defaultDiagram(frame), {once: true});
    frame.appendChild(node);
    frame.setAttribute("aria-label", "Diagrama del problema " + (state.problem + 1));
  }

  function renderProblem() {
    const index = state.problem, problem = problems[index];
    $("questionCounter").textContent = "EJERCICIO 0" + (index + 1) + " DE 03";
    $("questionTitle").textContent = problem.ready && problem.title ? problem.title : "Composición geométrica pendiente";
    $("questionStatement").textContent = problem.ready && problem.statement ? problem.statement : DEFAULT_STATEMENT;
    $("diagramNumber").textContent = "0" + (index + 1);
    $("figureCount").textContent = problem.ready && Number.isInteger(problem.figure_count) ?
      problem.figure_count + " figuras geométricas" : "3 a 5 figuras · por definir";
    $("pageIndicator").textContent = "0" + (index + 1) + " / 03";
    $("prevButton").disabled = index === 0;
    $("nextButton").textContent = index === 2 ? "Volver al inicio ↺" : "Siguiente →";
    const answer = state.answers[index];
    $("areaValue").value = answer.value;
    $("areaUnit").value = answer.unit;
    $("reasoning").value = answer.reasoning;
    $("saveStatus").textContent = "Borrador local · sin envío";
    renderDiagram(problem);
    updateProgress();
  }

  function saveAnswer() {
    if (!["active", "paused"].includes(state.status)) return;
    state.answers[state.problem] = {
      value: $("areaValue").value.slice(0, 50),
      unit: $("areaUnit").value,
      reasoning: $("reasoning").value.slice(0, 5000)
    };
    save();
    updateProgress();
    $("saveStatus").textContent = "Borrador de demostración actualizado · sin envío";
  }

  function selectProblem(index) {
    if (state.status !== "active" || index < 0 || index >= 3) return;
    saveAnswer();
    state.problem = index;
    save();
    renderProblem();
  }

  function errorMessage(message) {
    let node = $("runtimeNotice");
    if (!node) {
      node = document.createElement("p");
      node.id = "runtimeNotice";
      node.style.cssText = "color:#b53c44;font-size:12px;max-width:560px;margin:10px 0";
      $("previewStart").closest(".welcome-actions").after(node);
    }
    node.textContent = message;
  }

  async function enterFullscreen() {
    if (document.fullscreenElement) return true;
    if (!document.fullscreenEnabled || !document.documentElement.requestFullscreen) {
      errorMessage("Este navegador no permite activar pantalla completa mediante esta página. Para una evaluación supervisada usa un navegador de escritorio compatible; el docente deberá definir una alternativa accesible.");
      return false;
    }
    try {
      await document.documentElement.requestFullscreen({navigationUI: "hide"});
      return !!document.fullscreenElement;
    } catch (_) {
      errorMessage("No se pudo activar pantalla completa. Revisa los permisos del navegador y vuelve a pulsar el botón.");
      return false;
    }
  }

  async function startPreview() {
    const ok = await enterFullscreen();
    if (!ok) return;
    state.status = "active";
    state.problem = 0;
    state.strikes = 0;
    state.startAt = Date.now();
    state.lastIncidentAt = 0;
    state.answers = [{value:"",unit:"",reasoning:""},{value:"",unit:"",reasoning:""},{value:"",unit:"",reasoning:""}];
    state.incidents = [];
    state.armed = true;
    $("incidentModal").classList.add("hidden");
    show("examView");
    renderProblem();
    updateStatus();
    tickClock();
    save();
  }

  function showIncidentModal(reason) {
    const locked = state.status === "locked";
    $("modalEyebrow").textContent = locked ? "LÍMITE DE INCIDENCIAS ALCANZADO" : "CONTROL DE INTEGRIDAD";
    $("modalTitle").textContent = locked ? "Sesión bloqueada" : "Salida detectada";
    $("modalText").textContent = locked ?
      "Se registraron tres salidas. La sesión de prueba queda bloqueada. Una evaluación oficial requerirá revisión del docente antes de cualquier decisión académica." :
      "Se detectó una salida del entorno de examen (" + reason + "). Debes regresar a pantalla completa para continuar.";
    $("modalStrikeCount").textContent = state.strikes + " de " + STRIKE_LIMIT + " incidencias";
    $("modalAction").textContent = locked ? "Ver resumen de la simulación" : "Volver a pantalla completa";
    $("modalSymbol").textContent = locked ? "×" : "!";
    $("modalFoot").textContent = locked ?
      "Esto es una simulación local; no se ha enviado ningún reporte académico." :
      "Salir de pantalla completa o cambiar de pestaña pausa la actividad.";
    $("incidentModal").classList.remove("hidden");
    if (!document.hidden) $("modalAction").focus();
  }

  function incident(reason) {
    if (state.status !== "active" || !state.armed) return;
    const now = Date.now();
    if (now - state.lastIncidentAt < INCIDENT_DEBOUNCE_MS) return;
    state.lastIncidentAt = now;
    state.armed = false; // One departure = one strike (even if multiple events fire).
    state.strikes = Math.min(STRIKE_LIMIT, state.strikes + 1);
    state.incidents.push({number: state.strikes, reason, at: new Date(now).toISOString()});
    state.status = state.strikes >= STRIKE_LIMIT ? "locked" : "paused";
    saveAnswer();
    updateStatus();
    updateProgress();
    save();
    showIncidentModal(reason);
  }

  async function resumeOrShowResult() {
    if (state.status === "locked") {
      finish(true);
      return;
    }
    if (state.status !== "paused") return;
    const ok = await enterFullscreen();
    if (!ok) return;
    state.status = "active";
    state.armed = true;
    $("incidentModal").classList.add("hidden");
    updateStatus();
    updateProgress();
    save();
  }

  function finish(blocked) {
    if (state.status === "finished") return;
    const isLocked = !!blocked || state.status === "locked";
    if (state.status === "active") saveAnswer();
    state.status = isLocked ? "locked" : "finished";
    state.armed = false;
    updateStatus();
    $("incidentModal").classList.add("hidden");
    show("resultView");
    $("resultIcon").textContent = isLocked ? "!" : "◇";
    $("resultHeading").textContent = isLocked ? "Simulación bloqueada" : "Simulación finalizada";
    $("resultDescription").textContent = isLocked ?
      "Se alcanzó el límite de tres incidencias. En la versión real el docente deberá poder revisar el registro y desbloquear o validar la sesión." :
      "Probaste la interfaz de respuestas. Los ejercicios definitivos aún no se han incorporado y no hay ningún envío ni calificación.";
    $("resultSummary").textContent =
      "Problemas con valor, unidad y procedimiento: " + completedCount() + " de 3\n" +
      "Incidencias registradas: " + state.strikes + " de 3\n" +
      "Modo: demostración sin persistencia remota";
    save();
    if (document.fullscreenElement && document.exitFullscreen) {
      document.exitFullscreen().catch(() => {});
    }
  }

  function reset() {
    try { sessionStorage.removeItem(STORAGE_KEY); } catch (_) {}
    state.status = "welcome";
    state.armed = false;
    state.startAt = null;
    state.strikes = 0;
    state.incidents = [];
    show("welcomeView");
    updateStatus();
    if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(() => {});
  }

  async function loadManifest() {
    try {
      const response = await fetch("./manifest.json", {cache: "no-store"});
      if (!response.ok) return;
      const data = await response.json();
      if (!Array.isArray(data.problems) || data.problems.length !== 3) return;
      problems = data.problems.map((p, i) => ({
        id: "P0" + (i + 1),
        ready: p.ready === true && !!p.statement &&
          Number.isInteger(p.figure_count) && p.figure_count >= 3 && p.figure_count <= 5,
        title: typeof p.title === "string" ? p.title.slice(0, 160) : null,
        statement: typeof p.statement === "string" ? p.statement.slice(0, 3000) : null,
        diagram: typeof p.diagram === "string" ? p.diagram : null,
        figure_count: p.figure_count
      }));
      if (state.status === "active" || state.status === "paused") renderProblem();
    } catch (_) {
      // Static file:// previews might not support fetch; placeholders still render.
    }
  }

  function bind() {
    $("previewStart").addEventListener("click", startPreview);
    $("prevButton").addEventListener("click", () => selectProblem(state.problem - 1));
    $("nextButton").addEventListener("click", () => selectProblem(state.problem === 2 ? 0 : state.problem + 1));
    document.querySelectorAll(".rail-item").forEach((button) =>
      button.addEventListener("click", () => selectProblem(Number(button.dataset.problem))));
    ["areaValue", "areaUnit", "reasoning"].forEach((id) => $(id).addEventListener("input", saveAnswer));
    $("areaUnit").addEventListener("change", saveAnswer);
    $("finishButton").addEventListener("click", () => finish(false));
    $("simulateStrike").addEventListener("click", () => incident("simulación de salida QA"));
    $("modalAction").addEventListener("click", resumeOrShowResult);
    $("restartButton").addEventListener("click", reset);

    document.addEventListener("fullscreenchange", () => {
      if (state.status === "active" && state.armed && !document.fullscreenElement) incident("salida de pantalla completa");
    });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) incident("cambio de pestaña o ventana oculta");
      else if (state.status === "paused" || state.status === "locked") showIncidentModal("cambio de pestaña");
    });
    window.addEventListener("blur", () => {
      clearTimeout(lastFocusTimeout);
      lastFocusTimeout = setTimeout(() => {
        if (!document.hasFocus() && !document.hidden) incident("pérdida de foco de la ventana");
      }, 800);
    });
    window.addEventListener("focus", () => clearTimeout(lastFocusTimeout));
    // The timer is informative ONLY in preview. Real assessments must use server time and expiry.
    setInterval(tickClock, 1000);
  }

  function init() {
    bind();
    if (load()) {
      if (state.status === "active") {
        // Reloaded while an exam was in progress. Count as one new departure.
        state.armed = true;
        incident("recarga durante el examen");
      }
      if (state.status === "paused") {
        show("examView");
        renderProblem();
        showIncidentModal("sesión interrumpida");
      } else if (state.status === "locked") {
        show("examView");
        renderProblem();
        showIncidentModal("sesión bloqueada");
      } else if (state.status === "finished") finish(false);
    } else {
      show("welcomeView");
    }
    updateStatus();
    tickClock();
    loadManifest();
  }

  init();
})();