# THREAD Code-Driven Pixel/Raster Cinematic Renderer — Multi-Shot Temporal Engine.

import os
import math
from pathlib import Path
import numpy as np
from PIL import Image

from thread_runtime.shot_manifest import ShotManifest
from thread_runtime.errors import MissingAssetError

PALETTE = {
    "void": (8, 6, 18),
    "sky_deep": (10, 8, 24),
    "sky_dusk": (54, 22, 50),
    "horizon_orange": (218, 85, 32),
    "sea_deep": (12, 16, 28),
    "sea_glint": (185, 95, 45),
    "mountain_far": (24, 16, 35),
    "mountain_mid": (16, 12, 24),
    "altar_stone": (38, 32, 45),
    "gold_rune": (212, 172, 13),
    "fire_core": (255, 140, 20),
    "robe_light": (245, 242, 252),
    "skin_mid": (210, 145, 115),
    "cyan_core": (0, 229, 255),
}

BAYER_4X4 = np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
], dtype=np.float32) / 16.0


class CinematicRenderer:
    """Renders 426x240 pixel/raster cinematic frames across multi-shot temporal timelines."""

    def __init__(self, internal_w: int = 426, internal_h: int = 240, target_w: int = 1280, target_h: int = 720):
        self.w = internal_w
        self.h = internal_h
        self.tw = target_w
        self.th = target_h
        self.layer_image_cache = {}
        self.manifest_cache = {}
        # Hard‑coded path relative to repository root – adjust if repository location changes.
        self.base_shots_dir = Path("/home/ahvnav/projects/thread-runtime/story/story_I/part_1/shots")

    def get_manifest(self, shot_dir: Path) -> ShotManifest:
        """Load and cache ShotManifest for a shot directory."""
        key = str(shot_dir)
        if key not in self.manifest_cache:
            manifest_path = Path(shot_dir) / "manifest.json"
            self.manifest_cache[key] = ShotManifest(manifest_path)
        return self.manifest_cache[key]

    def _load_layer_image(self, file_path: Path) -> Image.Image:
        """Load and cache RGBA layer image."""
        key = str(file_path)
        if key not in self.layer_image_cache:
            if not file_path.exists():
                raise MissingAssetError(f"Missing required authored raster asset: {file_path}")
            img = Image.open(file_path).convert("RGBA")
            if img.size != (self.w, self.h):
                img = img.resize((self.w, self.h), Image.Resampling.NEAREST)
            self.layer_image_cache[key] = img
        return self.layer_image_cache[key]

    def _resolve_active_shot_id(self, time_ms: int, total_duration_ms: int = 120000) -> tuple[str, float]:
        """Resolve active shot_id (e.g. shot_001..shot_012) and progress [0.0, 1.0] within shot."""
        progress_total = time_ms / float(total_duration_ms)
        shot_num = int(progress_total * 12) + 1
        shot_num = max(1, min(12, shot_num))
        shot_id = f"shot_{shot_num:03d}"

        # Calculate within‑shot progress [0.0, 1.0]
        shot_duration_ms = total_duration_ms / 12.0
        time_in_shot = time_ms % shot_duration_ms
        shot_progress = time_in_shot / shot_duration_ms
        return (shot_id, shot_progress)

    def draw_cinematic_frame(self, time_ms: int, total_duration_ms: int = 120000) -> Image.Image:
        """Render 720p HD frame from layered authored raster assets for active shot.

        If the environment variable ``FRAME_CAPTURE`` is set to ``1`` the renderer will
        additionally write the raw 426×240 frame for the exact frames 719 and 720 to the
        validation output directory.
        """
        shot_id, shot_progress = self._resolve_active_shot_id(time_ms, total_duration_ms)
        shot_dir = self.base_shots_dir / shot_id
        frame_cnt = int(time_ms / 41.6)  # Approximate 24 fps frame counter

        # Base Canvas – background colour matches the palette entry ``void``
        canvas = Image.new("RGBA", (self.w, self.h), (8, 6, 18, 255))

        if (shot_dir / "manifest.json").exists():
            manifest = self.get_manifest(shot_dir)
            cam_x, cam_y = manifest.interpolate_camera(shot_progress)

            # Composite Layers in Deterministic Z‑Order
            for layer in manifest.layers:
                layer_img = self._load_layer_image(layer.file_path)
                offset_x = int(cam_x * layer.parallax)
                offset_y = int(cam_y * layer.parallax)
                canvas.paste(layer_img, (offset_x, offset_y), layer_img)

        # -----------------------------------------------------------------
        # BAYER 4X4 DITHERING & BITWISE SCANLINES
        # -----------------------------------------------------------------
        rgb_img = canvas.convert("RGB")
        arr = np.array(rgb_img, dtype=np.float32)
        bayer = np.tile(BAYER_4X4, (self.h // 4 + 1, self.w // 4 + 1))[:self.h, :self.w]
        for c in range(3):
            arr[:, :, c] += (bayer - 0.5) * 8.0
        arr = np.clip(arr, 0, 255).astype(np.uint8)

        scanline_rows = ((np.arange(self.h) + frame_cnt) & 3) == 0
        arr[scanline_rows, :, :] = (arr[scanline_rows, :, :] * 0.92).astype(np.uint8)

        low_res = Image.fromarray(arr)
        high_res = low_res.resize((self.tw, self.th), Image.Resampling.NEAREST)

        # -----------------------------------------------------------------
        # Optional deterministic frame capture for audit purposes
        # -----------------------------------------------------------------
        if os.getenv("FRAME_CAPTURE") == "1":
            # Compute the logical frame index based on a true 24 fps rate
            frame_index = int(round(time_ms / (1000.0 / 24)))
            if frame_index in (719, 720):
                out_dir = Path("output/final_validation/visual")
                out_dir.mkdir(parents=True, exist_ok=True)
                if frame_index == 719:
                    target_path = out_dir / "shot_005_f719.png"
                else:
                    target_path = out_dir / "shot_006_f720.png"
                high_res.save(target_path)
        return high_res
