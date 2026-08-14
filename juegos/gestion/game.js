"use strict";

const $ = (id) => document.getElementById(id);
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const priceModes = {
  budget: { demand: 1.18, price: 0.84, rep: 1, label: "Alta" },
  standard: { demand: 1.0, price: 1.0, rep: 0, label: "Media" },
  premium: { demand: 0.82, price: 1.34, rep: -1, label: "Baja" }
};

const events = [
  {
    title: "Un día normal en la plaza",
    text: "Demanda estable. Es un buen momento para mejorar tu operación.",
    badge: "NORMAL",
    tone: "neutral",
    demandMul: 1,
    repDelta: 0,
    energyDelta: 0,
    conditionDelta: 0,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Demanda ×1.00", "Sin modificadores"]
  },
  {
    title: "Festival en el barrio",
    text: "La plaza recibirá más visitantes. Tener stock y personal disponible será clave.",
    badge: "OPORTUNIDAD",
    tone: "good",
    demandMul: 1.35,
    repDelta: 2,
    energyDelta: -3,
    conditionDelta: -2,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Demanda +35%", "Reputación +2", "Mayor desgaste"]
  },
  {
    title: "Proveedor con descuento",
    text: "Tu proveedor principal ofrece inventario a mejor precio durante este turno.",
    badge: "OFERTA",
    tone: "good",
    demandMul: 1.02,
    repDelta: 0,
    energyDelta: 0,
    conditionDelta: 0,
    cashDelta: 0,
    restockMult: 0.65,
    effects: ["Reabastecer -35%", "Demanda estable"]
  },
  {
    title: "Visita de creador de contenido",
    text: "Una publicación viral puede llenar la plaza. La experiencia del cliente será visible para todos.",
    badge: "VIRAL",
    tone: "good",
    demandMul: 1.48,
    repDelta: 3,
    energyDelta: -5,
    conditionDelta: -2,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Demanda +48%", "Reputación +3", "Energía -5"]
  },
  {
    title: "Lluvia fuerte",
    text: "Hay menos tráfico peatonal. Puede ser un buen día para mantenimiento o descanso.",
    badge: "BAJA AFLUENCIA",
    tone: "neutral",
    demandMul: 0.72,
    repDelta: 0,
    energyDelta: 4,
    conditionDelta: 1,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Demanda -28%", "Energía +4", "Desgaste menor"]
  },
  {
    title: "Falla eléctrica parcial",
    text: "Los equipos trabajarán bajo estrés. Los locales con mantenimiento atrasado son vulnerables.",
    badge: "RIESGO",
    tone: "bad",
    demandMul: 0.9,
    repDelta: -1,
    energyDelta: -4,
    conditionDelta: -9,
    cashDelta: -8,
    restockMult: 1,
    effects: ["Condición -9", "Caja -$8", "Demanda -10%"]
  },
  {
    title: "Competidor abre cerca",
    text: "Una nueva plaza ofrece promociones agresivas. La reputación y el precio ahora importan más.",
    badge: "COMPETENCIA",
    tone: "bad",
    demandMul: 0.82,
    repDelta: -1,
    energyDelta: 0,
    conditionDelta: 0,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Demanda -18%", "Reputación -1"]
  },
  {
    title: "Salida masiva de estudiantes",
    text: "Cientos de jóvenes pasan por la zona. Si respondes rápido, el día puede ser excelente.",
    badge: "RUSH",
    tone: "good",
    demandMul: 1.28,
    repDelta: 1,
    energyDelta: -3,
    conditionDelta: -2,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Demanda +28%", "Reputación +1"]
  },
  {
    title: "Equipo agotado",
    text: "La semana pesa sobre el personal. Una pausa puede proteger la productividad.",
    badge: "PERSONAL",
    tone: "bad",
    demandMul: 0.95,
    repDelta: 0,
    energyDelta: -14,
    conditionDelta: 0,
    cashDelta: 0,
    restockMult: 1,
    effects: ["Energía -14", "Demanda -5%"]
  },
  {
    title: "Inspección sorpresa",
    text: "La administración revisará el estado de los tres locales al cerrar el día.",
    badge: "INSPECCIÓN",
    tone: "neutral",
    demandMul: 0.96,
    repDelta: 0,
    energyDelta: -2,
    conditionDelta: 0,
    cashDelta: 0,
    restockMult: 1,
    special: "inspection",
    effects: ["Condición ≥65: reputación +4", "Condición <65: reputación -6"]
  }
];

