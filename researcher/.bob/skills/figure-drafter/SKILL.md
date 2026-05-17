---
name: figure-drafter
description: Render every figure in paper/figures/_manifest.json using the appropriate scientific renderer (Typst CeTZ/fletcher for architecture and taxonomy diagrams, matplotlib/lilaq for plots, PIL grid composer for qualitative samples). Produces SVG/PDF/typ artifacts and a render report. Replaces and supersedes the legacy visualization-generator.
---

This skill draws what `figure-planner` decided to draw. It is renderer-aware:
each figure type has a dedicated renderer with venue-grammar inheritance.
Bob never inlines matplotlib code in chat — always via subprocess.

<Steps>
<Step>
**Read** `paper/figures/_manifest.json`. For each entry process figures in the
order: architecture → teaser → main_results → ablation → qualitative.
Architecture renders first because its color/module-name decisions seed
`shared.color_map` and `shared.module_names` for later figures.
</Step>

<Step>
**Renderer dispatch table**:

| `type` field | Renderer command |
|--------------|------------------|
| `architecture` | `uv run python scripts/viz_arch.py --spec <spec> --out paper/figures/<id>.typ` (emits CeTZ/fletcher Typst code; included via `#include "figures/<id>.typ"`) |
| `taxonomy_tree` | `uv run python scripts/viz_arch.py --mode tree --spec <spec> --out paper/figures/<id>.typ` |
| `equation_graph` | `uv run python scripts/viz_arch.py --mode equation --spec <spec> --out paper/figures/<id>.typ` |
| `grouped_bar`, `line`, `scatter`, `heatmap`, `surface`, `ablation_bar` | `uv run python scripts/viz_draft.py --spec <spec> --out paper/figures/<id>.svg` |
| `qualitative_grid` | `uv run python scripts/viz_grid.py --spec <spec> --out paper/figures/<id>.png` |
| `failure_panel` | `uv run python scripts/viz_grid.py --mode failure --spec <spec> --out paper/figures/<id>.png` |
| `teaser_composite` | composite: render each panel separately then `uv run python scripts/viz_compose.py --spec <spec> --out paper/figures/<id>.svg` |

If a renderer script does not yet exist, the drafter creates a stub at the
path and writes a TODO into the spec — it does NOT silently skip.
</Step>

<Step>
**Architecture renderer contract** (`scripts/viz_arch.py`):

Reads the spec's `narrative`, `data_sources` (analysis.json model modules),
and `equations`. Emits Typst CeTZ code:

```typst
// paper/figures/fig_arch.typ
#import "@preview/cetz:0.2.2"
#import "@preview/fletcher:0.5.1" as fletcher: node, edge

#figure(
  fletcher.diagram(
    node-stroke: 0.6pt,
    spacing: (10mm, 6mm),
    node((0,0), [Image\ Encoder], shape: fletcher.shapes.rect, fill: rgb("#F0F0F0")),
    node((0,1), [Text\ Encoder], shape: fletcher.shapes.rect, fill: rgb("#F0F0F0")),
    node((1,0.5), [Representation\ Learner\ (rep_dim=512)], shape: fletcher.shapes.rect, fill: rgb("#FFF3E0")),
    node((2,0.5), [Weighted Fusion\ $alpha z_{clip} + (1-alpha) z_{rep}$], shape: fletcher.shapes.diamond, fill: rgb("#E3F2FD")),
    edge((0,0), (1,0.5), "->"),
    edge((0,1), (1,0.5), "->"),
    edge((1,0.5), (2,0.5), "->"),
    edge((0,0), (2,0.5), "->", bend: 30deg, label: [CLIP path]),
    edge((0,1), (2,0.5), "->", bend: -30deg, label: [CLIP path]),
  ),
  caption: [<from spec.narrative>],
) <fig:arch>
```

