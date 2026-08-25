# Slide Block Reference

The `slides` array in `config/walking-deck-config.json` lists the blocks to
render, in order. Each entry is either a block id (string) or an object
`{ "block": "<id>", "content": { ... } }` to supply inline content (useful for
`section` and `bullets`, which can appear multiple times). Content for named
blocks is read from `config/walking-deck-content.json` by matching key.

Every field is optional; a block renders what it is given.

| Block | Purpose | Key content fields |
|-------|---------|--------------------|
| `cover` | Title slide | `eyebrow`, `title`, `subtitle`, `stamp` |
| `agenda` | The story flow | `takeaway`, `items[]` (`num`, `head`, `body`) |
| `problem` | Why change + context | `takeaway`, `context` (`label`, `text`), `cards[]` |
| `vision` | Operating model | `takeaway`, `label`, `statement`, `steps[]`, `sowhat` |
| `how_it_works` | Lifecycle stages | `takeaway`, `stages[]`, `governance` |
| `roles` | Each platform/team's job | `takeaway`, `cards[]` (`name`, `role`, `rows[]`), `footnote` |
| `scope` | In / out of scope | `takeaway`, `in_scope[]`, `out_scope[]` |
| `roadmap` | Waves + repeatable cycle | `takeaway`, `waves[]`, `cycle[]`, `outcome` |
| `milestones` | Dated checkpoints | `takeaway`, `items[]` (`date`, `head`, `body`, `status`), `critical_path` |
| `current_state` | RAG level-set | `takeaway`, `mode`, `cards[]` |
| `team` | Ownership + rhythm | `takeaway`, `owners[]` (`role`, `names`, `accent`), `rhythm[]` |
| `next_steps` | Moves + help wanted | `takeaway`, `moves[]`, `help[]`, `success` |
| `closer` | Vision / scale | `takeaway`, `tiers[]` (`head`, `when`, `body`), `banner` |
| `section` | Divider | `title`, `subtitle` |
| `bullets` | Simple content slide | `title`, `takeaway`, `bullets[]` |

## Cards and bullets

- `cards[]` items use `head`, `accent`, and either `bullets` (a list of
  `[lead, body]` pairs) or a plain `body` string. 1-4 cards lay out automatically.
- `accent` accepts `primary`, `accent`, `dark`, `green`, `amber`, `red`, or a
  brand color name. Status blocks (milestones, current_state) also map
  `complete`/`active`/`upcoming` to green/amber/brand.
- Rich text lists (`rows`, `rhythm`, `help`, `bullets`) are arrays of
  `[bold_lead, normal_body]` pairs; a plain string renders as a single bullet.

## Adding a slide more than once

```json
"slides": [
  "cover",
  { "block": "section", "content": { "title": "PART ONE", "subtitle": "The problem" } },
  "problem",
  { "block": "bullets", "content": { "title": "APPENDIX", "bullets": [["Detail A", ""], ["Detail B", ""]] } }
]
```
