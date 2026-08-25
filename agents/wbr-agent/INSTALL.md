# Installation

## Prerequisites

- Python 3.10 or later.
- `pip install -r requirements.txt` (installs python-pptx).
- A PowerPoint status template to roll forward each week (any layout works after mapping).
- PowerPoint is NOT required. Everything runs through python-pptx.

## Install from GitHub Release

1. Download `WBR_Agent_Setup_<version>.zip` from the Releases page (the tag starts with `wbr-agent/`).
2. Extract it to a permanent folder.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. To use it as a Copilot agent in VS Code, copy `wbr-agent.agent.md` into your project's
   `.github/agents/` folder and reload VS Code (`Ctrl+Shift+P`, `Reload Window`).

## One-time setup (map your template)

```
python inspect_deck.py "path/to/your_template.pptx" --out deck-structure.json
```

Copy `wbr_config.example.json` to `wbr_config.json`, set `deck_dir` and `baseline_deck`, then
update the shape names to match `deck-structure.json`. An LLM can do this mapping for you: give it
`deck-structure.json` and `wbr_config.example.json` and ask it to produce `wbr_config.json`.

## Weekly run

```
python draft_wbr.py --input weekly_input.json
# review drafts/<week>/content-plan.md, then:
python generate_wbr.py --input weekly_input.json
```

Add `--out-dir ./test-output` to `generate_wbr.py` to preview without writing to your deck folder.

## Troubleshooting

- If the agent does not appear in Copilot, confirm the file is at
  `.github/agents/wbr-agent.agent.md` and reload the window.
- If an edit did not apply, the shape name in `wbr_config.json` likely does not match your deck.
  Re-run `inspect_deck.py` and fix the name.
- If dates did not roll, the prior deck's week could not be detected. Confirm a slide title
  contains a `M/D/YYYY` to `M/D/YYYY` range.
