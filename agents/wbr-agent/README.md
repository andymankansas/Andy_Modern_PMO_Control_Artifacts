# WBR Agent

Generate a weekly WBR (Weekly Business Review) PowerPoint by rolling the prior week's deck forward
and applying updates from a small weekly input file. Map any status template once, then produce a
polished, dated deck every week in seconds.

The agent never rebuilds slides from scratch and never edits your source deck. It copies the prior
week's deck to a new dated file and surgically updates only what changed, so your design and any
hand-tuned content carry forward.

- Template-agnostic: works with your PowerPoint layout after a one-time mapping.
- PowerPoint not required: runs on python-pptx, cross-platform.
- Draft first, review, then generate: you approve the content and RAG status before anything is written.
- Point an LLM at this folder and it can set up and run the whole thing for you.

## Point an LLM at this folder

Open this folder in VS Code with GitHub Copilot (or any capable LLM) and say:

> Read README.md in this folder and set up the WBR Agent for my template at `<path to your .pptx>`,
> then generate this week's deck for the week of `<start>` to `<end>`.

The `wbr-agent.agent.md` file is a ready-to-use Copilot agent definition. Copy it into your
project's `.github/agents/` folder to invoke the agent by name.

## Requirements

- Python 3.10 or later.
- `pip install -r requirements.txt` (installs python-pptx).
- A PowerPoint status template to roll forward each week.

## One-time setup: map your template

The engine finds what to edit by shape name on each slide. Map your deck once:

```
pip install -r requirements.txt
python inspect_deck.py "path/to/your_template.pptx" --out deck-structure.json
```

Copy the example config and edit it:

```
# Windows PowerShell
Copy-Item wbr_config.example.json wbr_config.json
# macOS / Linux
cp wbr_config.example.json wbr_config.json
```

In `wbr_config.json`, set `deck_dir` (the folder holding your deck), `baseline_deck` (the template
filename), and update each shape name to match `deck-structure.json`. The `samples/mapping-notes.md`
guide explains every field. The fastest path: give an LLM `deck-structure.json` and
`wbr_config.example.json` and ask it to produce your `wbr_config.json`.

## Weekly run

```
# 1. Prepare this week's input
cp weekly_input.example.json weekly_input.json      # then edit report_week and what changed

# 2. Draft and review
python draft_wbr.py --input weekly_input.json
#    read drafts/<week>/content-plan.md, confirm RAG status, resolve gaps

# 3. Generate the dated deck (after approval)
python generate_wbr.py --input weekly_input.json
```

Preview without writing to your deck folder:

```
python generate_wbr.py --input weekly_input.json --out-dir ./test-output
```

The generator writes a new dated `.pptx` and a `.validation.md` report listing every change.

## The weekly input file

Every section is optional. Anything you omit carries forward from last week. Set `report_week`
(the reporting week) and, when refreshing metrics, `metrics_week`. Leave `prior_deck` blank to roll
the configured baseline forward, or set it to a specific filename to roll a particular deck.

Sections: `programs` (RAG plus narrative per card), `risks` (the full risk register),
`priorities` (the ranked list), `timeline` (the "Updated" stamp and optional phase text),
`reporting` (executive summary and two deliverable columns), and `metrics` (current and prior week
values plus insights).

Narrative formatting: a line that is a known section header (Accomplishments, In Progress,
Risks / Blockers, Next Steps) renders bold; a "Label: text" line renders the label bold; bullet
lines stay regular. For heavier formatting, edit the generated deck afterward.

## What it updates

- Reporting week dates across titles and the subtitle.
- Priority ranking table.
- Program status cards: RAG label text, RAG pill color, and narrative.
- Risk register, including severity color cells (H red, M amber, L green by default).
- Timeline "Updated" stamp and optional phase text.
- Reporting executive summary and the two deliverable columns.
- Support metrics for the current and prior week plus an insights paragraph.

## What it never touches

- Slides listed in `leave_as_is_slides` in your config.
- Your source deck. Generation always writes a new dated copy.

## Files

| File | Purpose |
|------|---------|
| `wbr-agent.agent.md` | Copilot agent definition. Copy into `.github/agents/` to use in VS Code. |
| `inspect_deck.py` | Dump any deck's slides and shape names to JSON for mapping. |
| `wbr_config.example.json` | Template map plus color and behavior settings. Copy to `wbr_config.json`. |
| `weekly_input.example.json` | Weekly content. Copy to `weekly_input.json`. |
| `draft_wbr.py` | Stage 1: writes a content plan and gaps report. |
| `generate_wbr.py` | Stage 2: writes the dated deck and a validation report. |
| `wbr_lib.py` | Shared date, PPTX, and rich-text helpers. |
| `samples/mapping-notes.md` | How to map your template to the config. |

## Optional knowledge base

This agent works standalone, and it also pairs with two companion agents:

- The Meeting Monitor Agent collects meeting, email, and Teams notes as `.md` files.
- The Project Context Layer Agent indexes those notes into a queryable knowledge base with weekly
  rollups.

When a Project Context Layer is installed, set `knowledge_base.context_layer_path` in
`wbr_config.json` to that agent's folder (the one containing the `context_layer` package). The
draft stage then adds a week over week change digest (new and closed action items, new decisions,
new risks) so nothing is missed. Left blank, the agent skips the digest and relies on your weekly
input file. No configuration is required to run without it.

## Troubleshooting

- An edit did not apply: the shape name in `wbr_config.json` does not match your deck. Re-run
  `inspect_deck.py` and fix the name.
- Dates did not roll forward: the prior week could not be detected. Ensure a slide title contains a
  `M/D/YYYY` to `M/D/YYYY` range.
- The agent is missing in Copilot: confirm `wbr-agent.agent.md` is in `.github/agents/` and reload
  the VS Code window.

## License

MIT. See `LICENSE`.
