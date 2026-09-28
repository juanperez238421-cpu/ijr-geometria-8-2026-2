#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas — Opus-style V3.

Builds on Mixed Basics V2 but changes the pedagogy from repeated
"whole-gap" slides to a persistent reasoning system:
SEE → DECOMPOSE → CHOOSE → CALCULATE → CHECK.

The same workbench remains on screen while geometry and equations transform.
"""
from __future__ import annotations

import math
from manim import *
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import (
    Geometry8ShadedAreasMixedBasicsV2,
    BLACK_TEXT, DARK_GRAY, LIGHT_GRAY, PAPER_GRAY, SHADE,
    RUN_QUICK, RUN_NORMAL, RUN_SLOW,
    PAUSE_READ, PAUSE_EXPLAIN, PAUSE_WORK, PAUSE_CHALLENGE, PAUSE_FINAL,
)


class Geometry8ShadedAreasOpus55V3(Geometry8ShadedAreasMixedBasicsV2):
    """Continuous, strategy-first shaded-area masterclass."""

    def validate_math(self):
        assert 8 * 5 - 3 * 2 == 34
        assert 5 * 9 + 7 * 9 == 108
        assert 18 * 9 - 6 * 9 == 108
        assert math.isclose(8**2 - math.pi * 2**2, 64 - 4 * math.pi)
        assert math.isclose(12*8 + 12*5/2 - 3*5 - math.pi*2**2, 111 - 4*math.pi)
        assert math.isclose(14*10 - 4*2 - 0.5*math.pi*3**2, 132 - 4.5*math.pi)

    # ------------------------------------------------------------------
    # Persistent workbench
    # ------------------------------------------------------------------
    def build_workbench(self):
        course = self.txt("GEOMETRY 8 · PERIOD III", 22, BOLD, DARK_GRAY)
        title = self.txt("SHADED AREAS · SIMPLE → COMPLEX", 34, BOLD)
        course.to_edge(UP, buff=0.10).to_edge(LEFT, buff=0.40)
        title.next_to(course, DOWN, buff=0.03).align_to(course, LEFT)
        rule = Line(LEFT*7.5, RIGHT*7.5, color=LIGHT_GRAY, stroke_width=2)
        rule.next_to(title, DOWN, buff=0.08)

        labels = ["SEE", "DECOMPOSE", "CHOOSE", "CALCULATE", "CHECK"]
        self.steps = VGroup()
        for label in labels:
            box = RoundedRectangle(width=2.18, height=0.58, corner_radius=0.18,
                                   stroke_color=LIGHT_GRAY, stroke_width=1.6,
                                   fill_color=WHITE, fill_opacity=1)
            t = self.txt(label, 20, NORMAL, DARK_GRAY).move_to(box)
            self.steps.add(VGroup(box, t))
        self.steps.arrange(RIGHT, buff=0.16)
        self.fit(self.steps, 12.8, 0.65)
        self.steps.next_to(rule, DOWN, buff=0.10).to_edge(LEFT, buff=0.72)
        self.cursor = RoundedRectangle(width=self.steps[0].width+0.10,
                                       height=self.steps[0].height+0.10,
                                       corner_radius=0.21,
                                       stroke_color=BLACK, stroke_width=2.5,
                                       fill_opacity=0).move_to(self.steps[0])

        self.left_panel = RoundedRectangle(width=7.35, height=5.55, corner_radius=0.16,
                                           stroke_color=LIGHT_GRAY, stroke_width=2,
                                           fill_color=WHITE, fill_opacity=1)
        self.right_panel = RoundedRectangle(width=6.45, height=5.55, corner_radius=0.16,
                                            stroke_color=LIGHT_GRAY, stroke_width=2,
                                            fill_color=WHITE, fill_opacity=1)
        self.left_panel.move_to(LEFT*3.95 + DOWN*0.95)
        self.right_panel.move_to(RIGHT*3.68 + DOWN*0.95)
        lt = self.txt("VISUAL MODEL", 19, BOLD, DARK_GRAY).next_to(self.left_panel.get_top(), DOWN, buff=0.15)
        rt = self.txt("REASONING", 19, BOLD, DARK_GRAY).next_to(self.right_panel.get_top(), DOWN, buff=0.15)
        self.chrome = VGroup(course, title, rule, self.steps, self.cursor,
                             self.left_panel, self.right_panel, lt, rt)
        self.add(self.chrome)
        self.geometry = None
        self.reasoning = None

    def step(self, n: int):
        self.play(self.cursor.animate.move_to(self.steps[n]), run_time=RUN_QUICK)

    def place_left(self, mob):
        self.fit(mob, 6.45, 4.55)
        mob.move_to(self.left_panel.get_center() + DOWN*0.08)
        return mob

    def place_right(self, mob):
        self.fit(mob, 5.70, 4.65)
        mob.move_to(self.right_panel.get_center() + DOWN*0.06)
        return mob

    def swap_left(self, mob):
        mob = self.place_left(mob)
        if self.geometry is None:
            self.play(FadeIn(mob, shift=UP*0.08), run_time=RUN_NORMAL)
        else:
            self.play(ReplacementTransform(self.geometry, mob), run_time=RUN_NORMAL)
        self.geometry = mob

    def swap_right(self, mob):
        mob = self.place_right(mob)
        if self.reasoning is None:
            self.play(FadeIn(mob, shift=UP*0.08), run_time=RUN_NORMAL)
        else:
            self.play(ReplacementTransform(self.reasoning, mob), run_time=RUN_NORMAL)
        self.reasoning = mob

    def reason_card(self, title, lines, height=2.4):
        return self.note_box(title, lines, width=5.65, body_size=23)

    def equation_card(self, title, expr, size=37):
        card = self.formula_box(expr, width=5.75, height=1.15, size=size)
        tt = self.txt(title, 22, BOLD, DARK_GRAY).next_to(card, UP, buff=0.18)
        return VGroup(tt, card)

    # ------------------------------------------------------------------
    # New geometry
    # ------------------------------------------------------------------
    def segmented_region(self):
        h = 3.05
        scale = 5.8/18
        widths = [5*scale, 6*scale, 7*scale]
        rects = VGroup(); x = -sum(widths)/2
        for i,w in enumerate(widths):
            r = Rectangle(width=w, height=h, stroke_color=BLACK, stroke_width=3,
                          fill_color=SHADE if i != 1 else WHITE,
                          fill_opacity=0.94 if i != 1 else 1)
            r.move_to(RIGHT*(x+w/2)); x += w; rects.add(r)
        labels = VGroup(
            self.txt("5 cm", 21, BOLD).next_to(rects[0], UP, buff=0.10),
            self.txt("6 cm", 21, BOLD).next_to(rects[1], UP, buff=0.10),
            self.txt("7 cm", 21, BOLD).next_to(rects[2], UP, buff=0.10),
            self.txt("height = 9 cm", 21, BOLD).next_to(rects, DOWN, buff=0.14),
        )
        return VGroup(rects, labels)

    def house_region(self):
        s = 0.34
        body = Rectangle(width=12*s, height=8*s, stroke_color=BLACK, stroke_width=3,
                         fill_color=SHADE, fill_opacity=0.94)
        roof = Polygon(body.get_corner(UL), body.get_corner(UR), body.get_top()+UP*(5*s),
                       stroke_color=BLACK, stroke_width=3,
                       fill_color=SHADE, fill_opacity=0.94)
        door = Rectangle(width=3*s, height=5*s, stroke_color=BLACK, stroke_width=2.6,
                         fill_color=WHITE, fill_opacity=1)
        door.move_to(body.get_bottom()+UP*door.height/2+LEFT*0.75)
        window = Circle(radius=2*s, stroke_color=BLACK, stroke_width=2.6,
                        fill_color=WHITE, fill_opacity=1)
        window.move_to(body.get_center()+RIGHT*1.05+UP*0.28)
        labels = VGroup(
            self.txt("12 cm", 20, BOLD).next_to(body, DOWN, buff=0.24),
            self.txt("8 cm", 20, BOLD).next_to(body, LEFT, buff=0.11),
            self.txt("roof h = 5 cm", 18, BOLD).next_to(roof, RIGHT, buff=0.12),
            self.txt("3 × 5", 16, BOLD).move_to(door.get_center()),
            self.txt("r = 2", 16, BOLD).move_to(window.get_center()),
        )
        return VGroup(VGroup(body, roof), door, window, labels)

    def challenge_region(self):
        sx, sy = 5.5/14, 3.7/10
        outer = Rectangle(width=14*sx, height=10*sy, stroke_color=BLACK, stroke_width=3,
                          fill_color="#B9B9B9", fill_opacity=0.94)
        center = Rectangle(width=4*sx, height=2*sy, stroke_color=BLACK, stroke_width=2.5,
                           fill_color=WHITE, fill_opacity=1).move_to(outer)
        r = 3*min(sx,sy)
        # True quarter-circle cutouts, not full circles centered at the corners.
        q1 = Sector(
            outer_radius=r, inner_radius=0, angle=PI/2, start_angle=-PI/2,
            arc_center=outer.get_corner(UL),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        q2 = Sector(
            outer_radius=r, inner_radius=0, angle=PI/2, start_angle=PI/2,
            arc_center=outer.get_corner(DR),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        labels = VGroup(
            self.txt("14 cm", 20, BOLD).next_to(outer, DOWN, buff=0.12),
            self.txt("10 cm", 20, BOLD).next_to(outer, LEFT, buff=0.11),
            self.txt("4 × 2", 17, BOLD).next_to(center, UP, buff=0.07),
            self.txt("2 quarter-circle gaps · r = 3", 17, BOLD).next_to(outer, UP, buff=0.18),
        )
        return VGroup(outer, center, q1, q2, labels)

    # ------------------------------------------------------------------
    # Continuous lesson beats
    # ------------------------------------------------------------------
    def opening_v3(self):
        self.validate_math()
        title = self.txt("SHADED AREAS", 66, BOLD)
        sub = self.txt("The hard part is choosing the model — not memorizing a formula.", 30, NORMAL, DARK_GRAY)
        path = self.txt("SEE → DECOMPOSE → CHOOSE → CALCULATE → CHECK", 29, BOLD)
        g = VGroup(title, sub, path).arrange(DOWN, buff=0.30).move_to(UP*0.15)
        self.play(FadeIn(title, shift=UP*0.10), run_time=RUN_NORMAL)
        self.play(Write(sub), run_time=RUN_SLOW)
        self.play(FadeIn(path), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(g), run_time=RUN_NORMAL)
        self.build_workbench()

    def beat_simple(self):
        self.step(0)
        fig, outer, gap = self.rectangle_hole(8,5,3,2,0.58)
        dims = VGroup(self.dim_label("8", outer.get_bottom()+DOWN*0.30),
                      self.dim_label("5", outer.get_left()+LEFT*0.31),
                      self.dim_label("3", gap.get_bottom()+DOWN*0.22,22),
                      self.dim_label("2", gap.get_right()+RIGHT*0.22,22))
        geo = VGroup(fig,dims)
        self.swap_left(geo)
        self.swap_right(self.reason_card("SEE THE REGION", ["One whole rectangle.", "One white gap.", "Gray is what remains."]))
        self.wait(PAUSE_READ)

        self.step(1)
        self.play(Indicate(outer, scale_factor=1.02), Indicate(gap, scale_factor=1.08), run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", ["WHOLE: 8×5", "GAP: 3×2"]))
        self.wait(PAUSE_READ)

        self.step(2)
        ghost = gap.copy().set_opacity(0.65); self.add(ghost)
        self.play(ghost.animate.shift(RIGHT*2.0+UP*0.65), run_time=RUN_SLOW)
        self.swap_right(self.equation_card("CHOOSE", r"A_s=A_{whole}-A_{gap}"))
        self.wait(PAUSE_READ); self.play(FadeOut(ghost), run_time=RUN_QUICK)

        self.step(3)
        self.swap_right(self.equation_card("CALCULATE", r"8(5)-3(2)=40-6=34", 39))
        self.wait(PAUSE_READ)

        self.step(4)
        self.swap_right(self.reason_card("CHECK", ["34 < 40 ✓", "Removed area decreases the total.", "Answer uses units²."]))
        self.wait(PAUSE_READ)

    def beat_two_methods(self):
        self.step(0)
        geo = self.segmented_region(); self.swap_left(geo)
        rects = geo[0]
        self.swap_right(self.reason_card("ONE REGION · TWO MODELS", ["ADD shaded pieces", "or", "SUBTRACT the white gap"]))
        self.wait(PAUSE_READ)

        self.step(1)
        self.play(rects[0].animate.shift(LEFT*0.20), rects[2].animate.shift(RIGHT*0.20), run_time=RUN_NORMAL)
        self.step(2)
        self.swap_right(self.reason_card("METHOD A · ADD", ["Use when shaded pieces are easy to isolate."]))
        self.step(3)
        self.swap_right(self.equation_card("ADD", r"5(9)+7(9)=45+63=108\,cm^2", 34))
        self.wait(PAUSE_READ)

        self.play(rects[0].animate.shift(RIGHT*0.20), rects[2].animate.shift(LEFT*0.20), run_time=RUN_NORMAL)
        self.step(2)
        self.swap_right(self.reason_card("METHOD B · SUBTRACT", ["Use when the missing region is simpler."]))
        self.step(3)
        self.swap_right(self.equation_card("SUBTRACT", r"18(9)-6(9)=162-54=108\,cm^2", 34))
        self.wait(PAUSE_READ)

        self.step(4)
        self.swap_right(self.reason_card("CHECK", ["Both methods = 108 cm².", "Different path. Same geometry."]))
        self.wait(PAUSE_READ)

    def beat_mixed(self):
        self.step(0)
        geo, square, circle = self.square_circle_hole(8,2,0.48)
        radius = Line(circle.get_center(), circle.get_center()+RIGHT*(2*0.48), color=BLACK, stroke_width=2)
        labels = VGroup(self.dim_label("side=8", square.get_bottom()+DOWN*0.28,22),
                        self.dim_label("r=2", radius.get_center()+UP*0.22,21))
        model = VGroup(geo,radius,labels); self.swap_left(model)
        self.swap_right(self.reason_card("MIXED FORMULAS", ["Whole: square", "Gap: circle", "Different formulas can share one model."]))
        self.wait(PAUSE_READ)

        self.step(1); self.play(Indicate(square), Indicate(circle), run_time=RUN_NORMAL)
        self.step(2); self.swap_right(self.equation_card("CHOOSE", r"A_s=s^2-\pi r^2"))
        self.step(3); self.swap_right(self.equation_card("CALCULATE", r"64-4\pi\approx51.43\,units^2", 34))
        self.step(4); self.swap_right(self.reason_card("CHECK", ["Exact form: 64−4π", "Approximate only at the end.", "Radius ≠ diameter."]))
        self.wait(PAUSE_READ)

    def beat_complex(self):
        self.step(0)
        geo = self.house_region(); self.swap_left(geo)
        body, door, window, _ = geo
        self.swap_right(self.reason_card("COMPLEX REGION", ["Now even the outside is composite.", "Build the whole before subtracting gaps."]))
        self.wait(PAUSE_READ)

        self.step(1)
        self.play(body[0].animate.shift(DOWN*0.08), body[1].animate.shift(UP*0.18), run_time=RUN_NORMAL)
        self.swap_right(self.reason_card("DECOMPOSE", ["Whole = rectangle + triangle roof", "Gaps = door + circular window"]))
        self.wait(PAUSE_READ)
        self.play(body[0].animate.shift(UP*0.08), body[1].animate.shift(DOWN*0.18), run_time=RUN_NORMAL)

        self.step(2)
        self.swap_right(self.equation_card("MODEL", r"(A_r+A_t)-(A_d+A_c)", 39))
        self.step(3)
        eqs = VGroup(self.math(r"A_{whole}=12(8)+\frac{12(5)}2=126",31),
                      self.math(r"A_{gaps}=3(5)+\pi(2)^2=15+4\pi",31),
                      self.math(r"A_s=111-4\pi\approx98.43\,cm^2",31)).arrange(DOWN,buff=0.20)
        self.swap_right(eqs); self.wait(PAUSE_WORK)

        self.step(4)
        self.swap_right(self.reason_card("CHECK", ["ADD what belongs to the whole.", "Subtract every removed region.", "98.43 < 126 ✓"]))
        self.wait(PAUSE_READ)

    def beat_strategy_map(self):
        self.step(2)
        cards = VGroup(
            self.reason_card("IF SHADED PIECES ARE SIMPLE", ["ADD them."]),
            self.reason_card("IF GAPS ARE SIMPLE", ["SUBTRACT them."]),
            self.reason_card("IF OUTSIDE IS COMPOSITE", ["Build whole, then remove gaps."]),
        ).arrange(DOWN,buff=0.16)
        self.swap_right(cards)
        tri = Polygon(LEFT*2.2+DOWN*1.15, RIGHT*2.2+DOWN*1.15, UP*1.65,
                      stroke_color=BLACK, stroke_width=3, fill_color=SHADE, fill_opacity=0.94)
        gap = Rectangle(width=1.1,height=0.8,stroke_color=BLACK,stroke_width=2.5,
                        fill_color=WHITE,fill_opacity=1).move_to(tri.get_center()+DOWN*0.55)
        self.swap_left(VGroup(tri,gap,self.txt("Strategy before arithmetic",23,BOLD).next_to(tri,DOWN,buff=0.16)))
        self.wait(PAUSE_WORK)

    def beat_challenge(self):
        self.step(0)
        geo = self.challenge_region(); self.swap_left(geo)
        self.swap_right(self.reason_card("CHALLENGE · THINK FIRST", ["Outer: 14×10", "Center gap: 4×2", "Two quarter-circle gaps: r=3", "Write the model before numbers."]))
        self.wait(PAUSE_CHALLENGE)

        self.step(1); self.play(Indicate(geo[0]),Indicate(geo[1]),Indicate(geo[2]),Indicate(geo[3]),run_time=RUN_NORMAL)
        self.step(2); self.swap_right(self.equation_card("MODEL", r"14(10)-4(2)-2\left(\frac{\pi3^2}{4}\right)",31))
        self.step(3); self.swap_right(self.equation_card("CALCULATE", r"132-4.5\pi\approx117.86\,cm^2",34))
        self.step(4); self.swap_right(self.reason_card("CHECK", ["117.86 < 140 ✓", "Removed area > 0 ✓", "Square units ✓"]))
        self.wait(PAUSE_READ)

    def close_v3(self):
        self.step(4)
        self.swap_left(self.txt("MODEL THE REGION — THEN CALCULATE", 28, BOLD))
        self.swap_right(self.reason_card("THE HABIT TO KEEP", ["1. Identify.", "2. Decompose.", "3. Choose ADD / SUBTRACT / both.", "4. Calculate only what the model needs.", "5. Check units and reasonableness."]))
        self.wait(PAUSE_FINAL)
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=RUN_NORMAL)
        final = VGroup(self.txt("SHADED AREA IS A MODELING PROBLEM", 48, BOLD),
                       self.txt("not a memorization problem", 32, NORMAL, DARK_GRAY),
                       self.txt("SEE → DECOMPOSE → CHOOSE → CALCULATE → CHECK", 28, BOLD)).arrange(DOWN,buff=0.30)
        final.move_to(ORIGIN)
        self.play(FadeIn(final,shift=UP*0.10),run_time=RUN_SLOW)
        self.wait(PAUSE_FINAL)

    def construct(self):
        self.opening_v3()
        self.beat_simple()
        self.beat_two_methods()
        self.beat_mixed()
        self.beat_complex()
        self.beat_strategy_map()
        self.beat_challenge()
        self.close_v3()


# Preview:
# LESSON_TIME_SCALE=0.05 manim -pql Geometry8_Shaded_Areas_Opus55_V3.py Geometry8ShadedAreasOpus55V3 --disable_caching
# Final:
# LESSON_TIME_SCALE=1.0 manim -pqh Geometry8_Shaded_Areas_Opus55_V3.py Geometry8ShadedAreasOpus55V3 --format=mp4 --disable_caching
