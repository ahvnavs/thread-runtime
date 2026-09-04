"""Tests for narrative state, condition evaluation, and effect application."""

import unittest

from thread_runtime.engine import apply_effect, evaluate_condition
from thread_runtime.model import Condition, Effect, StoryState


class TestNarrativeState(unittest.TestCase):
    def setUp(self):
        self.state = StoryState(
            flags={"met_guide": True, "opened_door": False},
            variables={"trust": 5, "gold": 10},
            inventory=["rusty_key"],
        )

    def test_condition_evaluation_has_flag(self):
        cond1 = Condition(type="has_flag", name="met_guide")
        cond2 = Condition(type="has_flag", name="nonexistent_flag")
        self.assertTrue(evaluate_condition(cond1, self.state))
        self.assertFalse(evaluate_condition(cond2, self.state))

    def test_condition_evaluation_flag_equals(self):
        cond1 = Condition(type="flag_equals", name="met_guide", value=True)
        cond2 = Condition(type="flag_equals", name="opened_door", value=True)
        self.assertTrue(evaluate_condition(cond1, self.state))
        self.assertFalse(evaluate_condition(cond2, self.state))

    def test_condition_evaluation_has_item(self):
        cond1 = Condition(type="has_item", item="rusty_key")
        cond2 = Condition(type="has_item", item="diamond")
        self.assertTrue(evaluate_condition(cond1, self.state))
        self.assertFalse(evaluate_condition(cond2, self.state))

    def test_condition_evaluation_variable_comparisons(self):
        cond_eq = Condition(type="variable_equals", name="trust", value=5)
        cond_gt = Condition(type="variable_greater_than", name="trust", value=3)
        cond_lt = Condition(type="variable_less_than", name="trust", value=10)
        cond_fail = Condition(type="variable_greater_than", name="trust", value=10)

        self.assertTrue(evaluate_condition(cond_eq, self.state))
        self.assertTrue(evaluate_condition(cond_gt, self.state))
        self.assertTrue(evaluate_condition(cond_lt, self.state))
        self.assertFalse(evaluate_condition(cond_fail, self.state))

    def test_effect_set_flag(self):
        eff = Effect(type="set_flag", name="opened_door", value=True)
        apply_effect(eff, self.state)
        self.assertTrue(self.state.flags["opened_door"])

    def test_effect_set_and_add_variable(self):
        eff_set = Effect(type="set_variable", name="trust", value=10)
        apply_effect(eff_set, self.state)
        self.assertEqual(self.state.variables["trust"], 10)

        eff_add = Effect(type="add_variable", name="trust", amount=2)
        apply_effect(eff_add, self.state)
        self.assertEqual(self.state.variables["trust"], 12)

    def test_effect_add_and_remove_item(self):
        eff_add = Effect(type="add_item", item="silver_coin")
        apply_effect(eff_add, self.state)
        self.assertIn("silver_coin", self.state.inventory)

        eff_remove = Effect(type="remove_item", item="rusty_key")
        apply_effect(eff_remove, self.state)
        self.assertNotIn("rusty_key", self.state.inventory)


if __name__ == "__main__":
    unittest.main()
