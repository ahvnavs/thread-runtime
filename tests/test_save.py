"""Tests for atomic JSON save and resume state operations including narrative state."""

import json
import tempfile
import unittest
from pathlib import Path

from thread_runtime.engine import StoryEngine
from thread_runtime.errors import SaveLoadError, SaveValidationError
from thread_runtime.package import validate_story_package
from thread_runtime.save import (
    SAVE_SCHEMA_VERSION,
    load_save_file,
    restore_engine_from_save,
    save_game,
)


class TestSaveResume(unittest.TestCase):
    def setUp(self):
        self.story_data = {
            "schema_version": "1.0",
            "metadata": {
                "id": "save-test-story",
                "title": "Save Test Story",
                "version": "1.0.0",
            },
            "initial_state": {
                "flags": {"has_map": False},
                "variables": {"gold": 10},
                "inventory": [],
            },
            "start_scene": "scene_1",
            "scenes": {
                "scene_1": {
                    "id": "scene_1",
                    "title": "Scene 1",
                    "text": "First scene.",
                    "choices": [
                        {
                            "id": "c1",
                            "text": "Go to scene 2",
                            "target": "scene_2",
                            "effects": [
                                {"type": "add_item", "item": "key"},
                                {"type": "set_flag", "name": "found_key", "value": True},
                                {"type": "add_variable", "name": "gold", "amount": 5},
                            ],
                        }
                    ],
                },
                "scene_2": {
                    "id": "scene_2",
                    "title": "Scene 2",
                    "text": "Second scene.",
                    "is_ending": True,
                    "ending_type": "Victory",
                },
            },
        }
        self.package = validate_story_package(self.story_data)

    def test_save_and_restore_narrative_state(self):
        engine = StoryEngine(self.package)
        engine.choose("c1")
        self.assertTrue(engine.completed)
        self.assertEqual(engine.current_scene_id, "scene_2")
        self.assertIn("key", engine.state.inventory)
        self.assertTrue(engine.state.flags["found_key"])
        self.assertEqual(engine.state.variables["gold"], 15)

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tf:
            save_path = Path(tf.name)

        try:
            save_game(engine, save_path)
            raw_save = load_save_file(save_path)

            self.assertEqual(raw_save["state"]["inventory"], ["key"])
            self.assertTrue(raw_save["state"]["flags"]["found_key"])
            self.assertEqual(raw_save["state"]["variables"]["gold"], 15)

            restored_engine = restore_engine_from_save(raw_save, self.package)
            self.assertEqual(restored_engine.current_scene_id, "scene_2")
            self.assertEqual(restored_engine.state.inventory, ["key"])
            self.assertTrue(restored_engine.state.flags["found_key"])
            self.assertEqual(restored_engine.state.variables["gold"], 15)
        finally:
            save_path.unlink(missing_ok=True)

    def test_legacy_save_file_backward_compatibility(self):
        legacy_save_data = {
            "save_version": SAVE_SCHEMA_VERSION,
            "story_id": "save-test-story",
            "story_version": "1.0.0",
            "current_scene_id": "scene_1",
            "history": ["scene_1"],
            "completed": False,
            # 'state' field omitted intentionally
        }
        restored_engine = restore_engine_from_save(legacy_save_data, self.package)
        self.assertEqual(restored_engine.current_scene_id, "scene_1")
        self.assertIsInstance(restored_engine.state.flags, dict)
        self.assertIsInstance(restored_engine.state.inventory, list)


if __name__ == "__main__":
    unittest.main()
