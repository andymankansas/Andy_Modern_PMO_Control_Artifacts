# Installation

## Prerequisites

- Python 3.10 or later (the Knowledge Base uses only the standard library).
- Optional, for Stage 1 ingestion: Visual Studio Code with GitHub Copilot and WorkIQ access.
- Optional, only if you generate `.docx` notes: `pip install -r requirements.txt`.

## Install from GitHub Release

1. Download `Project_Context_Layer_Setup_<version>.zip` from the Releases page (the tag starts with `project-context-layer/`).
2. Extract it to a permanent folder.
3. To use it as a Copilot agent, copy `project-context-layer.agent.md` into your project's `.github/agents/` folder and reload VS Code (`Ctrl+Shift+P`, `Reload Window`).
4. To use the Knowledge Base directly, just run the CLI from the extracted folder (see below).

## Quick start (no Microsoft 365 needed)

```powershell
cd project-context-layer
Copy-Item context_layer\config.example.json context_layer\config.json
# edit config.json: point artifacts_dirs at .\samples to smoke-test
python -m context_layer.context_cli backfill
python -m context_layer.context_cli status
python reports\weekly_report.py
python reports\open_items.py
```

The `samples/` folder has two linked notes so you can see entities, lineage, quality, and the
rollup work end to end. Then point `artifacts_dirs` at your own notes folder.

## Daily use

- `python -m context_layer.context_cli daily` indexes only new or changed notes (fast, idempotent).
- `python -m context_layer.context_cli backfill --reset` does a clean full rebuild.

## Stage 1 ingestion (optional)

Stage 1 collects meetings, email, and chat into notes via WorkIQ / Microsoft 365. If you have
that access, adapt the tracked-meeting list, `seed_terms`, and folders in `config.json`, then run
the agent in Copilot Chat. If you do not, skip Stage 1 and index any existing notes folder.

## Troubleshooting

- If the agent does not appear in Copilot, confirm the file is at `.github/agents/project-context-layer.agent.md` and reload the window.
- If indexing finds nothing, confirm `artifacts_dirs` points at a folder of `.md` notes shaped like the samples.
- After changing the extractor, run `backfill --reset` for a clean rebuild.
