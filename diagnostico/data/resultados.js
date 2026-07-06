// Datos base para el diagnóstico inicial de Geometría 8°.
// IMPORTANTE: este repositorio es público. No subir aquí datos personales reales
// sin revisar antes un mecanismo de autenticación privado.

const DIAGNOSTIC_CONFIG = {
  course: "Geometría 8°",
  period: "2026-2",
  totalQuestions: 15,
  secondsPerQuestion: 60,
  teacherPassword: "geo-docente-2026",
  groups: ["8A", "8B", "8C"],
};

const QUESTIONS = [
  { id: 1, topic: "Puntos, rectas y planos", answer: "B", skill: "Reconocer elementos geométricos básicos" },
  { id: 2, topic: "Ángulos", answer: "C", skill: "Identificar tipos de ángulos" },
  { id: 3, topic: "Rectas paralelas y perpendiculares", answer: "A", skill: "Relacionar posiciones relativas entre rectas" },
  { id: 4, topic: "Triángulos", answer: "D", skill: "Clasificar triángulos según lados o ángulos" },
  { id: 5, topic: "Cuadriláteros", answer: "B", skill: "Diferenciar propiedades de cuadriláteros" },
  { id: 6, topic: "Perímetro", answer: "A", skill: "Calcular longitudes alrededor de una figura" },
  { id: 7, topic: "Área", answer: "C", skill: "Aplicar fórmulas de área en figuras planas" },
  { id: 8, topic: "Circunferencia y círculo", answer: "D", skill: "Relacionar radio, diámetro y perímetro" },
  { id: 9, topic: "Unidades de medida", answer: "B", skill: "Convertir o interpretar magnitudes geométricas" },
  { id: 10, topic: "Plano cartesiano", answer: "A", skill: "Ubicar puntos y reconocer coordenadas" },
  { id: 11, topic: "Simetría", answer: "C", skill: "Identificar ejes de simetría" },
  { id: 12, topic: "Transformaciones", answer: "B", skill: "Reconocer traslación, rotación o reflexión" },
  { id: 13, topic: "Sólidos geométricos", answer: "D", skill: "Asociar figuras 3D con sus elementos" },
  { id: 14, topic: "Razonamiento espacial", answer: "A", skill: "Interpretar información visual" },
  { id: 15, topic: "Resolución de problemas", answer: "C", skill: "Seleccionar procedimientos adecuados" },
];

const GROUP_RESULTS = {
  "8A": {
    students: 0,
    average: null,
    questions: QUESTIONS.map(q => ({ id: q.id, correctPercent: null, dominantError: "Pendiente por cargar resultados" }))
  },
  "8B": {
    students: 0,
    average: null,
    questions: QUESTIONS.map(q => ({ id: q.id, correctPercent: null, dominantError: "Pendiente por cargar resultados" }))
  },
  "8C": {
    students: 0,
    average: null,
    questions: QUESTIONS.map(q => ({ id: q.id, correctPercent: null, dominantError: "Pendiente por cargar resultados" }))
  }
};

// Plantilla privada. Cada registro se consulta con grupo + documento.
// Ejemplo futuro:
// "8A": {
//   "1234567890": { name: "Estudiante", score: 11, percent: 73.3, correct: [1,2,3], incorrect: [4,5], feedback: "Repasar áreas y ángulos." }
// }
const INDIVIDUAL_RESULTS = {
  "8A": {},
  "8B": {},
  "8C": {}
};
