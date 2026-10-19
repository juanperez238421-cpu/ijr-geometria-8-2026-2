#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Circle problems, 2D-only senior-QA edition.

Design goals
------------
* No 3D objects in the problems.
* Pure black text and black technical linework on a white background.
* Large projector-safe 2D diagrams with explicit shaded/hatched target regions.
* Clear separation between geometry, dimensions, target area, formula and answer.
* Smooth build order: CONTEXT -> DRAW -> DIMENSIONS -> TARGET REGION -> MODEL -> SOLVE.
* No morphing between unrelated geometries; every transition is spatially stable.

Target: Manim Community Edition 0.20.x.
Final render protocol:
    manim -pqh Geometry8_Circle_2D_Only_Workshop.py \
        Geometry8Circle2DOnlyWorkshop --format=mp4 --disable_caching \
        --fps 30 --resolution 1920,1080
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass

from manim import *


TIME_SCALE = float(os.getenv("LESSON_TIME_SCALE", "1.0"))

BG = "#FFFFFF"
BLACK_INK = "#000000"
DARK_GRAY = "#444444"
MID_GRAY = "#A9A9A9"
LIGHT_GRAY = "#E6E6E6"
VERY_LIGHT = "#F5F5F5"
GRID_GRAY = "#D8D8D8"

RUN_FAST = 0.45
RUN = 0.82
RUN_SLOW = 1.25
PAUSE_SHORT = 0.70
PAUSE_READ = 1.15
PAUSE_THINK = 1.60
PAUSE_ANSWER = 1.80


@dataclass(frozen=True)
class Problem:
    number: int
    eyebrow: str
    title: str
    prompt: str


