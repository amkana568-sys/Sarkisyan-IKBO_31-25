"""Command-line entry point for variant 23."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config_parser import ConfigError, convert


def make_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Конвертер учебного конфигурационного "
            "языка в JSON"
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="путь к выходному JSON-файлу",
    )
    return parser


def main() -> int:
    """Read stdin, convert the document and write the JSON file."""
    args = make_parser().parse_args()
    source = sys.stdin.read()
    try:
        result = convert(source)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    except (ConfigError, OSError, TypeError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
