"""context_cli.py - single entry point for the Project Context Layer.

Usage (from repo root, with the venv python):
    python -m context_layer.context_cli backfill        # extract+merge all artifacts
    python -m context_layer.context_cli build <file...>  # extract+merge specific .md files
    python -m context_layer.context_cli link             # re-run lineage over the store
    python -m context_layer.context_cli quality          # completeness + drift report
    python -m context_layer.context_cli rollup           # weekly rollup + diff
    python -m context_layer.context_cli daily            # build(new) + quality + (Mon) rollup
    python -m context_layer.context_cli status           # quick store summary
    python -m context_layer.context_cli correction ...   # append a norms rule
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import corrections, merge, quality, rollup, store


def _cfg(args):
    return store.load_config(getattr(args, "config", None))


def cmd_backfill(args):
    cfg = _cfg(args)
    if getattr(args, "reset", False):
        removed = merge.reset_store(cfg)
        print(f"Reset: cleared {removed} store file(s) for a clean rebuild.")
    stats = merge.backfill(cfg)
    print(f"Backfill: {stats['artifacts']} artifacts, "
          f"{stats['created']} entities created, {stats['linked']} linked.")


def cmd_build(args):
    cfg = _cfg(args)
    sd = store.store_dir(cfg)
    written = []
    from . import extract
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"  missing: {f}")
            continue
        sc = extract.extract_file(p, cfg)
        out = sd / "sidecars" / (p.stem + ".entities.json")
        store.write_json(out, sc)
        written.append(out)
    stats = merge.merge_files(written, cfg)
    print(f"Build: {len(written)} files, {stats['created']} created, {stats['linked']} linked.")


def cmd_link(args):
    cfg = _cfg(args)
    sd = store.store_dir(cfg)
    sidecars = sorted((sd / "sidecars").glob("*.entities.json"))
    # rebuild the store from scratch to re-thread lineage deterministically
    (sd / "entities.jsonl").unlink(missing_ok=True)
    (sd / "relations.jsonl").unlink(missing_ok=True)
    stats = merge.merge_files(sidecars, cfg)
    print(f"Relinked from {len(sidecars)} sidecars: {stats['created']} created, {stats['linked']} linked.")


def cmd_quality(args):
    cfg = _cfg(args)
    res = quality.run_quality(cfg)
    print(res["summary"])
    print(f"Report: {res['report']}")


def cmd_rollup(args):
    cfg = _cfg(args)
    res = rollup.build_rollup(cfg)
    print(f"Rollup {res['week']}: {res['counts']}")
    print(f"MD: {res['md']}")


def cmd_daily(args):
    cfg = _cfg(args)
    # Incremental: only new/changed artifacts are extracted+merged (idempotent
    # thanks to dedupe + lineage). Use `backfill` for a full rebuild.
    stats = merge.incremental(cfg)
    print(f"Daily merge: {stats['artifacts']} new/changed of {stats['scanned']} scanned, "
          f"{stats['created']} created, {stats['linked']} linked.")
    q = quality.run_quality(cfg)
    print(q["summary"])
    if date.today().weekday() == 0 or args.force_rollup:
        r = rollup.build_rollup(cfg)
        print(f"Weekly rollup {r['week']} built.")


def cmd_status(args):
    cfg = _cfg(args)
    sd = store.store_dir(cfg)
    ents = store.read_jsonl(sd / "entities.jsonl")
    by_type = {}
    for e in ents:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    print(f"Store: {sd}")
    print(f"Entities: {len(ents)}")
    for t in sorted(by_type):
        print(f"  {t}: {by_type[t]}")


def cmd_correction(args):
    cfg = _cfg(args)
    rec = corrections.add_correction(cfg, args.trigger, args.pattern,
                                     args.decision, args.rule, args.scope)
    print(f"Correction saved: {rec['rule']}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="context_cli")
    p.add_argument("--config", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    bf = sub.add_parser("backfill")
    bf.add_argument("--reset", action="store_true",
                    help="Delete entities/relations/sidecars/manifest first for a clean rebuild.")
    bf.set_defaults(func=cmd_backfill)

    b = sub.add_parser("build")
    b.add_argument("files", nargs="+")
    b.set_defaults(func=cmd_build)

    sub.add_parser("link").set_defaults(func=cmd_link)
    sub.add_parser("quality").set_defaults(func=cmd_quality)
    sub.add_parser("rollup").set_defaults(func=cmd_rollup)
    sub.add_parser("status").set_defaults(func=cmd_status)

    d = sub.add_parser("daily")
    d.add_argument("--force-rollup", action="store_true")
    d.set_defaults(func=cmd_daily)

    c = sub.add_parser("correction")
    c.add_argument("--trigger", required=True)
    c.add_argument("--pattern", required=True)
    c.add_argument("--decision", required=True)
    c.add_argument("--rule", required=True)
    c.add_argument("--scope", default="global")
    c.set_defaults(func=cmd_correction)

    args = p.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
