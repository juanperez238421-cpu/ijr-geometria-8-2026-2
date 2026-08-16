# Senior Progressive Growth V5 — design audit

## Problem corrected
Dynamic V4 exposed too much capacity immediately: the floor was already large, three-to-five recipes were selectable from the beginning, five or more tables were easy to install, and build money reset per level. This weakened the management loop because expansion was mostly cosmetic rather than an economic consequence of service quality.

## V5 economic model
- Persistent business cash saved in `robledo_kitchen_rush_business_v5`.
- Persistent customer satisfaction from 0–100%.
- Persistent purchased layout.
- Four expansion tiers with hard physical bounds and fixture caps.
- Menu unlocks and menu-slot limits tied to expansion tier.
- Concurrent customer and party-size limits tied to expansion tier.
- Expansion requires both cash and satisfaction.

## Service-quality model
- Complete tables generate business revenue and satisfaction.
- Fast completion is defined as 30 seconds or less from order placement to final dish delivery.
- A fast table restores one lost life, capped at three.
- Walkouts cost one life, -10% satisfaction and -$12.
- Order cards display the remaining fast-service life window.

## Starter balance
Tier 1 begins with $430, 68% satisfaction, two tables maximum, two concurrent parties, parties of at most two customers, two menu slots, and only Salad + Burger available. The recommended starter layout costs most of the initial capital, forcing players to earn revenue before expansion.

## Expansion effect
Growth is not a score-only unlock. Each expansion rebuilds the actual restaurant envelope and increases specific fixture caps. Fryer/oven and later ingredient supplies remain unavailable until the corresponding restaurant tier permits them.