const quizBank = [
  { tag: "Area", en: "A rectangle is 12 cm long and 7 cm wide. What is its area?", es: "Un rectángulo mide 12 cm por 7 cm. ¿Cuál es su área?", options: ["19 cm²", "38 cm²", "84 cm²", "96 cm²"], correct: 2, explain: "A = b·h = 12·7 = 84 cm²." },
  { tag: "Area", en: "A square has side length 9 m. What is its area?", es: "Un cuadrado tiene lado de 9 m. ¿Cuál es su área?", options: ["18 m²", "36 m²", "72 m²", "81 m²"], correct: 3, explain: "A = s² = 9² = 81 m²." },
  { tag: "Triangle", en: "A triangle has base 14 cm and height 8 cm. Find its area.", es: "Un triángulo tiene base 14 cm y altura 8 cm. Halla su área.", options: ["44 cm²", "56 cm²", "88 cm²", "112 cm²"], correct: 1, explain: "A = (b·h)/2 = (14·8)/2 = 56 cm²." },
  { tag: "Parallelogram", en: "A parallelogram has base 10 cm and perpendicular height 6 cm. What is its area?", es: "Un paralelogramo tiene base 10 cm y altura perpendicular 6 cm. ¿Cuál es su área?", options: ["30 cm²", "32 cm²", "60 cm²", "80 cm²"], correct: 2, explain: "A = b·h = 10·6 = 60 cm²." },
  { tag: "Trapezoid", en: "A trapezoid has bases 8 cm and 14 cm, and height 5 cm. Find its area.", es: "Un trapecio tiene bases de 8 cm y 14 cm, y altura 5 cm. Halla su área.", options: ["44 cm²", "50 cm²", "55 cm²", "110 cm²"], correct: 2, explain: "A = ((B+b)·h)/2 = ((14+8)·5)/2 = 55 cm²." },
  { tag: "Circle", en: "A circle has radius 4 cm. What is its exact area?", es: "Un círculo tiene radio 4 cm. ¿Cuál es su área exacta?", options: ["4π cm²", "8π cm²", "16π cm²", "32π cm²"], correct: 2, explain: "A = πr² = π·4² = 16π cm²." },
  { tag: "Circle", en: "A circle has diameter 10 m. What is its exact circumference?", es: "Un círculo tiene diámetro 10 m. ¿Cuál es su circunferencia exacta?", options: ["5π m", "10π m", "20π m", "25π m"], correct: 1, explain: "C = πd = 10π m." },
  { tag: "Circle", en: "The diameter of a circle is 18 cm. What is its radius?", es: "El diámetro de un círculo es 18 cm. ¿Cuál es su radio?", options: ["6 cm", "9 cm", "18 cm", "36 cm"], correct: 1, explain: "r = d/2 = 18/2 = 9 cm." },
  { tag: "Semicircle", en: "A semicircle has radius 6 cm. What is the area of the semicircular region?", es: "Un semicírculo tiene radio 6 cm. ¿Cuál es el área de la región semicircular?", options: ["6π cm²", "12π cm²", "18π cm²", "36π cm²"], correct: 2, explain: "A = (πr²)/2 = (36π)/2 = 18π cm²." },
  { tag: "Shaded Area", en: "A 10 cm × 8 cm rectangle contains an unshaded 4 cm × 3 cm rectangle. What is the shaded area?", es: "Un rectángulo de 10×8 cm contiene un rectángulo sin sombrear de 4×3 cm. ¿Área sombreada?", options: ["12 cm²", "56 cm²", "68 cm²", "80 cm²"], correct: 2, explain: "Shaded = 10·8 − 4·3 = 80 − 12 = 68 cm²." },
  { tag: "Shaded Area", en: "A square has side 12 cm. A circle of radius 3 cm is removed. What is the remaining exact area?", es: "Un cuadrado tiene lado 12 cm. Se retira un círculo de radio 3 cm. ¿Área restante exacta?", options: ["144−3π cm²", "144−6π cm²", "144−9π cm²", "132π cm²"], correct: 2, explain: "Remaining area = 12² − π·3² = 144 − 9π cm²." },
  { tag: "Shaded Area", en: "A ring has outer radius 5 cm and inner radius 2 cm. What is its exact area?", es: "Un anillo tiene radio exterior 5 cm e interior 2 cm. ¿Cuál es su área exacta?", options: ["3π cm²", "7π cm²", "21π cm²", "29π cm²"], correct: 2, explain: "A = π(5²−2²) = π(25−4) = 21π cm²." },
  { tag: "Composite Area", en: "Two non-overlapping rectangles measure 6×4 cm and 3×2 cm. What is their total area?", es: "Dos rectángulos sin superposición miden 6×4 cm y 3×2 cm. ¿Área total?", options: ["18 cm²", "24 cm²", "30 cm²", "36 cm²"], correct: 2, explain: "A = 6·4 + 3·2 = 24 + 6 = 30 cm²." },
  { tag: "Perimeter", en: "A rectangle measures 9 cm by 5 cm. What is its perimeter?", es: "Un rectángulo mide 9 cm por 5 cm. ¿Cuál es su perímetro?", options: ["14 cm", "28 cm", "45 cm", "90 cm"], correct: 1, explain: "P = 2(9+5) = 28 cm." },
  { tag: "Triangle", en: "A triangle has area 45 cm² and base 10 cm. What is its height?", es: "Un triángulo tiene área 45 cm² y base 10 cm. ¿Cuál es su altura?", options: ["4.5 cm", "8 cm", "9 cm", "18 cm"], correct: 2, explain: "45 = (10·h)/2 → 45 = 5h → h = 9 cm." },
  { tag: "Circle", en: "A circle has area 49π cm². What is its radius?", es: "Un círculo tiene área 49π cm². ¿Cuál es su radio?", options: ["3.5 cm", "7 cm", "14 cm", "49 cm"], correct: 1, explain: "πr² = 49π → r² = 49 → r = 7 cm." },
  { tag: "Sector", en: "A 90° sector is cut from a circle of radius 8 cm. What is the sector's exact area?", es: "Un sector de 90° se toma de un círculo de radio 8 cm. ¿Área exacta del sector?", options: ["8π cm²", "16π cm²", "32π cm²", "64π cm²"], correct: 1, explain: "90° is 1/4 of a circle: (1/4)·π·8² = 16π cm²." },
  { tag: "Shaded Area", en: "A 10×10 square has four 2×2 corner squares removed. What area remains?", es: "A un cuadrado 10×10 se le quitan cuatro cuadrados 2×2 en las esquinas. ¿Qué área queda?", options: ["68 units²", "76 units²", "84 units²", "92 units²"], correct: 2, explain: "100 − 4(4) = 100 − 16 = 84 units²." },
  { tag: "Concept", en: "Which unit is appropriate for area?", es: "¿Qué unidad es apropiada para medir área?", options: ["cm", "cm²", "cm³", "degrees"], correct: 1, explain: "Area is measured in square units, such as cm²." },
  { tag: "Concept", en: "Which formula gives the area of a circle?", es: "¿Cuál fórmula da el área de un círculo?", options: ["A=2πr", "A=πr²", "A=πd", "A=r²/2"], correct: 1, explain: "The circle area formula is A = πr²." },
  { tag: "Concept", en: "For a shaded region formed by a large shape with a hole, what is the usual strategy?", es: "Para una región sombreada formada por una figura grande con un hueco, ¿qué estrategia se usa normalmente?", options: ["Add outer and inner areas", "Multiply the areas", "Outer area − inner area", "Use perimeter only"], correct: 2, explain: "Shaded area = area of the outer region − area of the removed region." },
  { tag: "Composite Area", en: "A 12×6 rectangle is joined to a 4×3 rectangle without overlap. What is the composite area?", es: "Un rectángulo 12×6 se une a uno 4×3 sin superposición. ¿Área compuesta?", options: ["72 units²", "76 units²", "84 units²", "96 units²"], correct: 2, explain: "12·6 + 4·3 = 72 + 12 = 84 units²." },
  { tag: "Trapezoid", en: "A trapezoid has area 72 cm², height 8 cm and one base 10 cm. Find the other base.", es: "Un trapecio tiene área 72 cm², altura 8 cm y una base 10 cm. Halla la otra base.", options: ["6 cm", "8 cm", "10 cm", "18 cm"], correct: 1, explain: "72=((10+b)·8)/2=4(10+b) → 18=10+b → b=8 cm." },
  { tag: "Shaded Area", en: "A rectangle 15×10 cm contains a circular hole of radius 2 cm. What is the exact remaining area?", es: "Un rectángulo 15×10 cm contiene un hueco circular de radio 2 cm. ¿Área restante exacta?", options: ["150−2π cm²", "150−4π cm²", "150−8π cm²", "146π cm²"], correct: 1, explain: "Remaining area = 150 − π·2² = 150 − 4π cm²." },
  { tag: "Perimeter vs Area", en: "You want to know how much tile covers a floor. Which quantity do you calculate?", es: "Quieres saber cuánta baldosa cubre un piso. ¿Qué cantidad calculas?", options: ["Perimeter", "Area", "Diameter", "Angle"], correct: 1, explain: "Covering a surface requires area, not perimeter." },
  { tag: "Perimeter vs Area", en: "You want to put a fence around a rectangular garden. Which quantity matters most?", es: "Quieres poner una cerca alrededor de un jardín rectangular. ¿Qué cantidad importa más?", options: ["Area", "Volume", "Perimeter", "Radius"], correct: 2, explain: "A fence follows the boundary, so you need the perimeter." }
];

