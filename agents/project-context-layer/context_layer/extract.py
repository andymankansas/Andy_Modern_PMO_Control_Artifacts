"""extract.py - parse one artifact .md into a {entities, relations} sidecar.

Deterministic parser over the Daily Meeting Notes Monitor templates (meeting
recap, Email Digest, Teams Digest). No entity ids are assigned here; merge.py
owns identity. Each extracted item carries provenance and a confidence derived
from which source it came from.

Separators for action items are matched permissively (em-dash, en-dash, hyphen,
or colon) so both older and newer (no-em-dash) files parse.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import store

SECTION_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
META_RE = re.compile(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
SEP_RE = re.compile(r"\s*[\u2014\u2013]\s*|\s-\s")
STATUS_WORDS = {
    "open": "open", "closed": "closed", "done": "closed", "complete": "closed",
    "completed": "closed", "in progress": "open", "in-progress": "open",
    "blocked": "open", "pending": "open", "not started": "open",
    "slipped": "slipped", "superseded": "superseded",
}


def _method_and_confidence(sources: str) -> tuple[str, str]:
    s = (sources or "").lower()
    if "recap" in s or "minutes" in s:
        return "verbatim", "high"
    if "transcript" in s:
        return "transcript", "medium"
    if "ai notes" in s or "ai note" in s:
        return "ai_notes", "medium"
    return "inferred", "low"


def _split_blocks(lines: list[str]) -> tuple[str, list[str], list[dict]]:
    """Return (h1_title, preamble_lines, [{level, title, lines}])."""
    h1 = ""
    preamble: list[str] = []
    blocks: list[dict] = []
    cur: dict | None = None
    for line in lines:
        m = SECTION_RE.match(line)
        if m:
            stripped = line.lstrip()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = m.group(1).strip()
            if level == 1 and not h1:
                h1 = title
                cur = None
                continue
            cur = {"level": level, "title": title, "lines": []}
            blocks.append(cur)
            continue
        if cur is None:
            preamble.append(line)
        else:
            cur["lines"].append(line)
    return h1, preamble, blocks


def _parse_meta(preamble: list[str]) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in preamble:
        m = META_RE.match(line)
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip()
    return meta


def _bullets(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        m = BULLET_RE.match(line)
        if m:
            txt = re.sub(r"\*\*|__", "", m.group(1)).strip()
            if txt and txt not in {"-", "\u2014", "None", "N/A"}:
                out.append(txt)
    return out


def _detect_systems(text: str, cfg: dict) -> list[str]:
    low = text.lower()
    return [s for s in cfg.get("systems", []) if s.lower() in low]


def _detect_stage(text: str, cfg: dict) -> int | None:
    low = text.lower()
    for stage, kws in cfg.get("stage_keywords", {}).items():
        if any(k in low for k in kws):
            return int(stage)
    return None


def _parse_action_item(raw: str) -> dict:
    cleaned = re.sub(r"(?i)^\s*(owner|action item|action|task)\s*:\s*", "", raw).strip()
    parts = [p.strip() for p in SEP_RE.split(cleaned) if p.strip()]
    if len(parts) < 2 and "," in cleaned:
        parts = [p.strip() for p in cleaned.split(",", 1) if p.strip()]
    owner = parts[0] if len(parts) >= 2 else None
    due = store.find_date(raw)
    status = None
    low = raw.lower()
    for word, canon in STATUS_WORDS.items():
        if word in low:
            status = canon
            break
    title = parts[1] if len(parts) >= 2 else cleaned
    # drop trailing due/status tokens from the title
    title = re.sub(r"(?i)\b(open|closed|done|complete[d]?|in[\s-]?progress|blocked|pending)\b\s*$", "", title).strip()
    return {"owner": owner, "due": due, "status": status or "open", "title": title or cleaned, "text": raw}


def extract_file(path: str | Path, cfg: dict) -> dict:
    """Parse one .md artifact and return {'source': ..., 'entities': [...], 'relations': [...]}."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    h1, preamble, blocks = _split_blocks(lines)
    meta = _parse_meta(preamble)
    sections: dict[str, list[str]] = {}
    for b in blocks:
        if b["level"] == 2:
            sections.setdefault(b["title"].lower(), []).extend(b["lines"])
    msg_blocks = [b for b in blocks if b["level"] == 3]

    name = path.stem
    parts = name.split("__")
    file_date = None
    workstream = meta.get("workstream")
    if len(parts) >= 3:
        file_date = parts[1]
        workstream = workstream or parts[2].split("_v")[0]
    workstream = workstream or (cfg.get("workstreams") or ["AEM"])[0]
    date = meta.get("date", file_date) or file_date or ""
    date = date[:10] if date else ""

    is_email = h1.lower().startswith("email digest")
    is_teams = h1.lower().startswith("teams digest")
    method, confidence = _method_and_confidence(meta.get("sources captured", ""))
    if is_email or is_teams:
        method, confidence = "verbatim", "high"

    src_type = "email_thread" if is_email else "teams_thread" if is_teams else "meeting"
    prov = [{
        "source_type": src_type,
        "source_file": path.name,
        "extracted_iso": store.now_iso(),
        "method": method,
    }]

    entities: list[dict] = []
    relations: list[dict] = []

    def add_entity(**kw) -> dict:
        kw.setdefault("workstream", workstream)
        kw.setdefault("confidence", confidence)
        kw.setdefault("provenance", [dict(p) for p in prov])
        kw.setdefault("first_seen", date)
        kw.setdefault("last_seen", date)
        kw.setdefault("systems", [])
        entities.append(kw)
        return kw

    if is_email or is_teams:
        # One thread entity per message subject (### heading); pull only the
        # labeled Action items / Decisions fields from each message body.
        for b in msg_blocks:
            subject = re.sub(r"\*\*|__", "", b["title"]).strip()
            if not subject:
                continue
            body = b["lines"]
            body_txt = "\n".join(body)
            tk = store.thread_key(subject)
            thread = add_entity(
                type=src_type, title=subject, status=None,
                thread_key=tk, systems=_detect_systems(body_txt, cfg),
                stage=_detect_stage(body_txt, cfg), text=subject,
            )
            _harvest_digest(body, add_entity, relations, cfg)
        return {"source": path.name, "entities": entities, "relations": relations}

    # Meeting artifact
    body_all = text
    meeting = add_entity(
        type="meeting", title=h1 or name, status=None,
        systems=_detect_systems(body_all, cfg), stage=_detect_stage(body_all, cfg),
        text=(("\n".join(sections.get("summary / overview", [])).strip()) or h1 or name),
    )

    # Attendees -> person entities + attended relations
    attendees = meta.get("attendees", "")
    for who in [a.strip() for a in re.split(r",|;", attendees) if a.strip()]:
        who_clean = re.sub(r"\(.*?\)", "", who).strip()
        if not who_clean or len(who_clean) > 60:
            continue
        person = add_entity(type="person", title=who_clean, status=None, text=who)
        relations.append({"from": "@" + who_clean, "type": "attended", "to": "@meeting",
                          "source_file": path.name, "iso": store.now_iso()})

    _harvest_items(sections.get("decisions", []), meeting, add_entity, relations, cfg, "meeting", h1)
    _harvest_items(sections.get("action items", []), meeting, add_entity, relations, cfg, "meeting", h1, kind="action_item")
    _harvest_items(sections.get("open questions / risks", []), meeting, add_entity, relations, cfg, "meeting", h1, kind="risk")

    return {"source": path.name, "entities": entities, "relations": relations}


