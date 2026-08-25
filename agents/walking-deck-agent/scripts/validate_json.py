"""Validate a JSON file against a bundled schema.

Usage:
    python scripts/validate_json.py walking-deck-config.schema.json config/walking-deck-config.json
    python scripts/validate_json.py walking-deck-content.schema.json config/walking-deck-content.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: validate_json.py <schema-name> <json-file>", file=sys.stderr)
        return 2
    schema_path = SCHEMA_DIR / sys.argv[1]
    data_path = Path(sys.argv[2])
    with schema_path.open(encoding="utf-8") as f:
        schema = json.load(f)
    with data_path.open(encoding="utf-8") as f:
        data = json.load(f)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            loc = "/".join(str(p) for p in err.path) or "<root>"
            print(f"INVALID at {loc}: {err.message}", file=sys.stderr)
        return 1
    print(f"OK: {data_path} is valid against {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
