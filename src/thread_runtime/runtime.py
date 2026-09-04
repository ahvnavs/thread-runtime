"""THREAD Real-Time Execution Runtime."""

import sys
import os
from pathlib import Path
from typing import Optional

from thread_runtime.story import StoryDefinition
from thread_runtime.playback_engine import PygamePlaybackEngine


class ThreadRuntimeEngine:
    """Linux real-time runtime executing story cutscenes."""

    def __init__(self, story_file: Path, headless: Optional[bool] = None):
        self.story_file = Path(story_file)
        if not self.story_file.exists():
            raise FileNotFoundError(f"Story file not found: {self.story_file}")

        self.story = StoryDefinition.load_from_json(self.story_file)
        if headless is None:
            self.headless = os.environ.get("HEADLESS", "0") == "1"
        else:
            self.headless = headless

        self.max_frames = int(os.environ["MAX_FRAMES"]) if "MAX_FRAMES" in os.environ else None

    def play(self) -> bool:
        """Execute real-time presentation loop."""
        playback = PygamePlaybackEngine(self.story_file, headless=self.headless)
        return playback.play(max_frames=self.max_frames)
