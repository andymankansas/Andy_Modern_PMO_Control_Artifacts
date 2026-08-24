"""Shared store: config, paths, JSONL IO, id minting, and text helpers.

Everything else in context_layer imports from here so the store is written and
read one consistent way.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
_STOPWORDS = {
    "the", "a", "an", "to", "of", "for", "and", "or", "with", "on", "in",
    "re", "fw", "fwd", "update", "notes", "meeting", "sync", "call",
}


def load_config(config_path: str | os.PathLike | None = None) -> dict:
    """Load config.json, falling back to config.example.json."""
    if config_path:
        path = Path(config_path)
    else:
        path = HERE / "config.json"
        if not path.exists():
            path = HERE / "config.example.json"
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def store_dir(cfg: dict) -> Path:
    """Resolve the store directory (relative paths are relative to repo root)."""
    raw = cfg.get("store_dir", "context_layer/store")
    p = Path(raw)
    if not p.is_absolute():
        p = HERE.parent / raw
    p.mkdir(parents=True, exist_ok=True)
    for sub in ("sidecars", "quality", "rollups"):
        (p / sub).mkdir(exist_ok=True)
    return p


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def append_jsonl(path: Path, row: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize_title(text: str) -> str:
    """Lowercase, strip punctuation and stopwords for fuzzy matching / dedupe."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t and t not in _STOPWORDS]
    return " ".join(tokens)


def thread_key(subject: str) -> str:
    """Collapse Re:/Fwd: and trailing 'for <date>' variants into one key."""
    s = (subject or "").lower().strip()
    s = re.sub(r"^\s*(re|fw|fwd)\s*:\s*", "", s)
    while re.match(r"^\s*(re|fw|fwd)\s*:\s*", s):
        s = re.sub(r"^\s*(re|fw|fwd)\s*:\s*", "", s)
    s = re.sub(r"\bfor\s+\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return " ".join(s.split())


def mint_id(entity_type: str, first_seen: str, existing_ids: set[str]) -> str:
    """type-YYYYMMDD-NNNN, unique against existing ids for that (type, date)."""
    date_compact = (first_seen or now_iso())[:10].replace("-", "")
    prefix = f"{entity_type}-{date_compact}-"
    n = 1
    while f"{prefix}{n:04d}" in existing_ids:
        n += 1
    new_id = f"{prefix}{n:04d}"
    existing_ids.add(new_id)
    return new_id


DATE_RE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?"
    r"|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2})",
    re.IGNORECASE,
)


def find_date(text: str) -> str | None:
    m = DATE_RE.search(text or "")
    return m.group(1) if m else None
