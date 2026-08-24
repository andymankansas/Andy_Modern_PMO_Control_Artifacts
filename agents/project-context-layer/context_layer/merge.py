"""merge.py - fold extracted sidecars into the canonical store.

Owns entity identity: assigns stable ids, dedupes exact repeats, and threads
lineage (via link.find_match) so an item seen across multiple days is one entity
with a growing history. People are deduped by normalized name and reused as
owner_ref / attendee targets.
"""
from __future__ import annotations

from pathlib import Path

from . import extract, link, store


def _load(cfg: dict):
    sd = store.store_dir(cfg)
    entities = store.read_jsonl(sd / "entities.jsonl")
    relations = store.read_jsonl(sd / "relations.jsonl")
    return sd, entities, relations


def _index(entities: list[dict]) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = {}
    for e in entities:
        idx.setdefault(e["type"], []).append(e)
    return idx


def _exact_key(e: dict) -> tuple:
    return (e["type"], e.get("workstream"), store.normalize_title(e.get("title", "")),
            (e.get("first_seen") or "")[:10])


def _prov_files(e: dict) -> set[str]:
    return {p.get("source_file") for p in e.get("provenance", []) if p.get("source_file")}


def _cand_source(cand: dict) -> str | None:
    prov = cand.get("provenance") or [{}]
    return prov[0].get("source_file")


def _person_id(name: str, by_norm: dict, entities: list[dict], ids: set[str]) -> str:
    norm = store.normalize_title(name)
    if norm in by_norm:
        return by_norm[norm]["id"]
    pid = store.mint_id("person", store.now_iso(), ids)
    rec = {
        "id": pid, "type": "person", "workstream": "AEM", "title": name.strip(),
        "status": None, "confidence": "high", "provenance": [], "history": [],
        "first_seen": store.now_iso()[:10], "last_seen": store.now_iso()[:10],
        "systems": [], "text": name,
    }
    entities.append(rec)
    by_norm[norm] = rec
    return pid


def merge_sidecar(sidecar: dict, cfg: dict, entities: list[dict], relations: list[dict],
                  ids: set[str], stats: dict) -> None:
    idx = _index(entities)
    by_norm_person = {store.normalize_title(e["title"]): e for e in idx.get("person", [])}
    exact = {_exact_key(e): e for e in entities if e["type"] != "person"}
    # annotate existing action_items with their owner name for lineage scoring
    owner_by_ai = {}
    person_by_id = {e["id"]: e for e in idx.get("person", [])}
    for r in relations:
        if r.get("type") == "owned_by" and r["to"] in person_by_id:
            owner_by_ai[r["from"]] = person_by_id[r["to"]]["title"]
    for e in idx.get("action_item", []):
        e["_owner_name"] = owner_by_ai.get(e["id"], "")

    title_to_id: dict[str, str] = {}

    for cand in sidecar.get("entities", []):
        ctype = cand["type"]
        if ctype == "person":
            pid = _person_id(cand["title"], by_norm_person, entities, ids)
            title_to_id["@" + cand["title"]] = pid
            continue

        cand_src = _cand_source(cand)

        # Exact repeat of the same artifact -> absorb once, or skip if already recorded.
        ex = exact.get(_exact_key(cand))
        if ex is not None:
            if cand_src and cand_src in _prov_files(ex):
                stats["skipped"] += 1
            else:
                _absorb(ex, cand)
                stats["linked"] += 1
            title_to_id["@" + cand["title"]] = ex["id"]
            ex["last_seen"] = max(ex.get("last_seen", ""), cand.get("last_seen", ""))
            continue

        match = link.find_match(cand, idx, cfg)
        if match:
            if cand_src and cand_src in _prov_files(match):
                stats["skipped"] += 1
            else:
                _absorb(match, cand)
                stats["linked"] += 1
            title_to_id["@" + cand["title"]] = match["id"]
            match["last_seen"] = max(match.get("last_seen", ""), cand.get("last_seen", ""))
        else:
            new = _finalize(cand, ids)
            # owner_ref resolution for action items
            if cand.get("owner_name"):
                new["owner_ref"] = _person_id(cand["owner_name"], by_norm_person, entities, ids)
            entities.append(new)
            idx.setdefault(ctype, []).append(new)
            exact[_exact_key(new)] = new
            title_to_id["@" + cand["title"]] = new["id"]
            stats["created"] += 1

    # resolve relations against freshly assigned ids
    meeting_id = None
    for cand in sidecar.get("entities", []):
        if cand["type"] == "meeting":
            meeting_id = title_to_id.get("@" + cand["title"])
            break
    for rel in sidecar.get("relations", []):
        frm = title_to_id.get(rel["from"], rel["from"])
        to = rel["to"]
        if to == "@meeting":
            to = meeting_id
        elif to.startswith("person:"):
            to = _person_id(to.split("person:", 1)[1], by_norm_person, entities, ids)
        elif to.startswith("system:") or to.startswith("stage:"):
            to = to  # kept as symbolic node reference
        if not frm or not to or frm.startswith("@"):
            continue
        rid = store.mint_id("rel", store.now_iso(), ids)
        relations.append({"id": rid, "from": frm, "type": rel["type"], "to": to,
                          "source_file": rel.get("source_file"), "iso": rel.get("iso")})


