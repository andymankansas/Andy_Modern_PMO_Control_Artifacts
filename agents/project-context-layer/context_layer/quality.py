"""quality.py - completeness + drift checks over the store.

Emits a dated report plus a single-line health summary the monitor prints in its
run summary. Completeness looks for facts that are missing required detail; drift
compares recent seed-term / stage activity against a trailing baseline.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from . import store


def _recent(entities, days, field="last_seen"):
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    return [e for e in entities if (e.get(field) or "") >= cutoff]


def run_quality(cfg: dict) -> dict:
    sd = store.store_dir(cfg)
    entities = store.read_jsonl(sd / "entities.jsonl")

    issues: list[str] = []
    ai = [e for e in entities if e["type"] == "action_item"]
    open_ai = [e for e in ai if e.get("status") not in {"closed", "superseded"}]
    no_owner = [e for e in open_ai if not e.get("owner_ref")]
    no_due = [e for e in open_ai if not e.get("due")]
    dec_no_rat = [e for e in entities if e["type"] == "decision" and not e.get("has_rationale", True)]
    risks_no_status = [e for e in entities if e["type"] == "risk" and not e.get("status")]
    stubs = [e for e in entities if e["type"] == "meeting" and (e.get("confidence") == "low")]

    if no_owner:
        issues.append(f"{len(no_owner)} open action items missing an owner")
    if no_due:
        issues.append(f"{len(no_due)} open action items missing a due date")
    if dec_no_rat:
        issues.append(f"{len(dec_no_rat)} decisions missing rationale")
    if risks_no_status:
        issues.append(f"{len(risks_no_status)} risks missing status")
    if stubs:
        issues.append(f"{len(stubs)} meetings captured as low-confidence stubs")

    # Overdue open action items
    today = date.today().isoformat()
    overdue = [e for e in open_ai if e.get("due") and re.match(r"\d{4}-\d{2}-\d{2}", e["due"]) and e["due"] < today]
    if overdue:
        issues.append(f"{len(overdue)} open action items are past due")

    # Drift: system mention frequency recent vs baseline
    baseline_days = cfg.get("drift_baseline_days", 14)
    recent = _recent(entities, 3)
    base = _recent(entities, baseline_days)
    drift: list[str] = []

    def sys_counts(items):
        c = Counter()
        for e in items:
            for s in e.get("systems", []):
                c[s] += 1
        return c

    rc, bc = sys_counts(recent), sys_counts(base)
    for sysname in cfg.get("systems", []):
        base_rate = bc.get(sysname, 0) / max(baseline_days, 1)
        recent_rate = rc.get(sysname, 0) / 3.0
        if base_rate >= 1 and recent_rate == 0:
            drift.append(f'"{sysname}" mentions went silent vs {baseline_days}-day baseline')
        elif base_rate > 0 and recent_rate > 3 * base_rate and rc.get(sysname, 0) >= 3:
            drift.append(f'"{sysname}" mentions surging vs baseline')

    penalty = min(60, 4 * len(issues) + 3 * len(drift))
    score = max(0, 100 - penalty)

    report_lines = [
        f"# Context Health Report - {today}",
        "",
        f"**Score:** {score}/100",
        "",
        f"- Entities total: {len(entities)}",
        f"- Open action items: {len(open_ai)} ({len(overdue)} overdue)",
        "",
        "## Completeness issues",
    ]
    report_lines += [f"- {i}" for i in issues] or ["- None"]
    report_lines += ["", "## Drift flags"]
    report_lines += [f"- {d}" for d in drift] or ["- None"]
    report_lines.append("")
    report_lines.append(f"_Generated {store.now_iso()}_")
    report = "\n".join(report_lines)

    out = sd / "quality" / f"quality_report_{today}.md"
    out.write_text(report, encoding="utf-8")
    _mirror(cfg, out)

    one_line = f"Context health: {score}/100"
    if issues:
        one_line += ". " + issues[0]
    if drift:
        one_line += ". Drift: " + drift[0]
    return {"score": score, "issues": issues, "drift": drift, "summary": one_line, "report": str(out)}


def _mirror(cfg: dict, path: Path) -> None:
    mirror = cfg.get("mirror_dir")
    if not mirror:
        return
    try:
        dest = Path(mirror)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception as exc:
        print(f"  mirror skipped: {exc}")
