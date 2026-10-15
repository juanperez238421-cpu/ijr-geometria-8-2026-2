# Quiz virtual · Áreas sombreadas · Geometría 8°

Instituto Jorge Robledo · Periodo 3 de 2026

**ESTADO: PREPARACIÓN / VISTA PREVIA — NO ES UN EXAMEN OFICIAL.**

Esta carpeta contiene la estructura visual para una evaluación virtual de estudiantes que estarán fuera de Colombia (Canadá). Se reserva el espacio para **tres ejercicios**, cada uno compuesto por **entre 3 y 5 figuras geométricas**. Los enunciados y las animaciones se integrarán cuando Opus los entregue y el docente los valide.

## Acceso a la interfaz

- Publicación futura bajo GitHub Pages: \`/ijr-geometria-8-2026-2/evaluaciones/areas-sombreadas-canada/\`
- Abrir \`index.html\`. Para probar la vista previa debe usarse un navegador compatible con la Fullscreen API.
- El botón de evaluación **oficial permanece deshabilitado**. No hay credenciales, resultados, calificaciones ni soluciones públicas.
- El modo de prueba no debe compartirse como enlace de evaluación final.

## Layout

1. Portada de instrucciones y estado de preparación.
2. Sesión a pantalla completa: navegación de tres preguntas, enunciado, zona grande para imagen/animación, respuesta numérica con unidad y razonamiento escrito.
3. Panel superior: tiempo transcurrido, avance y contador de incidencias.
4. Incidencias: salida del modo pantalla completa, cambio de pestaña o pérdida de foco. Un evento puede disparar varias señales, pero se contabiliza una sola vez hasta reanudar. Tras la tercera incidencia se bloquea la simulación y se muestra un resumen.
5. Cierre con resumen local **sin envío académico**.

## Integración con el material de Opus

Editar exclusivamente \`manifest.json\` e incorporar imágenes SVG, PNG, WebP o clips MP4/WebM en una subcarpeta \`assets/\` dentro de este módulo. Un ejemplo del formato esperado:

\`\`\`json
{
  "id": "P01",
  "ready": true,
  "title": "Título revisado por el docente",
  "statement": "Enunciado sin solución...",
  "diagram": "assets/p01-diagrama.svg",
  "figure_count": 4
}
\`\`\`

Los archivos de manifest deben contener exactamente P01, P02 y P03 y un \`figure_count\` válido de 3, 4 o 5. El cliente inserta enunciados como texto para evitar la ejecución de HTML. Las animaciones que se muestren durante el examen deben contener **solo el planteamiento**, nunca la solución paso a paso. Las soluciones de Opus deben publicarse aparte **después de finalizar la convocatoria**, bajo control del docente.

**Validación matemática:** antes de activar cada pregunta, cotejar construcción geométrica, proporciones, cotas, solapamientos, región sombreada, método analítico, resultado exacto/aproximado y unidades. No insertar contenido sin esta revisión.

## Limitaciones y garantías que faltan para publicar

GitHub Pages es un hosting **estático**: ni oculta respuestas de manera segura, ni garantiza identidad, ni almacena envíos oficiales, ni impide una segunda pantalla, capturas o uso de otro dispositivo. La Fullscreen API tampoco puede impedir que un estudiante abandone el navegador. Los contadores \`sessionStorage\`, el cronómetro y el bloqueo actuales son **solo una simulación frontend** y pueden alterarse. No deben usarse para imponer una sanción o registrar una nota.

Para una versión oficial se requiere un backend autenticado, con inicio autorizado por el docente, expiración validada en servidor, persistencia transaccional de respuestas, registros con hora del servidor, eventos idempotentes, bloqueo supervisable, control de versiones de preguntas y calificación privada. Contrato de API sugerido:

\`\`\`txt
POST  /api/geometry8/shaded-areas/sessions
PATCH /api/geometry8/shaded-areas/sessions/:id/answers/:problemId
POST  /api/geometry8/shaded-areas/sessions/:id/events
POST  /api/geometry8/shaded-areas/sessions/:id/submit
GET   /api/geometry8/shaded-areas/sessions/:id/status
\`\`\`

La salida de pantalla completa puede deberse también a notificaciones, permisos, fallos del navegador o necesidades de accesibilidad. Configurar excepciones aprobadas previamente, revisión docente y un procedimiento de apelación. Una incidencia técnica no demuestra plagio.

## Lista de control QA previa a publicación

- [ ] Revisar visualmente en 1440 × 900, 1366 × 768 y pantalla móvil.
- [ ] Comprobar funcionamiento en Chrome/Edge de escritorio con Fullscreen API.
- [ ] Comprobar 3 alertas aisladas, deduplicación de \`fullscreenchange\`, \`visibilitychange\` y \`blur\`, bloqueo después de la tercera y reanudación entre alertas.
- [ ] Verificar navegación 1→2→3→1, conservación de respuestas en vista previa y unidades.
- [ ] Comprobar recarga, volver atrás, sesión interrumpida y navegador sin fullscreen.
- [ ] Validar contraste, teclado, texto ampliado y alternativas accesibles.
- [ ] Integrar los 3 ejercicios de Opus y comprobar sus 3–5 figuras.
- [ ] Revisar manualmente cada solución con dos métodos independientes y validar que no sea visible antes del cierre.
- [ ] Implementar y probar servidor, permisos, persistencia y auditoría.
- [ ] Fijar duración, horario según zona horaria del servidor y ventanas de acceso para Canadá/Colombia.
- [ ] Realizar prueba con cuentas estudiantiles ficticias y revisar los registros reales antes de activar el botón oficial.

## Separación del repositorio

Este módulo reside solo en \`evaluaciones/areas-sombreadas-canada/\`. No se modifica la página principal ni se añade navegación estudiantil mientras no esté listo.
