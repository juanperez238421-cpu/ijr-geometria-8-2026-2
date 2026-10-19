#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Circle area workshop, senior QA technical-3D edition.

Design goals
------------
* Realistic technical geometry instead of flat icon-like cylinders.
* Consistent CAD-inspired palette and isometric camera language.
* Large projector-safe text with strict 16:9 safe margins.
* Each exercise follows: SEE → IDENTIFY → MODEL → SOLVE → CHECK.
* 3D is used to clarify the physical situation; top view is used for the math.

Target: Manim Community Edition 0.20.x.
Final protocol render:
    manim -pqh Geometry8_Circle_Pi_Mixed_Workshop.py \
        Geometry8CirclePiMixedWorkshop --format=mp4 --disable_caching \
        --fps 30 --resolution 1920,1080
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass

import numpy as np
from manim import *

from circle_classroom_style import BLACK_TEXT


TIME_SCALE = float(os.getenv("LESSON_TIME_SCALE", "1.0"))
RUN_FAST = 0.55
RUN = 0.90
RUN_SLOW = 1.35
PAUSE_READ = 1.55
PAUSE_THINK = 3.00
PAUSE_ANSWER = 2.75
PAUSE_FINAL = 4.00

BG = "#F7F9FB"
INK = "#173042"
INK_SOFT = "#365A6D"
GRID = "#D7E1E8"
GRID_DARK = "#B8C8D2"
BLUE = "#72A8D8"
CYAN = "#69C7D8"
MINT = "#77C8A5"
MINT_DARK = "#3D9A79"
ORANGE = "#F0A24A"
ORANGE_DARK = "#C67820"
WATER = "#6CB6E8"
STONE = "#BFD0DA"
STONE_DARK = "#6D8998"
PALE_BLUE = "#EAF3FA"
PALE_MINT = "#EAF6F1"
PALE_ORANGE = "#FFF4E5"
WHITE_CARD = "#FFFFFF"


@dataclass(frozen=True)
class ProblemData:
    number: int
    eyebrow: str
    title: str
    prompt: str
    accent: str


def _close(actual: float, expected: float, tol: float = 1e-2) -> None:
    if abs(actual - expected) > tol:
        raise ValueError(f"math validation failed: {actual} != {expected}")


