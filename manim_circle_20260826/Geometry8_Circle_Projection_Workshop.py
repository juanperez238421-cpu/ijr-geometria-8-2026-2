#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry 8 — Circle workshop: physical 3D object → orthographic 2D analysis.

This scene deliberately reuses the senior-QA CAD models and classroom helpers
from Geometry8_Circle_Pi_Mixed_Workshop, but changes the pedagogy completely:
OBSERVE 3D → ISOLATE FACE → TOP VIEW → CLEAN 2D MODEL → SOLVE.

ManimCE 0.20.x final protocol target: 1920×1080, 30 fps, -pqh.
"""
from __future__ import annotations

from manim import *
from Geometry8_Circle_Pi_Mixed_Workshop import *


class Geometry8CircleProjectionWorkshop(Geometry8CirclePiMixedWorkshop):
    """Dedicated step-by-step projection workshop."""

    def setup(self) -> None:
        super().setup()
        self.projection_banner: VGroup | None = None

    # ------------------------------------------------------------------
    # Projection UI
    # ------------------------------------------------------------------
    def projection_step(self, number: int, title: str, detail: str,
                        accent: str = ACCENT_ORANGE) -> VGroup:
        box = RoundedRectangle(
            width=9.3, height=0.86, corner_radius=0.15,
            stroke_color=LIGHT_GRAY, stroke_width=1.6,
            fill_color=WHITE_FILL, fill_opacity=0.99,
        )
        tab = RoundedRectangle(
            width=1.25, height=0.66, corner_radius=0.12,
            stroke_color=accent, stroke_width=2.0,
            fill_color=WHITE_FILL, fill_opacity=1,
        )
        tab_text = self.text(f"STEP {number}", 18, BOLD).set_color(accent).move_to(tab)
        title_mob = self.text(title, 23, BOLD)
        detail_mob = self.text(detail, 16).set_color(INK_SOFT)
        copy = VGroup(title_mob, detail_mob).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        self.fit(copy, 7.25, 0.60)
        content = VGroup(VGroup(tab, tab_text), copy).arrange(RIGHT, buff=0.26)
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.20)
        return VGroup(box, content).move_to(UP * 2.16)

    def set_projection_step(self, number: int, title: str, detail: str,
                            accent: str = ACCENT_ORANGE) -> None:
        new = self.projection_step(number, title, detail, accent)
        self.fixed(new)
        if self.projection_banner is None:
            self.projection_banner = new
            self.play(FadeIn(new, shift=DOWN * 0.04), run_time=RUN_QUICK)
        else:
            old = self.projection_banner
            self.projection_banner = new
            self.play(FadeOut(old), FadeIn(new), run_time=RUN_QUICK)
            self.remove(old)

    def reset_projection_banner(self) -> None:
        if self.projection_banner is not None:
            old = self.projection_banner
            self.play(FadeOut(old), run_time=RUN_QUICK)
            self.remove(old)
            self.projection_banner = None

    # ------------------------------------------------------------------
    # Clean 2D diagrams used after the camera reaches top view
    # ------------------------------------------------------------------
    def radius_mark_2d(self, center: np.ndarray, radius: float, label: str,
                       color: str = ACCENT_ORANGE) -> VGroup:
        dot = Dot(center, radius=0.055, color=BLACK_TEXT)
        line = Line(center, center + RIGHT * radius, color=color, stroke_width=4)
        tick = Line(center + RIGHT * radius + DOWN * 0.13,
                    center + RIGHT * radius + UP * 0.13,
                    color=color, stroke_width=3)
        lab = self.mathtex(label, 31).next_to(line, UP, buff=0.15)
        return VGroup(dot, line, tick, lab)

    def diameter_mark_2d(self, center: np.ndarray, radius: float, label: str,
                         color: str = ACCENT_ORANGE) -> VGroup:
        line = Line(center + LEFT * radius, center + RIGHT * radius,
                    color=color, stroke_width=4)
        ticks = VGroup(
            Line(center + LEFT * radius + DOWN * 0.14,
                 center + LEFT * radius + UP * 0.14, color=color, stroke_width=3),
            Line(center + RIGHT * radius + DOWN * 0.14,
                 center + RIGHT * radius + UP * 0.14, color=color, stroke_width=3),
        )
        lab = self.mathtex(label, 31).next_to(line, UP, buff=0.15)
        return VGroup(line, ticks, lab)

    def garden_plan(self) -> tuple[Mobject, VGroup]:
        c = LEFT * 3.45 + DOWN * 0.58
        r = 1.78
        shape = Circle(radius=r, fill_color=MINT, fill_opacity=0.68,
                       stroke_color=ACCENT_RED, stroke_width=4.2).move_to(c)
        radius = self.radius_mark_2d(c, r, r"r=4\,\mathrm{m}")
        area = self.text("grass = area", 18, BOLD).set_color(ACCENT_GREEN).next_to(shape, UP, buff=0.18)
        edge = self.text("fence = circumference", 18, BOLD).set_color(ACCENT_RED).next_to(shape, DOWN, buff=0.20)
        return shape, VGroup(radius, area, edge)

    def pool_plan(self) -> tuple[Mobject, VGroup, VGroup]:
        c = LEFT * 3.45 + DOWN * 0.58
        r = 1.78
        shape = Circle(radius=r, fill_color=ACCENT_BLUE, fill_opacity=0.25,
                       stroke_color=ACCENT_BLUE, stroke_width=3.4).move_to(c)
        diameter = self.diameter_mark_2d(c, r, r"d=10\,\mathrm{m}")
        radius_line = Line(c, c + RIGHT * r, color=ACCENT_GREEN, stroke_width=4)
        radius_lab = self.mathtex(r"r=5\,\mathrm{m}", 31).next_to(radius_line, DOWN, buff=0.15)
        radius_group = VGroup(radius_line, radius_lab).set_opacity(0)
        return shape, VGroup(diameter), radius_group

    def walkway_plan(self) -> tuple[Mobject, VGroup]:
        c = LEFT * 3.45 + DOWN * 0.58
        inner, outer = 1.05, 1.82
        shape = Annulus(inner_radius=inner, outer_radius=outer,
                        fill_color=CYAN, fill_opacity=0.34,
                        stroke_color=STONE_DARK, stroke_width=2.0).move_to(c)
        outer_circle = Circle(radius=outer, color=ACCENT_ORANGE, stroke_width=3.0).move_to(c)
        inner_circle = Circle(radius=inner, color=ACCENT_BLUE, stroke_width=3.0).move_to(c)
        R = Line(c, c + UP * outer, color=ACCENT_ORANGE, stroke_width=4)
        Rlab = self.mathtex(r"R=5\,\mathrm{m}", 29).next_to(R, LEFT, buff=0.14)
        rr = Line(c, c + RIGHT * inner, color=ACCENT_BLUE, stroke_width=4)
        rlab = self.mathtex(r"r=3\,\mathrm{m}", 29).next_to(rr, DOWN, buff=0.14)
        tag = self.text("walkway = outer circle − fountain", 17, BOLD).set_color(ACCENT_TEAL)
        tag.next_to(shape, DOWN, buff=0.20)
        return shape, VGroup(outer_circle, inner_circle, R, Rlab, rr, rlab, tag)

    def patio_plan(self) -> tuple[Mobject, VGroup]:
        c = LEFT * 3.45 + DOWN * 0.58
        side, r = 3.58, 1.18
        shape = Difference(Square(side_length=side), Circle(radius=r))
        shape.set_fill(PAPER_GRAY, opacity=0.92).set_stroke(STONE_DARK, width=2.0)
        shape.move_to(c)
        square = Square(side_length=side, color=ACCENT_ORANGE, stroke_width=3.0).move_to(c)
        circle = Circle(radius=r, color=ACCENT_BLUE, stroke_width=3.0).move_to(c)
        side_line = Line(c + LEFT * side / 2 + DOWN * side / 2,
                         c + RIGHT * side / 2 + DOWN * side / 2,
                         color=ACCENT_ORANGE, stroke_width=4)
        side_lab = self.mathtex(r"12\,\mathrm{m}", 29).next_to(side_line, DOWN, buff=0.15)
        diam = Line(c + LEFT * r, c + RIGHT * r, color=ACCENT_BLUE, stroke_width=4)
        diam_lab = self.mathtex(r"d=8\,\mathrm{m}", 29).next_to(diam, UP, buff=0.14)
        tag = self.text("tile = square − circular hole", 17, BOLD).set_color(ACCENT_TEAL)
        tag.next_to(shape, DOWN, buff=0.42)
        return shape, VGroup(square, circle, side_line, side_lab, diam, diam_lab, tag)

    def rug_plan(self) -> tuple[Mobject, VGroup]:
        c = LEFT * 3.45 + DOWN * 0.58
        r = 1.78
        shape = Circle(radius=r, fill_color=PAPER_GRAY, fill_opacity=0.92,
                       stroke_color=BLACK_LINE, stroke_width=3.0).move_to(c)
        dot = Dot(c, radius=0.055, color=BLACK_TEXT)
        ray = Line(c, c + RIGHT * r, color=ACCENT_ORANGE, stroke_width=4)
        rlab = self.mathtex(r"r=?", 32).next_to(ray, UP, buff=0.15)
        alab = self.mathtex(r"A=78.54\,\mathrm{m}^2", 31).move_to(c + UP * 0.75)
        return shape, VGroup(dot, ray, rlab, alab)

    # ------------------------------------------------------------------
    # Generic 3D -> 2D choreography
    # ------------------------------------------------------------------
    def project_problem(self, stage: VGroup, strip: VGroup, focus: Mobject,
                        target: Mobject, details: VGroup, *, theta: float, phi: float) -> VGroup:
        self.set_projection_step(1, "OBSERVE THE 3D OBJECT",
                                 "Read the physical situation before choosing any formula.")
        self.play(FadeIn(stage[0]), run_time=RUN_QUICK)
        self.play(FadeIn(stage[1]), FadeIn(strip, shift=UP * 0.05), run_time=RUN_SLOW)
        self.move_camera(phi=phi * DEGREES, theta=theta * DEGREES, zoom=1.02, run_time=RUN_SLOW)
        self.wait(PAUSE_WORK)

        self.set_projection_step(2, "ISOLATE THE FACE THAT CONTAINS THE CIRCLE",
                                 "Height and side walls belong to the object, but not to the 2D circle calculation.",
                                 ACCENT_GREEN)
        self.play(FadeIn(focus), run_time=RUN_QUICK)
        self.play(Indicate(focus, color=ACCENT_GREEN, scale_factor=1.05), run_time=RUN_SLOW)
        self.wait(PAUSE_READ)

        self.set_projection_step(3, "ROTATE TO AN ORTHOGRAPHIC TOP VIEW",
                                 "Looking straight down removes perspective distortion and reveals the true geometry.")
        self.play(FadeOut(strip), run_time=RUN_QUICK)
        self.move_camera(phi=2 * DEGREES, theta=-90 * DEGREES, zoom=1.04, run_time=RUN_SLOW)
        self.wait(PAUSE_READ)

        self.set_projection_step(4, "REPLACE THE 3D OBJECT WITH A CLEAN 2D PLAN",
                                 "Keep only the region, boundary and measurements needed for the mathematical model.",
                                 ACCENT_TEAL)
        self.play(FadeOut(stage), ReplacementTransform(focus, target), run_time=RUN_SLOW)
        self.play(LaggedStart(*[FadeIn(m) for m in details], lag_ratio=0.10), run_time=RUN_SLOW)
        self.wait(PAUSE_READ)
        return VGroup(target, details)

    def finish_problem(self, diagram: VGroup, solution: VGroup) -> None:
        self.play(FadeOut(diagram), FadeOut(solution), run_time=RUN_NORMAL)
        self.remove(diagram, solution)
        self.camera_isometric()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera_isometric()
        self.opening_projection_lesson()
        self.problem_garden_projection()
        self.problem_pool_projection()
        self.problem_walkway_projection()
        self.problem_patio_projection()
        self.problem_inverse_projection()
        self.closing_projection_method()

    def opening_projection_lesson(self) -> None:
        kicker = self.text("GEOMETRY 8 · CIRCLE WORKSHOP", 21, BOLD).set_color(ACCENT_ORANGE)
        title1 = self.text("FROM A REAL 3D OBJECT", 44, BOLD)
        title2 = self.text("TO A CLEAN 2D CIRCLE ANALYSIS", 44, BOLD)
        subtitle = self.text("First project the object. Only then choose the circle formula.", 24).set_color(INK_SOFT)
        titles = VGroup(kicker, title1, title2, subtitle).arrange(DOWN, buff=0.15)
        self.fit(titles, 14.0, 2.10)
        titles.move_to(UP * 3.08)
        self.fixed(titles)

        c = DOWN * 0.58
        stage = VGroup(self.technical_floor(c), self.pool_model(c))
        face = Circle(radius=1.70, fill_color=ACCENT_BLUE, fill_opacity=0.18,
                      stroke_color=ACCENT_GREEN, stroke_width=5).shift(c + OUT * 0.39)

        labels = ["1 · OBSERVE 3D", "2 · ISOLATE FACE", "3 · TOP VIEW", "4 · DRAW 2D", "5 · SOLVE"]
        timeline = VGroup()
        for label in labels:
            box = RoundedRectangle(width=2.45, height=0.62, corner_radius=0.13,
                                   stroke_color=LIGHT_GRAY, stroke_width=1.3,
                                   fill_color=WHITE_FILL, fill_opacity=1)
            txt = self.text(label, 16, BOLD).move_to(box)
            timeline.add(VGroup(box, txt))
        timeline.arrange(RIGHT, buff=0.12)
        self.fit(timeline, 13.7, 0.64)
        timeline.move_to(DOWN * 3.90)
        self.fixed(timeline)

        self.play(Write(kicker), run_time=RUN_NORMAL)
        self.play(FadeIn(title1, shift=UP * 0.06), run_time=RUN_NORMAL)
        self.play(FadeIn(title2, shift=UP * 0.06), run_time=RUN_NORMAL)
        self.play(FadeIn(subtitle), run_time=RUN_QUICK)
        self.play(FadeIn(stage), FadeIn(timeline), run_time=RUN_SLOW)

        self.play(timeline[0][0].animate.set_stroke(ACCENT_ORANGE, width=2.2), run_time=RUN_QUICK)
        self.move_camera(phi=55 * DEGREES, theta=-63 * DEGREES, zoom=1.05, run_time=RUN_SLOW)
        self.wait(1.2)
        self.play(timeline[1][0].animate.set_stroke(ACCENT_GREEN, width=2.2), FadeIn(face), run_time=RUN_QUICK)
        self.play(Indicate(face, color=ACCENT_GREEN, scale_factor=1.05), run_time=RUN_SLOW)
        self.wait(1.0)
        self.play(timeline[2][0].animate.set_stroke(ACCENT_ORANGE, width=2.2), run_time=RUN_QUICK)
        self.move_camera(phi=2 * DEGREES, theta=-90 * DEGREES, zoom=1.05, run_time=RUN_SLOW)
        self.wait(0.8)

        self.play(timeline[3][0].animate.set_stroke(ACCENT_TEAL, width=2.2), run_time=RUN_QUICK)
        target_c = DOWN * 0.58
        target = Circle(radius=1.85, fill_color=ACCENT_BLUE, fill_opacity=0.18,
                        stroke_color=BLACK_LINE, stroke_width=3.2).move_to(target_c)
        self.play(FadeOut(stage), ReplacementTransform(face, target), run_time=RUN_SLOW)
        center = Dot(target_c, radius=0.055, color=BLACK_TEXT)
        radius = Line(target_c, target_c + RIGHT * 1.85, color=ACCENT_ORANGE, stroke_width=4)
        diameter = Line(target_c + LEFT * 1.85, target_c + RIGHT * 1.85,
                        color=ACCENT_GREEN, stroke_width=3.4)
        rlab = self.mathtex(r"r", 36).next_to(radius, UP, buff=0.14)
        dlab = self.mathtex(r"d=2r", 34).next_to(diameter, DOWN, buff=0.16)
        arc = Arc(radius=1.85, start_angle=35 * DEGREES, angle=145 * DEGREES,
                  color=ACCENT_RED, stroke_width=7).move_arc_center_to(target_c)
        blab = self.text("circumference C", 19, BOLD).set_color(ACCENT_RED).next_to(target, LEFT, buff=0.30)
        alab = self.text("area A", 21, BOLD).set_color(ACCENT_GREEN).move_to(target_c + UP * 0.72)
        geometry = VGroup(center, radius, diameter, rlab, dlab, arc, blab, alab)
        self.play(FadeIn(center), Create(radius), FadeIn(rlab), run_time=RUN_NORMAL)
        self.play(Create(diameter), FadeIn(dlab), run_time=RUN_NORMAL)
        self.play(Create(arc), FadeIn(blab), FadeIn(alab), run_time=RUN_SLOW)

        self.play(timeline[4][0].animate.set_stroke(ACCENT_ORANGE, width=2.2), run_time=RUN_QUICK)
        formulas = VGroup(self.mathtex(r"C=2\pi r=\pi d", 39), self.mathtex(r"A=\pi r^2", 41)).arrange(RIGHT, buff=0.80)
        box = RoundedRectangle(width=7.2, height=0.92, corner_radius=0.16,
                               stroke_color=LIGHT_GRAY, stroke_width=1.4,
                               fill_color=WHITE_FILL, fill_opacity=1)
        formulas.move_to(box)
        formula_group = VGroup(box, formulas).move_to(DOWN * 2.65)
        self.fixed(formula_group)
        self.play(FadeIn(box), Write(formulas), run_time=RUN_SLOW)
        self.wait(2.0)
        self.play(FadeOut(VGroup(target, geometry)), FadeOut(titles), FadeOut(timeline), FadeOut(formula_group), run_time=RUN_NORMAL)
        self.camera_isometric()

    def problem_garden_projection(self) -> None:
        self.set_header(ProblemData(1, "BOUNDARY VS REGION", "Circular garden · fence versus grass",
                                    "Radius = 4 m. Find the fence length and the grass area.", ACCENT_GREEN))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.garden_model(c))
        strip = self.data_strip([("GIVEN  r = 4 m", ACCENT_GREEN, 3.55),
                                 ("FENCE  →  C", ACCENT_RED, 3.55),
                                 ("GRASS  →  A", ACCENT_TEAL, 3.55)])
        focus = Circle(radius=1.74, fill_color=ACCENT_GREEN, fill_opacity=0.12,
                       stroke_color=ACCENT_GREEN, stroke_width=5).shift(c + OUT * 0.34)
        target, details = self.garden_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-58, phi=57)
        self.set_projection_step(5, "TRANSLATE THE 2D PLAN INTO MATHEMATICS",
                                 "The red boundary gives C; the filled region gives A.", ACCENT_GREEN)
        solution = self.reveal_solution("2D MODEL → SOLVE",
            [r"C=2\pi r=2\pi(4)=8\pi", r"C\approx25.13\,\mathrm{m}",
             r"A=\pi r^2=\pi(4)^2=16\pi", r"A\approx50.27\,\mathrm{m}^2"],
            r"\boxed{C\approx25.13\,\mathrm{m}\quad A\approx50.27\,\mathrm{m}^2}",
            ACCENT_GREEN, "Boundary uses m; region uses m².")
        self.finish_problem(diagram, solution)

    def problem_pool_projection(self) -> None:
        self.set_header(ProblemData(2, "DIAMETER → RADIUS", "Round pool cover · convert before area",
                                    "Diameter = 10 m. Find the material needed to cover the water surface.", ACCENT_BLUE))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.pool_model(c))
        strip = self.data_strip([("GIVEN  d = 10 m", ACCENT_BLUE, 3.55),
                                 ("AREA NEEDS r", ACCENT_ORANGE, 3.55),
                                 ("r = d / 2", ACCENT_GREEN, 3.55)])
        focus = Circle(radius=1.70, fill_color=ACCENT_BLUE, fill_opacity=0.14,
                       stroke_color=ACCENT_GREEN, stroke_width=5).shift(c + OUT * 0.40)
        target, details, radius_group = self.pool_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-56, phi=55)
        self.set_projection_step(5, "CONVERT DIAMETER TO RADIUS ON THE 2D PLAN",
                                 "The diameter crosses the whole circle; the radius is exactly half.", ACCENT_ORANGE)
        self.play(Indicate(details[0], color=ACCENT_ORANGE, scale_factor=1.02), run_time=RUN_NORMAL)
        self.play(radius_group.animate.set_opacity(1), run_time=RUN_NORMAL)
        diagram.add(radius_group)
        self.wait(PAUSE_READ)
        solution = self.reveal_solution("CONVERT → AREA",
            [r"r=\frac{d}{2}=\frac{10}{2}=5\,\mathrm{m}", r"A=\pi r^2", r"A=\pi(5)^2=25\pi"],
            r"\boxed{A\approx78.54\,\mathrm{m}^2}", ACCENT_BLUE,
            "The top view makes the diameter/radius relationship visually explicit.")
        self.finish_problem(diagram, solution)

    def problem_walkway_projection(self) -> None:
        self.set_header(ProblemData(3, "ANNULUS / RING", "Walkway around a fountain · subtract two circles",
                                    "Inner radius = 3 m; outer radius = 5 m. Find walkway area only.", ACCENT_ORANGE))
        c = DOWN * 0.32
        stage = VGroup(self.technical_floor(c), self.fountain_walkway_model(c))
        strip = self.data_strip([("OUTER  R = 5 m", ACCENT_ORANGE, 3.55),
                                 ("INNER  r = 3 m", ACCENT_BLUE, 3.55),
                                 ("RING = BIG − SMALL", ACCENT_TEAL, 4.10)])
        focus = Annulus(inner_radius=1.18, outer_radius=2.02,
                        fill_color=ACCENT_TEAL, fill_opacity=0.16,
                        stroke_color=ACCENT_GREEN, stroke_width=4).shift(c + OUT * 0.50)
        target, details = self.walkway_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-50, phi=58)
        self.set_projection_step(5, "SUBTRACT THE TWO 2D CIRCULAR REGIONS",
                                 "The fountain is a hole, so its circle must be removed from the outer circle.", ACCENT_ORANGE)
        solution = self.reveal_solution("BIG CIRCLE − SMALL CIRCLE",
            [r"A=\pi R^2-\pi r^2", r"A=\pi(5^2-3^2)", r"A=\pi(25-9)=16\pi"],
            r"\boxed{A\approx50.27\,\mathrm{m}^2}", ACCENT_ORANGE,
            "Only the annular walkway is counted.")
        self.finish_problem(diagram, solution)

    def problem_patio_projection(self) -> None:
        self.set_header(ProblemData(4, "COMPOSITE AREA", "Square patio with a circular fountain",
                                    "Patio = 12 m × 12 m; fountain diameter = 8 m. Find remaining tile area.", ACCENT_TEAL))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.patio_model(c))
        strip = self.data_strip([("SQUARE  12 × 12", ACCENT_ORANGE, 3.75),
                                 ("FOUNTAIN  d = 8 m", ACCENT_BLUE, 3.75),
                                 ("TILE = WHOLE − HOLE", ACCENT_TEAL, 4.25)])
        focus = Difference(Square(side_length=4.60), Circle(radius=1.53))
        focus.set_fill(ACCENT_TEAL, opacity=0.12).set_stroke(ACCENT_GREEN, width=4)
        focus.shift(c + OUT * 0.48)
        target, details = self.patio_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-48, phi=59)
        self.set_projection_step(5, "READ THE COMPOSITE 2D REGION AS WHOLE − HOLE",
                                 "The 3D fountain becomes a circular hole inside the square patio plan.", ACCENT_TEAL)
        solution = self.reveal_solution("COMPOSITE 2D REGION",
            [r"A_{\rm square}=12^2=144", r"r=\frac{8}{2}=4\,\mathrm{m}",
             r"A_{\rm circle}=\pi(4)^2=16\pi", r"A_{\rm tile}=144-16\pi"],
            r"\boxed{A_{\rm tile}\approx93.73\,\mathrm{m}^2}", ACCENT_TEAL,
            "Composite area = total square region − circular hole.")
        self.finish_problem(diagram, solution)

    def problem_inverse_projection(self) -> None:
        self.set_header(ProblemData(5, "INVERSE AREA", "Round rug · work backward from area",
                                    "Area = 78.54 m². Estimate the rug radius and diameter.", ACCENT_ORANGE))
        c = DOWN * 0.34
        stage = VGroup(self.technical_floor(c), self.rug_model(c))
        strip = self.data_strip([("GIVEN  A = 78.54 m²", ACCENT_BLUE, 4.15),
                                 ("UNKNOWN  r", ACCENT_ORANGE, 3.25),
                                 ("THEN  d = 2r", ACCENT_GREEN, 4.15)])
        focus = Circle(radius=1.90, fill_color=ACCENT_BLUE, fill_opacity=0.10,
                       stroke_color=ACCENT_GREEN, stroke_width=5).shift(c + OUT * 0.18)
        target, details = self.rug_plan()
        diagram = self.project_problem(stage, strip, focus, target, details, theta=-55, phi=53)
        self.set_projection_step(5, "REVERSE THE 2D AREA FORMULA",
                                 "Start from A = πr², undo multiplication by π, then undo the square.", ACCENT_ORANGE)
        solution = self.reveal_solution("REVERSE A = πr²",
            [r"78.54=\pi r^2", r"r^2=\frac{78.54}{\pi}\approx25",
             r"r\approx\sqrt{25}=5\,\mathrm{m}", r"d=2r\approx10\,\mathrm{m}"],
            r"\boxed{r\approx5\,\mathrm{m}\quad d\approx10\,\mathrm{m}}", ACCENT_ORANGE,
            "Inverse problems undo the operations in A = πr².")
        self.finish_problem(diagram, solution)

    def closing_projection_method(self) -> None:
        self.set_header(ProblemData(6, "METHOD", "The camera move is part of the mathematics",
                                    "Convert the physical object into a 2D region before choosing the formula.", ACCENT_GREEN))
        self.set_projection_step(1, "3D OBJECT → 2D PLAN → FORMULA",
                                 "The top view is not decoration: it reveals the exact geometry used in the calculation.",
                                 ACCENT_GREEN)
        specs = [
            ("1", "OBSERVE 3D", "What physical surface matters?", ACCENT_ORANGE),
            ("2", "ISOLATE FACE", "Ignore height and side walls.", ACCENT_GREEN),
            ("3", "TOP VIEW", "Remove perspective distortion.", ACCENT_BLUE),
            ("4", "DRAW 2D", "Mark r, d, R and holes.", ACCENT_TEAL),
            ("5", "SOLVE + CHECK", "Formula, substitution, units.", ACCENT_RED),
        ]
        cards = VGroup()
        for num, title, body, accent in specs:
            box = RoundedRectangle(width=2.55, height=1.48, corner_radius=0.16,
                                   stroke_color=LIGHT_GRAY, stroke_width=1.3,
                                   fill_color=WHITE_FILL, fill_opacity=1)
            n = self.text(num, 22, BOLD).set_color(accent)
            t = self.text(title, 18, BOLD)
            b = self.text(body, 14).set_color(INK_SOFT)
            self.fit(b, 2.10, 0.40)
            cards.add(VGroup(box, VGroup(n, t, b).arrange(DOWN, buff=0.10).move_to(box)))
        cards.arrange(RIGHT, buff=0.18)
        self.fit(cards, 13.6, 1.55)
        cards.move_to(DOWN * 0.15)
        self.fixed(cards)
        formulas = VGroup(self.mathtex(r"C=2\pi r=\pi d", 37),
                          self.mathtex(r"A=\pi r^2", 39),
                          self.mathtex(r"A_{\rm ring}=\pi(R^2-r^2)", 34)).arrange(RIGHT, buff=0.72)
        box = RoundedRectangle(width=11.2, height=1.10, corner_radius=0.16,
                               stroke_color=LIGHT_GRAY, stroke_width=1.4,
                               fill_color=VERY_LIGHT_GRAY, fill_opacity=1)
        self.fit(formulas, 10.6, 0.64)
        formulas.move_to(box)
        summary = VGroup(box, formulas).move_to(DOWN * 2.25)
        self.fixed(summary)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.05) for card in cards], lag_ratio=0.11), run_time=RUN_SLOW)
        self.wait(1.1)
        self.play(FadeIn(box), Write(formulas), run_time=RUN_SLOW)
        self.wait(PAUSE_FINAL)