def _finalize(cand: dict, ids: set[str]) -> dict:
    rec = dict(cand)
    rec.pop("owner_name", None)
    rec.pop("has_rationale", None)
    rec["id"] = store.mint_id(cand["type"], cand.get("first_seen") or store.now_iso(), ids)
    rec.setdefault("history", []).append({
        "iso": store.now_iso(), "change": "created",
        "source_file": (cand.get("provenance") or [{}])[0].get("source_file"),
    })
    return rec


def _absorb(existing: dict, cand: dict) -> None:
    """Merge a re-seen candidate into an existing entity, recording changes."""
    changes = []
    if cand.get("status") and cand["status"] != existing.get("status"):
        changes.append(f"status {existing.get('status')} -> {cand['status']}")
        existing["status"] = cand["status"]
    if cand.get("due") and cand.get("due") != existing.get("due"):
        changes.append(f"due {existing.get('due')} -> {cand['due']}")
        existing["due"] = cand["due"]
    for sysname in cand.get("systems", []):
        if sysname not in existing.get("systems", []):
            existing.setdefault("systems", []).append(sysname)
    for p in cand.get("provenance", []):
        existing.setdefault("provenance", []).append(p)
    src = (cand.get("provenance") or [{}])[0].get("source_file")
    existing.setdefault("history", []).append({
        "iso": store.now_iso(),
        "change": "re-seen" + (": " + "; ".join(changes) if changes else ""),
        "source_file": src,
    })


def merge_files(sidecar_paths: list[Path], cfg: dict) -> dict:
    sd, entities, relations = _load(cfg)
    ids = {e["id"] for e in entities} | {r["id"] for r in relations if "id" in r}
    stats = {"created": 0, "linked": 0, "sidecars": 0, "skipped": 0}
    for sp in sidecar_paths:
        sidecar = store.read_json(sp)
        merge_sidecar(sidecar, cfg, entities, relations, ids, stats)
        stats["sidecars"] += 1
    # strip transient scoring fields before persisting
    for e in entities:
        e.pop("_owner_name", None)
    store.write_jsonl(sd / "entities.jsonl", entities)
    store.write_jsonl(sd / "relations.jsonl", relations)
    return stats


def backfill(cfg: dict) -> dict:
    """Extract every artifact in the configured folders, write sidecars, merge."""
    sd = store.store_dir(cfg)
    sidecar_dir = sd / "sidecars"
    written: list[Path] = []
    manifest: dict[str, float] = {}
    for ws, folder in cfg.get("artifacts_dirs", {}).items():
        p = Path(folder)
        if not p.exists():
            continue
        for md in sorted(p.glob("*.md")):
            try:
                sc = extract.extract_file(md, cfg)
            except Exception as exc:  # keep going on a bad file
                print(f"  skip {md.name}: {exc}")
                continue
            out = sidecar_dir / (md.stem + ".entities.json")
            store.write_json(out, sc)
            written.append(out)
            manifest[md.name] = md.stat().st_mtime
    stats = merge_files(written, cfg)
    store.write_json(_manifest_path(sd), manifest)
    stats["artifacts"] = len(written)
    return stats


def _manifest_path(sd: Path) -> Path:
    return sd / "processed.json"


def reset_store(cfg: dict) -> int:
    """Delete the derived store (entities, relations, sidecars, manifest).

    Leaves corrections.jsonl, quality reports, and rollups untouched. Returns the
    number of files/dirs removed. Used by `backfill --reset` for a clean rebuild.
    """
    sd = store.store_dir(cfg)
    removed = 0
    for name in ("entities.jsonl", "relations.jsonl", "processed.json"):
        p = sd / name
        if p.exists():
            p.unlink()
            removed += 1
    sidecar_dir = sd / "sidecars"
    if sidecar_dir.exists():
        for f in sidecar_dir.glob("*.entities.json"):
            f.unlink()
            removed += 1
    return removed


def _load_manifest(sd: Path) -> dict:
    p = _manifest_path(sd)
    return store.read_json(p) if p.exists() else {}


def incremental(cfg: dict) -> dict:
    """Process only new or changed artifacts since the last run.

    A file is (re)processed when it is absent from the manifest or its mtime is
    newer than what was recorded. Keeps daily cost proportional to new files,
    not the whole folder. Full rebuilds still use backfill().
    """
    sd = store.store_dir(cfg)
    sidecar_dir = sd / "sidecars"
    manifest = _load_manifest(sd)
    written: list[Path] = []
    scanned = 0
    for ws, folder in cfg.get("artifacts_dirs", {}).items():
        p = Path(folder)
        if not p.exists():
            continue
        for md in sorted(p.glob("*.md")):
            scanned += 1
            key = md.name
            mtime = md.stat().st_mtime
            if manifest.get(key) is not None and mtime <= manifest[key]:
                continue
            try:
                sc = extract.extract_file(md, cfg)
            except Exception as exc:
                print(f"  skip {md.name}: {exc}")
                continue
            out = sidecar_dir / (md.stem + ".entities.json")
            store.write_json(out, sc)
            written.append(out)
            manifest[key] = mtime
    stats = merge_files(written, cfg)
    store.write_json(_manifest_path(sd), manifest)
    stats["artifacts"] = len(written)
    stats["scanned"] = scanned
    return stats

