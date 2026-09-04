"""Deterministic Audio Synthesizer, Mixer, and WAV Export Pipeline."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import List, Tuple, Union

from thread_runtime.cinematic import CinematicScene, CinematicTimeline


class AudioMixer:
    """Synthesizes and mixes audio cues for a CinematicScene into a stereo WAV file."""

    def __init__(self, scene: CinematicScene, sample_rate: int = 44100):
        self.scene = scene
        self.sample_rate = sample_rate
        self.total_samples = int((scene.duration_ms / 1000.0) * sample_rate)

    def generate_pcm_samples(self) -> Tuple[List[float], List[float]]:
        """Generate left and right channel normalized float samples (-1.0 to +1.0)."""
        left = [0.0] * self.total_samples
        right = [0.0] * self.total_samples

        timeline = CinematicTimeline(self.scene)
        timeline.start()

        # Step through scene shots and active audio cues
        current_ms = 0
        step_ms = 10
        step_samples = int((step_ms / 1000.0) * self.sample_rate)

        for shot in self.scene.shots:
            shot_start_ms = current_ms
            shot_duration_ms = shot.duration_ms

            for cue in shot.cues:
                cue_start_ms = shot_start_ms + cue.start_time_ms
                cue_duration_ms = cue.duration_ms or (shot_duration_ms - cue.start_time_ms)
                cue_start_sample = int((cue_start_ms / 1000.0) * self.sample_rate)
                cue_sample_count = int((cue_duration_ms / 1000.0) * self.sample_rate)
                end_sample = min(self.total_samples, cue_start_sample + cue_sample_count)

                vol = cue.volume

                if cue.cue_type == "ambience":
                    # Low wind whistle drone
                    for i in range(cue_start_sample, end_sample):
                        t = i / float(self.sample_rate)
                        val = 0.15 * math.sin(2 * math.pi * 120 * t) + 0.05 * math.sin(2 * math.pi * 180 * t)
                        left[i] += val * vol
                        right[i] += val * vol
                elif cue.cue_type == "sound_effect":
                    # Resonant metallic gate hum
                    for i in range(cue_start_sample, end_sample):
                        t = (i - cue_start_sample) / float(self.sample_rate)
                        envelope = math.exp(-t * 1.5)
                        val = 0.3 * math.sin(2 * math.pi * 110 * t) * envelope
                        left[i] += val * vol
                        right[i] += val * vol
                elif cue.cue_type == "dialogue":
                    # Synthesized voice formant pulse
                    for i in range(cue_start_sample, end_sample):
                        t = (i - cue_start_sample) / float(self.sample_rate)
                        val = 0.25 * math.sin(2 * math.pi * 220 * t) * math.sin(2 * math.pi * 5 * t)
                        left[i] += val * vol
                        right[i] += val * vol
                elif cue.cue_type == "music":
                    # Synth arpeggio theme
                    for i in range(cue_start_sample, end_sample):
                        t = i / float(self.sample_rate)
                        freq = 261.63 if (int(t * 4) % 3 == 0) else (311.13 if (int(t * 4) % 3 == 1) else 392.00)
                        val = 0.2 * math.sin(2 * math.pi * freq * t)
                        left[i] += val * vol
                        right[i] += val * vol

            current_ms += shot_duration_ms

        return left, right

    def render_to_wav(self, output_path: Union[str, Path]) -> Path:
        """Render stereo audio samples to a 16-bit PCM WAV file."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        left, right = self.generate_pcm_samples()

        with wave.open(str(out_file), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)

            frames = bytearray()
            for l_sample, r_sample in zip(left, right):
                # Clamp samples to [-1.0, 1.0]
                l_clamped = max(-1.0, min(1.0, l_sample))
                r_clamped = max(-1.0, min(1.0, r_sample))

                l_int = int(l_clamped * 32767)
                r_int = int(r_clamped * 32767)

                frames.extend(struct.pack("<hh", l_int, r_int))

            wf.writeframes(frames)

        return out_file
