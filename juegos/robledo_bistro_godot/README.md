# Robledo Bistro Senior — Godot 4 local game

This directory contains the **full desktop edition** of the restaurant-management game. It is no longer an HTML simulation: it is a Godot 4 project designed to export as a Windows `.exe` and Linux binary.

## Main mechanics

- Large restaurant map: kitchen, lobby, main dining room, storage, locked Dining Hall B, Garden Terrace and Kitchen Wing.
- Parties of 1–4 enter, queue, are assigned to tables, sit, browse the active menu, place individual dish orders, wait, eat, pay and leave.
- Tables become dirty after service and must be reset by the player or cleaner.
- Direct chef control with WASD / arrows, Shift sprint, E interaction, Q discard, M menu and Tab map.
- Recipe pipeline: fridge → prep → stove/oven when required → service pass → physical table delivery.
- Eight recipes with dedicated original dish assets and ingredient requirements.
- Inventory and emergency restocking.
- Configurable active menu (2–6 dishes), recipe unlocks and adjustable prices.
- Hire and train Host, Cook, Waiter and Cleaner; each role has wages and automation effects.
- Expand Dining Hall B, Garden Terrace and Kitchen Wing. The oven is physically unavailable until Kitchen Wing is bought.
- Kitchen equipment upgrades reduce preparation times.
- Restaurant themes (Classic, Garden, Neon).
- Seven-day campaign, cash, reputation, daily targets, walkouts, wages and local save/continue.
- Geometry Rescue appears **only after a life is lost**. Correct answers restore the life.

## Local development

1. Install Godot 4.3 or newer.
2. Import `project.godot` from this folder.
3. Press F6/F5 or run the main scene.

## Controls

- `WASD` / arrows: move
- `Shift`: sprint
- `E`: interact with nearest station/table
- `Q`: discard current dish
- `M`: current restaurant menu
- `Tab`: operational map
- `Esc`: close soft overlays

## Build

The repository workflow `.github/workflows/build-robledo-bistro-godot.yml` downloads the official Godot 4.3 headless editor and export templates, validates the project, exports Windows and Linux builds, and uploads a single offline ZIP artifact.

All custom SVG art in `assets/` was created specifically for this project. The official school logo is copied from the repository's existing `assets/logo_colegio_transparente.png`.
