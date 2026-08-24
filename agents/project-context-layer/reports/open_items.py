"""Example report: open and overdue action items from the knowledge base.

Run from the package root:  python reports/open_items.py
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from context_layer import query, store  # noqa: E402

cfg = store.load_config()
ents = query.load_entities(cfg)
people = {e["id"]: e["title"] for e in ents if e["type"] == "person"}

open_items = query.open_action_items(cfg)
overdue = {e["id"] for e in query.overdue_action_items(cfg)}
today = date.today().isoformat()

print(f"Open action items: {len(open_items)}  (as of {today})")
print("-" * 60)
for a in open_items:
    owner = people.get(a.get("owner_ref"), "unassigned")
    due = a.get("due") or "no due date"
    flag = "  [OVERDUE]" if a["id"] in overdue else ""
    print(f"- {a['title']}")
    print(f"    owner: {owner} | due: {due} | confidence: {a.get('confidence')}{flag}")
