#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compact JP classroom style for the Geometry 8 circle presentations.

Derived from the project's consolidated JP classroom visual architecture:
16:9 Full HD, white background, black/gray hierarchy, persistent section
headers, safe-area assertions, large projector-safe typography and controlled
camera focus.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16
config.frame_height = 9
config.frame_rate = 30
config.background_color = WHITE

BLACK_TEXT = BLACK
BLACK_LINE = BLACK
LIGHT_GRAY = "#D7D7D7"
VERY_LIGHT_GRAY = "#F0F0F0"
PAPER_GRAY = "#F8F8F8"
WHITE_FILL = WHITE
FRAME_WIDTH = 16.0
FRAME_HEIGHT = 9.0
SAFE_WIDTH = 14.75
SAFE_HEIGHT = 7.65
CONTENT_TOP_Y = 2.60
CONTENT_BOTTOM_Y = -4.05
TIME_SCALE = float(os.getenv("LESSON_TIME_SCALE", "1.0"))
RUN_QUICK = 0.70
RUN_NORMAL = 1.00
RUN_SLOW = 1.35
RUN_CAMERA = 1.25
PAUSE_SHORT = 0.85
PAUSE_READ = 1.80
PAUSE_EXPLAIN = 2.80
PAUSE_WORK = 3.80
PAUSE_SUMMARY = 4.60
PAUSE_FINAL = 5.20


@dataclass
class TableDiagram:
    group: VGroup
    rectangles: list[list[Rectangle]]
    entries: list[list[Mobject]]
    rows: list[VGroup]
    columns: list[VGroup]
    header: VGroup
    body: VGroup


@dataclass
class FigurePanel:
    group: VGroup
    box: RoundedRectangle
    figure: Mobject
    title: Mobject | None
    caption: Mobject | None


@dataclass
class SplitLayout:
    group: VGroup
    left: Mobject
    right: Mobject