class Geometry8CirclePiMixedWorkshop(ThreeDScene):
    """Senior-QA circle workshop with accurate models and intentional camera work."""

    def setup(self) -> None:
        super().setup()
        self.camera.background_color = BG
        self.header: VGroup | None = None
        self.validate_lesson_data()

    def validate_lesson_data(self) -> None:
        _close(2 * math.pi * 4, 25.132741)
        _close(math.pi * 4**2, 50.265482)
        _close(math.pi * 5**2, 78.539816)
        _close(math.pi * (5**2 - 3**2), 50.265482)
        _close(12**2 - math.pi * 4**2, 93.734518)
        _close(math.sqrt(78.54 / math.pi), 5.000006, tol=2e-2)

    def play(self, *animations, **kwargs):
        if kwargs.get("run_time") is not None:
            kwargs["run_time"] *= TIME_SCALE
        return super().play(*animations, **kwargs)

    def wait(self, duration: float = DEFAULT_WAIT_TIME, *args, **kwargs):
        return super().wait(duration * TIME_SCALE, *args, **kwargs)

    def fixed(self, *mobjects: Mobject) -> None:
        self.add_fixed_in_frame_mobjects(*mobjects)

    def text(self, content: str, size: int = 28, weight=NORMAL,
             color: str = INK, **kwargs) -> Text:
        return Text(content, font_size=size, color=color, weight=weight,
                    line_spacing=0.95, **kwargs)

    def mathtex(self, expression: str, size: int = 38, color: str = INK,
                **kwargs) -> MathTex:
        return MathTex(expression, font_size=size, color=color, **kwargs)

    @staticmethod
    def fit(mob: Mobject, max_width: float, max_height: float) -> Mobject:
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        if mob.height > max_height:
            mob.scale_to_fit_height(max_height)
        return mob

    def make_header(self, data: ProblemData) -> VGroup:
        eyebrow = self.text(
            f"PROBLEM {data.number:02d}  ·  {data.eyebrow}", 17, BOLD, color=data.accent
        ).move_to(UP * 4.08)
        title = self.text(data.title, 34, BOLD, color=INK)
        self.fit(title, 13.2, 0.55)
        title.move_to(UP * 3.60)
        prompt = self.text(data.prompt, 20, color=INK_SOFT)
        self.fit(prompt, 13.6, 0.52)
        prompt.move_to(UP * 3.12)
        rule = Line(LEFT * 6.85, RIGHT * 6.85, color=GRID_DARK, stroke_width=1.6)
        rule.move_to(UP * 2.76)
        return VGroup(eyebrow, title, prompt, rule)

    def set_header(self, data: ProblemData) -> None:
        new_header = self.make_header(data)
        self.fixed(new_header)
        if self.header is None:
            self.header = new_header
            self.play(FadeIn(new_header, shift=DOWN * 0.05), run_time=RUN_FAST)
        else:
            old = self.header
            self.header = new_header
            self.play(FadeOut(old), FadeIn(new_header), run_time=RUN_FAST)
            self.remove(old)

    def pill(self, text: str, accent: str, width: float = 3.75,
             fill: str = WHITE_CARD) -> VGroup:
        box = RoundedRectangle(width=width, height=0.68, corner_radius=0.18,
                               stroke_color=accent, stroke_width=1.8,
                               fill_color=fill, fill_opacity=0.97)
        label = self.text(text, 19, BOLD, color=INK)
        self.fit(label, width - 0.38, 0.38)
        label.move_to(box)
        return VGroup(box, label)

    def data_strip(self, specs: list[tuple[str, str, float]]) -> VGroup:
        items = VGroup(*[self.pill(label, accent, width=width)
                         for label, accent, width in specs]).arrange(RIGHT, buff=0.22)
        self.fit(items, 13.7, 0.72)
        items.move_to(DOWN * 3.86)
        self.fixed(items)
        return items

    def section_label(self, text: str, accent: str) -> VGroup:
        line = Line(LEFT * 0.38, RIGHT * 0.38, color=accent, stroke_width=4)
        label = self.text(text, 17, BOLD, color=accent)
        return VGroup(line, label).arrange(RIGHT, buff=0.15)

    def build_solution_panel(self, title: str, equations: list[str], answer: str,
                             accent: str, note: str, *, x: float = 4.45,
                             y: float = -0.20, width: float = 5.95,
                             height: float = 4.55) -> tuple[VGroup, VGroup, VGroup, VGroup]:
        panel = RoundedRectangle(width=width, height=height, corner_radius=0.18,
                                 stroke_color=GRID_DARK, stroke_width=1.5,
                                 fill_color=WHITE_CARD, fill_opacity=0.98).move_to([x, y, 0])
        accent_bar = RoundedRectangle(width=0.10, height=height - 0.24,
                                      corner_radius=0.04, stroke_width=0,
                                      fill_color=accent, fill_opacity=1)
        accent_bar.align_to(panel, LEFT).shift(RIGHT * 0.09)
        label = self.section_label(title, accent)
        label.move_to(panel.get_top() + DOWN * 0.48).align_to(panel, LEFT).shift(RIGHT * 0.38)
        eqs = VGroup(*[self.mathtex(eq, 35) for eq in equations])
        eqs.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        for eq in eqs:
            self.fit(eq, width - 0.82, 0.63)
        eqs.next_to(label, DOWN, buff=0.36, aligned_edge=LEFT)
        answer_box = RoundedRectangle(width=width - 0.72, height=0.82,
                                      corner_radius=0.14, stroke_color=accent,
                                      stroke_width=1.8, fill_color=PALE_MINT,
                                      fill_opacity=0.92)
        answer_mob = self.mathtex(answer, 36)
        self.fit(answer_mob, answer_box.width - 0.35, 0.50)
        answer_mob.move_to(answer_box)
        answer_group = VGroup(answer_box, answer_mob)
        answer_group.next_to(eqs, DOWN, buff=0.32, aligned_edge=LEFT)
        note_mob = self.text(note, 18, color=INK_SOFT)
        self.fit(note_mob, width - 0.82, 0.38)
        note_mob.next_to(answer_group, DOWN, buff=0.26, aligned_edge=LEFT)
        content = VGroup(label, eqs, answer_group, note_mob)
        if content.height > height - 0.52:
            content.scale_to_fit_height(height - 0.52)
        if content.width > width - 0.58:
            content.scale_to_fit_width(width - 0.58)
        content.move_to(panel).align_to(panel, LEFT).shift(RIGHT * 0.36)
        return VGroup(panel, accent_bar), label, eqs, VGroup(answer_group, note_mob)

    def reveal_solution(self, title: str, equations: list[str], answer: str,
                        accent: str, note: str) -> VGroup:
        bg, label, eqs, finish = self.build_solution_panel(title, equations, answer, accent, note)
        self.fixed(bg, label)
        self.play(FadeIn(bg), FadeIn(label), run_time=RUN_FAST)
        for eq in eqs:
            self.fixed(eq)
            self.play(Write(eq), run_time=RUN)
            self.wait(PAUSE_READ)
        self.fixed(finish)
        self.play(FadeIn(finish[0], shift=UP * 0.05), run_time=RUN)
        self.play(FadeIn(finish[1]), run_time=RUN_FAST)
        self.wait(PAUSE_ANSWER)
        return VGroup(bg, label, eqs, finish)

    def technical_floor(self, center: np.ndarray) -> VGroup:
        plane = NumberPlane(
            x_range=[-3.5, 3.5, 1], y_range=[-2.6, 2.6, 1],
            x_length=7.0, y_length=5.2,
            axis_config={"stroke_color": GRID_DARK, "stroke_width": 1.0,
                         "stroke_opacity": 0.42, "include_ticks": False},
            background_line_style={"stroke_color": GRID, "stroke_width": 1.0,
                                   "stroke_opacity": 0.42},
        ).shift(center + IN * 0.16)
        origin = center + LEFT * 2.95 + DOWN * 1.90 + OUT * 0.02
        triad = VGroup(
            Line3D(origin, origin + RIGHT * 0.46, thickness=0.015, color=BLUE),
            Line3D(origin, origin + UP * 0.46, thickness=0.015, color=MINT_DARK),
            Line3D(origin, origin + OUT * 0.46, thickness=0.015, color=ORANGE),
        )
        return VGroup(plane, triad)

    def dimension_line(self, start: np.ndarray, end: np.ndarray, *,
                       color: str = ORANGE, z_lift: float = 0.06,
                       tick: float = 0.16) -> VGroup:
        s = np.array(start, dtype=float) + OUT * z_lift
        e = np.array(end, dtype=float) + OUT * z_lift
        direction = e - s
        length = np.linalg.norm(direction[:2])
        if length <= 1e-6:
            raise ValueError("dimension line needs non-zero XY length")
        normal = np.array([-direction[1], direction[0], 0.0])
        normal = normal / np.linalg.norm(normal[:2])
        return VGroup(
            Line3D(s, e, thickness=0.020, color=color),
            Line3D(s - normal * tick, s + normal * tick, thickness=0.020, color=color),
            Line3D(e - normal * tick, e + normal * tick, thickness=0.020, color=color),
        )

    def camera_isometric(self, zoom: float = 0.93) -> None:
        self.set_camera_orientation(phi=62 * DEGREES, theta=-48 * DEGREES, zoom=zoom)

    def camera_top(self, zoom: float = 1.02) -> None:
        self.move_camera(phi=2 * DEGREES, theta=-90 * DEGREES, zoom=zoom, run_time=RUN_SLOW)

    def establish_model(self, stage: VGroup, strip: VGroup) -> None:
        self.play(FadeIn(stage[0]), run_time=RUN_FAST)
        self.play(LaggedStart(*[FadeIn(m) for m in stage[1:]], lag_ratio=0.08), run_time=RUN_SLOW)
        self.play(FadeIn(strip, shift=UP * 0.06), run_time=RUN)
        self.wait(PAUSE_THINK)

    def prepare_solution_view(self, stage: VGroup, strip: VGroup) -> None:
        self.play(FadeOut(strip), run_time=RUN_FAST)
        self.camera_top(zoom=1.00)
        self.play(stage.animate.shift(LEFT * 2.40), run_time=RUN_SLOW)
        self.wait(0.55)

    def clear_problem(self, stage: VGroup, solution: VGroup | None = None) -> None:
        animations = [FadeOut(stage)]
        if solution is not None:
            animations.append(FadeOut(solution))
        self.play(*animations, run_time=RUN)
        self.remove(stage)
        if solution is not None:
            self.remove(solution)
        self.camera_isometric()

    def garden_model(self, center: np.ndarray) -> VGroup:
        base = Cylinder(radius=1.92, height=0.20, direction=OUT,
                        fill_color=STONE, fill_opacity=0.88,
                        stroke_color=STONE_DARK, stroke_width=0.9,
                        resolution=(48, 8)).shift(center)
        grass = Cylinder(radius=1.74, height=0.18, direction=OUT,
                         fill_color=MINT, fill_opacity=0.90,
                         stroke_color=MINT_DARK, stroke_width=0.8,
                         resolution=(48, 8)).shift(center + OUT * 0.17)
        curb = Torus(major_radius=1.83, minor_radius=0.075,
                     fill_color=STONE_DARK, fill_opacity=0.95,
                     stroke_color=STONE_DARK, stroke_width=0.4,
                     resolution=(36, 12)).shift(center + OUT * 0.27)
        boundary = Circle(radius=1.74, color=ORANGE_DARK,
                          stroke_width=5.0).shift(center + OUT * 0.29)
        radius = self.dimension_line(center, center + RIGHT * 1.74,
                                     color=ORANGE, z_lift=0.31)
        center_dot = Dot3D(point=center + OUT * 0.32, radius=0.045, color=INK)
        return VGroup(base, grass, curb, boundary, radius, center_dot)

    def pool_model(self, center: np.ndarray) -> VGroup:
        shell = Cylinder(radius=1.95, height=0.52, direction=OUT,
                         fill_color=STONE, fill_opacity=0.88,
                         stroke_color=STONE_DARK, stroke_width=0.9,
                         resolution=(48, 10)).shift(center)
        water = Cylinder(radius=1.70, height=0.08, direction=OUT,
                         fill_color=WATER, fill_opacity=0.86,
                         stroke_color=BLUE, stroke_width=0.7,
                         resolution=(48, 6)).shift(center + OUT * 0.28)
        rim = Torus(major_radius=1.82, minor_radius=0.075,
                    fill_color=STONE_DARK, fill_opacity=0.95,
                    stroke_color=STONE_DARK, stroke_width=0.4,
                    resolution=(36, 12)).shift(center + OUT * 0.34)
        diameter = self.dimension_line(center + LEFT * 1.70,
                                       center + RIGHT * 1.70,
                                       color=ORANGE, z_lift=0.37, tick=0.18)
        return VGroup(shell, water, rim, diameter)

    def fountain_walkway_model(self, center: np.ndarray) -> VGroup:
        inner = 1.18
        outer = 2.02
        base = Cylinder(radius=outer, height=0.12, direction=OUT,
                        fill_color=STONE, fill_opacity=0.80,
                        stroke_color=STONE_DARK, stroke_width=0.7,
                        resolution=(48, 6)).shift(center)
        walkway = Annulus(inner_radius=inner, outer_radius=outer,
                          fill_color=CYAN, fill_opacity=0.72,
                          stroke_color=STONE_DARK, stroke_width=1.0)
        walkway.shift(center + OUT * 0.10)
        fountain = Cylinder(radius=inner, height=0.34, direction=OUT,
                            fill_color=WATER, fill_opacity=0.88,
                            stroke_color=BLUE, stroke_width=0.8,
                            resolution=(48, 8)).shift(center + OUT * 0.14)
        joints = VGroup()
        for k in range(16):
            a = TAU * k / 16
            p1 = center + np.array([inner * math.cos(a), inner * math.sin(a), 0.13])
            p2 = center + np.array([outer * math.cos(a), outer * math.sin(a), 0.13])
            joints.add(Line3D(p1, p2, thickness=0.008, color=GRID_DARK))
        mid_ring = Circle(radius=(inner + outer) / 2, color=GRID_DARK,
                          stroke_width=1.3).shift(center + OUT * 0.13)
        radii = VGroup(
            self.dimension_line(center, center + RIGHT * inner,
                                color=BLUE, z_lift=0.33, tick=0.13),
            self.dimension_line(center, center + UP * outer,
                                color=ORANGE, z_lift=0.16, tick=0.13),
        )
        return VGroup(base, walkway, fountain, joints, mid_ring, radii)

    def patio_model(self, center: np.ndarray) -> VGroup:
        side = 4.60
        fountain_r = 1.53
        slab = Prism(dimensions=[side, side, 0.18],
                     fill_color=STONE, fill_opacity=0.80,
                     stroke_color=STONE_DARK, stroke_width=0.9).shift(center)
        tile_outline = Difference(Square(side_length=side), Circle(radius=fountain_r))
        tile_outline.set_fill(PALE_BLUE, opacity=0.86)
        tile_outline.set_stroke(BLUE, width=1.2)
        tile_outline.shift(center + OUT * 0.12)
        fountain = Cylinder(radius=fountain_r, height=0.34, direction=OUT,
                            fill_color=CYAN, fill_opacity=0.86,
                            stroke_color=BLUE, stroke_width=0.8,
                            resolution=(48, 8)).shift(center + OUT * 0.13)
        square_dim = self.dimension_line(center + LEFT * side / 2 + DOWN * side / 2,
                                         center + RIGHT * side / 2 + DOWN * side / 2,
                                         color=ORANGE, z_lift=0.24, tick=0.16)
        circle_dim = self.dimension_line(center + LEFT * fountain_r,
                                         center + RIGHT * fountain_r,
                                         color=BLUE, z_lift=0.36, tick=0.13)
        return VGroup(slab, tile_outline, fountain, square_dim, circle_dim)

    def rug_model(self, center: np.ndarray) -> VGroup:
        rug = Cylinder(radius=1.90, height=0.10, direction=OUT,
                       fill_color=BLUE, fill_opacity=0.82,
                       stroke_color=INK_SOFT, stroke_width=0.8,
                       resolution=(48, 6)).shift(center)
        motif = VGroup()
        for radius in (0.62, 1.15, 1.62):
            motif.add(Circle(radius=radius, color=PALE_BLUE,
                             stroke_width=2.0).shift(center + OUT * 0.07))
        for k in range(8):
            a = TAU * k / 8
            p1 = center + np.array([0.64 * math.cos(a), 0.64 * math.sin(a), 0.075])
            p2 = center + np.array([1.58 * math.cos(a), 1.58 * math.sin(a), 0.075])
            motif.add(Line3D(p1, p2, thickness=0.008, color=PALE_BLUE))
        radius_dim = self.dimension_line(center, center + RIGHT * 1.90,
                                         color=ORANGE, z_lift=0.10, tick=0.15)
        return VGroup(rug, motif, radius_dim)

    def construct(self) -> None:
        self.camera_isometric()
        self.opening()
        self.problem_garden()
        self.problem_pool()
        self.problem_walkway()
        self.problem_patio()
        self.problem_inverse()
        self.closing()

    def opening(self) -> None:
        eyebrow = self.text("GEOMETRY 8 · CIRCLE WORKSHOP", 18, BOLD, color=BLUE).move_to(UP * 4.02)
        title = self.text("REAL CIRCLE PROBLEMS · TECHNICAL 3D", 40, BOLD, color=INK)
        self.fit(title, 13.0, 0.62)
        title.move_to(UP * 3.48)
        subtitle = self.text("Read the object first. Then turn the geometry into a formula.",
                             22, color=INK_SOFT).move_to(UP * 2.92)
        rule = Line(LEFT * 6.6, RIGHT * 6.6, color=GRID_DARK,
                    stroke_width=1.5).move_to(UP * 2.56)
        header = VGroup(eyebrow, title, subtitle, rule)
        self.fixed(header)
        center = DOWN * 0.35
        floor = self.technical_floor(center)
        disk = Cylinder(radius=1.72, height=0.24, direction=OUT,
                        fill_color=CYAN, fill_opacity=0.82,
                        stroke_color=INK_SOFT, stroke_width=0.8,
                        resolution=(48, 8)).shift(center + OUT * 0.05)
        boundary = Torus(major_radius=1.70, minor_radius=0.065,
                         fill_color=ORANGE, fill_opacity=0.96,
                         stroke_color=ORANGE_DARK, stroke_width=0.4,
                         resolution=(36, 12)).shift(center + OUT * 0.22)
        radius = self.dimension_line(center, center + RIGHT * 1.70,
                                     color=ORANGE, z_lift=0.26)
        model = VGroup(floor, disk, boundary, radius)
        strip = self.data_strip([
            ("BOUNDARY  →  C", ORANGE, 3.65),
            ("REGION  →  A", CYAN, 3.65),
            ("RADIUS  →  r", MINT_DARK, 3.65),
        ])
        self.play(FadeIn(floor), FadeIn(disk), run_time=RUN)
        self.play(Create(boundary), FadeIn(radius), run_time=RUN_SLOW)
        self.play(FadeIn(strip, shift=UP * 0.05), run_time=RUN)
        self.move_camera(phi=55 * DEGREES, theta=-60 * DEGREES,
                         zoom=1.03, run_time=RUN_SLOW)
        self.wait(2.8)
        self.camera_top(zoom=1.04)
        self.wait(1.5)
        self.play(FadeOut(model), FadeOut(strip), FadeOut(header), run_time=RUN)
        self.remove(model, strip, header)
        self.camera_isometric()

    def problem_garden(self) -> None:
        data = ProblemData(1, "BOUNDARY VS REGION", "Circular garden · fence or grass?",
                           "Radius = 4 m. Find the fence length around the garden and the grass area inside it.",
                           MINT_DARK)
        self.set_header(data)
        center = DOWN * 0.30
        stage = VGroup(self.technical_floor(center), self.garden_model(center))
        strip = self.data_strip([
            ("GIVEN  r = 4 m", MINT_DARK, 3.55),
            ("FENCE  →  C", ORANGE, 3.55),
            ("GRASS  →  A", CYAN, 3.55),
        ])
        self.establish_model(stage, strip)
        self.move_camera(phi=54 * DEGREES, theta=-60 * DEGREES,
                         zoom=1.02, run_time=RUN_SLOW)
        self.prepare_solution_view(stage, strip)
        solution = self.reveal_solution(
            "MODEL → SOLVE",
            [r"C=2\pi r=2\pi(4)=8\pi", r"C\approx25.13\,\mathrm{m}",
             r"A=\pi r^2=\pi(4)^2=16\pi", r"A\approx50.27\,\mathrm{m}^2"],
            r"\boxed{C\approx25.13\,\mathrm{m}\quad A\approx50.27\,\mathrm{m}^2}",
            MINT_DARK, "Check: fence uses m; grass uses m².")
        self.clear_problem(stage, solution)

    def problem_pool(self) -> None:
        data = ProblemData(2, "DIAMETER → RADIUS", "Round pool cover · diameter is not radius",
                           "Diameter = 10 m. How many square meters of material are needed to cover the pool?",
                           BLUE)
        self.set_header(data)
        center = DOWN * 0.30
        stage = VGroup(self.technical_floor(center), self.pool_model(center))
        strip = self.data_strip([
            ("GIVEN  d = 10 m", BLUE, 3.55),
            ("FIRST  r = d/2", ORANGE, 3.55),
            ("THEN  A = πr²", CYAN, 3.55),
        ])
        self.establish_model(stage, strip)
        self.move_camera(phi=52 * DEGREES, theta=-56 * DEGREES,
                         zoom=1.02, run_time=RUN_SLOW)
        self.prepare_solution_view(stage, strip)
        solution = self.reveal_solution(
            "CONVERT → AREA",
            [r"r=\frac{d}{2}=\frac{10}{2}=5\,\mathrm{m}", r"A=\pi r^2",
             r"A=\pi(5)^2=25\pi"],
            r"\boxed{A\approx78.54\,\mathrm{m}^2}", BLUE,
            "Area needs the radius, not the diameter.")
        self.clear_problem(stage, solution)

    def problem_walkway(self) -> None:
        data = ProblemData(3, "ANNULUS / RING", "Walkway around a fountain · subtract two circles",
                           "Inner radius = 3 m and outer radius = 5 m. Find only the walkway area.",
                           ORANGE_DARK)
        self.set_header(data)
        center = DOWN * 0.28
        stage = VGroup(self.technical_floor(center), self.fountain_walkway_model(center))
        strip = self.data_strip([
            ("OUTER  R = 5 m", ORANGE, 3.55),
            ("INNER  r = 3 m", BLUE, 3.55),
            ("RING  =  BIG − SMALL", CYAN, 4.10),
        ])
        self.establish_model(stage, strip)
        self.move_camera(phi=56 * DEGREES, theta=-52 * DEGREES,
                         zoom=1.00, run_time=RUN_SLOW)
        self.prepare_solution_view(stage, strip)
        solution = self.reveal_solution(
            "BIG CIRCLE − SMALL CIRCLE",
            [r"A=\pi R^2-\pi r^2", r"A=\pi(5^2-3^2)",
             r"A=\pi(25-9)=16\pi"],
            r"\boxed{A\approx50.27\,\mathrm{m}^2}", ORANGE_DARK,
            "Only the ring is counted; the fountain is removed.")
        self.clear_problem(stage, solution)

    def problem_patio(self) -> None:
        data = ProblemData(4, "COMPOSITE AREA", "Square patio with a circular fountain",
                           "Patio = 12 m × 12 m; fountain diameter = 8 m. Find the remaining tile area.",
                           CYAN)
        self.set_header(data)
        center = DOWN * 0.30
        stage = VGroup(self.technical_floor(center), self.patio_model(center))
        strip = self.data_strip([
            ("SQUARE  12 × 12", CYAN, 3.75),
            ("FOUNTAIN  d = 8 m", BLUE, 3.75),
            ("TILE  =  WHOLE − HOLE", ORANGE, 4.25),
        ])
        self.establish_model(stage, strip)
        self.move_camera(phi=58 * DEGREES, theta=-48 * DEGREES,
                         zoom=0.98, run_time=RUN_SLOW)
        self.prepare_solution_view(stage, strip)
        solution = self.reveal_solution(
            "WHOLE − HOLE",
            [r"A_{\rm square}=12^2=144", r"r=\frac{8}{2}=4\,\mathrm{m}",
             r"A_{\rm fountain}=\pi(4)^2=16\pi", r"A_{\rm tile}=144-16\pi"],
            r"\boxed{A_{\rm tile}\approx93.73\,\mathrm{m}^2}", CYAN,
            "Composite area = total region − circular hole.")
        self.clear_problem(stage, solution)

    def problem_inverse(self) -> None:
        data = ProblemData(5, "INVERSE AREA", "Round rug · work backward from area",
                           "Area = 78.54 m². Estimate the rug radius and diameter.", BLUE)
        self.set_header(data)
        center = DOWN * 0.30
        stage = VGroup(self.technical_floor(center), self.rug_model(center))
        strip = self.data_strip([
            ("GIVEN  A = 78.54 m²", BLUE, 4.15),
            ("UNDO  ×π", ORANGE, 3.25),
            ("UNDO  SQUARE  →  √", MINT_DARK, 4.15),
        ])
        self.establish_model(stage, strip)
        self.move_camera(phi=50 * DEGREES, theta=-55 * DEGREES,
                         zoom=1.03, run_time=RUN_SLOW)
        self.prepare_solution_view(stage, strip)
        solution = self.reveal_solution(
            "ISOLATE r",
            [r"78.54=\pi r^2", r"r^2=\frac{78.54}{\pi}\approx25",
             r"r\approx\sqrt{25}=5\,\mathrm{m}", r"d=2r\approx10\,\mathrm{m}"],
            r"\boxed{r\approx5\,\mathrm{m}\quad d\approx10\,\mathrm{m}}", BLUE,
            "Inverse problems reverse the operations in A = πr².")
        self.clear_problem(stage, solution)

    def closing(self) -> None:
        data = ProblemData(6, "CHECKLIST", "Circle problem strategy",
                           "Use the drawing to identify the quantity before choosing a formula.",
                           MINT_DARK)
        self.set_header(data)
        cards = VGroup(
            self.pill("1 · IDENTIFY  boundary or region", BLUE, 5.25, PALE_BLUE),
            self.pill("2 · CONVERT  d ↔ r when needed", ORANGE, 5.25, PALE_ORANGE),
            self.pill("3 · COMPOSE  whole − hole", CYAN, 5.25, PALE_BLUE),
            self.pill("4 · CHECK  m vs m²", MINT_DARK, 5.25, PALE_MINT),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.42, 0.42))
        cards.move_to(UP * 0.25)
        formula_box = RoundedRectangle(width=11.20, height=1.25,
                                       corner_radius=0.18, stroke_color=GRID_DARK,
                                       stroke_width=1.5, fill_color=WHITE_CARD,
                                       fill_opacity=0.98).move_to(DOWN * 2.10)
        formulas = VGroup(
            self.mathtex(r"C=2\pi r=\pi d", 41),
            self.mathtex(r"A=\pi r^2", 43),
            self.mathtex(r"A_{\rm ring}=\pi(R^2-r^2)", 38),
        ).arrange(RIGHT, buff=0.70)
        self.fit(formulas, 10.65, 0.70)
        formulas.move_to(formula_box)
        summary = VGroup(formula_box, formulas)
        self.fixed(cards, summary)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.05) for card in cards],
                              lag_ratio=0.14), run_time=RUN_SLOW)
        self.wait(2.0)
        self.play(FadeIn(formula_box), run_time=RUN_FAST)
        self.play(Write(formulas), run_time=RUN_SLOW)
        self.wait(PAUSE_FINAL)
