"""Tests for story package loading and validation."""

import json
import tempfile
import unittest
from pathlib import Path

from thread_runtime.errors import StoryLoadError, StoryValidationError
from thread_runtime.package import load_story_package, validate_story_package


class TestPackageValidation(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            "schema_version": "1.0",
            "metadata": {
                "id": "test-story",
                "title": "Test Story",
                "version": "1.0.0",
                "author": "Tester",
                "description": "A test story.",
            },
            "initial_state": {
                "flags": {"met_stranger": False},
                "variables": {"gold": 5},
                "inventory": [],
            },
            "start_scene": "scene_1",
            "scenes": {
                "scene_1": {
                    "id": "scene_1",
                    "title": "Scene One",
                    "text": "First scene narrative.",
                    "choices": [
                        {
                            "id": "c1",
                            "text": "Go to scene 2",
                            "target": "scene_2",
                            "condition": {"type": "has_flag", "name": "met_stranger"},
                            "effects": [{"type": "add_item", "item": "key"}],
                        },
                        {
                            "id": "c2",
                            "text": "Bypass to scene 2",
                            "target": "scene_2",
                        },
                    ],
                },
                "scene_2": {
                    "id": "scene_2",
                    "title": "Scene Two",
                    "text": "Ending scene narrative.",
                    "is_ending": True,
                    "ending_type": "Victory",
                },
            },
        }

    def test_valid_package_with_state_loads(self):
        package = validate_story_package(self.valid_data)
        self.assertEqual(package.metadata.id, "test-story")
        self.assertIsNotNone(package.initial_state)
        self.assertEqual(package.initial_state.variables["gold"], 5)

    def test_invalid_condition_type_rejected(self):
        data = dict(self.valid_data)
        data["scenes"]["scene_1"]["choices"][0]["condition"] = {"type": "invalid_condition_type"}
        with self.assertRaises(StoryValidationError):
            validate_story_package(data)

    def test_invalid_effect_type_rejected(self):
        data = dict(self.valid_data)
        data["scenes"]["scene_1"]["choices"][0]["effects"] = [{"type": "invalid_effect_type"}]
        with self.assertRaises(StoryValidationError):
            validate_story_package(data)


if __name__ == "__main__":
    unittest.main()
