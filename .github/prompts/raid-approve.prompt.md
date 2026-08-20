---
name: RAID Approve
description: "Conduct formal item-by-item review of a saved RAID proposal and create an approval manifest."
agent: RAID Review Agent
argument-hint: "Optional: proposal JSON path. Defaults to the latest proposal."
---

Open the selected or latest saved RAID proposal and conduct a formal item-by-item review.

For each recommendation, show its current value, proposed value, operation, rationale, sources, confidence, and warnings. Let me approve it, approve it with exact edits, reject it, defer it, or request more evidence. Do not permit uncertain proposals to be approved.

Do not write to the workbook. After every item has a disposition, create and validate the approval manifest and ask whether the eventual write should create a new copy or update the current workbook.