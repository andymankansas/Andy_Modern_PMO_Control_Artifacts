# Mapping your template to wbr_config.json

The engine finds what to edit by shape NAME on a given slide. Every deck names its shapes, and
those names are stable once the deck exists, because each week you roll the same deck forward.

## Steps
1. Dump your template:
   ```
   python inspect_deck.py "your_template.pptx" --out deck-structure.json
   ```
2. Open `deck-structure.json`. For each editable region, note the slide number and the shape
   `name` (for example `Text 5`, `Table 2`, `Shape 3`, `TextBox 19`).
3. Fill those names into `wbr_config.json`.

## What each config anchor means
- `subtitle`: the slide 1 shape that holds the reporting week ("Week of ...").
- `programs[].name_shape / rag_shape / rag_fill_shape / body_shape`: for each status card, the
  program name text, the RAG label text, the colored pill shape behind that label, and the
  narrative body.
- `risk_table.shape`: the risk register table. `columns` lists which weekly-input field fills each
  table column, left to right.
- `priorities_table.shape`: the ranked priority table. `text_col` is the column that holds each
  item.
- `reporting_slide`: the executive-summary shape plus the two deliverable name/body pairs.
- `timeline_slide`: the "Updated" stamp shape and optional phase text boxes by key.
- `metrics_slide`: the title (with a date range), the week label, and the shape for each metric in
  the current and prior week rows, plus the insights paragraph.
- `detail_titles`: title shapes on detail slides that carry the reporting week in their title.
- `leave_as_is_slides`: slides the agent must never touch.

## Colors
- `rag_colors` maps each RAG value to a hex fill for the pill shape.
- `severity_colors` maps H / M / L to the fill of the severity cell in the risk table.

## Tip
Give an LLM `deck-structure.json` and `wbr_config.example.json` and ask: "Produce wbr_config.json
that maps my deck. Match by shape name and slide number, keep the color maps, and set
leave_as_is_slides for any closing or divider slides."
