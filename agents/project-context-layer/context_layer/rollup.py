"""rollup.py - weekly compaction and week-over-week diff.

Compacts the past 7 days of the store into one object the Weekly Update and RAID
Review agents can read instead of re-reading dozens of artifacts. Also diffs
against the prior week's rollup to surface what changed.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from . import store


def _isoweek(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def _recent(entities, days):
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    return [e for e in entities if (e.get("last_seen") or "") >= cutoff]


def build_rollup(cfg: dict) -> dict:
    sd = store.store_dir(cfg)
    entities = store.read_jsonl(sd / "entities.jsonl")
    week = _isoweek(date.today())
    recent = _recent(entities, 7)

    open_ai = [e for e in entities if e["type"] == "action_item" and e.get("status") not in {"closed", "superseded"}]
    decisions_wk = [e for e in recent if e["type"] == "decision"]
    risks_active = [e for e in entities if e["type"] == "risk" and e.get("status") not in {"closed", "resolved"}]

    stage_activity = {}
    for e in recent:
        st = e.get("stage")
        if st:
            stage_activity[str(st)] = stage_activity.get(str(st), 0) + 1

    def slim(e):
        return {
            "id": e["id"], "title": e["title"], "status": e.get("status"),
            "due": e.get("due"), "stage": e.get("stage"), "systems": e.get("systems", []),
            "confidence": e.get("confidence"), "first_seen": e.get("first_seen"),
            "last_seen": e.get("last_seen"),
        }

    rollup = {
        "week": week,
        "generated": store.now_iso(),
        "counts": {
            "open_action_items": len(open_ai),
            "decisions_this_week": len(decisions_wk),
            "active_risks": len(risks_active),
        },
        "open_action_items": [slim(e) for e in sorted(open_ai, key=lambda x: x.get("due") or "9999")],
        "decisions_this_week": [slim(e) for e in decisions_wk],
        "active_risks": [slim(e) for e in risks_active],
        "stage_activity": stage_activity,
        "changed_vs_last_week": _diff_prev(sd, week, open_ai, decisions_wk, risks_active),
    }

    out_json = sd / "rollups" / f"weekly_{week}.json"
    store.write_json(out_json, rollup)
    md = _render_md(cfg, rollup)
    out_md = sd / "rollups" / f"weekly_{week}.md"
    out_md.write_text(md, encoding="utf-8")
    _mirror(cfg, out_md)
    _mirror(cfg, out_json)
    return {"week": week, "json": str(out_json), "md": str(out_md), "counts": rollup["counts"]}


def _diff_prev(sd: Path, week: str, open_ai, decisions_wk, risks_active) -> dict:
    prev_files = [p for p in sorted((sd / "rollups").glob("weekly_*.json"))
                  if p.stem != f"weekly_{week}"]
    if not prev_files:
        return {"new_action_items": len(open_ai), "note": "first rollup, no prior week"}
    prev = store.read_json(prev_files[-1])
    prev_ai_ids = {a["id"] for a in prev.get("open_action_items", [])}
    prev_risk_ids = {r["id"] for r in prev.get("active_risks", [])}
    now_ai_ids = {a["id"] for a in open_ai}
    new_ai = now_ai_ids - prev_ai_ids
    closed_ai = prev_ai_ids - now_ai_ids
    new_risks = {r["id"] for r in risks_active} - prev_risk_ids
    return {
        "compared_to": prev.get("week"),
        "new_action_items": len(new_ai),
        "closed_or_dropped_action_items": len(closed_ai),
        "new_decisions": len(decisions_wk),
        "new_risks": len(new_risks),
    }


def _render_md(cfg: dict, r: dict) -> str:
    names = cfg.get("stage_names", {})
    lines = [
        f"# Weekly Context Rollup - {r['week']}",
        "",
        f"- Open action items: {r['counts']['open_action_items']}",
        f"- Decisions this week: {r['counts']['decisions_this_week']}",
        f"- Active risks: {r['counts']['active_risks']}",
        "",
        "## What changed vs last week",
    ]
    d = r["changed_vs_last_week"]
    if "note" in d:
        lines.append(f"- {d['note']}")
    else:
        lines += [
            f"- Compared to {d.get('compared_to')}",
            f"- New action items: {d.get('new_action_items')}",
            f"- Closed / dropped action items: {d.get('closed_or_dropped_action_items')}",
            f"- New decisions: {d.get('new_decisions')}",
            f"- New risks: {d.get('new_risks')}",
        ]
    lines += ["", "## Open action items (by due date)"]
    for a in r["open_action_items"]:
        due = a.get("due") or "no due date"
        lines.append(f"- {a['title']} (due {due}, {a.get('confidence')})")
    lines += ["", "## Decisions this week"]
    for a in r["decisions_this_week"]:
        lines.append(f"- {a['title']}")
    lines += ["", "## Active risks"]
    for a in r["active_risks"]:
        lines.append(f"- {a['title']}")
    lines += ["", "## AEM stage activity"]
    for st, ct in sorted(r["stage_activity"].items()):
        lines.append(f"- Stage {st} ({names.get(st, '')}): {ct} items")
    lines += ["", f"_Generated {r['generated']}_"]
    return "\n".join(lines)


def _mirror(cfg: dict, path: Path) -> None:
    mirror = cfg.get("mirror_dir")
    if not mirror:
        return
    try:
        dest = Path(mirror)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / path.name).write_bytes(path.read_bytes())
    except Exception as exc:
        print(f"  mirror skipped: {exc}")