const initialBusinesses = () => [
  { id: "snack", name: "Snack Lab", emoji: "🍔", level: 1, stock: 18, maxStock: 26, staff: 1, condition: 86, baseDemand: 10, basePrice: 6 },
  { id: "arcade", name: "Arcade Hub", emoji: "🕹️", level: 1, stock: 16, maxStock: 24, staff: 1, condition: 88, baseDemand: 9, basePrice: 7 },
  { id: "shop", name: "Maker Shop", emoji: "🛍️", level: 1, stock: 14, maxStock: 22, staff: 1, condition: 90, baseDemand: 7, basePrice: 9 }
];

let state;
let selectedBusinessId = "snack";
let currentEvent;
let isSimulating = false;
let pendingAdvance = false;
let currentQuiz = null;
let lastQuizIndex = -1;

function newState() {
  return {
    day: 1,
    maxDays: 12,
    cash: 120,
    reputation: 55,
    energy: 80,
    ap: 2,
    lives: 3,
    maxLives: 3,
    marketingDays: 0,
    quizCorrect: 0,
    quizAttempts: 0,
    totalCustomers: 0,
    totalRevenue: 0,
    businesses: initialBusinesses(),
    ledger: []
  };
}

function selectedBusiness() {
  return state.businesses.find((b) => b.id === selectedBusinessId) || state.businesses[0];
}

