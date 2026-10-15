# Evaluación virtual · Áreas sombreadas · Geometría 8°

Instituto Jorge Robledo · 2026, periodo 3 · estudiantes en Canadá.

**PÁGINA PÚBLICA:** https://juanperez238421-cpu.github.io/ijr-geometria-8-2026-2/evaluaciones/areas-sombreadas-canada/

Cuatro problemas con enunciados y diagramas SVG de alta definición, siguiendo las cuatro imágenes aprobadas. En el navegador no se incluyen respuestas ni pasos de solución.

## Los cuatro ejercicios

1. Sector anular de **270°**: R = 6 cm; r = 3 cm.
2. Círculo inscrito en un cuadrado: lado = 12 cm; r = 6 cm.
3. Semicírculo y triángulo: diámetro = 12 cm; altura = 6 cm.
4. Cuatro cuartos de círculo en un cuadrado: lado = 14 cm; radio = 7 cm.

**Instrucción común:** Observa la figura y calcula el área de la región sombreada. Expresa tu respuesta en cm². Usa π = 3.14 cuando sea necesario.

## Proceso estudiantil

1. Escribe nombre y apellido, selecciona grupo (8A, 8B, 8C o movilidad) y acepta las reglas.
2. Activa pantalla completa e inicia. El intento se crea en la base privada de Supabase.
3. Navega entre los 4 ejercicios libremente. Las respuestas se guardan automáticamente en el servidor.
4. Responde con área, unidades (cm²) y justificación en texto.
5. Pulsa **Enviar evaluación** y conserva el identificador de comprobante.

La sesión queda vinculada a un token aleatorio de 256 bits guardado en el navegador (sessionStorage); el servidor guarda solo su hash SHA-256. Nunca se publican datos estudiantiles, claves o soluciones en el repositorio.

## Tres incidencias

El frontend vigila fullscreenchange, visibilitychange y blur y registra un incidente por salida para evitar contabilizaciones duplicadas de un mismo cambio. Los eventos se guardan en la tabla privada geo8_canada_quiz_attempts, junto con la hora del servidor. Tras tres eventos el servidor marca la sesión como **blocked** y no admite nuevas respuestas ni entregas. El docente deberá revisar las circunstancias; una salida de pantalla completa **no demuestra plagio**. La página no puede impedir capturas, móviles externos ni edición del navegador, y los eventos pueden ser omitidos por usuarios técnicamente avanzados. La regla se comunica explícitamente antes del inicio.

El temporizador es informativo; no se inventó una duración o fecha límite, pues aún no fueron fijadas por el docente.

## Backend aislado

- Supabase project: `rlfxnjbqxbozjdzkbwlz`
- Edge Function: `geometry8-canada-quiz`
- Tabla privada (RLS, sin grants a anon/authenticated): `public.geo8_canada_quiz_attempts`
- Operaciones: start, status, answer, incident, submit
- La función de borde usa service role **únicamente en servidor**, con token opaco por intento. Un cliente no puede consultar otros intentos sin token.
- Aún no hay un panel docente dentro de la página. Un docente con acceso a Supabase puede revisar registros privados mediante consultas autorizadas.

Ejemplo de reporte para un administrador autenticado en Supabase (consulta ejecutada solo en servidor):

```sql
select student_name, student_group, state, strikes, answers, started_at, submitted_at
from public.geo8_canada_quiz_attempts
order by started_at desc;
```

El registro por nombre no comprueba por sí mismo identidad institucional y los incidentes del navegador no son supervisión invulnerable. Se recomienda acceso mediante cuentas escolares para próximas convocatorias, validación de identidad, política de recuperación y revisión docente.

## QA

```bash
node --test evaluaciones/areas-sombreadas-canada/qa.test.cjs
```

- 4 manifest entries completadas; SVG individuales bajo assets/.
- 4 controles de navegación, 3 indicadores de incidencias y envío.
- No hay claves de respuestas ni enlace de solución.
- Validar manualmente navegador Edge/Chrome en desktop, viewport móvil y servicio de Supabase antes de usar para asignar una nota.
