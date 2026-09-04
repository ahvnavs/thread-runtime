"""Package archive (.threadpkg) creation, validation, inspection, and extraction."""

from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from thread_runtime.errors import (
    PackageArchiveError,
    StoryLoadError,
    StoryValidationError,
)
from thread_runtime.model import (
    PACKAGE_FORMAT_VERSION,
    PackageManifest,
    StoryPackage,
)
from thread_runtime.package import (
    validate_story_package_detailed,
)


def compute_bytes_sha256(data: bytes) -> str:
    """Compute hex SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def pack_story_package(
    story_source_path: Union[str, Path],
    output_pkg_path: Union[str, Path],
    media_mp4_path: Optional[Union[str, Path]] = None,
    subtitle_path: Optional[Union[str, Path]] = None,
    scene_manifest_path: Optional[Union[str, Path]] = None,
) -> Path:
    """Validate a story file and bundle it into a self-contained .threadpkg zip archive with optional media assets."""
    src_path = Path(story_source_path)
    out_path = Path(output_pkg_path).resolve()

    if not src_path.is_file():
        raise StoryLoadError(f"Story source file not found: {src_path}")

    # Read formatted story JSON bytes
    try:
        with open(src_path, "rb") as f:
            story_bytes = f.read()
        story_data = json.loads(story_bytes.decode("utf-8"))
        story_pkg, _ = validate_story_package_detailed(story_data)
    except Exception as e:
        raise StoryValidationError(f"Cannot pack invalid story package '{src_path}': {e}")

    story_hash = compute_bytes_sha256(story_bytes)
    now_iso = datetime.now(timezone.utc).isoformat()

    manifest = PackageManifest(
        package_format_version=PACKAGE_FORMAT_VERSION,
        story_id=story_pkg.metadata.id,
        story_version=story_pkg.metadata.version,
        title=story_pkg.metadata.title,
        runtime_minimum=story_pkg.metadata.minimum_runtime or "0.1.0",
        story_hash=story_hash,
        author=story_pkg.metadata.author,
        description=story_pkg.metadata.description,
        created_at=now_iso,
    )

    manifest_bytes = json.dumps(asdict(manifest), indent=2, ensure_ascii=False).encode("utf-8")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", manifest_bytes)
            zf.writestr("story.json", story_bytes)

            # Embed MP4 media file if provided
            if media_mp4_path and Path(media_mp4_path).is_file():
                zf.write(Path(media_mp4_path), arcname="media/audiovisual.mp4")

            # Embed Subtitles if provided
            if subtitle_path and Path(subtitle_path).is_file():
                zf.write(Path(subtitle_path), arcname="subtitles/english.vtt")

            # Embed Scene Manifest if provided
            if scene_manifest_path and Path(scene_manifest_path).is_file():
                zf.write(Path(scene_manifest_path), arcname="manifests/scene_manifest.json")

    except Exception as e:
        if out_path.exists():
            out_path.unlink(missing_ok=True)
        raise PackageArchiveError(f"Failed to create story package archive '{out_path}': {e}")

    return out_path


def load_story_package_from_archive(
    pkg_path: Union[str, Path]
) -> Tuple[StoryPackage, PackageManifest]:
    """Validate archive integrity and return StoryPackage & PackageManifest."""
    path = Path(pkg_path)
    if not path.is_file():
        raise StoryLoadError(f"Package archive file not found: {path}")

    if not zipfile.is_zipfile(path):
        raise PackageArchiveError(f"File '{path}' is not a valid zip package archive.")

    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            if "manifest.json" not in names:
                raise PackageArchiveError("Package archive missing required 'manifest.json'.")
            if "story.json" not in names:
                raise PackageArchiveError("Package archive missing required 'story.json'.")

            manifest_bytes = zf.read("manifest.json")
            story_bytes = zf.read("story.json")
    except PackageArchiveError:
        raise
    except Exception as e:
        raise PackageArchiveError(f"Failed to read package archive '{path}': {e}")

    # Parse and validate Manifest
    try:
        manifest_data = json.loads(manifest_bytes.decode("utf-8"))
    except Exception as e:
        raise StoryValidationError(f"Malformed manifest JSON in package archive: {e}")

    pkg_fmt = manifest_data.get("package_format_version")
    if pkg_fmt != PACKAGE_FORMAT_VERSION:
        raise StoryValidationError(
            f"Unsupported package format version '{pkg_fmt}'. Expected '{PACKAGE_FORMAT_VERSION}'."
        )

    expected_hash = manifest_data.get("story_hash")
    if not expected_hash:
        raise StoryValidationError("Package manifest missing required 'story_hash' field.")

    # Integrity Check: Compare SHA-256 hash of story.json
    actual_hash = compute_bytes_sha256(story_bytes)
    if actual_hash != expected_hash:
        raise StoryValidationError(
            "Story content integrity check failed: SHA-256 hash mismatch."
        )

    # Parse embedded story.json
    try:
        story_data = json.loads(story_bytes.decode("utf-8"))
    except Exception as e:
        raise StoryValidationError(f"Malformed embedded story.json in package archive: {e}")

    story_pkg, _ = validate_story_package_detailed(story_data)

    # Verify identity consistency
    m_story_id = manifest_data.get("story_id")
    if m_story_id != story_pkg.metadata.id:
        raise StoryValidationError(
            f"Manifest story_id '{m_story_id}' does not match embedded story id '{story_pkg.metadata.id}'."
        )

    m_story_ver = manifest_data.get("story_version")
    if m_story_ver != story_pkg.metadata.version:
        raise StoryValidationError(
            f"Manifest story_version '{m_story_ver}' does not match embedded story version '{story_pkg.metadata.version}'."
        )

    manifest = PackageManifest(
        package_format_version=pkg_fmt,
        story_id=m_story_id,
        story_version=m_story_ver,
        title=manifest_data.get("title", story_pkg.metadata.title),
        runtime_minimum=manifest_data.get("runtime_minimum", "0.1.0"),
        story_hash=expected_hash,
        author=manifest_data.get("author"),
        description=manifest_data.get("description"),
        created_at=manifest_data.get("created_at"),
    )

    return story_pkg, manifest


def unpack_story_package(
    pkg_path: Union[str, Path], dest_dir: Union[str, Path]
) -> Path:
    """Safely extract story package files, preventing zip slip / path traversal vulnerabilities."""
    archive_path = Path(pkg_path)
    target_dir = Path(dest_dir).resolve()

    if not archive_path.is_file():
        raise PackageArchiveError(f"Package file not found: {archive_path}")

    if not zipfile.is_zipfile(archive_path):
        raise PackageArchiveError(f"File '{archive_path}' is not a valid zip package archive.")

    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.infolist():
            member_path = member.filename

            # Path Traversal Security Checks:
            # 1. Reject absolute paths or Windows drive letters
            if Path(member_path).is_absolute() or member_path.startswith(("/", "\\")):
                raise PackageArchiveError(
                    f"Security Error: Unsafe absolute path '{member_path}' in package archive."
                )

            # 2. Resolve destination path and ensure it remains strictly inside target_dir
            destination_file = (target_dir / member_path).resolve()
            try:
                destination_file.relative_to(target_dir)
            except ValueError:
                raise PackageArchiveError(
                    f"Security Error: Path traversal attempt detected for '{member_path}'."
                )

            if member.is_dir():
                destination_file.mkdir(parents=True, exist_ok=True)
            else:
                destination_file.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(destination_file, "wb") as target:
                    target.write(source.read())

    return target_dir


def inspect_story_package_contents(pkg_path: Union[str, Path]) -> Dict[str, Any]:
    """Inspect package archive metadata and file entries list."""
    archive_path = Path(pkg_path)
    story_pkg, manifest = load_story_package_from_archive(archive_path)

    with zipfile.ZipFile(archive_path, "r") as zf:
        entries = sorted(zf.namelist())

    return {
        "manifest": manifest,
        "story": story_pkg,
        "entries": entries,
    }