function pickEvent() {
  const pool = state.day === 1 ? [events[0], events[0], events[4]] : events;
  return pool[rand(0, pool.length - 1)];
}

function initGame() {
  state = newState();
  selectedBusinessId = "snack";
  isSimulating = false;
  pendingAdvance = false;
  currentEvent = pickEvent();
  $("priceMode").value = "standard";
  $("quizModal").classList.add("hidden");
  $("endModal").classList.add("hidden");
  renderAll();
  addLedger("Inicio", "Capital inicial de operación", "+$120", "positive");
  renderLedger();
}

function renderAll() {
  renderHUD();
  renderEvent();
  renderBusinesses();
  renderSelectedPanel();
  renderActions();
  renderMilestones();
  renderBestScore();
  renderForecast();
}

function renderHUD() {
  $("dayValue").textContent = `${state.day} / ${state.maxDays}`;
  $("cashValue").textContent = `$${Math.round(state.cash)}`;
  $("repValue").textContent = Math.round(state.reputation);
  $("energyValue").textContent = Math.round(state.energy);
  $("apValue").textContent = state.ap;
  $("livesValue").textContent = "❤️".repeat(state.lives) + "🖤".repeat(state.maxLives - state.lives);
  $("livesValue").setAttribute("aria-label", `${state.lives} vidas`);
  $("quizValue").textContent = `${state.quizCorrect} / ${state.quizAttempts}`;
}

function renderEvent() {
  $("eventTitle").textContent = currentEvent.title;
  $("eventText").textContent = currentEvent.text;
  const badge = $("eventBadge");
  badge.textContent = currentEvent.badge;
  badge.className = `event-badge ${currentEvent.tone}`;
  $("eventEffects").innerHTML = currentEvent.effects.map((effect) => `<span class="effect-chip">${effect}</span>`).join("");
}

function renderBusinesses() {
  const grid = $("businessGrid");
  grid.innerHTML = "";
  for (const b of state.businesses) {
    const stockPct = clamp((b.stock / b.maxStock) * 100, 0, 100);
    const staffCap = 4 + b.level;
    const staffPct = clamp((b.staff / staffCap) * 100, 0, 100);
    const card = document.createElement("button");
    card.type = "button";
    card.className = `business-card ${b.id === selectedBusinessId ? "selected" : ""} ${isSimulating ? "busy" : ""}`;
    card.dataset.id = b.id;
    card.innerHTML = `
      <div class="business-title">
        <span class="business-emoji">${b.emoji}</span>
        <strong>${b.name}</strong>
        <span class="level-chip">Nv. ${b.level}</span>
      </div>
      <div class="metric">
        <div class="metric-line"><span>Stock</span><strong>${b.stock}/${b.maxStock}</strong></div>
        <div class="bar"><span style="width:${stockPct}%"></span></div>
      </div>
      <div class="metric">
        <div class="metric-line"><span>Condición</span><strong>${Math.round(b.condition)}%</strong></div>
        <div class="bar"><span style="width:${clamp(b.condition, 0, 100)}%"></span></div>
      </div>
      <div class="metric">
        <div class="metric-line"><span>Personal</span><strong>${b.staff}/${staffCap}</strong></div>
        <div class="bar"><span style="width:${staffPct}%"></span></div>
      </div>
      <div class="business-footer"><span>Precio base $${b.basePrice}</span><span>Demanda base ${b.baseDemand}</span></div>
    `;
    card.addEventListener("click", () => {
      if (isSimulating) return;
      selectedBusinessId = b.id;
      renderBusinesses();
      renderSelectedPanel();
      renderActions();
    });
    grid.appendChild(card);
  }
}

