# Pixel Plaza Manager

Juego alternativo de gestión para estudiantes de Geometría 8°.

## Propósito de diseño

El núcleo del juego **no depende de la geometría**. El estudiante administra una pequeña plaza comercial y toma decisiones de inventario, mantenimiento, contratación, mejoras, campañas, precios y energía del equipo. Esto ofrece una alternativa para estudiantes que prefieren gestión, estrategia económica y toma de decisiones en lugar de combate táctico.

La integración académica ocurre únicamente cuando el jugador entra en crisis y pierde una vida. En ese momento se pausa la simulación y se activa **Geometry Rescue**, una pregunta de selección múltiple relacionada con:

- área y perímetro;
- rectángulos, cuadrados, triángulos, paralelogramos y trapecios;
- círculo, radio, diámetro y sectores;
- áreas sombreadas simples y compuestas;
- descomposición y sustracción de áreas;
- selección conceptual entre área y perímetro.

Las preguntas se muestran en inglés y español para mantener el contenido disciplinar accesible sin convertir el idioma en una barrera para la comprensión matemática.

## Mecánicas principales

- 12 días de gestión.
- 3 negocios administrables.
- 2 puntos de gestión por día.
- Caja, reputación, energía, stock, personal, condición y nivel de negocio.
- Estrategias de precio económica, estándar y premium.
- Eventos aleatorios positivos, negativos y neutrales.
- Campañas temporales, mejoras, mantenimiento y contratación.
- Simulación visual de clientes y resultados diarios.
- 3 vidas.
- Quiz de rescate únicamente al perder una vida.
- Respuesta correcta: recupera la vida y estabiliza la partida.
- Respuesta incorrecta: la vida permanece perdida.
- Banco de 26 preguntas de geometría.
- Mejor puntuación guardada únicamente en `localStorage` del navegador.
- Sin cuentas, anuncios, analítica, backend ni recolección de datos personales.

## Condición de victoria

Completar los 12 días con:

- caja final de al menos `$180`;
- reputación de al menos `55`;
- al menos una vida disponible.

## Archivos

- `index.html`: interfaz del juego y modales.
- `style.css`: diseño responsivo y animaciones.
- `game.js`: motor de simulación, eventos, decisiones, crisis y cuestionario.

## Ejecución

Abrir `index.html` directamente o usar la ruta de GitHub Pages del repositorio. No requiere instalación ni librerías externas.
