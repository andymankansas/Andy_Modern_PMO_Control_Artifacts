# Project Context Layer

Turn the stream of a project's meetings, emails, and chats into a durable, queryable
**source of truth** that reports and other agents can build on.

Inspired by the idea of an enterprise "context layer": the bottleneck in useful AI is not
model capability, it is having trustworthy, organized context. This agent builds that context
from your everyday project signals.

```
 STAGE 1: INGESTION (optional)         STAGE 2: KNOWLEDGE BASE (always)
 collect signals  ->  notes folder  -> index notes -> queryable store -> reports
 (needs WorkIQ / M365)                 (plain Python, any notes folder)
```

## Why two stages, one agent

- **Ingestion** gathers meetings, email, and chat into organized note files. It needs
  WorkIQ / Microsoft 365 access.
- **Knowledge Base** indexes those notes into a linked, self-checking store and serves it as
  a project source of truth. It is plain Python over a folder, no network, and works on its own.

If you have M365, run both. If you only have a folder of notes (from this agent or anything
else), skip Stage 1 and just run Stage 2.

## What it does (six capabilities)

1. **Entity index** - parses each note into typed entities: people, meetings, decisions,
   action items, risks, email/chat threads.
2. **Lineage** - the same item seen across days becomes one entity with a history; subject
   variants of a thread collapse together.
3. **Quality + drift** - flags missing owners, due dates, rationale, and stubs, plus keyword
   drift, with a one-line health score.
4. **Confidence + provenance** - every fact is tagged high/medium/low and traceable to its
   source file.
5. **Corrections (norms)** - records your judgment calls so they are reused instead of re-asked.
6. **Weekly rollups** - compact weekly status with a week-over-week diff, ready for reports.

## Requirements

- Python 3.10+ (the knowledge base uses only the standard library).
- `python-docx` only if you generate `.docx` notes in Stage 1 (`pip install -r requirements.txt`).

## Quick start (no M365 needed)

```powershell
cd Project_Context_Layer
Copy-Item context_layer\config.example.json context_layer\config.json
# edit config.json -> point artifacts_dirs at .\samples to smoke-test
python -m context_layer.context_cli backfill
python -m context_layer.context_cli status
python reports\weekly_report.py
python reports\open_items.py
```

The included `samples/` folder has two linked notes so you can see entities, lineage
(an action item closing across the two weeks), quality, and the rollup work end to end.
Then point `artifacts_dirs` at your real notes folder.

## Commands

| Command | Purpose |
|---|---|
| `python -m context_layer.context_cli daily` | Incremental index of new/changed notes + quality + Monday rollup. Fast, idempotent. |
| `python -m context_layer.context_cli backfill` | Full rebuild from the whole notes folder. |
| `python -m context_layer.context_cli backfill --reset` | Clean rebuild (clears the derived store; keeps corrections, reports, rollups). |
| `python -m context_layer.context_cli quality` | Completeness + drift report. |
| `python -m context_layer.context_cli rollup` | Weekly rollup on demand. |
| `python -m context_layer.context_cli status` | Entity counts by type. |
| `python -m context_layer.context_cli correction --trigger ... --pattern ... --decision ... --rule ... --scope ...` | Record a norms rule. |

## Note format (what Stage 2 parses)

Stage 2 reads markdown notes named `<Name>__<YYYY-MM-DD>__<Workstream>.md` with these
section headings: Summary / Overview, Decisions, Action Items, Open Questions / Risks, Links,
and (for digests) message blocks under `## Messages` with `### <Subject>` headings. See
`samples/` for the exact shape. Action items parse best as
`Owner - action - YYYY-MM-DD - status`.

## Data and privacy

- `config.json` and `store/` are gitignored. No project data is committed.
- Stage 1 reads your M365 signals and writes local notes only. Stage 2 touches only local files.
- Configure what is collected via `seed_terms` and the tracked-meeting list in your own setup.

## Configuration

Copy `context_layer/config.example.json` to `context_layer/config.json` and edit the paths,
`seed_terms`, `systems`, and optional workflow `stage_keywords` / `stage_names`. See the agent
definition `project-context-layer.agent.md` for the full field reference.

## License

MIT. See `LICENSE`.
