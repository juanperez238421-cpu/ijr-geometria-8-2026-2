from __future__ import annotations

import numpy as np
from manim import *

from Geometry8_Shaded_Areas_Class2_Complex_Opus55_V3 import (
    Geometry8ShadedAreasClass2ComplexOpus55V3,
)
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import (
    DARK_GRAY,
    RUN_QUICK, RUN_NORMAL, RUN_SLOW,
    PAUSE_READ, PAUSE_EXPLAIN, PAUSE_WORK, PAUSE_CHALLENGE, PAUSE_FINAL,
)


class Geometry8ShadedAreasClass2ComplexOpus55V4QAFixed(
    Geometry8ShadedAreasClass2ComplexOpus55V3
):
    """QA-fixed V4.

    Repairs the main visual defects observed in the rendered V3:
    - calculation cards no longer overlap the reasoning ledger;
    - local zoom calculations isolate the selected geometric piece;
    - sign badges no longer cover dimension labels;
    - camera zoom keeps safe margins around cards and geometry;
    - capstone labels are repositioned to remove crowding.
    """

    def local_calc(self, target, title, equations, side=RIGHT):
        # Hide persistent reasoning during local calculations so there is no
        # text-on-text collision behind the calculation card.
        old_reasoning = self.reasoning

        # The detailed calculation should focus on only the selected piece.
        # A clean copy remains at full opacity while the full diagram is dimmed.
        focus_target = target.copy().set_z_index(20)
        self.add(focus_target)

        fade_anims = []
        if self.geometry is not None:
            fade_anims.append(self.geometry.animate.set_opacity(0.14))
        if old_reasoning is not None:
            fade_anims.append(old_reasoning.animate.set_opacity(0.0))
        if getattr(self, "active_badges", None) is not None:
            fade_anims.append(self.active_badges.animate.set_opacity(0.0))
        if fade_anims:
            self.play(*fade_anims, run_time=RUN_NORMAL)

        heading = self.txt(title, 17, BOLD)
        eqs = VGroup(*[
            self.math(eq, 27) for eq in equations
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        content = VGroup(heading, eqs).arrange(
            DOWN, aligned_edge=LEFT, buff=0.14
        )
        self.fit(content, 3.95, 2.45)

        box = SurroundingRectangle(
            content,
            buff=0.18,
            corner_radius=0.08,
            stroke_color=BLACK,
            stroke_width=1.8,
            fill_color=WHITE,
            fill_opacity=0.985,
        )
        card = VGroup(box, content).set_z_index(30)

        # Safe automatic side selection. The original V3 sometimes placed
        # cards where they collided with labels or fell too close to the crop.
        frame_cx = focus_target.get_center()[0]
        if side is DOWN:
            # Wide objects such as two circular caps are safer with the card
            # below but with extra spacing.
            card.next_to(focus_target, DOWN, buff=0.48)
        elif frame_cx < -3.4:
            card.next_to(focus_target, RIGHT, buff=0.46)
        else:
            card.next_to(focus_target, LEFT, buff=0.46)

        focus = VGroup(focus_target, card)
        # Generous margins prevent clipping at the zoomed frame edges.
        zoom_width = max(6.2, min(12.4, focus.width * 1.60))

        self.play(
            self.camera.frame.animate.move_to(focus).set(width=zoom_width),
            run_time=RUN_SLOW,
        )
        self.play(
            Indicate(focus_target, scale_factor=1.035),
            run_time=RUN_NORMAL,
        )
        self.play(FadeIn(box), FadeIn(heading), run_time=RUN_NORMAL)

        for eq in eqs:
            self.play(Write(eq), run_time=RUN_SLOW)
            self.wait(PAUSE_READ)

        self.wait(PAUSE_WORK)

        self.play(FadeOut(card), FadeOut(focus_target), run_time=RUN_NORMAL)
        self.play(
            self.camera.frame.animate.move_to(ORIGIN).set(width=config.frame_width),
            run_time=RUN_SLOW,
        )

        restore_anims = []
        if self.geometry is not None:
            restore_anims.append(self.geometry.animate.set_opacity(1.0))
        if old_reasoning is not None:
            restore_anims.append(old_reasoning.animate.set_opacity(1.0))
        if restore_anims:
            self.play(*restore_anims, run_time=RUN_NORMAL)

    def sign_badge(self, target, symbol):
        # Put badges near corners instead of the center. V3 often covered
        # labels such as 2×2, D=8 d=6, 4×4, etc.
        c = Circle(
            radius=0.17,
            stroke_color=BLACK,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        t = self.txt(symbol, 18, BOLD).move_to(c)
        badge = VGroup(c, t)

        if symbol == "+":
            pos = target.get_corner(UL) + RIGHT*0.25 + DOWN*0.25
        else:
            pos = target.get_corner(UR) + LEFT*0.05 + UP*0.18

        return badge.move_to(pos).set_z_index(25)

    def mark_signed(self, positives, negatives):
        badges = VGroup()
        for mob in positives:
            badge = self.sign_badge(mob, "+")
            badges.add(badge)
            self.play(
                FadeIn(badge, scale=0.75),
                Indicate(mob, scale_factor=1.02),
                run_time=RUN_NORMAL,
            )
            self.wait(PAUSE_READ/2)

        for mob in negatives:
            badge = self.sign_badge(mob, "−")
            badges.add(badge)
            self.play(
                FadeIn(badge, scale=0.75),
                Indicate(mob, scale_factor=1.04),
                run_time=RUN_NORMAL,
            )
            self.wait(PAUSE_READ/2)

        self.active_badges = badges
        return badges

    def capstone_region(self):
        # Same mathematics as V1/V3, but labels are placed in dedicated safe
        # positions to avoid the dense crowding visible in the V3 render.
        s = 0.255

        body = Rectangle(
            width=16*s,
            height=10*s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color="#B9B9B9",
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        hb, ht, trap_h = 8*s, 5*s, 4*s
        roof = Polygon(
            np.array([-hb, y0, 0]),
            np.array([ hb, y0, 0]),
            np.array([ ht, y0+trap_h, 0]),
            np.array([-ht, y0+trap_h, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color="#B9B9B9",
            fill_opacity=0.94,
        )

        cap = Sector(
            radius=5*s,
            angle=PI,
            start_angle=0,
            arc_center=np.array([0, y0+trap_h, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color="#B9B9B9",
            fill_opacity=0.94,
        )

        circle = Circle(
            radius=2*s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        circle.move_to(body.get_center()+LEFT*1.15+UP*0.20)

        D, d = 6*s, 4*s
        rc = body.get_center()+DOWN*0.30
        rhombus = Polygon(
            rc+LEFT*(D/2),
            rc+UP*(d/2),
            rc+RIGHT*(D/2),
            rc+DOWN*(d/2),
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        sector = Sector(
            radius=3*s,
            angle=PI/2,
            start_angle=PI,
            arc_center=body.get_center()+RIGHT*1.65+DOWN*0.55,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Clean label hierarchy:
        # outer dimensions outside; gap dimensions inside the white regions.
        labels = VGroup(
            self.txt("16 × 10", 15, BOLD).next_to(body, DOWN, buff=0.15),
            self.txt("B=16 · b=10 · h=4", 13, BOLD).next_to(roof, RIGHT, buff=0.12),
            self.txt("semicircle · r=5", 13, BOLD).next_to(cap, UP, buff=0.10),
            self.txt("r=2", 12, BOLD).move_to(circle),
            self.txt("D=6 · d=4", 11, BOLD).move_to(rhombus),
            self.txt("90° · r=3", 10, BOLD).move_to(sector.get_center()+LEFT*0.03),
        )

        return VGroup(VGroup(body, roof, cap), circle, rhombus, sector, labels)

    def closing_v4(self):
        self.play(
            *[FadeOut(m) for m in list(self.mobjects)],
            run_time=RUN_NORMAL,
        )

        title = self.txt("COMPLEX FIGURE ≠ COMPLEX METHOD", 44, BOLD)
        formula = self.formula_box(
            r"A_{shaded}=sum A_{(+)}-sum A_{(-)}",
            width=9.0,
            height=1.12,
            size=39,
        )
        steps = VGroup(
            self.txt("1. Identify every familiar figure.", 24, BOLD),
            self.txt("2. Mark + or − before calculating.", 24, BOLD),
            self.txt("3. Calculate one local area at a time.", 24, BOLD),
            self.txt("4. Build positive and negative subtotals.", 24, BOLD),
            self.txt("5. Combine and verify.", 24, BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        group = VGroup(title, formula, steps).arrange(DOWN, buff=0.26)
        self.fit(group, 13.2, 5.8)
        group.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP*0.08), run_time=RUN_SLOW)
        self.play(FadeIn(formula), run_time=RUN_NORMAL)

        for line in steps:
            self.play(FadeIn(line, shift=RIGHT*0.08), run_time=RUN_NORMAL)
            self.wait(PAUSE_READ/2)

        self.wait(PAUSE_FINAL)

    def construct(self):
        self.validate_math_class2()
        self.opening_class2()
        self.formula_atlas()
        self.build_workbench_class2()

        self.beat_facade_v3()
        self.beat_parallelogram_v3()
        self.beat_stadium_v3()
        self.beat_hexagon_v3()
        self.beat_capstone_v3()

        self.closing_v4()
