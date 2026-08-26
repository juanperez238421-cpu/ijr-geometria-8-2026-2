#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Measurements to pi + mixed circle workshop.

Target: Manim Community Edition 0.20.x + jp_classroom_style.py
Final render:
    manim -pqh Geometry8_Circle_Pi_Mixed_Workshop.py \
        Geometry8CirclePiMixedWorkshop --format=mp4 --disable_caching --fps 30
"""
from __future__ import annotations

import math

from circle_classroom_style import *


MEASUREMENTS = [
    ("Bottle cap", 4.0, 12.6),
    ("Cup rim", 8.0, 25.1),
    ("Plate", 20.0, 62.8),
]


class Geometry8CirclePiMixedWorkshop(JPMathClassroomScene):
    """Empirical pi discovery followed by direct, inverse, area and mixed exercises."""

    def validate_lesson_data(self) -> None:
        ratios = [c / d for _, d, c in MEASUREMENTS]
        assert 3.13 < ratios[0] < 3.16
        assert 3.13 < ratios[1] < 3.16
        assert 3.13 < ratios[2] < 3.16
        assert_close(14 * math.pi, 43.982297150257104, label="circumference d14")
        assert_close(31.42 / math.pi, 10.000900243663837, label="inverse diameter")
        assert_close(math.pi * 6**2, 113.09733552923255, label="area r6")
        assert_close(math.pi * 4.5**2, 63.61725123519331, label="area d9")
        assert_close(2 * math.pi * 6, 37.69911184307752, label="mixed circumference")

    def construct(self) -> None:
        self.standard_opening(
            "GEOMETRY 8 · CIRCLES",
            "FROM MEASUREMENTS TO π · MIXED WORKSHOP",
            "Measure, divide C by d, recognize π, then solve circumference, radius, diameter and area problems.",
            "Choose the quantity first: boundary, radius/diameter relation, or region.",
        )
        self.measurements_to_pi()
        self.formalize_formulas()
        self.exercise_circumference_from_diameter()
        self.exercise_inverse_from_circumference()
        self.exercise_area_from_radius()
        self.exercise_area_from_diameter()
        self.exercise_mixed_circle()
        self.final_decision_map()

    def measurements_to_pi(self) -> None:
        self.set_header(1, "MEASURE THREE ROUND OBJECTS",
                        "For each object, compare circumference C with diameter d by calculating the ratio C/d.")
        rows = []
        for name, d, c in MEASUREMENTS:
            rows.append([name, f"{d:.1f}", f"{c:.1f}", f"{c/d:.2f}"])
        table = self.build_table(headers=("Object", r"d\ (cm)", r"C\ (cm)", r"C/d"), body_rows=rows,
                                 column_widths=(3.6, 2.4, 2.4, 2.6), math_columns=(1, 2, 3),
                                 row_height=0.82, header_height=0.88, body_font_size=31, header_font_size=28)
        table.group.move_to(UP * 0.20)
        self.assert_content_safe(table.group, "measurement table")
        self.animate_table_rows(table, pause=PAUSE_READ)
        self.play(self.shade_cells(table, [(1, 3), (2, 3), (3, 3)]), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        conclusion = self.formula_panel(r"\frac{C}{d}\approx 3.14\approx \pi", width=7.0, height=1.15, font_size=58)
        conclusion.to_edge(DOWN, buff=0.34)
        self.play(FadeIn(conclusion), run_time=RUN_NORMAL)
        self.wait(PAUSE_SUMMARY)
        self.focus_on(conclusion, width=7.8, pause=PAUSE_EXPLAIN)
        self.clear_stage()

    def formalize_formulas(self) -> None:
        self.set_header(2, "TURN THE CONSTANT RATIO INTO FORMULAS",
                        "Because C/d is approximately π, circumference can be written using diameter or radius.")
        circle = Circle(radius=1.65, stroke_color=BLACK_LINE, stroke_width=3.0)
        diameter = Line(circle.get_left(), circle.get_right(), color=BLACK_LINE, stroke_width=3.0)
        radius = Line(circle.get_center(), circle.get_top(), color=BLACK_LINE, stroke_width=3.0)
        dlab = self.math(r"d", 45).next_to(diameter, UP, buff=0.10)
        rlab = self.math(r"r", 45).next_to(radius, RIGHT, buff=0.10)
        panel = self.figure_panel(VGroup(circle, diameter, radius, dlab, rlab), width=5.8, height=4.5,
                                  title="RADIUS AND DIAMETER")
        formulas = VGroup(
            self.formula_panel(r"\pi\approx\frac{C}{d}", width=6.0, height=0.95, font_size=50),
            self.formula_panel(r"C=\pi d=2\pi r", width=6.0, height=0.95, font_size=52),
            self.formula_panel(r"d=2r\qquad r=\frac d2", width=6.0, height=0.95, font_size=49),
            self.formula_panel(r"A=\pi r^2", width=6.0, height=0.95, font_size=54),
        ).arrange(DOWN, buff=0.18)
        layout = self.split_layout(panel.group, formulas, left_width=6.1, right_width=6.25, max_height=4.9, center_y=-0.33)
        self.assert_content_safe(layout.group, "formula summary")
        self.play(FadeIn(panel.group), run_time=RUN_NORMAL)
        for formula in formulas:
            self.play(FadeIn(formula), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ)
        self.wait(PAUSE_WORK)
        self.clear_stage()

    def exercise_layout(self, prompt: str, given_tex: str, solution_lines: list[str], answer_tex: str, label: str) -> None:
        prompt_panel = self.note_panel(prompt, ["Copy the data first.", "Choose the formula before substituting."],
                                       width=5.7, title_size=30, body_size=27)
        given_panel = self.formula_panel(given_tex, width=5.7, height=1.15, font_size=50)
        left = VGroup(prompt_panel, given_panel).arrange(DOWN, buff=0.30)
        stack = self.equation_stack(solution_lines, sizes=[47] * len(solution_lines), max_width=6.4, max_height=3.7)
        answer = self.formula_panel(answer_tex, width=6.2, height=1.08, font_size=50)
        right = VGroup(stack, answer).arrange(DOWN, buff=0.28)
        layout = self.split_layout(left, right, left_width=6.0, right_width=6.35, max_height=4.95, center_y=-0.34)
        self.assert_content_safe(layout.group, label)
        self.play(FadeIn(left), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)
        self.animate_equation_stack(stack, pause=PAUSE_READ)
        self.play(FadeIn(answer), run_time=RUN_NORMAL)
        self.wait(PAUSE_SUMMARY)

    def exercise_circumference_from_diameter(self) -> None:
        self.set_header(3, "EXERCISE 1 · PERIMETER / CIRCUMFERENCE FROM DIAMETER",
                        "A circle has diameter 14 cm. Find its circumference. Remember: perimeter of a circle = circumference.")
        self.exercise_layout("FIND C", r"d=14\,\mathrm{cm}",
                             [r"C=\pi d", r"C=\pi(14)=14\pi\,\mathrm{cm}", r"C\approx 43.98\,\mathrm{cm}"],
                             r"\boxed{C\approx 43.98\,\mathrm{cm}}", "exercise 1 layout")
        self.clear_stage()

    def exercise_inverse_from_circumference(self) -> None:
        self.set_header(4, "EXERCISE 2 · FIND DIAMETER AND RADIUS FROM CIRCUMFERENCE",
                        "A circle has circumference 31.42 cm. Work backward to find d, then divide by 2 to find r.")
        self.exercise_layout("FIND d AND r", r"C=31.42\,\mathrm{cm}",
                             [r"C=\pi d\Rightarrow d=\frac{C}{\pi}",
                              r"d=\frac{31.42}{\pi}\approx 10.00\,\mathrm{cm}",
                              r"r=\frac d2\approx 5.00\,\mathrm{cm}"],
                             r"\boxed{d\approx10.00\,\mathrm{cm},\ r\approx5.00\,\mathrm{cm}}", "exercise 2 layout")
        self.clear_stage()

    def exercise_area_from_radius(self) -> None:
        self.set_header(5, "EXERCISE 3 · AREA FROM RADIUS",
                        "A circle has radius 6 cm. Find the area and check that the final units are square units.")
        self.exercise_layout("FIND A", r"r=6\,\mathrm{cm}",
                             [r"A=\pi r^2", r"A=\pi(6)^2=36\pi\,\mathrm{cm}^2", r"A\approx113.10\,\mathrm{cm}^2"],
                             r"\boxed{A\approx113.10\,\mathrm{cm}^2}", "exercise 3 layout")
        self.clear_stage()

    def exercise_area_from_diameter(self) -> None:
        self.set_header(6, "EXERCISE 4 · AREA FROM DIAMETER",
                        "A circle has diameter 9 m. Area needs the radius, so convert first and only then apply A = πr².")
        self.exercise_layout("FIND A", r"d=9\,\mathrm{m}",
                             [r"r=\frac d2=4.5\,\mathrm{m}",
                              r"A=\pi(4.5)^2=20.25\pi\,\mathrm{m}^2", r"A\approx63.62\,\mathrm{m}^2"],
                             r"\boxed{A\approx63.62\,\mathrm{m}^2}", "exercise 4 layout")
        self.clear_stage()

    def exercise_mixed_circle(self) -> None:
        self.set_header(7, "EXERCISE 5 · ONE DIAMETER, TWO DIFFERENT QUESTIONS",
                        "A circular garden has diameter 12 m. Find both the perimeter and the area; notice the different units.")
        given = self.formula_panel(r"d=12\,\mathrm{m}\Rightarrow r=6\,\mathrm{m}", width=6.0, height=1.10, font_size=48)
        circ = self.note_panel("BOUNDARY / PERIMETER",
                               ["C = πd = 12π m", "C ≈ 37.70 m", "Answer uses linear units"],
                               width=6.2, title_size=28, body_size=28)
        area = self.note_panel("REGION / AREA",
                               ["A = πr² = 36π m²", "A ≈ 113.10 m²", "Answer uses square units"],
                               width=6.2, title_size=28, body_size=28)
        cards = VGroup(circ, area).arrange(RIGHT, buff=0.55)
        content = VGroup(given, cards).arrange(DOWN, buff=0.34)
        content.move_to(DOWN * 0.30)
        self.fit(content, 13.7, 5.0)
        self.assert_content_safe(content, "mixed exercise layout")
        self.play(FadeIn(given), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(circ), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(area), run_time=RUN_NORMAL)
        self.wait(PAUSE_SUMMARY)
        self.clear_stage()

    def final_decision_map(self) -> None:
        self.set_header(8, "HOW TO CHOOSE THE CORRECT CIRCLE FORMULA",
                        "Decide what the question asks before calculating: relation, boundary or region.")
        route = self.process_map([("1", "READ GIVEN DATA"), ("2", "RELATE d AND r"), ("3", "BOUNDARY? C"),
                                  ("4", "REGION? A"), ("5", "KEEP π OR DECIMAL"), ("6", "CHECK UNITS")],
                                 card_width=4.25, card_height=1.14, columns=3)
        route.move_to(DOWN * 0.35)
        self.fit(route, 13.9, 4.8)
        formulas = self.formula_panel(r"d=2r\qquad C=\pi d=2\pi r\qquad A=\pi r^2",
                                      width=10.2, height=1.15, font_size=50)
        formulas.to_edge(DOWN, buff=0.30)
        self.assert_content_safe(VGroup(route, formulas), "final formula decision map")
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in route], lag_ratio=0.09), run_time=RUN_SLOW * 1.8)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(formulas), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        self.standard_closing("Measure → identify the quantity → choose the formula → solve → check units.")
