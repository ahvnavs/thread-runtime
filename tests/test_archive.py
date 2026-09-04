"""Tests for .threadpkg package creation, validation, extraction, and security."""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from thread_runtime.archive import (
    inspect_story_package_contents,
    load_story_package_from_archive,
    pack_story_package,
    unpack_story_package,
)
from thread_runtime.errors import (
    PackageArchiveError,
    StoryValidationError,
)
from thread_runtime.package import load_story_package, validate_story_package


class TestPackageArchive(unittest.TestCase):
    def setUp(self):
        self.story_data = {
            "schema_version": "1.0",
            "metadata": {
                "id": "archive-test-story",
                "title": "Archive Test Story",
                "version": "1.0.0",
                "author": "Tester",
                "description": "Test story for archiving.",
            },
            "start_scene": "scene_start",
            "scenes": {
                "scene_start": {
                    "id": "scene_start",
                    "title": "Start",
                    "text": "Starting scene narrative.",
                    "choices": [
                        {"id": "c1", "text": "End story", "target": "scene_end"}
                    ],
                },
                "scene_end": {
                    "id": "scene_end",
                    "title": "End",
                    "text": "Ending scene narrative.",
                    "is_ending": True,
                    "ending_type": "Victory",
                },
            },
        }

    def test_pack_and_load_valid_archive(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as sf:
            sf.write(json.dumps(self.story_data))
            story_file = Path(sf.name)

        pkg_file = story_file.with_suffix(".threadpkg")

        try:
            # Pack
            packed_path = pack_story_package(story_file, pkg_file)
            self.assertTrue(packed_path.is_file())
            self.assertTrue(zipfile.is_zipfile(packed_path))

            # Load via package loader auto-detection
            pkg = load_story_package(packed_path)
            self.assertEqual(pkg.metadata.id, "archive-test-story")
            self.assertEqual(pkg.metadata.title, "Archive Test Story")
            self.assertEqual(len(pkg.scenes), 2)

            # Inspect
            details = inspect_story_package_contents(packed_path)
            self.assertEqual(details["manifest"].story_id, "archive-test-story")
            self.assertIn("manifest.json", details["entries"])
            self.assertIn("story.json", details["entries"])
        finally:
            story_file.unlink(missing_ok=True)
            pkg_file.unlink(missing_ok=True)

    def test_pack_invalid_story_rejected(self):
        invalid_data = dict(self.story_data)
        del invalid_data["metadata"]

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as sf:
            sf.write(json.dumps(invalid_data))
            story_file = Path(sf.name)

        pkg_file = story_file.with_suffix(".threadpkg")

        try:
            with self.assertRaises(StoryValidationError):
                pack_story_package(story_file, pkg_file)
        finally:
            story_file.unlink(missing_ok=True)
            pkg_file.unlink(missing_ok=True)

    def test_tampered_story_hash_integrity_check_failed(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as sf:
            sf.write(json.dumps(self.story_data))
            story_file = Path(sf.name)

        pkg_file = story_file.with_suffix(".threadpkg")

        try:
            pack_story_package(story_file, pkg_file)

            # Tamper story.json inside zip archive
            tampered_data = dict(self.story_data)
            tampered_data["scenes"]["scene_start"]["text"] = "TAMPERED NARRATIVE TEXT"
            tampered_bytes = json.dumps(tampered_data).encode("utf-8")

            # Re-write zip with tampered story.json but original manifest
            with zipfile.ZipFile(pkg_file, "r") as zf:
                manifest_bytes = zf.read("manifest.json")

            with zipfile.ZipFile(pkg_file, "w") as zf:
                zf.writestr("manifest.json", manifest_bytes)
                zf.writestr("story.json", tampered_bytes)

            with self.assertRaises(StoryValidationError) as cm:
                load_story_package_from_archive(pkg_file)
            self.assertIn("integrity check failed", str(cm.exception))
        finally:
            story_file.unlink(missing_ok=True)
            pkg_file.unlink(missing_ok=True)

    def test_unpack_valid_package(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as sf:
            sf.write(json.dumps(self.story_data))
            story_file = Path(sf.name)

        pkg_file = story_file.with_suffix(".threadpkg")
        dest_dir = Path(tempfile.mkdtemp())

        try:
            pack_story_package(story_file, pkg_file)
            extracted_path = unpack_story_package(pkg_file, dest_dir)

            self.assertTrue((extracted_path / "manifest.json").is_file())
            self.assertTrue((extracted_path / "story.json").is_file())

            # Validate unpacked story.json
            unpacked_pkg = load_story_package(extracted_path / "story.json")
            self.assertEqual(unpacked_pkg.metadata.id, "archive-test-story")
        finally:
            story_file.unlink(missing_ok=True)
            pkg_file.unlink(missing_ok=True)
            import shutil
            shutil.rmtree(dest_dir, ignore_errors=True)

    def test_unpack_path_traversal_attack_rejected(self):
        # Construct malicious zip with ../malicious.txt entry
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".threadpkg") as tf:
            pkg_file = Path(tf.name)

        dest_dir = Path(tempfile.mkdtemp())

        try:
            with zipfile.ZipFile(pkg_file, "w") as zf:
                zf.writestr("manifest.json", b"{}")
                zf.writestr("../malicious_escape.txt", b"malicious content")

            with self.assertRaises(PackageArchiveError) as cm:
                unpack_story_package(pkg_file, dest_dir)
            self.assertIn("Security Error", str(cm.exception))
        finally:
            pkg_file.unlink(missing_ok=True)
            import shutil
            shutil.rmtree(dest_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
