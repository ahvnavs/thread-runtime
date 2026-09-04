"""THREAD Code-Driven Cinematic Game Runtime Engine — Cycle 20."""

import math
import struct
import numpy as np
from PIL import Image, ImageDraw

# -----------------------------------------------------------------------------
# PALETTE DEFINITION & BITWISE PALETTE CYCLING
# -----------------------------------------------------------------------------
PALETTE_GAME = {
    "void": (8, 6, 18),
    "night": (16, 12, 32),
    "dusk": (52, 24, 46),
    "horizon": (218, 85, 32),
    "sea": (12, 16, 28),
    "sea_glint": (150, 60, 35),
    "mountain": (22, 16, 32),
    "altar": (35, 30, 42),
    "gold_rune": (212, 172, 13),
    "fire_core": (255, 140, 20),
    "robe_light": (250, 248, 255),
    "robe_shadow": (75, 65, 95),
    "skin_mid": (210, 145, 115),
    "skin_firelit": (255, 185, 125),
    "hair": (20, 14, 22),
    "future_void": (2, 6, 23),
    "future_structure": (8, 14, 30),
    "cyan_core": (0, 229, 255),
}

BAYER_4X4 = np.array([
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
], dtype=np.float32) / 16.0


class BitwiseProcEffects:
    """Bitwise procedural effects layer (dithering, xorshift32 PRNG, scanline modulation, water shimmer)."""

    @staticmethod
    def xorshift32(state: int) -> int:
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= (state >> 17) & 0xFFFFFFFF
        state ^= (state << 5) & 0xFFFFFFFF
        return state

    @staticmethod
    def apply_water_shimmer_and_scanline(arr: np.ndarray, elapsed_ms: int) -> np.ndarray:
        """Apply bitwise scanline modulation and water shimmer."""
        h, w, c = arr.shape
        frame_cnt = int(elapsed_ms / 41.6)

        # Scanline modulation: every 4th scanline at 90% brightness
        scanline_rows = ((np.arange(h) + frame_cnt) & 3) == 0
        arr[scanline_rows, :, :] = (arr[scanline_rows, :, :] * 0.90).astype(np.uint8)
        return arr


