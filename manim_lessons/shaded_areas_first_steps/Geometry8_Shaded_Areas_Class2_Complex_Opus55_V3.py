from __future__ import annotations
import math
from manim import *
from Geometry8_Shaded_Areas_Class2_Complex_Opus55_V1 import Geometry8ShadedAreasClass2ComplexOpus55V1
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import DARK_GRAY, RUN_QUICK, RUN_NORMAL, RUN_SLOW, PAUSE_READ, PAUSE_EXPLAIN, PAUSE_WORK, PAUSE_CHALLENGE, PAUSE_FINAL

class Geometry8ShadedAreasClass2ComplexOpus55V3(MovingCameraScene, Geometry8ShadedAreasClass2ComplexOpus55V1):
    """V3: explicit signed areas, real camera zooms, slower step-by-step calculations."""

    def local_calc(self, target, title, equations, side=RIGHT):
        heading = self.txt(title, 18, BOLD)
        eqs = VGroup(*[self.math(eq, 29) for eq in equations]).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        content = VGroup(heading, eqs).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        box = SurroundingRectangle(content, buff=0.18, corner_radius=0.08, stroke_color=BLACK, stroke_width=1.8, fill_color=WHITE, fill_opacity=0.98)
        card = VGroup(box, content).next_to(target, side, buff=0.28)
        focus = VGroup(target, card)
        width = max(4.8, min(10.4, focus.width * 1.28))
        self.play(self.camera.frame.animate.move_to(focus).set(width=width), run_time=RUN_SLOW)
        self.play(Indicate(target, scale_factor=1.04), run_time=RUN_NORMAL)
        self.play(FadeIn(box), FadeIn(heading), run_time=RUN_NORMAL)
        for eq in eqs:
            self.play(Write(eq), run_time=RUN_SLOW)
            self.wait(PAUSE_READ)
        self.wait(PAUSE_WORK)
        self.play(FadeOut(card), run_time=RUN_NORMAL)
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=config.frame_width), run_time=RUN_SLOW)

    def sign_badge(self, target, symbol):
        c = Circle(radius=0.19, stroke_color=BLACK, stroke_width=2, fill_color=WHITE, fill_opacity=1)
        t = self.txt(symbol, 21, BOLD).move_to(c)
        return VGroup(c, t).move_to(target.get_center() + UP*0.24)

    def mark_signed(self, positives, negatives):
        badges = VGroup()
        for mob in positives:
            b = self.sign_badge(mob, "+"); badges.add(b)
            self.play(FadeIn(b, scale=0.7), Indicate(mob, scale_factor=1.02), run_time=RUN_NORMAL); self.wait(PAUSE_READ/2)
        for mob in negatives:
            b = self.sign_badge(mob, "−"); badges.add(b)
            self.play(FadeIn(b, scale=0.7), Indicate(mob, scale_factor=1.05), run_time=RUN_NORMAL); self.wait(PAUSE_READ/2)
        return badges

    def signed_ledger(self, positive_rows, negative_rows):
        p = self.reason_card("POSITIVE AREAS (+)", positive_rows)
        n = self.reason_card("NEGATIVE AREAS (−)", negative_rows)
        return VGroup(p, n).arrange(DOWN, buff=0.16)

    def beat_facade_v3(self):
        self.step(0); geo=self.facade_region(); self.swap_left(geo); whole,sq,semi,_=geo; rect,trap=whole
        self.swap_right(self.reason_card("EXAMPLE 1 · FOUR COMPONENTS", ["Outside = rectangle + trapezoid.", "Gaps = square + semicircle.", "First classify signs. Then calculate."])); self.wait(PAUSE_EXPLAIN)
        self.step(1); self.play(Indicate(rect),Indicate(trap),run_time=RUN_NORMAL); self.wait(PAUSE_READ); self.play(Indicate(sq),Indicate(semi),run_time=RUN_NORMAL); self.wait(PAUSE_READ)
        self.step(2); badges=self.mark_signed([rect,trap],[sq,semi]); self.swap_right(self.signed_ledger(["A1 rectangle","A2 trapezoid"],["A3 square gap","A4 semicircle gap"])); self.wait(PAUSE_EXPLAIN)
        self.step(3)
        self.local_calc(rect,"A1 · RECTANGLE (+)",[r"A_1=bh",r"A_1=12(6)",r"A_1=72\,cm^2"],RIGHT)
        self.local_calc(trap,"A2 · TRAPEZOID (+)",[r"A_2=\frac{(B+b)h}{2}",r"A_2=\frac{(12+8)(4)}{2}",r"A_2=40\,cm^2"],RIGHT)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL",r"A_{(+)}=72+40=112\,cm^2",31)); self.wait(PAUSE_WORK)
        self.local_calc(sq,"A3 · SQUARE GAP (−)",[r"A_3=l^2",r"A_3=2^2",r"A_3=4\,cm^2"],RIGHT)
        self.local_calc(semi,"A4 · SEMICIRCLE GAP (−)",[r"A_4=\frac{\pi r^2}{2}",r"A_4=\frac{\pi(2)^2}{2}",r"A_4=2\pi\,cm^2"],LEFT)
        self.swap_right(self.equation_card("NEGATIVE SUBTOTAL",r"A_{(-)}=4+2\pi",31)); self.wait(PAUSE_WORK)
        final=VGroup(self.math(r"A_s=A_{(+)}-A_{(-)}",30),self.math(r"A_s=112-(4+2\pi)",30),self.math(r"A_s=108-2\pi",31),self.math(r"A_s\approx101.72\,cm^2",31)).arrange(DOWN,buff=0.18)
        self.swap_right(final); self.wait(PAUSE_CHALLENGE)
        self.step(4); self.swap_right(self.reason_card("CHECK",["101.72 < 112 ✓","Each gap subtracted once ✓","Square units ✓","Approximate π only at the end ✓"])); self.wait(PAUSE_EXPLAIN); self.play(FadeOut(badges),run_time=RUN_NORMAL)

    def beat_parallelogram_v3(self):
        self.step(0); geo=self.parallelogram_region(); self.swap_left(geo); outer,rh,tri,hline,_=geo
        self.swap_right(self.reason_card("EXAMPLE 2 · THREE FORMULAS",["Whole = parallelogram.","Gaps = rhombus + triangle.","The perpendicular height matters."])); self.wait(PAUSE_EXPLAIN)
        self.step(1); self.play(Indicate(hline),Indicate(rh),Indicate(tri),run_time=RUN_NORMAL); self.wait(PAUSE_READ)
        self.step(2); badges=self.mark_signed([outer],[rh,tri]); self.swap_right(self.signed_ledger(["A1 parallelogram"],["A2 rhombus","A3 triangle"])); self.wait(PAUSE_EXPLAIN)
        self.step(3)
        self.local_calc(outer,"A1 · PARALLELOGRAM (+)",[r"A_1=bh",r"A_1=16(9)",r"A_1=144\,cm^2"],RIGHT)
        self.local_calc(rh,"A2 · RHOMBUS GAP (−)",[r"A_2=\frac{Dd}{2}",r"A_2=\frac{8(6)}{2}",r"A_2=24\,cm^2"],RIGHT)
        self.local_calc(tri,"A3 · TRIANGLE GAP (−)",[r"A_3=\frac{bh}{2}",r"A_3=\frac{6(4)}{2}",r"A_3=12\,cm^2"],LEFT)
        final=VGroup(self.math(r"A_s=144-24-12",32),self.math(r"A_s=108\,cm^2",34)).arrange(DOWN,buff=0.22); self.swap_right(final); self.wait(PAUSE_WORK)
        self.step(4); self.swap_right(self.reason_card("CHECK",["Slanted side was not used as h.","Rhombus uses diagonals.","108 < 144 ✓"])); self.wait(PAUSE_EXPLAIN); self.play(FadeOut(badges),run_time=RUN_NORMAL)

    def beat_stadium_v3(self):
        self.step(0); geo=self.stadium_region(); self.swap_left(geo); outer,sq,q1,q2,_=geo; rect,lcap,rcap=outer
        self.swap_right(self.reason_card("EXAMPLE 3 · CIRCLE FRACTIONS",["Outside = rectangle + two semicircles.","Inside = square + two quarter circles.","Combine equal fractions before arithmetic."])); self.wait(PAUSE_EXPLAIN)
        self.step(1); self.play(Indicate(VGroup(lcap,rcap)),run_time=RUN_NORMAL); self.wait(PAUSE_READ); self.play(Indicate(VGroup(q1,q2)),run_time=RUN_NORMAL); self.wait(PAUSE_READ)
        self.step(2); badges=self.mark_signed([rect,lcap,rcap],[sq,q1,q2]); self.swap_right(self.signed_ledger(["rectangle","2 semicircles = 1 circle"],["square","2 quarters = 1 semicircle"])); self.wait(PAUSE_EXPLAIN)
        self.step(3)
        self.local_calc(rect,"A1 · RECTANGLE (+)",[r"A_1=10(6)",r"A_1=60\,cm^2"],RIGHT)
        self.local_calc(VGroup(lcap,rcap),"A2 · TWO SEMICIRCLES (+)",[r"2\left(\frac{\pi(3)^2}{2}\right)",r"A_2=9\pi\,cm^2"],DOWN)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL",r"A_{(+)}=60+9\pi",31)); self.wait(PAUSE_WORK)
        self.local_calc(sq,"A3 · SQUARE GAP (−)",[r"A_3=4^2",r"A_3=16\,cm^2"],RIGHT)
        self.local_calc(VGroup(q1,q2),"A4 · TWO QUARTERS (−)",[r"2\left(\frac{\pi(2)^2}{4}\right)",r"A_4=2\pi\,cm^2"],DOWN)
        self.swap_right(self.equation_card("NEGATIVE SUBTOTAL",r"A_{(-)}=16+2\pi",31)); self.wait(PAUSE_WORK)
        final=VGroup(self.math(r"A_s=(60+9\pi)-(16+2\pi)",29),self.math(r"A_s=44+7\pi",32),self.math(r"A_s\approx65.99\,cm^2",31)).arrange(DOWN,buff=0.18); self.swap_right(final); self.wait(PAUSE_CHALLENGE)
        self.step(4); self.swap_right(self.reason_card("CHECK",["2 semicircles → one circle ✓","2 quarters → one semicircle ✓","Exact form retained ✓"])); self.wait(PAUSE_EXPLAIN); self.play(FadeOut(badges),run_time=RUN_NORMAL)

    def beat_hexagon_v3(self):
        self.step(0); geo=self.hexagon_sector_region(); self.swap_left(geo); hx,sector,apothem,_=geo
        self.swap_right(self.reason_card("EXAMPLE 4 · POLYGON + SECTOR",["Whole = regular hexagon.","Gap = 120° sector.","Use perimeter + apothem, then angle fraction."])); self.wait(PAUSE_EXPLAIN)
        self.step(1); self.play(Indicate(apothem),Indicate(sector),run_time=RUN_NORMAL); self.wait(PAUSE_READ)
        self.step(2); badges=self.mark_signed([hx],[sector]); self.swap_right(self.signed_ledger(["A1 regular hexagon"],["A2 120° sector"])); self.wait(PAUSE_EXPLAIN)
        self.step(3)
        self.local_calc(hx,"A1 · HEXAGON (+)",[r"A_1=\frac{Pa}{2}",r"A_1=\frac{36(3\sqrt3)}{2}",r"A_1=54\sqrt3\,cm^2"],RIGHT)
        self.local_calc(sector,"A2 · 120° SECTOR (−)",[r"A_2=\frac{120}{360}\pi(3)^2",r"A_2=3\pi\,cm^2"],LEFT)
        final=VGroup(self.math(r"A_s=54\sqrt3-3\pi",31),self.math(r"A_s\approx84.11\,cm^2",31)).arrange(DOWN,buff=0.20); self.swap_right(final); self.wait(PAUSE_WORK)
        self.step(4); self.swap_right(self.reason_card("CHECK",["Apothem is perpendicular.","120/360 = 1/3 ✓","Exact radical and π kept until the end."])); self.wait(PAUSE_EXPLAIN); self.play(FadeOut(badges),run_time=RUN_NORMAL)

    def beat_capstone_v3(self):
        self.step(0); geo=self.capstone_region(); self.swap_left(geo); outer,circle,rh,sector,_=geo; body,roof,cap=outer
        self.swap_right(self.reason_card("CAPSTONE · SIX TERMS",["Positive: rectangle + trapezoid + semicircle.","Negative: circle + rhombus + 90° sector.","Calculate every term before combining."])); self.wait(PAUSE_CHALLENGE)
        self.step(1); self.play(Indicate(body),Indicate(roof),Indicate(cap),run_time=RUN_NORMAL); self.wait(PAUSE_READ); self.play(Indicate(circle),Indicate(rh),Indicate(sector),run_time=RUN_NORMAL); self.wait(PAUSE_READ)
        self.step(2); badges=self.mark_signed([body,roof,cap],[circle,rh,sector]); self.swap_right(self.signed_ledger(["A1 rectangle","A2 trapezoid","A3 semicircle"],["A4 circle","A5 rhombus","A6 90° sector"])); self.wait(PAUSE_EXPLAIN)
        self.step(3)
        self.local_calc(body,"A1 · RECTANGLE (+)",[r"A_1=16(10)",r"A_1=160\,cm^2"],RIGHT)
        self.local_calc(roof,"A2 · TRAPEZOID (+)",[r"A_2=\frac{(16+10)(4)}{2}",r"A_2=52\,cm^2"],RIGHT)
        self.local_calc(cap,"A3 · SEMICIRCLE (+)",[r"A_3=\frac{\pi(5)^2}{2}",r"A_3=12.5\pi\,cm^2"],DOWN)
        self.swap_right(self.equation_card("POSITIVE SUBTOTAL",r"A_{(+)}=212+12.5\pi",31)); self.wait(PAUSE_CHALLENGE)
        self.local_calc(circle,"A4 · CIRCLE GAP (−)",[r"A_4=\pi(2)^2",r"A_4=4\pi\,cm^2"],RIGHT)
        self.local_calc(rh,"A5 · RHOMBUS GAP (−)",[r"A_5=\frac{6(4)}{2}",r"A_5=12\,cm^2"],LEFT)
        self.local_calc(sector,"A6 · 90° SECTOR GAP (−)",[r"A_6=\frac{90}{360}\pi(3)^2",r"A_6=2.25\pi\,cm^2"],LEFT)
        self.swap_right(self.equation_card("NEGATIVE SUBTOTAL",r"A_{(-)}=12+6.25\pi",31)); self.wait(PAUSE_CHALLENGE)
        final=VGroup(self.math(r"A_s=A_{(+)}-A_{(-)}",29),self.math(r"A_s=(212+12.5\pi)-(12+6.25\pi)",27),self.math(r"A_s=200+6.25\pi",31),self.math(r"A_s\approx219.63\,cm^2",31)).arrange(DOWN,buff=0.16); self.swap_right(final); self.wait(PAUSE_CHALLENGE)
        self.step(4); self.swap_right(self.reason_card("FINAL CHECK",["3 positive terms counted once ✓","3 negative terms subtracted once ✓","Result smaller than outer total ✓","cm² ✓"])); self.wait(PAUSE_FINAL); self.play(FadeOut(badges),run_time=RUN_NORMAL)

    def closing_v3(self):
        self.play(*[FadeOut(m) for m in list(self.mobjects)],run_time=RUN_NORMAL)
        title=self.txt("COMPLEX FIGURE ≠ COMPLEX METHOD",46,BOLD)
        formula=self.formula_box(r"A_{shaded}=\sum A_{(+)}-\sum A_{(-)}",width=9.2,height=1.16,size=40)
        steps=VGroup(self.txt("1. Identify every familiar figure.",25,BOLD),self.txt("2. Mark + or − before calculating.",25,BOLD),self.txt("3. Calculate one local area at a time.",25,BOLD),self.txt("4. Build positive and negative subtotals.",25,BOLD),self.txt("5. Combine and verify.",25,BOLD)).arrange(DOWN,aligned_edge=LEFT,buff=0.16)
        g=VGroup(title,formula,steps).arrange(DOWN,buff=0.28); self.fit(g,13.6,6.2); g.move_to(ORIGIN)
        self.play(FadeIn(title,shift=UP*0.08),run_time=RUN_SLOW); self.play(FadeIn(formula),run_time=RUN_NORMAL)
        for line in steps: self.play(FadeIn(line,shift=RIGHT*0.08),run_time=RUN_NORMAL); self.wait(PAUSE_READ/2)
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
        self.closing_v3()
