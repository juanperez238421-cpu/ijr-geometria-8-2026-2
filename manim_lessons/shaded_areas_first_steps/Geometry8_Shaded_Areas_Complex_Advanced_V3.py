#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas — Advanced Problems — Senior V3.

A new senior-level classroom scene based on the established shaded-area visual
language. Every worked problem is more complex than the previous 4+ version:
5–7 visible area components, mixed positive/negative pieces, circle fractions,
regular polygons, and exact-to-decimal reasoning.

Algorithm preserved for students:
SEE -> DECOMPOSE -> MARK (+/-) -> CALCULATE LOCAL AREAS ->
BUILD SUBTOTALS -> COMBINE -> CHECK.
"""

from __future__ import annotations

import math
import numpy as np
from manim import *

from Geometry8_Shaded_Areas_Class2_Complex_4Plus_V6 import (
    Geometry8ShadedAreasClass2Complex4PlusV6,
)
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import (
    DARK_GRAY,
    SHADE,
    RUN_NORMAL,
    RUN_SLOW,
    PAUSE_READ,
    PAUSE_EXPLAIN,
    PAUSE_WORK,
    PAUSE_CHALLENGE,
    PAUSE_FINAL,
)


class Geometry8ShadedAreasComplexAdvancedV3(
    Geometry8ShadedAreasClass2Complex4PlusV6
):
    """Senior V3 — five advanced shaded-area problems with full solutions."""

    # ================================================================
    # NUMERICAL QA
    # ================================================================
    def validate_math_class2(self) -> None:
        p1 = (
            14 * 7
            + ((14 + 10) * 4) / 2
            + (math.pi * 5**2) / 2
            - 2**2
            - math.pi * 1.5**2
            - (4 * 3) / 2
        )
        p2 = (
            18 * 10
            - (8 * 6) / 2
            - (6 * 4) / 2
            - math.pi * 1**2
            - (math.pi * 2**2) / 2
        )
        p3 = (
            12 * 6
            + math.pi * 3**2
            - 4**2
            - math.pi * 1**2
            - 2 * ((math.pi * 2**2) / 4)
        )
        p4 = (
            (36 * (3 * math.sqrt(3))) / 2
            - (60 / 360) * math.pi * 2**2
            - math.pi * 1**2
            - (2 * 2) / 2
            - (2 * 1.5) / 2
        )
        p5 = (
            18 * 10
            + ((18 + 12) * 4) / 2
            + (math.pi * 6**2) / 2
            - math.pi * 2**2
            - (6 * 4) / 2
            - (90 / 360) * math.pi * 3**2
            - (4 * 3) / 2
        )

        assert math.isclose(p1, 136 + 10.25 * math.pi, abs_tol=1e-12)
        assert math.isclose(p2, 144 - 3 * math.pi, abs_tol=1e-12)
        assert math.isclose(p3, 56 + 6 * math.pi, abs_tol=1e-12)
        assert math.isclose(
            p4,
            54 * math.sqrt(3) - 3.5 - 5 * math.pi / 3,
            abs_tol=1e-12,
        )
        assert math.isclose(p5, 222 + 11.75 * math.pi, abs_tol=1e-12)

        assert math.isclose(p1, 168.20132469929538, abs_tol=1e-9)
        assert math.isclose(p2, 134.57522203923062, abs_tol=1e-9)
        assert math.isclose(p3, 74.84955592153876, abs_tol=1e-9)
        assert math.isclose(p4, 84.79475585273637, abs_tol=1e-9)
        assert math.isclose(p5, 258.91371368004256, abs_tol=1e-9)

        component_counts = {
            "advanced_facade": 6,
            "advanced_parallelogram": 5,
            "advanced_stadium": 7,
            "advanced_hexagon": 5,
            "advanced_capstone": 7,
        }
        assert min(component_counts.values()) >= 5

    # ================================================================
    # SENIOR V3 INTRO
    # ================================================================
    def opening_advanced_v3(self) -> None:
        self.validate_math_class2()

        kicker = self.txt("GEOMETRY 8 · SHADED AREAS", 23, BOLD, DARK_GRAY)
        title = self.txt("ADVANCED PROBLEMS · V3", 58, BOLD)
        sub = self.txt("5–7 AREA COMPONENTS PER PROBLEM", 30, BOLD, DARK_GRAY)
        promise = self.txt(
            "More pieces. More formulas. The same disciplined method.",
            27,
        )
        route = self.txt(
            "SEE → DECOMPOSE → MARK ± → LOCAL AREAS → SUBTOTALS → CHECK",
            25,
            BOLD,
        )

        group = VGroup(kicker, title, sub, promise, route).arrange(DOWN, buff=0.25)
        self.fit(group, 14.0, 6.2)
        group.move_to(ORIGIN)

        self.play(FadeIn(kicker, shift=UP * 0.08), run_time=RUN_NORMAL)
        self.play(Write(title), run_time=RUN_SLOW)
        self.play(FadeIn(sub), FadeIn(promise), run_time=RUN_NORMAL)
        self.play(FadeIn(route), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    def advanced_contract(self) -> None:
        title = self.txt("ADVANCED V3 · COMPLEXITY MAP", 38, BOLD)
        subtitle = self.txt(
            "Every problem requires at least five separate area decisions.",
            23,
            NORMAL,
            DARK_GRAY,
        )

        rows_data = [
            ("1", "ARCHITECTURAL FACADE", "6", "3 positive + 3 negative"),
            ("2", "PARALLELOGRAM PANEL", "5", "1 positive + 4 negative"),
            ("3", "STADIUM REGION", "7", "3 positive + 4 negative"),
            ("4", "HEXAGON MOSAIC", "5", "1 positive + 4 negative"),
            ("5", "CAPSTONE CHALLENGE", "7", "3 positive + 4 negative"),
        ]

        rows = VGroup()
        for num, name, count, structure in rows_data:
            circle = Circle(
                radius=0.24,
                stroke_color=BLACK,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            )
            n = self.txt(num, 18, BOLD).move_to(circle)
            nm = self.txt(name, 21, BOLD)
            ct = self.txt(f"{count} SHAPES", 20, BOLD)
            st = self.txt(structure, 19)
            row = VGroup(VGroup(circle, n), nm, ct, st).arrange(RIGHT, buff=0.32)
            self.fit(row, 12.8, 0.58)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        formula = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=8.8,
            height=1.08,
            size=39,
        )

        group = VGroup(title, subtitle, rows, formula).arrange(DOWN, buff=0.30)
        self.fit(group, 14.0, 7.0)
        group.move_to(ORIGIN)

        self.play(FadeIn(title), FadeIn(subtitle), run_time=RUN_NORMAL)
        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.07), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ / 2)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 1 — ADVANCED FACADE
    # 3 positive pieces, 3 negative pieces
    # ================================================================
    def advanced_facade_region(self) -> VGroup:
        s = 0.255

        body = Rectangle(
            width=14 * s,
            height=7 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        hb = 7 * s
        ht = 5 * s
        trap_h = 4 * s
        roof_vertices = [
            np.array([-hb, y0, 0]),
            np.array([ hb, y0, 0]),
            np.array([ ht, y0 + trap_h, 0]),
            np.array([-ht, y0 + trap_h, 0]),
        ]
        roof = Polygon(
            *roof_vertices,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        cap_center = np.array([0, y0 + trap_h, 0])
        cap = Sector(
            radius=5 * s,
            angle=PI,
            start_angle=0,
            arc_center=cap_center,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        square = Square(
            side_length=2 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(body.get_center() + LEFT * 1.05 + DOWN * 0.28)

        circle_center = body.get_center() + RIGHT * 1.10 + DOWN * 0.30
        circle_r = 1.5 * s
        circle = Circle(
            radius=circle_r,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        tri_center = body.get_center() + UP * 0.48
        tb, th = 4 * s, 3 * s
        tri_vertices = [
            tri_center + LEFT * (tb / 2) + DOWN * (th / 2),
            tri_center + RIGHT * (tb / 2) + DOWN * (th / 2),
            tri_center + UP * (th / 2),
        ]
        triangle = Polygon(
            *tri_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        body_vertices = body.get_vertices()
        self._assert_points_in_polygon(square.get_vertices(), body_vertices, "P1 square")
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, circle_r),
            body_vertices,
            "P1 circle",
        )
        self._assert_points_in_polygon(tri_vertices, body_vertices, "P1 triangle")

        labels = VGroup(
            self.txt("14 × 7", 15, BOLD).next_to(body, DOWN, buff=0.13),
            self.txt("B=14 · b=10 · h=4", 13, BOLD).next_to(roof, RIGHT, buff=0.10),
            self.txt("semicircle · r=5", 13, BOLD).next_to(cap, UP, buff=0.09),
            self.txt("2×2", 12, BOLD).move_to(square),
            self.txt("r=1.5", 11, BOLD).move_to(circle),
            self.txt("b=4 · h=3", 11, BOLD).move_to(triangle),
        )

        return VGroup(
            VGroup(body, roof, cap),
            square,
            circle,
            triangle,
            labels,
        )

    def beat_advanced_facade(self) -> None:
        self.step(0)
        geo = self.advanced_facade_region()
        self.swap_left(geo)
        outer, square, circle, tri, _ = geo
        body, roof, cap = outer

        self.swap_right(self.reason_card(
            "PROBLEM 1 · 6 COMPONENTS",
            [
                "Build the exterior from 3 positive pieces.",
                "Remove 3 independent gaps.",
                "Do not combine until every local area is known.",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(body), Indicate(roof), Indicate(cap), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(square), Indicate(circle), Indicate(tri), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([body, roof, cap], [square, circle, tri])
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2 trapezoid", "A3 semicircle"],
            ["A4 square", "A5 circle", "A6 triangle"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(body, "A1 · RECTANGLE (+)",
                        [r"A_1=14(7)", r"A_1=98\,cm^2"], RIGHT)
        self.local_calc(roof, "A2 · TRAPEZOID (+)",
                        [r"A_2=\frac{(14+10)(4)}{2}", r"A_2=48\,cm^2"], RIGHT)
        self.local_calc(cap, "A3 · SEMICIRCLE (+)",
                        [r"A_3=\frac{\pi(5)^2}{2}", r"A_3=12.5\pi\,cm^2"], DOWN)
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL",
            r"A_{(+)}=146+12.5\pi",
            30,
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(square, "A4 · SQUARE GAP (−)",
                        [r"A_4=2^2", r"A_4=4\,cm^2"], RIGHT)
        self.local_calc(circle, "A5 · CIRCLE GAP (−)",
                        [r"A_5=\pi(1.5)^2", r"A_5=2.25\pi\,cm^2"], LEFT)
        self.local_calc(tri, "A6 · TRIANGLE GAP (−)",
                        [r"A_6=\frac{4(3)}{2}", r"A_6=6\,cm^2"], RIGHT)
        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            r"A_{(-)}=10+2.25\pi",
            30,
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=(146+12.5\pi)-(10+2.25\pi)", 27),
            self.math(r"A_s=136+10.25\pi", 31),
            self.math(r"A_s\approx168.20\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "3 positive + 3 negative terms ✓",
                "All gaps lie inside the exterior ✓",
                "π was kept exact until the final line ✓",
                "Square units ✓",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 2 — ADVANCED PARALLELOGRAM
    # 1 positive, 4 negative
    # ================================================================
    def advanced_parallelogram_region(self) -> VGroup:
        s = 0.285
        b, h, slant = 18 * s, 10 * s, 2.1 * s
        verts = [
            np.array([-b/2, -h/2, 0]),
            np.array([ b/2, -h/2, 0]),
            np.array([ b/2 + slant, h/2, 0]),
            np.array([-b/2 + slant, h/2, 0]),
        ]
        outer = Polygon(
            *verts,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        # Rhombus D=8, d=6
        D, d = 8*s, 6*s
        rc = np.array([-0.72, 0.20, 0])
        rh_verts = [
            rc + LEFT*(D/2),
            rc + UP*(d/2),
            rc + RIGHT*(D/2),
            rc + DOWN*(d/2),
        ]
        rh = Polygon(
            *rh_verts,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Triangle b=6, h=4
        tb, th = 6*s, 4*s
        tc = np.array([1.55, -0.46, 0])
        tri_verts = [
            tc + LEFT*(tb/2) + DOWN*(th/2),
            tc + RIGHT*(tb/2) + DOWN*(th/2),
            tc + UP*(th/2),
        ]
        tri = Polygon(
            *tri_verts,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Circle r=1
        cc = np.array([2.20, 0.78, 0])
        cr = 1*s
        circle = Circle(
            radius=cr,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(cc)

        # Semicircle r=2
        sc = np.array([-2.00, -0.66, 0])
        sr = 2*s
        semi = Sector(
            radius=sr,
            angle=PI,
            start_angle=0,
            arc_center=sc,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        height_x = -b/2 + slant
        hline = DashedLine(
            np.array([height_x, -h/2, 0]),
            np.array([height_x, h/2, 0]),
            color=BLACK,
            stroke_width=2,
        )

        self._assert_points_in_polygon(rh_verts, verts, "P2 rhombus")
        self._assert_points_in_polygon(tri_verts, verts, "P2 triangle")
        self._assert_points_in_polygon(self._circle_sample_points(cc, cr), verts, "P2 circle")
        self._assert_points_in_polygon(
            self._sector_sample_points(sc, sr, 0, PI),
            verts,
            "P2 semicircle",
        )

        labels = VGroup(
            self.txt("b=18", 16, BOLD).next_to(outer, DOWN, buff=0.10),
            self.txt("h=10", 16, BOLD).next_to(hline, LEFT, buff=0.07),
            self.txt("D=8 · d=6", 13, BOLD).move_to(rh),
            self.txt("b=6 · h=4", 12, BOLD).move_to(tri),
            self.txt("r=1", 11, BOLD).move_to(circle),
            self.txt("semicircle r=2", 11, BOLD).move_to(sc + UP*0.18),
        )
        return VGroup(outer, rh, tri, circle, semi, hline, labels)

    def beat_advanced_parallelogram(self) -> None:
        self.step(0)
        geo = self.advanced_parallelogram_region()
        self.swap_left(geo)
        outer, rh, tri, circle, semi, hline, _ = geo

        self.swap_right(self.reason_card(
            "PROBLEM 2 · 5 COMPONENTS",
            [
                "Whole = one parallelogram.",
                "Remove four different gaps.",
                "Height is perpendicular — never use the slanted side.",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(hline), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(
            Indicate(rh), Indicate(tri), Indicate(circle), Indicate(semi),
            run_time=RUN_NORMAL,
        )
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([outer], [rh, tri, circle, semi])
        self.swap_right(self.signed_ledger(
            ["A1 parallelogram"],
            ["A2 rhombus", "A3 triangle", "A4 circle", "A5 semicircle"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(outer, "A1 · PARALLELOGRAM (+)",
                        [r"A_1=bh", r"A_1=18(10)", r"A_1=180\,cm^2"], RIGHT)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL", r"A_{(+)}=180", 31))
        self.wait(PAUSE_WORK)

        self.local_calc(rh, "A2 · RHOMBUS GAP (−)",
                        [r"A_2=\frac{8(6)}{2}", r"A_2=24\,cm^2"], RIGHT)
        self.local_calc(tri, "A3 · TRIANGLE GAP (−)",
                        [r"A_3=\frac{6(4)}{2}", r"A_3=12\,cm^2"], LEFT)
        self.local_calc(circle, "A4 · CIRCLE GAP (−)",
                        [r"A_4=\pi(1)^2", r"A_4=\pi\,cm^2"], LEFT)
        self.local_calc(semi, "A5 · SEMICIRCLE GAP (−)",
                        [r"A_5=\frac{\pi(2)^2}{2}", r"A_5=2\pi\,cm^2"], RIGHT)

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            r"A_{(-)}=36+3\pi",
            30,
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=180-(36+3\pi)", 30),
            self.math(r"A_s=144-3\pi", 32),
            self.math(r"A_s\approx134.58\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "5 components counted exactly once ✓",
                "Perpendicular h=10 used ✓",
                "Four gaps were all subtracted ✓",
                "134.58 < 180 ✓",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 3 — ADVANCED STADIUM
    # 3 positive, 4 negative
    # ================================================================
    def advanced_stadium_region(self) -> VGroup:
        s = 0.335
        rect = Rectangle(
            width=12*s,
            height=6*s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        r = 3*s
        lcap = Sector(
            radius=r, angle=PI, start_angle=PI/2, arc_center=rect.get_left(),
            stroke_color=BLACK, stroke_width=3, fill_color=SHADE, fill_opacity=0.94,
        )
        rcap = Sector(
            radius=r, angle=PI, start_angle=-PI/2, arc_center=rect.get_right(),
            stroke_color=BLACK, stroke_width=3, fill_color=SHADE, fill_opacity=0.94,
        )

        square = Square(
            side_length=4*s,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(rect)

        circle_center = rect.get_center() + RIGHT*1.55
        circle_r = 1*s
        circle = Circle(
            radius=circle_r,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        qr = 2*s
        inset = 0.12
        q1c = rect.get_corner(UL) + RIGHT*inset + DOWN*inset
        q2c = rect.get_corner(DR) + LEFT*inset + UP*inset
        q1 = Sector(
            radius=qr, angle=PI/2, start_angle=-PI/2, arc_center=q1c,
            stroke_color=BLACK, stroke_width=2.3, fill_color=WHITE, fill_opacity=1,
        )
        q2 = Sector(
            radius=qr, angle=PI/2, start_angle=PI/2, arc_center=q2c,
            stroke_color=BLACK, stroke_width=2.3, fill_color=WHITE, fill_opacity=1,
        )

        rv = rect.get_vertices()
        self._assert_points_in_polygon(square.get_vertices(), rv, "P3 square")
        self._assert_points_in_polygon(self._circle_sample_points(circle_center, circle_r), rv, "P3 circle")
        self._assert_points_in_polygon(self._sector_sample_points(q1c, qr, -PI/2, PI/2), rv, "P3 q1")
        self._assert_points_in_polygon(self._sector_sample_points(q2c, qr, PI/2, PI/2), rv, "P3 q2")

        labels = VGroup(
            self.txt("rectangle 12×6", 16, BOLD).next_to(rect, DOWN, buff=0.11),
            self.txt("caps r=3", 15, BOLD).next_to(lcap, LEFT, buff=0.07),
            self.txt("4×4", 12, BOLD).move_to(square),
            self.txt("r=1", 11, BOLD).move_to(circle),
            self.txt("quarter gaps r=2", 13, BOLD).next_to(rect, UP, buff=0.08),
        )
        return VGroup(VGroup(rect, lcap, rcap), square, circle, q1, q2, labels)

    def beat_advanced_stadium(self) -> None:
        self.step(0)
        geo = self.advanced_stadium_region()
        self.swap_left(geo)
        outer, square, circle, q1, q2, _ = geo
        rect, lcap, rcap = outer

        self.swap_right(self.reason_card(
            "PROBLEM 3 · 7 COMPONENTS",
            [
                "Positive: rectangle + two semicircular caps.",
                "Negative: square + circle + two quarter circles.",
                "Look for equal circle fractions before arithmetic.",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(VGroup(lcap, rcap)), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(square), Indicate(circle), Indicate(VGroup(q1, q2)), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([rect, lcap, rcap], [square, circle, q1, q2])
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2-A3 semicircles"],
            ["A4 square", "A5 circle", "A6-A7 quarters"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(rect, "A1 · RECTANGLE (+)",
                        [r"A_1=12(6)", r"A_1=72\,cm^2"], RIGHT)
        self.local_calc(VGroup(lcap, rcap), "A2+A3 · TWO SEMICIRCLES (+)",
                        [r"2\left(\frac{\pi(3)^2}{2}\right)", r"=9\pi\,cm^2"], DOWN)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL", r"A_{(+)}=72+9\pi", 30))
        self.wait(PAUSE_WORK)

        self.local_calc(square, "A4 · SQUARE GAP (−)",
                        [r"A_4=4^2", r"A_4=16\,cm^2"], RIGHT)
        self.local_calc(circle, "A5 · CIRCLE GAP (−)",
                        [r"A_5=\pi(1)^2", r"A_5=\pi\,cm^2"], LEFT)
        self.local_calc(VGroup(q1, q2), "A6+A7 · TWO QUARTERS (−)",
                        [r"2\left(\frac{\pi(2)^2}{4}\right)", r"=2\pi\,cm^2"], DOWN)
        self.swap_right(self.equation_card("NEGATIVE SUBTOTAL", r"A_{(-)}=16+3\pi", 30))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=(72+9\pi)-(16+3\pi)", 28),
            self.math(r"A_s=56+6\pi", 32),
            self.math(r"A_s\approx74.85\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "7 visible pieces were accounted for ✓",
                "2 semicircles = one circle ✓",
                "2 quarters = one semicircle ✓",
                "Exact π retained before approximation ✓",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 4 — ADVANCED HEXAGON
    # 1 positive, 4 negative
    # ================================================================
    def advanced_hexagon_region(self) -> VGroup:
        s = 0.43
        side = 6*s
        hx = RegularPolygon(
            n=6,
            radius=side,
            start_angle=0,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        c = hx.get_center()
        verts = hx.get_vertices()

        sr = 2*s
        sector = Sector(
            radius=sr,
            angle=PI/3,
            start_angle=-PI/6,
            arc_center=c,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        cc = c + LEFT*1.14 + UP*0.83
        cr = 1*s
        circle = Circle(
            radius=cr,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(cc)

        tc = c + LEFT*1.05 + DOWN*0.92
        tb = th = 2*s
        tri_verts = [
            tc + LEFT*(tb/2) + DOWN*(th/2),
            tc + RIGHT*(tb/2) + DOWN*(th/2),
            tc + UP*(th/2),
        ]
        tri = Polygon(
            *tri_verts,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        D, d = 2*s, 1.5*s
        rc = c + RIGHT*1.35 + UP*0.92
        rh_verts = [
            rc + LEFT*(D/2),
            rc + UP*(d/2),
            rc + RIGHT*(D/2),
            rc + DOWN*(d/2),
        ]
        rh = Polygon(
            *rh_verts,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        apothem = DashedLine(
            c,
            c + UP*(3*math.sqrt(3)*s),
            color=BLACK,
            stroke_width=2,
        )

        self._assert_points_in_polygon(self._sector_sample_points(c, sr, -PI/6, PI/3), verts, "P4 sector")
        self._assert_points_in_polygon(self._circle_sample_points(cc, cr), verts, "P4 circle")
        self._assert_points_in_polygon(tri_verts, verts, "P4 triangle")
        self._assert_points_in_polygon(rh_verts, verts, "P4 rhombus")

        labels = VGroup(
            self.txt("regular hexagon · side=6", 16, BOLD).next_to(hx, DOWN, buff=0.10),
            self.math(r"P=36\ {\rm cm}", 22).next_to(hx, LEFT, buff=0.07),
            self.math(r"a=3\sqrt3\ {\rm cm}", 21).next_to(apothem, RIGHT, buff=0.05),
            self.txt("60° · r=2", 12, BOLD).move_to(c + RIGHT*0.55),
            self.txt("r=1", 11, BOLD).move_to(circle),
            self.txt("b=2 · h=2", 10, BOLD).move_to(tri),
            self.txt("D=2 · d=1.5", 9, BOLD).move_to(rh),
        )
        return VGroup(hx, sector, circle, tri, rh, apothem, labels)

    def beat_advanced_hexagon(self) -> None:
        self.step(0)
        geo = self.advanced_hexagon_region()
        self.swap_left(geo)
        hx, sector, circle, tri, rh, apothem, _ = geo

        self.swap_right(self.reason_card(
            "PROBLEM 4 · 5 COMPONENTS",
            [
                "Whole: regular hexagon.",
                "Remove sector + circle + triangle + rhombus.",
                "This problem mixes four formula families.",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(apothem), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(sector), Indicate(circle), Indicate(tri), Indicate(rh), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([hx], [sector, circle, tri, rh])
        self.swap_right(self.signed_ledger(
            ["A1 regular hexagon"],
            ["A2 sector", "A3 circle", "A4 triangle", "A5 rhombus"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(hx, "A1 · HEXAGON (+)",
                        [r"A_1=\frac{Pa}{2}", r"A_1=\frac{36(3\sqrt3)}{2}", r"A_1=54\sqrt3"], RIGHT)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL", r"A_{(+)}=54\sqrt3", 31))
        self.wait(PAUSE_WORK)

        self.local_calc(sector, "A2 · 60° SECTOR (−)",
                        [r"A_2=\frac{60}{360}\pi(2)^2", r"A_2=\frac{2\pi}{3}"], LEFT)
        self.local_calc(circle, "A3 · CIRCLE (−)",
                        [r"A_3=\pi(1)^2", r"A_3=\pi"], RIGHT)
        self.local_calc(tri, "A4 · TRIANGLE (−)",
                        [r"A_4=\frac{2(2)}{2}", r"A_4=2"], RIGHT)
        self.local_calc(rh, "A5 · RHOMBUS (−)",
                        [r"A_5=\frac{2(1.5)}{2}", r"A_5=1.5"], LEFT)

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            r"A_{(-)}=3.5+\frac{5\pi}{3}",
            29,
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=54\sqrt3-\left(3.5+\frac{5\pi}{3}\right)", 26),
            self.math(r"A_s=54\sqrt3-3.5-\frac{5\pi}{3}", 28),
            self.math(r"A_s\approx84.80\,cm^2", 31),
        ).arrange(DOWN, buff=0.17)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "5 components accounted for ✓",
                "Apothem is perpendicular ✓",
                "Sector fraction = 60/360 = 1/6 ✓",
                "84.80 < 54√3 ≈ 93.53 ✓",
            ],
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 5 — ADVANCED CAPSTONE
    # 3 positive, 4 negative
    # ================================================================
    def advanced_capstone_region(self) -> VGroup:
        s = 0.235

        body = Rectangle(
            width=18*s,
            height=10*s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        hb, ht, trap_h = 9*s, 6*s, 4*s
        roof_vertices = [
            np.array([-hb, y0, 0]),
            np.array([ hb, y0, 0]),
            np.array([ ht, y0 + trap_h, 0]),
            np.array([-ht, y0 + trap_h, 0]),
        ]
        roof = Polygon(
            *roof_vertices,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        cap_center = np.array([0, y0 + trap_h, 0])
        cap = Sector(
            radius=6*s,
            angle=PI,
            start_angle=0,
            arc_center=cap_center,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        cc = body.get_center() + LEFT*1.48 + UP*0.32
        cr = 2*s
        circle = Circle(
            radius=cr,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(cc)

        D, d = 6*s, 4*s
        rc = body.get_center() + UP*0.28
        rh_verts = [
            rc + LEFT*(D/2),
            rc + UP*(d/2),
            rc + RIGHT*(D/2),
            rc + DOWN*(d/2),
        ]
        rh = Polygon(
            *rh_verts,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        sc = body.get_center() + RIGHT*1.25 + DOWN*0.32
        sr = 3*s
        sector = Sector(
            radius=sr,
            angle=PI/2,
            start_angle=PI,
            arc_center=sc,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        tc = body.get_center() + RIGHT*1.58 + UP*0.63
        tb, th = 4*s, 3*s
        tri_verts = [
            tc + LEFT*(tb/2) + DOWN*(th/2),
            tc + RIGHT*(tb/2) + DOWN*(th/2),
            tc + UP*(th/2),
        ]
        tri = Polygon(
            *tri_verts,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        bv = body.get_vertices()
        self._assert_points_in_polygon(self._circle_sample_points(cc, cr), bv, "P5 circle")
        self._assert_points_in_polygon(rh_verts, bv, "P5 rhombus")
        self._assert_points_in_polygon(self._sector_sample_points(sc, sr, PI, PI/2), bv, "P5 sector")
        self._assert_points_in_polygon(tri_verts, bv, "P5 triangle")

        labels = VGroup(
            self.txt("18 × 10", 14, BOLD).next_to(body, DOWN, buff=0.12),
            self.txt("B=18 · b=12 · h=4", 12, BOLD).next_to(roof, RIGHT, buff=0.09),
            self.txt("semicircle · r=6", 12, BOLD).next_to(cap, UP, buff=0.08),
            self.txt("r=2", 10, BOLD).move_to(circle),
            self.txt("D=6 · d=4", 9, BOLD).move_to(rh),
            self.txt("90° · r=3", 9, BOLD).move_to(sc + LEFT*0.18 + DOWN*0.14),
            self.txt("b=4 · h=3", 9, BOLD).move_to(tri),
        )

        return VGroup(VGroup(body, roof, cap), circle, rh, sector, tri, labels)

    def beat_advanced_capstone(self) -> None:
        self.step(0)
        geo = self.advanced_capstone_region()
        self.swap_left(geo)
        outer, circle, rh, sector, tri, _ = geo
        body, roof, cap = outer

        self.swap_right(self.reason_card(
            "PROBLEM 5 · CAPSTONE · 7 COMPONENTS",
            [
                "Positive: rectangle + trapezoid + semicircle.",
                "Negative: circle + rhombus + sector + triangle.",
                "Separate calculation from combination.",
            ],
        ))
        self.wait(PAUSE_CHALLENGE)

        self.step(1)
        self.play(Indicate(body), Indicate(roof), Indicate(cap), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(circle), Indicate(rh), Indicate(sector), Indicate(tri), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([body, roof, cap], [circle, rh, sector, tri])
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2 trapezoid", "A3 semicircle"],
            ["A4 circle", "A5 rhombus", "A6 90° sector", "A7 triangle"],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(body, "A1 · RECTANGLE (+)",
                        [r"A_1=18(10)", r"A_1=180\,cm^2"], RIGHT)
        self.local_calc(roof, "A2 · TRAPEZOID (+)",
                        [r"A_2=\frac{(18+12)(4)}{2}", r"A_2=60\,cm^2"], RIGHT)
        self.local_calc(cap, "A3 · SEMICIRCLE (+)",
                        [r"A_3=\frac{\pi(6)^2}{2}", r"A_3=18\pi\,cm^2"], DOWN)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL", r"A_{(+)}=240+18\pi", 30))
        self.wait(PAUSE_CHALLENGE)

        self.local_calc(circle, "A4 · CIRCLE GAP (−)",
                        [r"A_4=\pi(2)^2", r"A_4=4\pi\,cm^2"], RIGHT)
        self.local_calc(rh, "A5 · RHOMBUS GAP (−)",
                        [r"A_5=\frac{6(4)}{2}", r"A_5=12\,cm^2"], LEFT)
        self.local_calc(sector, "A6 · 90° SECTOR GAP (−)",
                        [r"A_6=\frac{90}{360}\pi(3)^2", r"A_6=2.25\pi\,cm^2"], LEFT)
        self.local_calc(tri, "A7 · TRIANGLE GAP (−)",
                        [r"A_7=\frac{4(3)}{2}", r"A_7=6\,cm^2"], RIGHT)

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            r"A_{(-)}=18+6.25\pi",
            30,
        ))
        self.wait(PAUSE_CHALLENGE)

        final = VGroup(
            self.math(r"A_s=(240+18\pi)-(18+6.25\pi)", 26),
            self.math(r"A_s=222+11.75\pi", 30),
            self.math(r"A_s\approx258.91\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "FINAL CHECK",
            [
                "7 components counted exactly once ✓",
                "3 positive and 4 negative terms ✓",
                "Result is below the complete exterior area ✓",
                "Exact π → final decimal → cm² ✓",
            ],
        ))
        self.wait(PAUSE_FINAL)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    def closing_advanced_v3(self) -> None:
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=RUN_NORMAL)

        title = self.txt("ADVANCED V3 · ONE METHOD, MANY PIECES", 43, BOLD)
        formula = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=9.0,
            height=1.12,
            size=39,
        )
        steps = VGroup(
            self.txt("1. Decompose before calculating.", 24, BOLD),
            self.txt("2. Assign + or − to every area component.", 24, BOLD),
            self.txt("3. Solve each local area independently.", 24, BOLD),
            self.txt("4. Build positive and negative subtotals.", 24, BOLD),
            self.txt("5. Combine only once; approximate π at the end.", 24, BOLD),
            self.txt("6. Check magnitude, component count, and square units.", 24, BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.13)

        group = VGroup(title, formula, steps).arrange(DOWN, buff=0.24)
        self.fit(group, 13.4, 6.4)
        group.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP*0.08), run_time=RUN_SLOW)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        for line in steps:
            self.play(FadeIn(line, shift=RIGHT*0.08), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ/2)
        self.wait(PAUSE_FINAL)

    # ================================================================
    # FULL TOTAL SCENE
    # ================================================================
    def construct(self) -> None:
        self.validate_math_class2()
        self.opening_advanced_v3()
        self.formula_atlas()
        self.advanced_contract()
        self.build_workbench_class2()

        self._qa_problem = "advanced_facade"
        self.beat_advanced_facade()

        self._qa_problem = "advanced_parallelogram"
        self.beat_advanced_parallelogram()

        self._qa_problem = "advanced_stadium"
        self.beat_advanced_stadium()

        self._qa_problem = "advanced_hexagon"
        self.beat_advanced_hexagon()

        self._qa_problem = "advanced_capstone"
        self.beat_advanced_capstone()

        self._qa_problem = ""
        self.closing_advanced_v3()


# Preview:
# manim -pql Geometry8_Shaded_Areas_Complex_Advanced_V3.py \
#   Geometry8ShadedAreasComplexAdvancedV3 --disable_caching
#
# Final:
# manim -pqh Geometry8_Shaded_Areas_Complex_Advanced_V3.py \
#   Geometry8ShadedAreasComplexAdvancedV3 --disable_caching
