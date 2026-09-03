import unittest

from thread_runtime.cli import build_parser


class TestCLI(unittest.TestCase):
    def test_parser_exists(self):
        parser = build_parser()
        self.assertEqual(parser.prog, "thread")


if __name__ == "__main__":
    unittest.main()
