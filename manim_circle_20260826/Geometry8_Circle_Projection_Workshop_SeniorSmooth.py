#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Senior QA edition: smoother physical 3D object -> mathematical 2D plan transition.

The geometry, monochrome typography, grayscale shading and analytical hatching
come from Geometry8_Circle_Projection_Workshop_Final.  This scene concentrates
on the pedagogical bridge between the physical object and the 2D region:

OBSERVE 3D -> ISOLATE SURFACE -> ROTATE TO TOP VIEW -> EXTRACT SURFACE ->
MORPH TO CLEAN PLAN -> HATCH TARGET REGION -> READ DIMENSIONS -> SOLVE.

ManimCE 0.20.x. Final target: literal -pqh, 1920x1080, 30 fps.
"""
from __future__ import annotations

from manim import *
from Geometry8_Circle_Projection_Workshop_Final import (
    Geometry8CircleProjectionWorkshopFinal,
    BLACK_INK,
    PALE_GRAY,
    PAPER,
)
import Geometry8_Circle_Projection_Workshop as m


class Geometry8CircleProjectionWorkshopSeniorSmooth(Geometry8CircleProjectionWorkshopFinal):
    """Full workshop with a deliberate, continuous 3D->2D explanatory morph."""

    def transition_chip(self, text: str, y: float = -2.75) -> VGroup:
        box = RoundedRectangle(
            width=6.8, height=0.62, corner_radius=0.13,
            stroke_color=BLACK_INK, stroke_width=1.4,
            fill_color=PAPER, fill_opacity=0.97,
        )
        label = self.text(text, 17, BOLD).move_to(box)
        self.fit(label, 6.35, 0.34)
        group = VGroup(box, label).move_to(UP * y)
        self.fixed(group)
        return group

    def _reveal_hatching(self, hatch: Mobject) -> None:
        """Draw hatching progressively so the target area becomes explicit."""
        if isinstance(hatch, VGroup) and len(hatch) > 0:
            self.play(
                LaggedStart(*[Create(line) for line in hatch], lag_ratio=0.035),
                run_time=1.35,
            )
        else:
            self.play(FadeIn(hatch), run_time=m.RUN_NORMAL)

    def project_problem(self, stage: VGroup, strip: VGroup, focus: Mobject,
                        target: Mobject, details: VGroup, *, theta: float, phi: float) -> VGroup:
        """Senior projection choreography with explicit visual continuity.

        The old version cut from the top face to the 2D diagram too abruptly.
        Here the same visible surface remains on screen through the camera move,
        is lifted from the physical object, then continuously morphed into the
        mathematical region before hatching and dimensions are revealed.
        """
        # 1) Build the physical object in layers, rather than popping it on screen.
        self.set_projection_step(
            1, "OBSERVE THE PHYSICAL 3D OBJECT",
            "Read the object first. Identify which surface the question is actually asking about.",
            BLACK_INK,
        )
        floor, model = stage[0], stage[1]
        self.play(FadeIn(floor), run_time=0.65)
        if isinstance(model, VGroup) and len(model) > 1:
            self.play(
                LaggedStart(*[FadeIn(part, shift=OUT * 0.025) for part in model], lag_ratio=0.055),
                FadeIn(strip, shift=UP * 0.05),
                run_time=1.55,
            )
        else:
            self.play(FadeIn(model), FadeIn(strip, shift=UP * 0.05), run_time=1.35)
        self.move_camera(
            phi=phi * DEGREES, theta=theta * DEGREES, zoom=1.02,
            run_time=2.0, rate_func=smooth,
        )
        self.wait(0.55)

        # 2) Isolate exactly the surface that survives into the mathematical plan.
        self.set_projection_step(
            2, "ISOLATE THE SURFACE USED BY THE QUESTION",
            "Side walls and height describe the object; the highlighted top region becomes the 2D geometry.",
            BLACK_INK,
        )
        self.play(FadeIn(focus), run_time=0.55)
        self.play(
            model.animate.set_opacity(0.62),
            focus.animate.set_fill(PALE_GRAY, opacity=0.46).set_stroke(BLACK_INK, width=7),
            run_time=0.85,
        )
        self.play(Indicate(focus, color=BLACK_INK, scale_factor=1.045), run_time=1.05)
        self.wait(0.45)

        # 3) Keep the SAME surface visible while the camera reaches an orthographic top view.
        self.set_projection_step(
            3, "ROTATE THE CAMERA — KEEP YOUR EYES ON THAT SAME SURFACE",
            "Perspective disappears gradually. In top view the selected face shows its true 2D shape.",
            BLACK_INK,
        )
        self.play(FadeOut(strip), run_time=0.45)
        top_chip = self.transition_chip("3D SURFACE  →  ORTHOGRAPHIC TOP VIEW  →  TRUE SHAPE")
        self.play(FadeIn(top_chip, shift=UP * 0.05), run_time=0.45)
        self.move_camera(
            phi=2 * DEGREES, theta=-90 * DEGREES, zoom=1.055,
            run_time=2.65, rate_func=smooth,
        )
        self.play(
            focus.animate.scale(1.045).set_fill(PALE_GRAY, opacity=0.60),
            stage.animate.set_opacity(0.28),
            run_time=0.75,
        )
        self.wait(0.55)

        # 4) Extract that physical surface and morph it directly into the clean plan.
        self.set_projection_step(
            4, "EXTRACT THE SURFACE AND TURN IT INTO THE 2D PLAN",
            "The selected face does not disappear: it moves into the analysis position and becomes the region we calculate.",
            BLACK_INK,
        )
        self.play(
            Transform(top_chip, self.transition_chip("PHYSICAL FACE  →  SAME OUTLINE  →  MATHEMATICAL REGION")),
            run_time=0.55,
        )

        # Every final plan in the monochrome edition is VGroup(region, hatch).
        if isinstance(target, VGroup) and len(target) >= 2:
            region = target[0]
            hatch = target[1]
        else:
            region = target
            hatch = None

        start = focus.get_center() + LEFT * 0.30
        end = region.get_center() + RIGHT * min(1.10, max(0.55, region.width * 0.35))
        guide = Arrow(
            start, end, buff=0.08, color=BLACK_INK,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.12,
        )
        self.play(GrowArrow(guide), run_time=0.55)
        self.play(
            ReplacementTransform(focus, region, path_arc=-12 * DEGREES),
            stage.animate.set_opacity(0.10),
            run_time=2.25,
            rate_func=smooth,
        )
        self.wait(0.35)

        # Hatching is deliberately delayed until AFTER the surface has become 2D.
        if hatch is not None:
            self.play(
                Transform(top_chip, self.transition_chip("NOW SHADE ONLY THE REGION THE QUESTION ASKS FOR")),
                run_time=0.45,
            )
            self._reveal_hatching(hatch)

        # First read geometric dimensions/boundaries, then textual area tags.
        numeric_details = VGroup()
        tag_details = VGroup()
        for mob in details:
            if isinstance(mob, VGroup) and len(mob) == 2 and isinstance(mob[0], RoundedRectangle):
                tag_details.add(mob)
            else:
                numeric_details.add(mob)

        if len(numeric_details):
            self.play(
                LaggedStart(*[FadeIn(x, shift=UP * 0.025) for x in numeric_details], lag_ratio=0.09),
                run_time=1.15,
            )
        if len(tag_details):
            self.play(
                LaggedStart(*[FadeIn(x, shift=UP * 0.04) for x in tag_details], lag_ratio=0.12),
                run_time=0.95,
            )

        self.play(FadeOut(stage), FadeOut(guide), FadeOut(top_chip), run_time=0.75)
        self.remove(stage, guide, top_chip)
        self.wait(0.55)
        return VGroup(target, details)

    def finish_problem(self, diagram: VGroup, solution: VGroup) -> None:
        """Gentler exit so the eye is not forced through a hard cut between problems."""
        self.play(FadeOut(solution, shift=RIGHT * 0.06), run_time=0.55)
        self.play(diagram.animate.scale(0.985).set_opacity(0.0), run_time=0.65)
        self.remove(diagram, solution)
        self.camera_isometric()