class CinematicGameCartridge:
    """Playable Cinematic Cartridge Runtime rendering 60.0s master film."""

    def __init__(self, internal_w: int = 426, internal_h: int = 240, target_w: int = 1280, target_h: int = 720):
        self.w = internal_w
        self.h = internal_h
        self.tw = target_w
        self.th = target_h
        self.effects = BitwiseProcEffects()

    def render_cartridge_frame(self, frame_idx: int, total_frames: int = 1440) -> Image.Image:
        """Render frame for 60.0s test film (1440 total frames @ 24fps)."""
        elapsed_ms = int((frame_idx / 24.0) * 1000)
        shot_idx = min(11, frame_idx // 120)  # 12 shots, 5s (120 frames) each

        img = Image.new("RGB", (self.w, self.h), PALETTE_GAME["void"])
        draw = ImageDraw.Draw(img)

        is_future = shot_idx in [8, 9, 10, 11] or (shot_idx == 7 and elapsed_ms > 37500)

        if not is_future:
            # 1. Sky Gradient & Dusk Horizon
            for y in range(int(self.h * 0.58)):
                f = y / (self.h * 0.58)
                r = int(10 + (218 - 10) * f)
                g = int(8 + (85 - 8) * f)
                b = int(22 + (32 - 22) * f)
                draw.line([(0, y), (self.w, y)], fill=(r, g, b))

            # 2. Mountain Silhouette
            draw.polygon([(0, 125), (130, 98), (290, 128), (self.w, 108), (self.w, self.h), (0, self.h)], fill=PALETTE_GAME["mountain"])

            # 3. Sea & Fleet Silhouettes
            draw.rectangle([0, int(self.h * 0.58), self.w, self.h], fill=PALETTE_GAME["sea"])

            for ship_x, scale in [(int(self.w * 0.72), 0.7), (int(self.w * 0.85), 0.5)]:
                sw = int(26 * scale)
                sh_y = int(self.h * 0.58) + 8
                draw.polygon([(ship_x, sh_y), (ship_x + sw, sh_y), (ship_x + sw - 4, sh_y + 7), (ship_x + 4, sh_y + 7)], fill=(8, 6, 14))
                draw.line([(ship_x + sw // 2, sh_y - int(18 * scale)), (ship_x + sw // 2, sh_y)], fill=(15, 12, 20), width=1)

            # 4. Altar & Fire Spill (Left Third)
            ax, ay = int(self.w * 0.28), int(self.h * 0.62)
            draw.rectangle([ax - 22, ay, ax + 22, self.h], fill=PALETTE_GAME["altar"], outline=(15, 12, 20), width=2)
            draw.polygon([(ax, ay + 10), (ax - 8, ay + 22), (ax + 8, ay + 22)], fill=PALETTE_GAME["gold_rune"])

            pulse = int(2 * math.sin(elapsed_ms / 150.0))
            draw.polygon([(ax - 12, ay - 4), (ax, ay - 20 - pulse), (ax + 12, ay - 4)], fill=PALETTE_GAME["fire_core"])

            # 5. Character rendering per shot
            if shot_idx in [2, 3, 6, 7]:  # Iphigenia
                cx = int(self.w * 0.68 - (frame_idx % 120 / 120.0) * (self.w * 0.24))
                cy = int(self.h * 0.42)
                draw.polygon([(cx - 18, cy + 20), (cx + 18, cy + 20), (cx + 30, cy + 90), (cx - 30, cy + 90)], fill=PALETTE_GAME["robe_light"])
                draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=PALETTE_GAME["skin_mid"])
                if shot_idx in [6, 7]:  # Hand rise
                    draw.line([(cx - 10, cy + 25), (cx - 30, cy + 8)], fill=PALETTE_GAME["skin_mid"], width=4)
            elif shot_idx in [0, 1, 4, 5]:  # Agamemnon / Establishing
                cx = int(self.w * 0.35)
                cy = int(self.h * 0.42)
                draw.polygon([(cx - 20, cy + 20), (cx + 20, cy + 20), (cx + 25, cy + 90), (cx - 25, cy + 90)], fill=PALETTE_GAME["sea"])
                draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=PALETTE_GAME["skin_mid"])
        else:
            # Future Aulis-9 Core Environment
            for y in range(self.h):
                f = y / float(self.h)
                r = int(2 + (8 - 2) * f)
                g = int(6 + (14 - 6) * f)
                b = int(23 + (30 - 23) * f)
                draw.line([(0, y), (self.w, y)], fill=(r, g, b))

            mx, mw = int(self.w * 0.4), int(self.w * 0.2)
            draw.rectangle([mx, 10, mx + mw, self.h], fill=PALETTE_GAME["future_structure"], outline=PALETTE_GAME["cyan_core"], width=1)
            pulse = int(12 + 6 * math.sin(elapsed_ms / 200.0))
            draw.ellipse([mx + mw // 2 - pulse, int(self.h * 0.35) - pulse, mx + mw // 2 + pulse, int(self.h * 0.35) + pulse], fill=PALETTE_GAME["cyan_core"])

            # Kaelen Figure
            cx, cy = int(self.w * 0.28), int(self.h * 0.42)
            draw.polygon([(cx - 18, cy + 20), (cx + 18, cy + 20), (cx + 25, cy + 90), (cx - 25, cy + 90)], fill=PALETTE_GAME["future_structure"])
            draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=PALETTE_GAME["skin_mid"])
            if shot_idx in [7, 11]:  # Hand rise match cut
                draw.line([(cx - 10, cy + 25), (cx - 30, cy + 8)], fill=PALETTE_GAME["cyan_core"], width=4)

        # 6. Bayer 4x4 Dithering & Bitwise Effects Pass
        arr = np.array(img, dtype=np.float32)
        bayer = np.tile(BAYER_4X4, (self.h // 4 + 1, self.w // 4 + 1))[:self.h, :self.w]
        for c in range(3):
            arr[:, :, c] += (bayer - 0.5) * 12.0
        arr = np.clip(arr, 0, 255).astype(np.uint8)

        # Apply scanlines
        arr = BitwiseProcEffects.apply_water_shimmer_and_scanline(arr, elapsed_ms)

        # 7. Upscale 3x to target 1280x720 via Nearest-Neighbor
        low_res = Image.fromarray(arr)
        high_res = low_res.resize((self.tw, self.th), Image.Resampling.NEAREST)
        return high_res
