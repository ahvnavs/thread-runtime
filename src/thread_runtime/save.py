"""Atomic JSON save state management and validation."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Union

from thread_runtime.engine import StoryEngine
from thread_runtime.errors import SaveLoadError, SaveValidationError
from thread_runtime.model import StoryPackage, StoryState

SAVE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class SaveState:
    """Serializable save state representation."""

    save_version: str
    story_id: str
    story_version: str
    current_scene_id: str
    history: List[str]
    completed: bool
    saved_at: str
    state: Dict[str, Any]


def create_save_state(engine: StoryEngine) -> SaveState:
    """Generate a SaveState object from an active StoryEngine instance."""
    now_iso = datetime.now(timezone.utc).isoformat()
    return SaveState(
        save_version=SAVE_SCHEMA_VERSION,
        story_id=engine.package.metadata.id,
        story_version=engine.package.metadata.version,
        current_scene_id=engine.current_scene_id,
        history=list(engine.history),
        completed=engine.completed,
        saved_at=now_iso,
        state=engine.state.to_dict(),
    )


def save_game(engine: StoryEngine, path: Union[str, Path]) -> SaveState:
    """Atomic write of engine save state to disk using a temporary file."""
    target_path = Path(path).resolve()
    save_state = create_save_state(engine)
    data = asdict(save_state)

    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=target_dir, delete=False, encoding="utf-8"
        ) as tf:
            temp_path = Path(tf.name)
            json.dump(data, tf, indent=2, ensure_ascii=False)
            tf.flush()
            os.fsync(tf.fileno())

        temp_path.replace(target_path)
    except Exception as e:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise SaveLoadError(f"Failed to write save file '{target_path}': {e}")

    return save_state


def load_save_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Read raw save JSON data from file."""
    file_path = Path(path)
    if not file_path.is_file():
        raise SaveLoadError(f"Save file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise SaveLoadError(f"Malformed save file JSON in '{file_path}': {e}")
    except Exception as e:
        raise SaveLoadError(f"Failed to read save file '{file_path}': {e}")

    if not isinstance(data, dict):
        raise SaveValidationError("Save file root must be a JSON object.")

    return data


def restore_engine_from_save(data: Dict[str, Any], package: StoryPackage) -> StoryEngine:
    """Validate save data against package identity and restore StoryEngine state."""
    if not isinstance(data, dict):
        raise SaveValidationError("Save state data must be a dictionary.")

    save_version = data.get("save_version")
    if not save_version or save_version != SAVE_SCHEMA_VERSION:
        raise SaveValidationError(
            f"Unsupported save schema version '{save_version}'. Expected '{SAVE_SCHEMA_VERSION}'."
        )

    story_id = data.get("story_id")
    if story_id != package.metadata.id:
        raise SaveValidationError(
            f"Save file story ID '{story_id}' does not match package ID '{package.metadata.id}'."
        )

    story_version = data.get("story_version")
    if story_version != package.metadata.version:
        raise SaveValidationError(
            f"Save file story version '{story_version}' does not match package version '{package.metadata.version}'."
        )

    current_scene_id = data.get("current_scene_id")
    if not current_scene_id or current_scene_id not in package.scenes:
        raise SaveValidationError(
            f"Saved scene '{current_scene_id}' does not exist in story package."
        )

    history = data.get("history")
    if not isinstance(history, list) or not history:
        history = [current_scene_id]

    completed = bool(data.get("completed", False))

    # Narrative State Restoration with backward compatibility
    state_raw = data.get("state")
    if isinstance(state_raw, dict):
        story_state = StoryState.from_dict(state_raw)
    else:
        # Fallback for legacy save files
        story_state = StoryState()

    return StoryEngine(
        package=package,
        current_scene_id=current_scene_id,
        completed=completed,
        history=history,
        state=story_state,
    )