function renderSelectedPanel() {
  const b = selectedBusiness();
  $("selectedName").textContent = `${b.emoji} ${b.name}`;
  const upgradeCost = 45 + (b.level - 1) * 25;
  $("upgradeCostText").textContent = b.level >= 4 ? "Nivel máximo" : `Nivel +1 · $${upgradeCost}`;
}

function renderActions() {
  const b = selectedBusiness();
  document.querySelectorAll(".action-btn").forEach((btn) => {
    const action = btn.dataset.action;
    let disabled = isSimulating || state.ap <= 0;
    if (action === "restock") {
      const cost = Math.round(20 * currentEvent.restockMult);
      btn.querySelector("small").textContent = `+8 stock · -$${cost}`;
      disabled ||= state.cash < cost || b.stock >= b.maxStock;
    }
    if (action === "maintenance") disabled ||= state.cash < 18 || b.condition >= 100;
    if (action === "hire") disabled ||= state.cash < 28 || b.staff >= 4 + b.level;
    if (action === "upgrade") {
      const cost = 45 + (b.level - 1) * 25;
      disabled ||= state.cash < cost || b.level >= 4;
    }
    if (action === "marketing") disabled ||= state.cash < 25;
    if (action === "break") disabled ||= state.energy >= 100;
    btn.disabled = disabled;
  });
  $("openDayBtn").disabled = isSimulating;
  $("priceMode").disabled = isSimulating;
}

function renderMilestones() {
  setMilestone("mCash", state.cash >= 180);
  setMilestone("mRep", state.reputation >= 55);
  setMilestone("mDay", state.day >= 12);
}

function setMilestone(id, done) {
  const el = $(id);
  el.textContent = done ? "✓" : "○";
  el.classList.toggle("done", done);
}

function renderForecast() {
  const mode = priceModes[$("priceMode").value] || priceModes.standard;
  let score = currentEvent.demandMul * mode.demand * (state.marketingDays > 0 ? 1.2 : 1);
  let label = "Media";
  if (score >= 1.25) label = "Muy alta";
  else if (score >= 1.08) label = "Alta";
  else if (score <= 0.78) label = "Baja";
  $("demandForecast").textContent = label + (state.marketingDays > 0 ? " · campaña activa" : "");
}

function renderLedger() {
  const ledger = $("ledger");
  ledger.innerHTML = state.ledger.length
    ? state.ledger.slice(0, 12).map((entry) => `
      <div class="ledger-entry">
        <span class="ledger-day">${entry.day}</span>
        <span class="ledger-text">${entry.text}</span>
        <strong class="ledger-amount ${entry.tone || ""}">${entry.amount || ""}</strong>
      </div>`).join("")
    : `<p class="muted">Aún no hay movimientos.</p>`;
}

function addLedger(day, text, amount = "", tone = "") {
  state.ledger.unshift({ day, text, amount, tone });
  renderLedger();
}

function renderBestScore() {
  const best = Number(localStorage.getItem("pixelPlazaBest") || 0);
  $("bestScore").textContent = best > 0 ? `Mejor partida: ${best} pts` : "Mejor partida: —";
}

function spendAP() {
  state.ap = Math.max(0, state.ap - 1);
  renderAll();
}