class JPMathClassroomScene(MovingCameraScene):
    def setup(self) -> None:
        super().setup()
        self.validate_lesson_data()
        self.camera.background_color = WHITE
        self.camera.frame.set(width=FRAME_WIDTH).move_to(ORIGIN)
        self.header_group: VGroup | None = None
        self.subtitle_group: Mobject | None = None

    def validate_lesson_data(self) -> None:
        pass

    def play(self, *animations, **kwargs):
        if kwargs.get("run_time") is not None:
            kwargs["run_time"] *= TIME_SCALE
        return super().play(*animations, **kwargs)

    def wait(self, duration: float = DEFAULT_WAIT_TIME, *args, **kwargs):
        return super().wait(duration * TIME_SCALE, *args, **kwargs)

    def text(self, content: str, size: int = 30, weight=NORMAL, **kwargs) -> Text:
        return Text(content, font_size=size, color=BLACK_TEXT, weight=weight, line_spacing=0.92, **kwargs)

    def math(self, expression: str, size: int = 38, **kwargs) -> MathTex:
        return MathTex(expression, font_size=size, color=BLACK_TEXT, **kwargs)

    def fit(self, mob: Mobject, max_width: float = SAFE_WIDTH, max_height: float = SAFE_HEIGHT) -> Mobject:
        if mob.width > max_width:
            mob.scale_to_fit_width(max_width)
        if mob.height > max_height:
            mob.scale_to_fit_height(max_height)
        return mob

    def formula_panel(self, expression: str, width: float = 8.4, height: float = 1.25,
                      font_size: int = 42, fill_opacity: float = 1.0) -> VGroup:
        panel = RoundedRectangle(width=width, height=height, corner_radius=0.12,
                                 stroke_color=BLACK_LINE, stroke_width=2.0,
                                 fill_color=PAPER_GRAY, fill_opacity=fill_opacity)
        equation = self.math(expression, font_size)
        self.fit(equation, width - 0.55, height - 0.28)
        equation.move_to(panel)
        return VGroup(panel, equation)

    def note_panel(self, title: str, lines: Sequence[str], width: float = 6.4,
                   title_size: int = 26, body_size: int = 23, max_text_height: float = 2.55) -> VGroup:
        title_mob = self.text(title, title_size, BOLD)
        body = VGroup(*[self.text(line, body_size) for line in lines])
        body.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        content = VGroup(title_mob, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        self.fit(content, width - 0.62, max_text_height)
        box = RoundedRectangle(width=width, height=max(1.10, content.height + 0.64), corner_radius=0.12,
                               stroke_color=BLACK_LINE, stroke_width=1.8,
                               fill_color=WHITE_FILL, fill_opacity=1.0)
        content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.31)
        return VGroup(box, content)

    def set_header(self, number: int, title: str, subtitle: str) -> None:
        number_box = RoundedRectangle(width=0.72, height=0.52, corner_radius=0.10,
                                      stroke_color=BLACK_LINE, stroke_width=2.0,
                                      fill_color=WHITE_FILL, fill_opacity=1.0)
        number_text = self.text(f"{number:02d}", 23, BOLD).move_to(number_box)
        title_text = self.text(title, 34, BOLD)
        self.fit(title_text, SAFE_WIDTH - number_box.width - 0.38, 0.56)
        title_row = VGroup(VGroup(number_box, number_text), title_text).arrange(RIGHT, buff=0.25)
        title_row.to_edge(UP, buff=0.16).to_edge(LEFT, buff=0.48)
        rule = Line(LEFT * 7.48, RIGHT * 7.48, color=LIGHT_GRAY, stroke_width=2)
        rule.next_to(title_row, DOWN, buff=0.07)
        subtitle_text = self.text(subtitle, 21)
        self.fit(subtitle_text, 14.25, 0.70)
        subtitle_text.next_to(rule, DOWN, buff=0.08).align_to(title_row, LEFT)
        new_header = VGroup(title_row, rule)
        if self.header_group is None:
            self.header_group = new_header
            self.add(new_header)
        else:
            old = self.header_group
            self.header_group = new_header
            self.play(ReplacementTransform(old, new_header), run_time=RUN_QUICK)
        if self.subtitle_group is None:
            self.subtitle_group = subtitle_text
            self.add(subtitle_text)
        else:
            old = self.subtitle_group
            self.subtitle_group = subtitle_text
            self.play(ReplacementTransform(old, subtitle_text), run_time=RUN_QUICK)

    def clear_stage(self, keep_header: bool = True) -> None:
        keep_ids: set[int] = set()
        if keep_header:
            for persistent in (self.header_group, self.subtitle_group):
                if persistent is not None:
                    keep_ids.update(id(member) for member in persistent.get_family())
        removable = [mob for mob in self.mobjects if id(mob) not in keep_ids]
        if removable:
            self.play(*[FadeOut(mob) for mob in removable], run_time=RUN_NORMAL)
        self.camera.frame.set(width=FRAME_WIDTH).move_to(ORIGIN)

    def assert_within_frame(self, mob: Mobject, label: str, margin: float = 0.03) -> None:
        left, right = mob.get_left()[0], mob.get_right()[0]
        bottom, top = mob.get_bottom()[1], mob.get_top()[1]
        if left < -FRAME_WIDTH/2 + margin or right > FRAME_WIDTH/2 - margin:
            raise ValueError(f"{label} exceeds horizontal frame bounds: {left:.3f}, {right:.3f}")
        if bottom < -FRAME_HEIGHT/2 + margin or top > FRAME_HEIGHT/2 - margin:
            raise ValueError(f"{label} exceeds vertical frame bounds: {bottom:.3f}, {top:.3f}")

    def assert_content_safe(self, mob: Mobject, label: str) -> None:
        self.assert_within_frame(mob, label, margin=0.15)
        if mob.get_top()[1] > CONTENT_TOP_Y:
            raise ValueError(f"{label} overlaps the persistent header zone")
        if mob.get_bottom()[1] < CONTENT_BOTTOM_Y:
            raise ValueError(f"{label} exceeds the safe lower content zone")

    def focus_on(self, mob: Mobject, width: float = 8.0, pause: float = PAUSE_READ) -> None:
        persistent = [x for x in (self.header_group, self.subtitle_group) if x is not None]
        if persistent:
            self.play(*[FadeOut(x) for x in persistent], run_time=RUN_QUICK)
        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.set(width=max(width, mob.width + 0.8)).move_to(mob), run_time=RUN_CAMERA)
        self.wait(pause)
        self.play(Restore(self.camera.frame), run_time=RUN_CAMERA)
        if persistent:
            self.play(*[FadeIn(x) for x in persistent], run_time=RUN_QUICK)

    def build_table(self, headers: Sequence[str], body_rows: Sequence[Sequence[str]],
                    column_widths: Sequence[float], *, math_columns: Iterable[int] = (),
                    row_height: float = 0.62, header_height: float = 0.72,
                    body_font_size: int = 25, header_font_size: int = 23) -> TableDiagram:
        math_cols = set(math_columns)
        total_width = sum(column_widths)
        total_height = header_height + len(body_rows) * row_height
        rects: list[list[Rectangle]] = []
        entries: list[list[Mobject]] = []
        rows: list[VGroup] = []
        left_edge = -total_width / 2
        top_edge = total_height / 2
        all_rows = [headers, *body_rows]
        for ri, data_row in enumerate(all_rows):
            h = header_height if ri == 0 else row_height
            y = top_edge - header_height / 2 if ri == 0 else top_edge - header_height - (ri - 1) * row_height - row_height / 2
            row_rects, row_entries = [], []
            x = left_edge
            for ci, w in enumerate(column_widths):
                box = Rectangle(width=w, height=h, stroke_color=BLACK_LINE, stroke_width=1.25,
                                fill_color=VERY_LIGHT_GRAY if ri == 0 else WHITE_FILL, fill_opacity=1)
                box.move_to([x + w/2, y, 0])
                content = data_row[ci]
                if ri == 0:
                    mob = self.math(content, header_font_size) if any(m in content for m in ("_", "^", "\\", "=")) else self.text(content, header_font_size, BOLD)
                elif ci in math_cols:
                    mob = self.math(content, body_font_size)
                else:
                    mob = self.text(content, body_font_size)
                self.fit(mob, w - 0.18, h - 0.12)
                mob.move_to(box)
                row_rects.append(box); row_entries.append(mob); x += w
            rects.append(row_rects); entries.append(row_entries); rows.append(VGroup(*row_rects, *row_entries))
        columns = []
        for ci in range(len(headers)):
            items = []
            for ri in range(len(all_rows)):
                items.extend([rects[ri][ci], entries[ri][ci]])
            columns.append(VGroup(*items))
        return TableDiagram(VGroup(*rows), rects, entries, rows, columns, rows[0], VGroup(*rows[1:]))

    def shade_cells(self, table: TableDiagram, coordinates: Sequence[tuple[int, int]], opacity: float = 1.0) -> AnimationGroup:
        return AnimationGroup(*[
            table.rectangles[r][c].animate.set_fill(LIGHT_GRAY, opacity=opacity)
            for r, c in coordinates
        ], lag_ratio=0.08)

    def animate_table_rows(self, table: TableDiagram, *, direction: np.ndarray = RIGHT,
                           pause: float = PAUSE_SHORT, include_header: bool = True) -> None:
        for row in table.rows[0 if include_header else 1:]:
            self.play(FadeIn(row, shift=direction * 0.12), run_time=RUN_NORMAL)
            self.wait(pause)

    def figure_panel(self, figure: Mobject, *, width: float = 6.2, height: float = 4.5,
                     title: str | None = None, caption: str | None = None,
                     inner_margin: float = 0.38, title_size: int = 25,
                     caption_size: int = 19, fill_color=WHITE_FILL) -> FigurePanel:
        box = RoundedRectangle(width=width, height=height, corner_radius=0.12,
                               stroke_color=BLACK_LINE, stroke_width=1.8,
                               fill_color=fill_color, fill_opacity=1)
        title_mob = self.text(title, title_size, BOLD) if title else None
        caption_mob = self.text(caption, caption_size) if caption else None
        available_h = height - 2 * inner_margin - (0.55 if title_mob else 0) - (0.48 if caption_mob else 0)
        self.fit(figure, width - 2 * inner_margin, max(0.8, available_h))
        figure.move_to(box)
        parts: list[Mobject] = [box, figure]
        if title_mob:
            self.fit(title_mob, width - 0.55, 0.42)
            title_mob.next_to(box.get_top(), DOWN, buff=0.18)
            figure.shift(DOWN * 0.18); parts.append(title_mob)
        if caption_mob:
            self.fit(caption_mob, width - 0.55, 0.40)
            caption_mob.next_to(box.get_bottom(), UP, buff=0.18)
            figure.shift(UP * 0.12); parts.append(caption_mob)
        return FigurePanel(VGroup(*parts), box, figure, title_mob, caption_mob)

    def split_layout(self, left: Mobject, right: Mobject, *, left_width: float = 6.7,
                     right_width: float = 6.7, max_height: float = 5.5,
                     gap: float = 0.45, center_y: float = -0.40) -> SplitLayout:
        self.fit(left, left_width, max_height); self.fit(right, right_width, max_height)
        left.move_to(LEFT * ((right_width + gap) / 2) + UP * center_y)
        right.move_to(RIGHT * ((left_width + gap) / 2) + UP * center_y)
        group = VGroup(left, right)
        self.fit(group, 14.4, max_height)
        return SplitLayout(group, left, right)

    def equation_stack(self, equations: Sequence[str], *, sizes: Sequence[int] | None = None,
                       buff: float = 0.26, max_width: float = 7.2, max_height: float = 4.8) -> VGroup:
        sizes = sizes or [36] * len(equations)
        mobs = VGroup(*[self.math(eq, size) for eq, size in zip(equations, sizes)])
        mobs.arrange(DOWN, aligned_edge=LEFT, buff=buff)
        self.fit(mobs, max_width, max_height)
        return mobs

    def animate_equation_stack(self, stack: VGroup, *, pause: float = PAUSE_READ, write: bool = True) -> None:
        for line in stack:
            self.play(Write(line) if write else FadeIn(line, shift=UP * 0.08), run_time=RUN_NORMAL)
            self.wait(pause)

    def process_map(self, steps: Sequence[tuple[str, str]], *, card_width: float = 4.3,
                    card_height: float = 1.10, columns: int = 3) -> VGroup:
        cards = VGroup()
        for number, text_value in steps:
            badge = RoundedRectangle(width=0.66, height=0.50, corner_radius=0.08,
                                     stroke_color=BLACK_LINE, stroke_width=1.5,
                                     fill_color=VERY_LIGHT_GRAY, fill_opacity=1)
            badge_text = self.text(number, 19, BOLD).move_to(badge)
            body = self.text(text_value, 21, BOLD)
            content = VGroup(VGroup(badge, badge_text), body).arrange(RIGHT, buff=0.18)
            self.fit(content, card_width - 0.35, card_height - 0.20)
            box = RoundedRectangle(width=card_width, height=card_height, corner_radius=0.10,
                                   stroke_color=BLACK_LINE, stroke_width=1.5,
                                   fill_color=WHITE_FILL, fill_opacity=1)
            content.move_to(box); cards.add(VGroup(box, content))
        cards.arrange_in_grid(cols=columns, buff=(0.25, 0.25))
        return cards

    def standard_opening(self, course_label: str, title: str, subtitle: str, promise: str) -> None:
        label = self.text(course_label, 28, BOLD)
        title_mob = self.text(title, 50, BOLD)
        rule = Line(LEFT * 5.5, RIGHT * 5.5, color=BLACK_LINE, stroke_width=2.2)
        subtitle_mob = self.text(subtitle, 27)
        promise_mob = self.text(promise, 25, MEDIUM)
        group = VGroup(label, title_mob, rule, subtitle_mob, promise_mob).arrange(DOWN, buff=0.30)
        self.fit(group, 14.4, 6.6)
        self.play(FadeIn(label, shift=UP * 0.18), run_time=RUN_NORMAL)
        self.play(Write(title_mob), run_time=RUN_SLOW)
        self.play(Create(rule), FadeIn(subtitle_mob), run_time=RUN_NORMAL)
        self.wait(PAUSE_EXPLAIN)
        self.play(FadeIn(promise_mob, shift=UP * 0.15), run_time=RUN_NORMAL)
        self.wait(PAUSE_FINAL)
        self.play(FadeOut(group), run_time=RUN_NORMAL)

    def standard_closing(self, sentence: str) -> None:
        closing = self.text(sentence, 34, BOLD)
        self.fit(closing, 13.8, 1.2); closing.move_to(ORIGIN)
        self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=RUN_NORMAL)
        self.play(FadeIn(closing), run_time=RUN_SLOW)
        self.wait(PAUSE_FINAL)
        self.play(FadeOut(closing), run_time=RUN_NORMAL)


def assert_close(actual: float, expected: float, *, tol: float = 1e-10, label: str = "value") -> None:
    if abs(actual - expected) > tol:
        raise ValueError(f"{label}: expected {expected}, got {actual}")
