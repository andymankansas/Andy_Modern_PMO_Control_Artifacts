---
name: RAID Setup
description: "Configure the RAID Review Agent using an existing workbook or the included template."
agent: RAID Review Agent
argument-hint: "Optional: existing workbook path or template destination."
---

Set up my RAID Review Agent.

Begin by asking whether I want to use my existing Workback and RAID workbook or create a new project workbook from the included `templates/Workback_RAID_Template.xlsx`.

Inspect the selected workbook without modifying it. Guide me one topic at a time through project scope, exclusions, workbook tab and field mappings, knowledge sources, optional WorkIQ settings, review policy, and write preferences. Save confirmed settings to `config/raid-config.json`, validate the configuration and workbook read-only, and show a final setup summary.

Do not perform a RAID review, approval, or workbook update during setup.