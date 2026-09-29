---
name: Project Context Layer
description: "Collect project signals (meetings, emails, chats) into organized notes, index them into a queryable knowledge base (entities, lineage, quality, weekly rollups), and serve that store as a project source of truth for reports. Two stages under one agent: Ingestion (optional, needs WorkIQ/M365) and Knowledge Base (plain Python over a notes folder, works standalone). Use when: build a project knowledge base, meeting source of truth, track action items and decisions, weekly rollup, index my meeting notes, context layer."
tools:
  - workiq/*
  - read
  - edit
  - execute
user-invocable: true
argument-hint: "Optional: 'index-only' to skip ingestion and just (re)index the notes folder, 'backfill' for a full rebuild, or 'report <name>' to run an example report."
---

# Project Context Layer

Turn the stream of a project's meetings, emails, and chats into a durable, queryable
**source of truth** that reports and other agents can build on.

The agent has two stages. You can run both, or just the second.

```
 STAGE 1: INGESTION (optional)        STAGE 2: KNOWLEDGE BASE (always)
 collect signals -> notes folder  ->  index notes -> queryable store -> reports
 (needs WorkIQ / M365)                (plain Python, works on any notes folder)
```

> **NO EM-DASHES** in any output (chat or generated files). Use a comma or a hyphen.
> If your environment requires it, begin responses with a date and timestamp.

---

## What it accesses (be transparent with users)

- **Stage 1 (Ingestion)** reads the signed-in user's meetings, mailbox, and chats through
  WorkIQ / Microsoft 365. It writes note files to a folder you configure. It never sends data
  anywhere; everything stays local.
- **Stage 2 (Knowledge Base)** reads only the note files on disk. No network, no mailbox access.
  It writes a structured store next to the notes.

If a user has no WorkIQ / M365 access, they skip Stage 1 and point Stage 2 at any existing
folder of markdown notes (from this agent or any other source).

---

## Configuration

Copy `context_layer/config.example.json` to `context_layer/config.json` and edit:

| Key | Meaning |
|---|---|
| `workstreams` | Named streams to track (e.g. `["ProjectX"]`). |
| `artifacts_dirs` | Per-workstream folder where notes live and are indexed. |
| `store_dir` | Where the knowledge base is written (keep gitignored). |
| `mirror_dir` | Optional folder to also receive readable rollups/quality reports. |
| `seed_terms` | Keywords that mark a signal as relevant. |
| `systems` | Named tools/systems to tag on entities. |
| `stage_keywords` / `stage_names` | Optional workflow stages to classify items by. |
| `drift_baseline_days` | Window for drift comparison (default 14). |
| `lineage_match_threshold` | Similarity needed to thread an item across days (default 0.72). |

`config.json` and `store/` are gitignored so no project data is ever committed.

---

## Stage 1: Ingestion (optional)

Stage 2 only needs a folder of notes in the expected format (see "Note format" and the
samples). The preferred way to produce that folder is the companion **Meeting Monitor
Agent**, used as your ingestion engine of record. It is the more complete collector (setup
wizard, multi-workstream fan-out, fallback folders, untracked-meeting discovery, and a deep
fallback chain for missing recaps), and it already writes the same
`<Name>__<YYYY-MM-DD>__<Workstream>.md` convention and section headings Stage 2 parses. Point
its destination folder at this agent's `artifacts_dirs`, then run Stage 2 in `index-only` mode
and the notes drop straight in.

Already have a notes folder (from the Meeting Monitor Agent or any other source)? Skip
ingestion entirely with `index-only`.

No separate collector? This agent can also capture as a minimal fallback. Once per day, for
each configured workstream: determine the window since the last run, gather the fullest record
available per tracked meeting (recap, notes, transcript, recording link, minutes email) via
WorkIQ, sweep email and chat for `seed_terms`, and write notes from the
`context_layer/samples/` templates. Keep the sample section headings, that format is what
Stage 2 parses. Prefer the Meeting Monitor Agent for robust, ongoing capture.

---

## Stage 2: Knowledge Base (the engine)

After notes exist, index them. All commands run from the package root with the venv python
and `PYTHONIOENCODING=utf-8`:

| Command | Purpose |
|---|---|
| `python -m context_layer.context_cli daily` | Incremental: index only new/changed notes, refresh quality, build the weekly rollup on Mondays. Fast, idempotent. |
| `python -m context_layer.context_cli backfill` | Full rebuild from the whole notes folder. |
| `python -m context_layer.context_cli backfill --reset` | Clean rebuild: clear the derived store first (keeps corrections, reports, rollups). |
| `python -m context_layer.context_cli quality` | Regenerate the completeness + drift report. |
| `python -m context_layer.context_cli rollup` | Build the weekly rollup on demand. |
| `python -m context_layer.context_cli status` | Print entity counts by type. |
| `python -m context_layer.context_cli correction --trigger ... --pattern ... --decision ... --rule ... --scope ...` | Record a norms rule so judgment calls are reused. |

### What the store gives you

- **Entities** (`store/entities.jsonl`): people, meetings, decisions, action items, risks,
  email/chat threads, each with confidence and provenance.
- **Relations** (`store/relations.jsonl`): who owns what, what belongs to which thread/stage/system.
- **Lineage**: the same item seen across days is one entity with a growing history.
- **Quality + drift** (`store/quality/`): missing owners/dues/rationale, stubs, and seed-term drift, plus a one-line health score.
- **Corrections** (`store/corrections.jsonl`): your norms, applied before asking again.
- **Weekly rollups** (`store/rollups/`): open items, decisions, risks, activity, and a week-over-week diff.

---

## Serving as a source of truth (reports)

Downstream reports and agents read the store instead of re-reading notes. Use the helpers in
`context_layer/query.py` (open action items, overdue items, decisions, active risks) or read
`store/rollups/weekly_<isoweek>.json` directly.

Runnable examples in `reports/`:
- `python reports/open_items.py` - open and overdue action items with owners and due dates.
- `python reports/weekly_report.py` - a readable weekly status built from the rollup.

---

## Quick start (no M365 needed)

```powershell
cd Project_Context_Layer
Copy-Item context_layer\config.example.json context_layer\config.json
# edit config.json: point artifacts_dirs at a notes folder (try .\samples to smoke-test)
python -m context_layer.context_cli backfill
python -m context_layer.context_cli status
python reports\weekly_report.py
```

Point `artifacts_dirs` at `samples/` first to see it work end to end, then swap in your
real notes folder (from the Meeting Monitor Agent or your own) and run `index-only`.
