"""corrections.py - the norms layer as data.

Every judgment call the user makes (include/skip a borderline item, a scope
decision, a taxonomy addition) is appended to corrections.jsonl. Before the
monitor asks the user about a borderline case, it calls match() to see whether a
prior ruling already covers it, so it only asks on genuinely new situations.
"""
from __future__ import annotations

from difflib import SequenceMatcher

from . import store


def add_correction(cfg: dict, trigger: str, pattern: str, decision: str,
                   rule: str, scope: str = "global") -> dict:
    sd = store.store_dir(cfg)
    rec = {
        "iso": store.now_iso(), "trigger": trigger, "pattern": pattern,
        "decision": decision, "rule": rule, "scope": scope,
    }
    store.append_jsonl(sd / "corrections.jsonl", rec)
    return rec


def load_corrections(cfg: dict) -> list[dict]:
    sd = store.store_dir(cfg)
    return store.read_jsonl(sd / "corrections.jsonl")


def match(cfg: dict, situation: str, scope: str = "global", threshold: float = 0.4) -> dict | None:
    """Return the best prior ruling for a situation, or None to ask the user.

    situation is a short description of the borderline case, e.g.
    "'GT' appears inside the word 'GTM' in a Teams message".

    Scoring blends sequence similarity with distinctive-token coverage so that
    differently phrased descriptions of the same situation still match.
    """
    sit_norm = store.normalize_title(situation)
    sit_tokens = set(sit_norm.split())
    if not sit_tokens:
        return None
    best, best_score = None, 0.0
    for c in load_corrections(cfg):
        if c.get("scope") not in {scope, "global"}:
            continue
        pat_norm = store.normalize_title(c.get("pattern", ""))
        pat_tokens = set(pat_norm.split())
        if not pat_tokens:
            continue
        seq = SequenceMatcher(None, sit_norm, pat_norm).ratio()
        coverage = len(pat_tokens & sit_tokens) / len(pat_tokens)
        score = max(seq, coverage)
        if score > best_score:
            best_score, best = score, c
    return best if best_score >= threshold else None
