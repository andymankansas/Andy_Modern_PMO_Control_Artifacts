"""draft_wbr.py - Stage 1 of the WBR agent: draft, then review.

Reads the prior week's deck (read-only), the weekly input file, and the Project
Context Layer knowledge base, then writes a content plan and a gaps report for
review. No deck is written here; generation happens in generate_wbr.py after the
plan is approved.

Usage (from the extracted package folder):
    python draft_wbr.py --input weekly_input.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import wbr_lib as lib  # noqa: E402
from pptx import Presentation  # noqa: E402


def kb_digest(cfg: dict) -> dict:
    """Pull a week-over-week change digest from the Project Context Layer, if present.

    Set knowledge_base.context_layer_path in wbr_config.json to the folder of an
    installed Project Context Layer agent to enable this. Left blank, the digest
    is skipped and the agent relies on the weekly input file.
    """
    kb_cfg = (cfg.get("knowledge_base") or {})
    cl_path = (kb_cfg.get("context_layer_path") or "").strip()
    if cl_path:
        p = Path(cl_path)
        if not p.is_absolute():
            p = (HERE / cl_path).resolve()
        sys.path.insert(0, str(p))
    try:
        from context_layer import query, store
    except Exception as exc:  # KB is optional
        return {"available": False, "reason": str(exc)}

    cfg = store.load_config()
    sd = store.store_dir(cfg)
    rollups = sorted((sd / "rollups").glob("weekly_*.json"))
    latest = store.read_json(rollups[-1]) if rollups else {}
    overdue = query.overdue_action_items(cfg)
    risks = query.active_risks(cfg)
    return {
        "available": True,
        "week": latest.get("week"),
        "counts": latest.get("counts", {}),
        "changed_vs_last_week": latest.get("changed_vs_last_week", {}),
        "decisions_this_week": [d.get("title") for d in latest.get("decisions_this_week", [])][:12],
        "overdue_action_items": [a.get("title") for a in overdue][:12],
        "active_risk_sample": [r.get("title") for r in risks][:12],
    }


def resolve_prior_deck(cfg: dict, weekly: dict) -> Path:
    raw = (weekly.get("prior_deck") or "").strip()
    if not raw:
        return Path(cfg["deck_dir"]) / cfg["baseline_deck"]
    p = Path(raw)
    return p if p.is_absolute() else Path(cfg["deck_dir"]) / raw


def build_plan(cfg: dict, weekly: dict) -> dict:
    prior = resolve_prior_deck(cfg, weekly)
    prs = Presentation(str(prior))
    detected = lib.detect_report_week(prs, cfg["subtitle"]["slide"], cfg["subtitle"]["shape"])

    rw = weekly["report_week"]
    start, end = lib.parse_date(rw["start"]), lib.parse_date(rw["end"])
    mw = weekly.get("metrics_week") or {}
    out_name = lib.output_filename(cfg["output_pattern"], start, end)

    gaps: list[str] = []
    programs = weekly.get("programs", {})
    for prog in cfg["programs"]:
        entry = programs.get(prog["key"], {})
        rag = (entry.get("rag") or "").strip()
        if rag and rag not in cfg["rag_values"]:
            gaps.append(f"Program '{prog['key']}' RAG '{rag}' is not one of {cfg['rag_values']}.")

    metrics = weekly.get("metrics") or {}
    if metrics.get("current") and any(metrics["current"].values()):
        missing = [k for k, v in metrics["current"].items() if not str(v).strip()]
        if missing:
            gaps.append(f"Support metrics current week missing: {', '.join(missing)}.")
    if not mw:
        gaps.append("No metrics_week provided; slide 9 date labels will be unchanged.")

    return {
        "prior_deck": str(prior),
        "prior_exists": prior.exists(),
        "detected_week": (lib.week_forms(*detected) if detected else None),
        "target_week": lib.week_forms(start, end),
        "output_filename": out_name,
        "metrics_week": mw,
        "programs": programs,
        "gaps": gaps,
        "kb": kb_digest(cfg),
    }


def render_plan_md(cfg: dict, plan: dict) -> str:
    lines = [
        f"# WBR Content Plan - {plan['target_week']['long']}",
        "",
        f"- Profile: {cfg['profile']}",
        f"- Prior deck: {plan['prior_deck']} (exists: {plan['prior_exists']})",
    ]
    if plan["detected_week"]:
        lines.append(f"- Detected prior reporting week: "
                     f"{plan['detected_week']['slash'].replace(lib.EN_DASH, 'to')}")
    lines += [
        f"- New reporting week: {plan['target_week']['slash'].replace(lib.EN_DASH, 'to')}",
        f"- Output filename: {plan['output_filename']}",
        "",
        "## Program status (proposed)",
    ]
    for prog in cfg["programs"]:
        entry = plan["programs"].get(prog["key"], {})
        rag = entry.get("rag") or "(unchanged)"
        body = "updated" if (entry.get("body") or "").strip() else "carried forward"
        lines.append(f"- {prog['key']}: RAG {rag}; narrative {body}")

    kb = plan["kb"]
    lines += ["", "## Knowledge base change digest"]
    if not kb.get("available"):
        lines.append("- Optional knowledge base not connected; skipping the change digest. "
                     "Fill the weekly input file directly.")
    else:
        c = kb.get("counts", {})
        d = kb.get("changed_vs_last_week", {})
        lines += [
            f"- Rollup week: {kb.get('week')}",
            f"- Open action items: {c.get('open_action_items')}; active risks: {c.get('active_risks')}",
            f"- WoW: +{d.get('new_action_items', 0)} new / "
            f"{d.get('closed_or_dropped_action_items', 0)} closed actions, "
            f"+{d.get('new_decisions', 0)} decisions, +{d.get('new_risks', 0)} risks",
            "",
            "### Decisions this week (review for slides)",
        ]
        lines += [f"- {t}" for t in kb.get("decisions_this_week", [])] or ["- (none)"]
        lines += ["", "### Overdue action items (risk candidates)"]
        lines += [f"- {t}" for t in kb.get("overdue_action_items", [])] or ["- (none)"]

    lines += ["", "## Gaps to resolve before generating"]
    lines += [f"- {g}" for g in plan["gaps"]] or ["- None."]
    lines += ["", "## Next step",
              "Review this plan, complete the weekly input file, then run generate_wbr.py."]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="draft_wbr")
    ap.add_argument("--input", required=True, help="Path to weekly_input.json")
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)

    cfg = lib.load_config(args.config)
    weekly = lib.load_weekly_input(args.input)
    plan = build_plan(cfg, weekly)

    start = lib.parse_date(weekly["report_week"]["start"])
    end = lib.parse_date(weekly["report_week"]["end"])
    slug = lib.output_filename("{start_month}-{start_day}-{end_label}-{year}", start, end)
    slug = slug.replace(" ", "-")
    out_dir = HERE / "drafts" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "content-plan.md").write_text(render_plan_md(cfg, plan), encoding="utf-8")
    from json import dumps
    (out_dir / "gaps.json").write_text(dumps(plan["gaps"], indent=2), encoding="utf-8")

    print(f"Draft written: {out_dir / 'content-plan.md'}")
    if plan["gaps"]:
        print(f"Gaps ({len(plan['gaps'])}):")
        for g in plan["gaps"]:
            print(f"  - {g}")
    else:
        print("No gaps flagged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
