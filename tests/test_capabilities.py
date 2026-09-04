"""Tests for capability detection model."""

import unittest

from thread_runtime.capabilities import SystemCapabilities, detect_capabilities


class TestCapabilities(unittest.TestCase):
    def test_detect_capabilities_returns_populated_model(self):
        caps = detect_capabilities()
        self.assertIsInstance(caps, SystemCapabilities)
        self.assertTrue(len(caps.os_name) > 0)
        self.assertTrue(len(caps.cpu_architecture) > 0)
        self.assertTrue(len(caps.python_version) > 0)
        self.assertIsInstance(caps.interactive_stdin, bool)
        self.assertIsInstance(caps.interactive_stdout, bool)
        self.assertIsInstance(caps.color_supported, bool)
        self.assertIsInstance(caps.unicode_supported, bool)
        self.assertIsInstance(caps.cwd_writable, bool)


if __name__ == "__main__":
    unittest.main()
