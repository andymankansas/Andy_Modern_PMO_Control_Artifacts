import json
from pathlib import Path

from jsonschema import Draft202012Validator

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _validate(schema_name: str, data_path: Path):
    schema = json.loads((PACKAGE_ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    assert not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_example_config_valid():
    _validate("walking-deck-config.schema.json", PACKAGE_ROOT / "config" / "walking-deck-config.example.json")


def test_sample_content_valid():
    _validate("walking-deck-content.schema.json", PACKAGE_ROOT / "samples" / "sample_project_content.json")


def test_config_rejects_bad_slug(tmp_path):
    schema = json.loads((PACKAGE_ROOT / "schemas" / "walking-deck-config.schema.json").read_text(encoding="utf-8"))
    bad = {"project_slug": "Bad Slug", "slides": ["cover"]}
    errors = list(Draft202012Validator(schema).iter_errors(bad))
    assert errors


def test_config_rejects_unknown_block():
    schema = json.loads((PACKAGE_ROOT / "schemas" / "walking-deck-config.schema.json").read_text(encoding="utf-8"))
    bad = {"project_slug": "ok", "slides": ["not_a_block"]}
    errors = list(Draft202012Validator(schema).iter_errors(bad))
    assert errors