Conventions enforced by the renderer:
- Module names sourced from `shared.module_names` for cross-figure consistency
- Block fill colors sourced from `shared.color_map` extended with semantic role tints (input=light gray, learnable=warm tint, frozen=cool tint, fusion=accent)
- Equations inside or adjacent to the block they describe (never floating)
- Arrow labels short (≤3 words); long descriptions go in the caption
- Aspect ratio honors `constraints.width_in`
</Step>

<Step>
**Plot renderer contract** (`scripts/viz_draft.py`):

Inherits `paper/figures/_style.mplstyle`. Reads spec's:
- `data_sources` paths (resolves JSON keys like `results/_index.json#base_to_novel`)
- `groups`, `highlight`, `axes`, `error_bars`, `legend_order`
- `shared.color_map` for consistent method colors

Hard rules:
- Highlight color (ours) used ONLY for the `highlight` group; baselines use grayscale
- Error bars rendered if spec.constraints.error_bars set; missing CIs in data raise an explicit warning, never silent
- Legend order matches `shared.method_order`
- All text ≥ `constraints.min_font_pt`
- Saves SVG (vector) by default; PDF on request
</Step>

<Step>
**Qualitative grid renderer** (`scripts/viz_grid.py`, PaperBanana-style but stricter):

For `qualitative_grid` and `failure_panel`:
- Reads tile sources from `results/qualitative/<dataset>/<sample_id>/{input.png,output.png}`
- Composes a row × col grid with:
  - Per-row dataset name on the left
  - Per-column method name on top (from `shared.method_order`)
  - Annotation overlays for failure cases (red box on miss, green tick on hit)
  - Bottom margin for caption
- Tile size ≥ `constraints.tile_min_px`, anti-aliased
- Output PNG (raster) embedded into Typst with `image("figures/<id>.png", width: <constraints.width_in>in)`

NEVER auto-generate fake samples. If `results/qualitative/` is empty, mark
the figure `blocked` in the render report and ask the scientist for source
images.
</Step>

<Step>
**Composite renderer** (`scripts/viz_compose.py` for teasers):

Reads sub-panel paths in spec (`panels: ["fig:arch_mini.svg", "fig:main_bar.svg"]`)
and lays them out with panel-letter labels (a, b, c) at top-left of each. Honors
the overall `width_in` constraint.
</Step>

<Step>
**Emit per-figure render report** at `paper/figures/<id>.render.json`:
```json
{
  "fig_id": "fig:arch",
  "renderer": "viz_arch.py",
  "output": "paper/figures/fig_arch.typ",
  "exit_code": 0,
  "warnings": [],
  "spec_hash": "...",
  "produced_at": "ISO-8601"
}
```

After all figures process, write `paper/figures/_render_report.json` with a
summary (succeeded, blocked, failed counts).
</Step>

<Step>
**Insert into Typst sections**. For each figure, add the proper include in
the right section file:

- SVG/PNG: `#figure(image("figures/<id>.svg", width: <w>in), caption: [<...>]) <<id>>`
- CeTZ `.typ`: `#include "figures/<id>.typ"` (the typ file itself contains the `#figure(...)` wrapper)
- Composite: `#figure(image("figures/<id>.svg", width: <w>in), caption: [<...>]) <<id>>`

Reference in prose: `as shown in @<fig_id>`.

Section-drafter consumes the manifest to know which `<fig_id>` each section
must reference. The drafter does NOT edit section files directly — it only
emits artifacts and updates the manifest with `inserted: false → true`.
</Step>
</Steps>

## Refusal rules

- Do NOT render a figure whose `data_source` is missing — write a `blocked` entry instead and continue with the next figure.
- Do NOT silently rescale text below `constraints.min_font_pt`. If the layout overflows, request a manual override from the scientist.
- Do NOT mix raster and vector renderings in the same figure unless `composite` mode declares it.
- Do NOT use a color outside the venue palette (or its declared extension) without an explicit override in the spec.
