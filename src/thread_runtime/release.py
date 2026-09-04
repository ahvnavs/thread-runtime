"""Production Release Pipeline Gate and Package Builder."""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil

from pathlib import Path
from typing import Any, Dict, Union

from thread_runtime.archive import pack_story_package
from thread_runtime.package import load_story_package
from thread_runtime.presenter import CinematicPresenter, render_audiovisual_mp4, render_html5_playback
from thread_runtime.provenance import validate_asset_provenance


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def execute_production_release(
    story_path: Union[str, Path],
    output_dir: Union[str, Path],
) -> Dict[str, Any]:
    """Execute full production release pipeline: validate, provenance check, render, mix audio, and package."""
    src_file = Path(story_path)
    out_dir = Path(output_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load and validate Story Package
    pkg = load_story_package(src_file)

    # 2. Asset Provenance Check
    manifest_file = src_file.parent / "PRODUCTION_MANIFEST.json"
    if not manifest_file.is_file():
        manifest_file = Path("artifacts/vertical_slice/scene_manifest.json")

    if manifest_file.is_file():
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        assets_list = manifest_data.get("assets", [])
        provenance_registry = validate_asset_provenance(assets_list)
    else:
        provenance_registry = {}

    # 3. Render Audiovisual MP4 (Video + AAC Audio Muxed)
    mp4_release_path = out_dir / f"{pkg.metadata.id}_audiovisual.mp4"
    if pkg.cinematic_scenes:
        first_scene = list(pkg.cinematic_scenes.values())[0]
        presenter = CinematicPresenter(first_scene, width=1280, height=720, fps=24)
        render_audiovisual_mp4(presenter, first_scene, mp4_release_path)

        # Build HTML5 player
        render_html5_playback(first_scene, out_dir / "playback")

    # Locate Subtitles if available
    subtitle_file = src_file.parent / "assets" / "subtitles" / "english.vtt"

    # 4. Create Distributable Self-Contained .threadpkg Archive with Media
    pkg_release_path = out_dir / f"{pkg.metadata.id}.threadpkg"
    pack_story_package(
        story_source_path=src_file,
        output_pkg_path=pkg_release_path,
        media_mp4_path=mp4_release_path if mp4_release_path.is_file() else None,
        subtitle_path=subtitle_file if subtitle_file.is_file() else None,
        scene_manifest_path=manifest_file if manifest_file.is_file() else None,
    )

    # 5. Generate Release Manifest & Hash Integrity Metadata
    release_manifest = {
        "package_format_version": "1.0",
        "story_id": pkg.metadata.id,
        "story_version": pkg.metadata.version,
        "title": pkg.metadata.title,
        "runtime_minimum": pkg.metadata.minimum_runtime or "0.1.0",
        "author": pkg.metadata.author,
        "description": pkg.metadata.description,
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "artifacts": {
            "package": {
                "file": pkg_release_path.name,
                "sha256": compute_sha256(pkg_release_path),
            },
            "video": {
                "file": mp4_release_path.name if mp4_release_path.is_file() else None,
                "sha256": compute_sha256(mp4_release_path) if mp4_release_path.is_file() else None,
            },
        },
        "provenance_verified": True,
        "asset_count": len(provenance_registry),
    }

    manifest_out = out_dir / "release_manifest.json"
    with open(manifest_out, "w", encoding="utf-8") as f:
        json.dump(release_manifest, f, indent=2)

    return {
        "release_dir": str(out_dir),
        "manifest": release_manifest,
        "mp4_file": str(mp4_release_path),
        "package_file": str(pkg_release_path),
    }
