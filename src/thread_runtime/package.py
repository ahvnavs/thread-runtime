"""Story package loader and strict validator."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Union

from thread_runtime.cinematic import CinematicScene, validate_cinematic_scene
from thread_runtime.errors import StoryLoadError, StoryValidationError
from thread_runtime.model import (
    SUPPORTED_CONDITION_TYPES,
    SUPPORTED_EFFECT_TYPES,
    SUPPORTED_SCHEMA_VERSIONS,
    Choice,
    Condition,
    Effect,
    Metadata,
    Scene,
    StoryPackage,
    StoryState,
)


def load_story_package(path: Union[str, Path]) -> StoryPackage:
    """Load a story package file or .threadpkg archive from disk and validate it."""
    file_path = Path(path)
    if not file_path.is_file():
        raise StoryLoadError(f"Story package file not found: {file_path}")

    if zipfile.is_zipfile(file_path):
        from thread_runtime.archive import load_story_package_from_archive

        story_pkg, _ = load_story_package_from_archive(file_path)
        return story_pkg

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StoryLoadError(f"Malformed story package JSON in '{file_path}': {e}")
    except Exception as e:
        raise StoryLoadError(f"Failed to read story package file '{file_path}': {e}")

    if not isinstance(data, dict):
        raise StoryValidationError("Story package root must be a JSON object.")

    return validate_story_package(data)


def validate_story_package(data: Dict[str, Any]) -> StoryPackage:
    """Validate raw dictionary data against the THREAD story package schema."""
    package, _ = validate_story_package_detailed(data)
    return package


def parse_condition(cond_raw: Dict[str, Any], context: str) -> Condition:
    """Parse and strictly validate a choice condition definition."""
    if not isinstance(cond_raw, dict):
        raise StoryValidationError(f"Condition in {context} must be an object.")

    ctype = cond_raw.get("type")
    if not ctype or not isinstance(ctype, str) or ctype not in SUPPORTED_CONDITION_TYPES:
        raise StoryValidationError(
            f"Unsupported condition type '{ctype}' in {context}. Supported: {sorted(SUPPORTED_CONDITION_TYPES)}"
        )

    name = cond_raw.get("name")
    item = cond_raw.get("item")
    value = cond_raw.get("value")

    if ctype in ("has_flag", "flag_equals", "variable_equals", "variable_greater_than", "variable_less_than"):
        if not name or not isinstance(name, str) or not name.strip():
            raise StoryValidationError(f"Condition '{ctype}' in {context} requires a non-empty 'name'.")

    if ctype == "has_item":
        if not item or not isinstance(item, str) or not item.strip():
            raise StoryValidationError(f"Condition 'has_item' in {context} requires a non-empty 'item'.")

    if ctype in ("variable_greater_than", "variable_less_than"):
        if value is None or not isinstance(value, (int, float)):
            raise StoryValidationError(f"Condition '{ctype}' in {context} requires a numeric 'value'.")

    return Condition(type=ctype, name=name, item=item, value=value)


def parse_effect(effect_raw: Dict[str, Any], context: str) -> Effect:
    """Parse and strictly validate an effect definition."""
    if not isinstance(effect_raw, dict):
        raise StoryValidationError(f"Effect in {context} must be an object.")

    etype = effect_raw.get("type")
    if not etype or not isinstance(etype, str) or etype not in SUPPORTED_EFFECT_TYPES:
        raise StoryValidationError(
            f"Unsupported effect type '{etype}' in {context}. Supported: {sorted(SUPPORTED_EFFECT_TYPES)}"
        )

    name = effect_raw.get("name")
    item = effect_raw.get("item")
    value = effect_raw.get("value")
    amount = effect_raw.get("amount")

    if etype in ("set_flag", "set_variable", "add_variable"):
        if not name or not isinstance(name, str) or not name.strip():
            raise StoryValidationError(f"Effect '{etype}' in {context} requires a non-empty 'name'.")

    if etype in ("add_item", "remove_item"):
        if not item or not isinstance(item, str) or not item.strip():
            raise StoryValidationError(f"Effect '{etype}' in {context} requires a non-empty 'item'.")

    if etype == "set_flag" and value is None:
        value = True

    return Effect(type=etype, name=name, item=item, value=value, amount=amount)


def validate_story_package_detailed(
    data: Dict[str, Any]
) -> Tuple[StoryPackage, List[str]]:
    """Validate package data and return validated StoryPackage along with diagnostic checks log."""
    if not isinstance(data, dict):
        raise StoryValidationError("Story package data must be a dictionary.")

    checks: List[str] = ["[✓] JSON Syntax"]

    # 1. Schema Version Validation
    schema_version = data.get("schema_version")
    if not schema_version or not isinstance(schema_version, str):
        raise StoryValidationError("Missing or invalid 'schema_version' field.")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise StoryValidationError(
            f"Unsupported schema version '{schema_version}'. Supported versions: {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    checks.append(f"[✓] Schema Version: {schema_version}")

    # 2. Metadata Validation
    metadata_raw = data.get("metadata")
    if not metadata_raw or not isinstance(metadata_raw, dict):
        raise StoryValidationError("Missing or invalid 'metadata' object.")

    meta_id = metadata_raw.get("id")
    if not meta_id or not isinstance(meta_id, str) or not meta_id.strip():
        raise StoryValidationError("Metadata requires a non-empty 'id' string.")

    meta_title = metadata_raw.get("title")
    if not meta_title or not isinstance(meta_title, str) or not meta_title.strip():
        raise StoryValidationError("Metadata requires a non-empty 'title' string.")

    meta_version = metadata_raw.get("version")
    if not meta_version or not isinstance(meta_version, str) or not meta_version.strip():
        raise StoryValidationError("Metadata requires a non-empty 'version' string.")

    metadata = Metadata(
        id=meta_id.strip(),
        title=meta_title.strip(),
        version=meta_version.strip(),
        author=metadata_raw.get("author"),
        description=metadata_raw.get("description"),
        minimum_runtime=metadata_raw.get("minimum_runtime"),
    )
    checks.append(
        f"[✓] Metadata: {metadata.title} (ID: {metadata.id}, v{metadata.version})"
    )

    # 3. Initial State Validation (Optional)
    initial_state: StoryState | None = None
    if "initial_state" in data:
        init_raw = data["initial_state"]
        if not isinstance(init_raw, dict):
            raise StoryValidationError("Field 'initial_state' must be an object.")
        initial_state = StoryState.from_dict(init_raw)
        checks.append("[✓] Initial State: Validated")

    # 4. Start Scene Validation
    start_scene = data.get("start_scene")
    if not start_scene or not isinstance(start_scene, str) or not start_scene.strip():
        raise StoryValidationError("Missing or invalid 'start_scene' field.")
    start_scene = start_scene.strip()
    checks.append(f"[✓] Start Scene: {start_scene}")

    # 5. Scenes Dictionary Validation
    scenes_raw = data.get("scenes")
    if not scenes_raw or not isinstance(scenes_raw, dict) or not scenes_raw:
        raise StoryValidationError("Story package must contain a non-empty 'scenes' dictionary.")

    if start_scene not in scenes_raw:
        raise StoryValidationError(f"Start scene '{start_scene}' is not defined in 'scenes'.")

    parsed_scenes: Dict[str, Scene] = {}
    total_choices = 0
    ending_count = 0

    for scene_key, scene_raw in scenes_raw.items():
        if not isinstance(scene_raw, dict):
            raise StoryValidationError(f"Scene '{scene_key}' must be a JSON object.")

        scene_id = scene_raw.get("id")
        if not scene_id or not isinstance(scene_id, str) or not scene_id.strip():
            raise StoryValidationError(f"Scene '{scene_key}' requires a non-empty 'id' string.")
        scene_id = scene_id.strip()

        if scene_id != scene_key:
            raise StoryValidationError(
                f"Scene key '{scene_key}' does not match declared scene id '{scene_id}'."
            )

        scene_title = scene_raw.get("title", scene_id)
        if not isinstance(scene_title, str):
            raise StoryValidationError(f"Scene '{scene_id}' title must be a string.")

        scene_text = scene_raw.get("text")
        if not scene_text or not isinstance(scene_text, str) or not scene_text.strip():
            raise StoryValidationError(f"Scene '{scene_id}' has empty or missing narrative text.")

        is_ending = bool(scene_raw.get("is_ending", False))
        ending_type = scene_raw.get("ending_type")
        if is_ending:
            ending_count += 1

        scene_effects_raw = scene_raw.get("effects", [])
        if not isinstance(scene_effects_raw, list):
            raise StoryValidationError(f"Scene '{scene_id}' effects must be a list.")
        parsed_scene_effects = [
            parse_effect(eff, f"scene '{scene_id}'") for eff in scene_effects_raw
        ]

        choices_raw = scene_raw.get("choices", [])
        if not isinstance(choices_raw, list):
            raise StoryValidationError(f"Scene '{scene_id}' choices field must be a list.")

        if not is_ending and len(choices_raw) == 0:
            raise StoryValidationError(
                f"Non-ending scene '{scene_id}' must have at least one choice."
            )

        parsed_choices: List[Choice] = []
        seen_choice_ids: Set[str] = set()

        for idx, choice_raw in enumerate(choices_raw):
            if not isinstance(choice_raw, dict):
                raise StoryValidationError(
                    f"Choice #{idx + 1} in scene '{scene_id}' must be an object."
                )

            c_id = choice_raw.get("id")
            if not c_id or not isinstance(c_id, str) or not c_id.strip():
                raise StoryValidationError(
                    f"Choice #{idx + 1} in scene '{scene_id}' requires a non-empty 'id'."
                )
            c_id = c_id.strip()

            if c_id in seen_choice_ids:
                raise StoryValidationError(
                    f"Duplicate choice ID '{c_id}' in scene '{scene_id}'."
                )
            seen_choice_ids.add(c_id)

            c_text = choice_raw.get("text")
            if not c_text or not isinstance(c_text, str) or not c_text.strip():
                raise StoryValidationError(
                    f"Choice '{c_id}' in scene '{scene_id}' requires non-empty 'text'."
                )

            c_target = choice_raw.get("target")
            if not c_target or not isinstance(c_target, str) or not c_target.strip():
                raise StoryValidationError(
                    f"Choice '{c_id}' in scene '{scene_id}' requires non-empty 'target'."
                )
            c_target = c_target.strip()

            parsed_cond: Condition | None = None
            if "condition" in choice_raw and choice_raw["condition"] is not None:
                parsed_cond = parse_condition(
                    choice_raw["condition"], f"choice '{c_id}' in scene '{scene_id}'"
                )

            c_effects_raw = choice_raw.get("effects", [])
            if not isinstance(c_effects_raw, list):
                raise StoryValidationError(
                    f"Effects in choice '{c_id}' of scene '{scene_id}' must be a list."
                )
            parsed_c_effects = [
                parse_effect(eff, f"choice '{c_id}' in scene '{scene_id}'")
                for eff in c_effects_raw
            ]

            parsed_choices.append(
                Choice(
                    id=c_id,
                    text=c_text.strip(),
                    target=c_target,
                    condition=parsed_cond,
                    effects=parsed_c_effects,
                )
            )
            total_choices += 1

        parsed_scenes[scene_id] = Scene(
            id=scene_id,
            title=scene_title.strip(),
            text=scene_text.strip(),
            choices=parsed_choices,
            effects=parsed_scene_effects,
            is_ending=is_ending,
            ending_type=ending_type,
        )

    checks.append(f"[✓] Scenes: {len(parsed_scenes)} scene(s) declared")
    checks.append(f"[✓] Choices: {total_choices} choice(s) validated")

    # 6. Referential Integrity
    for scene in parsed_scenes.values():
        for choice in scene.choices:
            if choice.target not in parsed_scenes:
                raise StoryValidationError(
                    f"Choice '{choice.id}' in scene '{scene.id}' references missing target scene '{choice.target}'."
                )
    checks.append("[✓] Referential Integrity: All choice targets exist")

    # 7. Reachability Validation
    reachable: Set[str] = set()
    queue = [start_scene]
    while queue:
        curr = queue.pop(0)
        if curr not in reachable:
            reachable.add(curr)
            for choice in parsed_scenes[curr].choices:
                if choice.target not in reachable:
                    queue.append(choice.target)

    unreachable = set(parsed_scenes.keys()) - reachable
    if unreachable:
        sorted_unreachable = sorted(unreachable)
        raise StoryValidationError(
            f"Unreachable scene(s) detected: {', '.join(sorted_unreachable)}."
        )
    checks.append("[✓] Reachability: All scenes reachable from start scene")
    checks.append(f"[✓] Endings: {ending_count} ending scene(s) defined")

    # 8. Cinematic Scenes Validation (Optional)
    parsed_cinematic_scenes: Dict[str, CinematicScene] = {}
    cinematic_raw = data.get("cinematic_scenes", {})
    if isinstance(cinematic_raw, dict) and cinematic_raw:
        for c_id, c_scene_raw in cinematic_raw.items():
            parsed_c = validate_cinematic_scene(c_scene_raw)
            if parsed_c.id != c_id:
                raise StoryValidationError(
                    f"Cinematic scene key '{c_id}' does not match declared id '{parsed_c.id}'."
                )
            parsed_cinematic_scenes[c_id] = parsed_c
        checks.append(f"[✓] Cinematic Scenes: {len(parsed_cinematic_scenes)} scene(s) validated")

    package = StoryPackage(
        schema_version=schema_version,
        metadata=metadata,
        start_scene=start_scene,
        scenes=parsed_scenes,
        initial_state=initial_state,
        cinematic_scenes=parsed_cinematic_scenes,
    )
    return package, checks
