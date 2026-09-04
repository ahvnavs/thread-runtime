"""Unit tests for THREAD Brick, ShotBrickSpec, and FilmSpec models."""

import unittest
from pathlib import Path
from thread_runtime.brick import Brick, ShotBrickSpec, FilmSpec


class TestBrickArchitecture(unittest.TestCase):

    def test_brick_creation_and_sorting(self):
        """Verify Brick creation and deterministic z-index sorting."""
        b1 = Brick(
            brick_id="bg",
            name="Background Dusk",
            semantic_category="environment",
            raster_path=Path("story/story_I/part_1/shots/shot_005/layers/background.png"),
            z_index=0,
        )
        b2 = Brick(
            brick_id="hand",
            name="Iphigenia Hand",
            semantic_category="character",
            raster_path=Path("story/story_I/part_1/shots/shot_005/layers/hand.png"),
            z_index=30,
            anchor_x=180,
            anchor_y=120,
            material="skin",
        )
        b3 = Brick(
            brick_id="altar",
            name="Granite Altar",
            semantic_category="prop",
            raster_path=Path("story/story_I/part_1/shots/shot_005/layers/altar.png"),
            z_index=10,
            material="granite",
        )

        shot_spec = ShotBrickSpec(
            shot_id="shot_005",
            duration_us=6_000_000,
            bricks=[b2, b1, b3],
        )

        sorted_bricks = shot_spec.get_sorted_bricks()
        self.assertEqual([b.brick_id for b in sorted_bricks], ["bg", "altar", "hand"])
        self.assertTrue(b1.is_valid())

    def test_film_spec_container(self):
        """Verify FilmSpec master container initialization."""
        film = FilmSpec(
            film_id="story_i_part_1",
            title="The Sacrifice of Iphigenia: Echoes at Aulis",
            duration_us=60_000_000,
            frame_rate=24,
            screenplay_source="story/story_I/part_1/screenplay/SCREENPLAY.md",
        )
        self.assertEqual(film.duration_us, 60_000_000)
        self.assertEqual(film.frame_rate, 24)


if __name__ == "__main__":
    unittest.main()
