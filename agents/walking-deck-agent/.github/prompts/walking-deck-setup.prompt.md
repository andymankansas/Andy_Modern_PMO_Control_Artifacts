---
name: Walking Deck Setup
description: "Configure the Walking Deck Agent: project, brand, output, slide selection, and sources."
agent: Walking Deck Agent
argument-hint: "Optional: project name."
---

Set up my Walking Deck Agent.

Guide me one topic at a time and confirm each answer before moving on:

1. Project name, a one-line objective, and the primary audience (who will read
   this deck, and why they should care).
2. Brand: primary, accent, and dark colors as hex; optional logo and hero image
   paths; and title/body fonts. If I have none, use the neutral default palette.
3. Output folder and filename pattern (use `{slug}` and `{date}` placeholders).
4. Which slide blocks to include and in what order. Show me the available blocks
   with `build_deck.py --list-blocks` and recommend the default story.
5. Sources: which folders hold my artifacts, and whether WorkIQ is available for
   optional Microsoft 365 grounding (account, tracked meetings, key people).

Write `config/walking-deck-config.json`, validate it against
`schemas/walking-deck-config.schema.json`, and show me a short summary. Do not
gather content or build the deck during setup.
