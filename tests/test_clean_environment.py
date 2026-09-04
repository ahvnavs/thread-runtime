"""Clean-environment customer package isolation tests."""

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from thread_runtime.archive import (
    load_story_package_from_archive,
    unpack_story_package,
)
from thread_runtime.errors import PackageArchiveError
from thread_runtime.release import execute_production_release


class TestCleanEnvironmentCustomerPackage(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="thread_customer_test_"))
        self.story_path = Path("story/story_I/part_1/story_i_part_1.json")

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_customer_package_embedded_media_and_isolation(self):
        """Verify that .threadpkg contains all media and resolves in isolated clean folder."""
        release_out = self.tmp_dir / "release"
        result = execute_production_release(self.story_path, release_out)

        pkg_file = Path(result["package_file"])
        self.assertTrue(pkg_file.is_file(), f"Package file missing: {pkg_file}")

        # 1. Inspect Zip Archive Contents
        with zipfile.ZipFile(pkg_file, "r") as zf:
            namelist = zf.namelist()
            self.assertIn("manifest.json", namelist)
            self.assertIn("story.json", namelist)
            self.assertIn("media/audiovisual.mp4", namelist)
            self.assertIn("subtitles/english.vtt", namelist)

            # Check that MP4 inside package is non-empty (>100KB)
            mp4_info = zf.getinfo("media/audiovisual.mp4")
            self.assertGreater(mp4_info.file_size, 100_000, "Embedded MP4 size too small")

        # 2. Extract into isolated directory OUTSIDE project workspace
        extract_dir = self.tmp_dir / "customer_install"
        unpacked_path = unpack_story_package(pkg_file, extract_dir)

        self.assertTrue((extract_dir / "manifest.json").is_file())
        self.assertTrue((extract_dir / "story.json").is_file())
        self.assertTrue((extract_dir / "media" / "audiovisual.mp4").is_file())
        self.assertTrue((extract_dir / "subtitles" / "english.vtt").is_file())

        # 3. Verify Offline Validation of Unpacked Package
        pkg, manifest = load_story_package_from_archive(pkg_file)
        self.assertEqual(manifest.story_id, "story-i-part-1-aulis")
        self.assertEqual(pkg.metadata.id, "story-i-part-1-aulis")

    def test_corrupt_package_fails_clearly(self):
        """Verify that a corrupted package archive fails clearly with PackageArchiveError."""
        corrupt_file = self.tmp_dir / "corrupt.threadpkg"
        with open(corrupt_file, "wb") as f:
            f.write(b"NOT_A_ZIP_FILE_CORRUPT_BYTES")

        with self.assertRaises(PackageArchiveError):
            unpack_story_package(corrupt_file, self.tmp_dir / "dest")


if __name__ == "__main__":
    unittest.main()
