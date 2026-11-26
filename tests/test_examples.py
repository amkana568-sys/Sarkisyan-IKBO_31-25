"""Integration tests for the two required subject-area examples."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config_parser import convert


class ExampleTests(unittest.TestCase):
    """Check example configuration files."""

    def test_computer_example(self):
        source = (ROOT / "examples" / "computer.cfg").read_text(
            encoding="utf-8"
        )
        result = convert(source)
        self.assertEqual(result["ram"], 16)
        self.assertEqual(result["power"], 80)
        self.assertEqual(result["label"], "CPU-8-core")

    def test_library_example(self):
        source = (ROOT / "examples" / "library.cfg").read_text(
            encoding="utf-8"
        )
        result = convert(source)
        self.assertEqual(result["active"], 40)
        self.assertEqual(result["details"]["rooms"], [2, 3, 4])


if __name__ == "__main__":
    unittest.main()
