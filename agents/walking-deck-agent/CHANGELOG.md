# Changelog

All notable changes to the Walking Deck Agent are documented here.

## 1.0.0 - 2026-08-25

Initial release.

- Deterministic, brandable walking-deck builder (`scripts/build_deck.py`) with a
  library of 15 selectable slide blocks (`scripts/deck_blocks.py`).
- Flexible slide selection: pick any subset of blocks, in any order, via config.
- Artifact intake cataloging (`scripts/intake.py`) and optional local recording
  transcription (`scripts/transcribe.py`, `faster-whisper`).
- JSON schemas for config and content, with a validator (`scripts/validate_json.py`).
- Agent definition and five prompts: setup, intake, interview, build, reconfigure.
- Interview question bank (`docs/QUESTIONS.md`) and block reference (`docs/BLOCKS.md`).
- Bundled sample content that builds a full 12-slide demo deck.
- Windows installer (`setup.ps1`), release builder (`scripts/build_release.ps1`),
  CI validation, and tests.
