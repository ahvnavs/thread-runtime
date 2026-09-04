"""Tests for the story execution engine and runtime state."""

import unittest

from thread_runtime.engine import StoryEngine
from thread_runtime.errors import StoryRuntimeError
from thread_runtime.package import validate_story_package


class TestStoryEngine(unittest.TestCase):
    def setUp(self):
        self.story_data = {
            "schema_version": "1.0",
            "metadata": {
                "id": "engine-test",
                "title": "Engine Test Story",
                "version": "1.0.0",
            },
            "initial_state": {
                "flags": {"has_map": False},
                "variables": {"reputation": 0},
                "inventory": [],
            },
            "start_scene": "start",
            "scenes": {
                "start": {
                    "id": "start",
                    "title": "Start Scene",
                    "text": "At the entrance.",
                    "choices": [
                        {
                            "id": "take_key",
                            "text": "Take Key",
                            "target": "hall",
                            "effects": [{"type": "add_item", "item": "key"}],
                        },
                        {
                            "id": "sneak_in",
                            "text": "Sneak in without key",
                            "target": "hall",
                        },
                    ],
                },
                "hall": {
                    "id": "hall",
                    "title": "The Grand Hall",
                    "text": "Inside the hall.",
                    "effects": [{"type": "add_variable", "name": "reputation", "amount": 1}],
                    "choices": [
                        {
                            "id": "unlock_door",
                            "text": "Unlock Vault Door",
                            "target": "vault",
                            "condition": {"type": "has_item", "item": "key"},
                        },
                        {
                            "id": "leave",
                            "text": "Leave Hall",
                            "target": "outside",
                        },
                    ],
                },
                "vault": {
                    "id": "vault",
                    "title": "The Vault",
                    "text": "Piles of treasure.",
                    "is_ending": True,
                    "ending_type": "Treasure Hunter",
                },
                "outside": {
                    "id": "outside",
                    "title": "Outside",
                    "text": "Back outside.",
                    "is_ending": True,
                    "ending_type": "Wanderer",
                },
            },
        }
        self.package = validate_story_package(self.story_data)

    def test_conditional_choices_hidden_until_condition_met(self):
        engine = StoryEngine(self.package)

        # 1. Sneak in without key
        engine.choose("sneak_in")
        self.assertEqual(engine.current_scene_id, "hall")
        self.assertNotIn("key", engine.state.inventory)
        self.assertEqual(engine.state.variables["reputation"], 1)

        # In hall, unlock_door requires key, so only "leave" choice should be available
        choices = engine.get_choices()
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].id, "leave")

    def test_taking_key_unlocks_conditional_choice(self):
        engine = StoryEngine(self.package)

        # 1. Take key
        engine.choose("take_key")
        self.assertEqual(engine.current_scene_id, "hall")
        self.assertIn("key", engine.state.inventory)

        # In hall, unlock_door should now be exposed
        choices = engine.get_choices()
        self.assertEqual(len(choices), 2)
        choice_ids = [c.id for c in choices]
        self.assertIn("unlock_door", choice_ids)
        self.assertIn("leave", choice_ids)

        # 2. Unlock vault door
        next_scene = engine.choose("unlock_door")
        self.assertEqual(next_scene.id, "vault")
        self.assertTrue(engine.completed)
        self.assertEqual(next_scene.ending_type, "Treasure Hunter")

    def test_restart_resets_engine_state_and_inventory(self):
        engine = StoryEngine(self.package)
        engine.choose("take_key")
        self.assertIn("key", engine.state.inventory)

        engine.restart()
        self.assertEqual(engine.current_scene_id, "start")
        self.assertNotIn("key", engine.state.inventory)
        self.assertFalse(engine.completed)


if __name__ == "__main__":
    unittest.main()
