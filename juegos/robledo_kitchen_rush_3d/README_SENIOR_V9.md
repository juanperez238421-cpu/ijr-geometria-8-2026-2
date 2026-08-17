# Robledo Kitchen Rush 3D — Senior V9

Senior V9 is a deliberate interaction redesign. It keeps the restaurant, recipes, stock, business progression, true-solo roster, NPC loyalty/traits, customization, expansions and Geometry Rescue systems from the previous production version, but replaces the Player 1 service interaction model.

## Senior QA findings from V8.1

V8.1 solved unreliable mouse events by layering several mechanisms: canvas pointer handlers, window-level fallbacks, right-button hold state, auxiliary-click recovery, low-FPS watchdogs, proximity correction and multiple visual pulses/particles. That improved fault tolerance, but it produced an interaction model that felt busy, indirect and difficult to read. The user could not easily tell whether a right-click was selecting, approaching, working, camera-dragging or being recovered by a fallback.

Senior V9 removes that ambiguity.

## Player 1 interaction contract

- **Left click floor:** move.
- **Left click object:** approach and perform one contextual primary action.
- **Prep / sink:** one click starts the timed job; no button holding is required.
- **Right click:** cancel only. It never picks food, chops, washes, cooks or controls the service camera.
- **Middle click:** throw the held item.
- **E / Space:** use the selected or nearest target.
- **Mouse wheel:** zoom.
- **C / Home:** camera preset / reset.
- In build mode the normal right-drag camera is restored.

## Interaction state machine

Player 1 now uses one explicit state machine: `idle → approach → execute/work → complete`. The chef never depends on a held mouse button to finish chopping or washing. Cook stations remain independent real-time appliances: one click places the food, cooking continues while the chef performs another task, and a later click collects the ready item.

## Presentation changes

Interaction feedback is intentionally quieter. V9 removes Player 1's legacy interaction particle bursts, pulsing selection spam and hold-to-work animation. A static target ring communicates selection. A compact action panel says exactly what the next click will do. Timed prep and washing show a single progress bar. The live service board adds station status chips for PREP, SINK, STOVE, FRYER and OVEN states.

## Solo service

One-player mode remains truly solo: one human chef, zero hidden AI helpers. The player must take orders, collect groceries, prep, cook, assemble, serve, clear tables and wash plates. Existing solo customer-cap and patience balancing remains active.

## Layout redesign

The recommended layout is now a compact work triangle rather than a long production line: grocery wall at the back, cleaning area on the left, cooking/prep wings around the kitchen, central pass/counters and wider dining lanes. The objective is to reduce unnecessary walking while preserving readable station separation.

## Systems retained

- six physical recipe workflows;
- finite grocery stock and paid restocking;
- recipe pinning and contextual guidance;
- cleanliness, shift goals and bonuses;
- chef XP and customer loyalty;
- returning regulars and NPC personality traits;
- customer mood/state bubbles;
- restaurant expansion and persistent business state;
- character name, gender/presentation, skin tone, body build, hair, uniform, apron and accessories;
- three local human-player modes;
- Geometry Rescue after life loss.

## QA gate

The V9 CI browser test verifies real Player 1 left-click pickup, cancellation-only right click, stock decrement, single-click automatic prep, task cancellation without item loss, solo zero-bot roster, NPC systems, service board integration, P2/P3 movement, build-mode pointer restoration, standalone offline packaging and Windows/Linux portable launchers.
