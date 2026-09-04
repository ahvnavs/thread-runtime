"""Tests for Cinematic Scene Specification, Timeline Scheduler, and Validation."""

import unittest

from thread_runtime.cinematic import (
    AudioCue,
    Camera,
    CharacterAction,
    CinematicScene,
    CinematicTimeline,
    Shot,
    Transition,
    validate_cinematic_scene,
)
from thread_runtime.errors import CinematicValidationError


class TestCinematicSpecification(unittest.TestCase):
    def setUp(self):
        self.scene_data = {
            "id": "scene_threshold",
            "title": "The Threshold",
            "duration_ms": 22000,
            "shots": [
                {
                    "id": "shot_001",
                    "duration_ms": 8000,
                    "camera": {
                        "framing": "extreme_wide",
                        "movement": "static",
                        "subject": "landscape",
                    },
                    "cues": [
                        {
                            "cue_type": "ambience",
                            "asset_id": "wind_whistle",
                            "start_time_ms": 0,
                        }
                    ],
                },
                {
                    "id": "shot_002",
                    "duration_ms": 14000,
                    "camera": {
                        "framing": "close",
                        "movement": "push_in",
                        "subject": "eyes",
                    },
                    "actions": [
                        {
                            "character_id": "traveler",
                            "action": "look",
                            "start_time_ms": 0,
                        }
                    ],
                    "cues": [
                        {
                            "cue_type": "dialogue",
                            "asset_id": "line_gate_remembers",
                            "speaker_id": "traveler",
                            "text": "The gate remembers...",
                        }
                    ],
                    "transition": {
                        "type": "match_cut",
                        "target_scene": "future_threshold",
                        "target_shot": "future_eyes",
                    },
                },
            ],
        }

    def test_valid_cinematic_scene_parsing(self):
        scene = validate_cinematic_scene(self.scene_data)
        self.assertEqual(scene.id, "scene_threshold")
        self.assertEqual(scene.duration_ms, 22000)
        self.assertEqual(len(scene.shots), 2)
        self.assertEqual(scene.shots[0].camera.framing, "extreme_wide")
        self.assertEqual(scene.shots[1].transition.type, "match_cut")
        self.assertEqual(scene.shots[1].transition.target_scene, "future_threshold")

    def test_duplicate_shot_ids_rejected(self):
        data = dict(self.scene_data)
        data["shots"] = [
            self.scene_data["shots"][0],
            dict(self.scene_data["shots"][0]),  # Duplicate shot_001 ID
        ]
        with self.assertRaises(CinematicValidationError):
            validate_cinematic_scene(data)

    def test_invalid_duration_rejected(self):
        data = dict(self.scene_data)
        data["shots"] = [dict(self.scene_data["shots"][0])]
        data["shots"][0]["duration_ms"] = -500
        with self.assertRaises(CinematicValidationError):
            validate_cinematic_scene(data)

    def test_invalid_camera_framing_rejected(self):
        data = dict(self.scene_data)
        data["shots"] = [dict(self.scene_data["shots"][0])]
        data["shots"][0]["camera"] = {"framing": "invalid_framing"}
        with self.assertRaises(CinematicValidationError):
            validate_cinematic_scene(data)

    def test_cinematic_timeline_advancement_and_events(self):
        scene = validate_cinematic_scene(self.scene_data)
        timeline = CinematicTimeline(scene)

        # 1. Start timeline
        start_evts = timeline.start()
        self.assertTrue(timeline.is_started)
        self.assertEqual(timeline.current_shot.id, "shot_001")
        self.assertEqual(start_evts[0].event_type, "scene_started")
        self.assertEqual(start_evts[1].event_type, "shot_started")

        # 2. Advance 4000ms (within shot_001)
        adv1_evts = timeline.advance(4000)
        self.assertEqual(timeline.elapsed_scene_ms, 4000)
        self.assertEqual(timeline.elapsed_shot_ms, 4000)
        self.assertEqual(timeline.remaining_shot_ms, 4000)
        self.assertFalse(timeline.is_complete)

        # 3. Advance 5000ms (cross boundary from shot_001 [8000ms] into shot_002)
        adv2_evts = timeline.advance(5000)
        self.assertEqual(timeline.elapsed_scene_ms, 9000)
        self.assertEqual(timeline.current_shot.id, "shot_002")

        evt_types = [e.event_type for e in adv2_evts]
        self.assertIn("shot_completed", evt_types)
        self.assertIn("shot_started", evt_types)
        self.assertIn("action_started", evt_types)
        self.assertIn("dialogue_started", evt_types)

        # 4. Advance to end of scene (another 14000ms)
        adv3_evts = timeline.advance(14000)
        self.assertTrue(timeline.is_complete)

        end_types = [e.event_type for e in adv3_evts]
        self.assertIn("shot_completed", end_types)
        self.assertIn("transition_started", end_types)
        self.assertIn("scene_completed", end_types)

    def test_timeline_reset(self):
        scene = validate_cinematic_scene(self.scene_data)
        timeline = CinematicTimeline(scene)
        timeline.start()
        timeline.advance(22000)
        self.assertTrue(timeline.is_complete)

        timeline.reset()
        self.assertFalse(timeline.is_complete)
        self.assertFalse(timeline.is_started)
        self.assertEqual(timeline.elapsed_scene_ms, 0)


if __name__ == "__main__":
    unittest.main()
