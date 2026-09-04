"""Tests for the THREAD CLI commands and user feedback."""

import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from thread_runtime.cli import build_parser, main


class TestCLI(unittest.TestCase):
    def test_parser_exists(self):
        parser = build_parser()
        self.assertEqual(parser.prog, "thread")

    @patch("thread_runtime.cli.get_version", return_value="9.9.9")
    def test_cli_version_from_metadata(self, mock_get_version):
        parser = build_parser()
        buf = io.StringIO()
        with redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
            parser.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("THREAD Runtime 9.9.9", buf.getvalue())

    def test_doctor_command(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["doctor"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("THREAD Runtime Diagnostics", output)
        self.assertIn("Platform:", output)
        self.assertIn("Status: READY", output)

    def test_info_command_with_valid_story(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["info", "examples/hello.thread"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Title:           The Crossroads of Destiny", output)
        self.assertIn("Total Scenes:    6", output)
        self.assertIn("Cinematic Scenes:1", output)

    def test_validate_command_with_detailed_reporting(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["validate", "examples/hello.thread"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("THREAD Package Validation", output)
        self.assertIn("[✓] Cinematic Scenes: 1 scene(s) validated", output)

    def test_cinematic_info_command(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["cinematic-info", "examples/hello.thread"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("THREAD Cinematic Scenes Summary", output)
        self.assertIn("Scene ID:    scene_threshold", output)
        self.assertIn("Duration:    32.0s", output)

    def test_cinematic_validate_command(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["cinematic-validate", "examples/hello.thread"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("[✓] Cinematic Scene 'scene_threshold': Validated", output)
        self.assertIn("[✓] Match Cut Reference:", output)

    def test_timeline_command(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["timeline", "examples/hello.thread", "scene_threshold"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("SCENE: The Threshold: Echoes of Eternity (scene_threshold)", output)
        self.assertIn("SHOT shot_001", output)
        self.assertIn("MATCH CUT → scene_future_threshold / shot_006", output)

    def test_cinematic_play_command(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["cinematic-play", "examples/hello.thread"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Playing Real-Time Timeline Simulation", output)
        self.assertIn("TRANSITION: MATCH_CUT", output)

    def test_release_command(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            rel_dir = Path(tmp_dir) / "test_rel"
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main(["release", "examples/hello.thread", "--output-dir", str(rel_dir)])

            self.assertEqual(exit_code, 0)
            output = buf.getvalue()
            self.assertIn("STATUS: RELEASE READY", output)
            self.assertTrue((rel_dir / "release_manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
