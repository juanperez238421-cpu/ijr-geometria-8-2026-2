#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Senior QA V3 — clean, non-overlapping 3D -> 2D circle projection workflow.

Design intent
-------------
The previous smooth version still allowed complex boolean geometry to morph while
the physical 3D model remained faintly visible.  That produced transient merged
shapes (especially the annulus, patio hole and rug) and occasional visual clutter.

This revision uses a stricter choreography:

    OBSERVE 3D -> ISOLATE FACE -> TOP VIEW -> REMOVE 3D CONTEXT ->
    MOVE THE SAME FACE -> CLEAN CROSSFADE -> HATCH REGION -> DIMENSIONS -> SOLVE

The selected face itself is moved and scaled without changing topology.  Only
when it has reached the final analysis position is it cross-faded into the clean
2D region.  The 3D stage is already gone at that point, so no two incompatible
geometries can occupy the same visual space.

ManimCE 0.20.x. Final target: literal -pqh, 1920x1080, 30 fps.
"""
from __future__ import annotations

from manim import *

from Geometry8_Circle_Projection_Workshop_Final import (
    Geometry8CircleProjectionWorkshopFinal,
    BLACK_INK,
    PALE_GRAY,
    PAPER,
    GRID_DARK,
)
import Geometry8_Circle_Projection_Workshop as m


class Geometry8CircleProjectionWorkshopSeniorSmooth(Geometry8CircleProjectionWorkshopFinal):
    """Senior-expert workshop with topology-safe, merge-free 3D->2D transitions."""

    # ------------------------------------------------------------------
    # Header QA: reserve generous projector margins for every problem.
    # ------------------------------------------------------------------
    def make_header(self, data: m.ProblemData) -> VGroup:
        eyebrow = self.text(
            f"PROBLEM {data.number:02d}  ·  {data.eyebrow}", 15, BOLD
        ).move_to(UP * 4.02)

        title = self.text(data.title, 31, BOLD)
        self.fit(title, 11.85, 0.50)
        title.move_to(UP * 3.56)

        prompt = self.text(data.prompt, 18)
        self.fit(prompt, 12.55, 0.46)
        prompt.move_to(UP * 3.08)

        rule = Line(
            LEFT * 6.40, RIGHT * 6.40,
            color=GRID_DARK, stroke_width=1.35,
        ).move_to(UP * 2.72)

        return VGroup(eyebrow, title, prompt, rule)

    # ------------------------------------------------------------------
    # Compact progress cue. It only exists while the lower screen is free.
    # ------------------------------------------------------------------
    def bridge_strip(self, active: int) -> VGroup:
        labels = ("3D FACE", "TOP VIEW", "2D PLAN")
        items = VGroup()
        for i, label in enumerate(labels):
            box = RoundedRectangle(
                width=1.72, height=0.48, corner_radius=0.10,
                stroke_color=BLACK_INK,
                stroke_width=2.2 if i == active else 1.0,
                fill_color=PAPER,
                fill_opacity=0.98,
            )
            txt = self.text(label, 13, BOLD).move_to(box)
            items.add(VGroup(box, txt))
            if i < 2:
                items.add(Arrow(
                    ORIGIN, RIGHT * 0.52,
                    buff=0.02, stroke_width=1.8,
                    color=BLACK_INK,
                    max_tip_length_to_length_ratio=0.20,
                ))
        items.arrange(RIGHT, buff=0.14)
        items.move_to(DOWN * 3.52)
        self.fixed(items)
        return items

    def _replace_bridge(self, old: VGroup, active: int) -> VGroup:
        new = self.bridge_strip(active)
        self.play(FadeOut(old), FadeIn(new), run_time=0.32)
        self.remove(old)
        return new

    def _reveal_hatching(self, hatch: Mobject) -> None:
        """Progressively draw hatching only after the clean 2D region exists."""
        if isinstance(hatch, VGroup) and len(hatch) > 0:
            self.play(
                LaggedStart(*[Create(line) for line in hatch], lag_ratio=0.030),
                run_time=1.25,
            )
        else:
            self.play(FadeIn(hatch), run_time=m.RUN_NORMAL)

    @staticmethod
    def _region_and_hatch(target: Mobject) -> tuple[Mobject, Mobject | None]:
        if isinstance(target, VGroup) and len(target) >= 2:
            return target[0], target[1]
        return target, None

    # ------------------------------------------------------------------
    # Core QA fix: no ReplacementTransform between complex shapes.
    # ------------------------------------------------------------------
    def project_problem(
        self,
        stage: VGroup,
        strip: VGroup,
        focus: Mobject,
        target: Mobject,
        details: VGroup,
        *,
        theta: float,
        phi: float,
    ) -> VGroup:
        """Topology-safe 3D->2D transition with explicit temporal separation.

        Critical invariant: when the clean 2D plan appears, the 3D stage has
        already been removed.  The selected face is first moved as itself; it is
        never morphed into a different boolean path while both objects are visible.
        """
        floor, model = stage[0], stage[1]
        region, hatch = self._region_and_hatch(target)

        # STEP 1 — establish physical context.
        self.set_projection_step(
            1,
            "OBSERVE THE PHYSICAL 3D OBJECT",
            "Read the real object first. Decide which surface the question refers to.",
            BLACK_INK,
        )
        self.play(FadeIn(floor), run_time=0.55)
        if isinstance(model, VGroup) and len(model) > 1:
            self.play(
                LaggedStart(
                    *[FadeIn(part, shift=OUT * 0.020) for part in model],
                    lag_ratio=0.045,
                ),
                FadeIn(strip, shift=UP * 0.04),
                run_time=1.30,
            )
        else:
            self.play(FadeIn(model), FadeIn(strip), run_time=1.20)

        self.move_camera(
            phi=phi * DEGREES,
            theta=theta * DEGREES,
            zoom=1.01,
            run_time=1.75,
            rate_func=smooth,
        )
        self.wait(0.35)

        # STEP 2 — isolate the exact face and suppress nonessential 3D geometry.
        self.set_projection_step(
            2,
            "ISOLATE THE SURFACE USED BY THE QUESTION",
            "Keep this face in sight. Side walls and height will not enter the circle-area model.",
            BLACK_INK,
        )
        self.play(FadeIn(focus), run_time=0.42)
        self.play(
            model.animate.set_opacity(0.48),
            focus.animate.set_fill(PALE_GRAY, opacity=0.58).set_stroke(BLACK_INK, width=6.5),
            run_time=0.72,
        )
        self.play(Indicate(focus, color=BLACK_INK, scale_factor=1.035), run_time=0.85)
        self.wait(0.30)

        # STEP 3 — rotate while the selected face remains stationary in the model.
        self.set_projection_step(
            3,
            "ROTATE TO AN ORTHOGRAPHIC TOP VIEW",
            "Perspective disappears; the selected surface now shows its true planar shape.",
            BLACK_INK,
        )
        self.play(FadeOut(strip), run_time=0.35)
        bridge = self.bridge_strip(0)
        self.play(FadeIn(bridge), run_time=0.35)
        self.move_camera(
            phi=2 * DEGREES,
            theta=-90 * DEGREES,
            zoom=1.04,
            run_time=2.25,
            rate_func=smooth,
        )
        bridge = self._replace_bridge(bridge, 1)
        self.wait(0.30)

        # STEP 4A — remove ALL physical context first. Focus remains alone.
        self.set_projection_step(
            4,
            "EXTRACT THE FACE — REMOVE THE 3D CONTEXT",
            "The same selected face remains; the physical object and construction grid now leave the screen.",
            BLACK_INK,
        )
        self.play(
            FadeOut(stage),
            focus.animate.set_fill(PALE_GRAY, opacity=0.78).set_stroke(BLACK_INK, width=5.0),
            run_time=0.78,
        )
        self.remove(stage)
        self.wait(0.22)

        # STEP 4B — move the SAME face to the analysis position without morphing it.
        fw = max(float(focus.width), 1e-6)
        fh = max(float(focus.height), 1e-6)
        rw = max(float(region.width), 1e-6)
        rh = max(float(region.height), 1e-6)
        scale_factor = min(rw / fw, rh / fh)

        self.play(
            focus.animate.scale(scale_factor).move_to(region.get_center()),
            run_time=1.55,
            rate_func=smooth,
        )
        bridge = self._replace_bridge(bridge, 2)
        self.wait(0.25)

        # CLEAN CROSSFADE — same position, same size, no boolean-path interpolation.
        region.set_opacity(0.0)
        self.add(region)
        self.play(
            focus.animate.set_opacity(0.0),
            region.animate.set_opacity(1.0),
            run_time=0.48,
            rate_func=smooth,
        )
        self.remove(focus)

        # The progress strip exits BEFORE hatching/tags appear: no lower-screen merges.
        self.play(FadeOut(bridge), run_time=0.30)
        self.remove(bridge)

        # STEP 5 — reveal the mathematical information in layers.
        self.set_projection_step(
            5,
            "READ THE CLEAN 2D MODEL",
            "First identify the requested region; then read dimensions and translate the drawing into a formula.",
            BLACK_INK,
        )

        if hatch is not None:
            self._reveal_hatching(hatch)

        # Separate geometry/dimensions from boxed explanatory tags.
        numeric_details = VGroup()
        tag_details = VGroup()
        for mob in details:
            if (
                isinstance(mob, VGroup)
                and len(mob) == 2
                and isinstance(mob[0], RoundedRectangle)
            ):
                tag_details.add(mob)
            else:
                numeric_details.add(mob)

        if len(numeric_details):
            self.play(
                LaggedStart(
                    *[FadeIn(x, shift=UP * 0.018) for x in numeric_details],
                    lag_ratio=0.075,
                ),
                run_time=1.00,
            )
        if len(tag_details):
            self.play(
                LaggedStart(
                    *[FadeIn(x, shift=UP * 0.025) for x in tag_details],
                    lag_ratio=0.10,
                ),
                run_time=0.78,
            )

        self.wait(0.42)
        return VGroup(target, details)

    def finish_problem(self, diagram: VGroup, solution: VGroup) -> None:
        """Clear one layer at a time before resetting the camera for the next problem."""
        self.play(FadeOut(solution, shift=RIGHT * 0.04), run_time=0.45)
        self.play(FadeOut(diagram), run_time=0.52)
        self.remove(diagram, solution)
        self.camera_isometric()
