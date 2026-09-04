"""Deterministic story execution engine and narrative state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union

from thread_runtime.errors import StoryRuntimeError
from thread_runtime.model import (
    Choice,
    Condition,
    Effect,
    Scene,
    StoryPackage,
    StoryState,
)


def evaluate_condition(condition: Condition, state: StoryState) -> bool:
    """Evaluate a condition against current narrative state cleanly."""
    ctype = condition.type
    if ctype == "has_flag":
        return bool(state.flags.get(condition.name, False))
    elif ctype == "flag_equals":
        return state.flags.get(condition.name, False) == bool(condition.value)
    elif ctype == "has_item":
        return condition.item in state.inventory
    elif ctype == "variable_equals":
        return state.variables.get(condition.name) == condition.value
    elif ctype == "variable_greater_than":
        val = state.variables.get(condition.name, 0)
        if not isinstance(val, (int, float)) or not isinstance(condition.value, (int, float)):
            return False
        return val > condition.value
    elif ctype == "variable_less_than":
        val = state.variables.get(condition.name, 0)
        if not isinstance(val, (int, float)) or not isinstance(condition.value, (int, float)):
            return False
        return val < condition.value
    return True


def apply_effect(effect: Effect, state: StoryState) -> None:
    """Apply a narrative state modification effect cleanly."""
    etype = effect.type
    if etype == "set_flag":
        if effect.name:
            state.flags[effect.name] = bool(effect.value)
    elif etype == "set_variable":
        if effect.name and effect.value is not None:
            state.variables[effect.name] = effect.value
    elif etype == "add_variable":
        if effect.name:
            curr = state.variables.get(effect.name, 0)
            if isinstance(curr, (int, float)):
                amt = effect.amount if effect.amount is not None else (effect.value or 0)
                if isinstance(amt, (int, float)):
                    state.variables[effect.name] = curr + amt
    elif etype == "add_item":
        if effect.item and effect.item not in state.inventory:
            state.inventory.append(effect.item)
    elif etype == "remove_item":
        if effect.item and effect.item in state.inventory:
            state.inventory.remove(effect.item)


@dataclass
class StoryEngine:
    """Narrative runtime engine maintaining active scene, state history, and condition evaluation."""

    package: StoryPackage
    current_scene_id: str = ""
    completed: bool = False
    history: List[str] = field(default_factory=list)
    state: StoryState = field(default_factory=StoryState)

    def __post_init__(self) -> None:
        if not self.current_scene_id:
            self.current_scene_id = self.package.start_scene
        if not self.history:
            self.history = [self.current_scene_id]

        # Populate initial_state from package if current state is uninitialized
        if (
            self.package.initial_state
            and not self.state.flags
            and not self.state.variables
            and not self.state.inventory
        ):
            self.state = StoryState.from_dict(self.package.initial_state.to_dict())

        # Apply initial scene entry effects if applicable
        current = self.current_scene
        for effect in current.effects:
            apply_effect(effect, self.state)

        choices = self.get_choices()
        if current.is_ending or not choices:
            self.completed = True

    @property
    def current_scene(self) -> Scene:
        """Return the current active Scene object."""
        return self.package.scenes[self.current_scene_id]

    def get_choices(self) -> List[Choice]:
        """Return available choices for the current scene matching state conditions."""
        if self.completed:
            return []
        available: List[Choice] = []
        for choice in self.current_scene.choices:
            if choice.condition is None or evaluate_condition(choice.condition, self.state):
                available.append(choice)
        return available

    def choose(self, selector: Union[str, int]) -> Scene:
        """Select a choice, apply its effects, transition scene, apply entry effects."""
        if self.completed:
            raise StoryRuntimeError("Cannot make a choice in a completed story.")

        choices = self.get_choices()
        if not choices:
            raise StoryRuntimeError(
                f"Scene '{self.current_scene_id}' has no available choices matching narrative state."
            )

        selected_choice: Choice | None = None

        if isinstance(selector, int):
            if 1 <= selector <= len(choices):
                selected_choice = choices[selector - 1]
            else:
                raise StoryRuntimeError(
                    f"Invalid choice index '{selector}'. Expected index between 1 and {len(choices)}."
                )
        elif isinstance(selector, str):
            selector_clean = selector.strip()
            # 1. Match direct choice ID
            for c in choices:
                if c.id == selector_clean:
                    selected_choice = c
                    break
            # 2. Match numeric index string
            if selected_choice is None and selector_clean.isdigit():
                idx = int(selector_clean)
                if 1 <= idx <= len(choices):
                    selected_choice = choices[idx - 1]

            if selected_choice is None:
                valid_ids = [c.id for c in choices]
                raise StoryRuntimeError(
                    f"Invalid choice '{selector}'. Expected one of {valid_ids} or index 1..{len(choices)}."
                )
        else:
            raise StoryRuntimeError("Choice selector must be an integer index or choice ID string.")

        # 1. Apply choice effects
        for effect in selected_choice.effects:
            apply_effect(effect, self.state)

        # 2. Transition scene
        target_scene_id = selected_choice.target
        if target_scene_id not in self.package.scenes:
            raise StoryRuntimeError(f"Target scene '{target_scene_id}' does not exist.")

        self.current_scene_id = target_scene_id
        self.history.append(target_scene_id)

        next_scene = self.current_scene

        # 3. Apply scene-entry effects
        for effect in next_scene.effects:
            apply_effect(effect, self.state)

        # 4. Check completion
        next_choices = self.get_choices()
        if next_scene.is_ending or not next_choices:
            self.completed = True

        return next_scene

    def restart(self) -> None:
        """Reset the story engine state to the starting scene and initial state."""
        self.current_scene_id = self.package.start_scene
        self.history = [self.current_scene_id]
        if self.package.initial_state:
            self.state = StoryState.from_dict(self.package.initial_state.to_dict())
        else:
            self.state = StoryState()

        current = self.current_scene
        for effect in current.effects:
            apply_effect(effect, self.state)

        choices = self.get_choices()
        self.completed = current.is_ending or not choices
