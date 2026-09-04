"""Story package data models and structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from thread_runtime.cinematic import CinematicScene

SUPPORTED_SCHEMA_VERSIONS = {"1.0"}
PACKAGE_FORMAT_VERSION = "1.0"

SUPPORTED_CONDITION_TYPES = {
    "has_flag",
    "flag_equals",
    "has_item",
    "variable_equals",
    "variable_greater_than",
    "variable_less_than",
}

SUPPORTED_EFFECT_TYPES = {
    "set_flag",
    "set_variable",
    "add_variable",
    "add_item",
    "remove_item",
}


@dataclass(frozen=True)
class Condition:
    """A requirement for choice availability based on narrative state."""

    type: str
    name: Optional[str] = None
    item: Optional[str] = None
    value: Optional[Union[bool, int, float, str]] = None


@dataclass(frozen=True)
class Effect:
    """A narrative state modification triggered by a choice or scene entry."""

    type: str
    name: Optional[str] = None
    item: Optional[str] = None
    value: Optional[Union[bool, int, float, str]] = None
    amount: Optional[Union[int, float]] = None


@dataclass(frozen=True)
class Choice:
    """A choice option leading to another scene."""

    id: str
    text: str
    target: str
    condition: Optional[Condition] = None
    effects: List[Effect] = field(default_factory=list)


@dataclass(frozen=True)
class Scene:
    """A narrative scene containing text, choices, entry effects, or an ending marker."""

    id: str
    title: str
    text: str
    choices: List[Choice] = field(default_factory=list)
    effects: List[Effect] = field(default_factory=list)
    is_ending: bool = False
    ending_type: Optional[str] = None


@dataclass(frozen=True)
class Metadata:
    """Metadata attributes for a story package."""

    id: str
    title: str
    version: str
    author: Optional[str] = None
    description: Optional[str] = None
    minimum_runtime: Optional[str] = None


@dataclass
class StoryState:
    """Dynamic narrative state container tracking flags, variables, and inventory."""

    flags: Dict[str, bool] = field(default_factory=dict)
    variables: Dict[str, Union[int, float, str]] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flags": dict(self.flags),
            "variables": dict(self.variables),
            "inventory": list(self.inventory),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StoryState:
        if not isinstance(data, dict):
            return cls()
        flags = dict(data.get("flags", {})) if isinstance(data.get("flags"), dict) else {}
        variables = dict(data.get("variables", {})) if isinstance(data.get("variables"), dict) else {}
        inventory = list(data.get("inventory", [])) if isinstance(data.get("inventory"), list) else []
        return cls(flags=flags, variables=variables, inventory=inventory)


@dataclass(frozen=True)
class StoryPackage:
    """Validated, self-contained story package."""

    schema_version: str
    metadata: Metadata
    start_scene: str
    scenes: Dict[str, Scene]
    initial_state: Optional[StoryState] = None
    cinematic_scenes: Dict[str, CinematicScene] = field(default_factory=dict)


@dataclass(frozen=True)
class PackageManifest:
    """Manifest describing a packaged .threadpkg story artifact."""

    package_format_version: str
    story_id: str
    story_version: str
    title: str
    runtime_minimum: str
    story_hash: str
    author: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
