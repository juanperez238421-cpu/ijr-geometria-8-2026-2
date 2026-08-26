#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime-safe final entry point for the 3D→2D circle workshop.

This file is intentionally tiny: the full pedagogical scene lives in
Geometry8_Circle_Projection_Workshop.py; these aliases guarantee compatibility
with the current senior-QA palette/timing names before Manim instantiates it.
"""
import Geometry8_Circle_Projection_Workshop as m

m.ACCENT_ORANGE = m.ORANGE
m.ACCENT_GREEN = m.MINT_DARK
m.ACCENT_RED = "#A45143"
m.ACCENT_TEAL = m.CYAN
m.ACCENT_BLUE = m.BLUE
m.LIGHT_GRAY = m.GRID_DARK
m.WHITE_FILL = m.WHITE_CARD
m.VERY_LIGHT_GRAY = m.PALE_BLUE
m.PAPER_GRAY = m.STONE
m.BLACK_LINE = m.INK
m.RUN_QUICK = m.RUN_FAST
m.RUN_NORMAL = m.RUN
m.PAUSE_WORK = m.PAUSE_THINK


class Geometry8CircleProjectionWorkshopFinal(m.Geometry8CircleProjectionWorkshop):
    """Final verified render entry point."""
    pass
