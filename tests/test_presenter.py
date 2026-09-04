"""Tests for Cinematic Presenter and Video Renderer."""

import tempfile
import unittest
from pathlib import Path

from thread_runtime.cinematic import validate_cinematic_scene
from thread_runtime.presenter import CinematicPresenter, render_html5_playback


class TestPresenter(unittest.TestCase):
    def setUp(self):
        self.scene_data = {
            "id": "test_slice",
            "title": "Test Vertical Slice",
            "duration_ms": 4000,
            "shots": [
                {
                    "id": "shot_001",
                    "duration_ms": 2000,
                    "camera": {
                        "framing": "wide",
                        "movement": "static",
                        "subject": "ancient_pass",
                    },
                },
                {
                    "id": "shot_006",
                    "duration_ms": 2000,
                    "camera": {
                        "framing": "close",
                        "movement": "static",
                        "subject": "eyes_future",
                    },
                    "cues": [
                        {
                            "cue_type": "dialogue",
                            "asset_id": "line_so_do_i",
                            "speaker_id": "cyber_elias",
                            "text": "And so do I.",
                        }
                    ],
                },
            ],
        }

    def test_draw_frame_returns_valid_image(self):
        scene = validate_cinematic_scene(self.scene_data)
        presenter = CinematicPresenter(scene, width=640, height=360, fps=12)

        frame1 = presenter.draw_frame(500)
        self.assertEqual(frame1.size, (640, 360))

        frame2 = presenter.draw_frame(3000)
        self.assertEqual(frame2.size, (640, 360))

    def test_html5_playback_generation(self):
        scene = validate_cinematic_scene(self.scene_data)
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_file = render_html5_playback(scene, tmp_dir)
            self.assertTrue(html_file.is_file())
            content = html_file.read_text(encoding="utf-8")
            self.assertIn("THREAD CINEMATIC RUNTIME", content)
            self.assertIn("Test Vertical Slice", content)


if __name__ == "__main__":
    unittest.main()