function doAction(action) {
  if (isSimulating || state.ap <= 0) return;
  const b = selectedBusiness();
  if (action === "restock") {
    const cost = Math.round(20 * currentEvent.restockMult);
    if (state.cash < cost || b.stock >= b.maxStock) return;
    state.cash -= cost;
    b.stock = Math.min(b.maxStock, b.stock + 8);
    addLedger(`D${state.day}`, `Reabastecimiento · ${b.name}`, `-$${cost}`, "negative");
  } else if (action === "maintenance") {
    if (state.cash < 18 || b.condition >= 100) return;
    state.cash -= 18;
    b.condition = clamp(b.condition + 25, 0, 100);
    addLedger(`D${state.day}`, `Mantenimiento · ${b.name}`, "-$18", "negative");
  } else if (action === "hire") {
    if (state.cash < 28 || b.staff >= 4 + b.level) return;
    state.cash -= 28;
    b.staff += 1;
    state.reputation = clamp(state.reputation + 1, 0, 100);
    addLedger(`D${state.day}`, `Nuevo integrante · ${b.name}`, "-$28", "negative");
  } else if (action === "upgrade") {
    const cost = 45 + (b.level - 1) * 25;
    if (state.cash < cost || b.level >= 4) return;
    state.cash -= cost;
    b.level += 1;
    b.maxStock += 6;
    b.condition = clamp(b.condition + 14, 0, 100);
    b.baseDemand += 1;
    state.reputation = clamp(state.reputation + 3, 0, 100);
    addLedger(`D${state.day}`, `Mejora a nivel ${b.level} · ${b.name}`, `-$${cost}`, "negative");
  } else if (action === "marketing") {
    if (state.cash < 25) return;
    state.cash -= 25;
    state.marketingDays = Math.max(state.marketingDays, 2);
    addLedger(`D${state.day}`, "Campaña de promoción activada", "-$25", "negative");
  } else if (action === "break") {
    if (state.energy >= 100) return;
    state.energy = clamp(state.energy + 25, 0, 100);
    addLedger(`D${state.day}`, "Pausa estratégica del equipo", "+25 ⚡", "positive");
  } else {
    return;
  }
  spendAP();
}

async function runDay() {
  if (isSimulating) return;
  isSimulating = true;
  renderActions();
  $("simulationTitle").textContent = `Día ${state.day} en operación`;
  $("simStatus").textContent = "Llegan clientes... decisiones tomadas, ahora observa el resultado.";
  renderBusinesses();

  const mode = priceModes[$("priceMode").value] || priceModes.standard;
  const reputationFactor = clamp(0.72 + state.reputation / 180, 0.68, 1.25);
  const marketingFactor = state.marketingDays > 0 ? 1.2 : 1;
  const energyFactor = clamp(0.58 + state.energy / 220, 0.58, 1.04);
  let totalDemand = 0;
  let totalServed = 0;
  let totalRevenue = 0;
  let totalShortage = 0;

  const results = state.businesses.map((b) => {
    const demand = Math.max(2, Math.round((b.baseDemand + b.level * 2 + rand(-2, 3)) * currentEvent.demandMul * mode.demand * marketingFactor * reputationFactor));
    const conditionFactor = clamp(0.55 + b.condition / 220, 0.55, 1.02);
    const capacity = Math.max(2, Math.floor((b.staff * 7 + b.level * 3) * conditionFactor * energyFactor));
    const served = Math.max(0, Math.min(demand, b.stock, capacity));
    const shortage = Math.max(0, demand - served);
    const unitPrice = b.basePrice * mode.price * (1 + (b.level - 1) * 0.07);
    const revenue = Math.round(served * unitPrice);
    totalDemand += demand;
    totalServed += served;
    totalRevenue += revenue;
    totalShortage += shortage;
    return { b, demand, served, shortage, revenue };
  });

  animateCustomers(Math.min(20, totalDemand));
  await sleep(2300);

  for (const result of results) {
    result.b.stock = Math.max(0, result.b.stock - result.served);
    result.b.condition = clamp(result.b.condition - Math.max(2, Math.round(result.served * 0.45)) + currentEvent.conditionDelta, 0, 100);
  }

  const staffCount = state.businesses.reduce((sum, b) => sum + b.staff, 0);
  const salaryCost = staffCount * 6;
  const leaseAndUtilities = 82 + state.day * 2;
  const eventCash = currentEvent.cashDelta || 0;
  const net = totalRevenue - salaryCost - leaseAndUtilities + eventCash;

  state.cash += net;
  state.totalRevenue += totalRevenue;
  state.totalCustomers += totalServed;
  state.energy = clamp(state.energy - Math.round(totalServed * 0.55 + staffCount * 1.3) + currentEvent.energyDelta, 0, 100);

  let repChange = currentEvent.repDelta + mode.rep;
  if (totalShortage === 0) repChange += 3;
  else repChange -= Math.ceil(totalShortage / 4);
  if (totalServed >= 28) repChange += 1;

  if (currentEvent.special === "inspection") {
    const avgCondition = averageCondition();
    if (avgCondition >= 65) {
      repChange += 4;
      addLedger(`D${state.day}`, "Inspección superada: locales en buen estado", "+4 ⭐", "positive");
    } else {
      repChange -= 6;
      addLedger(`D${state.day}`, "Inspección deficiente: mantenimiento insuficiente", "-6 ⭐", "negative");
    }
  }

  state.reputation = clamp(state.reputation + repChange, 0, 100);
  if (state.marketingDays > 0) state.marketingDays -= 1;

  addLedger(`D${state.day}`, `${totalServed}/${totalDemand} clientes atendidos · ventas $${totalRevenue}`, `${net >= 0 ? "+" : ""}$${net}`, net >= 0 ? "positive" : "negative");
  $("simStatus").textContent = `Resultado: ${totalServed}/${totalDemand} clientes · ventas $${totalRevenue} · neto ${net >= 0 ? "+" : ""}$${net}.`;
  flashShell(net >= 0 ? "good" : "bad");
  renderAll();

  await sleep(550);
  isSimulating = false;
  renderActions();

  const crisis = detectCrisis();
  pendingAdvance = true;
  if (crisis) {
    triggerLifeLoss(crisis);
  } else {
    advanceAfterDay();
  }
}

