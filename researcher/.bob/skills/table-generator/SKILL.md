---
name: table-generator
description: Plan and render publication-quality comparative tables (main results, ablations, dataset stats, parameter counts). Same planner→drafter→critic discipline as figures. Emits Typst table code into paper/tables/*.typ and a manifest paper/tables/_manifest.json.
---

Tables were entirely absent from the prior pipeline. This skill closes that
gap. A research paper without a main-results table is incomplete.

<Steps>
<Step>
**Plan tables** from `plan.md` + `paper/novelty.md` + `results/_index.json`.
Standard table set (emit when triggers fire):

| Table | Trigger | Columns |
|-------|---------|---------|
| `tab:main_results` | ≥2 baselines × ≥3 datasets | Method, Dataset₁, …, Datasetₙ, Mean ± std |
| `tab:base_to_novel` | base-to-novel protocol used | Method, Base, Novel, H-mean (per dataset + average) |
| `tab:ablation` | analysis lists ≥2 components | Variant, Components on/off, Metric, Δ |
| `tab:efficiency` | parameter-efficiency claim | Method, #Trainable, #Total, Throughput, Memory |
| `tab:dataset_stats` | ≥3 datasets used | Dataset, #Classes, #Train, #Val, #Test, Domain |
| `tab:hyperparams` | reproducibility section | Hyperparam, Value, Source |
| `tab:cross_dataset` | cross-dataset transfer | Source→Target, Method, Acc |

Write `paper/tables/_manifest.json`:
```json
{
  "tables": [
    {
      "tab_id": "tab:main_results",
      "section": "results",
      "intent": "Headline numbers proving ours beats baselines",
      "required": true,
      "data_source": "results/_index.json#base_to_novel",
      "schema": ["Method", "ImageNet", "...", "Average", "H-mean"],
      "highlight_row": "Ours++",
      "best_per_col_bold": true,
      "second_best_underline": true,
      "echoes": {"method_order": "figures/_manifest.json#shared.method_order"}
    }
  ]
}
```
</Step>

<Step>
**Render** each table:
```
uv run python scripts/table_gen.py --spec paper/tables/_manifest.json --tab-id tab:main_results --out paper/tables/main_results.typ
```

The renderer emits a Typst `#figure(table(...), caption: [...]) <tab:...>`:
- `columns: (...)` widths inferred from content
- `align:` left for method column, center/right for numerics
- Best-per-column **bold**, second-best _underlined_ (mandated for ML
  community tables)
- Highlight row shaded with `fill: rgb("#FFF3E0")`
- `±` formatting with `std` if `num_seeds > 1`
- Numbers formatted to consistent decimal places (2 by default; configurable
  per column)
- Source comments after every cell:
  ```typst
  [79.24] // src: results/_index.json#base_to_novel.ours.h_mean
  ```
</Step>

<Step>
**Critic passes** (same six dimensions as figure-critic, scoped to tables):
1. **Legibility** — column widths don't overflow; no auto-wrap mid-number
2. **Numerical** — every cell traces to `results/_index.json`; run `verify_numbers` on the rendered .typ
3. **Palette** — at most 1 highlight color; bold/underline conventions correct
4. **Narrative** — highlight row is the method the section claims wins; legend in body matches
5. **Venue** — caption above table for ACL/NeurIPS conventions; horizontal rules only (no vertical), per booktabs style
6. **Reviewer targets** — significance markers present if claim is "best"; std shown if num_seeds > 1

Emit `paper/tables/<id>.critique.json`. Refine loop with max 3 iterations.
</Step>

<Step>
**Cross-table & cross-figure consistency** check:
- Methods column order matches `figures/_manifest.json#shared.method_order`
- Dataset column order matches across all tables that share datasets
- The numbers in `tab:main_results` MUST match the bar heights in
  `fig:main_results` (same data source, same rounding)

Run consistency report:
```
uv run python scripts/table_gen.py --check-consistency --out paper/tables/_consistency.json
```
</Step>

<Step>
**Insert into section files**:
```typst
#include "tables/main_results.typ"
```
Reference in prose: `as summarized in @tab:main_results`. The
section-drafter consumes `tables/_manifest.json` analogously to the figure
manifest.
</Step>
</Steps>

## Refusal rules

- Do NOT emit a table with `[N/A]` or `[TODO]` cells in a required column. Either fill from data or mark the table `blocked` in the manifest.
- Do NOT mark "Ours" as best by re-formatting unless the actual number is genuinely best — bold belongs to the true argmax per column, even when it is a baseline.
- Do NOT use vertical rules (booktabs convention violation).
- Do NOT exceed page width — if needed, split a wide table or use a rotated `table.with(...)`.
