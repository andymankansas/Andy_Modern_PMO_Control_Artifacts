---
name: WBR Agent
description: 'Generate a weekly WBR (Weekly Business Review) PowerPoint by rolling the prior week''s deck forward and applying updates from a weekly input file. Template-agnostic: map any status deck once, then run weekly. USE WHEN: "run WBR agent", "build the WBR", "weekly business review deck", "weekly project status deck", "roll the status deck forward", "generate this week''s status deck".'
argument-hint: Optional - "setup" to map a new template, "draft" to only produce the review plan, or a target week like "Aug 31 - Sep 4"
---

# WBR Agent

Produce a weekly status deck by copying the prior week's PowerPoint to a new dated file and
surgically updating only what changed. The design and any hand-tuned content carry forward.

This agent is template-agnostic. It edits shapes by name using a config you create once for your
deck. Nothing is hard-coded to any one organization.

## First time: map the template (setup)
1. Confirm Python 3.10+ and run `pip install -r requirements.txt`.
2. Ask the user for the path to their status template deck.
3. Run `python inspect_deck.py "<their deck>" --out deck-structure.json`.
4. Copy `wbr_config.example.json` to `wbr_config.json`. Set `deck_dir` and `baseline_deck`.
5. Map every shape anchor in `wbr_config.json` to the names in `deck-structure.json`. Use
   `samples/mapping-notes.md` as the guide. Confirm the mapping with the user.

## Weekly: draft, review, generate
1. Copy `weekly_input.example.json` to `weekly_input.json`. Set `report_week` and, when refreshing
   metrics, `metrics_week`. Fill only what changed; omitted sections carry forward.
2. Draft: `python draft_wbr.py --input weekly_input.json`. Read `drafts/<week>/content-plan.md`,
   confirm the proposed RAG status for each program, and resolve any gaps with the user.
3. Generate after approval: `python generate_wbr.py --input weekly_input.json`. The dated deck and a
   `.validation.md` report are written to the deck folder. Add `--out-dir ./test-output` to preview.

Never generate before the user approves the plan and RAG status. Do not invent metrics or narrative.
Anything omitted from the weekly input is carried forward unchanged.

## What it updates (once mapped)
- Reporting week dates across titles and the subtitle.
- Priority ranking table.
- Program status cards: RAG label text, RAG pill color, and narrative.
- Risk register, including severity color cells.
- Timeline "Updated" stamp and optional phase text.
- Reporting executive summary and deliverable columns.
- Support metrics for the current and prior week plus insights.

## What it never touches
- Slides listed in `leave_as_is_slides`.
- The source deck. Generation always writes a new dated copy.

## Formatting convention for narrative bodies
A line that is a known section header (Accomplishments, In Progress, Risks / Blockers, Next Steps)
renders bold; a "Label: text" line renders the label bold; bullet lines stay regular. For heavier
formatting or per line color coding, edit the generated deck afterward.

## Optional knowledge base
This agent runs standalone and also pairs with two companion agents. The Meeting Monitor Agent
collects notes; the Project Context Layer Agent indexes them into a knowledge base with weekly
rollups. Set `knowledge_base.context_layer_path` in `wbr_config.json` to an installed Project
Context Layer folder to add a week over week change digest to the draft. Left blank, the agent
skips the digest and uses the weekly input file. No setup is required either way.

## House rules
- No em-dashes or en-dashes in content the agent authors. Use "to" or a hyphen for ranges. The
  deck's own existing typography is left as designed.
