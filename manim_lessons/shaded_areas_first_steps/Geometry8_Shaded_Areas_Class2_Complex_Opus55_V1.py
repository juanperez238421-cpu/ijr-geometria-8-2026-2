#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas II — Complex Figures — Opus-style V1.

Source alignment:
- Internal Geometry 8 area deck: rectangle, square, parallelogram, triangle,
  trapezoid, rhombus/kite, regular polygon, circle, semicircle, quarter circle,
  circular sector, composite figures and shaded areas.
- Preserves the Class 1 reasoning spine:
  SEE → DECOMPOSE → CHOOSE → CALCULATE → CHECK.

This class intentionally moves from simple holes to genuinely composite regions,
multiple removals and mixed formula families.
"""
from __future__ import annotations

import math
from manim import *

from Geometry8_Shaded_Areas_Opus55_V3 import Geometry8ShadedAreasOpus55V3
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import (
    BLACK_TEXT, DARK_GRAY, LIGHT_GRAY, PAPER_GRAY, SHADE,
    RUN_QUICK, RUN_NORMAL, RUN_SLOW,
    PAUSE_READ, PAUSE_EXPLAIN, PAUSE_WORK, PAUSE_CHALLENGE, PAUSE_FINAL,
)


class Geometry8ShadedAreasClass2ComplexOpus55V1(Geometry8ShadedAreasOpus55V3):
    """Second shaded-area class: complex decomposition and mixed formula families."""

    def validate_math_class2(self) -> None:
        assert math.isclose(12*6 + ((12+8)*4)/2 - 2**2 - (math.pi*2**2)/2, 108 - 2*math.pi)
        assert math.isclose(16*9 - (8*6)/2 - (6*4)/2, 108)
        assert math.isclose(10*6 + math.pi*3**2 - 4**2 - 2*((math.pi*2**2)/4), 44 + 7*math.pi)
        assert math.isclose((36*(3*math.sqrt(3)))/2 - (120/360)*math.pi*3**2, 54*math.sqrt(3) - 3*math.pi)
        assert math.isclose(
            (16*10 + ((16+10)*4)/2 + (math.pi*5**2)/2)
            - (math.pi*2**2 + (6*4)/2 + (90/360)*math.pi*3**2),
            200 + 6.25*math.pi,
        )

    def opening_class2(self) -> None:
        self.validate_math_class2()
        kicker = self.txt("GEOMETRY 8 · PERIOD III · CLASS 2", 24, BOLD, DARK_GRAY)
        title = self.txt("SHADED AREAS II", 64, BOLD)
        sub = self.txt("COMPLEX FIGURES · MULTIPLE METHODS", 32, BOLD, DARK_GRAY)
        promise = self.txt("A complex figure becomes manageable when every piece is named.", 28)
        route = self.txt("SEE → DECOMPOSE → CHOOSE → CALCULATE → CHECK", 28, BOLD)
        group = VGroup(kicker, title, sub, promise, route).arrange(DOWN, buff=0.26)
        self.fit(group, 14.2, 6.2)
        group.move_to(UP*0.10)
        self.play(FadeIn(kicker, shift=UP*0.10), run_time=RUN_NORMAL)
        self.play(Write(title), run_time=RUN_SLOW)
        self.play(FadeIn(sub), FadeIn(promise), run_time=RUN_NORMAL)
        self.play(FadeIn(route), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    def mini_formula_card(self, title: str, expr: str, note: str = "") -> VGroup:
        box = RoundedRectangle(width=3.45, height=1.65, corner_radius=0.13,
                               stroke_color=BLACK, stroke_width=1.8,
                               fill_color=WHITE, fill_opacity=1)
        tt = self.txt(title, 19, BOLD)
        eq = self.math(expr, 31)
        parts = [tt, eq]
        if note:
            parts.append(self.txt(note, 15, NORMAL, DARK_GRAY))
        content = VGroup(*parts).arrange(DOWN, buff=0.12)
        self.fit(content, 3.05, 1.28)
        content.move_to(box)
        return VGroup(box, content)

    def formula_atlas(self) -> None:
        title = self.txt("THE COMPLETE TOOLKIT USED IN THIS UNIT", 38, BOLD)
        subtitle = self.txt("Identify the figure first. The drawing decides which formula is valid.",
                            24, NORMAL, DARK_GRAY)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.12).to_edge(UP, buff=0.18)

        base = [
            ("RECTANGLE", r"A=bh", ""),
            ("SQUARE", r"A=l^2", ""),
            ("PARALLELOGRAM", r"A=bh", r"h\perp b"),
            ("TRIANGLE", r"A=\frac{bh}{2}", ""),
            ("TRAPEZOID", r"A=\frac{(B+b)h}{2}", ""),
            ("RHOMBUS / KITE", r"A=\frac{Dd}{2}", "D,d = diagonals"),
            ("REGULAR POLYGON", r"A=\frac{Pa}{2}", "a = apothem"),
            ("CIRCLE", r"A=\pi r^2", ""),
        ]
        cards = VGroup(*[self.mini_formula_card(*x) for x in base])
        cards.arrange_in_grid(rows=2, cols=4, buff=(0.18, 0.22))
        self.fit(cards, 14.4, 4.1)
        cards.move_to(DOWN*0.25)

        self.play(FadeIn(header), run_time=RUN_NORMAL)
        self.play(LaggedStart(*[FadeIn(c, shift=UP*0.06) for c in cards], lag_ratio=0.08),
                  run_time=RUN_SLOW*1.8)
        self.wait(PAUSE_WORK)

        circle_title = self.txt("CIRCLE PARTS + COMPOSITE REGIONS", 35, BOLD)
        circle_title.to_edge(UP, buff=0.24)
        circle_cards = VGroup(
            self.mini_formula_card("SEMICIRCLE", r"A=\frac{\pi r^2}{2}"),
            self.mini_formula_card("QUARTER CIRCLE", r"A=\frac{\pi r^2}{4}"),
            self.mini_formula_card("SECTOR", r"A=\frac{\theta}{360^\circ}\pi r^2"),
        ).arrange(RIGHT, buff=0.28)
        master = self.formula_box(r"A_{\rm shaded}=\sum A_{\rm added}-\sum A_{\rm removed}",
                                  width=9.2, height=1.18, size=42)
        note = self.txt("This synthesis combines the unit's two operations: build the whole, then remove gaps.",
                        22, NORMAL, DARK_GRAY)
        second = VGroup(circle_title, circle_cards, master, note).arrange(DOWN, buff=0.34)
        self.fit(second, 14.0, 6.2)
        second.move_to(ORIGIN)

        self.play(FadeOut(header), FadeOut(cards), run_time=RUN_NORMAL)
        self.play(FadeIn(circle_title), run_time=RUN_NORMAL)
        self.play(LaggedStart(*[FadeIn(c, shift=UP*0.06) for c in circle_cards], lag_ratio=0.12),
                  run_time=RUN_SLOW)
        self.play(FadeIn(master), FadeIn(note), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(second), run_time=RUN_NORMAL)

    def build_workbench_class2(self) -> None:
        super().build_workbench()
        old = self.chrome[1]
        new = self.txt("SHADED AREAS II · COMPLEX FIGURES", 34, BOLD)
        new.move_to(old).align_to(old, LEFT)
        old.become(new)

    def facade_region(self) -> VGroup:
        s = 0.34
        body = Rectangle(width=12*s, height=6*s, stroke_color=BLACK, stroke_width=3,
                         fill_color=SHADE, fill_opacity=0.94)
        y0 = body.get_top()[1]
        half_bottom, half_top, roof_h = 6*s, 4*s, 4*s
        roof = Polygon(np.array([-half_bottom, y0, 0]),
                       np.array([ half_bottom, y0, 0]),
                       np.array([ half_top, y0+roof_h, 0]),
                       np.array([-half_top, y0+roof_h, 0]),
                       stroke_color=BLACK, stroke_width=3,
                       fill_color=SHADE, fill_opacity=0.94)
        square_gap = Square(side_length=2*s, stroke_color=BLACK, stroke_width=2.4,
                            fill_color=WHITE, fill_opacity=1)
        square_gap.move_to(body.get_center()+LEFT*1.0+DOWN*0.10)
        semi_gap = Sector(radius=2*s, angle=PI, start_angle=0,
                          arc_center=np.array([0.75, y0+0.28, 0]),
                          stroke_color=BLACK, stroke_width=2.4,
                          fill_color=WHITE, fill_opacity=1)
        labels = VGroup(
            self.txt("12 cm", 19, BOLD).next_to(body, DOWN, buff=0.14),
            self.txt("6 cm", 19, BOLD).next_to(body, LEFT, buff=0.10),
            self.txt("B=12 · b=8 · h=4", 17, BOLD).next_to(roof, UP, buff=0.10),
            self.txt("2×2", 15, BOLD).move_to(square_gap),
            self.txt("r=2", 15, BOLD).move_to(semi_gap.get_center()+UP*0.12),
        )
        return VGroup(VGroup(body, roof), square_gap, semi_gap, labels)

    def parallelogram_region(self) -> VGroup:
        s = 0.31
        b, h, slant = 16*s, 9*s, 2*s
        outer = Polygon(np.array([-b/2, -h/2, 0]),
                        np.array([ b/2, -h/2, 0]),
                        np.array([ b/2+slant, h/2, 0]),
                        np.array([-b/2+slant, h/2, 0]),
                        stroke_color=BLACK, stroke_width=3,
                        fill_color=SHADE, fill_opacity=0.94)
        D, d = 8*s, 6*s
        rc = LEFT*1.15 + UP*0.20
        rhombus = Polygon(rc+LEFT*(D/2), rc+UP*(d/2), rc+RIGHT*(D/2), rc+DOWN*(d/2),
                          stroke_color=BLACK, stroke_width=2.4,
                          fill_color=WHITE, fill_opacity=1)
        tb, th = 6*s, 4*s
        tc = RIGHT*1.45 + DOWN*0.20
        triangle = Polygon(tc+LEFT*(tb/2)+DOWN*(th/2),
                           tc+RIGHT*(tb/2)+DOWN*(th/2),
                           tc+UP*(th/2),
                           stroke_color=BLACK, stroke_width=2.4,
                           fill_color=WHITE, fill_opacity=1)
        height_line = DashedLine(np.array([-b/2+slant, -h/2, 0]),
                                 np.array([-b/2+slant, h/2, 0]),
                                 color=BLACK, stroke_width=2)
        labels = VGroup(
            self.txt("b=16 cm", 18, BOLD).next_to(outer, DOWN, buff=0.12),
            self.txt("h=9 cm", 18, BOLD).next_to(height_line, LEFT, buff=0.08),
            self.txt("D=8 · d=6", 15, BOLD).move_to(rhombus),
            self.txt("b=6 · h=4", 14, BOLD).move_to(triangle),
        )
        return VGroup(outer, rhombus, triangle, height_line, labels)

    def stadium_region(self) -> VGroup:
        s = 0.36
        rect = Rectangle(width=10*s, height=6*s, stroke_color=BLACK, stroke_width=3,
                         fill_color=SHADE, fill_opacity=0.94)
        r = 3*s
        left_cap = Sector(radius=r, angle=PI, start_angle=PI/2, arc_center=rect.get_left(),
                          stroke_color=BLACK, stroke_width=3,
                          fill_color=SHADE, fill_opacity=0.94)
        right_cap = Sector(radius=r, angle=PI, start_angle=-PI/2, arc_center=rect.get_right(),
                           stroke_color=BLACK, stroke_width=3,
                           fill_color=SHADE, fill_opacity=0.94)
        square = Square(side_length=4*s, stroke_color=BLACK, stroke_width=2.4,
                        fill_color=WHITE, fill_opacity=1).move_to(rect)
        rq = 2*s
        q1 = Sector(radius=rq, angle=PI/2, start_angle=-PI/2, arc_center=rect.get_corner(UL),
                    stroke_color=BLACK, stroke_width=2.4,
                    fill_color=WHITE, fill_opacity=1)
        q2 = Sector(radius=rq, angle=PI/2, start_angle=PI/2, arc_center=rect.get_corner(DR),
                    stroke_color=BLACK, stroke_width=2.4,
                    fill_color=WHITE, fill_opacity=1)
        labels = VGroup(
            self.txt("rectangle 10×6", 18, BOLD).next_to(rect, DOWN, buff=0.12),
            self.txt("caps r=3", 17, BOLD).next_to(left_cap, LEFT, buff=0.08),
            self.txt("4×4", 15, BOLD).move_to(square),
            self.txt("quarter gaps r=2", 16, BOLD).next_to(rect, UP, buff=0.10),
        )
        return VGroup(VGroup(rect, left_cap, right_cap), square, q1, q2, labels)

    def hexagon_sector_region(self) -> VGroup:
        s = 0.43
        side = 6*s
        hexagon = RegularPolygon(n=6, radius=side, start_angle=0,
                                 stroke_color=BLACK, stroke_width=3,
                                 fill_color=SHADE, fill_opacity=0.94)
        sector = Sector(radius=3*s, angle=2*PI/3, start_angle=-PI/3,
                        arc_center=hexagon.get_center(),
                        stroke_color=BLACK, stroke_width=2.5,
                        fill_color=WHITE, fill_opacity=1)
        apothem = DashedLine(hexagon.get_center(),
                             hexagon.get_center()+UP*(3*math.sqrt(3)*s),
                             color=BLACK, stroke_width=2)
        angle_label = self.txt("120°", 16, BOLD).move_to(
            hexagon.get_center()+RIGHT*0.65+UP*0.25)
        labels = VGroup(
            self.txt("regular hexagon · side=6", 18, BOLD).next_to(hexagon, DOWN, buff=0.12),
            self.math(r"P=36\ {\rm cm}", 25).next_to(hexagon, LEFT, buff=0.10),
            self.math(r"a=3\sqrt3\ {\rm cm}", 24).next_to(apothem, RIGHT, buff=0.08),
            self.txt("sector r=3", 16, BOLD).next_to(sector, RIGHT, buff=0.08),
            angle_label,
        )
        return VGroup(hexagon, sector, apothem, labels)

    def capstone_region(self) -> VGroup:
        s = 0.255
        body = Rectangle(width=16*s, height=10*s, stroke_color=BLACK, stroke_width=3,
                         fill_color=SHADE, fill_opacity=0.94)
        y0 = body.get_top()[1]
        hb, ht, trap_h = 8*s, 5*s, 4*s
        roof = Polygon(np.array([-hb, y0, 0]), np.array([hb, y0, 0]),
                       np.array([ht, y0+trap_h, 0]), np.array([-ht, y0+trap_h, 0]),
                       stroke_color=BLACK, stroke_width=3,
                       fill_color=SHADE, fill_opacity=0.94)
        cap = Sector(radius=5*s, angle=PI, start_angle=0,
                     arc_center=np.array([0, y0+trap_h, 0]),
                     stroke_color=BLACK, stroke_width=3,
                     fill_color=SHADE, fill_opacity=0.94)
        circle = Circle(radius=2*s, stroke_color=BLACK, stroke_width=2.4,
                        fill_color=WHITE, fill_opacity=1)
        circle.move_to(body.get_center()+LEFT*1.15+UP*0.20)
        D, d = 6*s, 4*s
        rc = body.get_center()+DOWN*0.30
        rhombus = Polygon(rc+LEFT*(D/2), rc+UP*(d/2), rc+RIGHT*(D/2), rc+DOWN*(d/2),
                          stroke_color=BLACK, stroke_width=2.4,
                          fill_color=WHITE, fill_opacity=1)
        sector = Sector(radius=3*s, angle=PI/2, start_angle=PI,
                        arc_center=body.get_center()+RIGHT*1.65+DOWN*0.55,
                        stroke_color=BLACK, stroke_width=2.4,
                        fill_color=WHITE, fill_opacity=1)
        labels = VGroup(
            self.txt("16×10", 16, BOLD).next_to(body, DOWN, buff=0.12),
            self.txt("trapezoid: B=16 · b=10 · h=4", 15, BOLD).next_to(roof, RIGHT, buff=0.08),
            self.txt("semicircle r=5", 15, BOLD).next_to(cap, UP, buff=0.08),
            self.txt("circle r=2", 14, BOLD).next_to(circle, LEFT, buff=0.05),
            self.txt("rhombus D=6,d=4", 13, BOLD).next_to(rhombus, DOWN, buff=0.04),
            self.txt("90° sector r=3", 13, BOLD).next_to(sector, RIGHT, buff=0.04),
        )
        return VGroup(VGroup(body, roof, cap), circle, rhombus, sector, labels)

    def beat_facade(self) -> None:
        self.step(0)
        geo = self.facade_region()
        self.swap_left(geo)
        whole, square_gap, semi_gap, _ = geo
        self.swap_right(self.reason_card("COMPLEX EXAMPLE 1", [
            "Outside = rectangle + trapezoid.",
            "Removed = square + semicircle.",
            "One answer needs four area pieces.",
        ]))
        self.wait(PAUSE_READ)
        self.step(1)
        self.play(whole[0].animate.shift(DOWN*0.06),
                  whole[1].animate.shift(UP*0.12), run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", [
            "ADD rectangle + trapezoid.",
            "SUBTRACT square + semicircle.",
        ]))
        self.wait(PAUSE_READ)
        self.play(whole[0].animate.shift(UP*0.06),
                  whole[1].animate.shift(DOWN*0.12), run_time=RUN_NORMAL)
        self.step(2)
        self.swap_right(self.equation_card(
            "MODEL",
            r"\left[12(6)+\frac{(12+8)4}{2}\right]-\left[2^2+\frac{\pi2^2}{2}\right]",
            28))
        self.wait(PAUSE_READ)
        self.step(3)
        calc = VGroup(
            self.math(r"A_{\rm whole}=72+40=112", 30),
            self.math(r"A_{\rm gaps}=4+2\pi", 30),
            self.math(r"A_s=108-2\pi\approx101.72\,cm^2", 30),
        ).arrange(DOWN, buff=0.20)
        self.swap_right(calc)
        self.wait(PAUSE_WORK)
        self.step(4)
        self.swap_right(self.reason_card("CHECK", [
            "101.72 < 112 ✓",
            "Every removed piece is counted once.",
            "Approximation happens at the end.",
        ]))
        self.wait(PAUSE_READ)

    def beat_parallelogram(self) -> None:
        self.step(0)
        geo = self.parallelogram_region()
        self.swap_left(geo)
        outer, rhombus, triangle, height_line, _ = geo
        self.swap_right(self.reason_card("COMPLEX EXAMPLE 2", [
            "Whole: parallelogram.",
            "Gaps: rhombus + triangle.",
            "Height must be perpendicular to the base.",
        ]))
        self.wait(PAUSE_READ)
        self.step(1)
        self.play(Indicate(height_line, scale_factor=1.05),
                  Indicate(rhombus, scale_factor=1.06),
                  Indicate(triangle, scale_factor=1.06),
                  run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", [
            "Parallelogram: bh",
            "Rhombus: Dd/2",
            "Triangle: bh/2",
        ]))
        self.step(2)
        self.swap_right(self.equation_card("MODEL", r"16(9)-\frac{8(6)}2-\frac{6(4)}2", 34))
        self.step(3)
        self.swap_right(self.equation_card("CALCULATE", r"144-24-12=\boxed{108\,cm^2}", 36))
        self.wait(PAUSE_READ)
        self.step(4)
        self.swap_right(self.reason_card("CHECK", [
            "The slanted side is NOT the height.",
            "Diagonals are used for the rhombus.",
            "108 < 144 ✓",
        ]))
        self.wait(PAUSE_READ)

    def beat_stadium(self) -> None:
        self.step(0)
        geo = self.stadium_region()
        self.swap_left(geo)
        outer, square, q1, q2, _ = geo
        self.swap_right(self.reason_card("COMPLEX EXAMPLE 3", [
            "Outside = rectangle + 2 semicircles.",
            "Inside = square + 2 quarter circles.",
            "Pairing fractions can simplify the model.",
        ]))
        self.wait(PAUSE_READ)
        self.step(1)
        self.play(Indicate(outer[1], scale_factor=1.04),
                  Indicate(outer[2], scale_factor=1.04),
                  Indicate(q1, scale_factor=1.06),
                  Indicate(q2, scale_factor=1.06),
                  run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", [
            "2 semicircles → 1 full circle (r=3).",
            "2 quarter circles → 1 half circle (r=2).",
        ]))
        self.wait(PAUSE_READ)
        self.step(2)
        self.swap_right(self.equation_card(
            "MODEL",
            r"\left[10(6)+\pi3^2\right]-\left[4^2+2\left(\frac{\pi2^2}{4}\right)\right]",
            27))
        self.step(3)
        self.swap_right(self.equation_card("CALCULATE", r"44+7\pi\approx65.99\,cm^2", 36))
        self.wait(PAUSE_READ)
        self.step(4)
        self.swap_right(self.reason_card("CHECK", [
            "Exact form: 44 + 7π.",
            "No circular piece is double-counted.",
            "65.99 < outer area ✓",
        ]))
        self.wait(PAUSE_READ)

    def beat_regular_polygon(self) -> None:
        self.step(0)
        geo = self.hexagon_sector_region()
        self.swap_left(geo)
        hexagon, sector, apothem, _ = geo
        self.swap_right(self.reason_card("COMPLEX EXAMPLE 4", [
            "Whole: regular hexagon.",
            "Gap: 120° sector.",
            "Regular polygons use perimeter + apothem.",
        ]))
        self.wait(PAUSE_READ)
        self.step(1)
        self.play(Indicate(apothem, scale_factor=1.05),
                  Indicate(sector, scale_factor=1.05),
                  run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", [
            "Hexagon: A = Pa/2",
            "Sector: fraction θ/360° of a circle",
        ]))
        self.step(2)
        self.swap_right(self.equation_card(
            "MODEL",
            r"\frac{36(3\sqrt3)}2-\frac{120^\circ}{360^\circ}\pi(3)^2",
            29))
        self.step(3)
        calc = VGroup(
            self.math(r"A_{\rm hex}=54\sqrt3", 31),
            self.math(r"A_{\rm sector}=3\pi", 31),
            self.math(r"A_s=54\sqrt3-3\pi\approx84.11\,cm^2", 29),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(calc)
        self.wait(PAUSE_WORK)
        self.step(4)
        self.swap_right(self.reason_card("CHECK", [
            "Apothem is perpendicular to a side.",
            "120° = one third of a full circle.",
            "Exact form is kept before approximation.",
        ]))
        self.wait(PAUSE_READ)

    def beat_strategy_matrix(self) -> None:
        self.step(2)
        left = VGroup(
            self.txt("COMPLEX FIGURE?", 27, BOLD),
            self.txt("Ask these questions before calculating:", 21, NORMAL, DARK_GRAY),
            self.txt("1. What pieces BUILD the whole?", 22, BOLD),
            self.txt("2. What regions are REMOVED?", 22, BOLD),
            self.txt("3. Can fractions combine?", 22, BOLD),
            self.txt("4. Which measurements are perpendicular?", 22, BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        self.swap_left(left)
        cards = VGroup(
            self.reason_card("BUILD", ["Add components that belong to the outside."]),
            self.reason_card("REMOVE", ["Subtract every hole / notch / gap once."]),
            self.reason_card("SIMPLIFY", ["2 semicircles = 1 circle.", "4 quarter circles = 1 circle."]),
        ).arrange(DOWN, buff=0.12)
        self.swap_right(cards)
        self.wait(PAUSE_WORK)

    def beat_capstone(self) -> None:
        self.step(0)
        geo = self.capstone_region()
        self.swap_left(geo)
        outer, circle, rhombus, sector, _ = geo
        self.swap_right(self.reason_card("CAPSTONE · MODEL FIRST", [
            "Outside: rectangle + trapezoid + semicircle.",
            "Remove: circle + rhombus + 90° sector.",
            "Six area pieces. One coherent model.",
        ]))
        self.wait(PAUSE_CHALLENGE)
        self.step(1)
        self.play(Indicate(outer[0], scale_factor=1.01),
                  Indicate(outer[1], scale_factor=1.01),
                  Indicate(outer[2], scale_factor=1.01),
                  run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", [
            "ADD 3 outer pieces.",
            "SUBTRACT 3 internal gaps.",
            "Keep π exact until the final line.",
        ]))
        self.wait(PAUSE_READ)
        self.step(2)
        model = VGroup(
            self.math(r"A_{\rm whole}=16(10)+\frac{(16+10)4}{2}+\frac{\pi5^2}{2}", 25),
            self.math(r"A_{\rm gaps}=\pi2^2+\frac{6(4)}2+\frac{90^\circ}{360^\circ}\pi3^2", 25),
        ).arrange(DOWN, buff=0.22)
        self.swap_right(model)
        self.wait(PAUSE_WORK)
        self.step(3)
        calc = VGroup(
            self.math(r"A_{\rm whole}=212+12.5\pi", 29),
            self.math(r"A_{\rm gaps}=12+6.25\pi", 29),
            self.math(r"A_s=200+6.25\pi\approx219.63\,cm^2", 29),
        ).arrange(DOWN, buff=0.18)
        self.swap_right(calc)
        self.wait(PAUSE_WORK)
        self.step(4)
        self.swap_right(self.reason_card("VERIFY", [
            "Every component appears exactly once.",
            "Every hole has positive area.",
            "219.63 is smaller than the whole ✓",
            "Final unit: cm² ✓",
        ]))
        self.wait(PAUSE_READ)

    def closing_class2(self) -> None:
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=RUN_NORMAL)
        title = self.txt("COMPLEX ≠ RANDOM", 52, BOLD)
        sub = self.txt("Complex figures are combinations of familiar figures.",
                       30, NORMAL, DARK_GRAY)
        formula = self.formula_box(r"A_{\rm shaded}=\sum A_{\rm added}-\sum A_{\rm removed}",
                                   width=9.4, height=1.20, size=43)
        route = self.txt("IDENTIFY → DECOMPOSE → MODEL → COMPUTE → VERIFY", 27, BOLD)
        g = VGroup(title, sub, formula, route).arrange(DOWN, buff=0.32)
        self.fit(g, 13.5, 5.8)
        g.move_to(ORIGIN)
        self.play(FadeIn(title, shift=UP*0.10), run_time=RUN_SLOW)
        self.play(FadeIn(sub), FadeIn(formula), run_time=RUN_NORMAL)
        self.play(FadeIn(route), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)

    def construct(self) -> None:
        self.opening_class2()
        self.formula_atlas()
        self.build_workbench_class2()
        self.beat_facade()
        self.beat_parallelogram()
        self.beat_stadium()
        self.beat_regular_polygon()
        self.beat_strategy_matrix()
        self.beat_capstone()
        self.closing_class2()


# Preview:
# LESSON_TIME_SCALE=0.05 manim -pql Geometry8_Shaded_Areas_Class2_Complex_Opus55_V1.py \
#   Geometry8ShadedAreasClass2ComplexOpus55V1 --disable_caching
#
# Final:
# LESSON_TIME_SCALE=1.0 manim -pqh Geometry8_Shaded_Areas_Class2_Complex_Opus55_V1.py \
#   Geometry8ShadedAreasClass2ComplexOpus55V1 --format=mp4 --disable_caching
