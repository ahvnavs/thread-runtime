"""THREAD Story Package & Timeline Loader."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class ShotDefinition:
    id: str
    duration_ms: int
    camera_framing: str
    subject: str
    transition_type: Optional[str] = None


@dataclass
class StoryDefinition:
    id: str
    title: str
    duration_ms: int
    shots: List[ShotDefinition] = field(default_factory=list)

    @classmethod
    def load_from_json(cls, filepath: Path) -> "StoryDefinition":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        shots = []
        for s in data.get("shots", []):
            shots.append(
                ShotDefinition(
                    id=s["id"],
                    duration_ms=s["duration_ms"],
                    camera_framing=s.get("camera", {}).get("framing", "medium"),
                    subject=s.get("camera", {}).get("subject", "main"),
                    transition_type=s.get("transition", {}).get("type"),
                )
            )

        return cls(
            id=data.get("id", "story_i_part_1"),
            title=data.get("title", "Story I — Part 1"),
            duration_ms=data.get("duration_ms", 120000),
            shots=shots,
        )