function animateCustomers(count) {
  const flow = $("customerFlow");
  flow.innerHTML = "";
  const icons = ["🙂", "😎", "🤓", "🧢", "🎒", "👟", "🎧"];
  for (let i = 0; i < count; i += 1) {
    setTimeout(() => {
      const c = document.createElement("span");
      c.className = "customer";
      c.style.top = `${18 + rand(0, 48)}%`;
      c.style.animationDuration = `${1.5 + Math.random() * 1.4}s`;
      c.textContent = icons[rand(0, icons.length - 1)];
      flow.appendChild(c);
      setTimeout(() => c.remove(), 3200);
    }, i * 90);
  }
}

function averageCondition() {
  return state.businesses.reduce((sum, b) => sum + b.condition, 0) / state.businesses.length;
}

function detectCrisis() {
  if (state.cash < -40) return "La caja cayó a un nivel crítico.";
  if (state.reputation <= 8) return "La reputación de la plaza entró en zona crítica.";
  if (averageCondition() <= 18) return "La infraestructura está demasiado deteriorada.";
  if (state.energy <= 4) return "El equipo se quedó sin energía operativa.";
  return null;
}

function triggerLifeLoss(reason) {
  state.lives = Math.max(0, state.lives - 1);
  addLedger(`D${state.day}`, `Crisis: ${reason}`, "-1 ❤️", "negative");
  renderHUD();
  showQuiz(reason);
}

function showQuiz(reason) {
  let index;
  do {
    index = rand(0, quizBank.length - 1);
  } while (quizBank.length > 1 && index === lastQuizIndex);
  lastQuizIndex = index;
  currentQuiz = quizBank[index];
  $("quizTag").textContent = currentQuiz.tag;
  $("questionEn").textContent = currentQuiz.en;
  $("questionEs").textContent = currentQuiz.es;
  $("quizFeedback").textContent = `Crisis: ${reason}`;
  $("quizFeedback").className = "quiz-feedback";
  $("continueQuizBtn").classList.add("hidden");
  const grid = $("answerGrid");
  grid.innerHTML = "";
  currentQuiz.options.forEach((option, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "answer-btn";
    btn.textContent = `${String.fromCharCode(65 + idx)}. ${option}`;
    btn.addEventListener("click", () => answerQuiz(idx));
    grid.appendChild(btn);
  });
  $("quizModal").classList.remove("hidden");
}

function answerQuiz(index) {
  if (!currentQuiz) return;
  const buttons = [...document.querySelectorAll(".answer-btn")];
  if (buttons.some((b) => b.disabled)) return;
  state.quizAttempts += 1;
  buttons.forEach((b) => { b.disabled = true; });
  buttons[currentQuiz.correct].classList.add("correct");
  const feedback = $("quizFeedback");

  if (index === currentQuiz.correct) {
    state.quizCorrect += 1;
    state.lives = Math.min(state.maxLives, state.lives + 1);
    state.cash += 30;
    state.reputation = clamp(state.reputation + 6, 0, 100);
    feedback.textContent = `✓ Correct. ${currentQuiz.explain} Recuperas la vida, +$30 y +6 reputación.`;
    feedback.className = "quiz-feedback good";
    addLedger(`D${state.day}`, "Geometry Rescue correcto", "+1 ❤️", "positive");
  } else {
    buttons[index].classList.add("wrong");
    feedback.textContent = `✗ Respuesta incorrecta. ${currentQuiz.explain} La vida permanece perdida.`;
    feedback.className = "quiz-feedback bad";
    addLedger(`D${state.day}`, "Geometry Rescue incorrecto", "Vida no recuperada", "negative");
  }

  stabilizeAfterCrisis();
  renderAll();
  $("continueQuizBtn").textContent = state.lives <= 0 ? "VER RESULTADO" : "CONTINUAR PARTIDA";
  $("continueQuizBtn").classList.remove("hidden");
}

