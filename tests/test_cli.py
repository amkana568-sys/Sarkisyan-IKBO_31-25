"""Tests for command-line input and JSON file output."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "src" / "main.py"


class CommandLineTests(unittest.TestCase):
    """Check the command-line interface."""

    def run_program(self, source, output_path):
        """Run the converter with source text sent to standard input."""
        return subprocess.run(
            [sys.executable, str(PROGRAM), "--output", str(output_path)],
            input=source,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_reads_stdin_and_writes_json_file(self):
        """A valid configuration is converted and saved as JSON."""
        with tempfile.TemporaryDirectory() as folder:
            output_path = Path(folder) / "result.json"
            result = self.run_program("{name -> q(Test). count -> 3.}",
                                      output_path)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            data = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(data, {"name": "Test", "count": 3})

    def test_reports_syntax_error(self):
        """Invalid syntax returns an error and does not create JSON."""
        with tempfile.TemporaryDirectory() as folder:
            output_path = Path(folder) / "result.json"
            result = self.run_program("{name -> q(Test)}", output_path)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Синтаксическая ошибка", result.stderr)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
