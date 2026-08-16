# Robledo Kitchen Rush 3D — Senior Dynamic V4

This edition changes the game from a fixed three-player kitchen into a flexible local-coop restaurant simulator.

## Main additions

- 1, 2 or 3 human players on one PC; every unused crew slot becomes a physical autonomous bot.
- Role assignment for all three crew slots: Head Chef, Prep Specialist and Service Captain.
- Role-specific speed, cooking, chopping, washing and tip modifiers.
- Pre-shift menu planning with 3–5 active dishes.
- Full kitchen Build Mode with starting budget, fixture placement, zone validation, collision checks, removal/refunds and recommended auto-layout.
- Players place dining tables, counters, ingredient crates, prep boards, stove, fryer, oven, sink, plate rack and trash before opening.
- Seven-step onboarding tutorial for controls, orders, food states, kitchen planning, roles and camera.
- Perspective 3D CameraRig with dynamic crew-centroid follow, gyroscope-style lean, right-mouse orbit, wheel zoom and camera presets.
- Enlarged, more detailed procedural chefs, customers, stations, tables, ingredients and environment.
- Physical customers still enter, sit, browse, order, wait, eat and leave dirty dishes.
- Human cooking remains physical: ingredients -> prep -> cook/fry/bake -> plate -> table -> sink.
- Bot AI physically walks between installed stations and completes role-biased order or cleaning task pipelines.
- Existing Geometry Rescue remains isolated from normal play and appears only after a team life is lost.

## Browser E2E acceptance path

The CI test must execute the real user path:

1. Load WebGL game.
2. Click Plan a New Shift.
3. Verify flexible crew setup and two bots in the default one-human configuration.
4. Continue into tutorial.
5. Skip/finish tutorial.
6. Verify Build Mode begins with an invalid empty kitchen.
7. Install the Recommended Layout.
8. Verify all generated requirements are satisfied.
9. Open Restaurant.
10. Verify three crew members exist, two are bots, the HUD is visible and the service timer advances.

The source is bundled offline by the existing Three.js/esbuild pipeline and served by the portable localhost launcher.