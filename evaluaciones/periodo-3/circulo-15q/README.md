# Geometry 8 - Period III - Circle Evaluation - Real Applications

Senior LaTeX assessment package for the first Period III grade after Semana Robledista.

## Final compact structure

- Version A: 15 open-response questions, 3 pages, 45 points.
- Version B: 15 open-response questions, 3 pages, 45 points.
- Version C: 15 open-response questions, 3 pages, 45 points.
- Combined student print master: 9 pages total.
- Teacher key is delivered separately and does not count toward the 9-page student master.
- All diagrams remain native TikZ/vector graphics.
- The real-application question set and 45-point weighting are preserved.

## Space-optimization strategy

The final print layout uses a compact two-column card system: four half-width questions plus one full-width question per page. This keeps five questions on each page while preserving readable prompts, diagrams and dedicated calculation lines. Students are explicitly allowed to continue calculations on the back of the sheet when additional space is needed.

## Curricular scope

The assessment remains inside the current circle block and the repository Circle Clash scope: radius, diameter, circumference/perimeter, area, and pi. It also evaluates inverse reasoning, scaling, measurement, rotations, cost estimation, comparison and error analysis. Composite/shaded-area and solid-geometry content are intentionally excluded.

## Real-application architecture

1. Bicycle wheel: identify center, radius and diameter.
2. Round cafe table: edge band and tabletop area.
3. Manhole cover: rim length and metal area.
4. Fountain: recover dimensions from measured circumference.
5. Round rug: recover dimensions from known covered area.
6. Tree trunk: diameter and cross-sectional area from circumference.
7. Circular running path: distance over several laps.
8. Pizza value: compare area per peso.
9. School garden redesign: effect of changing the radius.
10. Bicycle odometer: distance from wheel rotations.
11. Round window: frame length, glass area and cost.
12. Circular patio: paving area, purchase rounding and cost.
13. Sprinkler coverage: additional area after increasing reach.
14. Pool-cover order: diagnose a radius/diameter error and quantify the overestimate.
15. Circular plaza expansion: recover radius, expand the plaza and calculate the extra paving budget.

## Senior QA

The compact revision was compiled from LaTeX, rendered page-by-page and preflighted after final pagination. Figure geometry was checked against the stated numerical relationships. In particular:

- diameter/radius constructions pass through the exact center;
- pizza drawings remain proportional to the stated diameters in each version;
- garden redesign figures use the exact stated scale factor;
- sprinkler and plaza before/after circles remain proportional to the stated radius change;
- the patio paving grid is clipped to the circular boundary;
- the running-path radius is represented on the track centerline;
- no overfull/underfull box warnings remain in the three student LaTeX builds;
- each version compiles to exactly 3 pages;
- the combined student PDF compiles to exactly 9 pages, is openable, vector/text based and unencrypted.

Editable compact LaTeX sources are distributed with the classroom artifact package.