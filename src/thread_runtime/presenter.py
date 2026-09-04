"""Cinematic Presenter, 2D Video Renderer, and Audiovisual Muxer for THREAD Runtime."""

from __future__ import annotations

import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Import imageio and its ffmpeg helper; these are required for video rendering.
import imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from thread_runtime.audio import AudioMixer
from thread_runtime.cinematic import CinematicScene, CinematicTimeline, Shot
from thread_runtime.errors import CinematicError


class CinematicPresenter:
    """Consumes a CinematicScene and renders 2D/2.5D composited frames and MP4 video output."""

    def __init__(
        self,
        scene: CinematicScene,
        width: int = 1280,
        height: int = 720,
        fps: int = 24,
        clean_cinematic: bool = True,
    ):
        self.scene = scene
        self.width = width
        self.height = height
        self.fps = fps
        self.clean_cinematic = clean_cinematic
        self.timeline = CinematicTimeline(scene)

    def draw_frame(self, elapsed_ms: int) -> Image.Image:
        """Render a single 1280x720 composited frame at the given timestamp."""
        img = Image.new("RGB", (self.width, self.height), color=(10, 14, 23))
        draw = ImageDraw.Draw(img)

        # Sync timeline to elapsed_ms
        self.timeline.reset()
        self.timeline.start()
        self.timeline.advance(elapsed_ms)

        shot = self.timeline.current_shot
        shot_id = shot.id if shot else "shot_001"
        framing = shot.camera.framing if shot else "wide"
        movement = shot.camera.movement if shot else "static"
        shot_elapsed_ms = self.timeline.elapsed_shot_ms
        shot_duration_ms = shot.duration_ms if shot else 5000
        progress = min(1.0, shot_elapsed_ms / float(max(1, shot_duration_ms)))

        is_future = shot_id in ("shot_006", "shot_007")

        # ---------------------------------------------------------
        # LAYER 1: SKY & ATMOSPHERIC BACKGROUND
        # ---------------------------------------------------------
        if not is_future:
            # Ancient Stagnant Aulis Sky (Twilight Violet to Burnt Orange)
            for y in range(self.height):
                factor = y / float(self.height)
                r = int(18 + (210 - 18) * (factor ** 1.3))
                g = int(14 + (85 - 14) * (factor ** 1.3))
                b = int(45 + (30 - 45) * (factor ** 1.3))
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))

            # Distant Mountain Ridges (Layered Atmospheric Depth)
            # Far ridge
            m_far = [(0, 480), (250, 360), (550, 440), (850, 320), (1280, 490), (1280, 720), (0, 720)]
            draw.polygon(m_far, fill=(28, 20, 38))
            # Near ridge
            m_near = [(0, 530), (320, 410), (640, 510), (960, 390), (1280, 560), (1280, 720), (0, 720)]
            draw.polygon(m_near, fill=(20, 15, 28))

            # Dead Glassy Sea Surface with Subtle Wave Reflections
            draw.rectangle([0, 520, self.width, 720], fill=(12, 16, 28))
            for wave_y in range(530, 720, 15):
                wave_alpha = int(60 * (wave_y - 520) / 200.0)
                draw.line([(0, wave_y), (self.width, wave_y)], fill=(180, 90, 40, wave_alpha))

            # Ships Silhouette Fleet at Anchor
            ship_shift = int(progress * 15 if movement == "tracking" else 0)
            for sx, sw in [(120 + ship_shift, 90), (340 + ship_shift, 140), (780 - ship_shift, 110), (1050 - ship_shift, 130)]:
                # Hull
                draw.polygon([(sx, 540), (sx + sw, 540), (sx + sw - 15, 565), (sx + 15, 565)], fill=(15, 12, 20))
                # Limp Mast & Sails
                draw.line([(sx + sw // 2, 430), (sx + sw // 2, 540)], fill=(25, 20, 30), width=3)
                draw.polygon([(sx + sw // 2 - 25, 445), (sx + sw // 2 + 25, 445), (sx + sw // 2 + 20, 520), (sx + sw // 2 - 20, 520)], fill=(35, 28, 40))
        else:
            # Far-Future Aulis-9 Core Sky / Deep Space Nebula Void
            for y in range(self.height):
                factor = y / float(self.height)
                r = int(5 + (30 - 5) * factor)
                g = int(8 + (15 - 8) * factor)
                b = int(25 + (60 - 25) * factor)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))

            # Cyber Mega-Structures & Quantum Reactor Monolith
            draw.rectangle([480, 60, 800, 720], fill=(4, 8, 18), outline=(0, 180, 220), width=2)
            # Glowing Quantum Core Pulse
            pulse_r = int(45 + 15 * math.sin(elapsed_ms / 200.0))
            draw.ellipse([640 - pulse_r, 260 - pulse_r, 640 + pulse_r, 260 + pulse_r], fill=(0, 229, 255, 180), outline=(255, 255, 255), width=2)
            draw.line([(640, 60), (640, 720)], fill=(0, 229, 255), width=2)

        # ---------------------------------------------------------
        # LAYER 2: CHARACTER PERFORMANCE & SUBJECT COMPOSITION
        # ---------------------------------------------------------
        if framing == "close" and shot_id in ("shot_004", "shot_005"):
            # Iphigenia / Altar Pillar Hand Touch Close Shot
            pillar_x = 520
            draw.rectangle([pillar_x, 140, pillar_x + 240, 720], fill=(45, 40, 55), outline=(90, 80, 110), width=3)
            # Carved Glowing Gold Rune
            rune_alpha = int(180 + 75 * math.sin(elapsed_ms / 250.0))
            draw.ellipse([pillar_x + 90, 320, pillar_x + 150, 380], outline=(230, 180, 50), width=4)
            # Graceful Reach Hand Silhouette
            hand_reach = int(min(1.0, progress * 1.5) * 80)
            draw.polygon([(280 + hand_reach, 400), (460 + hand_reach, 360), (510 + hand_reach, 350), (480 + hand_reach, 410)], fill=(220, 180, 140))
        elif framing == "close" and shot_id == "shot_006":
            # Commander Kaelen Quantum Monolith Cyber Hand Touch
            mono_x = 520
            draw.rectangle([mono_x, 140, mono_x + 240, 720], fill=(2, 10, 24), outline=(0, 229, 255), width=3)
            # Glowing Core Node Interface
            draw.ellipse([mono_x + 90, 320, mono_x + 150, 380], fill=(0, 229, 255), outline=(255, 255, 255), width=3)
            # Cybernetic Metallic Hand Reach
            hand_reach = int(min(1.0, progress * 1.5) * 80)
            draw.polygon([(280 + hand_reach, 400), (460 + hand_reach, 360), (510 + hand_reach, 350), (480 + hand_reach, 410)], fill=(40, 80, 110))
            draw.line([(320 + hand_reach, 390), (500 + hand_reach, 355)], fill=(0, 229, 255), width=3)
        elif framing == "close" and shot_id == "shot_007":
            # Close-up Commander Kaelen Glowing Cyan Iris & Cyber Seam
            draw.ellipse([440, 240, 840, 480], fill=(10, 20, 35), outline=(0, 180, 220), width=3)
            # Cyan Glowing Iris
            draw.ellipse([590, 310, 690, 410], fill=(0, 229, 255), outline=(255, 255, 255), width=4)
            draw.ellipse([625, 345, 655, 375], fill=(2, 6, 23))  # Pupil
            # Temple Seam Glow
            draw.line([(380, 340), (450, 340), (490, 370)], fill=(0, 229, 255), width=4)
        elif framing in ("wide", "medium") and not is_future:
            # Agamemnon / Iphigenia Staging
            cx = 640 + int((progress - 0.5) * 60 if movement == "tracking" else 0)
            cy = 460
            # Character Silhouette & Drapery
            draw.polygon([(cx - 45, cy + 160), (cx, cy), (cx + 45, cy + 160)], fill=(25, 35, 48))
            draw.ellipse([cx - 22, cy - 40, cx + 22, cy + 5], fill=(200, 160, 120))

        # ---------------------------------------------------------
        # LAYER 3: ATMOSPHERIC FOG & CINEMATIC VIGNETTE
        # ---------------------------------------------------------
        # Low Shoreline Fog / Mist
        for fy in range(500, 720, 10):
            mist_alpha = int(40 * (1.0 - abs(610 - fy) / 110.0))
            if mist_alpha > 0:
                draw.line([(0, fy), (self.width, fy)], fill=(160, 180, 200, mist_alpha))

        # Subtle Lens Vignette (Dark Corners)
        draw.rectangle([0, 0, self.width, 35], fill=(0, 0, 0, 120))
        draw.rectangle([0, self.height - 35, self.width, self.height], fill=(0, 0, 0, 120))

        # ---------------------------------------------------------
        # OPTIONAL OVERLAY: DEBUG HEADERS (ONLY IF NOT CLEAN_CINEMATIC)
        # ---------------------------------------------------------
        if not self.clean_cinematic:
            draw.rectangle([0, 0, self.width, 40], fill=(2, 6, 23))
            sec_text = f"{(elapsed_ms / 1000.0):05.2f}s / {(self.scene.duration_ms / 1000.0):02.0f}s"
            draw.text((20, 10), f"THREAD R&D  |  SCENE: {self.scene.title.upper()}  |  {sec_text}", fill=(148, 163, 184))

        return img

    def render_to_mp4(self, output_path: Union[str, Path]) -> Path:
        """Render the complete scene to a raw video MP4 file."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        total_frames = int((self.scene.duration_ms / 1000.0) * self.fps)
        step_ms = int(1000 / self.fps)

        writer = imageio.get_writer(str(out_file), fps=self.fps, codec="libx264", quality=8)

        for frame_idx in range(total_frames):
            elapsed_ms = frame_idx * step_ms
            img = self.draw_frame(elapsed_ms)
            writer.append_data(np.array(img))

        writer.close()
        return out_file


def render_audiovisual_mp4(
    presenter: CinematicPresenter,
    scene: CinematicScene,
    output_path: Union[str, Path],
) -> Path:
    """Render composited frames and synthesized audio, then mux into a self-contained audiovisual MP4."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        temp_video = tmp_path / "temp_video.mp4"
        temp_audio = tmp_path / "temp_audio.wav"

        # 1. Render raw video
        presenter.render_to_mp4(temp_video)

        # 2. Render synthesized stereo audio
        mixer = AudioMixer(scene)
        mixer.render_to_wav(temp_audio)

        # 3. Mux using embedded FFmpeg executable
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i", str(temp_video),
            "-i", str(temp_audio),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_file),
        ]
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return out_file


def render_html5_playback(scene: CinematicScene, output_dir: Union[str, Path]) -> Path:
    """Generate a standalone HTML5/Canvas interactive browser player."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html_file = out_dir / "index.html"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>THREAD Cinematic Player - {scene.title}</title>
  <style>
    body {{ background: #090d16; color: #e2e8f0; font-family: monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
    #stage {{ border: 2px solid #38bdf8; box-shadow: 0 0 30px rgba(56, 189, 248, 0.2); background: #000; border-radius: 6px; }}
    .controls {{ margin-top: 16px; display: flex; gap: 12px; align-items: center; }}
    button {{ background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; }}
    button:hover {{ background: #0369a1; }}
    input[type=range] {{ width: 400px; }}
  </style>
</head>
<body>
  <h2>THREAD CINEMATIC RUNTIME — HTML5 CANVAS PLAYER</h2>
  <canvas id="stage" width="1280" height="720"></canvas>
  <div class="controls">
    <button id="btn-play">PLAY / PAUSE</button>
    <input type="range" id="seeker" min="0" max="{scene.duration_ms}" value="0">
    <span id="timer">00.00s / {(scene.duration_ms / 1000.0):.2f}s</span>
  </div>
  <script>
    const sceneDuration = {scene.duration_ms};
    let elapsedMs = 0;
    let playing = false;
    let lastTime = 0;
    const canvas = document.getElementById('stage');
    const ctx = canvas.getContext('2d');

    function draw(ms) {{
      ctx.fillStyle = '#0a0e17';
      ctx.fillRect(0, 0, 1280, 720);

      const isFuture = ms >= 30000;
      if (!isFuture) {{
        let grad = ctx.createLinearGradient(0,0,0,720);
        grad.addColorStop(0, '#120e2d');
        grad.addColorStop(1, '#d2551e');
        ctx.fillStyle = grad;
        ctx.fillRect(0,0,1280,720);

        ctx.fillStyle = '#1c1426';
        ctx.beginPath();
        ctx.moveTo(0, 480);
        ctx.lineTo(300, 380);
        ctx.lineTo(600, 460);
        ctx.lineTo(900, 340);
        ctx.lineTo(1280, 500);
        ctx.lineTo(1280, 720);
        ctx.lineTo(0, 720);
        ctx.fill();

        ctx.fillStyle = '#0c101c';
        ctx.fillRect(0, 520, 1280, 200);
      }} else {{
        let grad = ctx.createLinearGradient(0,0,0,720);
        grad.addColorStop(0, '#050819');
        grad.addColorStop(1, '#1e0f3c');
        ctx.fillStyle = grad;
        ctx.fillRect(0,0,1280,720);

        ctx.fillStyle = '#040812';
        ctx.fillRect(480, 60, 320, 660);
        ctx.strokeStyle = '#00b4dc';
        ctx.strokeRect(480, 60, 320, 660);

        ctx.fillStyle = '#00e5ff';
        ctx.beginPath();
        ctx.arc(640, 260, 45, 0, Math.PI*2);
        ctx.fill();
      }}
    }}

    function loop(now) {{
      if (playing) {{
        if (!lastTime) lastTime = now;
        elapsedMs += (now - lastTime);
        lastTime = now;
        if (elapsedMs >= sceneDuration) {{
          elapsedMs = sceneDuration;
          playing = false;
        }}
        document.getElementById('seeker').value = elapsedMs;
        document.getElementById('timer').innerText = (elapsedMs/1000).toFixed(2) + 's / ' + (sceneDuration/1000).toFixed(2) + 's';
      }}
      draw(elapsedMs);
      requestAnimationFrame(loop);
    }}

    document.getElementById('btn-play').addEventListener('click', () => {{
      playing = !playing;
      lastTime = 0;
    }});

    document.getElementById('seeker').addEventListener('input', (e) => {{
      elapsedMs = parseInt(e.target.value);
      draw(elapsedMs);
    }});

    draw(0);
    requestAnimationFrame(loop);
  </script>
</body>
</html>
"""
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_file
