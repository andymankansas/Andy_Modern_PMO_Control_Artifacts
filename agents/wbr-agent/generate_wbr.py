"""generate_wbr.py - Stage 2 of the WBR agent: generate the dated deck.

Copies the prior week's deck to a new dated file, rolls all dates forward, and
applies the approved edits from the weekly input file (RAG, program narratives,
risk register, priorities, timeline stamp, reporting slide, support metrics).
Slides configured under leave_as_is_slides are never touched. Writes a
validation report alongside the deck.

Usage (from the extracted package folder):
    python generate_wbr.py --input weekly_input.json
    python generate_wbr.py --input weekly_input.json --out-dir ./test-output
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import wbr_lib as lib  # noqa: E402
from pptx import Presentation  # noqa: E402


def resolve_prior_deck(cfg: dict, weekly: dict) -> Path:
    raw = (weekly.get("prior_deck") or "").strip()
    if not raw:
        return Path(cfg["deck_dir"]) / cfg["baseline_deck"]
    p = Path(raw)
    return p if p.is_absolute() else Path(cfg["deck_dir"]) / raw


def roll_dates(prs, cfg, weekly, log):
    detected = lib.detect_report_week(prs, cfg["subtitle"]["slide"], cfg["subtitle"]["shape"])
    start = lib.parse_date(weekly["report_week"]["start"])
    end = lib.parse_date(weekly["report_week"]["end"])
    new = lib.week_forms(start, end)
    if detected:
        old = lib.week_forms(*detected)
        n_slash = lib.replace_text_everywhere(prs, old["slash"], new["slash"])
        n_long = lib.replace_text_everywhere(prs, old["week_of_long"], new["week_of_long"])
        n_long += lib.replace_text_everywhere(prs, old["long"], new["long"])
        log.append(f"Reporting week {old['slash']} -> {new['slash']} "
                   f"({n_slash} slash, {n_long} long occurrences).")
    else:
        log.append("WARNING: prior reporting week not detected; dates left unchanged.")

    mw = weekly.get("metrics_week") or {}
    if mw.get("start") and mw.get("end"):
        ms, me = lib.parse_date(mw["start"]), lib.parse_date(mw["end"])
        mf = lib.metrics_forms(ms, me)
        ms_slide = lib.slide_at(prs, cfg["metrics_slide"]["slide"])
        title = lib.find_shape(ms_slide, cfg["metrics_slide"]["title_shape"])
        if title is not None:
            import re
            txt = title.text_frame.text
            new_txt = re.sub(r"\d{2}/\d{2}/\d{4}-\s*\d{2}/\d{2}/\d{4}", mf["slash"], txt)
            lib.set_text(title, new_txt)
            log.append(f"Metrics title range -> {mf['slash']}.")
        wk = lib.find_shape(ms_slide, cfg["metrics_slide"]["week_label_shape"])
        if wk is not None:
            lib.set_text(wk, f"{mf['week_start']}\n-\n{mf['week_end']}")
            log.append("Metrics week label updated.")


def apply_programs(prs, cfg, weekly, log):
    programs = weekly.get("programs", {})
    rag_colors = cfg.get("rag_colors", {})
    for prog in cfg["programs"]:
        entry = programs.get(prog["key"], {})
        slide = lib.slide_at(prs, prog["slide"])
        rag = (entry.get("rag") or "").strip()
        if rag:
            shp = lib.find_shape(slide, prog["rag_shape"])
            if shp is not None:
                lib.set_text(shp, rag)
            fill_shape = lib.find_shape(slide, prog.get("rag_fill_shape", ""))
            if fill_shape is not None and rag in rag_colors:
                lib.set_fill(fill_shape, rag_colors[rag])
            log.append(f"{prog['key']} RAG -> {rag}.")
        body = entry.get("body") or ""
        if body.strip():
            shp = lib.find_shape(slide, prog["body_shape"])
            if shp is not None:
                lib.set_rich_text(shp, body)
                log.append(f"{prog['key']} narrative updated ({len(body)} chars).")


def apply_risks(prs, cfg, weekly, log):
    rows = ((weekly.get("risks") or {}).get("rows")) or []
    if not rows:
        return
    rt = cfg["risk_table"]
    slide = lib.slide_at(prs, rt["slide"])
    shape = lib.find_shape(slide, rt["shape"])
    if shape is None or not shape.has_table:
        log.append("WARNING: risk table not found; risks not applied.")
        return
    table = shape.table
    body_rows = len(table.rows) - rt["header_rows"]
    if len(rows) > body_rows:
        log.append(f"WARNING: {len(rows)} risk rows provided but table has {body_rows}; "
                   f"extra rows ignored (cannot add rows in place).")
    cols = rt["columns"]
    sev_colors = cfg.get("severity_colors", {})
    neutral = cfg.get("neutral_fill", "FFFFFF")
    cleared = 0
    for i in range(body_rows):
        r_index = i + rt["header_rows"]
        if i < len(rows):
            data = rows[i]
            for c_index, col in enumerate(cols):
                lib.set_cell_text(table.cell(r_index, c_index), data.get(col, ""))
            sev = str(data.get("severity", "")).strip().upper()
            if sev in sev_colors:
                lib.set_fill(table.cell(r_index, 0), sev_colors[sev])
        else:
            for c_index in range(len(cols)):
                lib.set_cell_text(table.cell(r_index, c_index), "")
            lib.set_fill(table.cell(r_index, 0), neutral)
            cleared += 1
    msg = f"Risk register updated ({min(len(rows), body_rows)} rows"
    msg += f", {cleared} trailing rows cleared)." if cleared else ")."
    log.append(msg)


def apply_priorities(prs, cfg, weekly, log):
    items = ((weekly.get("priorities") or {}).get("items")) or []
    if not items:
        return
    pt = cfg["priorities_table"]
    slide = lib.slide_at(prs, pt["slide"])
    shape = lib.find_shape(slide, pt["shape"])
    if shape is None or not shape.has_table:
        log.append("WARNING: priorities table not found; priorities not applied.")
        return
    table = shape.table
    body_rows = min(len(table.rows) - pt["header_rows"], pt["max_rows"])
    for i in range(body_rows):
        r_index = i + pt["header_rows"]
        text = items[i] if i < len(items) else ""
        lib.set_cell_text(table.cell(r_index, pt["text_col"]), text)
    log.append(f"Priorities updated ({min(len(items), body_rows)} items; "
               f"provide the full ranked list, trailing rows cleared).")


def apply_timeline(prs, cfg, weekly, log):
    tl = weekly.get("timeline") or {}
    cfg_tl = cfg["timeline_slide"]
    slide = lib.slide_at(prs, cfg_tl["slide"])
    updated = (tl.get("updated") or "").strip()
    if updated:
        d = lib.parse_date(updated)
        shp = lib.find_shape(slide, cfg_tl["updated_shape"])
        if shp is not None:
            lib.set_text(shp, f"Updated {d.month}/{d.day}/{d.year}")
            log.append("Timeline 'Updated' stamp refreshed.")
    for key, text in (tl.get("phases") or {}).items():
        shape_name = cfg_tl["phase_shapes"].get(key)
        if not shape_name:
            log.append(f"WARNING: timeline phase key '{key}' not in config; skipped.")
            continue
        shp = lib.find_shape(slide, shape_name)
        if shp is not None and str(text).strip():
            lib.set_rich_text(shp, text)
            log.append(f"Timeline phase '{key}' updated.")


def apply_reporting(prs, cfg, weekly, log):
    rep = weekly.get("reporting") or {}
    cfg_rep = cfg["reporting_slide"]
    slide = lib.slide_at(prs, cfg_rep["slide"])
    exec_summary = (rep.get("exec_summary") or "").strip()
    if exec_summary:
        shp = lib.find_shape(slide, cfg_rep["exec_shape"])
        if shp is not None:
            lib.set_text(shp, exec_summary)
            log.append("Reporting executive summary updated.")
    for i, deliv in enumerate(rep.get("deliverables") or []):
        if i >= len(cfg_rep["deliverables"]):
            break
        anchors = cfg_rep["deliverables"][i]
        name = (deliv.get("name") or "").strip()
        body = (deliv.get("body") or "").strip()
        if name:
            shp = lib.find_shape(slide, anchors["name_shape"])
            if shp is not None:
                lib.set_text(shp, name)
        if body:
            shp = lib.find_shape(slide, anchors["body_shape"])
            if shp is not None:
                lib.set_rich_text(shp, body)
        if name or body:
            log.append(f"Reporting deliverable {i + 1} updated.")


def apply_metrics(prs, cfg, weekly, log):
    metrics = weekly.get("metrics") or {}
    cfg_m = cfg["metrics_slide"]
    slide = lib.slide_at(prs, cfg_m["slide"])
    for bucket in ("current", "prior"):
        values = metrics.get(bucket) or {}
        for key, value in values.items():
            if not str(value).strip():
                continue
            shape_name = cfg_m[bucket].get(key)
            if not shape_name:
                continue
            shp = lib.find_shape(slide, shape_name)
            if shp is not None:
                lib.set_text(shp, str(value))
    insights = (metrics.get("insights") or "").strip()
    if insights:
        shp = lib.find_shape(slide, cfg_m["insights_shape"])
        if shp is not None:
            lib.set_text(shp, insights)
    if metrics.get("current") or metrics.get("prior") or insights:
        log.append("Support metrics updated.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="generate_wbr")
    ap.add_argument("--input", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default=None,
                    help="Override output folder (defaults to deck_dir). Use for testing.")
    args = ap.parse_args(argv)

    cfg = lib.load_config(args.config)
    weekly = lib.load_weekly_input(args.input)

    prior = resolve_prior_deck(cfg, weekly)
    if not prior.exists():
        print(f"ERROR: prior deck not found: {prior}")
        return 2

    start = lib.parse_date(weekly["report_week"]["start"])
    end = lib.parse_date(weekly["report_week"]["end"])
    out_name = lib.output_filename(cfg["output_pattern"], start, end)
    out_dir = Path(args.out_dir) if args.out_dir else Path(cfg["deck_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_name

    if out_path.resolve() == prior.resolve():
        print("ERROR: output path equals prior deck; refusing to overwrite the source.")
        return 2

    shutil.copy2(prior, out_path)
    prs = Presentation(str(out_path))

    log: list[str] = [f"Copied prior deck: {prior.name} -> {out_path.name}"]
    roll_dates(prs, cfg, weekly, log)
    apply_programs(prs, cfg, weekly, log)
    apply_risks(prs, cfg, weekly, log)
    apply_priorities(prs, cfg, weekly, log)
    apply_timeline(prs, cfg, weekly, log)
    apply_reporting(prs, cfg, weekly, log)
    apply_metrics(prs, cfg, weekly, log)
    lib.strip_highlights(prs)
    log.append(f"Left untouched: slides {cfg['leave_as_is_slides']}.")

    prs.save(str(out_path))

    report = out_path.with_suffix(".validation.md")
    report.write_text(
        "# WBR Generation Report - " + lib.week_forms(start, end)["long"] + "\n\n"
        + f"- Output: {out_path}\n\n## Actions\n"
        + "\n".join(f"- {line}" for line in log) + "\n",
        encoding="utf-8")

    print(f"Generated: {out_path}")
    print(f"Report: {report}")
    for line in log:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
