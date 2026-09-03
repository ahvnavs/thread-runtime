import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from thread_runtime.cli import build_parser


class TestCLI(unittest.TestCase):
    def test_parser_exists(self):
        parser = build_parser()
        self.assertEqual(parser.prog, "thread")

    @patch("thread_runtime.cli.get_version", return_value="9.9.9")
    def test_cli_version_from_metadata(self, mock_get_version):
        parser = build_parser()
        mock_get_version.assert_called_once_with("thread-runtime")
        buf = io.StringIO()
        with redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
            parser.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("THREAD Runtime 9.9.9", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
