"""link.py - lineage matching.

Given a candidate entity (decision / action_item / risk / thread) and the set of
existing entities, find the same real-world object seen on an earlier day so we
append to its history instead of creating a duplicate.
"""
from __future__ import annotations

from difflib import SequenceMatcher

from . import store

# Types that represent recurring, evolving objects worth threading over time.
LINKABLE = {"action_item", "decision", "risk", "email_thread", "teams_thread"}


def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_match(candidate: dict, index: dict, cfg: dict) -> dict | None:
    """Return the existing entity that candidate continues, or None.

    index maps entity_type -> list of existing entity dicts.
    """
    ctype = candidate.get("type")
    if ctype not in LINKABLE:
        return None
    threshold = cfg.get("lineage_match_threshold", 0.72)

    # Threads match purely on thread_key.
    if ctype in {"email_thread", "teams_thread"}:
        ck = candidate.get("thread_key")
        if not ck:
            return None
        for ex in index.get(ctype, []):
            if ex.get("thread_key") and ex["thread_key"] == ck:
                return ex
        return None

    cand_norm = store.normalize_title(candidate.get("title", ""))
    if not cand_norm:
        return None
    cand_owner = (candidate.get("owner_name") or "").lower().strip()
    cand_ws = candidate.get("workstream")

    best = None
    best_score = 0.0
    for ex in index.get(ctype, []):
        if ex.get("workstream") != cand_ws:
            continue
        if ex.get("status") in {"closed", "superseded"}:
            continue
        score = _sim(cand_norm, store.normalize_title(ex.get("title", "")))
        ex_owner = ""
        for rel_owner in [ex.get("_owner_name", "")]:
            ex_owner = (rel_owner or "").lower().strip()
        if cand_owner and ex_owner and cand_owner == ex_owner:
            score += 0.1
        if candidate.get("systems") and ex.get("systems"):
            if set(candidate["systems"]) & set(ex["systems"]):
                score += 0.05
        if score > best_score:
            best_score = score
            best = ex
    return best if best_score >= threshold else None
