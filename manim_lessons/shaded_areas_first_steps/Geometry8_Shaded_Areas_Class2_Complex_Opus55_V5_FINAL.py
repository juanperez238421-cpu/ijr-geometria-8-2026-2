from __future__ import annotations

import math
import numpy as np
from manim import *

from Geometry8_Shaded_Areas_Class2_Complex_Opus55_V4_QA_FIXED import (
    Geometry8ShadedAreasClass2ComplexOpus55V4QAFixed,
)
from Geometry8_Shaded_Areas_Mixed_Basics_V2 import (
    SHADE,
    RUN_QUICK, RUN_NORMAL, RUN_SLOW,
    PAUSE_READ, PAUSE_EXPLAIN, PAUSE_WORK, PAUSE_CHALLENGE, PAUSE_FINAL,
)


class Geometry8ShadedAreasClass2ComplexOpus55V5Final(
    Geometry8ShadedAreasClass2ComplexOpus55V4QAFixed
):
    """Final V5: geometry-integrity repair + production QA.

    V4 already repaired the principal text/camera collisions. V5 preserves that
    pedagogical/animation architecture and corrects the actual geometry of every
    subtractive region so the visible negative area matches the formula and stays
    inside the intended positive silhouette.
    """

    # ------------------------------------------------------------------
    # NUMERICAL / GEOMETRY QA HELPERS
    # ------------------------------------------------------------------
    @staticmethod
    def _point_in_convex_polygon(point, vertices, tol=1e-8):
        """Return True when a 2-D point is inside/on a convex polygon."""
        p = np.array(point[:2], dtype=float)
        verts = [np.array(v[:2], dtype=float) for v in vertices]
        signs = []
        for i in range(len(verts)):
            a = verts[i]
            b = verts[(i + 1) % len(verts)]
            edge = b - a
            rel = p - a
            cross = edge[0] * rel[1] - edge[1] * rel[0]
            if abs(cross) > tol:
                signs.append(np.sign(cross))
        return not signs or all(s == signs[0] for s in signs)

    @classmethod
    def _assert_points_in_polygon(cls, points, polygon_vertices, label):
        for idx, point in enumerate(points):
            assert cls._point_in_convex_polygon(point, polygon_vertices), (
                f"{label}: sampled point {idx} is outside the intended outer region: {point}"
            )

    @staticmethod
    def _sector_sample_points(center, radius, start_angle, angle, n=41):
        """Sample the filled sector: center + radial rays + arc points."""
        c = np.array(center, dtype=float)
        pts = [c]
        for rr in (0.25 * radius, 0.5 * radius, 0.75 * radius, radius):
            for theta in np.linspace(start_angle, start_angle + angle, n):
                pts.append(c + rr * np.array([math.cos(theta), math.sin(theta), 0.0]))
        return pts

    @staticmethod
    def _circle_sample_points(center, radius, n=96):
        c = np.array(center, dtype=float)
        return [
            c + radius * np.array([math.cos(t), math.sin(t), 0.0])
            for t in np.linspace(0, TAU, n, endpoint=False)
        ] + [c]

    def validate_math_class2(self) -> None:
        super().validate_math_class2()

        facade = 108 - 2 * math.pi
        parallelogram = 108.0
        stadium = 44 + 7 * math.pi
        hexagon = 54 * math.sqrt(3) - 3 * math.pi
        capstone = 200 + 6.25 * math.pi

        assert math.isclose(facade, 101.7168146928204, rel_tol=0, abs_tol=1e-9)
        assert math.isclose(parallelogram, 108.0, rel_tol=0, abs_tol=1e-12)
        assert math.isclose(stadium, 65.99114857512855, rel_tol=0, abs_tol=1e-9)
        assert math.isclose(hexagon, 84.10624098190042, rel_tol=0, abs_tol=1e-9)
        assert math.isclose(capstone, 219.6349540849362, rel_tol=0, abs_tol=1e-9)

    # ------------------------------------------------------------------
    # PROBLEM 1 — FACADE
    # ------------------------------------------------------------------
    def facade_region(self) -> VGroup:
        s = 0.34

        body = Rectangle(
            width=12 * s,
            height=6 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        half_bottom, half_top, roof_h = 6 * s, 4 * s, 4 * s
        roof_vertices = [
            np.array([-half_bottom, y0, 0]),
            np.array([ half_bottom, y0, 0]),
            np.array([ half_top, y0 + roof_h, 0]),
            np.array([-half_top, y0 + roof_h, 0]),
        ]
        roof = Polygon(
            *roof_vertices,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        # 2 × 2 square, entirely internal to the body.
        square_gap = Square(
            side_length=2 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        square_gap.move_to(body.get_center() + LEFT * 0.95 + DOWN * 0.10)

        # True semicircle of radius 2, moved toward the roof center. Its
        # complete semicircular area is visible; no masking changes the area.
        semi_center = np.array([0.35, y0 + 0.22, 0])
        semi_gap = Sector(
            radius=2 * s,
            angle=PI,
            start_angle=0,
            arc_center=semi_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Geometry integrity checks.
        body_vertices = body.get_vertices()
        self._assert_points_in_polygon(square_gap.get_vertices(), body_vertices, "facade square")
        self._assert_points_in_polygon(
            self._sector_sample_points(semi_center, 2 * s, 0, PI),
            roof_vertices,
            "facade semicircle",
        )

        labels = VGroup(
            self.txt("12 cm", 19, BOLD).next_to(body, DOWN, buff=0.14),
            self.txt("6 cm", 19, BOLD).next_to(body, LEFT, buff=0.10),
            self.txt("B=12 · b=8 · h=4", 17, BOLD).next_to(roof, UP, buff=0.10),
            self.txt("2×2", 15, BOLD).move_to(square_gap),
            self.txt("r=2", 15, BOLD).move_to(semi_center + UP * 0.24),
        )
        return VGroup(VGroup(body, roof), square_gap, semi_gap, labels)

    # ------------------------------------------------------------------
    # PROBLEM 2 — PARALLELOGRAM
    # ------------------------------------------------------------------
    def parallelogram_region(self) -> VGroup:
        s = 0.31
        b, h, slant = 16 * s, 9 * s, 2 * s
        outer_vertices = [
            np.array([-b / 2, -h / 2, 0]),
            np.array([ b / 2, -h / 2, 0]),
            np.array([ b / 2 + slant, h / 2, 0]),
            np.array([-b / 2 + slant, h / 2, 0]),
        ]
        outer = Polygon(
            *outer_vertices,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        # Rhombus D=8, d=6. V4 inherited the V1 center too far left, so the
        # left vertex crossed the slanted boundary. V5 moves the entire exact
        # rhombus rightward; dimensions and area are unchanged.
        D, d = 8 * s, 6 * s
        rc = np.array([-0.45, 0.02, 0])
        rhombus_vertices = [
            rc + LEFT * (D / 2),
            rc + UP * (d / 2),
            rc + RIGHT * (D / 2),
            rc + DOWN * (d / 2),
        ]
        rhombus = Polygon(
            *rhombus_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Triangle b=6, h=4, placed fully inside the right half.
        tb, th = 6 * s, 4 * s
        tc = np.array([1.55, -0.18, 0])
        triangle_vertices = [
            tc + LEFT * (tb / 2) + DOWN * (th / 2),
            tc + RIGHT * (tb / 2) + DOWN * (th / 2),
            tc + UP * (th / 2),
        ]
        triangle = Polygon(
            *triangle_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # Perpendicular altitude, visually distinct from the slanted side.
        height_x = -b / 2 + slant
        height_line = DashedLine(
            np.array([height_x, -h / 2, 0]),
            np.array([height_x,  h / 2, 0]),
            color=BLACK,
            stroke_width=2,
        )

        self._assert_points_in_polygon(rhombus_vertices, outer_vertices, "parallelogram rhombus")
        self._assert_points_in_polygon(triangle_vertices, outer_vertices, "parallelogram triangle")

        labels = VGroup(
            self.txt("b=16 cm", 18, BOLD).next_to(outer, DOWN, buff=0.12),
            self.txt("h=9 cm", 18, BOLD).next_to(height_line, LEFT, buff=0.08),
            self.txt("D=8 · d=6", 15, BOLD).move_to(rhombus),
            self.txt("b=6 · h=4", 14, BOLD).move_to(triangle),
        )
        return VGroup(outer, rhombus, triangle, height_line, labels)

    # ------------------------------------------------------------------
    # PROBLEM 3 — STADIUM
    # ------------------------------------------------------------------
    def stadium_region(self) -> VGroup:
        s = 0.36
        rect = Rectangle(
            width=10 * s,
            height=6 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        r = 3 * s
        left_cap = Sector(
            radius=r,
            angle=PI,
            start_angle=PI / 2,
            arc_center=rect.get_left(),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        right_cap = Sector(
            radius=r,
            angle=PI,
            start_angle=-PI / 2,
            arc_center=rect.get_right(),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        square = Square(
            side_length=4 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(rect)

        # Two ACTUAL quarter circles, each r=2. They are inset slightly from
        # the rectangle corners so neither the white fill nor its stroke can
        # leak across the stadium silhouette. Insetting does not alter area.
        rq = 2 * s
        inset = 0.12
        q1_center = rect.get_corner(UL) + RIGHT * inset + DOWN * inset
        q1 = Sector(
            radius=rq,
            angle=PI / 2,
            start_angle=-PI / 2,     # inward: DOWN -> RIGHT
            arc_center=q1_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        q2_center = rect.get_corner(DR) + LEFT * inset + UP * inset
        q2 = Sector(
            radius=rq,
            angle=PI / 2,
            start_angle=PI / 2,      # inward: UP -> LEFT
            arc_center=q2_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        rect_vertices = rect.get_vertices()
        self._assert_points_in_polygon(square.get_vertices(), rect_vertices, "stadium square")
        self._assert_points_in_polygon(
            self._sector_sample_points(q1_center, rq, -PI / 2, PI / 2),
            rect_vertices,
            "stadium quarter 1",
        )
        self._assert_points_in_polygon(
            self._sector_sample_points(q2_center, rq, PI / 2, PI / 2),
            rect_vertices,
            "stadium quarter 2",
        )

        labels = VGroup(
            self.txt("rectangle 10×6", 18, BOLD).next_to(rect, DOWN, buff=0.12),
            self.txt("caps r=3", 17, BOLD).next_to(left_cap, LEFT, buff=0.08),
            self.txt("4×4", 15, BOLD).move_to(square),
            self.txt("quarter gaps r=2", 16, BOLD).next_to(rect, UP, buff=0.10),
        )
        return VGroup(VGroup(rect, left_cap, right_cap), square, q1, q2, labels)

    # ------------------------------------------------------------------
    # PROBLEM 4 — REGULAR HEXAGON + 120° SECTOR
    # ------------------------------------------------------------------
    def hexagon_sector_region(self) -> VGroup:
        s = 0.43
        side = 6 * s
        hexagon = RegularPolygon(
            n=6,
            radius=side,
            start_angle=0,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        # Exact 120° sector, r=3, centered in the hexagon. r=3 is smaller
        # than the apothem 3√3, therefore the entire sector is internal.
        sector_radius = 3 * s
        sector_start = -PI / 3
        sector_angle = 2 * PI / 3
        center = hexagon.get_center()
        sector = Sector(
            radius=sector_radius,
            angle=sector_angle,
            start_angle=sector_start,
            arc_center=center,
            stroke_color=BLACK,
            stroke_width=2.5,
            fill_color=WHITE,
            fill_opacity=1,
        )

        apothem_length = 3 * math.sqrt(3) * s
        apothem = DashedLine(
            center,
            center + UP * apothem_length,
            color=BLACK,
            stroke_width=2,
        )

        self._assert_points_in_polygon(
            self._sector_sample_points(center, sector_radius, sector_start, sector_angle),
            hexagon.get_vertices(),
            "hexagon 120-degree sector",
        )

        angle_label = self.txt("120°", 16, BOLD).move_to(center + RIGHT * 0.63)
        labels = VGroup(
            self.txt("regular hexagon · side=6", 18, BOLD).next_to(hexagon, DOWN, buff=0.12),
            self.math(r"P=36\ {\rm cm}", 25).next_to(hexagon, LEFT, buff=0.10),
            self.math(r"a=3\sqrt3\ {\rm cm}", 24).next_to(apothem, LEFT, buff=0.08),
            self.txt("sector r=3", 16, BOLD).next_to(sector, RIGHT, buff=0.10),
            angle_label,
        )
        return VGroup(hexagon, sector, apothem, labels)

    # ------------------------------------------------------------------
    # PROBLEM 5 — CAPSTONE
    # ------------------------------------------------------------------
    def capstone_region(self) -> VGroup:
        s = 0.255

        body = Rectangle(
            width=16 * s,
            height=10 * s,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )
        y0 = body.get_top()[1]

        hb, ht, trap_h = 8 * s, 5 * s, 4 * s
        roof = Polygon(
            np.array([-hb, y0, 0]),
            np.array([ hb, y0, 0]),
            np.array([ ht, y0 + trap_h, 0]),
            np.array([-ht, y0 + trap_h, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        cap = Sector(
            radius=5 * s,
            angle=PI,
            start_angle=0,
            arc_center=np.array([0, y0 + trap_h, 0]),
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=SHADE,
            fill_opacity=0.94,
        )

        # Circle r=2, fully internal.
        circle_center = body.get_center() + LEFT * 1.42 + UP * 0.20
        circle = Circle(
            radius=2 * s,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(circle_center)

        # Rhombus D=6, d=4, separated from the circle and the sector.
        D, d = 6 * s, 4 * s
        rc = body.get_center() + UP * 0.34
        rhombus_vertices = [
            rc + LEFT * (D / 2),
            rc + UP * (d / 2),
            rc + RIGHT * (D / 2),
            rc + DOWN * (d / 2),
        ]
        rhombus = Polygon(
            *rhombus_vertices,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        # 90° sector r=3. V4 placed this too low/right and its lower arc
        # crossed the body boundary. V5 moves the COMPLETE exact sector well
        # inside the rectangle. No clipping/masking is used.
        sector_center = body.get_center() + RIGHT * 1.05 + DOWN * 0.35
        sector_radius = 3 * s
        sector_start = PI
        sector_angle = PI / 2
        sector = Sector(
            radius=sector_radius,
            angle=sector_angle,
            start_angle=sector_start,
            arc_center=sector_center,
            stroke_color=BLACK,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )

        body_vertices = body.get_vertices()
        self._assert_points_in_polygon(
            self._circle_sample_points(circle_center, 2 * s),
            body_vertices,
            "capstone circle",
        )
        self._assert_points_in_polygon(rhombus_vertices, body_vertices, "capstone rhombus")
        self._assert_points_in_polygon(
            self._sector_sample_points(sector_center, sector_radius, sector_start, sector_angle),
            body_vertices,
            "capstone 90-degree sector",
        )

        labels = VGroup(
            self.txt("16 × 10", 15, BOLD).next_to(body, DOWN, buff=0.15),
            self.txt("B=16 · b=10 · h=4", 13, BOLD).next_to(roof, RIGHT, buff=0.12),
            self.txt("semicircle · r=5", 13, BOLD).next_to(cap, UP, buff=0.10),
            self.txt("r=2", 12, BOLD).move_to(circle),
            self.txt("D=6 · d=4", 11, BOLD).move_to(rhombus),
            self.txt("90° · r=3", 10, BOLD).move_to(sector_center + LEFT * 0.23 + DOWN * 0.20),
        )

        return VGroup(VGroup(body, roof, cap), circle, rhombus, sector, labels)

    # ------------------------------------------------------------------
    # FINAL ASSEMBLY — preserve V4 pedagogy/camera architecture
    # ------------------------------------------------------------------
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
