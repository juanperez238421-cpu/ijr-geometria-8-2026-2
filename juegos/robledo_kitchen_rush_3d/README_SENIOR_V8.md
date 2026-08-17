# Robledo Kitchen Rush 3D — Senior V8

Senior V8 is a full gameplay/interaction revision focused on reliable human control, true solo service, readable kitchen production and richer restaurant simulation.

## Control correction

Player 1 no longer depends on a fragile select-then-interact sequence. During service, left click on an interactive object performs a smart action: the chef approaches the object and interacts when in range. Right click/hold performs manual interaction/work and is reserved for Player 1 rather than camera orbit. Middle click throws. Player 2 uses WASD + F/E/Q/Left Shift. Player 3 uses arrow keys + Period/Enter/Slash/Right Shift.

Senior V8.0.5 makes the first left/right mouse interaction execute synchronously on pointer-down whenever the chef is already in range. This removes a low-frame-rate race in which a short click could be released before the next WebGL animation frame and therefore appear to do nothing. If the target is farther away, the same click queues approach-and-interact behavior. Prep and sink work also have deterministic continuous-action semantics and a watchdog for throttled embedded browsers.

## True solo

Selecting one human player creates exactly one chef and no autonomous bots. The single player personally takes orders, gathers ingredients, preps, cooks, assembles, serves and cleans. Solo customer capacity, party size and patience are scaled so the loop remains demanding but playable.

## Restaurant layout

The recommended layout now uses a clear back-wall grocery zone, grouped sink/plate cleaning zone, centered prep/cook/assembly production line and wider dining/service aisles. The arrangement adapts to expansion tier.

## Recipe and ingredient systems

All six recipes have explicit physical routes from grocery to preparation/cooking, assembly and service. The recipe book shows each station step and recipes can be pinned to a live service board. Ingredient interactions add clearer state guidance, selection feedback, pickup/placement effects, idle presentation, cooking/prep particles and finite shift stock. Empty grocery compartments can be restocked through interaction for a small business cost.

## Character personalization

Every active human chef can set a name, gender/presentation, skin tone, body build, hair style, hair color, uniform color, apron color and accessory. Gender does not restrict appearance choices. Profiles persist locally.

## NPC and management systems

Customers now receive service traits, mood/speech bubbles, stronger waiting/eating gestures and a chance to become returning regulars. Senior V8 adds persistent loyalty and chef XP, shift objectives, cleanliness scoring, clean-kitchen bonuses and stock visibility.

## QA

The Senior V8 browser test validates true solo mode, zero bots, improved layout, six detailed recipe cards, character customization, real Player 1 left-click interaction, real Player 1 right-click grocery pickup, prep workflow, NPC dynamics, live management board, Player 2 WASD and Player 3 arrow controls. The workflow also validates the standalone offline HTML and native local Windows/Linux launchers.
