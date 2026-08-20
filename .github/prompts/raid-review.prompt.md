---
name: RAID Review
description: "Run an evidence-grounded, read-only RAID review and create a proposal."
agent: RAID Review Agent
argument-hint: "Optional: lookback days or since date."
---

Run a read-only RAID review using `config/raid-config.json`.

Review the configured workbook tabs, Meeting Monitor history, local knowledge-base material, project files, and enabled WorkIQ sources for the requested period. Cross-reference every recommendation against current workbook content. Produce timestamped Markdown and schema-valid JSON proposals with current values, proposed values, operations, rationale, confidence, and source evidence.

Do not modify the workbook and do not approve any proposal on my behalf.