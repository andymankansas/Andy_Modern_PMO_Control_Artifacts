"""Catalog project artifacts for a walking deck (read-only).

Scans one or more folders and classifies files into artifact types the agent
uses to ground the deck (SOW, meeting notes, recordings, prior decks, plans,
RAID logs, org/stakeholder lists, brand assets). Writes an intake manifest JSON
listing what was found and flags recordings that can be transcribed.

Usage:
    python scripts/intake.py --folders "C:/proj/docs" "C:/proj/recordings" --out output/intake_manifest.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

CLASSIFIERS = [
    ("recording", {".mp4", ".m4a", ".wav", ".mov", ".mp3"}, ()),
    ("prior_deck", {".pptx", ".ppt", ".key"}, ()),
    ("sow", set(), ("sow", "statement of work", "contract", "msa", "order form")),
    ("charter", set(), ("charter", "vision", "brief", "kickoff", "kick-off")),
    ("plan", set(), ("plan", "roadmap", "timeline", "workback", "schedule", "milestone")),
    ("raid", set(), ("raid", "risk", "issue", "decision", "action")),
    ("meeting_notes", set(), ("notes", "recap", "minutes", "standup", "sync", "meeting")),
    ("org", set(), ("org", "raci", "stakeholder", "roster", "team")),
    ("brand", {".svg", ".png", ".ai", ".eps"}, ("logo", "brand", "palette")),
    ("data", {".xlsx", ".xls", ".csv"}, ()),
    ("doc", {".docx", ".doc", ".pdf", ".md", ".txt"}, ()),
]


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    name = path.name.lower()
    for label, exts, keywords in CLASSIFIERS:
        if exts and ext in exts:
            if keywords and not any(k in name for k in keywords):
                if label in ("brand",):
                    continue
            return label
        if keywords and any(k in name for k in keywords):
            return label
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description="Catalog project artifacts for the walking deck (read-only).")
    parser.add_argument("--folders", nargs="+", required=True, help="Folders to scan")
    parser.add_argument("--out", default="output/intake_manifest.json", help="Manifest output path")
    parser.add_argument("--max-depth", type=int, default=4, help="Recursion depth limit")
    args = parser.parse_args()

    items = []
    for folder in args.folders:
        root = Path(folder)
        if not root.exists():
            print(f"Skip (not found): {root}")
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if len(p.relative_to(root).parts) > args.max_depth:
                continue
            if p.name.startswith("~$") or p.suffix.lower() == ".tmp":
                continue
            kind = classify(p)
            items.append({
                "path": str(p),
                "name": p.name,
                "type": kind,
                "size_kb": round(p.stat().st_size / 1024, 1),
                "modified": dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
                "transcribable": kind == "recording",
            })

    items.sort(key=lambda x: (x["type"], x["name"].lower()))
    by_type: dict[str, int] = {}
    for it in items:
        by_type[it["type"]] = by_type.get(it["type"], 0) + 1

    manifest = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "folders": args.folders,
        "counts": by_type,
        "recordings_to_transcribe": [i["path"] for i in items if i["transcribable"]],
        "items": items,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Cataloged {len(items)} artifacts -> {out}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")
    if manifest["recordings_to_transcribe"]:
        print("Recordings can be transcribed with scripts/transcribe.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
