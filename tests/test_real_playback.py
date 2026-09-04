"""Integration test for Pygame real-time presentation engine."""

import os
import unittest
from pathlib import Path
from thread_runtime.playback_engine import PygamePlaybackEngine


class TestRealPlaybackEngine(unittest.TestCase):
    """Test Pygame presentation engine initialization and rendering."""

    def test_pygame_presentation_engine_headless(self):
        story_file = Path("story/story_I/part_1/story.json")
        self.assertTrue(story_file.exists())

        # Initialize Pygame presentation engine in headless test mode
        playback = PygamePlaybackEngine(story_file, headless=True)
        self.assertIsNotNone(playback.screen)
        self.assertEqual(playback.screen.get_width(), 1280)
        self.assertEqual(playback.screen.get_height(), 720)

        # Draw frame at time 5000ms and verify surface buffer
        pil_img = playback.renderer.draw_cinematic_frame(5000, 120000)
        self.assertEqual(pil_img.size, (1280, 720))


if __name__ == "__main__":
    unittest.main()
