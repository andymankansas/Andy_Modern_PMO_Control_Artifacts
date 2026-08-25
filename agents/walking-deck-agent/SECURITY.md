# Security and Data Handling

## Principles

- The agent treats all project artifacts as read-only sources. It never modifies
  your source files.
- Deck generation is deterministic and local. No project content leaves your
  machine unless you choose to use optional WorkIQ grounding.
- Recording transcription runs locally on CPU with `faster-whisper`. Audio is
  never uploaded.

## Do not commit

Keep the following local and out of version control (already covered by
`.gitignore`):

- `config/walking-deck-config.json` and `config/walking-deck-content.json`.
- `output/*` - generated decks, manifests, and transcripts.
- Any artifacts you copy into the package folder (SOW, notes, recordings, decks).

The bundled `config/*.example.json` and `samples/*.json` contain no real project
data.

## Optional WorkIQ

WorkIQ grounding is optional and, when enabled, reads Microsoft 365 data under
your own credentials. It is read-only. Disable it during setup if you do not want
M365 access, and the agent will rely on local artifacts and your interview
answers.

## Reporting

If you find a security issue in this package, do not open a public issue.
Contact the repository owner directly.
