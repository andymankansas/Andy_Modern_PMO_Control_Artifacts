# Walking Deck Agent

Build a polished, self-service **walking deck** for any project or program. The
agent interviews you, ingests your artifacts (SOW, meeting notes, recordings,
prior decks, plans, RAID), and generates a branded PowerPoint from a flexible,
selectable set of slide blocks.

A walking deck is a concise slide story a newcomer can read in 10-20 minutes
without a presenter. It answers, like a news story: why change, the solution,
how it works, where we are and where we're going, and who moves it forward.

## Capabilities

- Interviews you one topic at a time and helps distill each slide to one message.
- Catalogs project artifacts read-only and extracts candidate facts.
- Optionally transcribes meeting recordings locally (offline, CPU) - no upload.
- Optionally supplements with WorkIQ (Microsoft 365) when available.
- Generates a 16:9 deck from a configurable, reorderable set of slide blocks.
- Fully brandable: colors, fonts, optional logo and hero image.
- Deterministic Python builder with schema-validated config and content.

## Install

Extract the release ZIP, open the extracted folder in VS Code, and run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

Then select **Walking Deck Agent** in VS Code Chat and run **Walking Deck Setup**.
See [INSTALL.md](INSTALL.md) for prerequisites and details.

## Normal Workflow

1. Run **Walking Deck Setup** - project, brand, output, slide selection, sources.
2. Run **Walking Deck Intake** - point the agent at your artifacts; transcribe
   recordings on request.
3. Run **Walking Deck Interview** - answer the targeted questions
   (see [docs/QUESTIONS.md](docs/QUESTIONS.md)).
4. Run **Walking Deck Build** - generate the branded `.pptx`.
5. Iterate on individual slide blocks and rebuild to a new dated file.

## Slide Blocks

`cover`, `agenda`, `problem`, `vision`, `how_it_works`, `roles`, `scope`,
`roadmap`, `milestones`, `current_state`, `team`, `next_steps`, `closer`,
plus generic `section` and `bullets`. Pick any subset, in any order. See
[docs/BLOCKS.md](docs/BLOCKS.md).

```powershell
.\.venv\Scripts\python.exe .\scripts\build_deck.py --list-blocks
```

## Try the demo

```powershell
.\.venv\Scripts\python.exe .\scripts\build_deck.py --config .\config\walking-deck-config.example.json
```

This builds a full 12-slide deck from the bundled sample content into `output/`.

## Package Layout

- `.github/agents/`: agent definition.
- `.github/prompts/`: setup, intake, interview, build, and reconfigure prompts.
- `config/`: example configuration (your runtime config stays local).
- `schemas/`: JSON contracts for config and content.
- `scripts/`: deterministic builder, artifact intake, transcription, validation, release.
- `samples/`: a filled sample content file that produces a demo deck.
- `docs/`: the interview question bank and slide block reference.
- `tests/`: builder and schema tests.
- `output/`: generated decks and manifests (ignored by Git).

## Data Handling

Do not commit runtime configuration, content, artifacts, transcripts, or
generated decks. The bundled sample contains no real project data.

## Current Platform

The installer targets Windows because the intended experience uses VS Code,
PowerShell, and OneDrive or SharePoint synced paths. Deck generation uses Python
and `python-pptx` and does not require desktop PowerPoint.