class Geometry8Circle2DOnlyWorkshop(Scene):
    """Clean 2D circle workshop for classroom projection."""

    def setup(self) -> None:
        super().setup()
        self.camera.background_color = BG
        self.header: VGroup | None = None
        self.validate_math()

    def play(self, *animations, **kwargs):
        if kwargs.get("run_time") is not None:
            kwargs["run_time"] *= TIME_SCALE
        return super().play(*animations, **kwargs)

    def wait(self, duration: float = DEFAULT_WAIT_TIME, *args, **kwargs):
        return super().wait(duration * TIME_SCALE, *args, **kwargs)

    @staticmethod
    def fit(mob: Mobject, max_width: float, max_height: float) -> Mobject:
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        if mob.height > max_height:
            mob.scale_to_fit_height(max_height)
        return mob

    def text(self, content: str, size: int = 28, weight=NORMAL, **kwargs) -> Text:
        kwargs.pop("color", None)
        return Text(
            content,
            font_size=size,
            color=BLACK_INK,
            weight=weight,
            line_spacing=0.95,
            **kwargs,
        )

    def mathtex(self, expression: str, size: int = 38, **kwargs) -> MathTex:
        kwargs.pop("color", None)
        return MathTex(expression, font_size=size, color=BLACK_INK, **kwargs)

    def validate_math(self) -> None:
        checks = [
            (2 * math.pi * 4, 25.132741),
            (math.pi * 4**2, 50.265482),
            (math.pi * 5**2, 78.539816),
            (math.pi * (5**2 - 3**2), 50.265482),
            (12**2 - math.pi * 4**2, 93.734518),
            (math.sqrt(78.54 / math.pi), 5.000006),
        ]
        for actual, expected in checks:
            if abs(actual - expected) > 0.03:
                raise ValueError(f"math validation failed: {actual} != {expected}")

    # ------------------------------------------------------------------
    # Global layout
    # ------------------------------------------------------------------
    def make_header(self, p: Problem) -> VGroup:
        eyebrow = self.text(f"PROBLEM {p.number:02d}  ·  {p.eyebrow}", 16, BOLD)
        eyebrow.move_to(UP * 3.95)

        title = self.text(p.title, 32, BOLD)
        self.fit(title, 12.1, 0.53)
        title.move_to(UP * 3.48)

        prompt = self.text(p.prompt, 19)
        self.fit(prompt, 12.6, 0.50)
        prompt.move_to(UP * 3.00)

        rule = Line(LEFT * 6.25, RIGHT * 6.25, color=GRID_GRAY, stroke_width=1.5)
        rule.move_to(UP * 2.64)
        return VGroup(eyebrow, title, prompt, rule)

    def set_header(self, p: Problem) -> None:
        new = self.make_header(p)
        if self.header is None:
            self.header = new
            self.play(FadeIn(new, shift=DOWN * 0.04), run_time=RUN_FAST)
        else:
            old = self.header
            self.header = new
            self.play(FadeOut(old, shift=UP * 0.03), FadeIn(new, shift=DOWN * 0.03), run_time=RUN_FAST)
            self.remove(old)

    def step_bar(self, active: int) -> VGroup:
        labels = ("DRAW", "READ", "SHADE", "MODEL", "SOLVE")
        items = VGroup()
        for i, label in enumerate(labels):
            box = RoundedRectangle(
                width=1.37, height=0.42, corner_radius=0.09,
                stroke_color=BLACK_INK,
                stroke_width=2.2 if i == active else 1.0,
                fill_color=VERY_LIGHT if i == active else BG,
                fill_opacity=1.0,
            )
            txt = self.text(label, 11, BOLD).move_to(box)
            items.add(VGroup(box, txt))
            if i < len(labels) - 1:
                items.add(Line(ORIGIN, RIGHT * 0.28, color=BLACK_INK, stroke_width=1.0))
        items.arrange(RIGHT, buff=0.08)
        items.move_to(DOWN * 3.68)
        return items

    def replace_step(self, old: VGroup, active: int) -> VGroup:
        new = self.step_bar(active)
        self.play(FadeOut(old), FadeIn(new), run_time=0.26)
        self.remove(old)
        return new

    def diagram_frame(self) -> RoundedRectangle:
        return RoundedRectangle(
            width=6.65, height=5.15, corner_radius=0.16,
            stroke_color=GRID_GRAY, stroke_width=1.25,
            fill_color=BG, fill_opacity=1.0,
        ).move_to(LEFT * 3.45 + DOWN * 0.12)

    def solution_frame(self) -> RoundedRectangle:
        return RoundedRectangle(
            width=5.52, height=5.15, corner_radius=0.16,
            stroke_color=GRID_GRAY, stroke_width=1.25,
            fill_color=BG, fill_opacity=1.0,
        ).move_to(RIGHT * 3.60 + DOWN * 0.12)

    def section_heading(self, text: str, at: list[float]) -> VGroup:
        line = Line(LEFT * 0.32, RIGHT * 0.32, color=BLACK_INK, stroke_width=3.2)
        label = self.text(text, 15, BOLD)
        g = VGroup(line, label).arrange(RIGHT, buff=0.13)
        g.move_to(at)
        return g

    # ------------------------------------------------------------------
    # Technical 2D primitives
    # ------------------------------------------------------------------
    def dimension(self, start, end, label: str, label_offset=UP * 0.30) -> VGroup:
        start = np.array(start, dtype=float)
        end = np.array(end, dtype=float)
        line = Line(start, end, color=BLACK_INK, stroke_width=2.4)
        v = end - start
        n = np.array([-v[1], v[0], 0.0])
        n = n / max(np.linalg.norm(n), 1e-8)
        tick = 0.16
        t1 = Line(start - n * tick, start + n * tick, color=BLACK_INK, stroke_width=2.1)
        t2 = Line(end - n * tick, end + n * tick, color=BLACK_INK, stroke_width=2.1)
        txt = self.mathtex(label, 29).move_to((start + end) / 2 + label_offset)
        return VGroup(line, t1, t2, txt)

    def leader_label(self, content: str, anchor, at, *, width: float = 2.40) -> VGroup:
        box = RoundedRectangle(
            width=width, height=0.52, corner_radius=0.09,
            stroke_color=BLACK_INK, stroke_width=1.25,
            fill_color=BG, fill_opacity=0.98,
        ).move_to(at)
        txt = self.text(content, 14, BOLD)
        self.fit(txt, width - 0.22, 0.30)
        txt.move_to(box)
        edge = box.get_left() if anchor[0] < at[0] else box.get_right()
        line = Line(anchor, edge, color=BLACK_INK, stroke_width=1.35)
        dot = Dot(anchor, radius=0.035, color=BLACK_INK)
        return VGroup(line, dot, box, txt)

    def hatch_disk(self, center, radius: float, spacing: float = 0.23) -> VGroup:
        lines = VGroup()
        y = -radius + spacing
        while y < radius:
            half = math.sqrt(max(radius * radius - y * y, 0.0))
            lines.add(Line(
                center + np.array([-half, y, 0.0]),
                center + np.array([half, y, 0.0]),
                color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42,
            ))
            y += spacing
        return lines

    def hatch_annulus(self, center, inner: float, outer: float, spacing: float = 0.22) -> VGroup:
        lines = VGroup()
        y = -outer + spacing
        while y < outer:
            xo = math.sqrt(max(outer * outer - y * y, 0.0))
            if abs(y) < inner:
                xi = math.sqrt(max(inner * inner - y * y, 0.0))
                lines.add(Line(center + np.array([-xo, y, 0]), center + np.array([-xi, y, 0]),
                               color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42))
                lines.add(Line(center + np.array([xi, y, 0]), center + np.array([xo, y, 0]),
                               color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42))
            else:
                lines.add(Line(center + np.array([-xo, y, 0]), center + np.array([xo, y, 0]),
                               color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42))
            y += spacing
        return lines

    def hatch_square_minus_circle(self, center, half: float, radius: float, spacing: float = 0.22) -> VGroup:
        lines = VGroup()
        y = -half + spacing
        while y < half:
            if abs(y) < radius:
                cut = math.sqrt(max(radius * radius - y * y, 0.0))
                lines.add(Line(center + np.array([-half, y, 0]), center + np.array([-cut, y, 0]),
                               color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42))
                lines.add(Line(center + np.array([cut, y, 0]), center + np.array([half, y, 0]),
                               color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42))
            else:
                lines.add(Line(center + np.array([-half, y, 0]), center + np.array([half, y, 0]),
                               color=BLACK_INK, stroke_width=1.0, stroke_opacity=0.42))
            y += spacing
        return lines

    def reveal_hatch(self, hatch: VGroup) -> None:
        self.play(
            LaggedStart(*[Create(line) for line in hatch], lag_ratio=0.028),
            run_time=1.15,
        )

    # ------------------------------------------------------------------
    # Solution panel
    # ------------------------------------------------------------------
    def solve_panel(self, given: str, formula: str, substitution: str, answer: str, note: str) -> VGroup:
        frame = self.solution_frame()
        heading = self.section_heading("MATHEMATICAL MODEL", [3.55, 2.02, 0])
        given_label = self.text(given, 18, BOLD).move_to([3.55, 1.42, 0])
        given_box = RoundedRectangle(
            width=4.76, height=0.60, corner_radius=0.10,
            stroke_color=BLACK_INK, stroke_width=1.2,
            fill_color=VERY_LIGHT, fill_opacity=1,
        ).move_to(given_label)
        given_group = VGroup(given_box, given_label)

        f1 = self.mathtex(formula, 35).move_to([3.55, 0.67, 0])
        f2 = self.mathtex(substitution, 33).move_to([3.55, -0.10, 0])

        answer_box = RoundedRectangle(
            width=4.76, height=0.82, corner_radius=0.12,
            stroke_color=BLACK_INK, stroke_width=2.0,
            fill_color=LIGHT_GRAY, fill_opacity=0.85,
        ).move_to([3.55, -1.02, 0])
        answer_m = self.mathtex(answer, 36).move_to(answer_box)
        self.fit(answer_m, 4.35, 0.48)

        note_m = self.text(note, 16)
        self.fit(note_m, 4.65, 0.56)
        note_m.move_to([3.55, -1.88, 0])

        self.play(FadeIn(frame), FadeIn(heading), run_time=RUN_FAST)
        self.play(FadeIn(given_group, shift=UP * 0.03), run_time=RUN_FAST)
        self.play(Write(f1), run_time=RUN)
        self.wait(PAUSE_SHORT)
        self.play(TransformFromCopy(f1, f2), run_time=RUN)
        self.wait(PAUSE_READ)
        self.play(FadeIn(answer_box, shift=UP * 0.03), Write(answer_m), run_time=RUN)
        self.play(FadeIn(note_m), run_time=RUN_FAST)
        self.wait(PAUSE_ANSWER)
        return VGroup(frame, heading, given_group, f1, f2, answer_box, answer_m, note_m)

    # ------------------------------------------------------------------
    # Opening
    # ------------------------------------------------------------------
    def intro(self) -> None:
        title = self.text("CIRCLE PROBLEMS · 2D ANALYSIS", 42, BOLD).move_to(UP * 1.65)
        sub = self.text("Draw the geometry. Shade the requested region. Then calculate.", 23)
        sub.move_to(UP * 0.93)
        rule = Line(LEFT * 4.75, RIGHT * 4.75, color=BLACK_INK, stroke_width=1.6).move_to(UP * 0.42)

        formulas = VGroup(
            self.mathtex(r"d=2r", 39),
            self.mathtex(r"C=2\pi r", 39),
            self.mathtex(r"A=\pi r^2", 39),
            self.mathtex(r"A_{\mathrm{ring}}=\pi(R^2-r^2)", 37),
        ).arrange(RIGHT, buff=0.65).move_to(DOWN * 0.48)
        self.fit(formulas, 11.7, 0.80)

        method = self.text("CONTEXT  →  DIAGRAM  →  TARGET REGION  →  FORMULA  →  ANSWER", 20, BOLD)
        method.move_to(DOWN * 1.58)

        self.play(Write(title), run_time=RUN)
        self.play(FadeIn(sub), Create(rule), run_time=RUN_FAST)
        self.play(LaggedStart(*[Write(x) for x in formulas], lag_ratio=0.14), run_time=1.55)
        self.play(FadeIn(method, shift=UP * 0.05), run_time=RUN)
        self.wait(PAUSE_THINK)
        self.play(FadeOut(VGroup(title, sub, rule, formulas, method)), run_time=0.62)

    # ------------------------------------------------------------------
    # Problem 1 — garden
    # ------------------------------------------------------------------
    def problem_garden(self) -> None:
        p = Problem(
            1, "RADIUS + AREA + CIRCUMFERENCE",
            "Circular garden: grass area and fence length",
            "A circular garden has radius 4 m. Find the grass area and the fence length around it.",
        )
        self.set_header(p)
        frame = self.diagram_frame()
        self.play(FadeIn(frame), run_time=RUN_FAST)
        step = self.step_bar(0)
        self.play(FadeIn(step), run_time=RUN_FAST)

        c = np.array([-3.45, -0.15, 0.0])
        r = 1.78
        outline = Circle(radius=r, color=BLACK_INK, stroke_width=4.2).move_to(c)
        center = Dot(c, radius=0.055, color=BLACK_INK)
        self.play(Create(outline), GrowFromCenter(center), run_time=1.10)

        step = self.replace_step(step, 1)
        dim = self.dimension(c, c + RIGHT * r, r"r=4\,\mathrm{m}", UP * 0.31)
        self.play(Create(dim[0]), Create(dim[1]), Create(dim[2]), Write(dim[3]), run_time=0.95)
        boundary_tag = self.leader_label("FENCE = OUTER BOUNDARY", c + LEFT * r * 0.92, [-3.70, 1.78, 0], width=2.78)
        self.play(FadeIn(boundary_tag), run_time=RUN_FAST)

        step = self.replace_step(step, 2)
        fill = Circle(radius=r, stroke_width=0, fill_color=LIGHT_GRAY, fill_opacity=0.72).move_to(c)
        fill.set_z_index(-2)
        self.add(fill)
        hatch = self.hatch_disk(c, r)
        self.reveal_hatch(hatch)
        area_tag = self.leader_label("SHADED DISK = GRASS", c + DOWN * 0.55, [-3.58, -2.18, 0], width=2.60)
        self.play(FadeIn(area_tag), run_time=RUN_FAST)
        self.play(Indicate(outline, color=BLACK_INK, scale_factor=1.035), run_time=0.70)

        step = self.replace_step(step, 3)
        panel = self.solve_panel(
            "Given: r = 4 m",
            r"A=\pi r^2\quad\text{and}\quad C=2\pi r",
            r"A=16\pi\approx 50.27\,\mathrm{m}^2\quad C=8\pi\approx25.13\,\mathrm{m}",
            r"\boxed{A\approx50.27\,\mathrm{m}^2\ ;\ C\approx25.13\,\mathrm{m}}",
            "Area uses square units; fence length uses linear units.",
        )
        step = self.replace_step(step, 4)
        self.wait(PAUSE_SHORT)
        self.play(FadeOut(panel), FadeOut(VGroup(fill, hatch, outline, center, dim, boundary_tag, area_tag, frame, step)), run_time=0.65)

    # ------------------------------------------------------------------
    # Problem 2 — pool
    # ------------------------------------------------------------------
    def problem_pool(self) -> None:
        p = Problem(
            2, "DIAMETER → RADIUS → AREA",
            "Round pool: how much cover material is needed?",
            "A circular pool has diameter 10 m. Find the area of the circular cover.",
        )
        self.set_header(p)
        frame = self.diagram_frame()
        self.play(FadeIn(frame), run_time=RUN_FAST)
        step = self.step_bar(0)
        self.play(FadeIn(step), run_time=RUN_FAST)

        c = np.array([-3.45, -0.15, 0.0])
        r = 1.78
        outline = Circle(radius=r, color=BLACK_INK, stroke_width=4.2).move_to(c)
        self.play(Create(outline), run_time=1.00)

        step = self.replace_step(step, 1)
        dim = self.dimension(c + LEFT * r, c + RIGHT * r, r"d=10\,\mathrm{m}", UP * 0.31)
        self.play(Create(dim[0]), Create(dim[1]), Create(dim[2]), Write(dim[3]), run_time=0.95)
        radius_hint = self.mathtex(r"r=\frac d2=5\,\mathrm{m}", 30).move_to([-3.45, 1.76, 0])
        self.play(Write(radius_hint), run_time=RUN)

        step = self.replace_step(step, 2)
        fill = Circle(radius=r, stroke_width=0, fill_color=LIGHT_GRAY, fill_opacity=0.72).move_to(c)
        fill.set_z_index(-2)
        self.add(fill)
        hatch = self.hatch_disk(c, r)
        self.reveal_hatch(hatch)
        tag = self.leader_label("SHADED DISK = COVER AREA", c + DOWN * 0.48, [-3.50, -2.18, 0], width=2.88)
        self.play(FadeIn(tag), run_time=RUN_FAST)

        step = self.replace_step(step, 3)
        panel = self.solve_panel(
            "Given: d = 10 m → r = 5 m",
            r"A=\pi r^2",
            r"A=\pi(5)^2=25\pi\approx78.54\,\mathrm{m}^2",
            r"\boxed{A\approx78.54\,\mathrm{m}^2}",
            "Convert diameter to radius before using the area formula.",
        )
        step = self.replace_step(step, 4)
        self.play(FadeOut(panel), FadeOut(VGroup(fill, hatch, outline, dim, radius_hint, tag, frame, step)), run_time=0.65)

    # ------------------------------------------------------------------
    # Problem 3 — annulus
    # ------------------------------------------------------------------
    def problem_walkway(self) -> None:
        p = Problem(
            3, "ANNULUS · OUTER AREA − INNER AREA",
            "Circular walkway around a fountain",
            "The fountain radius is 3 m and the outer walkway radius is 5 m. Find only the walkway area.",
        )
        self.set_header(p)
        frame = self.diagram_frame()
        self.play(FadeIn(frame), run_time=RUN_FAST)
        step = self.step_bar(0)
        self.play(FadeIn(step), run_time=RUN_FAST)

        c = np.array([-3.45, -0.15, 0.0])
        ro, ri = 1.90, 1.14
        outer = Circle(radius=ro, color=BLACK_INK, stroke_width=4.2).move_to(c)
        inner = Circle(radius=ri, color=BLACK_INK, stroke_width=3.4).move_to(c)
        center = Dot(c, radius=0.05, color=BLACK_INK)
        self.play(Create(outer), run_time=0.78)
        self.play(Create(inner), GrowFromCenter(center), run_time=0.78)

        step = self.replace_step(step, 1)
        dR = self.dimension(c, c + UP * ro, r"R=5\,\mathrm{m}", LEFT * 0.52)
        dr = self.dimension(c, c + RIGHT * ri, r"r=3\,\mathrm{m}", DOWN * 0.30)
        self.play(Create(dR[0]), Create(dR[1]), Create(dR[2]), Write(dR[3]), run_time=0.78)
        self.play(Create(dr[0]), Create(dr[1]), Create(dr[2]), Write(dr[3]), run_time=0.78)

        step = self.replace_step(step, 2)
        ring_fill = Annulus(inner_radius=ri, outer_radius=ro, stroke_width=0,
                            fill_color=LIGHT_GRAY, fill_opacity=0.74).move_to(c)
        ring_fill.set_z_index(-2)
        self.add(ring_fill)
        hatch = self.hatch_annulus(c, ri, ro)
        self.reveal_hatch(hatch)
        hole = Circle(radius=ri, stroke_color=BLACK_INK, stroke_width=2.0,
                      fill_color=BG, fill_opacity=1.0).move_to(c)
        self.add(hole)
        tag1 = self.leader_label("TARGET = WALKWAY RING", c + LEFT * 1.55, [-3.88, -2.22, 0], width=2.70)
        tag2 = self.leader_label("INNER CIRCLE = HOLE", c + RIGHT * 0.58, [-2.18, 1.72, 0], width=2.32)
        self.play(FadeIn(tag1), FadeIn(tag2), run_time=0.75)

        step = self.replace_step(step, 3)
        panel = self.solve_panel(
            "Given: R = 5 m, r = 3 m",
            r"A_{\mathrm{ring}}=\pi(R^2-r^2)",
            r"A=\pi(25-9)=16\pi\approx50.27\,\mathrm{m}^2",
            r"\boxed{A_{\mathrm{walkway}}\approx50.27\,\mathrm{m}^2}",
            "Subtract the inner circular hole from the outer circle.",
        )
        step = self.replace_step(step, 4)
        self.play(FadeOut(panel), FadeOut(VGroup(ring_fill, hatch, hole, outer, inner, center, dR, dr, tag1, tag2, frame, step)), run_time=0.68)

    # ------------------------------------------------------------------
    # Problem 4 — patio minus fountain
    # ------------------------------------------------------------------
    def problem_patio(self) -> None:
        p = Problem(
            4, "COMPOSITE AREA · SQUARE − CIRCLE",
            "Square patio with a circular fountain",
            "A 12 m × 12 m patio contains a circular fountain of diameter 8 m. Find the tiled area.",
        )
        self.set_header(p)
        frame = self.diagram_frame()
        self.play(FadeIn(frame), run_time=RUN_FAST)
        step = self.step_bar(0)
        self.play(FadeIn(step), run_time=RUN_FAST)

        c = np.array([-3.45, -0.12, 0.0])
        half, r = 2.02, 1.34
        square = Square(side_length=2 * half, color=BLACK_INK, stroke_width=4.2).move_to(c)
        circle = Circle(radius=r, color=BLACK_INK, stroke_width=3.8).move_to(c)
        self.play(Create(square), run_time=0.82)
        self.play(Create(circle), run_time=0.82)

        step = self.replace_step(step, 1)
        side_dim = self.dimension(c + LEFT * half + DOWN * half,
                                  c + RIGHT * half + DOWN * half,
                                  r"12\,\mathrm{m}", DOWN * 0.31)
        dia_dim = self.dimension(c + LEFT * r, c + RIGHT * r,
                                 r"d=8\,\mathrm{m}", UP * 0.30)
        self.play(Create(side_dim[0]), Create(side_dim[1]), Create(side_dim[2]), Write(side_dim[3]), run_time=0.78)
        self.play(Create(dia_dim[0]), Create(dia_dim[1]), Create(dia_dim[2]), Write(dia_dim[3]), run_time=0.78)

        step = self.replace_step(step, 2)
        square_fill = Square(side_length=2 * half, stroke_width=0,
                             fill_color=LIGHT_GRAY, fill_opacity=0.74).move_to(c)
        square_fill.set_z_index(-3)
        self.add(square_fill)
        hole = Circle(radius=r, stroke_width=0, fill_color=BG, fill_opacity=1.0).move_to(c)
        hole.set_z_index(-2)
        self.add(hole)
        hatch = self.hatch_square_minus_circle(c, half, r)
        self.reveal_hatch(hatch)
        self.bring_to_front(square, circle, side_dim, dia_dim)
        tag = self.leader_label("TILE = SQUARE − CIRCULAR HOLE", c + LEFT * 1.76, [-3.62, -2.40, 0], width=3.28)
        self.play(FadeIn(tag), run_time=RUN_FAST)

        step = self.replace_step(step, 3)
        panel = self.solve_panel(
            "Given: square 12 m; fountain d = 8 m → r = 4 m",
            r"A_{\mathrm{tile}}=12^2-\pi(4)^2",
            r"A=144-16\pi\approx93.73\,\mathrm{m}^2",
            r"\boxed{A_{\mathrm{tile}}\approx93.73\,\mathrm{m}^2}",
            "The shaded part is everything inside the square but outside the circle.",
        )
        step = self.replace_step(step, 4)
        self.play(FadeOut(panel), FadeOut(VGroup(square_fill, hole, hatch, square, circle, side_dim, dia_dim, tag, frame, step)), run_time=0.70)

    # ------------------------------------------------------------------
    # Problem 5 — inverse area
    # ------------------------------------------------------------------
    def problem_rug(self) -> None:
        p = Problem(
            5, "INVERSE AREA · FIND RADIUS",
            "Circular rug: recover radius from its area",
            "A circular rug has area 78.54 m². Estimate its radius and diameter.",
        )
        self.set_header(p)
        frame = self.diagram_frame()
        self.play(FadeIn(frame), run_time=RUN_FAST)
        step = self.step_bar(0)
        self.play(FadeIn(step), run_time=RUN_FAST)

        c = np.array([-3.45, -0.15, 0.0])
        r = 1.78
        outline = Circle(radius=r, color=BLACK_INK, stroke_width=4.2).move_to(c)
        self.play(Create(outline), run_time=0.95)

        step = self.replace_step(step, 1)
        radius_unknown = self.dimension(c, c + RIGHT * r, r"r=?", UP * 0.31)
        area_given = self.mathtex(r"A=78.54\,\mathrm{m}^2", 34).move_to(c + UP * 0.55)
        self.play(Create(radius_unknown[0]), Create(radius_unknown[1]), Create(radius_unknown[2]), Write(radius_unknown[3]), run_time=0.82)
        self.play(Write(area_given), run_time=RUN)

        step = self.replace_step(step, 2)
        fill = Circle(radius=r, stroke_width=0, fill_color=LIGHT_GRAY, fill_opacity=0.72).move_to(c)
        fill.set_z_index(-2)
        self.add(fill)
        hatch = self.hatch_disk(c, r)
        self.reveal_hatch(hatch)
        tag = self.leader_label("KNOWN AREA → UNKNOWN RADIUS", c + DOWN * 0.60, [-3.45, -2.18, 0], width=3.10)
        self.play(FadeIn(tag), run_time=RUN_FAST)

        step = self.replace_step(step, 3)
        panel = self.solve_panel(
            "Given: A = 78.54 m²",
            r"r=\sqrt{\frac{A}{\pi}}",
            r"r=\sqrt{\frac{78.54}{\pi}}\approx5.00\,\mathrm{m}\qquad d=2r",
            r"\boxed{r\approx5.00\,\mathrm{m}\ ;\ d\approx10.00\,\mathrm{m}}",
            "When area is known, isolate r by taking the square root.",
        )
        step = self.replace_step(step, 4)
        self.play(FadeOut(panel), FadeOut(VGroup(fill, hatch, outline, radius_unknown, area_given, tag, frame, step)), run_time=0.68)

    def outro(self) -> None:
        if self.header is not None:
            self.play(FadeOut(self.header), run_time=RUN_FAST)
            self.header = None
        title = self.text("CHECK THE REGION BEFORE YOU CALCULATE", 37, BOLD).move_to(UP * 1.55)
        rules = VGroup(
            self.text("1. Draw the exact 2D shape.", 22),
            self.text("2. Mark the given dimensions.", 22),
            self.text("3. Shade only the region requested.", 22),
            self.text("4. Choose the formula that matches that region.", 22),
            self.text("5. Check units: m for length, m² for area.", 22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.27).move_to(DOWN * 0.20)
        self.play(Write(title), run_time=RUN)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.05) for x in rules], lag_ratio=0.12), run_time=1.65)
        self.wait(2.20)

    def construct(self) -> None:
        self.intro()
        self.problem_garden()
        self.problem_pool()
        self.problem_walkway()
        self.problem_patio()
        self.problem_rug()
        self.outro()
