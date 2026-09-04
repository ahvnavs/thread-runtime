"""THREAD Brick & Modular Cinematic Compositing Architecture.

Defines Bricks (authored visual primitives), Shot composition models, and Film orchestration structures.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class Brick:
    """A reusable authored visual primitive (Lego brick) in the THREAD engine."""

    brick_id: str
    name: str
    semantic_category: str  # character, environment, prop, mask, lighting, atmosphere
    raster_path: Path
    z_index: int = 0
    anchor_x: int = 0
    anchor_y: int = 0
    opacity: float = 1.0
    material: Optional[str] = None  # granite, linen, bronze, obsidian, cyan_conduit
    palette_map: Optional[Dict[int, Tuple[int, int, int, int]]] = None
    mask_path: Optional[Path] = None
    animation_poses: List[Path] = field(default_factory=list)

    def is_valid(self) -> bool:
        return self.raster_path.exists()


@dataclass
class ShotBrickSpec:
    """Assembles modular bricks, subpixel camera parameters, and bitwise effects for a single shot."""

    shot_id: str
    duration_us: int
    canvas: Tuple[int, int] = (426, 240)
    bricks: List[Brick] = field(default_factory=list)
    start_pan: Tuple[float, float] = (0.0, 0.0)
    end_pan: Tuple[float, float] = (0.0, 0.0)
    bitwise_effects: List[str] = field(default_factory=list)

    def get_sorted_bricks(self) -> List[Brick]:
        """Returns bricks sorted deterministically by z_index."""
        return sorted(self.bricks, key=lambda b: b.z_index)


@dataclass
class FilmSpec:
    """Master Film container orchestrating all shots across the canonical integer microsecond timeline."""

    film_id: str
    title: str
    duration_us: int
    frame_rate: int = 24
    shots: List[ShotBrickSpec] = field(default_factory=list)
    screenplay_source: Optional[str] = None
