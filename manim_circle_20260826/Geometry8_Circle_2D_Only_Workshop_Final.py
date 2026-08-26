#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime-safe final entrypoint for the 2D-only Geometry 8 circle workshop."""
import numpy as np
import Geometry8_Circle_2D_Only_Workshop as m

# The scene uses numpy inside runtime geometry helpers. Keep the source scene
# intentionally readable and inject the module here before Manim instantiates it.
m.np = np


class Geometry8Circle2DOnlyWorkshopFinal(m.Geometry8Circle2DOnlyWorkshop):
    """Final 2D-only classroom render entrypoint."""
    pass
