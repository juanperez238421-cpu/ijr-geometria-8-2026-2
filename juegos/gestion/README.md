# Robledo Bistro 3D

Juego alternativo de **gestión y administración en un entorno 3D** para Geometría 8°. La mecánica principal no depende de contenidos académicos: el estudiante administra y opera un restaurante low-poly, inspirado en el ritmo de los juegos de cocina y servicio.

## Idea central

El jugador controla directamente al chef/gerente dentro de una cocina tridimensional. Debe desplazarse entre estaciones, completar recetas y atender clientes antes de que se agote su paciencia.

Flujo típico:

1. **Refrigerador:** tomar el pedido más urgente.
2. **Mesa de preparación:** cortar / preparar.
3. **Estufa:** cocinar cuando la receta lo requiere.
4. **Pase de servicio:** entregar el plato al cliente.

Las recetas tienen rutas diferentes y los clientes se acumulan durante horas pico. La rapidez de servicio afecta propinas, reputación y supervivencia del restaurante.

## Mecánicas de gestión

- Campaña de 5 días.
- Caja y reputación persistentes entre días.
- Objetivo mínimo de pedidos por turno.
- Cola de clientes con paciencia individual.
- Propinas variables por rapidez.
- Tres vidas.
- Tres clientes que abandonan sin ser atendidos provocan la pérdida de una vida.
- No alcanzar la meta diaria también provoca una pérdida de vida.
- Mejoras entre turnos:
  - mesa de preparación,
  - estufa,
  - decoración/paciencia,
  - ayudante de cocina automático.
- Puntuación final y mejor puntuación guardada en `localStorage`.

## Cuestionario de Geometría

La geometría **no forma parte del loop principal del restaurante**. Una pregunta aparece únicamente cuando se pierde una vida.

- Si la respuesta es correcta, se recupera la vida.
- Si es incorrecta, la vida permanece perdida.
- El juego queda completamente pausado mientras se responde.
- Banco bilingüe EN/ES con áreas, perímetros, círculos, figuras compuestas y áreas sombreadas.

## Entorno 3D

El juego usa un renderer low-poly propio construido con coordenadas **X/Y/Z**, proyección isométrica, ordenamiento por profundidad, cajas tridimensionales, paredes, mobiliario, estaciones, mesas, personajes y sprites de estado. No usa librerías externas, por lo que puede ejecutarse completamente offline.

Incluye:

- cocina y comedor tridimensionales,
- colisiones con mobiliario,
- seguimiento de cámara,
- clientes animados entrando, haciendo fila, comiendo y saliendo,
- chef controlable con WASD/flechas,
- sprint con Shift,
- interacción contextual con E,
- descarte de plato con Q,
- vapor animado sobre la estufa,
- indicadores 3D de estaciones y pedidos.

## Identidad institucional

Se utiliza la imagen real `assets/logo_colegio_transparente.png` del Instituto Jorge Robledo tanto en la interfaz como dentro del escenario. El empaquetador offline la incrusta como `data:image/png;base64`, por lo que sigue visible sin conexión.

## Ejecutar desde el repositorio

Abre:

`juegos/gestion/index.html`

No requiere backend.

## Crear versión offline en un único HTML

```bash
python juegos/gestion/build_offline.py
```

Genera:

- `dist/Robledo_Bistro_3D_OFFLINE.html`
- `dist/Robledo_Bistro_3D_OFFLINE_Package.zip`
- `dist/LEEME.txt`

El HTML generado contiene CSS, JavaScript y logo incrustados. El estudiante puede abrirlo con doble clic en Chrome, Edge o Firefox sin Internet ni instalación.

## Privacidad

No hay cuentas, login, anuncios, analítica, librerías remotas ni envío de información. Solo se guarda la mejor puntuación en el navegador local.
