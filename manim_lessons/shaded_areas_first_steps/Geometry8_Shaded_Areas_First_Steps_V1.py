#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Shaded Areas: First Steps

Beginner-first classroom presentation for the first contact with shaded areas.
Target: ManimCE 0.20.1, 1920x1080, 30 fps.

Pedagogical progression:
1) meaning of shaded area,
2) rectangle minus rectangle,
3) square minus rectangle,
4) one whole figure with a central gap,
5) L-shape as a missing corner,
6) guided practice,
7) three short independent problems,
8) final reproducible method.

The visual language follows the consolidated JP classroom protocol:
- white background,
- black/gray hierarchy,
- large readable typography,
- numbered section header,
- one mathematical decision at a time,
- explicit pauses,
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
MID_GRAY = "#737373"
LIGHT_GRAY = "#D9D9D9"
PAPER_GRAY = "#F4F4F4"
SHADE = "#CFCFCF"

RUN_QUICK = 0.65
RUN_NORMAL = 0.95
RUN_SLOW = 1.25
PAUSE_SHORT = 0.80
PAUSE_READ = 1.80
PAUSE_EXPLAIN = 2.80
PAUSE_WORK = 4.50
PAUSE_CHALLENGE = 6.50
PAUSE_FINAL = 5.00


class Geometry8ShadedAreasFirstStepsV1(Scene):
    """Beginner shaded-area lesson using only simple dimensions and operations."""

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

    def section_header(self, number: int, title: str, subtitle: str):
        badge = RoundedRectangle(width=0.72, height=0.52, corner_radius=0.10,
                                 stroke_color=BLACK, stroke_width=2,
                                 fill_color=WHITE, fill_opacity=1)
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

    def formula_box(self, expression: str, width=6.2, height=1.05, size=42):
        box = RoundedRectangle(width=width, height=height, corner_radius=0.12,
                               stroke_color=BLACK, stroke_width=2,
                               fill_color=PAPER_GRAY, fill_opacity=1)
        eq = self.math(expression, size)
        self.fit(eq, width - 0.45, height - 0.22)
        eq.move_to(box)
        return VGroup(box, eq)

    def note_box(self, title: str, lines: list[str], width=5.8, body_size=24):
        t = self.txt(title, 26, BOLD)
        body = VGroup(*[self.txt(line, body_size) for line in lines]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.14)
        content = VGroup(t, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        self.fit(content, width - 0.55, 3.0)
        box = RoundedRectangle(width=width,
                               height=max(1.45, content.height + 0.55),
                               corner_radius=0.12, stroke_color=BLACK,
                               stroke_width=1.8, fill_color=WHITE, fill_opacity=1)
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.28)
        return VGroup(box, content)

    def dim_label(self, text: str, position, size=25):
        label = self.txt(text, size, BOLD)
        label.move_to(position)
        return label

    def step_line(self, number: int, label: str, equation: str, y: float, result=False):
        badge = Circle(radius=0.23, stroke_color=BLACK, stroke_width=2,
                       fill_color=WHITE, fill_opacity=1)
        badge_num = self.txt(str(number), 20, BOLD).move_to(badge)
        words = self.txt(label, 25, BOLD if result else NORMAL)
        eq = self.math(equation, 36 if result else 32)
        row = VGroup(VGroup(badge, badge_num), words, eq).arrange(RIGHT, buff=0.24)
        self.fit(row, 7.0, 0.72)
        row.move_to(RIGHT * 3.65 + UP * y)
        return row

    def clear_scene(self):
        if self.mobjects:
            self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=RUN_NORMAL)

    def rectangle_with_hole(self, outer_w: float, outer_h: float,
                            hole_w: float, hole_h: float,
                            scale: float = 0.62, hole_offset=ORIGIN):
        outer = Rectangle(width=outer_w * scale, height=outer_h * scale,
                          stroke_color=BLACK, stroke_width=3,
                          fill_color=SHADE, fill_opacity=0.92)
        hole = Rectangle(width=hole_w * scale, height=hole_h * scale,
                         stroke_color=BLACK, stroke_width=3,
                         fill_color=WHITE, fill_opacity=1).move_to(
                             outer.get_center() + hole_offset)
        return VGroup(outer, hole), outer, hole

    def add_basic_dimensions(self, outer: Rectangle, w_text: str, h_text: str):
        width_label = self.dim_label(w_text, outer.get_bottom() + DOWN * 0.34)
        height_label = self.dim_label(h_text, outer.get_left() + LEFT * 0.36)
        return VGroup(width_label, height_label)

    def construct(self):
        self.cover()
        self.meaning()
        self.example_one()
        self.example_two()
        self.example_three()
        self.example_four()
        self.guided_practice()
        self.practice_ladder()
        self.checks()
        self.summary()

    def cover(self):
        course = self.txt("GEOMETRY 8", 28, BOLD, DARK_GRAY)
        title = self.txt("SHADED AREAS", 62, BOLD)
        subtitle = self.txt("FIRST STEPS", 38, BOLD, DARK_GRAY)
        promise = self.txt("Start simple: identify the whole, identify the gap, subtract.", 28)
        formula = self.formula_box(r"A_{\text{shaded}}=A_{\text{whole}}-A_{\text{unshaded}}", 8.7, 1.22, 47)
        group = VGroup(course, title, subtitle, promise, formula).arrange(DOWN, buff=0.34)
        group.move_to(ORIGIN + UP * 0.10)
        self.play(FadeIn(course, shift=DOWN * 0.12), run_time=RUN_NORMAL)
        self.play(Write(title), run_time=RUN_SLOW)
        self.play(FadeIn(subtitle), FadeIn(promise), run_time=RUN_NORMAL)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        self.clear_scene()

    def meaning(self):
        self.section_header(1, "WHAT DOES SHADED AREA MEAN?",
                            "Only the gray part counts. White gaps are not part of the answer.")
        figure, outer, hole = self.rectangle_with_hole(8, 5, 3, 2, scale=0.65)
        figure.move_to(LEFT * 3.65 + DOWN * 0.45)
        dims = self.add_basic_dimensions(outer, "8 units", "5 units")
        hole_w = self.dim_label("3", hole.get_bottom() + DOWN * 0.28, 23)
        hole_h = self.dim_label("2", hole.get_right() + RIGHT * 0.28, 23)
        dims.add(hole_w, hole_h)
        whole_tag = self.txt("WHOLE FIGURE", 24, BOLD).next_to(outer, UP, buff=0.26)
        gap_tag = self.txt("UNSHADED GAP", 22, BOLD).next_to(hole, UP, buff=0.12)
        keep = self.note_box("ONE IDEA", ["Gray = keep", "White = remove", "So we subtract."],
                             width=5.5, body_size=27).move_to(RIGHT * 3.55 + UP * 0.20)
        symbolic = self.formula_box(r"\boxed{\text{shaded}=\text{whole}-\text{gap}}", 5.7, 1.10, 39)
        symbolic.next_to(keep, DOWN, buff=0.36)
        self.play(FadeIn(outer), FadeIn(whole_tag), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(hole), FadeIn(gap_tag), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(keep), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(symbolic), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def example_one(self):
        self.section_header(2, "EXAMPLE 1 · RECTANGLE MINUS RECTANGLE",
                            "All dimensions are given. Follow three steps and stop after the units are squared.")
        figure, outer, hole = self.rectangle_with_hole(8, 5, 3, 2, scale=0.64)
        figure.move_to(LEFT * 3.80 + DOWN * 0.52)
        dims = self.add_basic_dimensions(outer, "8", "5")
        dims.add(self.dim_label("3", hole.get_bottom() + DOWN * 0.28, 23),
                 self.dim_label("2", hole.get_right() + RIGHT * 0.28, 23))
        prompt = self.txt("Find the shaded area.", 30, BOLD).next_to(figure, UP, buff=0.34)
        s1 = self.step_line(1, "Whole area", r"8\times 5=40", 1.45)
        s2 = self.step_line(2, "Gap area", r"3\times 2=6", 0.38)
        s3 = self.step_line(3, "Subtract", r"40-6=\boxed{34\ \text{units}^2}", -0.78, result=True)
        reminder = self.txt("The answer is smaller than the whole: 34 < 40 ✓", 24, BOLD)
        reminder.move_to(RIGHT * 3.60 + DOWN * 2.05)
        self.play(FadeIn(figure), FadeIn(dims), FadeIn(prompt), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(s1, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(s2, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(s3, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(reminder), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def example_two(self):
        self.section_header(3, "EXAMPLE 2 · SQUARE WITH A SMALL WHITE WINDOW",
                            "A square still uses base × height; both dimensions simply happen to be equal.")
        figure, outer, hole = self.rectangle_with_hole(6, 6, 2, 4, scale=0.62)
        figure.move_to(LEFT * 3.75 + DOWN * 0.45)
        dims = self.add_basic_dimensions(outer, "6", "6")
        dims.add(self.dim_label("2", hole.get_bottom() + DOWN * 0.28, 23),
                 self.dim_label("4", hole.get_right() + RIGHT * 0.28, 23))
        prompt = self.txt("Find the shaded area.", 30, BOLD).next_to(figure, UP, buff=0.34)
        s1 = self.step_line(1, "Whole square", r"6\times 6=36", 1.45)
        s2 = self.step_line(2, "White window", r"2\times 4=8", 0.38)
        s3 = self.step_line(3, "Subtract", r"36-8=\boxed{28\ \text{units}^2}", -0.78, result=True)
        self.play(FadeIn(figure), FadeIn(dims), FadeIn(prompt), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def example_three(self):
        self.section_header(4, "EXAMPLE 3 · A SIMPLE CENTRAL GAP",
                            "Use subtraction first. Then verify the same answer by adding the two equal shaded pieces.")
        outer = Rectangle(width=6.0, height=2.4, stroke_color=BLACK, stroke_width=3,
                          fill_color=SHADE, fill_opacity=0.92).move_to(LEFT * 3.55 + DOWN * 0.55)
        hole = Rectangle(width=1.2, height=2.4, stroke_color=BLACK, stroke_width=3,
                         fill_color=WHITE, fill_opacity=1).move_to(outer)
        dims = VGroup(self.dim_label("10", outer.get_bottom() + DOWN * 0.34),
                      self.dim_label("4", outer.get_left() + LEFT * 0.34),
                      self.dim_label("2", hole.get_bottom() + DOWN * 0.30, 23))
        method_a = self.note_box("METHOD A · SUBTRACT",
                                 ["Whole: 10 × 4 = 40", "Gap: 2 × 4 = 8", "40 − 8 = 32 units²"],
                                 width=5.9, body_size=25).move_to(RIGHT * 3.55 + UP * 0.75)
        method_b = self.note_box("METHOD B · CHECK BY ADDING",
                                 ["Left: 4 × 4 = 16", "Right: 4 × 4 = 16", "16 + 16 = 32 units²"],
                                 width=5.9, body_size=25).move_to(RIGHT * 3.55 + DOWN * 1.25)
        check = self.formula_box(r"32=32\quad \checkmark", 3.0, 0.90, 38)
        check.to_edge(DOWN, buff=0.28).shift(RIGHT * 3.55)
        self.play(FadeIn(outer), FadeIn(hole), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(method_a), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(method_b), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(check), run_time=RUN_QUICK)
        self.wait(PAUSE_EXPLAIN)
        self.clear_scene()

    def example_four(self):
        self.section_header(5, "EXAMPLE 4 · THE FIRST L-SHAPE",
                            "Do not split the L-shape yet. Enclose it in one easy rectangle and subtract the missing corner.")
        scale = 0.58
        outer = Rectangle(width=7 * scale, height=6 * scale, stroke_color=BLACK, stroke_width=3,
                          fill_color=SHADE, fill_opacity=0.92).move_to(LEFT * 3.75 + DOWN * 0.55)
        missing = Rectangle(width=3 * scale, height=2 * scale, stroke_color=BLACK, stroke_width=3,
                            fill_color=WHITE, fill_opacity=1)
        missing.align_to(outer, RIGHT).align_to(outer, UP)
        dims = VGroup(self.dim_label("7", outer.get_bottom() + DOWN * 0.34),
                      self.dim_label("6", outer.get_left() + LEFT * 0.34),
                      self.dim_label("3", missing.get_bottom() + DOWN * 0.26, 23),
                      self.dim_label("2", missing.get_left() + LEFT * 0.28, 23))
        idea = self.formula_box(r"A_L=A_{\text{outer}}-A_{\text{corner}}", 6.0, 1.0, 39)
        idea.move_to(RIGHT * 3.55 + UP * 1.55)
        s1 = self.step_line(1, "Outer rectangle", r"7\times 6=42", 0.55)
        s2 = self.step_line(2, "Missing corner", r"3\times 2=6", -0.48)
        s3 = self.step_line(3, "Subtract", r"42-6=\boxed{36\ \text{units}^2}", -1.52, result=True)
        self.play(FadeIn(outer), FadeIn(missing), FadeIn(dims), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(idea), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        for step in (s1, s2, s3):
            self.play(FadeIn(step, shift=RIGHT * 0.10), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ if step is not s3 else PAUSE_EXPLAIN)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def guided_practice(self):
        self.section_header(6, "GUIDED PRACTICE · YOU TRY FIRST",
                            "Do not calculate immediately. First point to the whole region and the white gap.")
        figure, outer, hole = self.rectangle_with_hole(9, 5, 2, 3, scale=0.64)
        figure.move_to(LEFT * 3.75 + DOWN * 0.45)
        dims = self.add_basic_dimensions(outer, "9", "5")
        dims.add(self.dim_label("2", hole.get_bottom() + DOWN * 0.28, 23),
                 self.dim_label("3", hole.get_right() + RIGHT * 0.28, 23))
        prompt = self.txt("What is the shaded area?", 33, BOLD).next_to(figure, UP, buff=0.36)
        thinking = self.note_box("YOUR 3 STEPS", ["1. Whole = ?", "2. Gap = ?", "3. Whole − gap = ?"],
                                 width=5.7, body_size=29).move_to(RIGHT * 3.55 + UP * 0.35)
        pause = self.txt("PAUSE · CALCULATE BEFORE THE REVEAL", 25, BOLD, DARK_GRAY)
        pause.move_to(RIGHT * 3.55 + DOWN * 1.55)
        self.play(FadeIn(figure), FadeIn(dims), FadeIn(prompt), run_time=RUN_NORMAL)
        self.play(FadeIn(thinking), FadeIn(pause), run_time=RUN_NORMAL)
        self.wait(PAUSE_CHALLENGE)
        answer = self.formula_box(r"9\times 5-2\times 3=45-6=\boxed{39\ \text{units}^2}", 6.3, 1.08, 38)
        answer.move_to(RIGHT * 3.55 + DOWN * 1.25)
        self.play(FadeOut(pause), FadeIn(answer), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def practice_ladder(self):
        self.section_header(7, "PRACTICE LADDER · THREE VERY SHORT PROBLEMS",
                            "Each problem uses exactly the same logic. The only change is the dimensions.")
        cards = VGroup()
        data = [("A", "6 × 4 whole", "2 × 1 gap", r"24-2=\boxed{22}"),
                ("B", "8 × 6 whole", "3 × 2 gap", r"48-6=\boxed{42}"),
                ("C", "10 × 7 whole", "4 × 3 gap", r"70-12=\boxed{58}")]
        for letter, whole, gap, result in data:
            title = self.txt(f"PROBLEM {letter}", 25, BOLD)
            l1 = self.txt(whole, 24)
            l2 = self.txt(gap, 24)
            q = self.txt("Shaded area = ?", 24, BOLD)
            ans = self.math(result, 34)
            content = VGroup(title, l1, l2, q, ans).arrange(DOWN, buff=0.17)
            box = RoundedRectangle(width=4.45, height=4.30, corner_radius=0.14,
                                   stroke_color=BLACK, stroke_width=2,
                                   fill_color=WHITE, fill_opacity=1)
            content.move_to(box)
            ans.set_opacity(0)
            cards.add(VGroup(box, content))
        cards.arrange(RIGHT, buff=0.36).move_to(DOWN * 0.45)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.12),
                  run_time=RUN_SLOW * 1.5)
        self.wait(PAUSE_CHALLENGE)
        reveal = self.txt("REVEAL", 23, BOLD, DARK_GRAY).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(reveal), run_time=RUN_QUICK)
        for card in cards:
            ans = card[1][-1]
            self.play(ans.animate.set_opacity(1), run_time=RUN_QUICK)
            self.wait(PAUSE_READ)
        self.wait(PAUSE_WORK)
        self.clear_scene()

    def checks(self):
        self.section_header(8, "THREE CHECKS BEFORE YOU WRITE THE FINAL ANSWER",
                            "These checks catch the most common beginner mistakes without adding new formulas.")
        cards = VGroup(
            self.note_box("CHECK 1 · UNITS", ["Area uses square units.", "Write units²."], 4.45, 27),
            self.note_box("CHECK 2 · SIZE", ["A removed gap must be", "smaller than the whole."], 4.45, 27),
            self.note_box("CHECK 3 · RESULT", ["If you subtract a gap,", "shaded < whole."], 4.45, 27),
        ).arrange(RIGHT, buff=0.34)
        cards.move_to(UP * 0.15)
        mistake = self.formula_box(r"40-6=34\ \text{units}^2\quad \checkmark", 5.6, 1.06, 40)
        mistake.to_edge(DOWN, buff=0.54)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.10) for c in cards], lag_ratio=0.14),
                  run_time=RUN_SLOW * 1.4)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(mistake), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        self.clear_scene()

    def summary(self):
        self.section_header(9, "THE BEGINNER METHOD",
                            "Use this same four-step route until shaded-area problems begin to feel automatic.")
        route_data = [("1", "FIND THE WHOLE", "What complete easy shape contains the shaded region?"),
                      ("2", "FIND THE GAP", "What white part must be removed?"),
                      ("3", "SUBTRACT", "Whole area − gap area"),
                      ("4", "WRITE units²", "Finish with square units and a quick size check.")]
        cards = VGroup()
        for num, title, body in route_data:
            badge = Circle(radius=0.30, stroke_color=BLACK, stroke_width=2)
            badge_num = self.txt(num, 22, BOLD).move_to(badge)
            title_mob = self.txt(title, 25, BOLD)
            body_mob = self.txt(body, 21)
            self.fit(body_mob, 5.3, 0.72)
            content = VGroup(VGroup(badge, badge_num), title_mob, body_mob).arrange(DOWN, buff=0.17)
            box = RoundedRectangle(width=6.2, height=2.05, corner_radius=0.13,
                                   stroke_color=BLACK, stroke_width=2,
                                   fill_color=WHITE, fill_opacity=1)
            content.move_to(box)
            cards.add(VGroup(box, content))
        cards.arrange_in_grid(rows=2, cols=2, buff=(0.45, 0.40)).move_to(DOWN * 0.15)
        final = self.formula_box(r"\boxed{A_{\text{shaded}}=A_{\text{whole}}-A_{\text{unshaded}}}", 8.0, 1.10, 45)
        final.to_edge(DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.11),
                  run_time=RUN_SLOW * 1.8)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(final), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        closing = self.txt("START SIMPLE. LABEL THE PARTS. CALCULATE ONE STEP AT A TIME.", 28, BOLD)
        closing.to_edge(DOWN, buff=0.18)
        self.play(FadeOut(final), FadeIn(closing), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)


# QA preview:
# manim -pql Geometry8_Shaded_Areas_First_Steps_V1.py Geometry8ShadedAreasFirstStepsV1 --disable_caching
# Final:
# manim -pqh Geometry8_Shaded_Areas_First_Steps_V1.py Geometry8ShadedAreasFirstStepsV1 --disable_caching
