# Robledo Kitchen Rush 3D

A full local **Three.js isometric cooperative cooking game for exactly three simultaneous players on one PC**. The project intentionally uses original procedural low-poly 3D art and mechanics rather than copying assets or level layouts from commercial cooking games.

## What is implemented

- True Three.js 3D scene with orthographic/isometric camera, ACES tone mapping, dynamic shadows, fog and a stylized miniature-kitchen look.
- Three simultaneous chef characters with independent controls, collisions, dash, pickup/drop and real item throwing.
- Three keyboard layouts plus automatic support for the first three connected gamepads.
- Physical ingredient objects and state transitions: raw, chopped, cooked/fried/baked and burnt.
- Physical kitchen stations: ingredient crates, two chopping boards, stove, fryer, oven, assembly counters, clean-plate stack, sink and trash.
- Cooking/preparation progress indicators above stations.
- Six recipes: Rush Burger, Garden Salad, Golden Fries, Mini Pizza, Grill Plate and Cheesy Toast.
- Plate-based assembly: ingredients must actually be prepared and combined in the correct state.
- Customers enter the restaurant, walk to tables, sit, browse the menu, choose dishes, create timed order tickets, wait, eat and leave.
- Party sizes of 1–3; a table can request multiple different dishes in the same order.
- Correct physical delivery to the correct table. Wrong dishes are rejected and break the combo.
- Customer patience timers, walkouts, team lives, tips and a combo multiplier.
- Dirty plates remain after a party leaves; players collect them and wash them at the sink before reuse.
- Three-level local campaign: Bistro Basics, Split Service and Dinner Rush, with increasing menu complexity, table count and customer pressure.
- 0–3 star scoring and localStorage progression/unlocks.
- Recipe book, controls screen, pause/restart, results screen and persistent local best progress.
- Geometry Rescue remains separated from normal gameplay and triggers only after a team life is lost.
- Official Instituto Jorge Robledo logo is embedded in the generated standalone build from the repository asset.

## Controls

### Player 1
WASD • `E` interact/work • `Q` throw • Left Shift dash

### Player 2
Arrow keys • `Enter` interact/work • `/` throw • Right Shift dash

### Player 3
IJKL • `O` interact/work • `U` throw • `P` dash

### Gamepad
Left stick • A/Cross interact • X/Square throw • B/Circle dash. The first three connected gamepads map to P1–P3.

For three students playing at once, three USB/Bluetooth gamepads are recommended because many keyboards have hardware key-ghosting limitations.

## Offline build

The build uses `three` plus `esbuild`. `scripts/build.mjs` bundles Three.js and the complete game into a single IIFE script, then inlines JavaScript, CSS and the school logo into `dist/Robledo_Kitchen_Rush_3D_OFFLINE.html`. The result can be opened directly with `file://`; it does not need a server after download.

GitHub Actions validates the source, builds the standalone game and publishes a ZIP containing both the ready-to-play offline HTML and complete editable source.
