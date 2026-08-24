"""query.py - read-only helpers downstream agents use against the store."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from . import store


def load_entities(cfg: dict) -> list[dict]:
    sd = store.store_dir(cfg)
    return store.read_jsonl(sd / "entities.jsonl")


def open_action_items(cfg: dict, owner: str | None = None, stage: int | None = None,
                      system: str | None = None) -> list[dict]:
    ents = load_entities(cfg)
    people = {e["id"]: e["title"] for e in ents if e["type"] == "person"}
    out = []
    for e in ents:
        if e["type"] != "action_item":
            continue
        if e.get("status") in {"closed", "superseded"}:
            continue
        if stage and e.get("stage") != stage:
            continue
        if system and system not in e.get("systems", []):
            continue
        if owner:
            oname = people.get(e.get("owner_ref"), "")
            if owner.lower() not in oname.lower():
                continue
        out.append(e)
    return sorted(out, key=lambda x: x.get("due") or "9999")


def overdue_action_items(cfg: dict) -> list[dict]:
    today = date.today().isoformat()
    return [e for e in open_action_items(cfg) if e.get("due") and e["due"] < today]


def decisions(cfg: dict) -> list[dict]:
    return [e for e in load_entities(cfg) if e["type"] == "decision"]


def active_risks(cfg: dict) -> list[dict]:
    return [e for e in load_entities(cfg)
            if e["type"] == "risk" and e.get("status") not in {"closed", "resolved"}]
