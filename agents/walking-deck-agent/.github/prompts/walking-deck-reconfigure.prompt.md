---
name: Walking Deck Reconfigure
description: "Change brand, slide selection, or output settings for the Walking Deck Agent."
agent: Walking Deck Agent
argument-hint: "Optional: what to change (brand, slides, output)."
---

Reconfigure my Walking Deck Agent.

Load `config/walking-deck-config.json` and change only what I ask:

- **Brand** - primary/accent/dark colors, logo, hero, fonts.
- **Slides** - which blocks are included and their order (see `--list-blocks`).
- **Output** - folder and filename pattern.
- **Sources** - artifact folders and WorkIQ settings.

Revalidate against the schema, show me a short summary of what changed, and do
not rebuild the deck until I confirm.
