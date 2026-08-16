ROBLEDO KITCHEN RUSH 3D — SENIOR AUTONOMOUS SERVICE V6

CORE CHANGE
The old individual ingredient crates are removed from the active build system. A single procedural Grocery Market + Freezer wall contains labeled pickup compartments for every ingredient required by the active menu.

CUSTOMER SERVICE
Customers now enter -> sit -> browse -> READY TO ORDER. A human or bot must physically reach the table and take the order. Only after confirmation does the 30-second fast-service timer begin.

BOT AI
Bots no longer simulate dishes with a fake carry visual. They use the same live WorldItem and station interaction functions as humans:
- take customer order
- pick a clean plate
- collect exact groceries from the market/freezer
- chop on the prep board
- cook on stove/fryer/oven and wait for real ready state
- assemble components on a real plate at a counter
- deliver the identified recipe to the correct table
- collect dirty plates, wash them and return them to the rack

QA
Static source validation rejects the old simulated BotBrain path and legacy ingredient-crate fixture labels. Browser E2E validates a real waiter order, a complete salad preparation chain, a burger stove chain, fast-service life restoration, and a real dirty-plate wash/return cycle.
