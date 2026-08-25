import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE_ROOT / "scripts"))

import build_deck  # noqa: E402
import deck_blocks  # noqa: E402
from pptx import Presentation  # noqa: E402


def test_registry_has_expected_blocks():
    expected = {
        "cover", "agenda", "problem", "vision", "how_it_works", "roles",
        "scope", "roadmap", "milestones", "current_state", "team",
        "next_steps", "closer", "section", "bullets",
    }
    assert expected.issubset(set(deck_blocks.REGISTRY))


def test_build_demo_deck(tmp_path):
    config = PACKAGE_ROOT / "config" / "walking-deck-config.example.json"
    out = tmp_path / "demo.pptx"
    result = build_deck.build(config, None, str(out))
    assert result.exists()
    prs = Presentation(result)
    assert len(prs.slides) == 12
    assert abs(prs.slide_width / prs.slide_height - 16 / 9) < 0.001


def test_unknown_block_raises(tmp_path):
    config = tmp_path / "bad.json"
    content = tmp_path / "content.json"
    content.write_text('{"meta": {}}', encoding="utf-8")
    config.write_text(
        '{"project_slug": "x", "slides": ["not_a_block"], "content_file": "content.json"}',
        encoding="utf-8",
    )
    # content_file is resolved relative to the package root, so point the build at
    # an inline content file by writing it where the resolver expects.
    (tmp_path / "content.json").write_text('{"meta": {}}', encoding="utf-8")
    with pytest.raises(SystemExit):
        build_deck.build(config, content, str(tmp_path / "out.pptx"))


def test_brand_defaults_and_hex():
    brand = deck_blocks.Brand.from_dict({"primary": "#123456"})
    assert brand.primary == deck_blocks._hex("123456")
    # unknown accent name falls back to primary
    assert brand.color("nope") == brand.primary
    assert brand.color("green") == deck_blocks.GREEN
