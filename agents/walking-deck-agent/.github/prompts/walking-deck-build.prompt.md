---
name: Walking Deck Build
description: "Validate the config and content, then generate the branded walking deck."
agent: Walking Deck Agent
argument-hint: "Optional: an output path override."
---

Build my walking deck.

1. Validate `config/walking-deck-config.json` and `config/walking-deck-content.json`
   against their schemas.
2. Run `scripts/build_deck.py --config config/walking-deck-config.json`. It
   renders only the selected slide blocks, checks package integrity, and writes a
   dated `.pptx` into the output folder.
3. Tell me the output path and slide count, and offer to open it.
4. If I want changes, iterate on specific slide blocks in the content file and
   rebuild - always to a new dated file. Never overwrite a deck I have edited.
