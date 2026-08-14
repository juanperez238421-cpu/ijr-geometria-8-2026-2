# Robledo Bistro 3D Senior

Versión ampliada del juego alternativo de gestión para Geometría 8°. Es un simulador de restaurante 3D low-poly, offline y sin dependencias externas.

## Experiencia principal

- Mapa 3D mucho más grande con cocina, almacén, salón, lobby, zona de expansión y terraza.
- Clientes que entran, esperan mesa, se sientan, consultan la carta, seleccionan un plato, esperan, comen y salen.
- Partidas/grupos de 1–4 clientes y mesas con capacidad.
- Carta configurable: activar/desactivar platos, ajustar precios, desbloquear recetas y controlar inventario.
- Flujo de cocina: tomar comanda → ingredientes → preparación → cocción/horno → pase → llevar a la mesa.
- Platos terminados almacenados en el pase; el jugador o un waiter puede entregarlos.

## Gestión senior

Entre turnos existen cinco áreas de decisión:

1. **Resumen:** ingresos, reputación, walkouts, inventario y reabastecimiento.
2. **Carta & recetas:** selección del menú, precios y desbloqueo de recetas.
3. **Personal:** host, cook, waiter y cleaner con contratación, salarios y niveles.
4. **Expansión:** nuevo comedor, terraza y ala de cocina; las compras modifican físicamente el mapa.
5. **Personalización:** estilos visuales con bonificaciones de ambiente/paciencia.

## Empleados

- **Host:** acelera la asignación de mesas y protege la paciencia de la fila.
- **Cook:** produce automáticamente algunos pedidos en cocina.
- **Waiter:** recoge platos listos del pase y los lleva a las mesas.
- **Cleaner:** libera mesas sucias más rápido.

## Assets

El juego usa el logo real `assets/logo_colegio_transparente.png` y assets SVG originales incluidos en `juegos/gestion/assets/` para carta, letrero y platos. El empaquetador los incrusta como data URI en la versión standalone.

## Geometry Rescue

La geometría no controla las mecánicas de restaurante. Solo aparece una pregunta bilingüe cuando se pierde una vida. Una respuesta correcta recupera la vida.

## Offline

`python juegos/gestion/build_offline.py` genera:

- `dist/Robledo_Bistro_3D_SENIOR_OFFLINE.html`
- `dist/Robledo_Bistro_3D_SENIOR_OFFLINE_Package.zip`

No requiere servidor, cuenta, analytics ni conexión a Internet después de descargar.
