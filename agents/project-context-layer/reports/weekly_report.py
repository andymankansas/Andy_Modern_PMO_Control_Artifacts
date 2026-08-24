"""Example report: a readable weekly status built from the latest rollup.

Run from the package root:  python reports/weekly_report.py
Builds the rollup first so it is always current.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from context_layer import rollup, store  # noqa: E402

cfg = store.load_config()
res = rollup.build_rollup(cfg)
sd = store.store_dir(cfg)
data = store.read_json(Path(res["json"]))

c = data["counts"]
d = data["changed_vs_last_week"]

print(f"# Weekly Status - {data['week']}")
print()
print(f"Open action items: {c['open_action_items']}")
print(f"Decisions this week: {c['decisions_this_week']}")
print(f"Active risks: {c['active_risks']}")
print()
print("## What changed vs last week")
if "note" in d:
    print(f"- {d['note']}")
else:
    print(f"- Compared to {d.get('compared_to')}")
    print(f"- New action items: {d.get('new_action_items')}")
    print(f"- Closed / dropped: {d.get('closed_or_dropped_action_items')}")
    print(f"- New decisions: {d.get('new_decisions')}")
    print(f"- New risks: {d.get('new_risks')}")
print()
print("## Open action items (by due date)")
for a in data["open_action_items"][:20]:
    print(f"- {a['title']} (due {a.get('due') or 'n/a'})")
