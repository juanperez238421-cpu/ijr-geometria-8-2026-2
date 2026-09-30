#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas II — Complex 4+ Components — V6.

Purpose
-------
Production classroom scene for complex shaded-area problems in which EVERY
worked problem contains at least four geometric area components.

Pedagogical algorithm
---------------------
SEE -> DECOMPOSE -> MARK (+/-) -> CALCULATE LOCAL AREAS ->
BUILD SUBTOTALS -> COMBINE -> CHECK.

This version preserves the proven V5 camera/layout/QA architecture and upgrades
the two problems that previously had fewer than four components:
- Problem 2: parallelogram - rhombus - triangle - circle (4 components).
- Problem 4: hexagon - sector - circle - triangle (4 components).

All five worked problems now contain 4, 4, 6, 4, and 6 visible area components.
"""

from __future__ import annotations

import math
import numpy as np
from manim import *

from Geometry8_Shaded_Areas_Class2_Complex_Opus55_V5_FINAL import (
    Geometry8ShadedAreasClass2ComplexOpus55V5Final,
)
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import (
    DARK_GRAY,
    SHADE,
    RUN_QUICK,
    RUN_NORMAL,
    RUN_SLOW,
    PAUSE_READ,
    PAUSE_EXPLAIN,
    PAUSE_WORK,
    PAUSE_CHALLENGE,
    PAUSE_FINAL,
)


class Geometry8ShadedAreasClass2Complex4PlusV6(
    Geometry8ShadedAreasClass2ComplexOpus55V5Final
):
    """Full total solution scene: five complex problems, each with 4+ shapes."""

    # ==================================================================
    # MATHEMATICAL QA — values displayed in THIS version only
    # ==================================================================
    def validate_math_class2(self) -> None:
        facade = 12 * 6 + ((12 + 8) * 4) / 2 - 2**2 - (math.pi * 2**2) / 2

        parallelogram = (
            16 * 9
            - (8 * 6) / 2
            - (6 * 4) / 2
            - math.pi * 1**2
        )

        stadium = (
            10 * 6
            + math.pi * 3**2
            - 4**2
            - 2 * ((math.pi * 2**2) / 4)
        )

        hexagon = (
            (36 * (3 * math.sqrt(3))) / 2
            - (60 / 360) * math.pi * 2**2
            - math.pi * 1**2
            - (2 * 2) / 2
        )

        capstone = (
            16 * 10
            + ((16 + 10) * 4) / 2
            + (math.pi * 5**2) / 2
            - math.pi * 2**2
            - (6 * 4) / 2
            - (90 / 360) * math.pi * 3**2
        )

        assert math.isclose(facade, 108 - 2 * math.pi, abs_tol=1e-12)
        assert math.isclose(parallelogram, 108 - math.pi, abs_tol=1e-12)
        assert math.isclose(stadium, 44 + 7 * math.pi, abs_tol=1e-12)
        assert math.isclose(
            hexagon,
            54 * math.sqrt(3) - 2 - 5 * math.pi / 3,
            abs_tol=1e-12,
        )
        assert math.isclose(capstone, 200 + 6.25 * math.pi, abs_tol=1e-12)

        assert math.isclose(facade, 101.7168146928204, abs_tol=1e-9)
        assert math.isclose(parallelogram, 104.8584073464102, abs_tol=1e-9)
        assert math.isclose(stadium, 65.99114857512855, abs_tol=1e-9)
        assert math.isclose(hexagon, 86.29475585273637, abs_tol=1e-9)
        assert math.isclose(capstone, 219.6349540849362, abs_tol=1e-9)

        # Explicit complexity contract.
        component_counts = {
            "facade": 4,
            "parallelogram": 4,
            "stadium": 6,
            "hexagon": 4,
            "capstone": 6,
        }
        assert min(component_counts.values()) >= 4

    # ==================================================================
    # INTRODUCTION — make the 4+ requirement explicit for students
    # ==================================================================
    def complexity_contract(self) -> None:
        title = self.txt("TODAY: EVERY PROBLEM HAS AT LEAST 4 SHAPES", 40, BOLD)
        subtitle = self.txt(
            "The number of pieces increases. The method stays the same.",
            24,
            NORMAL,
            DARK_GRAY,
        )

        data = [
            ("1", "FACADE", "4", "rectangle + trapezoid - square - semicircle"),
            ("2", "PARALLELOGRAM", "4", "parallelogram - rhombus - triangle - circle"),
            ("3", "STADIUM", "6", "rectangle + 2 semicircles - square - 2 quarters"),
            ("4", "HEXAGON", "4", "hexagon - sector - circle - triangle"),
            ("5", "CAPSTONE", "6", "3 positive pieces - 3 negative pieces"),
        ]

        rows = VGroup()
        for number, name, count, description in data:
            badge = Circle(
                radius=0.25,
                stroke_color=BLACK,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            )
            n = self.txt(number, 19, BOLD).move_to(badge)
            name_mob = self.txt(name, 22, BOLD)
            count_mob = self.txt(f"{count} SHAPES", 21, BOLD)
            desc = self.txt(description, 20)
            self.fit(desc, 7.7, 0.48)

            row = VGroup(VGroup(badge, n), name_mob, count_mob, desc)
            row.arrange(RIGHT, buff=0.28)
            self.fit(row, 13.4, 0.62)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        master = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=8.8,
            height=1.10,
            size=40,
        )

        group = VGroup(title, subtitle, rows, master).arrange(DOWN, buff=0.30)
        self.fit(group, 14.2, 7.2)
        group.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=RUN_SLOW)
        self.play(FadeIn(subtitle), run_time=RUN_NORMAL)
        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.08), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ / 2)
        self.play(FadeIn(master), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    # ==================================================================
    # PROBLEM 2 — 4 COMPONENTS
    # parallelogram - rhombus - triangle - circle
    # ==================================================================
    def parallelogram_region(self) -> VGroup:
        s = 0.31
        b, h, slant = 16 * s, 9 * s, 2 * s

        outer_vertices = [
            np.array([-b / 2, -h / 2, 0]),
            np.array([ b / 2, -h / 2, 0]),
            np.array([ b / 2 + slant, h / 2, 0]),
            np.array([-b / 2 + slant, h / 2, 0]),
        ]
        outer = Polygon(
            *outer_vertices,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        # Gap 1: rhombus, D=8, d=6.
        D, d = 8 * s, 6 * s
        rc = np.array([-0.45, 0.02, 0])
        rhombus_vertices = [
            rc + LEFT * (D / 2),
            rc + UP * (d / 2),
            rc + RIGHT * (D / 2),
            rc + DOWN * (d / 2),
        ]
        rhombus = Polygon(
            *rhombus_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Gap 2: triangle, b=6, h=4.
        tb, th = 6 * s, 4 * s
        tc = np.array([1.55, -0.18, 0])
        triangle_vertices = [
            tc + LEFT * (tb / 2) + DOWN * (th / 2),
            tc + RIGHT * (tb / 2) + DOWN * (th / 2),
            tc + UP * (th / 2),
        ]
        triangle = Polygon(
            *triangle_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Gap 3: circle, r=1. It is intentionally separated from the other
        # gaps so the decomposition remains visually unambiguous.
        circle_center = np.array([1.90, 0.86, 0])
        circle_radius = 1 * s
        circle = Circle(
            radius=circle_radius,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        # True perpendicular altitude of the parallelogram.
        height_x = -b / 2 + slant
        height_line = DashedLine(
            np.array([height_x, -h / 2, 0]),
            np.array([height_x,  h / 2, 0]),
            color=BLACK,
            stroke_width=2,
        )

        # Geometry-integrity QA.
        self._assert_points_in_polygon(rhombus_vertices, outer_vertices, "P2 rhombus")
        self._assert_points_in_polygon(triangle_vertices, outer_vertices, "P2 triangle")
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, circle_radius),
            outer_vertices,
            "P2 circle",
        )
        assert circle.get_bottom()[1] > triangle.get_top()[1] + 0.03

        labels = VGroup(
            self.txt("b=16 cm", 18, BOLD).next_to(outer, DOWN, buff=0.12),
            self.txt("h=9 cm", 18, BOLD).next_to(height_line, LEFT, buff=0.08),
            self.txt("D=8 · d=6", 15, BOLD).move_to(rhombus),
            self.txt("b=6 · h=4", 14, BOLD).move_to(triangle),
            self.txt("r=1", 13, BOLD).move_to(circle),
        )

        return VGroup(outer, rhombus, triangle, circle, height_line, labels)

    def beat_parallelogram_v6(self) -> None:
        self.step(0)
        geo = self.parallelogram_region()
        self.swap_left(geo)
        outer, rh, tri, circle, hline, _ = geo

        self.swap_right(self.reason_card(
            "EXAMPLE 2 · FOUR COMPONENTS",
            [
                "Whole: parallelogram.",
                "Remove: rhombus + triangle + circle.",
                "Four shapes = four local area calculations.",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(hline), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(
            Indicate(rh),
            Indicate(tri),
            Indicate(circle),
            run_time=RUN_NORMAL,
        )
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([outer], [rh, tri, circle])
        self.swap_right(self.signed_ledger(
            ["A1 parallelogram"],
            ["A2 rhombus", "A3 triangle", "A4 circle"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(
            outer,
            "A1 · PARALLELOGRAM (+)",
            [r"A_1=bh", r"A_1=16(9)", r"A_1=144\,cm^2"],
            RIGHT,
        )
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL",
            r"A_{(+)}=144\,cm^2",
            31,
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(
            rh,
            "A2 · RHOMBUS GAP (−)",
            [r"A_2=\frac{Dd}{2}", r"A_2=\frac{8(6)}{2}", r"A_2=24\,cm^2"],
            RIGHT,
        )
        self.local_calc(
            tri,
            "A3 · TRIANGLE GAP (−)",
            [r"A_3=\frac{bh}{2}", r"A_3=\frac{6(4)}{2}", r"A_3=12\,cm^2"],
            LEFT,
        )
        self.local_calc(
            circle,
            "A4 · CIRCLE GAP (−)",
            [r"A_4=\pi r^2", r"A_4=\pi(1)^2", r"A_4=\pi\,cm^2"],
            LEFT,
        )

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            r"A_{(-)}=24+12+\pi=36+\pi",
            30,
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=A_{(+)}-A_{(-)}", 29),
            self.math(r"A_s=144-(36+\pi)", 31),
            self.math(r"A_s=108-\pi", 33),
            self.math(r"A_s\approx104.86\,cm^2", 32),
        ).arrange(DOWN, buff=0.17)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "Exactly 4 components accounted for ✓",
                "Perpendicular height used for the parallelogram ✓",
                "Every gap subtracted exactly once ✓",
                "104.86 < 144 and units are cm² ✓",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ==================================================================
    # PROBLEM 4 — 4 COMPONENTS
    # regular hexagon - 60° sector - circle - triangle
    # ==================================================================
    def hexagon_sector_region(self) -> VGroup:
        s = 0.43
        side = 6 * s

        hexagon = RegularPolygon(
            n=6,
            radius=side,
            start_angle=0,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        center = hexagon.get_center()

        # Gap 1: 60° sector, r=2, pointing to the right.
        sector_radius = 2 * s
        sector_start = -PI / 6
        sector_angle = PI / 3
        sector = Sector(
            radius=sector_radius,
            angle=sector_angle,
            start_angle=sector_start,
            arc_center=center,
            stroke_color=BLACK,
            stroke_width=2.5,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Gap 2: circle r=1 in the upper-left portion.
        circle_center = center + LEFT * 1.15 + UP * 0.82
        circle_radius = 1 * s
        circle = Circle(
            radius=circle_radius,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        # Gap 3: triangle b=2, h=2 in the lower-left portion.
        tri_center = center + LEFT * 1.00 + DOWN * 0.92
        tb, th = 2 * s, 2 * s
        triangle_vertices = [
            tri_center + LEFT * (tb / 2) + DOWN * (th / 2),
            tri_center + RIGHT * (tb / 2) + DOWN * (th / 2),
            tri_center + UP * (th / 2),
        ]
        triangle = Polygon(
            *triangle_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Apothem used to compute the whole regular hexagon.
        apothem_length = 3 * math.sqrt(3) * s
        apothem = DashedLine(
            center,
            center + UP * apothem_length,
            color=BLACK,
            stroke_width=2,
        )

        vertices = hexagon.get_vertices()
        self._assert_points_in_polygon(
            self._sector_sample_points(
                center,
                sector_radius,
                sector_start,
                sector_angle,
            ),
            vertices,
            "P4 sector",
        )
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, circle_radius),
            vertices,
            "P4 circle",
        )
        self._assert_points_in_polygon(
            triangle_vertices,
            vertices,
            "P4 triangle",
        )

        # Separation checks prevent accidental overlap between independent gaps.
        assert circle.get_bottom()[1] > triangle.get_top()[1] + 0.20
        assert circle.get_right()[0] < center[0] - 0.45
        assert triangle.get_right()[0] < center[0] - 0.45

        labels = VGroup(
            self.txt("regular hexagon · side=6", 17, BOLD).next_to(
                hexagon, DOWN, buff=0.12
            ),
            self.math(r"P=36\ {m cm}", 23).next_to(
                hexagon, LEFT, buff=0.08
            ),
            self.math(r"a=3\sqrt3\ {m cm}", 22).next_to(
                apothem, RIGHT, buff=0.06
            ),
            self.txt("60° · r=2", 13, BOLD).move_to(center + RIGHT * 0.55),
            self.txt("r=1", 12, BOLD).move_to(circle),
            self.txt("b=2 · h=2", 11, BOLD).move_to(triangle),
        )

        return VGroup(hexagon, sector, circle, triangle, apothem, labels)

    def beat_hexagon_v6(self) -> None:
        self.step(0)
        geo = self.hexagon_sector_region()
        self.swap_left(geo)
        hx, sector, circle, tri, apothem, _ = geo

        self.swap_right(self.reason_card(
            "EXAMPLE 4 · FOUR COMPONENTS",
            [
                "Whole: regular hexagon.",
                "Remove: 60° sector + circle + triangle.",
                "Use four different area decisions, then one subtraction.",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(apothem), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(
            Indicate(sector),
            Indicate(circle),
            Indicate(tri),
            run_time=RUN_NORMAL,
        )
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([hx], [sector, circle, tri])
        self.swap_right(self.signed_ledger(
            ["A1 regular hexagon"],
            ["A2 60° sector", "A3 circle", "A4 triangle"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(
            hx,
            "A1 · HEXAGON (+)",
            [
                r"A_1=\frac{Pa}{2}",
                r"A_1=\frac{36(3\sqrt3)}{2}",
                r"A_1=54\sqrt3\,cm^2",
            ],
            RIGHT,
        )
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL",
            r"A_{(+)}=54\sqrt3\,cm^2",
            31,
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(
            sector,
            "A2 · 60° SECTOR (−)",
            [
                r"A_2=\frac{60}{360}\pi(2)^2",
                r"A_2=\frac{2\pi}{3}\,cm^2",
            ],
            LEFT,
        )
        self.local_calc(
            circle,
            "A3 · CIRCLE GAP (−)",
            [r"A_3=\pi(1)^2", r"A_3=\pi\,cm^2"],
            RIGHT,
        )
        self.local_calc(
            tri,
            "A4 · TRIANGLE GAP (−)",
            [
                r"A_4=\frac{bh}{2}",
                r"A_4=\frac{2(2)}{2}",
                r"A_4=2\,cm^2",
            ],
            RIGHT,
        )

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            r"A_{(-)}=\frac{2\pi}{3}+\pi+2=2+\frac{5\pi}{3}",
            28,
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=A_{(+)}-A_{(-)}", 29),
            self.math(r"A_s=54\sqrt3-\left(2+\frac{5\pi}{3}\right)", 28),
            self.math(r"A_s=54\sqrt3-2-\frac{5\pi}{3}", 29),
            self.math(r"A_s\approx86.29\,cm^2", 31),
        ).arrange(DOWN, buff=0.16)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "Exactly 4 components accounted for ✓",
                "60/360 = 1/6 for the sector ✓",
                "Exact radical and π kept until the final line ✓",
                "86.29 < 54√3 ≈ 93.53 and units are cm² ✓",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ==================================================================
    # FINAL ASSEMBLY — FULL TOTAL SCENE
    # ==================================================================
    def construct(self) -> None:
        self.validate_math_class2()

        self.opening_class2()
        self.formula_atlas()
        self.complexity_contract()
        self.build_workbench_class2()

        self._qa_problem = "facade"
        self.beat_facade_v3()

        self._qa_problem = "parallelogram_4plus"
        self.beat_parallelogram_v6()

        self._qa_problem = "stadium"
        self.beat_stadium_v3()

        self._qa_problem = "hexagon_4plus"
        self.beat_hexagon_v6()

        self._qa_problem = "capstone"
        self.beat_capstone_v3()

        self._qa_problem = ""
        self.closing_v4()


# Preview:
# manim -pql Geometry8_Shaded_Areas_Class2_Complex_4Plus_V6.py \
#   Geometry8ShadedAreasClass2Complex4PlusV6 --disable_caching
#
# Final:
# manim -pqh Geometry8_Shaded_Areas_Class2_Complex_4Plus_V6.py \
#   Geometry8ShadedAreasClass2Complex4PlusV6 --disable_caching
