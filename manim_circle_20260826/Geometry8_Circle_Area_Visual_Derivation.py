#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Circle Area: visual derivation and worked examples.

Target: Manim Community Edition 0.20.x + jp_classroom_style.py
Final render:
    manim -pqh Geometry8_Circle_Area_Visual_Derivation.py \
        Geometry8CircleAreaVisualDerivation --format=mp4 --disable_caching --fps 30
"""
from __future__ import annotations

import math
import numpy as np

from circle_classroom_style import *


RADIUS_EXAMPLE = 4.0
DIAMETER_EXAMPLE = 10.0
COMPARE_RADIUS = 3.0


class Geometry8CircleAreaVisualDerivation(JPMathClassroomScene):
    """Notebook-friendly derivation of A = pi r^2 with large projector-safe visuals."""

    def validate_lesson_data(self) -> None:
        assert_close(math.pi * RADIUS_EXAMPLE**2, 50.26548245743669, label="r=4 area")
        assert_close(DIAMETER_EXAMPLE / 2, 5.0, label="d=10 radius")
        assert_close(math.pi * (DIAMETER_EXAMPLE / 2) ** 2, 78.53981633974483, label="d=10 area")
        assert_close(2 * math.pi * COMPARE_RADIUS, 18.84955592153876, label="comparison circumference")
        assert_close(math.pi * COMPARE_RADIUS**2, 28.274333882308138, label="comparison area")

    def construct(self) -> None:
        self.standard_opening(
            "GEOMETRY 8 · CIRCLES",
            "CIRCLE AREA: WHY A = πr²",
            "Rearrange the circle, connect radius to area, then solve from radius or diameter.",
            "Boundary uses linear units. Region uses square units.",
        )
        self.boundary_vs_region()
        self.sector_rearrangement()
        self.example_from_radius()
        self.example_from_diameter()
        self.compare_circumference_area()
        self.summary_method()

    def boundary_vs_region(self) -> None:
        self.set_header(1, "FIRST: WHAT DOES AREA MEASURE?",
                        "Circumference follows the boundary; area measures the region inside the circle.")
        r = 1.65
        left_circle = Circle(radius=r, stroke_color=BLACK_LINE, stroke_width=5.0, fill_opacity=0)
        boundary_label = self.text("BOUNDARY", 34, BOLD).next_to(left_circle, DOWN, buff=0.25)
        left_note = self.text("Circumference C", 28).next_to(boundary_label, DOWN, buff=0.10)
        left = VGroup(left_circle, boundary_label, left_note)
        right_circle = Circle(radius=r, stroke_color=BLACK_LINE, stroke_width=2.8,
                              fill_color=VERY_LIGHT_GRAY, fill_opacity=1.0)
        region_label = self.text("REGION", 34, BOLD).next_to(right_circle, DOWN, buff=0.25)
        right_note = self.text("Area A", 28).next_to(region_label, DOWN, buff=0.10)
        right = VGroup(right_circle, region_label, right_note)
        layout = self.split_layout(left, right, left_width=6.0, right_width=6.0, max_height=4.9, center_y=-0.25)
        self.assert_content_safe(layout.group, "boundary versus region")
        self.play(Create(left_circle), FadeIn(boundary_label), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(left_note), run_time=RUN_QUICK)
        self.play(FadeIn(right_circle), FadeIn(region_label), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(right_note), run_time=RUN_QUICK)
        self.wait(PAUSE_WORK)
        self.clear_stage()

    def sector_rearrangement(self) -> None:
        self.set_header(2, "CUT THE CIRCLE INTO THIN SECTORS",
                        "Alternating the sectors makes a shape that approaches a rectangle as the sectors become thinner.")
        radius = 1.55
        n = 16
        theta = TAU / n
        source_center = LEFT * 3.55 + DOWN * 0.25
        sectors = VGroup()
        for i in range(n):
            sector = Sector(radius=radius, angle=theta, start_angle=i * theta,
                            stroke_color=BLACK_LINE, stroke_width=1.2,
                            fill_color=VERY_LIGHT_GRAY if i % 2 == 0 else WHITE, fill_opacity=1.0)
            sector.shift(source_center)
            sectors.add(sector)
        center_dot = Dot(source_center, radius=0.06, color=BLACK_LINE)
        radius_line = Line(source_center, source_center + RIGHT * radius, color=BLACK_LINE, stroke_width=3)
        radius_label = self.math(r"r", 42).next_to(radius_line, UP, buff=0.08)
        note = self.note_panel("VISUAL IDEA", ["All sectors have the same radius r.",
                                                "Half the arcs move to the top.",
                                                "Half the arcs move to the bottom."],
                               width=6.0, title_size=29, body_size=27)
        note.move_to(RIGHT * 3.4 + DOWN * 0.35)
        intro_group = VGroup(sectors, center_dot, radius_line, radius_label, note)
        self.assert_content_safe(intro_group, "sector introduction")
        self.play(FadeIn(sectors), FadeIn(center_dot), run_time=RUN_SLOW)
        self.play(Create(radius_line), FadeIn(radius_label), run_time=RUN_NORMAL)
        self.play(FadeIn(note), run_time=RUN_NORMAL)
        self.wait(PAUSE_WORK)

        arc_width = 2 * radius * math.sin(theta / 2)
        targets: list[Mobject] = []
        center_y = -0.45
        top_apex_y = center_y - radius / 2
        bottom_apex_y = center_y + radius / 2
        top_indices = [i for i in range(n) if i % 2 == 0]
        bottom_indices = [i for i in range(n) if i % 2 == 1]
        total_row_width = (len(top_indices) - 1) * arc_width
        x0 = -total_row_width / 2
        for i, sector in enumerate(sectors):
            target = Sector(radius=radius, angle=theta, start_angle=-theta / 2,
                            stroke_color=BLACK_LINE, stroke_width=1.2,
                            fill_color=VERY_LIGHT_GRAY if i % 2 == 0 else WHITE, fill_opacity=1.0)
            if i % 2 == 0:
                k = top_indices.index(i)
                x = x0 + k * arc_width
                target.rotate(PI / 2)
                target.shift(np.array([x, top_apex_y, 0]))
            else:
                k = bottom_indices.index(i)
                x = x0 + k * arc_width + arc_width / 2
                target.rotate(-PI / 2)
                target.shift(np.array([x, bottom_apex_y, 0]))
            targets.append(target)
        self.play(FadeOut(note), FadeOut(center_dot), FadeOut(radius_line), FadeOut(radius_label), run_time=RUN_QUICK)
        self.play(LaggedStart(*[Transform(sector, target) for sector, target in zip(sectors, targets)], lag_ratio=0.035),
                  run_time=RUN_SLOW * 2.2)
        self.wait(PAUSE_EXPLAIN)

        rearranged = sectors
        base_y = rearranged.get_bottom()[1] - 0.35
        x_left = rearranged.get_left()[0]
        x_right = rearranged.get_right()[0]
        base_line = DoubleArrow(np.array([x_left, base_y, 0]), np.array([x_right, base_y, 0]),
                                buff=0.0, tip_length=0.16, color=BLACK_LINE, stroke_width=2.4)
        base_label = self.math(r"\text{base}\approx \frac{C}{2}=\pi r", 43).next_to(base_line, DOWN, buff=0.10)
        height_x = rearranged.get_right()[0] + 0.45
        height_arrow = DoubleArrow(np.array([height_x, rearranged.get_bottom()[1], 0]),
                                   np.array([height_x, rearranged.get_top()[1], 0]),
                                   buff=0.0, tip_length=0.16, color=BLACK_LINE, stroke_width=2.4)
        height_label = self.math(r"r", 42).next_to(height_arrow, RIGHT, buff=0.10)
        formula = self.formula_panel(r"A=(\pi r)(r)=\pi r^2", width=7.0, height=1.15, font_size=58)
        formula.to_edge(DOWN, buff=0.30)
        derivation_group = VGroup(rearranged, base_line, base_label, height_arrow, height_label, formula)
        self.assert_content_safe(derivation_group, "area derivation")
        self.play(GrowFromCenter(base_line), FadeIn(base_label), run_time=RUN_NORMAL)
        self.play(GrowFromCenter(height_arrow), FadeIn(height_label), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)
        self.wait(PAUSE_SUMMARY)
        self.focus_on(formula, width=8.0, pause=PAUSE_EXPLAIN)
        self.clear_stage()

    def example_from_radius(self) -> None:
        self.set_header(3, "EXAMPLE 1 · AREA FROM THE RADIUS",
                        "If the radius is already known, substitute it directly into A = πr² and keep square units.")
        circle = Circle(radius=1.55, stroke_color=BLACK_LINE, stroke_width=3.2,
                        fill_color=VERY_LIGHT_GRAY, fill_opacity=0.6)
        radius = Line(circle.get_center(), circle.get_right(), color=BLACK_LINE, stroke_width=3.2)
        r_label = self.math(r"r=4\,\mathrm{cm}", 42).next_to(radius, UP, buff=0.10)
        panel = self.figure_panel(VGroup(circle, radius, r_label), width=6.0, height=4.4, title="GIVEN RADIUS")
        stack = self.equation_stack([r"A=\pi r^2", r"A=\pi(4)^2", r"A=16\pi\ \mathrm{cm}^2",
                                     r"A\approx 50.27\ \mathrm{cm}^2"],
                                    sizes=[54, 54, 54, 56], max_width=6.2, max_height=4.3)
        layout = self.split_layout(panel.group, stack, left_width=6.2, right_width=6.2, max_height=4.8, center_y=-0.35)
        self.assert_content_safe(layout.group, "radius worked example")
        self.play(FadeIn(panel.group), run_time=RUN_NORMAL)
        self.animate_equation_stack(stack, pause=PAUSE_READ)
        self.wait(PAUSE_WORK)
        self.focus_on(stack[-1], width=6.6, pause=PAUSE_EXPLAIN)
        self.clear_stage()

    def example_from_diameter(self) -> None:
        self.set_header(4, "EXAMPLE 2 · AREA FROM THE DIAMETER",
                        "Area needs the radius. Convert d to r first: r = d/2.")
        circle = Circle(radius=1.55, stroke_color=BLACK_LINE, stroke_width=3.2,
                        fill_color=VERY_LIGHT_GRAY, fill_opacity=0.6)
        diameter = Line(circle.get_left(), circle.get_right(), color=BLACK_LINE, stroke_width=3.2)
        d_label = self.math(r"d=10\,\mathrm{m}", 43).next_to(diameter, UP, buff=0.11)
        panel = self.figure_panel(VGroup(circle, diameter, d_label), width=6.0, height=4.4, title="GIVEN DIAMETER")
        stack = self.equation_stack([r"r=\frac{d}{2}=\frac{10}{2}=5\,\mathrm{m}", r"A=\pi r^2",
                                     r"A=\pi(5)^2=25\pi\ \mathrm{m}^2", r"A\approx 78.54\ \mathrm{m}^2"],
                                    sizes=[47, 52, 48, 54], max_width=6.45, max_height=4.3)
        layout = self.split_layout(panel.group, stack, left_width=6.2, right_width=6.25, max_height=4.8, center_y=-0.35)
        self.assert_content_safe(layout.group, "diameter worked example")
        self.play(FadeIn(panel.group), run_time=RUN_NORMAL)
        self.animate_equation_stack(stack, pause=PAUSE_READ)
        self.wait(PAUSE_WORK)
        self.focus_on(stack[-1], width=6.6, pause=PAUSE_EXPLAIN)
        self.clear_stage()

    def compare_circumference_area(self) -> None:
        self.set_header(5, "DO NOT MIX CIRCUMFERENCE AND AREA",
                        "The same radius can produce two different quantities: boundary length and region size.")
        left = self.note_panel("CIRCUMFERENCE = BOUNDARY",
                               ["Formula: C = 2πr", "For r = 3 cm: C = 6π cm", "Linear units: cm, m, units"],
                               width=6.3, title_size=29, body_size=28)
        right = self.note_panel("AREA = REGION",
                                ["Formula: A = πr²", "For r = 3 cm: A = 9π cm²", "Square units: cm², m², units²"],
                                width=6.3, title_size=29, body_size=28)
        layout = self.split_layout(left, right, left_width=6.4, right_width=6.4, max_height=4.9, center_y=-0.35)
        self.assert_content_safe(layout.group, "circumference area comparison")
        self.play(FadeIn(left), run_time=RUN_NORMAL)
        self.wait(PAUSE_READ)
        self.play(FadeIn(right), run_time=RUN_NORMAL)
        self.wait(PAUSE_SUMMARY)
        self.clear_stage()

    def summary_method(self) -> None:
        self.set_header(6, "AREA METHOD YOU CAN REUSE",
                        "Start from the given measurement, convert to radius if needed, square the radius, multiply by π, then check units.")
        route = self.process_map([("1", "READ r OR d"), ("2", "IF d: r=d/2"), ("3", "USE A=πr²"),
                                  ("4", "SQUARE r"), ("5", "MULTIPLY BY π"), ("6", "WRITE units²")],
                                 card_width=4.25, card_height=1.14, columns=3)
        route.move_to(DOWN * 0.30)
        self.fit(route, 13.9, 4.8)
        final = self.formula_panel(r"\boxed{A=\pi r^2}", width=5.4, height=1.15, font_size=64)
        final.to_edge(DOWN, buff=0.30)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in route], lag_ratio=0.10), run_time=RUN_SLOW * 1.8)
        self.wait(PAUSE_WORK)
        self.play(FadeIn(final), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        self.standard_closing("Circle area measures the region: A = πr², always in square units.")
