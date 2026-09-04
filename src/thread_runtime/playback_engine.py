"""THREAD Real-Time Pygame Presentation Engine — Build Cycle 22."""

import os
import sys
import time
import math
import numpy as np
from pathlib import Path
from PIL import Image

# Import pygame for real-time Linux window presentation
import pygame

from thread_runtime.story import StoryDefinition
from thread_runtime.renderer import CinematicRenderer, PALETTE


class PygamePlaybackEngine:
    """Real-Time Pygame/SDL Presentation Engine for Linux desktop."""

    def __init__(self, story_path: Path, internal_w: int = 426, internal_h: int = 240, target_w: int = 1280, target_h: int = 720, headless: bool = False):
        self.story_path = Path(story_path)
        if not self.story_path.exists():
            raise FileNotFoundError(f"Story file not found: {self.story_path}")

        self.story = StoryDefinition.load_from_json(self.story_path)
        self.internal_w = internal_w
        self.internal_h = internal_h
        self.target_w = target_w
        self.target_h = target_h
        self.headless = headless

        if self.headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"

        pygame.init()
        pygame.font.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.screen = pygame.display.set_mode((self.target_w, self.target_h))
        pygame.display.set_caption(f"THREAD — {self.story.title}")
        self.clock = pygame.time.Clock()
        self.renderer = CinematicRenderer(internal_w, internal_h, target_w, target_h)
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

        # Load Audio if available
        self.audio_path = self.story_path.parent / "audio/ambience.wav"
        if self.audio_path.exists() and pygame.mixer.get_init():
            try:
                pygame.mixer.music.load(str(self.audio_path))
                pygame.mixer.music.play(-1)
            except Exception:
                pass

        # Parse Subtitles
        self.subtitles = []
        sub_path = self.story_path.parent / "subtitles/english.vtt"
        if sub_path.exists():
            self._load_subtitles(sub_path)

    def _load_subtitles(self, filepath: Path):
        """Parse WebVTT subtitle cues."""
        lines = filepath.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if "-->" in line:
                parts = line.split("-->")
                start_ms = self._time_to_ms(parts[0].strip())
                end_ms = self._time_to_ms(parts[1].strip())
                text = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if text:
                    self.subtitles.append((start_ms, end_ms, text))

    @staticmethod
    def _time_to_ms(t_str: str) -> int:
        pts = t_str.split(":")
        mins = int(pts[0])
        secs_pts = pts[1].split(".")
        secs = int(secs_pts[0])
        ms = int(secs_pts[1])
        return (mins * 60 + secs) * 1000 + ms

    def play(self, max_frames: Optional[int] = None) -> bool:
        """Run real-time presentation playback loop until story timeline completes."""
        print(f"=== LAUNCHING REAL-TIME PLAYBACK: {self.story.title} ===")
        print(f"    Window Resolution: {self.target_w}x{self.target_h} (Canvas: {self.internal_w}x{self.internal_h})")
        print(f"    Duration: {self.story.duration_ms / 1000.0:.1f}s | Headless Mode: {self.headless}")

        start_time = time.monotonic()
        paused = False
        pause_start = 0.0
        total_paused_ms = 0.0

        running = True
        fps_samples = []
        rendered_frames = 0

        while running:
            # Process User Input Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        if paused:
                            pause_start = time.monotonic()
                        else:
                            total_paused_ms += (time.monotonic() - pause_start) * 1000.0
                    elif event.key == pygame.K_r:
                        start_time = time.monotonic()
                        total_paused_ms = 0.0

            if paused:
                time.sleep(0.05)
                continue

            # Monotonic real time position (or accelerated step in headless test if max_frames set)
            if self.headless and max_frames is not None:
                elapsed_ms = int((rendered_frames / 24.0) * 1000.0)
            else:
                now = time.monotonic()
                elapsed_ms = int((now - start_time) * 1000.0 - total_paused_ms)

            if elapsed_ms >= self.story.duration_ms:
                print(f"[✓] Real-time story timeline completed ({elapsed_ms/1000.0:.1f}s). Exiting cleanly.")
                running = False
                break

            # Render Frame to PIL Image & Convert to Pygame Surface
            pil_img = self.renderer.draw_cinematic_frame(elapsed_ms, self.story.duration_ms)
            mode = pil_img.mode
            size = pil_img.size
            data = pil_img.tobytes()

            pygame_surf = pygame.image.fromstring(data, size, mode)
            self.screen.blit(pygame_surf, (0, 0))

            # Render Subtitles
            active_sub = ""
            for s_start, s_end, text in self.subtitles:
                if s_start <= elapsed_ms <= s_end:
                    active_sub = text
                    break

            if active_sub:
                sub_surf = self.font.render(active_sub, True, (255, 255, 255), (10, 8, 22))
                sub_rect = sub_surf.get_rect(center=(self.target_w // 2, self.target_h - 45))
                self.screen.blit(sub_surf, sub_rect)

            pygame.display.flip()

            rendered_frames += 1
            if max_frames is not None and rendered_frames >= max_frames:
                print(f"[✓] Max frames ({max_frames}) rendered in test mode. Exiting cleanly.")
                running = False
                break

            if not self.headless:
                self.clock.tick(24)
                current_fps = self.clock.get_fps()
                if current_fps > 0:
                    fps_samples.append(current_fps)

        pygame.quit()
        avg_fps = np.mean(fps_samples) if fps_samples else 24.0
        print(f"=== REAL-TIME PRESENTATION FINISHED | Avg FPS: {avg_fps:.1f} ===")
        return True
