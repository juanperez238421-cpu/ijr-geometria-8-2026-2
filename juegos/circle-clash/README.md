# Circle Clash Arena · Geometría 8°

Juego multijugador 2D para practicar radio, diámetro, longitud de la circunferencia, área y número π.

## Decisión técnica: 2D sobre 3D

Para esta actividad se prioriza **2D web nativo** en lugar de Three.js/Godot. El objetivo principal es que 2–12 equipos mantengan una sesión sincronizada y puedan responder/atacar desde computadores escolares con hardware y redes heterogéneas. El render 2D elimina WebGL, modelos, texturas y un bucle 3D continuo, reduciendo carga de GPU, tiempo de descarga y puntos de falla. El repositorio conserva los proyectos 3D existentes para actividades donde la visualización espacial sí es el objetivo principal.

## Arquitectura de conexión

- Frontend estático en GitHub Pages: HTML + CSS + JavaScript sin dependencias externas.
- Backend autoritativo: Supabase Edge Function `geo8-circle-clash`.
- Estado persistente: PostgreSQL.
- El navegador **nunca calcula la respuesta correcta ni modifica directamente la puntuación**.
- Cada equipo recibe un token aleatorio de alta entropía; en base de datos solo se conserva su SHA-256.
- Respuestas y ataques usan UUID idempotentes para que un reintento de red no duplique puntos ni daño.
- El cliente realiza snapshots cortos y periódicos. Si se pierde Internet, reanuda desde el último evento confirmado.
- El reloj de ronda es del servidor; el reloj local solo dibuja la cuenta regresiva.
- No hay dependencia funcional de un WebSocket persistente: una caída temporal de conexión no destruye la partida.

## Reglas

- Cada equipo inicia con **100 puntos = 5.0**.
- Nota visible: `puntos / 20`.
- Piso de seguridad: **20 puntos = 1.0**.
- Respuesta incorrecta: −2 puntos.
- Respuesta correcta: genera carga según rapidez y racha.
- Solo una respuesta correcta en la ronda habilita una acción de batalla:
  - `Arc Bolt`: 10 de carga → −5 puntos al objetivo.
  - `Pi Cannon`: 16 de carga → −8 puntos al objetivo.
  - `Diameter Shield`: 12 de carga → +8 de escudo.
- El escudo absorbe daño antes de restar puntuación.
- 12 rondas; 40 s para resolver + 12 s de batalla.
- La sala inicia automáticamente 15 s después de que entra el segundo equipo.

## Privacidad y seguridad

Los equipos usan alias. No se requiere nombre completo, correo, cuenta Supabase ni otro dato personal. Las tablas del juego tienen RLS habilitado y no conceden lectura/escritura directa a `anon` o `authenticated`; las mutaciones pasan exclusivamente por funciones `SECURITY DEFINER` invocadas por la Edge Function.

## QA

Prueba estática:

```bash
node juegos/circle-clash/qa/static.mjs
```

Prueba real de integración contra Supabase:

```bash
node juegos/circle-clash/qa/integration.mjs
```

La integración crea dos equipos QA con una sala aleatoria, espera el reloj real del servidor, prueba respuesta correcta/incorrecta, idempotencia de reintentos, bloqueo de ataque tras respuesta incorrecta, ataque válido, daño final y recuperación del stream de eventos.

## URL

`https://juanperez238421-cpu.github.io/ijr-geometria-8-2026-2/juegos/circle-clash/`
