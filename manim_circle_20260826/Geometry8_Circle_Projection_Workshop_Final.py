#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final monochrome technical edition — Geometry 8 circle 3D→2D workshop.

QA goals:
* every textual element is pure black;
* physical 3D objects use neutral grayscale shading with crisp black edges;
* the relevant mathematical face is isolated before the orthographic top view;
* each 2D problem diagram explicitly shades/hatches the region being calculated;
* annular/composite problems visibly separate whole, hole, and target region.
"""
from __future__ import annotations

import math
import numpy as np
from manim import *

import Geometry8_Circle_Pi_Mixed_Workshop as b
import Geometry8_Circle_Projection_Workshop as m


# ---------------------------------------------------------------------------
# Runtime palette aliases used by the inherited projection choreography.
# All semantic annotation lines / borders are black; fills stay grayscale.
# ---------------------------------------------------------------------------
BLACK_INK = "#000000"
DARK_GRAY = "#4B4B4B"
MID_GRAY = "#8A8A8A"
LIGHT_GRAY_FILL = "#D7D7D7"
PALE_GRAY = "#EEEEEE"
PAPER = "#FFFFFF"
GRID_GRAY = "#D8D8D8"
GRID_DARK = "#AAAAAA"

for mod in (b, m):
    mod.INK = BLACK_INK
    mod.INK_SOFT = BLACK_INK
    mod.BLACK_TEXT = BLACK_INK
    mod.BG = PAPER

m.ACCENT_ORANGE = BLACK_INK
m.ACCENT_GREEN = BLACK_INK
m.ACCENT_RED = BLACK_INK
m.ACCENT_TEAL = BLACK_INK
m.ACCENT_BLUE = BLACK_INK
m.LIGHT_GRAY = GRID_DARK
m.WHITE_FILL = PAPER
m.VERY_LIGHT_GRAY = PALE_GRAY
m.PAPER_GRAY = LIGHT_GRAY_FILL
m.BLACK_LINE = BLACK_INK
m.RUN_QUICK = m.RUN_FAST
m.RUN_NORMAL = m.RUN
m.PAUSE_WORK = m.PAUSE_THINK


class Geometry8CircleProjectionWorkshopFinal(m.Geometry8CircleProjectionWorkshop):
    """Monochrome senior-QA render with shaded CAD objects and explicit area diagrams."""

    # ------------------------------------------------------------------
    # Typography: force every text / formula element to pure black.
    # ------------------------------------------------------------------
    def text(self, content: str, size: int = 28, weight=NORMAL, color=BLACK_INK, **kwargs) -> Text:
        kwargs.pop("color", None)
        return Text(
            content,
            font_size=size,
            color=BLACK_INK,
            weight=weight,
            line_spacing=0.95,
            **kwargs,
        )

    def mathtex(self, expression: str, size: int = 38, color=BLACK_INK, **kwargs) -> MathTex:
        kwargs.pop("color", None)
        return MathTex(expression, font_size=size, color=BLACK_INK, **kwargs)

    # ------------------------------------------------------------------
    # Technical helpers
    # ------------------------------------------------------------------
    def technical_floor(self, center: np.ndarray) -> VGroup:
        plane = NumberPlane(
            x_range=[-3.5, 3.5, 1],
            y_range=[-2.6, 2.6, 1],
            x_length=7.0,
            y_length=5.2,
            axis_config={
                "stroke_color": GRID_DARK,
                "stroke_width": 1.0,
                "stroke_opacity": 0.45,
                "include_ticks": False,
            },
            background_line_style={
                "stroke_color": GRID_GRAY,
                "stroke_width": 1.0,
                "stroke_opacity": 0.48,
            },
        ).shift(center + IN * 0.16)
        origin = center + LEFT * 2.95 + DOWN * 1.90 + OUT * 0.02
        triad = VGroup(
            Line3D(origin, origin + RIGHT * 0.46, thickness=0.014, color=BLACK_INK),
            Line3D(origin, origin + UP * 0.46, thickness=0.014, color=BLACK_INK),
            Line3D(origin, origin + OUT * 0.46, thickness=0.014, color=BLACK_INK),
        )
        return VGroup(plane, triad)

    def dimension_line(self, start: np.ndarray, end: np.ndarray, *,
                       color: str = BLACK_INK, z_lift: float = 0.06,
                       tick: float = 0.16) -> VGroup:
        return super().dimension_line(
            start, end, color=BLACK_INK, z_lift=z_lift, tick=tick
        )

    def _rot(self, point: np.ndarray, angle: float) -> np.ndarray:
        c, s = math.cos(angle), math.sin(angle)
        x, y = float(point[0]), float(point[1])
        return np.array([c * x - s * y, s * x + c * y, 0.0])

    def hatch_disk(self, center: np.ndarray, radius: float, *,
                   spacing: float = 0.24, angle: float = 45 * DEGREES,
                   opacity: float = 0.42) -> VGroup:
        """Parallel technical hatching clipped analytically to a disk."""
        lines = VGroup()
        y = -radius + spacing
        while y < radius:
            half = math.sqrt(max(radius * radius - y * y, 0.0))
            a = self._rot(np.array([-half, y, 0.0]), angle) + center
            c = self._rot(np.array([half, y, 0.0]), angle) + center
            lines.add(Line(a, c, color=BLACK_INK, stroke_width=1.15, stroke_opacity=opacity))
            y += spacing
        return lines

    def hatch_annulus(self, center: np.ndarray, inner: float, outer: float, *,
                      spacing: float = 0.22, angle: float = 45 * DEGREES,
                      opacity: float = 0.42) -> VGroup:
        """Parallel hatching clipped to an annulus; the inner circle remains empty."""
        lines = VGroup()
        y = -outer + spacing
        while y < outer:
            out_x = math.sqrt(max(outer * outer - y * y, 0.0))
            segments = []
            if abs(y) < inner:
                in_x = math.sqrt(max(inner * inner - y * y, 0.0))
                segments = [(-out_x, -in_x), (in_x, out_x)]
            else:
                segments = [(-out_x, out_x)]
            for x1, x2 in segments:
                a = self._rot(np.array([x1, y, 0.0]), angle) + center
                c = self._rot(np.array([x2, y, 0.0]), angle) + center
                lines.add(Line(a, c, color=BLACK_INK, stroke_width=1.15, stroke_opacity=opacity))
            y += spacing
        return lines

    def hatch_square_minus_circle(self, center: np.ndarray, side: float, radius: float, *,
                                  spacing: float = 0.23, opacity: float = 0.40) -> VGroup:
        """Horizontal hatching for the square region outside a circular hole."""
        lines = VGroup()
        half = side / 2
        y = -half + spacing
        while y < half:
            if abs(y) < radius:
                cut = math.sqrt(max(radius * radius - y * y, 0.0))
                lines.add(Line(center + np.array([-half, y, 0]),
                               center + np.array([-cut, y, 0]),
                               color=BLACK_INK, stroke_width=1.1, stroke_opacity=opacity))
                lines.add(Line(center + np.array([cut, y, 0]),
                               center + np.array([half, y, 0]),
                               color=BLACK_INK, stroke_width=1.1, stroke_opacity=opacity))
            else:
                lines.add(Line(center + np.array([-half, y, 0]),
                               center + np.array([half, y, 0]),
                               color=BLACK_INK, stroke_width=1.1, stroke_opacity=opacity))
            y += spacing
        return lines

    def area_tag(self, text: str, at: np.ndarray, *, width: float = 2.45) -> VGroup:
        box = RoundedRectangle(
            width=width, height=0.55, corner_radius=0.10,
            stroke_color=BLACK_INK, stroke_width=1.4,
            fill_color=PAPER, fill_opacity=0.96,
        )
        label = self.text(text, 15, BOLD).move_to(box)
        self.fit(label, width - 0.24, 0.32)
        return VGroup(box, label).move_to(at)

    # ------------------------------------------------------------------
    # 3D models: grayscale shading + explicit black silhouette / feature edges.
    # ------------------------------------------------------------------
    def garden_model(self, center: np.ndarray) -> VGroup:
        base = Cylinder(radius=1.94, height=0.22, direction=OUT,
                        fill_color=DARK_GRAY, fill_opacity=0.88,
                        stroke_color=BLACK_INK, stroke_width=1.4,
                        resolution=(64, 10)).shift(center)
        grass = Cylinder(radius=1.74, height=0.18, direction=OUT,
                         fill_color=LIGHT_GRAY_FILL, fill_opacity=0.98,
                         stroke_color=BLACK_INK, stroke_width=1.3,
                         resolution=(64, 8)).shift(center + OUT * 0.18)
        rim = Torus(major_radius=1.84, minor_radius=0.075,
                    fill_color=MID_GRAY, fill_opacity=1,
                    stroke_color=BLACK_INK, stroke_width=0.8,
                    resolution=(48, 16)).shift(center + OUT * 0.29)
        outer_edge = Circle(radius=1.74, color=BLACK_INK, stroke_width=5.2).shift(center + OUT * 0.31)
        inner_edge = Circle(radius=1.62, color=BLACK_INK, stroke_width=1.1,
                            stroke_opacity=0.45).shift(center + OUT * 0.315)
        radius = self.dimension_line(center, center + RIGHT * 1.74, z_lift=0.34)
        dot = Dot3D(center + OUT * 0.35, radius=0.045, color=BLACK_INK)
        return VGroup(base, grass, rim, outer_edge, inner_edge, radius, dot)

    def pool_model(self, center: np.ndarray) -> VGroup:
        shell = Cylinder(radius=1.96, height=0.55, direction=OUT,
                         fill_color=DARK_GRAY, fill_opacity=0.84,
                         stroke_color=BLACK_INK, stroke_width=1.5,
                         resolution=(64, 12)).shift(center)
        water = Cylinder(radius=1.70, height=0.09, direction=OUT,
                         fill_color=LIGHT_GRAY_FILL, fill_opacity=0.98,
                         stroke_color=BLACK_INK, stroke_width=1.3,
                         resolution=(64, 8)).shift(center + OUT * 0.30)
        rim = Torus(major_radius=1.83, minor_radius=0.08,
                    fill_color=MID_GRAY, fill_opacity=1,
                    stroke_color=BLACK_INK, stroke_width=0.8,
                    resolution=(48, 16)).shift(center + OUT * 0.36)
        top_edge = Circle(radius=1.70, color=BLACK_INK, stroke_width=4.6).shift(center + OUT * 0.39)
        diameter = self.dimension_line(center + LEFT * 1.70, center + RIGHT * 1.70,
                                       z_lift=0.42, tick=0.18)
        return VGroup(shell, water, rim, top_edge, diameter)

    def fountain_walkway_model(self, center: np.ndarray) -> VGroup:
        inner, outer = 1.18, 2.02
        base = Cylinder(radius=outer, height=0.13, direction=OUT,
                        fill_color=DARK_GRAY, fill_opacity=0.82,
                        stroke_color=BLACK_INK, stroke_width=1.4,
                        resolution=(64, 8)).shift(center)
        walkway = Annulus(inner_radius=inner, outer_radius=outer,
                          fill_color=LIGHT_GRAY_FILL, fill_opacity=0.96,
                          stroke_color=BLACK_INK, stroke_width=1.4).shift(center + OUT * 0.11)
        fountain = Cylinder(radius=inner, height=0.34, direction=OUT,
                            fill_color=MID_GRAY, fill_opacity=0.93,
                            stroke_color=BLACK_INK, stroke_width=1.4,
                            resolution=(64, 10)).shift(center + OUT * 0.14)
        outer_edge = Circle(radius=outer, color=BLACK_INK, stroke_width=4.4).shift(center + OUT * 0.15)
        inner_edge = Circle(radius=inner, color=BLACK_INK, stroke_width=4.0).shift(center + OUT * 0.34)
        joints = VGroup()
        for k in range(16):
            a = TAU * k / 16
            p1 = center + np.array([inner * math.cos(a), inner * math.sin(a), 0.14])
            p2 = center + np.array([outer * math.cos(a), outer * math.sin(a), 0.14])
            joints.add(Line3D(p1, p2, thickness=0.009, color=BLACK_INK))
        radii = VGroup(
            self.dimension_line(center, center + RIGHT * inner, z_lift=0.37, tick=0.13),
            self.dimension_line(center, center + UP * outer, z_lift=0.18, tick=0.13),
        )
        return VGroup(base, walkway, fountain, outer_edge, inner_edge, joints, radii)

    def patio_model(self, center: np.ndarray) -> VGroup:
        side, r = 4.60, 1.53
        slab = Prism(dimensions=[side, side, 0.20],
                     fill_color=DARK_GRAY, fill_opacity=0.82,
                     stroke_color=BLACK_INK, stroke_width=1.5).shift(center)
        remaining = Difference(Square(side_length=side), Circle(radius=r))
        remaining.set_fill(LIGHT_GRAY_FILL, opacity=0.97).set_stroke(BLACK_INK, width=1.5)
        remaining.shift(center + OUT * 0.13)
        fountain = Cylinder(radius=r, height=0.35, direction=OUT,
                            fill_color=MID_GRAY, fill_opacity=0.95,
                            stroke_color=BLACK_INK, stroke_width=1.5,
                            resolution=(64, 10)).shift(center + OUT * 0.14)
        square_edge = Square(side_length=side, color=BLACK_INK, stroke_width=4.0).shift(center + OUT * 0.15)
        circle_edge = Circle(radius=r, color=BLACK_INK, stroke_width=4.0).shift(center + OUT * 0.34)
        square_dim = self.dimension_line(center + LEFT * side / 2 + DOWN * side / 2,
                                         center + RIGHT * side / 2 + DOWN * side / 2,
                                         z_lift=0.27, tick=0.16)
        circle_dim = self.dimension_line(center + LEFT * r, center + RIGHT * r,
                                         z_lift=0.38, tick=0.13)
        return VGroup(slab, remaining, fountain, square_edge, circle_edge, square_dim, circle_dim)

    def rug_model(self, center: np.ndarray) -> VGroup:
        rug = Cylinder(radius=1.90, height=0.11, direction=OUT,
                       fill_color=LIGHT_GRAY_FILL, fill_opacity=0.98,
                       stroke_color=BLACK_INK, stroke_width=1.5,
                       resolution=(64, 8)).shift(center)
        edge = Circle(radius=1.90, color=BLACK_INK, stroke_width=4.6).shift(center + OUT * 0.08)
        rings = VGroup(*[
            Circle(radius=rr, color=BLACK_INK, stroke_width=1.2, stroke_opacity=0.42)
            .shift(center + OUT * 0.08)
            for rr in (0.62, 1.15, 1.62)
        ])
        spokes = VGroup()
        for k in range(8):
            a = TAU * k / 8
            p1 = center + np.array([0.62 * math.cos(a), 0.62 * math.sin(a), 0.085])
            p2 = center + np.array([1.62 * math.cos(a), 1.62 * math.sin(a), 0.085])
            spokes.add(Line3D(p1, p2, thickness=0.007, color=BLACK_INK))
        radius = self.dimension_line(center, center + RIGHT * 1.90, z_lift=0.13, tick=0.15)
        return VGroup(rug, edge, rings, spokes, radius)

    # ------------------------------------------------------------------
    # 2D analysis plans: the exact requested region is visibly hatched.
    # ------------------------------------------------------------------
    def radius_mark_2d(self, center: np.ndarray, radius: float, label: str,
                       color: str = BLACK_INK) -> VGroup:
        dot = Dot(center, radius=0.055, color=BLACK_INK)
        line = Line(center, center + RIGHT * radius, color=BLACK_INK, stroke_width=4)
        tick = Line(center + RIGHT * radius + DOWN * 0.13,
                    center + RIGHT * radius + UP * 0.13,
                    color=BLACK_INK, stroke_width=3)
        lab = self.mathtex(label, 31).next_to(line, UP, buff=0.15)
        return VGroup(dot, line, tick, lab)

    def diameter_mark_2d(self, center: np.ndarray, radius: float, label: str,
                         color: str = BLACK_INK) -> VGroup:
        line = Line(center + LEFT * radius, center + RIGHT * radius,
                    color=BLACK_INK, stroke_width=4)
        ticks = VGroup(
            Line(center + LEFT * radius + DOWN * 0.14,
                 center + LEFT * radius + UP * 0.14, color=BLACK_INK, stroke_width=3),
            Line(center + RIGHT * radius + DOWN * 0.14,
                 center + RIGHT * radius + UP * 0.14, color=BLACK_INK, stroke_width=3),
        )
        lab = self.mathtex(label, 31).next_to(line, UP, buff=0.15)
        return VGroup(line, ticks, lab)

    def garden_plan(self):
        c, r = LEFT * 3.45 + DOWN * 0.58, 1.78
        disk = Circle(radius=r, fill_color=PALE_GRAY, fill_opacity=0.86,
                      stroke_color=BLACK_INK, stroke_width=5.0).move_to(c)
        hatch = self.hatch_disk(c, r, spacing=0.25, opacity=0.34)
        radius = self.radius_mark_2d(c, r, r"r=4\,\mathrm{m}")
        area_tag = self.area_tag("SHADED REGION = GRASS AREA", c + UP * 2.05, width=3.55)
        edge_tag = self.area_tag("OUTER EDGE = FENCE LENGTH", c + DOWN * 2.05, width=3.45)
        edge_arc = Arc(radius=r, start_angle=15 * DEGREES, angle=150 * DEGREES,
                       color=BLACK_INK, stroke_width=8).move_arc_center_to(c)
        return VGroup(disk, hatch), VGroup(radius, area_tag, edge_tag, edge_arc)

    def pool_plan(self):
        c, r = LEFT * 3.45 + DOWN * 0.58, 1.78
        disk = Circle(radius=r, fill_color=PALE_GRAY, fill_opacity=0.86,
                      stroke_color=BLACK_INK, stroke_width=4.5).move_to(c)
        hatch = self.hatch_disk(c, r, spacing=0.24, opacity=0.34)
        diameter = self.diameter_mark_2d(c, r, r"d=10\,\mathrm{m}")
        target = self.area_tag("SHADED DISK = COVER AREA", c + DOWN * 2.05, width=3.15)
        radius_line = Line(c, c + RIGHT * r, color=BLACK_INK, stroke_width=4)
        radius_lab = self.mathtex(r"r=5\,\mathrm{m}", 31).next_to(radius_line, DOWN, buff=0.15)
        radius_group = VGroup(radius_line, radius_lab).set_opacity(0)
        return VGroup(disk, hatch), VGroup(diameter, target), radius_group

    def walkway_plan(self):
        c, inner, outer = LEFT * 3.45 + DOWN * 0.58, 1.05, 1.82
        ring = Annulus(inner_radius=inner, outer_radius=outer,
                       fill_color=PALE_GRAY, fill_opacity=0.88,
                       stroke_color=BLACK_INK, stroke_width=3.0).move_to(c)
        hatch = self.hatch_annulus(c, inner, outer, spacing=0.22, opacity=0.38)
        outer_circle = Circle(radius=outer, color=BLACK_INK, stroke_width=4.0).move_to(c)
        inner_circle = Circle(radius=inner, color=BLACK_INK, stroke_width=4.0).move_to(c)
        R = Line(c, c + UP * outer, color=BLACK_INK, stroke_width=4)
        Rlab = self.mathtex(r"R=5\,\mathrm{m}", 29).next_to(R, LEFT, buff=0.14)
        rr = Line(c, c + RIGHT * inner, color=BLACK_INK, stroke_width=4)
        rlab = self.mathtex(r"r=3\,\mathrm{m}", 29).next_to(rr, DOWN, buff=0.14)
        outer_tag = self.area_tag("A_outer = πR²", c + LEFT * 2.55 + UP * 1.25, width=2.25)
        hole_tag = self.area_tag("A_hole = πr²", c + LEFT * 2.45 + DOWN * 1.00, width=2.20)
        target_tag = self.area_tag("HATCHED RING = A_outer − A_hole",
                                   c + DOWN * 2.12, width=4.15)
        return VGroup(ring, hatch), VGroup(
            outer_circle, inner_circle, R, Rlab, rr, rlab, outer_tag, hole_tag, target_tag
        )

    def patio_plan(self):
        c, side, r = LEFT * 3.45 + DOWN * 0.58, 3.58, 1.18
        remaining = Difference(Square(side_length=side), Circle(radius=r))
        remaining.set_fill(PALE_GRAY, opacity=0.88).set_stroke(BLACK_INK, width=3.0)
        remaining.move_to(c)
        hatch = self.hatch_square_minus_circle(c, side, r, spacing=0.22, opacity=0.36)
        square = Square(side_length=side, color=BLACK_INK, stroke_width=4.0).move_to(c)
        circle = Circle(radius=r, color=BLACK_INK, stroke_width=4.0).move_to(c)
        side_line = Line(c + LEFT * side / 2 + DOWN * side / 2,
                         c + RIGHT * side / 2 + DOWN * side / 2,
                         color=BLACK_INK, stroke_width=4)
        side_lab = self.mathtex(r"12\,\mathrm{m}", 29).next_to(side_line, DOWN, buff=0.15)
        diam = Line(c + LEFT * r, c + RIGHT * r, color=BLACK_INK, stroke_width=4)
        diam_lab = self.mathtex(r"d=8\,\mathrm{m}", 29).next_to(diam, UP, buff=0.14)
        square_tag = self.area_tag("WHOLE = 12²", c + LEFT * 2.45 + UP * 1.35, width=2.05)
        hole_tag = self.area_tag("HOLE = π(4)²", c + RIGHT * 2.45 + UP * 1.35, width=2.30)
        target_tag = self.area_tag("HATCHED TILE = WHOLE − CIRCLE",
                                   c + DOWN * 2.18, width=3.80)
        return VGroup(remaining, hatch), VGroup(
            square, circle, side_line, side_lab, diam, diam_lab,
            square_tag, hole_tag, target_tag
        )

    def rug_plan(self):
        c, r = LEFT * 3.45 + DOWN * 0.58, 1.78
        disk = Circle(radius=r, fill_color=PALE_GRAY, fill_opacity=0.88,
                      stroke_color=BLACK_INK, stroke_width=4.5).move_to(c)
        hatch = self.hatch_disk(c, r, spacing=0.25, opacity=0.34)
        dot = Dot(c, radius=0.055, color=BLACK_INK)
        ray = Line(c, c + RIGHT * r, color=BLACK_INK, stroke_width=4)
        rlab = self.mathtex(r"r=?", 32).next_to(ray, UP, buff=0.15)
        alab = self.mathtex(r"A=78.54\,\mathrm{m}^2", 31).move_to(c + UP * 0.72)
        target = self.area_tag("GIVEN SHADED AREA → FIND r", c + DOWN * 2.05, width=3.25)
        return VGroup(disk, hatch), VGroup(dot, ray, rlab, alab, target)

    # ------------------------------------------------------------------
    # Override focus colors so the 3D face-isolation stage is also monochrome.
    # ------------------------------------------------------------------
    def problem_garden_projection(self) -> None:
        self.set_header(m.ProblemData(1, "BOUNDARY VS REGION", "Circular garden · fence versus grass",
                                    "Radius = 4 m. Find the fence length and the grass area.", BLACK_INK))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.garden_model(c))
        strip = self.data_strip([("GIVEN  r = 4 m", BLACK_INK, 3.55),
                                 ("FENCE  →  C", BLACK_INK, 3.55),
                                 ("GRASS  →  A", BLACK_INK, 3.55)])
        focus = Circle(radius=1.74, fill_color=PALE_GRAY, fill_opacity=0.30,
                       stroke_color=BLACK_INK, stroke_width=6).shift(c + OUT * 0.34)
        target, details = self.garden_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-58, phi=57)
        self.set_projection_step(5, "READ THE SHADED REGION AND THE OUTER EDGE",
                                 "Hatching marks the grass area; the bold outline is the fence length.",
                                 BLACK_INK)
        solution = self.reveal_solution("2D MODEL → SOLVE",
            [r"C=2\pi r=2\pi(4)=8\pi", r"C\approx25.13\,\mathrm{m}",
             r"A=\pi r^2=\pi(4)^2=16\pi", r"A\approx50.27\,\mathrm{m}^2"],
            r"\boxed{C\approx25.13\,\mathrm{m}\quad A\approx50.27\,\mathrm{m}^2}",
            BLACK_INK, "Boundary uses m; shaded region uses m².")
        self.finish_problem(diagram, solution)

    def problem_pool_projection(self) -> None:
        self.set_header(m.ProblemData(2, "DIAMETER → RADIUS", "Round pool cover · convert before area",
                                    "Diameter = 10 m. Find the material needed to cover the water surface.", BLACK_INK))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.pool_model(c))
        strip = self.data_strip([("GIVEN  d = 10 m", BLACK_INK, 3.55),
                                 ("AREA NEEDS r", BLACK_INK, 3.55),
                                 ("r = d / 2", BLACK_INK, 3.55)])
        focus = Circle(radius=1.70, fill_color=PALE_GRAY, fill_opacity=0.30,
                       stroke_color=BLACK_INK, stroke_width=6).shift(c + OUT * 0.40)
        target, details, radius_group = self.pool_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-56, phi=55)
        self.set_projection_step(5, "CONVERT DIAMETER TO RADIUS ON THE SHADED DISK",
                                 "The entire hatched circle is the cover area; radius is half the diameter.",
                                 BLACK_INK)
        self.play(Indicate(details[0], color=BLACK_INK, scale_factor=1.02), run_time=m.RUN_NORMAL)
        self.play(radius_group.animate.set_opacity(1), run_time=m.RUN_NORMAL)
        diagram.add(radius_group)
        self.wait(m.PAUSE_READ)
        solution = self.reveal_solution("CONVERT → AREA",
            [r"r=\frac{d}{2}=\frac{10}{2}=5\,\mathrm{m}", r"A=\pi r^2", r"A=\pi(5)^2=25\pi"],
            r"\boxed{A\approx78.54\,\mathrm{m}^2}", BLACK_INK,
            "The hatched top-view disk is exactly the material area.")
        self.finish_problem(diagram, solution)

    def problem_walkway_projection(self) -> None:
        self.set_header(m.ProblemData(3, "ANNULUS / RING", "Walkway around a fountain · subtract two circles",
                                    "Inner radius = 3 m; outer radius = 5 m. Find walkway area only.", BLACK_INK))
        c = DOWN * 0.32
        stage = VGroup(self.technical_floor(c), self.fountain_walkway_model(c))
        strip = self.data_strip([("OUTER  R = 5 m", BLACK_INK, 3.55),
                                 ("INNER  r = 3 m", BLACK_INK, 3.55),
                                 ("RING = BIG − SMALL", BLACK_INK, 4.10)])
        focus = Annulus(inner_radius=1.18, outer_radius=2.02,
                        fill_color=PALE_GRAY, fill_opacity=0.34,
                        stroke_color=BLACK_INK, stroke_width=5).shift(c + OUT * 0.50)
        target, details = self.walkway_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-50, phi=58)
        self.set_projection_step(5, "SEPARATE OUTER AREA, INNER HOLE, AND TARGET RING",
                                 "Only the hatched annulus counts: A_walkway = A_outer − A_hole.",
                                 BLACK_INK)
        solution = self.reveal_solution("BIG CIRCLE − SMALL CIRCLE",
            [r"A=\pi R^2-\pi r^2", r"A=\pi(5^2-3^2)", r"A=\pi(25-9)=16\pi"],
            r"\boxed{A\approx50.27\,\mathrm{m}^2}", BLACK_INK,
            "The unhatched inner disk is excluded from the answer.")
        self.finish_problem(diagram, solution)

    def problem_patio_projection(self) -> None:
        self.set_header(m.ProblemData(4, "COMPOSITE AREA", "Square patio with a circular fountain",
                                    "Patio = 12 m × 12 m; fountain diameter = 8 m. Find remaining tile area.", BLACK_INK))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.patio_model(c))
        strip = self.data_strip([("SQUARE  12 × 12", BLACK_INK, 3.75),
                                 ("FOUNTAIN  d = 8 m", BLACK_INK, 3.75),
                                 ("TILE = WHOLE − HOLE", BLACK_INK, 4.25)])
        focus = Difference(Square(side_length=4.60), Circle(radius=1.53))
        focus.set_fill(PALE_GRAY, opacity=0.30).set_stroke(BLACK_INK, width=5)
        focus.shift(c + OUT * 0.48)
        target, details = self.patio_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-48, phi=59)
        self.set_projection_step(5, "IDENTIFY THE HATCHED TILE REGION",
                                 "The square is the whole; the unhatched circle is the removed fountain.",
                                 BLACK_INK)
        solution = self.reveal_solution("COMPOSITE 2D REGION",
            [r"A_{\rm square}=12^2=144", r"r=\frac{8}{2}=4\,\mathrm{m}",
             r"A_{\rm circle}=\pi(4)^2=16\pi", r"A_{\rm tile}=144-16\pi"],
            r"\boxed{A_{\rm tile}\approx93.73\,\mathrm{m}^2}", BLACK_INK,
            "Hatched tile area = whole square − circular hole.")
        self.finish_problem(diagram, solution)

    def problem_inverse_projection(self) -> None:
        self.set_header(m.ProblemData(5, "INVERSE AREA", "Round rug · work backward from area",
                                    "Area = 78.54 m². Estimate the rug radius and diameter.", BLACK_INK))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.rug_model(c))
        strip = self.data_strip([("GIVEN  A = 78.54 m²", BLACK_INK, 4.15),
                                 ("UNKNOWN  r", BLACK_INK, 3.25),
                                 ("THEN  d = 2r", BLACK_INK, 4.15)])
        focus = Circle(radius=1.90, fill_color=PALE_GRAY, fill_opacity=0.30,
                       stroke_color=BLACK_INK, stroke_width=6).shift(c + OUT * 0.18)
        target, details = self.rug_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-55, phi=53)
        self.set_projection_step(5, "USE THE GIVEN HATCHED AREA TO WORK BACKWARD",
                                 "The full disk area is known; reverse A = πr² to recover r and then d.",
                                 BLACK_INK)
        solution = self.reveal_solution("REVERSE A = πr²",
            [r"78.54=\pi r^2", r"r^2=\frac{78.54}{\pi}\approx25",
             r"r\approx\sqrt{25}=5\,\mathrm{m}", r"d=2r\approx10\,\mathrm{m}"],
            r"\boxed{r\approx5\,\mathrm{m}\quad d\approx10\,\mathrm{m}}", BLACK_INK,
            "The complete hatched disk corresponds to the given area.")
        self.finish_problem(diagram, solution)
