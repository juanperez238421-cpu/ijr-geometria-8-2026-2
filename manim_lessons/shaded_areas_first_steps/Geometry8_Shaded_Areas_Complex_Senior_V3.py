#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas — Complex Senior V3.

Senior classroom version with a new set of harder composite-area problems.
Every worked problem contains at least six visible geometric components and
requires explicit signed-area bookkeeping.

Method:
SEE -> DECOMPOSE -> MARK (+/-) -> CALCULATE LOCAL AREAS ->
BUILD SUBTOTALS -> COMBINE -> CHECK.

Built on the validated V6 / V5 camera, workbench and event-QA architecture.
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


class Geometry8ShadedAreasComplexSeniorV3(
    Geometry8ShadedAreasClass2Complex4PlusV6
):
    """Five new high-complexity shaded-area problems with full solutions."""

    # ================================================================
    # NUMERICAL CONTRACT
    # ================================================================
    def validate_math_class2(self) -> None:
        p1 = (
            18*8
            + ((18+12)*5)/2
            + (math.pi*6**2)/2
            - 3**2
            - math.pi*2**2
            - (4*3)/2
        )
        p2 = (
            14*6
            + math.pi*3**2
            + (8*4)/2
            - 4*2
            - 2*((math.pi*2**2)/4)
            - math.pi*1.5**2
        )
        p3 = (
            54*math.sqrt(3)
            - math.pi*1**2
            - (90/360)*math.pi*2**2
            - (4*2)/2
            - (3*2)/2
            - 2**2
        )
        p4 = (
            20*12
            + (math.pi*5**2)/2
            - math.pi*3**2
            - 2*(3*2)
            - 2*((math.pi*2**2)/2)
        )
        p5 = (
            20*12
            + ((20+12)*4)/2
            + (math.pi*6**2)/2
            - math.pi*2**2
            - (6*4)/2
            - (90/360)*math.pi*4**2
            - 4*3
            - (4*3)/2
        )

        assert math.isclose(p1, 204 + 14*math.pi, abs_tol=1e-12)
        assert math.isclose(p2, 92 + 4.75*math.pi, abs_tol=1e-12)
        assert math.isclose(p3, 54*math.sqrt(3) - 11 - 2*math.pi, abs_tol=1e-12)
        assert math.isclose(p4, 228 - 0.5*math.pi, abs_tol=1e-12)
        assert math.isclose(p5, 274 + 10*math.pi, abs_tol=1e-12)

        assert math.isclose(p1, 247.98229715025707, abs_tol=1e-9)
        assert math.isclose(p2, 106.92256510455152, abs_tol=1e-9)
        assert math.isclose(p3, 76.24755830153978, abs_tol=1e-9)
        assert math.isclose(p4, 226.4292036732051, abs_tol=1e-9)
        assert math.isclose(p5, 305.41592653589794, abs_tol=1e-9)

        counts = {
            "observatory": 6,
            "bridge": 8,
            "hexagonal_emblem": 6,
            "courtyard": 7,
            "master_capstone": 8,
        }
        assert min(counts.values()) >= 6

    # ================================================================
    # INTRO
    # ================================================================
    def senior_v3_contract(self) -> None:
        title = self.txt("SHADED AREAS · SENIOR V3", 54, BOLD)
        subtitle = self.txt(
            "NEW COMPLEX SET · 6–8 COMPONENTS PER PROBLEM",
            28, BOLD, DARK_GRAY
        )
        note = self.txt(
            "Difficulty now comes from bookkeeping, mixed formulas and exact forms — not from guessing.",
            23, NORMAL, DARK_GRAY
        )

        rows_data = [
            ("1", "OBSERVATORY", "6 pieces", "rectangle + trapezoid + semicircle − 3 gaps"),
            ("2", "BRIDGE", "8 pieces", "stadium + triangle − rectangle − quarters − circle"),
            ("3", "EMBLEM", "6 pieces", "hexagon − circle − sector − rhombus − triangle − square"),
            ("4", "COURTYARD", "7 pieces", "rectangle + semicircle − circle − 2 rectangles − 2 semicircles"),
            ("5", "MASTER", "8 pieces", "3 positive regions − 5 independent gaps"),
        ]

        rows = VGroup()
        for n, name, count, desc in rows_data:
            badge = Circle(
                radius=0.24, stroke_color=BLACK, stroke_width=2,
                fill_color=WHITE, fill_opacity=1
            )
            num = self.txt(n, 18, BOLD).move_to(badge)
            nm = self.txt(name, 21, BOLD)
            ct = self.txt(count, 19, BOLD)
            ds = self.txt(desc, 18)
            self.fit(ds, 7.4, 0.48)
            row = VGroup(VGroup(badge, num), nm, ct, ds).arrange(RIGHT, buff=0.28)
            self.fit(row, 13.5, 0.60)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        formula = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=8.8, height=1.08, size=40
        )

        g = VGroup(title, subtitle, note, rows, formula).arrange(DOWN, buff=0.26)
        self.fit(g, 14.2, 7.4)
        g.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP*0.08), run_time=RUN_SLOW)
        self.play(FadeIn(subtitle), FadeIn(note), run_time=RUN_NORMAL)
        for row in rows:
            self.play(FadeIn(row, shift=RIGHT*0.08), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ/2)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(g), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 1 — OBSERVATORY FACADE · 6 COMPONENTS
    # ================================================================
    def observatory_region(self) -> VGroup:
        s = 0.235

        body = Rectangle(
            width=18*s, height=8*s,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        y0 = body.get_top()[1]

        hb, ht, th = 9*s, 6*s, 5*s
        roof = Polygon(
            np.array([-hb, y0, 0]), np.array([hb, y0, 0]),
            np.array([ht, y0+th, 0]), np.array([-ht, y0+th, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )

        dome = Sector(
            radius=6*s, angle=PI, start_angle=0,
            arc_center=np.array([0, y0+th, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )

        square = Square(
            side_length=3*s,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        ).move_to(body.get_center()+LEFT*1.25+DOWN*0.25)

        circle_center = body.get_center()+RIGHT*1.35+UP*0.25
        circle = Circle(
            radius=2*s,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        ).move_to(circle_center)

        tb, t_h = 4*s, 3*s
        tc = body.get_center()+RIGHT*0.25+DOWN*0.55
        tri_pts = [
            tc+LEFT*(tb/2)+DOWN*(t_h/2),
            tc+RIGHT*(tb/2)+DOWN*(t_h/2),
            tc+UP*(t_h/2),
        ]
        triangle = Polygon(
            *tri_pts,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        )

        bverts = body.get_vertices()
        self._assert_points_in_polygon(square.get_vertices(), bverts, "P1 square")
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 2*s),
            bverts, "P1 circle"
        )
        self._assert_points_in_polygon(tri_pts, bverts, "P1 triangle")

        labels = VGroup(
            self.txt("18 × 8", 15, BOLD).next_to(body, DOWN, buff=0.12),
            self.txt("B=18 · b=12 · h=5", 13, BOLD).next_to(roof, RIGHT, buff=0.10),
            self.txt("semicircle r=6", 13, BOLD).next_to(dome, UP, buff=0.08),
            self.txt("3×3", 12, BOLD).move_to(square),
            self.txt("diameter=4", 11, BOLD).move_to(circle),
            self.txt("b=4 · h=3", 10, BOLD).move_to(triangle),
        )

        return VGroup(VGroup(body, roof, dome), square, circle, triangle, labels)

    def beat_observatory(self) -> None:
        self.step(0)
        geo = self.observatory_region()
        self.swap_left(geo)
        outer, sq, circ, tri, _ = geo
        body, roof, dome = outer

        self.swap_right(self.reason_card(
            "PROBLEM 1 · OBSERVATORY · SIX COMPONENTS",
            [
                "Build the outside with 3 positive pieces.",
                "Remove 3 independent gaps.",
                "Notice: diameter 4 means circle radius 2.",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(body), Indicate(roof), Indicate(dome), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(sq), Indicate(circ), Indicate(tri), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([body, roof, dome], [sq, circ, tri])
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2 trapezoid", "A3 semicircle"],
            ["A4 square", "A5 circle", "A6 triangle"]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(body, "A1 · RECTANGLE (+)",
                        [r"A_1=18(8)", r"A_1=144\,cm^2"], RIGHT)
        self.local_calc(roof, "A2 · TRAPEZOID (+)",
                        [r"A_2=\frac{(18+12)5}{2}", r"A_2=75\,cm^2"], RIGHT)
        self.local_calc(dome, "A3 · SEMICIRCLE (+)",
                        [r"A_3=\frac{\pi(6)^2}{2}", r"A_3=18\pi\,cm^2"], DOWN)
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL", r"A_{(+)}=219+18\pi", 30
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(sq, "A4 · SQUARE GAP (−)",
                        [r"A_4=3^2", r"A_4=9\,cm^2"], RIGHT)
        self.local_calc(circ, "A5 · CIRCLE GAP (−)",
                        [r"d=4\Rightarrow r=2", r"A_5=\pi(2)^2", r"A_5=4\pi\,cm^2"], LEFT)
        self.local_calc(tri, "A6 · TRIANGLE GAP (−)",
                        [r"A_6=\frac{4(3)}{2}", r"A_6=6\,cm^2"], RIGHT)
        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL", r"A_{(-)}=15+4\pi", 30
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=(219+18\pi)-(15+4\pi)", 27),
            self.math(r"A_s=204+14\pi", 32),
            self.math(r"A_s\approx247.98\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "6 components accounted for ✓",
                "Diameter converted to radius before area ✓",
                "Exact π form kept until the final line ✓",
                "247.98 cm² is smaller than the outside total ✓",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 2 — BRIDGE · 8 COMPONENTS
    # ================================================================
    def bridge_region(self) -> VGroup:
        s = 0.285

        rect = Rectangle(
            width=14*s, height=6*s,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        rcap = 3*s
        left_cap = Sector(
            radius=rcap, angle=PI, start_angle=PI/2,
            arc_center=rect.get_left(),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        right_cap = Sector(
            radius=rcap, angle=PI, start_angle=-PI/2,
            arc_center=rect.get_right(),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )

        tb, th = 8*s, 4*s
        base_y = rect.get_top()[1]
        tri_pts = [
            np.array([-tb/2, base_y, 0]),
            np.array([tb/2, base_y, 0]),
            np.array([0, base_y+th, 0]),
        ]
        top_triangle = Polygon(
            *tri_pts,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )

        gap_rect = Rectangle(
            width=4*s, height=2*s,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        ).move_to(rect.get_center()+DOWN*0.15)

        rq = 2*s
        q1_center = rect.get_corner(UL)+RIGHT*0.16+DOWN*0.16
        q1 = Sector(
            radius=rq, angle=PI/2, start_angle=-PI/2,
            arc_center=q1_center,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        )
        q2_center = rect.get_corner(DR)+LEFT*0.16+UP*0.16
        q2 = Sector(
            radius=rq, angle=PI/2, start_angle=PI/2,
            arc_center=q2_center,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        )

        circle_center = rect.get_center()+RIGHT*1.20+UP*0.48
        circle = Circle(
            radius=1.5*s,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1
        ).move_to(circle_center)

        rv = rect.get_vertices()
        self._assert_points_in_polygon(gap_rect.get_vertices(), rv, "P2 rectangle gap")
        self._assert_points_in_polygon(
            self._sector_sample_points(q1_center, rq, -PI/2, PI/2), rv, "P2 q1"
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(q2_center, rq, PI/2, PI/2), rv, "P2 q2"
        )
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 1.5*s), rv, "P2 circle"
        )

        labels = VGroup(
            self.txt("rectangle 14×6", 14, BOLD).next_to(rect, DOWN, buff=0.10),
            self.txt("caps r=3", 13, BOLD).next_to(left_cap, LEFT, buff=0.06),
            self.txt("triangle b=8 · h=4", 12, BOLD).next_to(top_triangle, UP, buff=0.08),
            self.txt("4×2", 11, BOLD).move_to(gap_rect),
            self.txt("quarter gaps r=2", 11, BOLD).next_to(rect, UP, buff=0.07),
            self.txt("r=1.5", 10, BOLD).move_to(circle),
        )
        return VGroup(
            VGroup(rect, left_cap, right_cap, top_triangle),
            gap_rect, q1, q2, circle, labels
        )

    def beat_bridge(self) -> None:
        self.step(0)
        geo = self.bridge_region()
        self.swap_left(geo)
        outer, gap_rect, q1, q2, circle, _ = geo
        rect, lcap, rcap, top_tri = outer

        self.swap_right(self.reason_card(
            "PROBLEM 2 · BRIDGE · EIGHT COMPONENTS",
            [
                "Positive: rectangle + 2 semicircles + triangle.",
                "Negative: rectangle + 2 quarter circles + circle.",
                "Combine equal circular fractions before final arithmetic.",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(rect), Indicate(VGroup(lcap, rcap)), Indicate(top_tri),
                  run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(gap_rect), Indicate(VGroup(q1, q2)), Indicate(circle),
                  run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([rect, lcap, rcap, top_tri], [gap_rect, q1, q2, circle])
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2+A3 semicircles", "A4 triangle"],
            ["A5 rectangle", "A6+A7 quarters", "A8 circle"]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(rect, "A1 · RECTANGLE (+)",
                        [r"A_1=14(6)", r"A_1=84\,cm^2"], RIGHT)
        self.local_calc(VGroup(lcap, rcap), "A2+A3 · TWO SEMICIRCLES (+)",
                        [r"A_{2+3}=\pi(3)^2", r"A_{2+3}=9\pi\,cm^2"], DOWN)
        self.local_calc(top_tri, "A4 · TRIANGLE (+)",
                        [r"A_4=\frac{8(4)}{2}", r"A_4=16\,cm^2"], DOWN)
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL", r"A_{(+)}=100+9\pi", 30
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(gap_rect, "A5 · RECTANGLE GAP (−)",
                        [r"A_5=4(2)", r"A_5=8\,cm^2"], RIGHT)
        self.local_calc(VGroup(q1, q2), "A6+A7 · TWO QUARTERS (−)",
                        [r"2\left(\frac{\pi(2)^2}{4}\right)", r"A_{6+7}=2\pi\,cm^2"], DOWN)
        self.local_calc(circle, "A8 · CIRCLE GAP (−)",
                        [r"A_8=\pi(1.5)^2", r"A_8=2.25\pi\,cm^2"], LEFT)
        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL", r"A_{(-)}=8+4.25\pi", 30
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=(100+9\pi)-(8+4.25\pi)", 26),
            self.math(r"A_s=92+4.75\pi", 31),
            self.math(r"A_s\approx106.92\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "8 visible components accounted for ✓",
                "Two semicircles became one full circle ✓",
                "Two quarters became one semicircle ✓",
                "106.92 cm² is physically plausible ✓",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 3 — HEXAGONAL EMBLEM · 6 COMPONENTS
    # ================================================================
    def emblem_region(self) -> VGroup:
        s = 0.40
        side = 6*s
        hx = RegularPolygon(
            n=6, radius=side, start_angle=0,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        center = hx.get_center()

        circle_center = center + LEFT*1.15 + UP*0.75
        circle = Circle(
            radius=1*s, stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        ).move_to(circle_center)

        sector = Sector(
            radius=2*s, angle=PI/2, start_angle=-PI/4,
            arc_center=center+RIGHT*0.85+UP*0.45,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )
        sector_center = center+RIGHT*0.85+UP*0.45

        rc = center + LEFT*0.90 + DOWN*0.85
        D, d = 4*s, 2*s
        rh_pts = [rc+LEFT*D/2, rc+UP*d/2, rc+RIGHT*D/2, rc+DOWN*d/2]
        rh = Polygon(
            *rh_pts, stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )

        tc = center + RIGHT*0.90 + DOWN*0.85
        tb, th = 3*s, 2*s
        tri_pts = [
            tc+LEFT*tb/2+DOWN*th/2,
            tc+RIGHT*tb/2+DOWN*th/2,
            tc+UP*th/2,
        ]
        tri = Polygon(
            *tri_pts, stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )

        sq = Square(
            side_length=2*s,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        ).move_to(center+UP*1.15)

        verts = hx.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 1*s), verts, "P3 circle"
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(sector_center, 2*s, -PI/4, PI/2),
            verts, "P3 sector"
        )
        self._assert_points_in_polygon(rh_pts, verts, "P3 rhombus")
        self._assert_points_in_polygon(tri_pts, verts, "P3 triangle")
        self._assert_points_in_polygon(sq.get_vertices(), verts, "P3 square")

        apothem = DashedLine(
            center, center+UP*(3*math.sqrt(3)*s),
            color=BLACK, stroke_width=2
        )

        labels = VGroup(
            self.txt("regular hexagon · side=6", 15, BOLD).next_to(hx, DOWN, buff=0.10),
            self.math(r"a=3\sqrt3", 20).next_to(apothem, LEFT, buff=0.06),
            self.txt("r=1", 10, BOLD).move_to(circle),
            self.txt("90° · r=2", 10, BOLD).move_to(sector_center+RIGHT*0.22),
            self.txt("D=4 · d=2", 9, BOLD).move_to(rh),
            self.txt("b=3 · h=2", 9, BOLD).move_to(tri),
            self.txt("2×2", 10, BOLD).move_to(sq),
        )
        return VGroup(hx, circle, sector, rh, tri, sq, apothem, labels)

    def beat_emblem(self) -> None:
        self.step(0)
        geo = self.emblem_region()
        self.swap_left(geo)
        hx, circle, sector, rh, tri, sq, apothem, _ = geo

        self.swap_right(self.reason_card(
            "PROBLEM 3 · HEXAGONAL EMBLEM · SIX COMPONENTS",
            [
                "One regular polygon is the whole.",
                "Five different gaps use five formula decisions.",
                "The apothem is needed only for the hexagon.",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(apothem), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(circle), Indicate(sector), Indicate(rh),
                  Indicate(tri), Indicate(sq), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([hx], [circle, sector, rh, tri, sq])
        self.swap_right(self.signed_ledger(
            ["A1 regular hexagon"],
            ["A2 circle", "A3 90° sector", "A4 rhombus", "A5 triangle", "A6 square"]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(
            hx, "A1 · HEXAGON (+)",
            [r"P=36,\ a=3\sqrt3", r"A_1=\frac{Pa}{2}", r"A_1=54\sqrt3\,cm^2"],
            RIGHT
        )
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL", r"A_{(+)}=54\sqrt3", 30
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(circle, "A2 · CIRCLE GAP (−)",
                        [r"A_2=\pi(1)^2", r"A_2=\pi"], RIGHT)
        self.local_calc(sector, "A3 · 90° SECTOR GAP (−)",
                        [r"A_3=\frac{90}{360}\pi(2)^2", r"A_3=\pi"], LEFT)
        self.local_calc(rh, "A4 · RHOMBUS GAP (−)",
                        [r"A_4=\frac{4(2)}{2}", r"A_4=4"], RIGHT)
        self.local_calc(tri, "A5 · TRIANGLE GAP (−)",
                        [r"A_5=\frac{3(2)}{2}", r"A_5=3"], LEFT)
        self.local_calc(sq, "A6 · SQUARE GAP (−)",
                        [r"A_6=2^2", r"A_6=4"], DOWN)

        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL", r"A_{(-)}=11+2\pi", 30
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=54\sqrt3-(11+2\pi)", 27),
            self.math(r"A_s=54\sqrt3-11-2\pi", 29),
            self.math(r"A_s\approx76.25\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "5 independent gaps subtracted once each ✓",
                "90° means one quarter of a circle ✓",
                "Exact radical and π retained ✓",
                "76.25 cm² < whole hexagon area ✓",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 4 — COURTYARD · 7 COMPONENTS
    # ================================================================
    def courtyard_region(self) -> VGroup:
        s = 0.235

        body = Rectangle(
            width=20*s, height=12*s,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        dome = Sector(
            radius=5*s, angle=PI, start_angle=0,
            arc_center=body.get_top(),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )

        circle_center = body.get_center()
        circle = Circle(
            radius=3*s,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        ).move_to(circle_center)

        r1 = Rectangle(
            width=3*s, height=2*s,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        ).move_to(body.get_center()+LEFT*1.45+DOWN*0.75)
        r2 = r1.copy().move_to(body.get_center()+RIGHT*1.45+DOWN*0.75)

        semi_r = 2*s
        s1_center = body.get_center()+LEFT*1.55+UP*0.92
        s2_center = body.get_center()+RIGHT*1.55+UP*0.92
        s1 = Sector(
            radius=semi_r, angle=PI, start_angle=0,
            arc_center=s1_center,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )
        s2 = Sector(
            radius=semi_r, angle=PI, start_angle=0,
            arc_center=s2_center,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )

        verts = body.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 3*s), verts, "P4 circle"
        )
        self._assert_points_in_polygon(r1.get_vertices(), verts, "P4 rect1")
        self._assert_points_in_polygon(r2.get_vertices(), verts, "P4 rect2")
        self._assert_points_in_polygon(
            self._sector_sample_points(s1_center, semi_r, 0, PI), verts, "P4 semi1"
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(s2_center, semi_r, 0, PI), verts, "P4 semi2"
        )

        labels = VGroup(
            self.txt("20 × 12", 14, BOLD).next_to(body, DOWN, buff=0.10),
            self.txt("top semicircle r=5", 13, BOLD).next_to(dome, UP, buff=0.08),
            self.txt("r=3", 11, BOLD).move_to(circle),
            self.txt("3×2", 10, BOLD).move_to(r1),
            self.txt("3×2", 10, BOLD).move_to(r2),
            self.txt("r=2", 9, BOLD).move_to(s1_center+UP*0.15),
            self.txt("r=2", 9, BOLD).move_to(s2_center+UP*0.15),
        )
        return VGroup(VGroup(body, dome), circle, r1, r2, s1, s2, labels)

    def beat_courtyard(self) -> None:
        self.step(0)
        geo = self.courtyard_region()
        self.swap_left(geo)
        outer, circle, r1, r2, s1, s2, _ = geo
        body, dome = outer

        self.swap_right(self.reason_card(
            "PROBLEM 4 · COURTYARD · SEVEN COMPONENTS",
            [
                "Positive: rectangle + top semicircle.",
                "Negative: circle + 2 rectangles + 2 semicircles.",
                "Symmetry lets us group equal gaps efficiently.",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(1)
        self.play(Indicate(body), Indicate(dome), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(circle), Indicate(VGroup(r1, r2)), Indicate(VGroup(s1, s2)),
                  run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed([body, dome], [circle, r1, r2, s1, s2])
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2 semicircle"],
            ["A3 circle", "A4+A5 rectangles", "A6+A7 semicircles"]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(body, "A1 · RECTANGLE (+)",
                        [r"A_1=20(12)", r"A_1=240"], RIGHT)
        self.local_calc(dome, "A2 · SEMICIRCLE (+)",
                        [r"A_2=\frac{\pi(5)^2}{2}", r"A_2=12.5\pi"], DOWN)
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL", r"A_{(+)}=240+12.5\pi", 29
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(circle, "A3 · CIRCLE GAP (−)",
                        [r"A_3=\pi(3)^2", r"A_3=9\pi"], RIGHT)
        self.local_calc(VGroup(r1, r2), "A4+A5 · TWO RECTANGLES (−)",
                        [r"2(3)(2)", r"A_{4+5}=12"], DOWN)
        self.local_calc(VGroup(s1, s2), "A6+A7 · TWO SEMICIRCLES (−)",
                        [r"2\left(\frac{\pi(2)^2}{2}\right)", r"A_{6+7}=4\pi"], DOWN)
        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL", r"A_{(-)}=12+13\pi", 29
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=(240+12.5\pi)-(12+13\pi)", 26),
            self.math(r"A_s=228-0.5\pi", 31),
            self.math(r"A_s\approx226.43\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "CHECK",
            [
                "7 components accounted for ✓",
                "Equal gaps grouped without double-counting ✓",
                "Negative circular total exceeds the top semicircle slightly ✓",
                "226.43 cm² is consistent with the drawing ✓",
            ]
        ))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # PROBLEM 5 — MASTER CAPSTONE · 8 COMPONENTS
    # ================================================================
    def master_region(self) -> VGroup:
        s = 0.22

        body = Rectangle(
            width=20*s, height=12*s,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        y0 = body.get_top()[1]

        hb, ht, h = 10*s, 6*s, 4*s
        roof = Polygon(
            np.array([-hb, y0, 0]), np.array([hb, y0, 0]),
            np.array([ht, y0+h, 0]), np.array([-ht, y0+h, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )
        cap = Sector(
            radius=6*s, angle=PI, start_angle=0,
            arc_center=np.array([0, y0+h, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94
        )

        circle_center = body.get_center()+LEFT*1.55+UP*0.55
        circle = Circle(
            radius=2*s,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        ).move_to(circle_center)

        rc = body.get_center()+RIGHT*1.35+UP*0.55
        D, d = 6*s, 4*s
        rh_pts = [rc+LEFT*D/2, rc+UP*d/2, rc+RIGHT*D/2, rc+DOWN*d/2]
        rh = Polygon(
            *rh_pts,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )

        sector_center = body.get_center()+LEFT*1.40+DOWN*0.95
        sector = Sector(
            radius=4*s, angle=PI/2, start_angle=0,
            arc_center=sector_center,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )

        gap_rect = Rectangle(
            width=4*s, height=3*s,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        ).move_to(body.get_center()+RIGHT*1.55+DOWN*0.88)

        tc = body.get_center()+DOWN*0.15
        tb, th = 4*s, 3*s
        tri_pts = [
            tc+LEFT*tb/2+DOWN*th/2,
            tc+RIGHT*tb/2+DOWN*th/2,
            tc+UP*th/2,
        ]
        tri = Polygon(
            *tri_pts,
            stroke_color=BLACK, stroke_width=2.3,
            fill_color=WHITE, fill_opacity=1
        )

        verts = body.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 2*s), verts, "P5 circle"
        )
        self._assert_points_in_polygon(rh_pts, verts, "P5 rhombus")
        self._assert_points_in_polygon(
            self._sector_sample_points(sector_center, 4*s, 0, PI/2), verts, "P5 sector"
        )
        self._assert_points_in_polygon(gap_rect.get_vertices(), verts, "P5 rectangle")
        self._assert_points_in_polygon(tri_pts, verts, "P5 triangle")

        labels = VGroup(
            self.txt("20 × 12", 13, BOLD).next_to(body, DOWN, buff=0.10),
            self.txt("B=20 · b=12 · h=4", 11, BOLD).next_to(roof, RIGHT, buff=0.08),
            self.txt("semicircle r=6", 11, BOLD).next_to(cap, UP, buff=0.07),
            self.txt("r=2", 9, BOLD).move_to(circle),
            self.txt("D=6 · d=4", 8, BOLD).move_to(rh),
            self.txt("90° · r=4", 8, BOLD).move_to(sector_center+RIGHT*0.23+UP*0.18),
            self.txt("4×3", 9, BOLD).move_to(gap_rect),
            self.txt("b=4 · h=3", 8, BOLD).move_to(tri),
        )
        return VGroup(VGroup(body, roof, cap), circle, rh, sector, gap_rect, tri, labels)

    def beat_master(self) -> None:
        self.step(0)
        geo = self.master_region()
        self.swap_left(geo)
        outer, circle, rh, sector, gap_rect, tri, _ = geo
        body, roof, cap = outer

        self.swap_right(self.reason_card(
            "PROBLEM 5 · MASTER CAPSTONE · EIGHT COMPONENTS",
            [
                "Positive: rectangle + trapezoid + semicircle.",
                "Negative: circle + rhombus + sector + rectangle + triangle.",
                "This is a bookkeeping problem: calculate locally, combine globally.",
            ]
        ))
        self.wait(PAUSE_CHALLENGE)

        self.step(1)
        self.play(Indicate(body), Indicate(roof), Indicate(cap), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Indicate(circle), Indicate(rh), Indicate(sector),
                  Indicate(gap_rect), Indicate(tri), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)

        self.step(2)
        badges = self.mark_signed(
            [body, roof, cap],
            [circle, rh, sector, gap_rect, tri]
        )
        self.swap_right(self.signed_ledger(
            ["A1 rectangle", "A2 trapezoid", "A3 semicircle"],
            ["A4 circle", "A5 rhombus", "A6 sector", "A7 rectangle", "A8 triangle"]
        ))
        self.wait(PAUSE_EXPLAIN)

        self.step(3)
        self.local_calc(body, "A1 · RECTANGLE (+)",
                        [r"A_1=20(12)", r"A_1=240"], RIGHT)
        self.local_calc(roof, "A2 · TRAPEZOID (+)",
                        [r"A_2=\frac{(20+12)4}{2}", r"A_2=64"], RIGHT)
        self.local_calc(cap, "A3 · SEMICIRCLE (+)",
                        [r"A_3=\frac{\pi(6)^2}{2}", r"A_3=18\pi"], DOWN)
        self.swap_right(self.equation_card(
            "POSITIVE SUBTOTAL", r"A_{(+)}=304+18\pi", 29
        ))
        self.wait(PAUSE_WORK)

        self.local_calc(circle, "A4 · CIRCLE GAP (−)",
                        [r"A_4=\pi(2)^2", r"A_4=4\pi"], RIGHT)
        self.local_calc(rh, "A5 · RHOMBUS GAP (−)",
                        [r"A_5=\frac{6(4)}{2}", r"A_5=12"], LEFT)
        self.local_calc(sector, "A6 · 90° SECTOR GAP (−)",
                        [r"A_6=\frac{90}{360}\pi(4)^2", r"A_6=4\pi"], RIGHT)
        self.local_calc(gap_rect, "A7 · RECTANGLE GAP (−)",
                        [r"A_7=4(3)", r"A_7=12"], LEFT)
        self.local_calc(tri, "A8 · TRIANGLE GAP (−)",
                        [r"A_8=\frac{4(3)}{2}", r"A_8=6"], DOWN)
        self.swap_right(self.equation_card(
            "NEGATIVE SUBTOTAL", r"A_{(-)}=30+8\pi", 29
        ))
        self.wait(PAUSE_WORK)

        final = VGroup(
            self.math(r"A_s=(304+18\pi)-(30+8\pi)", 26),
            self.math(r"A_s=274+10\pi", 32),
            self.math(r"A_s\approx305.42\,cm^2", 31),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(final)
        self.wait(PAUSE_CHALLENGE)

        self.step(4)
        self.swap_right(self.reason_card(
            "FINAL CHECK",
            [
                "8 components counted exactly once ✓",
                "5 different negative regions handled independently ✓",
                "Exact π form retained until evaluation ✓",
                "305.42 cm² < total outside area ✓",
            ]
        ))
        self.wait(PAUSE_FINAL)
        self.play(FadeOut(badges), run_time=RUN_NORMAL)

    # ================================================================
    # CLOSING
    # ================================================================
    def closing_senior_v3(self) -> None:
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=RUN_NORMAL)

        title = self.txt("SENIOR METHOD · CONTROL THE BOOKKEEPING", 42, BOLD)
        formula = self.formula_box(
            r"A_{\rm shaded}=\sum A_{(+)}-\sum A_{(-)}",
            width=8.8, height=1.08, size=40
        )
        steps = VGroup(
            self.txt("1. Decompose before calculating.", 23, BOLD),
            self.txt("2. Give every piece an A-number.", 23, BOLD),
            self.txt("3. Mark every term + or −.", 23, BOLD),
            self.txt("4. Compute local areas one at a time.", 23, BOLD),
            self.txt("5. Build positive and negative subtotals.", 23, BOLD),
            self.txt("6. Combine once, then verify units and magnitude.", 23, BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        g = VGroup(title, formula, steps).arrange(DOWN, buff=0.25)
        self.fit(g, 13.5, 6.2)
        g.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP*0.08), run_time=RUN_SLOW)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        for line in steps:
            self.play(FadeIn(line, shift=RIGHT*0.08), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ/2)
        self.wait(PAUSE_FINAL)

    # ================================================================
    # FULL TOTAL ASSEMBLY
    # ================================================================
    def construct(self) -> None:
        self.validate_math_class2()

        self.opening_class2()
        self.formula_atlas()
        self.senior_v3_contract()
        self.build_workbench_class2()

        self._qa_problem = "senior_v3_observatory"
        self.beat_observatory()

        self._qa_problem = "senior_v3_bridge"
        self.beat_bridge()

        self._qa_problem = "senior_v3_emblem"
        self.beat_emblem()

        self._qa_problem = "senior_v3_courtyard"
        self.beat_courtyard()

        self._qa_problem = "senior_v3_master"
        self.beat_master()

        self._qa_problem = ""
        self.closing_senior_v3()


# Preview:
# manim -pql Geometry8_Shaded_Areas_Complex_Senior_V3.py \
#   Geometry8ShadedAreasComplexSeniorV3 --disable_caching
#
# Final:
# manim -pqh Geometry8_Shaded_Areas_Complex_Senior_V3.py \
#   Geometry8ShadedAreasComplexSeniorV3 --disable_caching
