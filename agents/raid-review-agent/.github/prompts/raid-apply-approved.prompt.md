---
name: RAID Apply Approved
description: "Apply only formally approved RAID changes with backup and post-write validation."
agent: RAID Review Agent
argument-hint: "Proposal and approval paths, plus new-copy or current-workbook mode."
---

Apply only changes in the selected validated proposal and approval manifest.

Verify that the workbook fingerprint still matches the reviewed version. Create a timestamped backup first. Default to a new output copy. If I select current-workbook mode, require me to confirm the exact resolved workbook path before writing.

Use the packaged deterministic writer, reopen and validate the result, and report all workbook, backup, proposal, approval, and audit paths. Never apply rejected, deferred, needs-more-evidence, uncertain, or unapproved changes.