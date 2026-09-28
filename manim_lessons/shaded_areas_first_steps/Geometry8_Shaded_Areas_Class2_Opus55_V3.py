#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas II — Complex Figures — Opus 5.5 style V3.

Pedagogical design:
- explicit numbered solution steps,
- deliberate pauses for student prediction,
- moving-camera zooms for each local calculation,
- positive (+) and negative (-) area accounting,
- exact expressions before decimal approximation,
- full 2D area formula inventory from the internal Geometry 8 deck.

ManimCE target: 0.20.1 · 1920×1080 · 30 fps.
"""
from __future__ import annotations

import math
import os
import numpy as np
from manim import *

config.background_color = WHITE
config.frame_rate = 30

BLACK_TEXT = BLACK
DARK_GRAY = "#444444"
MID_GRAY = "#888888"
LIGHT_GRAY = "#C8C8C8"
PAPER = "#F5F5F5"
SHADE = "#C9C9C9"
SHADE_DARK = "#B4B4B4"

TIME_SCALE = float(os.getenv("LESSON_TIME_SCALE", "1.0"))

def T(seconds: float) -> float:
    return seconds * TIME_SCALE

RUN_FAST = T(0.55)
RUN_NORMAL = T(1.0)
RUN_SLOW = T(1.55)

PAUSE_SHORT = T(0.8)
PAUSE_READ = T(1.5)
PAUSE_EXPLAIN = T(2.0)
PAUSE_WORK = T(2.4)
PAUSE_CHALLENGE = T(3.2)
PAUSE_FINAL = T(3.4)


class Geometry8ShadedAreasClass2Opus55V3(MovingCameraScene):
    """Full Class 2: complex shaded areas with explicit signed-area bookkeeping."""

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_math(self) -> None:
        assert math.isclose(12*6 + ((12+8)*4)/2 - 2**2 - (math.pi*2**2)/2,
                            108 - 2*math.pi)
        assert math.isclose(16*9 - (8*6)/2 - (6*4)/2, 108)
        assert math.isclose(10*6 + math.pi*3**2 - 4**2 - 2*((math.pi*2**2)/4),
                            44 + 7*math.pi)
        assert math.isclose((36*(3*math.sqrt(3)))/2
                            - (120/360)*math.pi*3**2,
                            54*math.sqrt(3) - 3*math.pi)
        assert math.isclose(
            (16*10 + ((16+10)*4)/2 + (math.pi*5**2)/2)
            - (math.pi*2**2 + (6*4)/2 + (90/360)*math.pi*3**2),
            200 + 6.25*math.pi,
        )

    # ------------------------------------------------------------------
    # Base helpers
    # ------------------------------------------------------------------
    def txt(self, text: str, size: int = 30, weight=NORMAL, color=BLACK_TEXT) -> Text:
        return Text(text, font_size=size, weight=weight, color=color)

    def math(self, tex: str, size: int = 34) -> MathTex:
        return MathTex(tex, font_size=size, color=BLACK_TEXT)

    def fit(self, mob: Mobject, width: float, height: float) -> Mobject:
        if mob.width <= 0 or mob.height <= 0:
            return mob
        mob.scale(min(width / mob.width, height / mob.height))
        return mob

    def tag(self, text: str, *, width: float = 0.70) -> VGroup:
        box = RoundedRectangle(
            width=width, height=0.48, corner_radius=0.12,
            stroke_color=BLACK, stroke_width=2,
            fill_color=WHITE, fill_opacity=1,
        )
        lab = self.txt(text, 18, BOLD).move_to(box)
        return VGroup(box, lab)

    def sign_tag(self, sign: str, number: int) -> VGroup:
        return self.tag(f"{sign}{number}", width=0.82)

    def note_card(self, title: str, lines: list[str]) -> VGroup:
        box = RoundedRectangle(
            width=5.70, height=4.20, corner_radius=0.14,
            stroke_color=LIGHT_GRAY, stroke_width=1.8,
            fill_color=PAPER, fill_opacity=1,
        )
        title_m = self.txt(title, 22, BOLD)
        bullets = VGroup()
        for line in lines:
            dot = Dot(radius=0.045, color=BLACK)
            body = self.txt(line, 21)
            row = VGroup(dot, body).arrange(RIGHT, buff=0.12, aligned_edge=UP)
            bullets.add(row)
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        content = VGroup(title_m, bullets).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        self.fit(content, 5.15, 3.65)
        content.move_to(box)
        return VGroup(box, content)

    def calc_card(self, title: str, equations: list[str], size: int = 29) -> VGroup:
        box = RoundedRectangle(
            width=5.70, height=4.20, corner_radius=0.14,
            stroke_color=LIGHT_GRAY, stroke_width=1.8,
            fill_color=WHITE, fill_opacity=1,
        )
        title_m = self.txt(title, 21, BOLD, DARK_GRAY)
        eqs = VGroup(*[self.math(eq, size) for eq in equations])
        eqs.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        content = VGroup(title_m, eqs).arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        self.fit(content, 5.18, 3.65)
        content.move_to(box)
        return VGroup(box, content)

    def formula_card(self, title: str, expr: str) -> VGroup:
        box = RoundedRectangle(
            width=3.35, height=1.55, corner_radius=0.12,
            stroke_color=BLACK, stroke_width=1.6,
            fill_color=WHITE, fill_opacity=1,
        )
        title_m = self.txt(title, 17, BOLD, DARK_GRAY)
        eq = self.math(expr, 27)
        content = VGroup(title_m, eq).arrange(DOWN, buff=0.12)
        self.fit(content, 2.95, 1.18)
        content.move_to(box)
        return VGroup(box, content)

    def swap_right(self, mob: Mobject, run_time: float = RUN_NORMAL) -> None:
        self.fit(mob, 5.78, 4.70)
        mob.move_to(self.right_panel.get_center() + DOWN*0.07)
        if self.reasoning is None:
            self.play(FadeIn(mob, shift=UP*0.06), run_time=run_time)
        else:
            self.play(ReplacementTransform(self.reasoning, mob), run_time=run_time)
        self.reasoning = mob

    def swap_left(self, mob: Mobject, run_time: float = RUN_NORMAL) -> None:
        self.fit(mob, 6.50, 4.70)
        mob.move_to(self.left_panel.get_center() + DOWN*0.08)
        if self.geometry is None:
            self.play(FadeIn(mob, shift=UP*0.06), run_time=run_time)
        else:
            self.play(ReplacementTransform(self.geometry, mob), run_time=run_time)
        self.geometry = mob

    def set_step(self, index: int) -> None:
        self.play(self.cursor.animate.move_to(self.steps[index]), run_time=RUN_FAST)

    def zoom_to(self, target: Mobject, width: float) -> None:
        self.play(
            self.camera.frame.animate.set(width=width).move_to(target),
            run_time=RUN_SLOW,
        )

    def camera_home(self) -> None:
        self.play(
            self.camera.frame.animate.set(width=config.frame_width).move_to(ORIGIN),
            run_time=RUN_SLOW,
        )

    def flash_formula(self, target: Mobject) -> None:
        self.play(Indicate(target, scale_factor=1.05), run_time=RUN_NORMAL)

    # ------------------------------------------------------------------
    # Persistent classroom layout
    # ------------------------------------------------------------------
    def build_workbench(self) -> None:
        course = self.txt("GEOMETRY 8 · PERIOD III", 21, BOLD, DARK_GRAY)
        title = self.txt("SHADED AREAS II · COMPLEX FIGURES", 34, BOLD)
        course.to_edge(UP, buff=0.10).to_edge(LEFT, buff=0.42)
        title.next_to(course, DOWN, buff=0.03).align_to(course, LEFT)
        rule = Line(LEFT*7.45, RIGHT*7.45, color=LIGHT_GRAY, stroke_width=2)
        rule.next_to(title, DOWN, buff=0.08)

        labels = ["1 SEE", "2 DECOMPOSE", "3 MARK + / −", "4 CALCULATE", "5 CHECK"]
        self.steps = VGroup()
        for label in labels:
            box = RoundedRectangle(
                width=2.46, height=0.57, corner_radius=0.16,
                stroke_color=LIGHT_GRAY, stroke_width=1.5,
                fill_color=WHITE, fill_opacity=1,
            )
            lab = self.txt(label, 17, BOLD, DARK_GRAY).move_to(box)
            self.steps.add(VGroup(box, lab))
        self.steps.arrange(RIGHT, buff=0.12)
        self.fit(self.steps, 13.05, 0.65)
        self.steps.next_to(rule, DOWN, buff=0.10).to_edge(LEFT, buff=0.63)

        self.cursor = RoundedRectangle(
            width=self.steps[0].width + 0.10,
            height=self.steps[0].height + 0.10,
            corner_radius=0.19,
            stroke_color=BLACK, stroke_width=2.5,
            fill_opacity=0,
        ).move_to(self.steps[0])

        self.left_panel = RoundedRectangle(
            width=7.42, height=5.55, corner_radius=0.15,
            stroke_color=LIGHT_GRAY, stroke_width=1.9,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(LEFT*3.92 + DOWN*0.96)
        self.right_panel = RoundedRectangle(
            width=6.36, height=5.55, corner_radius=0.15,
            stroke_color=LIGHT_GRAY, stroke_width=1.9,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(RIGHT*3.72 + DOWN*0.96)

        lt = self.txt("GEOMETRIC MODEL", 18, BOLD, DARK_GRAY)
        rt = self.txt("STEP-BY-STEP SOLUTION", 18, BOLD, DARK_GRAY)
        lt.next_to(self.left_panel.get_top(), DOWN, buff=0.14)
        rt.next_to(self.right_panel.get_top(), DOWN, buff=0.14)

        self.chrome = VGroup(
            course, title, rule, self.steps, self.cursor,
            self.left_panel, self.right_panel, lt, rt,
        )
        self.add(self.chrome)
        self.geometry = None
        self.reasoning = None

    # ------------------------------------------------------------------
    # Opening and formula inventory
    # ------------------------------------------------------------------
    def opening(self) -> None:
        title = self.txt("SHADED AREAS II", 66, BOLD)
        sub = self.txt("COMPLEX FIGURES · EXPLICIT SOLUTIONS", 31, BOLD, DARK_GRAY)
        q = self.txt("What is added? What is removed? Which formula belongs to each piece?", 26)
        route = self.txt("SEE → DECOMPOSE → MARK + / − → CALCULATE → CHECK", 28, BOLD)
        p = self.txt("Today every local area is calculated before the final total.", 24, NORMAL, DARK_GRAY)
        group = VGroup(title, sub, q, route, p).arrange(DOWN, buff=0.26)
        self.fit(group, 14.0, 6.2)
        group.move_to(UP*0.08)
        self.play(FadeIn(title, shift=UP*0.12), run_time=RUN_NORMAL)
        self.play(Write(sub), run_time=RUN_SLOW)
        self.play(FadeIn(q), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(route), run_time=RUN_NORMAL)
        self.play(FadeIn(p), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    def formula_atlas(self) -> None:
        title = self.txt("FORMULA ATLAS · EVERYTHING ALREADY SEEN", 38, BOLD)
        subtitle = self.txt(
            "The drawing chooses the formula. The formula does not choose the drawing.",
            24, NORMAL, DARK_GRAY,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.12).to_edge(UP, buff=0.18)

        data = [
            ("RECTANGLE", r"A=bh"),
            ("SQUARE", r"A=l^2"),
            ("PARALLELOGRAM", r"A=bh"),
            ("TRIANGLE", r"A=\frac{bh}{2}"),
            ("TRAPEZOID", r"A=\frac{(B+b)h}{2}"),
            ("RHOMBUS / KITE", r"A=\frac{Dd}{2}"),
            ("REGULAR POLYGON", r"A=\frac{Pa}{2}"),
            ("CIRCLE", r"A=\pi r^2"),
            ("SEMICIRCLE", r"A=\frac{\pi r^2}{2}"),
            ("QUARTER CIRCLE", r"A=\frac{\pi r^2}{4}"),
            ("SECTOR", r"A=\frac{\theta}{360^\circ}\pi r^2"),
        ]
        cards = VGroup(*[self.formula_card(a, b) for a, b in data])
        cards.arrange_in_grid(rows=3, cols=4, buff=(0.15, 0.17))
        self.fit(cards, 14.2, 4.9)
        cards.move_to(DOWN*0.15)

        synthesis = RoundedRectangle(
            width=8.9, height=1.02, corner_radius=0.12,
            stroke_color=BLACK, stroke_width=2,
            fill_color=PAPER, fill_opacity=1,
        )
        syn_eq = self.math(r"A_{shaded}=\sum A_{(+)}-\sum A_{(-)}", 38).move_to(synthesis)
        syn = VGroup(synthesis, syn_eq).next_to(cards, DOWN, buff=0.16)

        self.play(FadeIn(header), run_time=RUN_NORMAL)
        self.play(
            LaggedStart(*[FadeIn(card, shift=UP*0.05) for card in cards], lag_ratio=0.05),
            run_time=RUN_SLOW*1.7,
        )
        self.wait(PAUSE_READ)
        self.play(FadeIn(syn, shift=UP*0.05), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(header), FadeOut(cards), FadeOut(syn), run_time=RUN_NORMAL)

    # ------------------------------------------------------------------
    # Geometry builders
    # ------------------------------------------------------------------
    def facade_model(self) -> VGroup:
        s = 0.34
        body = Rectangle(
            width=12*s, height=6*s, stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        y0 = body.get_top()[1]
        roof = Polygon(
            np.array([-6*s, y0, 0]), np.array([6*s, y0, 0]),
            np.array([4*s, y0+4*s, 0]), np.array([-4*s, y0+4*s, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        square = Square(
            side_length=2*s, stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(body.get_center()+LEFT*1.05+DOWN*0.12)
        semi = Sector(
            radius=2*s, angle=PI, start_angle=0,
            arc_center=body.get_center()+RIGHT*1.15+UP*0.50,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        labs = VGroup(
            self.txt("12 cm", 18, BOLD).next_to(body, DOWN, buff=0.12),
            self.txt("6 cm", 18, BOLD).next_to(body, LEFT, buff=0.08),
            self.txt("B=12  b=8  h=4", 16, BOLD).next_to(roof, UP, buff=0.08),
            self.txt("2×2", 14, BOLD).move_to(square),
            self.txt("r=2", 14, BOLD).move_to(semi.get_center()+UP*0.10),
        )
        return VGroup(VGroup(body, roof), square, semi, labs)

    def parallelogram_model(self) -> VGroup:
        s = 0.31
        b, h, sl = 16*s, 9*s, 2*s
        outer = Polygon(
            np.array([-b/2, -h/2, 0]),
            np.array([ b/2, -h/2, 0]),
            np.array([ b/2+sl, h/2, 0]),
            np.array([-b/2+sl, h/2, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        height = DashedLine(
            np.array([-b/2+sl, -h/2, 0]),
            np.array([-b/2+sl,  h/2, 0]),
            color=BLACK, stroke_width=2,
        )
        D, d = 8*s, 6*s
        rc = LEFT*1.20 + UP*0.22
        rhombus = Polygon(
            rc+LEFT*(D/2), rc+UP*(d/2), rc+RIGHT*(D/2), rc+DOWN*(d/2),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        tb, th = 6*s, 4*s
        tc = RIGHT*1.45+DOWN*0.18
        tri = Polygon(
            tc+LEFT*(tb/2)+DOWN*(th/2),
            tc+RIGHT*(tb/2)+DOWN*(th/2),
            tc+UP*(th/2),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        labs = VGroup(
            self.txt("b=16 cm", 17, BOLD).next_to(outer, DOWN, buff=0.11),
            self.txt("h=9 cm", 17, BOLD).next_to(height, LEFT, buff=0.07),
            self.txt("D=8, d=6", 14, BOLD).move_to(rhombus),
            self.txt("b=6, h=4", 13, BOLD).move_to(tri),
        )
        return VGroup(outer, rhombus, tri, height, labs)

    def stadium_model(self) -> VGroup:
        s = 0.36
        rect = Rectangle(
            width=10*s, height=6*s, stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        r = 3*s
        lcap = Sector(
            radius=r, angle=PI, start_angle=PI/2, arc_center=rect.get_left(),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        rcap = Sector(
            radius=r, angle=PI, start_angle=-PI/2, arc_center=rect.get_right(),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        square = Square(
            side_length=4*s, stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(rect)
        qr = 2*s
        q1 = Sector(
            radius=qr, angle=PI/2, start_angle=-PI/2, arc_center=rect.get_corner(UL),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        q2 = Sector(
            radius=qr, angle=PI/2, start_angle=PI/2, arc_center=rect.get_corner(DR),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        labs = VGroup(
            self.txt("rectangle 10×6", 16, BOLD).next_to(rect, DOWN, buff=0.11),
            self.txt("2 semicircles  r=3", 15, BOLD).next_to(rect, UP, buff=0.09),
            self.txt("4×4", 14, BOLD).move_to(square),
            self.txt("quarter gaps r=2", 14, BOLD).next_to(rect, RIGHT, buff=0.07),
        )
        return VGroup(VGroup(rect, lcap, rcap), square, q1, q2, labs)

    def hexagon_model(self) -> VGroup:
        s = 0.43
        side = 6*s
        hexagon = RegularPolygon(
            n=6, radius=side, start_angle=0,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.95,
        )
        sector = Sector(
            radius=3*s, angle=2*PI/3, start_angle=-PI/3,
            arc_center=hexagon.get_center(),
            stroke_color=BLACK, stroke_width=2.5,
            fill_color=WHITE, fill_opacity=1,
        )
        apothem = DashedLine(
            hexagon.get_center(),
            hexagon.get_center()+UP*(3*math.sqrt(3)*s),
            color=BLACK, stroke_width=2,
        )
        labs = VGroup(
            self.txt("regular hexagon · side=6", 16, BOLD).next_to(hexagon, DOWN, buff=0.10),
            self.math(r"P=36", 23).next_to(hexagon, LEFT, buff=0.09),
            self.math(r"a=3\sqrt3", 22).next_to(apothem, RIGHT, buff=0.06),
            self.txt("120° · r=3", 14, BOLD).next_to(sector, RIGHT, buff=0.06),
        )
        return VGroup(hexagon, sector, apothem, labs)

    def capstone_model(self) -> VGroup:
        s = 0.255
        body = Rectangle(
            width=16*s, height=10*s, stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE_DARK, fill_opacity=0.95,
        )
        y0 = body.get_top()[1]
        roof = Polygon(
            np.array([-8*s, y0, 0]), np.array([8*s, y0, 0]),
            np.array([5*s, y0+4*s, 0]), np.array([-5*s, y0+4*s, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE_DARK, fill_opacity=0.95,
        )
        cap = Sector(
            radius=5*s, angle=PI, start_angle=0,
            arc_center=np.array([0, y0+4*s, 0]),
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE_DARK, fill_opacity=0.95,
        )
        circle = Circle(
            radius=2*s, stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(body.get_center()+LEFT*1.15+UP*0.18)
        D, d = 6*s, 4*s
        rc = body.get_center()+DOWN*0.32
        rhombus = Polygon(
            rc+LEFT*(D/2), rc+UP*(d/2), rc+RIGHT*(D/2), rc+DOWN*(d/2),
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        sector = Sector(
            radius=3*s, angle=PI/2, start_angle=PI,
            arc_center=body.get_center()+RIGHT*1.65+DOWN*0.55,
            stroke_color=BLACK, stroke_width=2.4,
            fill_color=WHITE, fill_opacity=1,
        )
        labs = VGroup(
            self.txt("16×10", 15, BOLD).next_to(body, DOWN, buff=0.10),
            self.txt("trapezoid B=16, b=10, h=4", 13, BOLD).next_to(roof, RIGHT, buff=0.06),
            self.txt("semicircle r=5", 13, BOLD).next_to(cap, UP, buff=0.06),
            self.txt("circle r=2", 12, BOLD).next_to(circle, LEFT, buff=0.04),
            self.txt("rhombus D=6,d=4", 11, BOLD).next_to(rhombus, DOWN, buff=0.03),
            self.txt("90° sector r=3", 11, BOLD).next_to(sector, RIGHT, buff=0.03),
        )
        return VGroup(VGroup(body, roof, cap), circle, rhombus, sector, labs)

    # ------------------------------------------------------------------
    # Explicit calculation choreography
    # ------------------------------------------------------------------
    def mark_signed_pieces(self, positive: list[Mobject], negative: list[Mobject]) -> VGroup:
        tags = VGroup()
        for i, mob in enumerate(positive, start=1):
            tg = self.sign_tag("+", i)
            tg.next_to(mob, UP, buff=0.06)
            tags.add(tg)
        for j, mob in enumerate(negative, start=len(positive)+1):
            tg = self.sign_tag("−", j)
            tg.next_to(mob, DOWN, buff=0.06)
            tags.add(tg)
        self.play(LaggedStart(*[FadeIn(x, scale=0.85) for x in tags], lag_ratio=0.14), run_time=RUN_SLOW)
        return tags

    def local_calculation(
        self,
        target: Mobject,
        title: str,
        progressive_lines: list[str],
        *,
        zoom_width: float = 5.0,
        pause: float = PAUSE_WORK,
        formula_size: int = 29,
    ) -> None:
        self.zoom_to(target, zoom_width)
        self.flash_formula(target)
        self.zoom_to(self.right_panel, 7.4)
        for i in range(1, len(progressive_lines)+1):
            card = self.calc_card(title, progressive_lines[:i], size=formula_size)
            self.swap_right(card, run_time=RUN_NORMAL)
            self.wait(pause if i == len(progressive_lines) else PAUSE_READ)
        self.camera_home()

    # ------------------------------------------------------------------
    # Example 1 — facade
    # ------------------------------------------------------------------
    def example_facade(self) -> None:
        self.set_step(0)
        geo = self.facade_model()
        whole, square, semi, _ = geo
        body, roof = whole
        self.swap_left(geo)
        self.swap_right(self.note_card("EXAMPLE 1 · COMPOSITE FACADE", [
            "The outside is not one formula.",
            "Two pieces build the whole.",
            "Two white regions are removed.",
            "We will calculate four areas separately.",
        ]))
        self.wait(PAUSE_EXPLAIN)

        checkpoint = self.note_card("PAUSE · PREDICT", [
            "Which regions should be positive (+)?",
            "Which regions should be negative (−)?",
            "Which formula belongs to each region?",
        ])
        self.swap_right(checkpoint)
        self.wait(PAUSE_CHALLENGE)

        self.set_step(1)
        self.play(body.animate.shift(DOWN*0.08), roof.animate.shift(UP*0.14), run_time=RUN_NORMAL)
        self.wait(PAUSE_SHORT)
        self.play(body.animate.shift(UP*0.08), roof.animate.shift(DOWN*0.14), run_time=RUN_NORMAL)
        self.play(Indicate(square, scale_factor=1.08), Indicate(semi, scale_factor=1.08), run_time=RUN_NORMAL)
        self.swap_right(self.note_card("DECOMPOSE", [
            "A₁ rectangle: 12 × 6",
            "A₂ trapezoid: B=12, b=8, h=4",
            "A₃ square gap: side 2",
            "A₄ semicircle gap: r=2",
        ]))
        self.wait(PAUSE_READ)

        self.set_step(2)
        tags = self.mark_signed_pieces([body, roof], [square, semi])
        self.swap_right(self.calc_card("SIGNED AREA MODEL", [
            r"A_s=(+A_1)+(+A_2)+(-A_3)+(-A_4)",
            r"A_s=A_1+A_2-A_3-A_4",
        ], size=28))
        self.wait(PAUSE_WORK)

        self.set_step(3)
        self.local_calculation(body, "STEP 4A · POSITIVE AREA A₁", [
            r"A_1=bh",
            r"A_1=12(6)",
            r"A_1=72\,cm^2",
        ], zoom_width=5.0)

        self.local_calculation(roof, "STEP 4B · POSITIVE AREA A₂", [
            r"A_2=\frac{(B+b)h}{2}",
            r"A_2=\frac{(12+8)(4)}{2}",
            r"A_2=\frac{80}{2}=40\,cm^2",
        ], zoom_width=5.0)

        self.swap_right(self.calc_card("POSITIVE SUBTOTAL", [
            r"A_{(+)}=A_1+A_2",
            r"A_{(+)}=72+40",
            r"A_{(+)}=112\,cm^2",
        ], size=30))
        self.zoom_to(self.right_panel, 7.4)
        self.wait(PAUSE_WORK)
        self.camera_home()

        self.local_calculation(square, "STEP 4C · NEGATIVE AREA A₃", [
            r"A_3=l^2",
            r"A_3=2^2",
            r"A_3=4\,cm^2",
        ], zoom_width=3.7)

        self.local_calculation(semi, "STEP 4D · NEGATIVE AREA A₄", [
            r"A_4=\frac{\pi r^2}{2}",
            r"A_4=\frac{\pi(2)^2}{2}",
            r"A_4=2\pi\,cm^2",
        ], zoom_width=3.7)

        self.swap_right(self.calc_card("NEGATIVE SUBTOTAL", [
            r"A_{(-)}=A_3+A_4",
            r"A_{(-)}=4+2\pi",
        ], size=30))
        self.zoom_to(self.right_panel, 7.4)
        self.wait(PAUSE_WORK)
        self.camera_home()

        self.swap_right(self.calc_card("FINAL COMBINATION", [
            r"A_s=A_{(+)}-A_{(-)}",
            r"A_s=112-(4+2\pi)",
            r"A_s=108-2\pi",
            r"A_s\approx101.72\,cm^2",
        ], size=29))
        self.zoom_to(self.right_panel, 7.2)
        self.wait(PAUSE_CHALLENGE)
        self.camera_home()

        self.set_step(4)
        self.swap_right(self.note_card("CHECK", [
            "101.72 < 112, so removing area decreased the total.",
            "π stayed exact until the final approximation.",
            "Every component was counted once.",
            "The final unit is cm².",
        ]))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(tags), run_time=RUN_FAST)

    # ------------------------------------------------------------------
    # Example 2 — parallelogram / rhombus / triangle
    # ------------------------------------------------------------------
    def example_parallelogram(self) -> None:
        self.set_step(0)
        geo = self.parallelogram_model()
        outer, rhombus, tri, height, _ = geo
        self.swap_left(geo)
        self.swap_right(self.note_card("EXAMPLE 2 · DIFFERENT FORMULA FAMILIES", [
            "Whole: parallelogram.",
            "Gap 1: rhombus.",
            "Gap 2: triangle.",
            "The vertical dashed segment is the height.",
        ]))
        self.wait(PAUSE_EXPLAIN)

        self.set_step(1)
        self.play(Indicate(height, scale_factor=1.04), run_time=RUN_NORMAL)
        self.swap_right(self.note_card("IMPORTANT HEIGHT CHECK", [
            "Parallelogram area uses perpendicular height.",
            "Do NOT use the slanted side as h.",
            "Rhombus area uses diagonals D and d.",
        ]))
        self.wait(PAUSE_READ)

        self.set_step(2)
        tags = self.mark_signed_pieces([outer], [rhombus, tri])
        self.swap_right(self.calc_card("SIGNED AREA MODEL", [
            r"A_s=(+A_1)+(-A_2)+(-A_3)",
            r"A_s=A_1-A_2-A_3",
        ], size=29))
        self.wait(PAUSE_WORK)

        self.set_step(3)
        self.local_calculation(outer, "STEP 4A · PARALLELOGRAM", [
            r"A_1=bh",
            r"A_1=16(9)",
            r"A_1=144\,cm^2",
        ], zoom_width=5.6)

        self.local_calculation(rhombus, "STEP 4B · RHOMBUS GAP", [
            r"A_2=\frac{Dd}{2}",
            r"A_2=\frac{8(6)}{2}",
            r"A_2=24\,cm^2",
        ], zoom_width=3.8)

        self.local_calculation(tri, "STEP 4C · TRIANGLE GAP", [
            r"A_3=\frac{bh}{2}",
            r"A_3=\frac{6(4)}{2}",
            r"A_3=12\,cm^2",
        ], zoom_width=3.8)

        self.swap_right(self.calc_card("FINAL COMBINATION", [
            r"A_s=144-24-12",
            r"A_s=120-12",
            r"A_s=\boxed{108\,cm^2}",
        ], size=31))
        self.zoom_to(self.right_panel, 7.3)
        self.wait(PAUSE_WORK)
        self.camera_home()

        self.set_step(4)
        self.swap_right(self.note_card("CHECK", [
            "108 < 144 ✓",
            "The slanted side was never used as height.",
            "The rhombus used diagonals, not side length.",
        ]))
        self.wait(PAUSE_READ)
        self.play(FadeOut(tags), run_time=RUN_FAST)

    # ------------------------------------------------------------------
    # Example 3 — stadium / circular fractions
    # ------------------------------------------------------------------
    def example_stadium(self) -> None:
        self.set_step(0)
        geo = self.stadium_model()
        outer, square, q1, q2, _ = geo
        rect, lcap, rcap = outer
        self.swap_left(geo)
        self.swap_right(self.note_card("EXAMPLE 3 · CIRCLE FRACTIONS", [
            "Outside = rectangle + two semicircles.",
            "Inside = square + two quarter circles.",
            "Fractions can be combined before calculating.",
        ]))
        self.wait(PAUSE_EXPLAIN)

        self.set_step(1)
        self.play(Indicate(lcap), Indicate(rcap), run_time=RUN_NORMAL)
        self.swap_right(self.calc_card("SIMPLIFY THE POSITIVE CIRCULAR PART", [
            r"2\left(\frac{\pi r^2}{2}\right)=\pi r^2",
            r"2\ \text{semicircles}=1\ \text{circle}",
        ], size=28))
        self.wait(PAUSE_WORK)
        self.play(Indicate(q1), Indicate(q2), run_time=RUN_NORMAL)
        self.swap_right(self.calc_card("SIMPLIFY THE NEGATIVE CIRCULAR PART", [
            r"2\left(\frac{\pi r^2}{4}\right)=\frac{\pi r^2}{2}",
            r"2\ \text{quarter circles}=1\ \text{semicircle}",
        ], size=27))
        self.wait(PAUSE_WORK)

        self.set_step(2)
        tags = self.mark_signed_pieces([rect, lcap, rcap], [square, q1, q2])
        self.swap_right(self.calc_card("SIGNED AREA MODEL", [
            r"A_s=+A_{rect}+A_{2semi}-A_{sq}-A_{2quarter}",
        ], size=27))
        self.wait(PAUSE_READ)

        self.set_step(3)
        self.local_calculation(rect, "STEP 4A · RECTANGLE", [
            r"A_1=10(6)",
            r"A_1=60\,cm^2",
        ], zoom_width=4.8)

        self.local_calculation(VGroup(lcap, rcap), "STEP 4B · TWO SEMICIRCLES", [
            r"A_2=\pi(3)^2",
            r"A_2=9\pi\,cm^2",
        ], zoom_width=5.6)

        self.local_calculation(square, "STEP 4C · SQUARE GAP", [
            r"A_3=4^2",
            r"A_3=16\,cm^2",
        ], zoom_width=3.8)

        self.local_calculation(VGroup(q1, q2), "STEP 4D · TWO QUARTER-CIRCLE GAPS", [
            r"A_4=2\left(\frac{\pi(2)^2}{4}\right)",
            r"A_4=2\pi\,cm^2",
        ], zoom_width=4.4)

        self.swap_right(self.calc_card("FINAL COMBINATION", [
            r"A_s=(60+9\pi)-(16+2\pi)",
            r"A_s=44+7\pi",
            r"A_s\approx65.99\,cm^2",
        ], size=29))
        self.zoom_to(self.right_panel, 7.3)
        self.wait(PAUSE_CHALLENGE)
        self.camera_home()

        self.set_step(4)
        self.swap_right(self.note_card("CHECK", [
            "Circular fractions were combined correctly.",
            "Exact form 44 + 7π is preserved.",
            "The approximation appears only at the end.",
        ]))
        self.wait(PAUSE_READ)
        self.play(FadeOut(tags), run_time=RUN_FAST)

    # ------------------------------------------------------------------
    # Example 4 — regular polygon and sector
    # ------------------------------------------------------------------
    def example_hexagon(self) -> None:
        self.set_step(0)
        geo = self.hexagon_model()
        hexagon, sector, apothem, _ = geo
        self.swap_left(geo)
        self.swap_right(self.note_card("EXAMPLE 4 · REGULAR POLYGON + SECTOR", [
            "Whole: regular hexagon.",
            "Gap: 120° circular sector.",
            "The hexagon uses perimeter and apothem.",
        ]))
        self.wait(PAUSE_EXPLAIN)

        self.set_step(1)
        self.play(Indicate(apothem, scale_factor=1.05), run_time=RUN_NORMAL)
        self.swap_right(self.note_card("DECOMPOSE THE FORMULAS", [
            "Hexagon: A = Pa / 2",
            "Sector: A = (θ / 360°)πr²",
            "120° is one third of a full circle.",
        ]))
        self.wait(PAUSE_READ)

        self.set_step(2)
        tags = self.mark_signed_pieces([hexagon], [sector])
        self.swap_right(self.calc_card("SIGNED AREA MODEL", [
            r"A_s=(+A_1)+(-A_2)",
            r"A_s=A_{hex}-A_{sector}",
        ], size=29))
        self.wait(PAUSE_READ)

        self.set_step(3)
        self.local_calculation(hexagon, "STEP 4A · REGULAR HEXAGON", [
            r"P=6(6)=36\,cm",
            r"a=3\sqrt3\,cm",
            r"A_1=\frac{Pa}{2}",
            r"A_1=\frac{36(3\sqrt3)}{2}=54\sqrt3\,cm^2",
        ], zoom_width=5.5, formula_size=27)

        self.local_calculation(sector, "STEP 4B · 120° SECTOR GAP", [
            r"A_2=\frac{120^\circ}{360^\circ}\pi(3)^2",
            r"A_2=\frac13(9\pi)",
            r"A_2=3\pi\,cm^2",
        ], zoom_width=3.8)

        self.swap_right(self.calc_card("FINAL COMBINATION", [
            r"A_s=54\sqrt3-3\pi",
            r"A_s\approx84.11\,cm^2",
        ], size=30))
        self.zoom_to(self.right_panel, 7.3)
        self.wait(PAUSE_WORK)
        self.camera_home()

        self.set_step(4)
        self.swap_right(self.note_card("CHECK", [
            "Apothem is perpendicular to a side.",
            "120° = 1/3 of 360°.",
            "The sector is subtracted because it is a gap.",
        ]))
        self.wait(PAUSE_READ)
        self.play(FadeOut(tags), run_time=RUN_FAST)

    # ------------------------------------------------------------------
    # Capstone — six pieces
    # ------------------------------------------------------------------
    def capstone(self) -> None:
        self.set_step(0)
        geo = self.capstone_model()
        outer, circle, rhombus, sector, _ = geo
        body, roof, cap = outer
        self.swap_left(geo)
        self.swap_right(self.note_card("CAPSTONE · SIX AREA PIECES", [
            "Positive: rectangle + trapezoid + semicircle.",
            "Negative: circle + rhombus + 90° sector.",
            "Do not write one giant equation immediately.",
            "Calculate locally, subtotal, then combine.",
        ]))
        self.wait(PAUSE_CHALLENGE)

        self.set_step(1)
        self.play(
            Indicate(body), Indicate(roof), Indicate(cap),
            run_time=RUN_NORMAL,
        )
        self.wait(PAUSE_SHORT)
        self.play(
            Indicate(circle), Indicate(rhombus), Indicate(sector),
            run_time=RUN_NORMAL,
        )
        self.swap_right(self.note_card("DECOMPOSITION COMPLETE", [
            "A₁ rectangle 16×10",
            "A₂ trapezoid B=16, b=10, h=4",
            "A₃ semicircle r=5",
            "A₄ circle r=2",
            "A₅ rhombus D=6, d=4",
            "A₆ sector 90°, r=3",
        ]))
        self.wait(PAUSE_EXPLAIN)

        self.set_step(2)
        tags = self.mark_signed_pieces([body, roof, cap], [circle, rhombus, sector])
        self.swap_right(self.calc_card("SIGNED AREA LEDGER", [
            r"A_s=+A_1+A_2+A_3-A_4-A_5-A_6",
            r"A_s=A_{(+)}-A_{(-)}",
        ], size=28))
        self.wait(PAUSE_WORK)

        self.set_step(3)
        self.local_calculation(body, "STEP 4A · + RECTANGLE", [
            r"A_1=16(10)",
            r"A_1=160\,cm^2",
        ], zoom_width=4.8)

        self.local_calculation(roof, "STEP 4B · + TRAPEZOID", [
            r"A_2=\frac{(16+10)(4)}{2}",
            r"A_2=\frac{104}{2}",
            r"A_2=52\,cm^2",
        ], zoom_width=4.8)

        self.local_calculation(cap, "STEP 4C · + SEMICIRCLE", [
            r"A_3=\frac{\pi(5)^2}{2}",
            r"A_3=\frac{25\pi}{2}",
            r"A_3=12.5\pi\,cm^2",
        ], zoom_width=4.4)

        self.swap_right(self.calc_card("POSITIVE SUBTOTAL", [
            r"A_{(+)}=160+52+12.5\pi",
            r"A_{(+)}=212+12.5\pi",
        ], size=30))
        self.zoom_to(self.right_panel, 7.3)
        self.wait(PAUSE_WORK)
        self.camera_home()

        self.local_calculation(circle, "STEP 4D · − CIRCLE GAP", [
            r"A_4=\pi(2)^2",
            r"A_4=4\pi\,cm^2",
        ], zoom_width=3.6)

        self.local_calculation(rhombus, "STEP 4E · − RHOMBUS GAP", [
            r"A_5=\frac{6(4)}{2}",
            r"A_5=12\,cm^2",
        ], zoom_width=3.6)

        self.local_calculation(sector, "STEP 4F · − 90° SECTOR GAP", [
            r"A_6=\frac{90^\circ}{360^\circ}\pi(3)^2",
            r"A_6=\frac14(9\pi)",
            r"A_6=2.25\pi\,cm^2",
        ], zoom_width=3.6)

        self.swap_right(self.calc_card("NEGATIVE SUBTOTAL", [
            r"A_{(-)}=4\pi+12+2.25\pi",
            r"A_{(-)}=12+6.25\pi",
        ], size=30))
        self.zoom_to(self.right_panel, 7.3)
        self.wait(PAUSE_WORK)
        self.camera_home()

        checkpoint = self.note_card("PAUSE · BEFORE THE FINAL LINE", [
            "Positive subtotal: 212 + 12.5π",
            "Negative subtotal: 12 + 6.25π",
            "What should survive after subtraction?",
        ])
        self.swap_right(checkpoint)
        self.wait(PAUSE_CHALLENGE)

        self.swap_right(self.calc_card("FINAL COMBINATION", [
            r"A_s=(212+12.5\pi)-(12+6.25\pi)",
            r"A_s=212+12.5\pi-12-6.25\pi",
            r"A_s=200+6.25\pi",
            r"A_s\approx219.63\,cm^2",
        ], size=28))
        self.zoom_to(self.right_panel, 7.2)
        self.wait(PAUSE_CHALLENGE)
        self.camera_home()

        self.set_step(4)
        self.swap_right(self.note_card("FINAL CHECK", [
            "Every positive component appears exactly once.",
            "Every removed region is subtracted exactly once.",
            "The shaded result is smaller than the complete outside.",
            "Exact form appears before decimal approximation.",
            "Final unit: cm².",
        ]))
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeOut(tags), run_time=RUN_FAST)

    # ------------------------------------------------------------------
    # Closing
    # ------------------------------------------------------------------
    def closing(self) -> None:
        self.camera_home()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=RUN_NORMAL)
        title = self.txt("COMPLEX DOES NOT MEAN RANDOM", 50, BOLD)
        subtitle = self.txt("It means several familiar areas combined with signs.", 28, NORMAL, DARK_GRAY)
        eq = self.math(r"A_{shaded}=\sum A_{(+)}-\sum A_{(-)}", 46)
        steps = VGroup(
            self.txt("1 · Identify every geometric piece.", 26, BOLD),
            self.txt("2 · Mark what is added (+) and removed (−).", 26, BOLD),
            self.txt("3 · Calculate one local area at a time.", 26, BOLD),
            self.txt("4 · Form subtotals.", 26, BOLD),
            self.txt("5 · Combine and verify.", 26, BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        group = VGroup(title, subtitle, eq, steps).arrange(DOWN, buff=0.28)
        self.fit(group, 13.5, 6.2)
        group.move_to(ORIGIN)
        self.play(FadeIn(title, shift=UP*0.10), run_time=RUN_SLOW)
        self.play(FadeIn(subtitle), run_time=RUN_NORMAL)
        self.play(Write(eq), run_time=RUN_SLOW)
        self.play(
            LaggedStart(*[FadeIn(row, shift=RIGHT*0.08) for row in steps], lag_ratio=0.17),
            run_time=RUN_SLOW*1.4,
        )
        self.wait(PAUSE_FINAL)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.validate_math()
        self.opening()
        self.formula_atlas()
        self.build_workbench()
        self.example_facade()
        self.example_parallelogram()
        self.example_stadium()
        self.example_hexagon()
        self.capstone()
        self.closing()


# Preview:
# LESSON_TIME_SCALE=0.05 manim -pql Geometry8_Shaded_Areas_Class2_Opus55_V3.py \
#   Geometry8ShadedAreasClass2Opus55V3 --disable_caching
#
# Final:
# LESSON_TIME_SCALE=1.0 manim -pqh Geometry8_Shaded_Areas_Class2_Opus55_V3.py \
#   Geometry8ShadedAreasClass2Opus55V3 --format=mp4 --disable_caching
