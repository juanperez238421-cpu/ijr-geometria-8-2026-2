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

## Escudo institucional auténtico (2026-10-15)

La cabecera de la evaluación utiliza `assets/escudo-institucional-original.svg`, recurso SVG con imagen WebP optimizada tomada de la **imagen institucional original entregada en las fuentes del proyecto** (`logo_colegio_fondo_blanco.png`). Se conserva su heráldica, colores y proporción; no se reinterpreta con figuras vectoriales inventadas. El cambio solo aplica al examen, sin sobrescribir el escudo SVG general de otros módulos.

## Registro privado de auditoría (2026-10-15)

En el proyecto Supabase existen los registros originales en `public.geo8_canada_quiz_attempts` y una nueva bitácora en `private.geo8_canada_quiz_audit_v1`. La bitácora contiene copias de los intentos ya existentes identificadas como `historical_baseline / BASELINE`, y para futuros cambios utiliza un trigger `AFTER INSERT OR UPDATE OR DELETE` que almacena snapshots de respuestas, incidencias, estado y marcas de tiempo con una huella SHA-256. El hash permite detectar inconsistencias del contenido, **no es una firma externa contra un administrador privilegiado**. La tabla tiene RLS sin políticas públicas y no expone el token de sesión; sus entradas son append-only mediante un trigger de protección contra UPDATE/DELETE. No debe publicarse ningún snapshot con datos personales en GitHub Pages.

Consultas de revisión desde la consola SQL de Supabase, con privilegios administrativos:

```sql
-- Evidencia de entrega por estudiante (solo lectura)
select id, student_name, student_group, state, strikes, started_at,
       submitted_at, (select count(*) from jsonb_object_keys(answers)) as total_respuestas
from public.geo8_canada_quiz_attempts
where student_group='8C' and student_name ilike '%APELLIDO_O_NOMBRE%';

-- Huellas de registros auditados
select audit_id, source, change_type, attempt_id,
       captured_at, (snapshot->>'state') as state,
       snapshot_sha256 = encode(sha256(convert_to(snapshot::text,'UTF8')),'hex') as digest_ok
from private.geo8_canada_quiz_audit_v1
order by audit_id desc;
```


### Vista de auditoría para docentes

Se creó también `private.geo8_canada_quiz_audit_report_v1` (solo para personal autorizado en el editor SQL de Supabase). Cada fila muestra el último snapshot registrado, el tipo de evidencia (`historical_baseline` o `live_trigger`), la cantidad de respuestas, las incidencias, versiones y si el SHA-256 sigue correspondiendo al contenido. Los intentos anteriores a la creación del trigger tienen únicamente una copia retrospectiva: **no se puede afirmar que constituyan un historial detallado de eventos que no fueron capturados originalmente**.

```sql
select attempt_id, student_name, student_group, state,
       strikes, answered_slots, audit_captured_at,
       evidence_source, versions_count, integrity_verified
from private.geo8_canada_quiz_audit_report_v1
order by audit_captured_at desc;
```

Se validó el trigger INSERT/UPDATE/DELETE dentro de una transacción revertida (sin crear intentos de prueba permanentes). Un SHA-256 calculado y almacenado en la misma base de datos no equivale a un sellado de tiempo externo ni resiste a un administrador malicioso con acceso total.

## Mejoras de legibilidad y calculadora (octubre de 2026)

- Instrucciones y enunciados más grandes y de alto contraste; grilla minimalista en escritorio y distribución adaptable para dispositivos móviles.
- Calculadora visible dentro del mismo examen; botones de 46–49 px, foco por teclado, controles con nombres accesibles, pantalla de cálculo y mensajes anunciados mediante ARIA.
- Operaciones: suma, resta, multiplicación, división, paréntesis, exponente, porcentaje, cambio de signo y π=3.14 exactamente (no Math.PI).
- El parser de expresiones no ejecuta JavaScript dinámico ni utiliza servicios externos; no contiene las soluciones de los ejercicios.
- La tecla = calcula. Con el resultado listo, "Usar resultado en mi respuesta" transfiere el valor no negativo al input del ejercicio activo y emite el evento input existente, manteniendo el mismo autoguardado privado en Supabase.
- Mientras se usa la calculadora no es necesario cambiar de pestaña ni abandonar pantalla completa.
- Las operaciones de la calculadora no se registran en Supabase; el estudiante debe escribir su razonamiento en el campo previsto. Cambiar el diseño no modifica intentos o calificaciones previas.

Pruebas: node --test evaluaciones/areas-sombreadas-canada/qa.test.cjs

Incluye precedencia, π, coma decimal, división por cero, caracteres no permitidos, accesibilidad estructural y puntos de ruptura responsive.
