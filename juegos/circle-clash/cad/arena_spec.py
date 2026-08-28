"""Parametric CAD-style specification for Circle Clash Arena 3D.

This file is intentionally browser-independent.  It gives students a Python
representation of the same geometric arena rendered by Three.js so the project
can be reused in the 3D Design + Programming track.

The script uses only the Python standard library and exports JSON that can be
consumed by a renderer, a CAD script, or a later mesh-generation pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class ArenaSpec:
    world_size: float = 64.0
    playable_radius: float = 34.8
    inner_ring_radius: float = 10.5
    middle_ring_radius: float = 20.5
    outer_ring_radius: float = 30.5
    core_base_radius: float = 4.1
    core_ring_radius: float = 4.6
    tower_offset: float = 27.0
    player_radius: float = 0.92
    player_height: float = 3.25

    @property
    def playable_diameter(self) -> float:
        return 2.0 * self.playable_radius

    @property
    def playable_circumference(self) -> float:
        return 2.0 * math.pi * self.playable_radius

    @property
    def playable_area(self) -> float:
        return math.pi * self.playable_radius**2

    def to_payload(self) -> dict[str, float | dict[str, float]]:
        payload = asdict(self)
        payload["derived"] = {
            "playable_diameter": self.playable_diameter,
            "playable_circumference": self.playable_circumference,
            "playable_area": self.playable_area,
        }
        return payload


def normalized_percent_to_world(percent: float, world_size: float = 64.0) -> float:
    """Convert the authoritative 0-100 multiplayer coordinate to CAD/world units."""
    half_world = world_size / 2.0
    return ((percent - 50.0) / 50.0) * half_world


def export_json(path: str | Path = "arena-spec.json") -> Path:
    target = Path(path)
    target.write_text(json.dumps(ArenaSpec().to_payload(), indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    spec = ArenaSpec()
    print(json.dumps(spec.to_payload(), indent=2))
