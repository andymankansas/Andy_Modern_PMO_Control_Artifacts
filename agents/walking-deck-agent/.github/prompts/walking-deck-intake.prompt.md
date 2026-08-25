---
name: Walking Deck Intake
description: "Gather and catalog project artifacts (SOW, notes, recordings, decks, plans, RAID) for the deck."
agent: Walking Deck Agent
argument-hint: "Optional: a folder path to scan."
---

Help me gather the artifacts that describe my project so the walking deck is
grounded in real evidence.

Ask me to point you to any of these that exist (a folder path or file paths):

- **SOW / contract / order form** - scope, objectives, deliverables, dates.
- **Project charter / vision / kickoff brief** - the "why" and success criteria.
- **Meeting notes, recaps, and minutes** - decisions, status, and context.
- **Recordings** (`.mp4`, `.wav`, `.m4a`) - I can transcribe these locally with
  your go-ahead (no upload).
- **Prior decks / status reports** - existing narrative and visuals to reuse.
- **Project plan / roadmap / workback / timeline** - phases and milestone dates.
- **RAID / risk log** - risks, issues, assumptions, dependencies, decisions.
- **Org chart / RACI / stakeholder list** - owners and accountable teams.
- **Brand assets** - logo and color palette.

Then:

1. Run `scripts/intake.py` on the folders I give you to produce a read-only
   manifest at `output/intake_manifest.json`.
2. For any recordings, ask before transcribing, then run `scripts/transcribe.py`.
3. Read the highest-value artifacts and extract candidate facts for the deck:
   problem, objectives, scope, milestones with dates, owners, and risks.
4. Show me a short summary of what you found and where the gaps are.

Do not write deck content yet and do not modify any of my source files. Carry
what you learned into the interview.
