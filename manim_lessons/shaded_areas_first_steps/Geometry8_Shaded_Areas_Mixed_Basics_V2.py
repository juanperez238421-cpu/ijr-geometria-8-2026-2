#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas: Mixed Basic Figures V2

A beginner-first ManimCE lesson that deliberately uses rectangles, squares,
triangles, and circles from the start. The mathematical load stays low:
recognize the whole shape, recognize the white gap, calculate both areas,
then subtract.

Target: ManimCE 0.20.1, 1920x1080, 30 fps.

Pedagogical progression
-----------------------
1. Shaded area means whole minus gap — across several shape families.
2. Quick formula toolbox: rectangle/square, triangle, circle.
3. Rectangle minus rectangle.
4. Circle minus circle (ring / annulus).
5. Square minus triangle.
6. Triangle minus triangle.
7. Square minus circle.
8. Guided mixed-shape practice.
9. Three visual practice problems: rectangle, circle, triangle.
10. Final four-step routine.

Visual protocol
---------------
- white background and grayscale hierarchy,
- large classroom typography,
- one mathematical decision at a time,
- figures on the left, explicit numbered solution on the right,
- generous pauses for student calculation,
- no decorative color dependence,
- QA-friendly LESSON_TIME_SCALE.
"""

from __future__ import annotations

import os
from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16
config.frame_height = 9
config.frame_rate = 30
config.background_color = WHITE

TIME_SCALE = float(os.getenv("LESSON_TIME_SCALE", "1.0"))

BLACK_TEXT = BLACK
DARK_GRAY = "#303030"
LIGHT_GRAY = "#D9D9D9"
PAPER_GRAY = "#F4F4F4"
SHADE = "#CFCFCF"

RUN_QUICK = 0.62
RUN_NORMAL = 0.92
RUN_SLOW = 1.18
PAUSE_READ = 1.70
PAUSE_EXPLAIN = 2.70
PAUSE_WORK = 4.20
PAUSE_CHALLENGE = 6.20
PAUSE_FINAL = 4.80


class Geometry8ShadedAreasMixedBasicsV2(Scene):
    """First shaded-area lesson with rectangles, triangles, and circles."""

    def play(self, *animations, **kwargs):
        if kwargs.get("run_time") is not None:
            kwargs["run_time"] *= TIME_SCALE
        return super().play(*animations, **kwargs)

    def wait(self, duration=DEFAULT_WAIT_TIME, *args, **kwargs):
        return super().wait(duration * TIME_SCALE, *args, **kwargs)

    def txt(self, content: str, size: int = 30, weight=NORMAL, color=BLACK_TEXT):
        return Text(content, font_size=size, weight=weight, color=color, line_spacing=0.92)

    def math(self, expression: str, size: int = 40):
        return MathTex(expression, font_size=size, color=BLACK_TEXT)

    def fit(self, mob: Mobject, max_width: float, max_height: float):
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        if mob.height > max_height:
            mob.scale_to_fit_height(max_height)
        return mob

    def clear_scene(self):
        if self.mobjects:
            self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=RUN_NORMAL)

    def section_header(self, number: int, title: str, subtitle: str):
        badge = RoundedRectangle(
            width=0.72, height=0.52, corner_radius=0.10,
            stroke_color=BLACK, stroke_width=2,
            fill_color=WHITE, fill_opacity=1,
        )
        badge_num = self.txt(f"{number:02d}", 22, BOLD).move_to(badge)
        title_mob = self.txt(title, 34, BOLD)
        self.fit(title_mob, 13.4, 0.62)
        title_row = VGroup(VGroup(badge, badge_num), title_mob).arrange(RIGHT, buff=0.24)
        title_row.to_edge(UP, buff=0.16).to_edge(LEFT, buff=0.46)
        rule = Line(LEFT * 7.45, RIGHT * 7.45, color=LIGHT_GRAY, stroke_width=2)
        rule.next_to(title_row, DOWN, buff=0.07)
        subtitle_mob = self.txt(subtitle, 21, color=DARK_GRAY)
        self.fit(subtitle_mob, 14.3, 0.58)
        subtitle_mob.next_to(rule, DOWN, buff=0.08).align_to(title_row, LEFT)
        group = VGroup(title_row, rule, subtitle_mob)
        self.add(group)
        return group

    def formula_box(self, expression: str, width=6.3, height=1.05, size=40):
        box = RoundedRectangle(
            width=width, height=height, corner_radius=0.12,
            stroke_color=BLACK, stroke_width=2,
            fill_color=PAPER_GRAY, fill_opacity=1,
        )
        eq = self.math(expression, size)
        self.fit(eq, width - 0.45, height - 0.22)
        eq.move_to(box)
        return VGroup(box, eq)

    def note_box(self, title: str, lines: list[str], width=5.8, body_size=24):
        title_mob = self.txt(title, 26, BOLD)
        body = VGroup(*[self.txt(line, body_size) for line in lines]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.14
        )
        content = VGroup(title_mob, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        self.fit(content, width - 0.55, 3.0)
        box = RoundedRectangle(
            width=width, height=max(1.45, content.height + 0.55),
            corner_radius=0.12, stroke_color=BLACK, stroke_width=1.8,
            fill_color=WHITE, fill_opacity=1,
        )
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.28)
        return VGroup(box, content)

    def step_line(self, number: int, label: str, equation: str, y: float, result=False):
        badge = Circle(radius=0.23, stroke_color=BLACK, stroke_width=2,
                       fill_color=WHITE, fill_opacity=1)
        badge_num = self.txt(str(number), 20, BOLD).move_to(badge)
        words = self.txt(label, 24, BOLD if result else NORMAL)
        eq = self.math(equation, 35 if result else 31)
        row = VGroup(VGroup(badge, badge_num), words, eq).arrange(RIGHT, buff=0.22)
        self.fit(row, 7.0, 0.72)
        row.move_to(RIGHT * 3.60 + UP * y)
        return row

    def dim_label(self, text: str, point, size=24):
        return self.txt(text, size, BOLD).move_to(point)

    def figure_panel(self, figure: Mobject, title: str):
        panel = RoundedRectangle(
            width=6.9, height=5.35, corner_radius=0.16,
            stroke_color=LIGHT_GRAY, stroke_width=2,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(LEFT * 3.75 + DOWN * 0.40)
        title_mob = self.txt(title, 26, BOLD, DARK_GRAY)
        title_mob.next_to(panel.get_top(), DOWN, buff=0.24)
        figure.move_to(panel.get_center() + DOWN * 0.28)
        return VGroup(panel, title_mob, figure)

    def rectangle_hole(self, outer_w=8, outer_h=5, hole_w=3, hole_h=2, scale=0.56):
        outer = Rectangle(
            width=outer_w * scale, height=outer_h * scale,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94,
        )
        hole = Rectangle(
            width=hole_w * scale, height=hole_h * scale,
            stroke_color=BLACK, stroke_width=3,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(outer)
        return VGroup(outer, hole), outer, hole

    def annulus(self, outer_r=2.0, inner_r=1.0):
        outer = Circle(radius=outer_r, stroke_color=BLACK, stroke_width=3,
                       fill_color=SHADE, fill_opacity=0.94)
        inner = Circle(radius=inner_r, stroke_color=BLACK, stroke_width=3,
                       fill_color=WHITE, fill_opacity=1).move_to(outer)
        return VGroup(outer, inner), outer, inner

    def triangle_hole(self, outer_base=8, outer_height=6, inner_base=4, inner_height=2, scale=0.50):
        b = outer_base * scale
        h = outer_height * scale
        outer = Polygon(
            LEFT * b / 2 + DOWN * h / 2,
            RIGHT * b / 2 + DOWN * h / 2,
            UP * h / 2,
            stroke_color=BLACK, stroke_width=3,
            fill_color=SHADE, fill_opacity=0.94,
        )
        ib = inner_base * scale
        ih = inner_height * scale
        inner = Polygon(
            LEFT * ib / 2 + DOWN * ih / 2,
            RIGHT * ib / 2 + DOWN * ih / 2,
            UP * ih / 2,
            stroke_color=BLACK, stroke_width=3,
            fill_color=WHITE, fill_opacity=1,
        ).shift(DOWN * (h * 0.08))
        return VGroup(outer, inner), outer, inner

    def square_circle_hole(self, side=8, radius=2, scale=0.48):
        outer = Square(side_length=side * scale, stroke_color=BLACK, stroke_width=3,
                       fill_color=SHADE, fill_opacity=0.94)
        hole = Circle(radius=radius * scale, stroke_color=BLACK, stroke_width=3,
                      fill_color=WHITE, fill_opacity=1).move_to(outer)
        return VGroup(outer, hole), outer, hole

    def square_triangle_hole(self, side=6, tri_base=4, tri_height=3, scale=0.54):
        outer = Square(side_length=side * scale, stroke_color=BLACK, stroke_width=3,
                       fill_color=SHADE, fill_opacity=0.94)
        b = tri_base * scale
        h = tri_height * scale
        inner = Polygon(
            LEFT * b / 2 + DOWN * h / 2,
            RIGHT * b / 2 + DOWN * h / 2,
            UP * h / 2,
            stroke_color=BLACK, stroke_width=3,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(outer)
        return VGroup(outer, inner), outer, inner

    def construct(self):
        self.cover()
        self.same_idea_many_shapes()
        self.formula_toolbox()
        self.rectangle_example()
        self.circle_example()
        self.square_triangle_example()
        self.triangle_example()
        self.square_circle_example()
        self.guided_mixed_practice()
        self.visual_practice_ladder()
        self.summary()

    def cover(self):
        course = self.txt("GEOMETRY 8", 28, BOLD, DARK_GRAY)
        title = self.txt("SHADED AREAS", 60, BOLD)
        subtitle = self.txt("BASIC FIGURES · MIXED SHAPES", 34, BOLD, DARK_GRAY)
        promise = self.txt("Rectangles, triangles and circles — one simple method.", 28)
        formula = self.formula_box(r"A_{\text{shaded}}=A_{\text{whole}}-A_{\text{gap}}", 8.3, 1.18, 46)
        group = VGroup(course, title, subtitle, promise, formula).arrange(DOWN, buff=0.34)
        group.move_to(ORIGIN + UP * 0.08)
        self.play(FadeIn(course, shift=DOWN * 0.12), run_time=RUN_NORMAL)
        self.play(Write(title), run_time=RUN_SLOW)
        self.play(FadeIn(subtitle), FadeIn(promise), run_time=RUN_NORMAL)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        self.clear_scene()

    def same_idea_many_shapes(self):
        self.section_header(1, "ONE IDEA · MANY FIGURES",
                            "The outside shape can change. The white gap can change. The logic does not change.")
        rect_fig, _, _ = self.rectangle_hole(6, 4, 2, 1.5, 0.42)
        rect_card = VGroup(self.txt("RECTANGLE", 22, BOLD), rect_fig, self.txt("whole − gap", 22)).arrange(DOWN, buff=0.22)
        ring_fig, _, _ = self.annulus(1.15, 0.52)
        ring_card = VGroup(self.txt("CIRCLE", 22, BOLD), ring_fig, self.txt("whole − gap", 22)).arrange(DOWN, buff=0.22)
        tri_fig, _, _ = self.triangle_hole(6, 4.5, 2.5, 1.3, 0.42)
        tri_card = VGroup(self.txt("TRIANGLE", 22, BOLD), tri_fig, self.txt("whole − gap", 22)).arrange(DOWN, buff=0.22)
        cards = VGroup()
        for content in (rect_card, ring_card, tri_card):
            box = RoundedRectangle(width=4.35, height=4.40, corner_radius=0.15,
                                   stroke_color=BLACK, stroke_width=2,
                                   fill_color=WHITE, fill_opacity=1)
            content.move_to(box)
            cards.add(VGroup(box, content))
        cards.arrange(RIGHT, buff=0.42).move_to(DOWN * 0.38)
        formula = self.formula_box(r"\boxed{\text{shaded}=\text{whole}-\text{unshaded gap}}", 7.2, 1.00, 38)
        formula.to_edge(DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.15),
                  run_time=RUN_SLOW * 1.7)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def formula_toolbox(self):
        self.section_header(2, "FORMULA TOOLBOX · ONLY THREE BASIC AREAS",
                            "Before subtracting, identify which formula belongs to each shape.")
        data = [
            ("RECTANGLE / SQUARE", r"A=b\times h", "Multiply base by height."),
            ("TRIANGLE", r"A=\frac{b\times h}{2}", "Multiply, then divide by 2."),
            ("CIRCLE", r"A=\pi r^2", "Use the radius, not the diameter."),
        ]
        cards = VGroup()
        for title, eq, tip in data:
            content = VGroup(self.txt(title, 24, BOLD), self.math(eq, 44), self.txt(tip, 21)).arrange(DOWN, buff=0.28)
            self.fit(content, 4.1, 2.55)
            box = RoundedRectangle(width=4.45, height=3.15, corner_radius=0.14,
                                   stroke_color=BLACK, stroke_width=2,
                                   fill_color=WHITE, fill_opacity=1)
            content.move_to(box)
            cards.add(VGroup(box, content))
        cards.arrange(RIGHT, buff=0.35).move_to(UP * 0.35)
        reminder = self.note_box("THEN DO ONE LAST ACTION",
                                 ["Area of whole figure", "− Area of white gap", "= shaded area"],
                                 width=6.4, body_size=26).to_edge(DOWN, buff=0.34)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.14),
                  run_time=RUN_SLOW * 1.6)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(reminder), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.clear_scene()

    def rectangle_example(self):
        self.section_header(3, "EXAMPLE 1 · RECTANGLE MINUS RECTANGLE",
                            "Start with the familiar case. Every dimension is given.")
        fig, outer, hole = self.rectangle_hole(8, 5, 3, 2, 0.58)
        panel = self.figure_panel(fig, "Find the gray area")
        dims = VGroup(
            self.dim_label("8", outer.get_bottom() + DOWN * 0.33),
            self.dim_label("5", outer.get_left() + LEFT * 0.34),
            self.dim_label("3", hole.get_bottom() + DOWN * 0.25, 22),
            self.dim_label("2", hole.get_right() + RIGHT * 0.25, 22),
        )
        s1 = self.step_line(1, "Whole", r"8\times5=40", 1.35)
        s2 = self.step_line(2, "Gap", r"3\times2=6", 0.28)
        s3 = self.step_line(3, "Subtract", r"40-6=\boxed{34\ \text{units}^2}", -0.85, True)
        check = self.txt("34 < 40  ✓", 25, BOLD, DARK_GRAY).move_to(RIGHT * 3.60 + DOWN * 2.05)
        self.play(FadeIn(panel), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.play(FadeIn(check), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def circle_example(self):
        self.section_header(4, "EXAMPLE 2 · CIRCLE MINUS CIRCLE",
                            "A ring is just a large circle with a smaller circular gap removed.")
        fig, outer, inner = self.annulus(1.95, 0.98)
        panel = self.figure_panel(fig, "Ring / annulus")
        center = outer.get_center()
        r_outer = Line(center, center + RIGHT * 1.95, color=BLACK, stroke_width=2)
        r_inner = Line(center, center + UP * 0.98, color=BLACK, stroke_width=2)
        r4 = self.dim_label("r = 4", r_outer.get_center() + DOWN * 0.25, 23)
        r2 = self.dim_label("r = 2", r_inner.get_center() + LEFT * 0.38, 23)
        s1 = self.step_line(1, "Large circle", r"\pi(4)^2=16\pi", 1.35)
        s2 = self.step_line(2, "Small circle", r"\pi(2)^2=4\pi", 0.28)
        s3 = self.step_line(3, "Subtract", r"16\pi-4\pi=\boxed{12\pi\ \text{units}^2}", -0.85, True)
        approx = self.txt("Exact answer first. 12π ≈ 37.7 units²", 24, BOLD, DARK_GRAY)
        approx.move_to(RIGHT * 3.60 + DOWN * 2.05)
        self.play(FadeIn(panel), Create(r_outer), FadeIn(r4), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(Create(r_inner), FadeIn(r2), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.play(FadeIn(approx), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def square_triangle_example(self):
        self.section_header(5, "EXAMPLE 3 · SQUARE MINUS TRIANGLE",
                            "The whole and the gap do not need to use the same area formula.")
        fig, outer, inner = self.square_triangle_hole(6, 4, 3, 0.58)
        panel = self.figure_panel(fig, "Square with a triangular gap")
        dims = VGroup(
            self.dim_label("6", outer.get_bottom() + DOWN * 0.31),
            self.dim_label("6", outer.get_left() + LEFT * 0.33),
            self.dim_label("b = 4", inner.get_bottom() + DOWN * 0.25, 22),
            self.dim_label("h = 3", inner.get_right() + RIGHT * 0.36, 22),
        )
        s1 = self.step_line(1, "Square", r"6\times6=36", 1.35)
        s2 = self.step_line(2, "Triangle gap", r"\frac{4\times3}{2}=6", 0.28)
        s3 = self.step_line(3, "Subtract", r"36-6=\boxed{30\ \text{units}^2}", -0.85, True)
        reminder = self.txt("Different formulas. Same subtraction rule.", 24, BOLD, DARK_GRAY)
        reminder.move_to(RIGHT * 3.60 + DOWN * 2.05)
        self.play(FadeIn(panel), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.play(FadeIn(reminder), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def triangle_example(self):
        self.section_header(6, "EXAMPLE 4 · TRIANGLE MINUS TRIANGLE",
                            "Keep the arithmetic easy: calculate each triangle separately, then subtract.")
        fig, outer, inner = self.triangle_hole(8, 6, 4, 2, 0.54)
        panel = self.figure_panel(fig, "Large triangle with a small gap")
        dims = VGroup(
            self.dim_label("b = 8", outer.get_bottom() + DOWN * 0.33),
            self.dim_label("h = 6", outer.get_left() + LEFT * 0.42),
            self.dim_label("b = 4", inner.get_bottom() + DOWN * 0.22, 21),
            self.dim_label("h = 2", inner.get_right() + RIGHT * 0.34, 21),
        )
        s1 = self.step_line(1, "Large triangle", r"\frac{8\times6}{2}=24", 1.35)
        s2 = self.step_line(2, "Small triangle", r"\frac{4\times2}{2}=4", 0.28)
        s3 = self.step_line(3, "Subtract", r"24-4=\boxed{20\ \text{units}^2}", -0.85, True)
        check = self.txt("20 < 24  ✓", 25, BOLD, DARK_GRAY).move_to(RIGHT * 3.60 + DOWN * 2.05)
        self.play(FadeIn(panel), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.play(FadeIn(check), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def square_circle_example(self):
        self.section_header(7, "EXAMPLE 5 · SQUARE MINUS CIRCLE",
                            "This is still a basic subtraction problem: one square area and one circle area.")
        fig, outer, hole = self.square_circle_hole(8, 2, 0.48)
        panel = self.figure_panel(fig, "Square with a circular opening")
        center = hole.get_center()
        radius_line = Line(center, center + RIGHT * (2 * 0.48), color=BLACK, stroke_width=2)
        dims = VGroup(
            self.dim_label("8", outer.get_bottom() + DOWN * 0.31),
            self.dim_label("8", outer.get_left() + LEFT * 0.33),
            self.dim_label("r = 2", radius_line.get_center() + DOWN * 0.27, 22),
        )
        s1 = self.step_line(1, "Square", r"8\times8=64", 1.35)
        s2 = self.step_line(2, "Circle gap", r"\pi(2)^2=4\pi", 0.28)
        s3 = self.step_line(3, "Subtract", r"64-4\pi\approx\boxed{51.4\ \text{units}^2}", -0.85, True)
        exact = self.txt("Exact form: 64 − 4π units²", 24, BOLD, DARK_GRAY)
        exact.move_to(RIGHT * 3.60 + DOWN * 2.05)
        self.play(FadeIn(panel), Create(radius_line), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.play(FadeIn(exact), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def guided_mixed_practice(self):
        self.section_header(8, "GUIDED PRACTICE · NAME THE TWO FORMULAS FIRST",
                            "Do not calculate yet. Decide which formula belongs to the whole and which belongs to the gap.")
        fig, outer, hole = self.square_circle_hole(10, 3, 0.42)
        panel = self.figure_panel(fig, "Your turn: square − circle")
        center = hole.get_center()
        radius_line = Line(center, center + RIGHT * (3 * 0.42), color=BLACK, stroke_width=2)
        dims = VGroup(
            self.dim_label("10", outer.get_bottom() + DOWN * 0.30),
            self.dim_label("10", outer.get_left() + LEFT * 0.33),
            self.dim_label("r = 3", radius_line.get_center() + DOWN * 0.26, 22),
        )
        task = self.note_box("BEFORE CALCULATING",
                             ["1. Whole formula = ?", "2. Gap formula = ?", "3. Then subtract."],
                             width=6.0, body_size=28).move_to(RIGHT * 3.55 + UP * 0.55)
        pause = self.txt("PAUSE · SOLVE IT", 26, BOLD, DARK_GRAY).move_to(RIGHT * 3.55 + DOWN * 1.40)
        self.play(FadeIn(panel), Create(radius_line), FadeIn(dims), run_time=RUN_NORMAL)
        self.play(FadeIn(task), FadeIn(pause), run_time=RUN_NORMAL)
        self.wait(PAUSE_CHALLENGE)
        answer = self.formula_box(r"10^2-\pi(3)^2=100-9\pi\approx\boxed{71.7\ \text{units}^2}",
                                  6.45, 1.13, 36).move_to(RIGHT * 3.55 + DOWN * 1.30)
        self.play(FadeOut(pause), FadeIn(answer), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def visual_practice_ladder(self):
        self.section_header(9, "PRACTICE LADDER · THREE BASIC FIGURES",
                            "Try each picture before the answer appears. Focus on choosing the correct area formula.")
        fig_a, _, _ = self.rectangle_hole(6, 3, 2, 1, 0.34)
        cont_a = VGroup(self.txt("A · 6×3 minus 2×1", 20, BOLD), fig_a,
                        self.math(r"18-2=\boxed{16}", 31).set_opacity(0)).arrange(DOWN, buff=0.24)
        fig_b, _, _ = self.annulus(1.02, 0.34)
        cont_b = VGroup(self.txt("B · R = 3, r = 1", 20, BOLD), fig_b,
                        self.math(r"9\pi-\pi=\boxed{8\pi}", 31).set_opacity(0)).arrange(DOWN, buff=0.24)
        fig_c, _, _ = self.triangle_hole(6, 5, 2, 2, 0.34)
        cont_c = VGroup(self.txt("C · b=6,h=5; gap b=2,h=2", 18, BOLD), fig_c,
                        self.math(r"15-2=\boxed{13}", 31).set_opacity(0)).arrange(DOWN, buff=0.24)
        cards = VGroup()
        for content in (cont_a, cont_b, cont_c):
            self.fit(content, 4.15, 3.70)
            box = RoundedRectangle(width=4.45, height=4.50, corner_radius=0.14,
                                   stroke_color=BLACK, stroke_width=2,
                                   fill_color=WHITE, fill_opacity=1)
            content.move_to(box)
            cards.add(VGroup(box, content))
        cards.arrange(RIGHT, buff=0.35).move_to(DOWN * 0.42)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.14),
                  run_time=RUN_SLOW * 1.7)
        self.wait(PAUSE_CHALLENGE)
        reveal = self.txt("REVEAL", 23, BOLD, DARK_GRAY).to_edge(DOWN, buff=0.22)
        self.play(FadeIn(reveal), run_time=RUN_QUICK)
        for card in cards:
            answer = card[1][-1]
            self.play(answer.animate.set_opacity(1), run_time=RUN_QUICK)
            self.wait(PAUSE_READ)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def summary(self):
        self.section_header(10, "THE SAME FOUR STEPS WORK FOR EVERY BASIC FIGURE",
                            "Rectangle, triangle or circle: identify the shapes first, then calculate.")
        route = [
            ("1", "NAME THE WHOLE", "Rectangle? triangle? circle?"),
            ("2", "NAME THE GAP", "Which shape is white / removed?"),
            ("3", "CALCULATE BOTH", "Use the correct formula for each."),
            ("4", "SUBTRACT", "Whole − gap, then write units²."),
        ]
        cards = VGroup()
        for num, title, body in route:
            badge = Circle(radius=0.29, stroke_color=BLACK, stroke_width=2)
            badge_num = self.txt(num, 22, BOLD).move_to(badge)
            title_mob = self.txt(title, 24, BOLD)
            body_mob = self.txt(body, 21)
            self.fit(body_mob, 5.2, 0.68)
            content = VGroup(VGroup(badge, badge_num), title_mob, body_mob).arrange(DOWN, buff=0.16)
            box = RoundedRectangle(width=6.15, height=1.95, corner_radius=0.13,
                                   stroke_color=BLACK, stroke_width=2,
                                   fill_color=WHITE, fill_opacity=1)
            content.move_to(box)
            cards.add(VGroup(box, content))
        cards.arrange_in_grid(rows=2, cols=2, buff=(0.45, 0.35)).move_to(UP * 0.05)
        final = self.formula_box(r"\boxed{A_{\text{shaded}}=A_{\text{whole}}-A_{\text{gap}}}",
                                 7.6, 1.05, 44).to_edge(DOWN, buff=0.28)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.12),
                  run_time=RUN_SLOW * 1.8)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(final), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        closing = self.txt("FIRST IDENTIFY THE SHAPES. THEN CHOOSE THE FORMULAS.", 28, BOLD)
        closing.to_edge(DOWN, buff=0.20)
        self.play(FadeOut(final), FadeIn(closing), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)


# QA preview:
# manim -pql Geometry8_Shaded_Areas_Mixed_Basics_V2.py Geometry8ShadedAreasMixedBasicsV2 --disable_caching
# Final:
# manim -pqh Geometry8_Shaded_Areas_Mixed_Basics_V2.py Geometry8ShadedAreasMixedBasicsV2 --disable_caching
