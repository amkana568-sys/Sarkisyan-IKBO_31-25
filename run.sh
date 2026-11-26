#!/usr/bin/env bash
set -euo pipefail

output="${1:-result.json}"
python3 "$(dirname "$0")/src/main.py" --output "$output"
