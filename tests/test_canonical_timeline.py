"""Automated Unit Tests for Canonical Timeline, Cross-Modal Sync & Asset Provenance."""

import unittest
from pathlib import Path
from thread_runtime.canonical_timeline import (
    CanonicalTimeline,
    SubtitleCue,
    AudioEvent,
    frame_to_timestamp_us,
    timestamp_us_to_frame,
    FRAME_RATE,
    MICROSECONDS_PER_SECOND,
)
from thread_runtime.shot_manifest import ShotManifest
from thread_runtime.errors import MissingAssetError, ShotManifestError


class TestCanonicalTimeline(unittest.TestCase):

    def test_deterministic_frame_timestamp_mapping(self):
        """Verify deterministic floor mapping between 24 FPS frame_index and integer timestamp_us."""
        self.assertEqual(frame_to_timestamp_us(0), 0)
        self.assertEqual(frame_to_timestamp_us(24), 1_000_000)
        self.assertEqual(frame_to_timestamp_us(1440), 60_000_000)

        self.assertEqual(timestamp_us_to_frame(0), 0)
        self.assertEqual(timestamp_us_to_frame(1_000_000), 24)
        self.assertEqual(timestamp_us_to_frame(60_000_000), 1440)

    def test_match_cut_exact_boundary(self):
        """Verify Match Cut snaps cleanly at Frame 720 (30,000,000 us) with 0 drift."""
        frame_719_us = frame_to_timestamp_us(719)
        frame_720_us = frame_to_timestamp_us(720)

        self.assertEqual(timestamp_us_to_frame(frame_719_us), 719)
        self.assertEqual(timestamp_us_to_frame(frame_720_us), 720)
        self.assertEqual(frame_720_us, 30_000_000)

    def test_zero_timing_drift_across_60_seconds(self):
        """Verify zero microsecond timing drift across 1,440 frames (no float accumulation)."""
        expected_total_duration_us = 60_000_000
        calculated_us = frame_to_timestamp_us(1440)
        drift_us = abs(expected_total_duration_us - calculated_us)
        self.assertEqual(drift_us, 0)

    def test_subtitle_cue_boundary_and_validation(self):
        """Verify subtitle cue boundaries, zero overlap, and validity."""
        cue1 = SubtitleCue("cue1", start_us=1_000_000, end_us=5_000_000, text="Test Subtitle")
        self.assertEqual(cue1.start_frame, 24)
        self.assertEqual(cue1.end_frame, 120)
        self.assertTrue(cue1.is_active_at_frame(24))
        self.assertTrue(cue1.is_active_at_frame(119))
        self.assertFalse(cue1.is_active_at_frame(120))

        with self.assertRaises(ValueError):
            SubtitleCue("invalid", start_us=5_000_000, end_us=1_000_000, text="Invalid")

    def test_audio_event_boundary_and_validation(self):
        """Verify audio event boundaries and validity."""
        evt = AudioEvent("aud1", start_us=24_000_000, end_us=30_000_000, source="altar_hum.wav")
        self.assertEqual(evt.start_frame, 576)
        self.assertEqual(evt.end_frame, 720)

        with self.assertRaises(ValueError):
            AudioEvent("invalid", start_us=30_000_000, end_us=24_000_000, source="bad.wav")

    def test_canonical_timeline_cross_modal_synchronization(self):
        """Verify cross-modal synchronization for shots, subtitles, and audio events."""
        timeline = CanonicalTimeline(duration_us=60_000_000, frame_rate=FRAME_RATE)
        timeline.register_shot("shot_005", 24_000_000, 30_000_000)
        timeline.register_shot("shot_006", 30_000_000, 36_000_000)

        timeline.add_subtitle_cue(SubtitleCue("sub_005", 25_000_000, 29_500_000, "She reached out...", shot_id="shot_005"))
        timeline.add_audio_event(AudioEvent("aud_005", 25_000_000, 30_000_000, "altar_hum.wav", shot_id="shot_005"))

        # Frame 612 (Fingertip Touch)
        f612_state = timeline.get_frame_state(612)
        self.assertEqual(f612_state["shot_id"], "shot_005")
        self.assertIn("She reached out...", f612_state["subtitles"])
        self.assertIn("aud_005", f612_state["audio_events"])

        # Frame 720 (Match Cut)
        f720_state = timeline.get_frame_state(720)
        self.assertEqual(f720_state["shot_id"], "shot_006")
        self.assertEqual(len(f720_state["subtitles"]), 0)

    def test_shot_manifest_modular_layers_resolution(self):
        """Verify ShotManifest resolves modular layers/ subfolder paths correctly."""
        manifest_path = Path("story/story_I/part_1/shots/shot_005/manifest.json")
        manifest = ShotManifest(manifest_path)

        self.assertEqual(manifest.shot_id, "shot_005")
        self.assertEqual(len(manifest.layers), 8)
        self.assertTrue(manifest.layers[0].file_path.exists())
        self.assertTrue("layers" in str(manifest.layers[0].file_path))


if __name__ == "__main__":
    unittest.main()
