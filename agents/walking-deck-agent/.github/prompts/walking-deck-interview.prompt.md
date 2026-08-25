---
name: Walking Deck Interview
description: "Answer targeted questions that supply the content for each walking-deck slide."
agent: Walking Deck Agent
argument-hint: "Optional: a slide block to focus on (e.g. problem, roadmap)."
---

Interview me to fill in the walking deck. Use anything you already learned from
my artifacts so you only ask what is missing, and work one topic at a time.

For each topic, help me distill the answer to a single sentence and lead with the
"why." Follow the question bank in `docs/QUESTIONS.md`, which covers:

1. **Audience & objective** - who reads this, and the one-sentence goal.
2. **Business context** - who we serve, their objectives, and what success looks like.
3. **Problem / why change** - the pain points and the cost of the status quo.
4. **Solution / operating model** - what it is and, more importantly, why.
5. **How it works** - the lifecycle or process stages, and the governance benefit.
6. **Systems / roles** - each platform or team's one clear job (standard categories).
7. **Scope** - what is in and out.
8. **Roadmap / phases / waves** - the sequence, with dates where known.
9. **Milestones** - dated delivery checkpoints and their status.
10. **Current state** - what is complete, stabilizing, and at risk (RAG).
11. **Team & operating rhythm** - owners and recurring governance.
12. **Next steps & help wanted** - the immediate asks.
13. **Vision / what's next** - how the model repeats and scales.

As we go, populate `config/walking-deck-content.json` block by block and validate
it against `schemas/walking-deck-content.schema.json`. Mark anything I have not
confirmed as an explicit assumption for me to validate. Do not build the deck
until I say the content is ready.
