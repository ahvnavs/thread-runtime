"""Unit tests for THREAD Shot Manifest System & Authored Layer Pipeline."""

import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

from thread_runtime.shot_manifest import ShotManifest, ShotLayer
from thread_runtime.errors import MissingAssetError, ShotManifestError
from thread_runtime.renderer import CinematicRenderer


class TestShotManifestSystem(unittest.TestCase):
    """Tests for ShotManifest parsing, layer ordering, camera interpolation, multi-shot transitions, and missing asset handling."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.shot_dir = Path(self.temp_dir.name)

        # Create dummy 426x240 PNG layer files
        self.bg_path = self.shot_dir / "bg.png"
        self.fg_path = self.shot_dir / "fg.png"

        img = Image.new("RGBA", (426, 240), (10, 20, 30, 255))
        img.save(self.bg_path)
        img.save(self.fg_path)

        # Write valid manifest.json
        self.manifest_path = self.shot_dir / "manifest.json"
        manifest_content = """{
            "shot_id": "test_shot",
            "canvas": [426, 240],
            "duration_s": 8.0,
            "layers": [
                { "id": "fg_layer", "file": "fg.png", "z": 20, "parallax": 0.5 },
                { "id": "bg_layer", "file": "bg.png", "z": 0, "parallax": 0.0 }
            ],
            "camera": {
                "start": [0.0, 0.0],
                "end": [10.0, 5.0],
                "duration_s": 8.0
            }
        }"""
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest_content)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manifest_loads_and_parses_cleanly(self):
        """Verify that ShotManifest parses manifest.json correctly."""
        manifest = ShotManifest(self.manifest_path)
        self.assertEqual(manifest.shot_id, "test_shot")
        self.assertEqual(manifest.canvas, (426, 240))
        self.assertEqual(manifest.duration_s, 8.0)
        self.assertEqual(len(manifest.layers), 2)

    def test_layer_ordering_is_deterministic(self):
        """Verify that layers are sorted deterministically by z-index."""
        manifest = ShotManifest(self.manifest_path)
        self.assertEqual(manifest.layers[0].layer_id, "bg_layer")
        self.assertEqual(manifest.layers[0].z_index, 0)
        self.assertEqual(manifest.layers[1].layer_id, "fg_layer")
        self.assertEqual(manifest.layers[1].z_index, 20)

    def test_camera_interpolation_is_deterministic(self):
        """Verify that camera pan interpolation is exact and deterministic."""
        manifest = ShotManifest(self.manifest_path)
        start_cam = manifest.interpolate_camera(0.0)
        mid_cam = manifest.interpolate_camera(0.5)
        end_cam = manifest.interpolate_camera(1.0)

        self.assertEqual(start_cam, (0.0, 0.0))
        self.assertEqual(mid_cam, (5.0, 2.5))
        self.assertEqual(end_cam, (10.0, 5.0))

    def test_missing_layer_asset_fails_clearly(self):
        """Verify that missing a required layer PNG raises MissingAssetError."""
        self.fg_path.unlink()
        with self.assertRaises(MissingAssetError):
            ShotManifest(self.manifest_path)

    def test_missing_manifest_fails_clearly(self):
        """Verify that a missing manifest.json raises MissingAssetError."""
        missing_path = self.shot_dir / "non_existent_manifest.json"
        with self.assertRaises(MissingAssetError):
            ShotManifest(missing_path)

    def test_multi_shot_timeline_resolution(self):
        """Verify that CinematicRenderer resolves active shot_id chronologically."""
        renderer = CinematicRenderer()
        shot1_id, _ = renderer._resolve_active_shot_id(time_ms=1000)
        shot2_id, _ = renderer._resolve_active_shot_id(time_ms=15000)
        shot8_id, _ = renderer._resolve_active_shot_id(time_ms=75000)
        shot12_id, _ = renderer._resolve_active_shot_id(time_ms=115000)

        self.assertEqual(shot1_id, "shot_001")
        self.assertEqual(shot2_id, "shot_002")
        self.assertEqual(shot8_id, "shot_008")
        self.assertEqual(shot12_id, "shot_012")

    def test_shot_visual_state_transition(self):
        """Verify that visual frame outputs change when timeline transitions shots."""
        renderer = CinematicRenderer()
        frame1 = np.array(renderer.draw_cinematic_frame(time_ms=2000))
        frame8 = np.array(renderer.draw_cinematic_frame(time_ms=75000))

        # Check frame arrays are not identical
        self.assertFalse(np.array_equal(frame1, frame8))


if __name__ == "__main__":
    unittest.main()