function stabilizeAfterCrisis() {
  state.cash = Math.max(state.cash, 18);
  state.reputation = Math.max(state.reputation, 24);
  state.energy = Math.max(state.energy, 34);
  state.businesses.forEach((b) => {
    b.condition = Math.max(b.condition, 32);
    b.stock = Math.max(b.stock, 4);
  });
}

function continueAfterQuiz() {
  $("quizModal").classList.add("hidden");
  currentQuiz = null;
  if (state.lives <= 0) {
    endGame(false, "La plaza agotó todas sus vidas de gestión.");
    return;
  }
  if (pendingAdvance) advanceAfterDay();
}

function advanceAfterDay() {
  pendingAdvance = false;
  if (state.day >= state.maxDays) {
    const success = state.cash >= 180 && state.reputation >= 55 && state.lives > 0;
    endGame(success, success
      ? "Superaste los 12 días con una operación rentable y buena reputación."
      : "Sobreviviste los 12 días, pero faltó alcanzar la meta de caja o reputación.");
    return;
  }
  state.day += 1;
  state.ap = 2;
  currentEvent = pickEvent();
  $("simulationTitle").textContent = "Prepara el día";
  $("simStatus").textContent = "Usa tus puntos de gestión y luego abre la plaza.";
  renderAll();
}

function endGame(success, message) {
  const score = Math.max(0, Math.round(state.cash + state.reputation * 3 + state.lives * 100 + state.quizCorrect * 40 + state.totalCustomers * 2));
  const best = Number(localStorage.getItem("pixelPlazaBest") || 0);
  if (score > best) localStorage.setItem("pixelPlazaBest", String(score));
  $("endIcon").textContent = success ? "🏆" : "📊";
  $("endTitle").textContent = success ? "¡Plaza consolidada!" : "Cierre de operación";
  $("endText").textContent = message;
  $("endStats").innerHTML = `
    <div class="end-stat"><span>Puntuación</span><strong>${score}</strong></div>
    <div class="end-stat"><span>Caja final</span><strong>$${Math.round(state.cash)}</strong></div>
    <div class="end-stat"><span>Reputación</span><strong>${Math.round(state.reputation)}</strong></div>
    <div class="end-stat"><span>Clientes</span><strong>${state.totalCustomers}</strong></div>
    <div class="end-stat"><span>Quiz</span><strong>${state.quizCorrect}/${state.quizAttempts}</strong></div>
    <div class="end-stat"><span>Vidas</span><strong>${state.lives}/${state.maxLives}</strong></div>
  `;
  $("endModal").classList.remove("hidden");
  renderBestScore();
}

function flashShell(kind) {
  const shell = document.querySelector(".game-shell");
  const cls = kind === "good" ? "flash-good" : "flash-bad";
  shell.classList.remove("flash-good", "flash-bad");
  void shell.offsetWidth;
  shell.classList.add(cls);
  setTimeout(() => shell.classList.remove(cls), 600);
}

function confirmRestart() {
  if (window.confirm("¿Reiniciar toda la partida? El mejor puntaje guardado se conserva.")) initGame();
}

function bindUI() {
  document.querySelectorAll(".action-btn").forEach((btn) => {
    btn.addEventListener("click", () => doAction(btn.dataset.action));
  });
  $("openDayBtn").addEventListener("click", runDay);
  $("priceMode").addEventListener("change", renderForecast);
  $("helpBtn").addEventListener("click", () => $("helpModal").classList.remove("hidden"));
  $("closeHelpBtn").addEventListener("click", () => $("helpModal").classList.add("hidden"));
  $("restartBtn").addEventListener("click", confirmRestart);
  $("continueQuizBtn").addEventListener("click", continueAfterQuiz);
  $("playAgainBtn").addEventListener("click", initGame);
  $("helpModal").addEventListener("click", (event) => {
    if (event.target === $("helpModal")) $("helpModal").classList.add("hidden");
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("helpModal").classList.contains("hidden")) $("helpModal").classList.add("hidden");
  });
}

bindUI();
initGame();
