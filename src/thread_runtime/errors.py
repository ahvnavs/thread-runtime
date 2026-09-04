"""Domain-specific exceptions for THREAD Runtime."""


class ThreadError(Exception):
    """Base exception for all THREAD Runtime errors."""

    pass


class StoryLoadError(ThreadError):
    """Raised when a story package cannot be loaded or parsed."""

    pass


class StoryValidationError(ThreadError):
    """Raised when a story package fails validation rules."""

    pass


class StoryRuntimeError(ThreadError):
    """Raised during story runtime execution or state transitions."""

    pass


class SaveError(ThreadError):
    """Base exception for save/resume operations."""

    pass


class SaveLoadError(SaveError):
    """Raised when a save file cannot be read or parsed."""

    pass


class SaveValidationError(SaveError):
    """Raised when a save state is invalid or incompatible with the story package."""

    pass


class PackageArchiveError(ThreadError):
    """Raised when package packing, unpacking, or inspection fails."""

    pass


class CinematicError(ThreadError):
    """Base exception for cinematic timeline and scene operations."""

    pass


class CinematicValidationError(CinematicError):
    """Raised when a cinematic scene or shot fails validation rules."""

    pass


class MissingAssetError(CinematicError):
    """Raised when a required authored raster PNG layer or media asset is missing."""

    pass


class ShotManifestError(CinematicError):
    """Raised when a shot manifest JSON is invalid or corrupted."""

    pass
