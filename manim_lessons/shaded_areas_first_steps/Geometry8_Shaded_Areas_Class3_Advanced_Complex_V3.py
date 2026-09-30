#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas III — Advanced Complex Figures — Senior V3.

This lesson is a deliberate escalation from the previous complex-areas class.
Every worked problem now contains 6–9 area components and mixes several formula
families in one figure.

Senior reasoning spine
----------------------
SEE -> DECOMPOSE -> MARK (+/-) -> CALCULATE EACH LOCAL AREA ->
BUILD POSITIVE / NEGATIVE SUBTOTALS -> COMBINE -> VERIFY.

The goal is not to make the algebra obscure. The goal is to make the geometric
decomposition richer while preserving a rigorous, repeatable method.
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


class Geometry8ShadedAreasClass3AdvancedComplexV3(
    Geometry8ShadedAreasClass2Complex4PlusV6
):
    """Senior V3 — five advanced shaded-area problems with 6–9 components."""

    # ------------------------------------------------------------------
    # Mathematical QA
    # ------------------------------------------------------------------
    def validate_math_class2(self) -> None:
        p1 = (
            18 * 10
            + ((18 + 12) * 4) / 2
            + (math.pi * 6**2) / 2
            - 4 * 6
            - 2 * math.pi * 1.5**2
        )
        p2 = (
            14 * 8
            + math.pi * 4**2
            - 6 * 3
            - 2 * math.pi * 1**2
            - 2 * ((math.pi * 2**2) / 4)
        )
        p3 = (
            (48 * (4 * math.sqrt(3))) / 2
            - math.pi * 2**2
            - (90 / 360) * math.pi * 3**2
            - (4 * 3) / 2
            - (4 * 3) / 2
            - 3 * 2
        )
        p4 = (
            16 * 8
            + 2 * ((math.pi * 4**2) / 2)
            + ((16 + 10) * 4) / 2
            - math.pi * 2**2
            - (6 * 4) / 2
            - (6 * 3) / 2
            - (120 / 360) * math.pi * 3**2
        )
        p5 = (
            20 * 12
            + ((20 + 14) * 5) / 2
            + (math.pi * 7**2) / 2
            - math.pi * 2**2
            - 3**2
            - (6 * 4) / 2
            - (90 / 360) * math.pi * 3**2
            - 2 * math.pi * 1**2
        )

        assert math.isclose(p1, 216 + 13.5 * math.pi, abs_tol=1e-12)
        assert math.isclose(p2, 94 + 12 * math.pi, abs_tol=1e-12)
        assert math.isclose(
            p3,
            96 * math.sqrt(3) - 18 - 25 * math.pi / 4,
            abs_tol=1e-12,
        )
        assert math.isclose(p4, 159 + 9 * math.pi, abs_tol=1e-12)
        assert math.isclose(p5, 304 + 65 * math.pi / 4, abs_tol=1e-12)

        assert math.isclose(p1, 258.41150082346223, abs_tol=1e-9)
        assert math.isclose(p2, 131.6991118430775, abs_tol=1e-9)
        assert math.isclose(p3, 128.64192344167603, abs_tol=1e-9)
        assert math.isclose(p4, 187.27433388230813, abs_tol=1e-9)
        assert math.isclose(p5, 355.05088062083416, abs_tol=1e-9)

        component_counts = {
            "advanced_facade": 6,
            "bridge_plate": 8,
            "hexagon_plaza": 6,
            "roofed_stadium": 8,
            "capstone_emblem": 9,
        }
        assert min(component_counts.values()) >= 6

    # ------------------------------------------------------------------
    # Opening and class map
    # ------------------------------------------------------------------
    def opening_class3(self) -> None:
        kicker = self.txt("GEOMETRY 8 · PERIOD III · CLASS 3", 24, BOLD, DARK_GRAY)
        title = self.txt("SHADED AREAS III", 62, BOLD)
        sub = self.txt("ADVANCED COMPOSITE FIGURES", 32, BOLD, DARK_GRAY)
        promise = self.txt(
            "6–9 components per problem · one rigorous decomposition method",
            26,
        )
        route = self.txt(
            "SEE → DECOMPOSE → MARK ± → LOCAL AREAS → SUBTOTALS → CHECK",
            25,
            BOLD,
        )
        group = VGroup(kicker, title, sub, promise, route).arrange(DOWN, buff=0.25)
        self.fit(group, 14.2, 6.2)
        group.move_to(UP * 0.05)

        self.play(FadeIn(kicker, shift=UP * 0.08), run_time=RUN_NORMAL)
        self.play(Write(title), run_time=RUN_SLOW)
        self.play(FadeIn(sub), FadeIn(promise), run_time=RUN_NORMAL)
        self.play(FadeIn(route), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    def advanced_contract(self) -> None:
        title = self.txt("THE FIGURES ARE HARDER — THE METHOD IS NOT", 39, BOLD)
        subtitle = self.txt(
            "Count every visible area component before calculating.",
            24,
            NORMAL,
            DARK_GRAY,
        )

        data = [
            ("1", "ADVANCED FACADE", "6", "3 added pieces · 3 removed pieces"),
            ("2", "BRIDGE PLATE", "8", "stadium outside · 5 independent gaps"),
            ("3", "HEXAGON PLAZA", "6", "regular polygon · 5 mixed cut-outs"),
            ("4", "ROOFED STADIUM", "8", "4 positive pieces · 4 negative pieces"),
            ("5", "CAPSTONE EMBLEM", "9", "3 positive pieces · 6 negative pieces"),
        ]

        rows = VGroup()
        for number, name, count, description in data:
            badge = Circle(
                radius=0.24,
                stroke_color=BLACK,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            )
            n = self.txt(number, 18, BOLD).move_to(badge)
            nm = self.txt(name, 20, BOLD)
            ct = self.txt(f"{count} COMPONENTS", 19, BOLD)
            ds = self.txt(description, 19)
            self.fit(ds, 7.2, 0.45)
            row = VGroup(VGroup(badge, n), nm, ct, ds).arrange(RIGHT, buff=0.26)
            self.fit(row, 13.4, 0.60)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.19)
        master = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=8.8,
            height=1.10,
            size=39,
        )
        note = self.txt(
            "Rule: no arithmetic until every component has a sign.",
            22,
            BOLD,
            DARK_GRAY,
        )

        group = VGroup(title, subtitle, rows, master, note).arrange(DOWN, buff=0.26)
        self.fit(group, 14.2, 7.3)
        group.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.06), run_time=RUN_SLOW)
        self.play(FadeIn(subtitle), run_time=RUN_NORMAL)
        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.06), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ / 2)
        self.play(FadeIn(master), FadeIn(note), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    def build_workbench_class3(self) -> None:
        super().build_workbench_class2()
        old = self.chrome[1]
        new = self.txt("SHADED AREAS III · ADVANCED COMPLEX FIGURES", 32, BOLD)
        new.move_to(old).align_to(old, LEFT)
        old.become(new)

    # ------------------------------------------------------------------
    # Generic senior solution engine
    # ------------------------------------------------------------------
    def solve_advanced_problem(
        self,
        geometry,
        positives,
        negatives,
        intro_title,
        intro_lines,
        positive_subtotal,
        negative_subtotal,
        final_lines,
        checks,
    ) -> None:
        self.step(0)
        self.swap_left(geometry)

        self.swap_right(self.reason_card(intro_title, intro_lines))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        positive_mobs = [row[0] for row in positives]
        negative_mobs = [row[0] for row in negatives]
        self.play(
            *[Indicate(mob, scale_factor=1.02) for mob in positive_mobs],
            run_time=RUN_NORMAL,
        )
        self.wait(PAUSE_READ)
        self.play(
            *[Indicate(mob, scale_factor=1.04) for mob in negative_mobs],
            run_time=RUN_NORMAL,
        )
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed(positive_mobs, negative_mobs)
        self.swap_right(self.signed_ledger(
            [row[1] for row in positives],
            [row[1] for row in negatives],
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        for mob, _, calc_title, equations, side in positives:
            self.local_calc(mob, calc_title, equations, side)

        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL",
            positive_subtotal,
            29,
        ))
        self.wait(PAUSE_WORK)

        for mob, _, calc_title, equations, side in negatives:
            self.local_calc(mob, calc_title, equations, side)

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL",
            negative_subtotal,
            28,
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(*[self.math(eq, size) for eq, size in final_lines]).arrange(
            DOWN,
            buff=0.16,
        )
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card("FINAL CHECK", checks))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ==================================================================
    # PROBLEM 1 — ADVANCED FACADE · 6 COMPONENTS
    # ==================================================================
    def advanced_facade_region(self):
        s = 0.22

        body = Rectangle(
            width=18 * s,
            height=10 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        roof = Polygon(
            np.array([-9 * s, y0, 0]),
            np.array([ 9 * s, y0, 0]),
            np.array([ 6 * s, y0 + 4 * s, 0]),
            np.array([-6 * s, y0 + 4 * s, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        cap_center = np.array([0, y0 + 4 * s, 0])
        cap = Sector(
            radius=6 * s,
            angle=PI,
            start_angle=0,
            arc_center=cap_center,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        door = Rectangle(
            width=4 * s,
            height=6 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(body.get_bottom() + UP * (3 * s))

        c1_center = body.get_center() + LEFT * 1.28 + UP * 0.46
        c2_center = body.get_center() + RIGHT * 1.28 + UP * 0.46
        window_r = 1.5 * s
        c1 = Circle(
            radius=window_r,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(c1_center)
        c2 = c1.copy().move_to(c2_center)

        body_vertices = body.get_vertices()
        self._assert_points_in_polygon(door.get_vertices(), body_vertices, "P1 door")
        self._assert_points_in_polygon(
            self._circle_sample_points(c1_center, window_r),
            body_vertices,
            "P1 left window",
        )
        self._assert_points_in_polygon(
            self._circle_sample_points(c2_center, window_r),
            body_vertices,
            "P1 right window",
        )

        labels = VGroup(
            self.txt("18 × 10", 16, BOLD).next_to(body, DOWN, buff=0.12),
            self.txt("B=18 · b=12 · h=4", 14, BOLD).next_to(roof, RIGHT, buff=0.10),
            self.txt("semicircle · r=6", 14, BOLD).next_to(cap, UP, buff=0.08),
            self.txt("door 4×6", 12, BOLD).move_to(door),
            self.txt("r=1.5", 11, BOLD).move_to(c1),
            self.txt("r=1.5", 11, BOLD).move_to(c2),
        )

        return VGroup(VGroup(body, roof, cap), door, c1, c2, labels), body, roof, cap, door, c1, c2

    def beat_advanced_facade(self) -> None:
        geo, body, roof, cap, door, c1, c2 = self.advanced_facade_region()

        positives = [
            (body, "A1 rectangle", "A1 · RECTANGLE (+)",
             [r"A_1=18(10)", r"A_1=180\,cm^2"], RIGHT),
            (roof, "A2 trapezoid", "A2 · TRAPEZOID (+)",
             [r"A_2=\frac{(18+12)(4)}{2}", r"A_2=60\,cm^2"], RIGHT),
            (cap, "A3 semicircle", "A3 · SEMICIRCLE (+)",
             [r"A_3=\frac{\pi(6)^2}{2}", r"A_3=18\pi\,cm^2"], DOWN),
        ]
        negatives = [
            (door, "A4 door rectangle", "A4 · DOOR (−)",
             [r"A_4=4(6)", r"A_4=24\,cm^2"], RIGHT),
            (c1, "A5 circle window", "A5 · LEFT CIRCLE (−)",
             [r"A_5=\pi(1.5)^2", r"A_5=2.25\pi\,cm^2"], RIGHT),
            (c2, "A6 circle window", "A6 · RIGHT CIRCLE (−)",
             [r"A_6=\pi(1.5)^2", r"A_6=2.25\pi\,cm^2"], LEFT),
        ]

        self.solve_advanced_problem(
            geo,
            positives,
            negatives,
            "PROBLEM 1 · ADVANCED FACADE",
            [
                "Build the outside from 3 positive pieces.",
                "Remove a door and 2 circular windows.",
                "Six components must appear in the ledger.",
            ],
            r"A_{(+)}=180+60+18\pi=240+18\pi",
            r"A_{(-)}=24+2.25\pi+2.25\pi=24+4.5\pi",
            [
                (r"A_s=(240+18\pi)-(24+4.5\pi)", 27),
                (r"A_s=216+13.5\pi", 31),
                (r"A_s\approx258.41\,cm^2", 31),
            ],
            [
                "3 positive + 3 negative components ✓",
                "Both equal windows counted separately ✓",
                "Exact π retained before approximation ✓",
                "Result is smaller than the complete outside ✓",
            ],
        )

    # ==================================================================
    # PROBLEM 2 — BRIDGE PLATE · 8 COMPONENTS
    # ==================================================================
    def bridge_plate_region(self):
        s = 0.27

        rect = Rectangle(
            width=14 * s,
            height=8 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        rcap = 4 * s
        left_cap = Sector(
            radius=rcap,
            angle=PI,
            start_angle=PI / 2,
            arc_center=rect.get_left(),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        right_cap = Sector(
            radius=rcap,
            angle=PI,
            start_angle=-PI / 2,
            arc_center=rect.get_right(),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        center_gap = Rectangle(
            width=6 * s,
            height=3 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(rect)

        circle_r = 1 * s
        lc_center = rect.get_center() + LEFT * 1.20
        rc_center = rect.get_center() + RIGHT * 1.20
        lc = Circle(
            radius=circle_r,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(lc_center + DOWN * 0.04)
        rc = lc.copy().move_to(rc_center + UP * 0.04)

        rq = 2 * s
        inset = 0.10
        q1_center = rect.get_corner(UL) + RIGHT * inset + DOWN * inset
        q2_center = rect.get_corner(DR) + LEFT * inset + UP * inset
        q1 = Sector(
            radius=rq,
            angle=PI / 2,
            start_angle=-PI / 2,
            arc_center=q1_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        q2 = Sector(
            radius=rq,
            angle=PI / 2,
            start_angle=PI / 2,
            arc_center=q2_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        rv = rect.get_vertices()
        self._assert_points_in_polygon(center_gap.get_vertices(), rv, "P2 central rectangle")
        self._assert_points_in_polygon(
            self._circle_sample_points(lc.get_center(), circle_r), rv, "P2 left circle"
        )
        self._assert_points_in_polygon(
            self._circle_sample_points(rc.get_center(), circle_r), rv, "P2 right circle"
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(q1_center, rq, -PI / 2, PI / 2), rv, "P2 quarter 1"
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(q2_center, rq, PI / 2, PI / 2), rv, "P2 quarter 2"
        )

        labels = VGroup(
            self.txt("rectangle 14×8", 15, BOLD).next_to(rect, DOWN, buff=0.10),
            self.txt("side caps r=4", 14, BOLD).next_to(left_cap, LEFT, buff=0.06),
            self.txt("6×3", 12, BOLD).move_to(center_gap),
            self.txt("r=1", 10, BOLD).move_to(lc),
            self.txt("r=1", 10, BOLD).move_to(rc),
            self.txt("quarter r=2", 10, BOLD).move_to(q1.get_center()),
            self.txt("quarter r=2", 10, BOLD).move_to(q2.get_center()),
        )

        geo = VGroup(VGroup(rect, left_cap, right_cap), center_gap, lc, rc, q1, q2, labels)
        return geo, rect, left_cap, right_cap, center_gap, lc, rc, q1, q2

    def beat_bridge_plate(self) -> None:
        geo, rect, lcap, rcap, gap, lc, rc, q1, q2 = self.bridge_plate_region()

        positives = [
            (rect, "A1 rectangle", "A1 · RECTANGLE (+)",
             [r"A_1=14(8)", r"A_1=112\,cm^2"], RIGHT),
            (lcap, "A2 left semicircle", "A2 · LEFT SEMICIRCLE (+)",
             [r"A_2=\frac{\pi(4)^2}{2}", r"A_2=8\pi\,cm^2"], RIGHT),
            (rcap, "A3 right semicircle", "A3 · RIGHT SEMICIRCLE (+)",
             [r"A_3=\frac{\pi(4)^2}{2}", r"A_3=8\pi\,cm^2"], LEFT),
        ]
        negatives = [
            (gap, "A4 central rectangle", "A4 · CENTRAL GAP (−)",
             [r"A_4=6(3)", r"A_4=18\,cm^2"], RIGHT),
            (lc, "A5 left circle", "A5 · LEFT CIRCLE (−)",
             [r"A_5=\pi(1)^2", r"A_5=\pi\,cm^2"], RIGHT),
            (rc, "A6 right circle", "A6 · RIGHT CIRCLE (−)",
             [r"A_6=\pi(1)^2", r"A_6=\pi\,cm^2"], LEFT),
            (q1, "A7 quarter circle", "A7 · QUARTER 1 (−)",
             [r"A_7=\frac{\pi(2)^2}{4}", r"A_7=\pi\,cm^2"], RIGHT),
            (q2, "A8 quarter circle", "A8 · QUARTER 2 (−)",
             [r"A_8=\frac{\pi(2)^2}{4}", r"A_8=\pi\,cm^2"], LEFT),
        ]

        self.solve_advanced_problem(
            geo,
            positives,
            negatives,
            "PROBLEM 2 · BRIDGE PLATE",
            [
                "Outside: rectangle + 2 semicircular caps.",
                "Inside: rectangle + 2 circles + 2 quarters.",
                "Eight components — classify before simplifying.",
            ],
            r"A_{(+)}=112+8\pi+8\pi=112+16\pi",
            r"A_{(-)}=18+\pi+\pi+\pi+\pi=18+4\pi",
            [
                (r"A_s=(112+16\pi)-(18+4\pi)", 27),
                (r"A_s=94+12\pi", 32),
                (r"A_s\approx131.70\,cm^2", 31),
            ],
            [
                "3 positive + 5 negative components ✓",
                "Two semicircles form one full r=4 circle ✓",
                "Two quarters contribute 2π in total ✓",
                "Every gap is subtracted exactly once ✓",
            ],
        )

    # ==================================================================
    # PROBLEM 3 — HEXAGON PLAZA · 6 COMPONENTS
    # ==================================================================
    def hexagon_plaza_region(self):
        s = 0.34
        side = 8 * s

        hx = RegularPolygon(
            n=6,
            radius=side,
            start_angle=0,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        center = hx.get_center()
        apothem = DashedLine(
            center,
            center + UP * (4 * math.sqrt(3) * s),
            color=BLACK,
            stroke_width=2,
        )

        circle_center = center + LEFT * 1.25 + UP * 0.85
        circle = Circle(
            radius=2 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        sector_center = center + RIGHT * 1.02 + UP * 0.18
        sector = Sector(
            radius=3 * s,
            angle=PI / 2,
            start_angle=-PI / 4,
            arc_center=sector_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        rh_center = center + LEFT * 0.92 + DOWN * 0.88
        rh = Polygon(
            rh_center + LEFT * (2 * s),
            rh_center + UP * (1.5 * s),
            rh_center + RIGHT * (2 * s),
            rh_center + DOWN * (1.5 * s),
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        tri_center = center + RIGHT * 0.82 + DOWN * 0.98
        tri = Polygon(
            tri_center + LEFT * (2 * s) + DOWN * (1.5 * s),
            tri_center + RIGHT * (2 * s) + DOWN * (1.5 * s),
            tri_center + UP * (1.5 * s),
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        rgap = Rectangle(
            width=3 * s,
            height=2 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(center + UP * 1.28)

        verts = hx.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 2 * s), verts, "P3 circle"
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(sector_center, 3 * s, -PI / 4, PI / 2),
            verts,
            "P3 sector",
        )
        self._assert_points_in_polygon(rh.get_vertices(), verts, "P3 rhombus")
        self._assert_points_in_polygon(tri.get_vertices(), verts, "P3 triangle")
        self._assert_points_in_polygon(rgap.get_vertices(), verts, "P3 rectangle")

        labels = VGroup(
            self.txt("regular hexagon · side=8", 16, BOLD).next_to(hx, DOWN, buff=0.10),
            self.math(r"P=48\,\text{cm}", 22).next_to(hx, LEFT, buff=0.06),
            self.math(r"a=4\sqrt3\,\text{cm}", 21).next_to(apothem, RIGHT, buff=0.05),
            self.txt("r=2", 10, BOLD).move_to(circle),
            self.txt("90° · r=3", 10, BOLD).move_to(sector_center + RIGHT * 0.22),
            self.txt("D=4 · d=3", 9, BOLD).move_to(rh),
            self.txt("b=4 · h=3", 9, BOLD).move_to(tri),
            self.txt("3×2", 9, BOLD).move_to(rgap),
        )

        geo = VGroup(hx, circle, sector, rh, tri, rgap, apothem, labels)
        return geo, hx, circle, sector, rh, tri, rgap

    def beat_hexagon_plaza(self) -> None:
        geo, hx, circle, sector, rh, tri, rgap = self.hexagon_plaza_region()

        positives = [
            (hx, "A1 regular hexagon", "A1 · HEXAGON (+)",
             [r"A_1=\frac{Pa}{2}",
              r"A_1=\frac{48(4\sqrt3)}{2}",
              r"A_1=96\sqrt3\,cm^2"], RIGHT),
        ]
        negatives = [
            (circle, "A2 circle", "A2 · CIRCLE (−)",
             [r"A_2=\pi(2)^2", r"A_2=4\pi\,cm^2"], RIGHT),
            (sector, "A3 90° sector", "A3 · 90° SECTOR (−)",
             [r"A_3=\frac{90}{360}\pi(3)^2",
              r"A_3=\frac{9\pi}{4}\,cm^2"], LEFT),
            (rh, "A4 rhombus", "A4 · RHOMBUS (−)",
             [r"A_4=\frac{4(3)}{2}", r"A_4=6\,cm^2"], RIGHT),
            (tri, "A5 triangle", "A5 · TRIANGLE (−)",
             [r"A_5=\frac{4(3)}{2}", r"A_5=6\,cm^2"], LEFT),
            (rgap, "A6 rectangle", "A6 · RECTANGLE GAP (−)",
             [r"A_6=3(2)", r"A_6=6\,cm^2"], DOWN),
        ]

        self.solve_advanced_problem(
            geo,
            positives,
            negatives,
            "PROBLEM 3 · HEXAGON PLAZA",
            [
                "One regular polygon contains five different gaps.",
                "The apothem belongs only to the hexagon formula.",
                "Keep radicals and π exact until the final line.",
            ],
            r"A_{(+)}=96\sqrt3",
            r"A_{(-)}=4\pi+\frac{9\pi}{4}+6+6+6=18+\frac{25\pi}{4}",
            [
                (r"A_s=96\sqrt3-\left(18+\frac{25\pi}{4}\right)", 26),
                (r"A_s=96\sqrt3-18-\frac{25\pi}{4}", 28),
                (r"A_s\approx128.64\,cm^2", 31),
            ],
            [
                "6 components accounted for ✓",
                "Apothem is perpendicular to a side ✓",
                "90/360 = 1/4 for the sector ✓",
                "Exact radical and π retained until the end ✓",
            ],
        )

    # ==================================================================
    # PROBLEM 4 — ROOFED STADIUM · 8 COMPONENTS
    # ==================================================================
    def roofed_stadium_region(self):
        s = 0.26

        rect = Rectangle(
            width=16 * s,
            height=8 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        cap_r = 4 * s
        lcap = Sector(
            radius=cap_r,
            angle=PI,
            start_angle=PI / 2,
            arc_center=rect.get_left(),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        rcap = Sector(
            radius=cap_r,
            angle=PI,
            start_angle=-PI / 2,
            arc_center=rect.get_right(),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        y0 = rect.get_top()[1]
        roof = Polygon(
            np.array([-8 * s, y0, 0]),
            np.array([ 8 * s, y0, 0]),
            np.array([ 5 * s, y0 + 4 * s, 0]),
            np.array([-5 * s, y0 + 4 * s, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        circle_center = rect.get_center() + LEFT * 1.33 + UP * 0.44
        circle = Circle(
            radius=2 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        rh_center = rect.get_center() + DOWN * 0.50
        rh = Polygon(
            rh_center + LEFT * (3 * s),
            rh_center + UP * (2 * s),
            rh_center + RIGHT * (3 * s),
            rh_center + DOWN * (2 * s),
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        tri_center = rect.get_center() + RIGHT * 0.68 + UP * 0.44
        tri = Polygon(
            tri_center + LEFT * (3 * s) + DOWN * (1.5 * s),
            tri_center + RIGHT * (3 * s) + DOWN * (1.5 * s),
            tri_center + UP * (1.5 * s),
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        sec_center = rect.get_center() + RIGHT * 1.40 + DOWN * 0.20
        sector = Sector(
            radius=3 * s,
            angle=2 * PI / 3,
            start_angle=PI,
            arc_center=sec_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        rv = rect.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 2 * s), rv, "P4 circle"
        )
        self._assert_points_in_polygon(rh.get_vertices(), rv, "P4 rhombus")
        self._assert_points_in_polygon(tri.get_vertices(), rv, "P4 triangle")
        self._assert_points_in_polygon(
            self._sector_sample_points(sec_center, 3 * s, PI, 2 * PI / 3),
            rv,
            "P4 sector",
        )

        labels = VGroup(
            self.txt("rectangle 16×8", 14, BOLD).next_to(rect, DOWN, buff=0.10),
            self.txt("side caps r=4", 13, BOLD).next_to(lcap, LEFT, buff=0.05),
            self.txt("roof B=16 · b=10 · h=4", 13, BOLD).next_to(roof, UP, buff=0.07),
            self.txt("r=2", 10, BOLD).move_to(circle),
            self.txt("D=6 · d=4", 9, BOLD).move_to(rh),
            self.txt("b=6 · h=3", 9, BOLD).move_to(tri),
            self.txt("120° · r=3", 9, BOLD).move_to(sec_center + LEFT * 0.18),
        )

        geo = VGroup(VGroup(rect, lcap, rcap, roof), circle, rh, tri, sector, labels)
        return geo, rect, lcap, rcap, roof, circle, rh, tri, sector

    def beat_roofed_stadium(self) -> None:
        geo, rect, lcap, rcap, roof, circle, rh, tri, sector = self.roofed_stadium_region()

        positives = [
            (rect, "A1 rectangle", "A1 · RECTANGLE (+)",
             [r"A_1=16(8)", r"A_1=128\,cm^2"], RIGHT),
            (lcap, "A2 left semicircle", "A2 · LEFT SEMICIRCLE (+)",
             [r"A_2=\frac{\pi(4)^2}{2}", r"A_2=8\pi\,cm^2"], RIGHT),
            (rcap, "A3 right semicircle", "A3 · RIGHT SEMICIRCLE (+)",
             [r"A_3=\frac{\pi(4)^2}{2}", r"A_3=8\pi\,cm^2"], LEFT),
            (roof, "A4 trapezoid roof", "A4 · TRAPEZOID ROOF (+)",
             [r"A_4=\frac{(16+10)(4)}{2}", r"A_4=52\,cm^2"], DOWN),
        ]
        negatives = [
            (circle, "A5 circle", "A5 · CIRCLE GAP (−)",
             [r"A_5=\pi(2)^2", r"A_5=4\pi\,cm^2"], RIGHT),
            (rh, "A6 rhombus", "A6 · RHOMBUS GAP (−)",
             [r"A_6=\frac{6(4)}{2}", r"A_6=12\,cm^2"], RIGHT),
            (tri, "A7 triangle", "A7 · TRIANGLE GAP (−)",
             [r"A_7=\frac{6(3)}{2}", r"A_7=9\,cm^2"], LEFT),
            (sector, "A8 120° sector", "A8 · 120° SECTOR (−)",
             [r"A_8=\frac{120}{360}\pi(3)^2", r"A_8=3\pi\,cm^2"], LEFT),
        ]

        self.solve_advanced_problem(
            geo,
            positives,
            negatives,
            "PROBLEM 4 · ROOFED STADIUM",
            [
                "Four pieces build the exterior.",
                "Four different gaps are removed.",
                "Use positive and negative subtotals to control the algebra.",
            ],
            r"A_{(+)}=128+8\pi+8\pi+52=180+16\pi",
            r"A_{(-)}=4\pi+12+9+3\pi=21+7\pi",
            [
                (r"A_s=(180+16\pi)-(21+7\pi)", 27),
                (r"A_s=159+9\pi", 32),
                (r"A_s\approx187.27\,cm^2", 31),
            ],
            [
                "4 positive + 4 negative components ✓",
                "Roof is added; all internal white regions are removed ✓",
                "120° sector contributes one third of a circle ✓",
                "Positive/negative subtotals reconcile exactly ✓",
            ],
        )

    # ==================================================================
    # PROBLEM 5 — CAPSTONE EMBLEM · 9 COMPONENTS
    # ==================================================================
    def capstone_emblem_region(self):
        s = 0.20

        body = Rectangle(
            width=20 * s,
            height=12 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        roof = Polygon(
            np.array([-10 * s, y0, 0]),
            np.array([ 10 * s, y0, 0]),
            np.array([ 7 * s, y0 + 5 * s, 0]),
            np.array([-7 * s, y0 + 5 * s, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        cap_center = np.array([0, y0 + 5 * s, 0])
        cap = Sector(
            radius=7 * s,
            angle=PI,
            start_angle=0,
            arc_center=cap_center,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        c_big_center = body.get_center() + LEFT * 1.10 + UP * 0.55
        c_big = Circle(
            radius=2 * s,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(c_big_center)

        square = Square(
            side_length=3 * s,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(body.get_center() + RIGHT * 1.18 + UP * 0.55)

        rh_center = body.get_center() + DOWN * 0.55
        rh = Polygon(
            rh_center + LEFT * (3 * s),
            rh_center + UP * (2 * s),
            rh_center + RIGHT * (3 * s),
            rh_center + DOWN * (2 * s),
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        sec_center = body.get_center() + RIGHT * 1.30 + DOWN * 0.45
        sector = Sector(
            radius=3 * s,
            angle=PI / 2,
            start_angle=PI,
            arc_center=sec_center,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        )

        small_r = 1 * s
        s1_center = body.get_center() + LEFT * 1.55 + DOWN * 0.55
        s2_center = body.get_center() + LEFT * 0.45 + UP * 0.55
        s1 = Circle(
            radius=small_r,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(s1_center)
        s2 = s1.copy().move_to(s2_center)

        bv = body.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(c_big_center, 2 * s), bv, "P5 large circle"
        )
        self._assert_points_in_polygon(square.get_vertices(), bv, "P5 square")
        self._assert_points_in_polygon(rh.get_vertices(), bv, "P5 rhombus")
        self._assert_points_in_polygon(
            self._sector_sample_points(sec_center, 3 * s, PI, PI / 2),
            bv,
            "P5 sector",
        )
        self._assert_points_in_polygon(
            self._circle_sample_points(s1_center, small_r), bv, "P5 small circle 1"
        )
        self._assert_points_in_polygon(
            self._circle_sample_points(s2_center, small_r), bv, "P5 small circle 2"
        )

        labels = VGroup(
            self.txt("20 × 12", 14, BOLD).next_to(body, DOWN, buff=0.12),
            self.txt("B=20 · b=14 · h=5", 12, BOLD).next_to(roof, RIGHT, buff=0.08),
            self.txt("semicircle · r=7", 12, BOLD).next_to(cap, UP, buff=0.07),
            self.txt("r=2", 9, BOLD).move_to(c_big),
            self.txt("3×3", 9, BOLD).move_to(square),
            self.txt("D=6 · d=4", 8, BOLD).move_to(rh),
            self.txt("90° · r=3", 8, BOLD).move_to(sec_center + LEFT * 0.15),
            self.txt("r=1", 8, BOLD).move_to(s1),
            self.txt("r=1", 8, BOLD).move_to(s2),
        )

        geo = VGroup(VGroup(body, roof, cap), c_big, square, rh, sector, s1, s2, labels)
        return geo, body, roof, cap, c_big, square, rh, sector, s1, s2

    def beat_capstone_emblem(self) -> None:
        geo, body, roof, cap, c_big, square, rh, sector, s1, s2 = self.capstone_emblem_region()

        positives = [
            (body, "A1 rectangle", "A1 · RECTANGLE (+)",
             [r"A_1=20(12)", r"A_1=240\,cm^2"], RIGHT),
            (roof, "A2 trapezoid", "A2 · TRAPEZOID (+)",
             [r"A_2=\frac{(20+14)(5)}{2}", r"A_2=85\,cm^2"], RIGHT),
            (cap, "A3 semicircle", "A3 · SEMICIRCLE (+)",
             [r"A_3=\frac{\pi(7)^2}{2}", r"A_3=\frac{49\pi}{2}\,cm^2"], DOWN),
        ]
        negatives = [
            (c_big, "A4 circle r=2", "A4 · LARGE CIRCLE (−)",
             [r"A_4=\pi(2)^2", r"A_4=4\pi\,cm^2"], RIGHT),
            (square, "A5 square 3×3", "A5 · SQUARE (−)",
             [r"A_5=3^2", r"A_5=9\,cm^2"], LEFT),
            (rh, "A6 rhombus", "A6 · RHOMBUS (−)",
             [r"A_6=\frac{6(4)}{2}", r"A_6=12\,cm^2"], RIGHT),
            (sector, "A7 90° sector", "A7 · 90° SECTOR (−)",
             [r"A_7=\frac{90}{360}\pi(3)^2",
              r"A_7=\frac{9\pi}{4}\,cm^2"], LEFT),
            (s1, "A8 circle r=1", "A8 · SMALL CIRCLE 1 (−)",
             [r"A_8=\pi(1)^2", r"A_8=\pi\,cm^2"], RIGHT),
            (s2, "A9 circle r=1", "A9 · SMALL CIRCLE 2 (−)",
             [r"A_9=\pi(1)^2", r"A_9=\pi\,cm^2"], LEFT),
        ]

        self.solve_advanced_problem(
            geo,
            positives,
            negatives,
            "PROBLEM 5 · CAPSTONE EMBLEM",
            [
                "Three pieces build the outside.",
                "Six independent gaps must be removed.",
                "Nine terms: organize first, calculate second.",
            ],
            r"A_{(+)}=240+85+\frac{49\pi}{2}=325+\frac{49\pi}{2}",
            r"A_{(-)}=21+\frac{33\pi}{4}",
            [
                (r"A_s=\left(325+\frac{49\pi}{2}\right)-\left(21+\frac{33\pi}{4}\right)", 24),
                (r"A_s=304+\frac{65\pi}{4}", 31),
                (r"A_s\approx355.05\,cm^2", 31),
            ],
            [
                "3 positive + 6 negative components = 9 total ✓",
                "Two small circles are counted as separate gaps ✓",
                "All exact fractions of π are combined correctly ✓",
                "Final area is positive and below the complete outside ✓",
            ],
        )

    # ------------------------------------------------------------------
    # Closing
    # ------------------------------------------------------------------
    def closing_class3(self) -> None:
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=RUN_NORMAL)

        title = self.txt("ADVANCED FIGURE ≠ NEW METHOD", 44, BOLD)
        formula = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=9.0,
            height=1.12,
            size=39,
        )
        steps = VGroup(
            self.txt("1. Count every area component.", 24, BOLD),
            self.txt("2. Assign + or − before calculating.", 24, BOLD),
            self.txt("3. Solve each local area independently.", 24, BOLD),
            self.txt("4. Build positive and negative subtotals.", 24, BOLD),
            self.txt("5. Combine exact forms, approximate last, verify units.", 24, BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        group = VGroup(title, formula, steps).arrange(DOWN, buff=0.26)
        self.fit(group, 13.2, 5.9)
        group.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=RUN_SLOW)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        for line in steps:
            self.play(FadeIn(line, shift=RIGHT * 0.08), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ / 2)
        self.wait(PAUSE_FINAL)

    # ------------------------------------------------------------------
    # Full total scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.validate_math_class2()
        self.opening_class3()
        self.formula_atlas()
        self.advanced_contract()
        self.build_workbench_class3()

        self._qa_problem = "advanced_facade"
        self.beat_advanced_facade()

        self._qa_problem = "bridge_plate"
        self.beat_bridge_plate()

        self._qa_problem = "hexagon_plaza"
        self.beat_hexagon_plaza()

        self._qa_problem = "roofed_stadium"
        self.beat_roofed_stadium()

        self._qa_problem = "capstone_emblem"
        self.beat_capstone_emblem()

        self._qa_problem = ""
        self.closing_class3()


# Preview:
# manim -pql Geometry8_Shaded_Areas_Class3_Advanced_Complex_V3.py \
#   Geometry8ShadedAreasClass3AdvancedComplexV3 --disable_caching
#
# Final:
# manim -pqh Geometry8_Shaded_Areas_Class3_Advanced_Complex_V3.py \
#   Geometry8ShadedAreasClass3AdvancedComplexV3 --disable_caching
