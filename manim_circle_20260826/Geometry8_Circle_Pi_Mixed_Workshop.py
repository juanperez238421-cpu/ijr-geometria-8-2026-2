#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Real-world circle area workshop with 3D camera work.

Target: Manim Community Edition 0.20.x.
The scene intentionally keeps the existing scene/class name so the established
GitHub Actions PQH protocol can render it without changing the delivery contract.

Final render:
    manim -pqh Geometry8_Circle_Pi_Mixed_Workshop.py \
        Geometry8CirclePiMixedWorkshop --format=mp4 --disable_caching \
        --fps 30 --resolution 1920,1080
"""
from __future__ import annotations

import math
import os

import numpy as np
from manim import *

# Reuse the established project configuration and visual constants.
from circle_classroom_style import (
    BLACK_LINE,
    BLACK_TEXT,
    LIGHT_GRAY,
    PAPER_GRAY,
    VERY_LIGHT_GRAY,
    WHITE_FILL,
)


TIME_SCALE = float(os.getenv("LESSON_TIME_SCALE", "1.0"))
RUN_QUICK = 0.65
RUN_NORMAL = 1.0
RUN_SLOW = 1.35
PAUSE_PLAN = 3.2
PAUSE_STEP = 1.65
PAUSE_ANSWER = 3.0
PAUSE_FINAL = 4.2

ACCENT_BLUE = "#2864A8"
ACCENT_GREEN = "#4F8A4C"
ACCENT_ORANGE = "#D1842C"
ACCENT_TEAL = "#287C7E"
ACCENT_PURPLE = "#73559A"
ACCENT_RED = "#A84B45"


def _close(actual: float, expected: float, tol: float = 1e-2) -> None:
    if abs(actual - expected) > tol:
        raise ValueError(f"math validation failed: {actual} != {expected}")


class Geometry8CirclePiMixedWorkshop(ThreeDScene):
    """Projector-safe, real-world circle workshop with 3D spatial interpretation."""

    def setup(self) -> None:
        super().setup()
        self.camera.background_color = WHITE
        self.header_group: VGroup | None = None
        self.header_subtitle: Mobject | None = None
        self.validate_lesson_data()

    def validate_lesson_data(self) -> None:
        _close(2 * math.pi * 4, 25.132741)
        _close(math.pi * 4**2, 50.265482)
        _close(math.pi * 5**2, 78.539816)
        _close(math.pi * (5**2 - 3**2), 50.265482)
        _close(12**2 - math.pi * 4**2, 93.734518)
        _close(math.sqrt(78.54 / math.pi), 5.000006, tol=2e-2)

    # ------------------------------------------------------------------
    # Protocol helpers
    # ------------------------------------------------------------------
    def play(self, *animations, **kwargs):
        if kwargs.get("run_time") is not None:
            kwargs["run_time"] *= TIME_SCALE
        return super().play(*animations, **kwargs)

    def wait(self, duration: float = DEFAULT_WAIT_TIME, *args, **kwargs):
        return super().wait(duration * TIME_SCALE, *args, **kwargs)

    def text(self, content: str, size: int = 30, weight=NORMAL, **kwargs) -> Text:
        return Text(content, font_size=size, color=BLACK_TEXT, weight=weight,
                    line_spacing=0.92, **kwargs)

    def mathtex(self, expression: str, size: int = 42, **kwargs) -> MathTex:
        return MathTex(expression, font_size=size, color=BLACK_TEXT, **kwargs)

    def fit(self, mob: Mobject, max_width: float, max_height: float) -> Mobject:
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        if mob.height > max_height:
            mob.scale_to_fit_height(max_height)
        return mob

    def fixed(self, *mobjects: Mobject) -> None:
        self.add_fixed_in_frame_mobjects(*mobjects)

    def make_header(self, number: int, title: str, subtitle: str) -> VGroup:
        badge = RoundedRectangle(width=0.72, height=0.54, corner_radius=0.10,
                                 stroke_color=BLACK_LINE, stroke_width=2,
                                 fill_color=WHITE, fill_opacity=1)
        badge_text = self.text(f"{number:02d}", 23, BOLD).move_to(badge)
        title_mob = self.text(title, 34, BOLD)
        self.fit(title_mob, 12.8, 0.58)
        row = VGroup(VGroup(badge, badge_text), title_mob).arrange(RIGHT, buff=0.24)
        row.to_edge(UP, buff=0.16).to_edge(LEFT, buff=0.48)
        rule = Line(LEFT * 7.45, RIGHT * 7.45, color=LIGHT_GRAY, stroke_width=2)
        rule.next_to(row, DOWN, buff=0.07)
        subtitle_mob = self.text(subtitle, 21)
        self.fit(subtitle_mob, 14.2, 0.64)
        subtitle_mob.next_to(rule, DOWN, buff=0.08).align_to(row, LEFT)
        return VGroup(row, rule, subtitle_mob)

    def set_header(self, number: int, title: str, subtitle: str) -> None:
        new = self.make_header(number, title, subtitle)
        self.fixed(new)
        if self.header_group is None:
            self.header_group = new
            self.play(FadeIn(new, shift=DOWN * 0.08), run_time=RUN_QUICK)
        else:
            old = self.header_group
            self.header_group = new
            self.play(FadeOut(old), FadeIn(new), run_time=RUN_QUICK)
            self.remove(old)

    def question_card(self, title: str, lines: list[str], accent: str,
                      width: float = 5.25, height: float = 2.35) -> VGroup:
        box = RoundedRectangle(width=width, height=height, corner_radius=0.14,
                               stroke_color=BLACK_LINE, stroke_width=2,
                               fill_color=WHITE_FILL, fill_opacity=0.98)
        marker = Rectangle(width=0.12, height=height - 0.12, stroke_width=0,
                           fill_color=accent, fill_opacity=1)
        marker.align_to(box, LEFT).shift(RIGHT * 0.06)
        title_mob = self.text(title, 28, BOLD)
        body = VGroup(*[self.text(line, 24) for line in lines]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.13)
        content = VGroup(title_mob, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        self.fit(content, width - 0.58, height - 0.38)
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.34)
        return VGroup(box, marker, content)

    def equation_card(self, equations: list[str], answer: str, accent: str,
                      width: float = 5.45) -> tuple[VGroup, VGroup, VGroup]:
        eq_mobs = VGroup(*[self.mathtex(eq, 40) for eq in equations])
        eq_mobs.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        for eq in eq_mobs:
            self.fit(eq, width - 0.70, 0.78)
        answer_mob = self.mathtex(answer, 43)
        self.fit(answer_mob, width - 0.70, 0.88)
        divider = Line(LEFT * (width - 0.72) / 2, RIGHT * (width - 0.72) / 2,
                       color=accent, stroke_width=4)
        content = VGroup(eq_mobs, divider, answer_mob).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22)
        box = RoundedRectangle(width=width, height=max(2.35, content.height + 0.54),
                               corner_radius=0.14, stroke_color=BLACK_LINE,
                               stroke_width=2, fill_color=PAPER_GRAY, fill_opacity=0.98)
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.35)
        return VGroup(box, content), eq_mobs, answer_mob

    def pause_prompt(self, text: str = "PAUSE · PLAN · CHOOSE A FORMULA") -> VGroup:
        box = RoundedRectangle(width=4.85, height=0.68, corner_radius=0.12,
                               stroke_color=BLACK_LINE, stroke_width=1.7,
                               fill_color=VERY_LIGHT_GRAY, fill_opacity=1)
        label = self.text(text, 21, BOLD).move_to(box)
        return VGroup(box, label)

    def world_label(self, text: str, accent: str) -> VGroup:
        dot = Dot(radius=0.08, color=accent)
        label = self.text(text, 22, BOLD)
        return VGroup(dot, label).arrange(RIGHT, buff=0.12)

    def show_solution(self, card: VGroup, eq_mobs: VGroup, answer: Mobject,
                      position: np.ndarray = RIGHT * 4.55 + DOWN * 0.95) -> None:
        card.move_to(position)
        self.fixed(card)
        box = card[0]
        divider = card[1][1]
        self.play(FadeIn(box), run_time=RUN_QUICK)
        for eq in eq_mobs:
            self.play(Write(eq), run_time=RUN_NORMAL)
            self.wait(PAUSE_STEP)
        self.play(Create(divider), run_time=RUN_QUICK)
        self.play(Write(answer), run_time=RUN_NORMAL)
        self.wait(PAUSE_ANSWER)

    def clear_problem(self, *mobjects: Mobject) -> None:
        live = [m for m in mobjects if m is not None]
        if live:
            self.play(*[FadeOut(m) for m in live], run_time=RUN_NORMAL)
            for mob in live:
                self.remove(mob)
        self.stop_ambient_camera_rotation()
        self.set_camera_orientation(phi=62 * DEGREES, theta=-48 * DEGREES, zoom=0.92)

    # ------------------------------------------------------------------
    # Scene construction
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.set_camera_orientation(phi=62 * DEGREES, theta=-48 * DEGREES, zoom=0.92)
        self.opening()
        self.problem_garden_boundary_and_area()
        self.problem_pool_cover_from_diameter()
        self.problem_annular_walkway()
        self.problem_square_patio_minus_fountain()
        self.problem_inverse_area_to_radius()
        self.closing()

    def opening(self) -> None:
        title = self.text("GEOMETRY 8 · REAL CIRCLE PROBLEMS", 46, BOLD)
        subtitle = self.text("AREA · CIRCUMFERENCE · COMPOSITE REGIONS · INVERSE PROBLEMS", 27)
        prompt = self.text("See the object → identify the geometry → choose the formula → calculate → check units", 23)
        title_block = VGroup(title, subtitle, prompt).arrange(DOWN, buff=0.24)
        title_block.to_edge(UP, buff=0.55)
        self.fixed(title_block)

        # A short 3D visual language preview: boundary ring, filled disk and raised cylinder.
        disk = Cylinder(radius=1.45, height=0.22, direction=OUT,
                        fill_color=ACCENT_BLUE, fill_opacity=0.72,
                        stroke_color=BLACK_LINE, stroke_width=1.2).shift(LEFT * 2.7 + DOWN * 0.7)
        ring = Circle(radius=1.45, color=ACCENT_RED, stroke_width=8).shift(LEFT * 2.7 + DOWN * 0.7 + OUT * 0.12)
        radius = Line(LEFT * 2.7 + DOWN * 0.7 + OUT * 0.13,
                      LEFT * 1.25 + DOWN * 0.7 + OUT * 0.13,
                      color=BLACK_LINE, stroke_width=5)
        center = Dot3D(point=LEFT * 2.7 + DOWN * 0.7 + OUT * 0.16,
                       radius=0.06, color=BLACK)
        legend = self.question_card(
            "READ THE PICTURE FIRST",
            ["Red edge → circumference C", "Filled region → area A", "Radius controls both formulas"],
            ACCENT_BLUE, width=5.35, height=2.45,
        ).move_to(RIGHT * 3.9 + DOWN * 0.45)
        self.fixed(legend)

        self.play(FadeIn(disk), Create(ring), Create(radius), FadeIn(center), run_time=RUN_SLOW)
        self.play(FadeIn(legend), run_time=RUN_NORMAL)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(3.0)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=20 * DEGREES, theta=-90 * DEGREES, zoom=0.96, run_time=RUN_SLOW)
        self.wait(2.0)
        self.play(FadeOut(disk), FadeOut(ring), FadeOut(radius), FadeOut(center), FadeOut(legend), FadeOut(title_block),
                  run_time=RUN_NORMAL)
        for mob in (legend, title_block):
            self.remove(mob)
        self.set_camera_orientation(phi=62 * DEGREES, theta=-48 * DEGREES, zoom=0.92)

    def problem_garden_boundary_and_area(self) -> None:
        self.set_header(
            1,
            "CIRCULAR GARDEN · FENCE OR GRASS?",
            "A garden has radius 4 m. Find the fence length around it and the grass area inside it.",
        )
        center = np.array([-3.0, -0.55, 0.0])
        garden = Cylinder(radius=2.15, height=0.32, direction=OUT,
                          fill_color=ACCENT_GREEN, fill_opacity=0.76,
                          stroke_color=BLACK_LINE, stroke_width=1.2).shift(center)
        boundary = Circle(radius=2.15, color=ACCENT_RED, stroke_width=8).shift(center + OUT * 0.17)
        radius = Line(center + OUT * 0.18, center + RIGHT * 2.15 + OUT * 0.18,
                      color=BLACK_LINE, stroke_width=5)
        center_dot = Dot3D(point=center + OUT * 0.20, radius=0.06, color=BLACK)
        world = VGroup(garden, boundary, radius, center_dot)

        q = self.question_card(
            "WHAT DOES EACH QUESTION MEAN?",
            ["Fence → boundary → C", "Grass → region → A", "Given: r = 4 m"],
            ACCENT_GREEN,
        ).move_to(RIGHT * 4.55 + UP * 0.85)
        pause = self.pause_prompt().move_to(RIGHT * 4.55 + DOWN * 2.45)
        label = self.world_label("real garden model", ACCENT_GREEN).move_to(LEFT * 3.0 + DOWN * 3.15)
        self.fixed(q, pause, label)

        self.play(FadeIn(garden), Create(boundary), Create(radius), FadeIn(center_dot), run_time=RUN_SLOW)
        self.play(FadeIn(q), FadeIn(pause), FadeIn(label), run_time=RUN_NORMAL)
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(PAUSE_PLAN)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=8 * DEGREES, theta=-90 * DEGREES, zoom=0.96, run_time=RUN_SLOW)
        self.play(FadeOut(pause), run_time=RUN_QUICK)

        sol, eqs, ans = self.equation_card(
            [r"C=2\pi r=2\pi(4)=8\pi", r"C\approx25.13\,\mathrm{m}",
             r"A=\pi r^2=\pi(4)^2=16\pi"],
            r"\boxed{C\approx25.13\,\mathrm{m}\quad A\approx50.27\,\mathrm{m}^2}",
            ACCENT_GREEN,
        )
        self.show_solution(sol, eqs, ans, RIGHT * 4.55 + DOWN * 0.75)
        self.clear_problem(world, q, label, sol)

    def problem_pool_cover_from_diameter(self) -> None:
        self.set_header(
            2,
            "ROUND POOL COVER · DIAMETER IS NOT RADIUS",
            "A circular pool has diameter 10 m. How many square meters of cover material are needed?",
        )
        center = np.array([-3.0, -0.55, 0.0])
        pool = Cylinder(radius=2.20, height=0.52, direction=OUT,
                        fill_color=ACCENT_BLUE, fill_opacity=0.70,
                        stroke_color=BLACK_LINE, stroke_width=1.2).shift(center)
        rim = Circle(radius=2.20, color=BLACK_LINE, stroke_width=5).shift(center + OUT * 0.27)
        diameter = Line(center + LEFT * 2.20 + OUT * 0.29,
                        center + RIGHT * 2.20 + OUT * 0.29,
                        color=ACCENT_ORANGE, stroke_width=7)
        world = VGroup(pool, rim, diameter)
        q = self.question_card(
            "FIRST CONVERSION",
            ["Given: d = 10 m", "Area formula needs r", "So r = d/2 = 5 m"],
            ACCENT_BLUE,
        ).move_to(RIGHT * 4.55 + UP * 0.85)
        pause = self.pause_prompt("PAUSE · CONVERT d → r FIRST").move_to(RIGHT * 4.55 + DOWN * 2.45)
        self.fixed(q, pause)

        self.play(FadeIn(pool), Create(rim), Create(diameter), run_time=RUN_SLOW)
        self.play(FadeIn(q), FadeIn(pause), run_time=RUN_NORMAL)
        self.begin_ambient_camera_rotation(rate=0.09)
        self.wait(PAUSE_PLAN)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=7 * DEGREES, theta=-90 * DEGREES, zoom=0.96, run_time=RUN_SLOW)
        self.play(FadeOut(pause), run_time=RUN_QUICK)

        sol, eqs, ans = self.equation_card(
            [r"r=\frac{d}{2}=\frac{10}{2}=5\,\mathrm{m}",
             r"A=\pi r^2=\pi(5)^2=25\pi"],
            r"\boxed{A\approx78.54\,\mathrm{m}^2}",
            ACCENT_BLUE,
        )
        self.show_solution(sol, eqs, ans, RIGHT * 4.55 + DOWN * 0.70)
        self.clear_problem(world, q, sol)

    def problem_annular_walkway(self) -> None:
        self.set_header(
            3,
            "WALKWAY AROUND A FOUNTAIN · SUBTRACT TWO CIRCLES",
            "The fountain radius is 3 m and the outer walkway radius is 5 m. Find only the walkway area.",
        )
        center = np.array([-3.0, -0.55, 0.0])
        inner_v = 1.35
        outer_v = 2.25

        walkway = Surface(
            lambda u, v: np.array([
                center[0] + (inner_v + (outer_v - inner_v) * v) * np.cos(u),
                center[1] + (inner_v + (outer_v - inner_v) * v) * np.sin(u),
                0.15,
            ]),
            u_range=[0, TAU], v_range=[0, 1], resolution=(36, 8),
            fill_color=ACCENT_ORANGE, fill_opacity=0.82,
            stroke_color=ACCENT_ORANGE, stroke_width=0.7,
        )
        fountain = Cylinder(radius=inner_v, height=0.48, direction=OUT,
                            fill_color=ACCENT_BLUE, fill_opacity=0.75,
                            stroke_color=BLACK_LINE, stroke_width=1.2).shift(center)
        outer_ring = Circle(radius=outer_v, color=BLACK_LINE, stroke_width=5).shift(center + OUT * 0.16)
        inner_ring = Circle(radius=inner_v, color=BLACK_LINE, stroke_width=5).shift(center + OUT * 0.25)
        world = VGroup(walkway, fountain, outer_ring, inner_ring)

        q = self.question_card(
            "AREA OF A RING",
            ["Outer radius: R = 5 m", "Inner radius: r = 3 m", "Walkway = big circle − fountain"],
            ACCENT_ORANGE,
        ).move_to(RIGHT * 4.55 + UP * 0.85)
        pause = self.pause_prompt("PAUSE · WRITE A_outer − A_inner").move_to(RIGHT * 4.55 + DOWN * 2.45)
        self.fixed(q, pause)

        self.play(FadeIn(fountain), FadeIn(walkway), Create(outer_ring), Create(inner_ring), run_time=RUN_SLOW)
        self.play(FadeIn(q), FadeIn(pause), run_time=RUN_NORMAL)
        self.begin_ambient_camera_rotation(rate=0.07)
        self.wait(PAUSE_PLAN)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=10 * DEGREES, theta=-90 * DEGREES, zoom=0.95, run_time=RUN_SLOW)
        self.play(FadeOut(pause), run_time=RUN_QUICK)

        sol, eqs, ans = self.equation_card(
            [r"A=\pi R^2-\pi r^2", r"A=\pi(5^2-3^2)=\pi(25-9)", r"A=16\pi"],
            r"\boxed{A\approx50.27\,\mathrm{m}^2}",
            ACCENT_ORANGE,
        )
        self.show_solution(sol, eqs, ans, RIGHT * 4.55 + DOWN * 0.78)
        self.clear_problem(world, q, sol)

    def problem_square_patio_minus_fountain(self) -> None:
        self.set_header(
            4,
            "SQUARE PATIO WITH A CIRCULAR FOUNTAIN · COMPOSITE AREA",
            "A 12 m × 12 m patio contains a circular fountain of diameter 8 m. Find the remaining tile area.",
        )
        center = np.array([-3.0, -0.55, 0.0])
        patio = Cube(side_length=4.75, fill_color=LIGHT_GRAY, fill_opacity=0.60,
                     stroke_color=BLACK_LINE, stroke_width=1.0).stretch(0.07, 2).shift(center)
        fountain = Cylinder(radius=1.58, height=0.42, direction=OUT,
                            fill_color=ACCENT_TEAL, fill_opacity=0.78,
                            stroke_color=BLACK_LINE, stroke_width=1.2).shift(center + OUT * 0.10)
        diameter = Line(center + LEFT * 1.58 + OUT * 0.34,
                        center + RIGHT * 1.58 + OUT * 0.34,
                        color=ACCENT_PURPLE, stroke_width=7)
        world = VGroup(patio, fountain, diameter)

        q = self.question_card(
            "COMPOSITE REGION",
            ["Square area: 12 × 12", "Fountain: d = 8 m → r = 4 m", "Tile = square − circle"],
            ACCENT_TEAL,
        ).move_to(RIGHT * 4.55 + UP * 0.85)
        pause = self.pause_prompt("PAUSE · AREA WHOLE − AREA HOLE").move_to(RIGHT * 4.55 + DOWN * 2.45)
        self.fixed(q, pause)

        self.play(FadeIn(patio), FadeIn(fountain), Create(diameter), run_time=RUN_SLOW)
        self.play(FadeIn(q), FadeIn(pause), run_time=RUN_NORMAL)
        self.begin_ambient_camera_rotation(rate=0.07)
        self.wait(PAUSE_PLAN)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=8 * DEGREES, theta=-90 * DEGREES, zoom=0.96, run_time=RUN_SLOW)
        self.play(FadeOut(pause), run_time=RUN_QUICK)

        sol, eqs, ans = self.equation_card(
            [r"A_{\rm square}=12^2=144", r"r=4\,\mathrm{m}\Rightarrow A_{\rm circle}=16\pi",
             r"A_{\rm tile}=144-16\pi"],
            r"\boxed{A_{\rm tile}\approx93.73\,\mathrm{m}^2}",
            ACCENT_TEAL,
        )
        self.show_solution(sol, eqs, ans, RIGHT * 4.55 + DOWN * 0.78)
        self.clear_problem(world, q, sol)

    def problem_inverse_area_to_radius(self) -> None:
        self.set_header(
            5,
            "ROUND RUG · WORK BACKWARD FROM AREA",
            "A circular rug has area 78.54 m². Estimate its radius and diameter.",
        )
        center = np.array([-3.0, -0.55, 0.0])
        rug = Cylinder(radius=2.15, height=0.14, direction=OUT,
                       fill_color=ACCENT_PURPLE, fill_opacity=0.72,
                       stroke_color=BLACK_LINE, stroke_width=1.2).shift(center)
        rim = Circle(radius=2.15, color=BLACK_LINE, stroke_width=4).shift(center + OUT * 0.08)
        radius = Line(center + OUT * 0.09, center + RIGHT * 2.15 + OUT * 0.09,
                      color=ACCENT_RED, stroke_width=7)
        world = VGroup(rug, rim, radius)

        q = self.question_card(
            "INVERSE AREA",
            ["Given: A = 78.54 m²", "A = πr²", "Undo π, then undo the square"],
            ACCENT_PURPLE,
        ).move_to(RIGHT * 4.55 + UP * 0.85)
        pause = self.pause_prompt("PAUSE · ISOLATE r², THEN √").move_to(RIGHT * 4.55 + DOWN * 2.45)
        self.fixed(q, pause)

        self.play(FadeIn(rug), Create(rim), Create(radius), run_time=RUN_SLOW)
        self.play(FadeIn(q), FadeIn(pause), run_time=RUN_NORMAL)
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(PAUSE_PLAN)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=8 * DEGREES, theta=-90 * DEGREES, zoom=0.96, run_time=RUN_SLOW)
        self.play(FadeOut(pause), run_time=RUN_QUICK)

        sol, eqs, ans = self.equation_card(
            [r"78.54=\pi r^2", r"r^2=\frac{78.54}{\pi}\approx25",
             r"r\approx\sqrt{25}=5\,\mathrm{m}", r"d=2r\approx10\,\mathrm{m}"],
            r"\boxed{r\approx5\,\mathrm{m}\quad d\approx10\,\mathrm{m}}",
            ACCENT_PURPLE,
        )
        self.show_solution(sol, eqs, ans, RIGHT * 4.55 + DOWN * 0.90)
        self.clear_problem(world, q, sol)

    def closing(self) -> None:
        self.set_header(
            6,
            "CIRCLE PROBLEM STRATEGY",
            "The drawing tells you what to measure; the units tell you whether the answer is length or area.",
        )
        cards = VGroup(
            self.question_card("1 · IDENTIFY", ["Boundary? Region? Missing radius?"], ACCENT_BLUE, width=4.25, height=1.35),
            self.question_card("2 · CONVERT", ["d = 2r before using A = πr²"], ACCENT_ORANGE, width=4.25, height=1.35),
            self.question_card("3 · COMPOSE", ["Whole − hole for ring/composite area"], ACCENT_TEAL, width=4.25, height=1.35),
            self.question_card("4 · CHECK", ["m for length · m² for area"], ACCENT_PURPLE, width=4.25, height=1.35),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.45, 0.38))
        cards.move_to(DOWN * 0.15)
        formulas = VGroup(
            self.mathtex(r"C=2\pi r=\pi d", 47),
            self.mathtex(r"A=\pi r^2", 50),
            self.mathtex(r"A_{\rm ring}=\pi(R^2-r^2)", 44),
        ).arrange(RIGHT, buff=0.75)
        self.fit(formulas, 13.4, 0.90)
        formulas.move_to(DOWN * 3.05)
        self.fixed(cards, formulas)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.10) for card in cards], lag_ratio=0.14),
                  run_time=RUN_SLOW * 1.6)
        self.wait(2.5)
        self.play(Write(formulas), run_time=RUN_SLOW)
        self.wait(PAUSE_FINAL)
