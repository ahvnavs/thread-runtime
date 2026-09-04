"""Production Release Gate, Clean Environment, and Audiovisual Acceptance Tests."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from thread_runtime.audio import AudioMixer
from thread_runtime.cinematic import validate_cinematic_scene
from thread_runtime.package import load_story_package
from thread_runtime.provenance import validate_asset_provenance
from thread_runtime.release import compute_sha256, execute_production_release
from thread_runtime.errors import StoryValidationError


class TestReleaseGate(unittest.TestCase):
    def test_audio_mixer_wav_rendering(self):
        scene_data = {
            "id": "audio_test_scene",
            "title": "Audio Test Scene",
            "duration_ms": 2000,
            "shots": [
                {
                    "id": "shot_001",
                    "duration_ms": 2000,
                    "camera": {"framing": "wide", "movement": "static"},
                    "cues": [
                        {"cue_type": "ambience", "asset_id": "wind_whistle", "start_time_ms": 0},
                        {"cue_type": "sound_effect", "asset_id": "gate_hum", "start_time_ms": 500},
                    ],
                }
            ],
        }
        scene = validate_cinematic_scene(scene_data)
        mixer = AudioMixer(scene, sample_rate=22050)

        with tempfile.TemporaryDirectory() as tmp_dir:
            wav_path = Path(tmp_dir) / "test_audio.wav"
            out = mixer.render_to_wav(wav_path)
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size, 1000)

    def test_asset_provenance_validation(self):
        valid_assets = [
            {"id": "asset_01", "type": "environment", "source": "2D Compositor", "license": "MIT", "status": "ORIGINAL"},
            {"id": "asset_02", "type": "audio", "source": "Audio Mixer", "license": "MIT", "status": "GENERATED"},
        ]
        registry = validate_asset_provenance(valid_assets)
        self.assertIn("asset_01", registry)
        self.assertEqual(registry["asset_01"].status, "ORIGINAL")

        invalid_assets = [
            {"id": "mystery_asset", "type": "image", "status": "UNKNOWN"},
        ]
        with self.assertRaises(StoryValidationError):
            validate_asset_provenance(invalid_assets)

    def test_clean_environment_release_execution(self):
        with tempfile.TemporaryDirectory() as src_release_dir, tempfile.TemporaryDirectory() as clean_dir:
            src_out = Path(src_release_dir) / "release_pkg"
            res = execute_production_release("examples/hello.thread", src_out)

            # Copy release artifact to clean isolated folder
            isolated_target = Path(clean_dir) / "isolated_release"
            shutil.copytree(src_out, isolated_target)

            # Verify files exist in isolated environment
            mp4_file = isolated_target / "hello-thread-demo_audiovisual.mp4"
            pkg_file = isolated_target / "hello-thread-demo.threadpkg"
            manifest_file = isolated_target / "release_manifest.json"

            self.assertTrue(mp4_file.is_file())
            self.assertTrue(pkg_file.is_file())
            self.assertTrue(manifest_file.is_file())

            # Check manifest checksums
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            self.assertEqual(compute_sha256(mp4_file), manifest["artifacts"]["video"]["sha256"])
            self.assertEqual(compute_sha256(pkg_file), manifest["artifacts"]["package"]["sha256"])

            # Test loading package from clean isolated environment
            clean_pkg = load_story_package(pkg_file)
            self.assertEqual(clean_pkg.metadata.id, "hello-thread-demo")
            self.assertIn("scene_threshold", clean_pkg.cinematic_scenes)


if __name__ == "__main__":
    unittest.main()