def _harvest_items(lines, parent, add_entity, relations, cfg, parent_type, parent_title, kind=None):
    """Turn a section's bullets into decision/action_item/risk entities.

    When kind is None (decisions section) create decisions. parent is a source
    entity used only for relation wiring via its title.
    """
    for raw in _bullets(lines):
        low_ctx = raw.lower()
        this_kind = kind or "decision"
        systems = _detect_systems(raw, cfg)
        stage = _detect_stage(raw, cfg)
        if this_kind == "action_item":
            parsed = _parse_action_item(raw)
            ent = add_entity(type="action_item", title=parsed["title"], status=parsed["status"],
                             due=parsed["due"], systems=systems, stage=stage, text=raw,
                             owner_name=parsed["owner"])
            if parsed["owner"]:
                relations.append({"from": "@" + ent["title"], "type": "owned_by",
                                  "to": "person:" + parsed["owner"], "source_file": None,
                                  "iso": store.now_iso()})
        elif this_kind == "risk":
            ent = add_entity(type="risk", title=raw[:120], status="open",
                             systems=systems, stage=stage, text=raw)
        else:
            rationale = "because" in low_ctx or "rationale" in low_ctx or "(" in raw
            ent = add_entity(type="decision", title=raw[:120], status="active",
                             systems=systems, stage=stage, text=raw,
                             has_rationale=rationale)
        if stage:
            relations.append({"from": "@" + ent["title"], "type": "at_stage",
                              "to": f"stage:{stage}", "source_file": None, "iso": store.now_iso()})
        for sysname in systems:
            relations.append({"from": "@" + ent["title"], "type": "about_system",
                              "to": f"system:{sysname}", "source_file": None, "iso": store.now_iso()})


def _harvest_digest(body: list[str], add_entity, relations, cfg) -> None:
    """From a digest message body, extract only the labeled Action items / Decisions."""
    meta = _parse_meta(body)
    ai_raw = meta.get("action items", "")
    dec_raw = meta.get("decisions", "")

    def _substantive(v: str) -> bool:
        return bool(v) and v.strip().strip("-").strip() not in {"", "None", "N/A", "\u2014", "-"}

    if _substantive(ai_raw):
        for part in re.split(r";|\n", ai_raw):
            part = part.strip()
            if not part:
                continue
            parsed = _parse_action_item(part)
            ent = add_entity(type="action_item", title=parsed["title"], status=parsed["status"],
                             due=parsed["due"], systems=_detect_systems(part, cfg),
                             stage=_detect_stage(part, cfg), text=part, owner_name=parsed["owner"])
            if parsed["owner"]:
                relations.append({"from": "@" + ent["title"], "type": "owned_by",
                                  "to": "person:" + parsed["owner"], "source_file": None,
                                  "iso": store.now_iso()})
    if _substantive(dec_raw):
        for part in re.split(r";|\n", dec_raw):
            part = part.strip()
            if not part:
                continue
            add_entity(type="decision", title=part[:120], status="active",
                       systems=_detect_systems(part, cfg), stage=_detect_stage(part, cfg),
                       text=part, has_rationale=("because" in part.lower() or "(" in part))
