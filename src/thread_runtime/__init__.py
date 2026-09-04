"""THREAD Runtime package initialization."""

from thread_runtime.archive import (
    inspect_story_package_contents,
    load_story_package_from_archive,
    pack_story_package,
    unpack_story_package,
)
from thread_runtime.audio import AudioMixer
from thread_runtime.capabilities import SystemCapabilities, detect_capabilities
from thread_runtime.cinematic import (
    AudioCue,
    Camera,
    CharacterAction,
    CinematicEvent,
    CinematicScene,
    CinematicTimeline,
    Shot,
    Transition,
    validate_cinematic_scene,
)
from thread_runtime.engine import StoryEngine, apply_effect, evaluate_condition
from thread_runtime.errors import (
    CinematicError,
    CinematicValidationError,
    PackageArchiveError,
    SaveError,
    SaveLoadError,
    SaveValidationError,
    StoryLoadError,
    StoryRuntimeError,
    StoryValidationError,
    ThreadError,
)
from thread_runtime.model import (
    PACKAGE_FORMAT_VERSION,
    SUPPORTED_CONDITION_TYPES,
    SUPPORTED_EFFECT_TYPES,
    Choice,
    Condition,
    Effect,
    Metadata,
    PackageManifest,
    Scene,
    StoryPackage,
    StoryState,
)
from thread_runtime.package import (
    load_story_package,
    validate_story_package,
    validate_story_package_detailed,
)
from thread_runtime.presenter import CinematicPresenter, render_audiovisual_mp4, render_html5_playback
from thread_runtime.provenance import AssetProvenance, validate_asset_provenance
from thread_runtime.release import execute_production_release
from thread_runtime.save import (
    SaveState,
    load_save_file,
    restore_engine_from_save,
    save_game,
)

__all__ = [
    "Choice",
    "Condition",
    "Effect",
    "Metadata",
    "Scene",
    "StoryPackage",
    "StoryState",
    "PackageManifest",
    "PACKAGE_FORMAT_VERSION",
    "SUPPORTED_CONDITION_TYPES",
    "SUPPORTED_EFFECT_TYPES",
    "Camera",
    "CharacterAction",
    "AudioCue",
    "Transition",
    "Shot",
    "CinematicScene",
    "CinematicEvent",
    "CinematicTimeline",
    "validate_cinematic_scene",
    "CinematicPresenter",
    "render_audiovisual_mp4",
    "render_html5_playback",
    "AudioMixer",
    "AssetProvenance",
    "validate_asset_provenance",
    "execute_production_release",
    "StoryEngine",
    "SystemCapabilities",
    "SaveState",
    "ThreadError",
    "StoryLoadError",
    "StoryValidationError",
    "StoryRuntimeError",
    "SaveError",
    "SaveLoadError",
    "SaveValidationError",
    "PackageArchiveError",
    "CinematicError",
    "CinematicValidationError",
    "load_story_package",
    "validate_story_package",
    "validate_story_package_detailed",
    "detect_capabilities",
    "save_game",
    "load_save_file",
    "restore_engine_from_save",
    "pack_story_package",
    "unpack_story_package",
    "inspect_story_package_contents",
    "load_story_package_from_archive",
    "evaluate_condition",
    "apply_effect",
]
