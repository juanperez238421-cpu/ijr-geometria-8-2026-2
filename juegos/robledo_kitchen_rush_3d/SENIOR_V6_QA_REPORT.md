# Senior QA — Autonomous Service V6

## Defects identified in V5

1. Ingredient storage was represented as one crate per ingredient. It looked like debug/test fixtures rather than a restaurant grocery system.
2. `BotBrain` did not use the live item/station mechanics. It displayed synthetic carry models, waited arbitrary durations, then called `party.serve()` directly. Therefore bots could appear to cook without creating, chopping, heating or assembling a real `WorldItem`.
3. Customer tickets appeared automatically after browsing. The Service Captain role was not required to take the customer's order.
4. Bot movement used direct steering only and could stall against obstacles.
5. Dirty-table bot cleaning was simulated rather than using the real dirty plate + sink + rack loop.

## V6 acceptance criteria

- One Grocery Market + Freezer build fixture; no active tomato/lettuce/meat/etc. crate buttons.
- Grocery interior visibly displays menu-required ingredients behind market-style glass doors and category headers.
- The fixture creates distinct logical pickup compartments so both humans and bots can request a specific ingredient.
- Customers transition through `readyToOrder`; a human or bot must confirm the order.
- Fast Service begins at confirmation, not while the customer is browsing or waiting for a waiter.
- Bot cooking uses real `Game.interact()` calls and live plates, ingredients, prep boards, cooking stations and counters.
- Bot cleaning uses a real dirty plate, sink progress and plate-rack return.
- Bot station reservations prevent two bots from corrupting the same production slot.
- Obstacle avoidance provides a sidestep fallback when direct bot movement is blocked.
- Browser E2E must observe the complete event chain rather than only checking UI text.

## Automated browser scenarios

### Scenario A — Starter storage and layout
Fresh local storage -> Tier 1 -> Recommended Layout. Verify 2 tables, exactly one grocery fixture, zero legacy ingredient crates and logical storage compartments for bun, lettuce, meat and tomato.

### Scenario B — Waiter + salad
Create a table in `readyToOrder`; a Service bot must reach it and confirm the ticket. A Prep bot must then pick tomato and lettuce from the real grocery wall, chop both on the real prep station, add them to a real plate on the counter and serve the identified Salad. The test begins with two lives and requires the completed fast table to restore the third life.

### Scenario C — Burger stove path
A second order forces a bot to retrieve meat and bun, put meat on the live stove, wait until `cooked`, retrieve it, assemble the burger plate and serve it.

### Scenario D — Cleaning
Inject one dirty table. A bot must pick up the dirty plate, insert it into the live sink, execute wash progress, retrieve the clean plate and return it to the plate rack.

### Failure policy
Any JavaScript runtime exception, console error, missing station transition, task abort during the burger scenario, missing waiter confirmation, missing ingredient event or incomplete cleaning cycle fails CI.
