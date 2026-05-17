---
name: figure-planner
description: Decide WHERE figures are needed, WHAT TYPE each must be, WHAT NARRATIVE INTENT it serves, and WHAT VENUE-SPECIFIC STYLE it follows. Emits paper/figures/_manifest.json which downstream skills (figure-drafter, figure-critic, section-drafter) consume. Treats figures as scientific communication objects, not graphics.
---

This skill is the **brain** of the visualization pipeline. It does not draw
anything — it decides what should be drawn, where, why, and how.

A figure is a *scientific communication object* with five dimensions:
1. **Intent** — what claim does it support?
2. **Type** — architecture, comparison, ablation, qualitative, schematic, equation-graph, data-flow
3. **Section anchor** — where in the paper is it referenced?
4. **Visual grammar** — venue-specific layout/typography/palette
5. **Mathematical integration** — which equations does it visualize?

<Steps>
<Step>
**Read upstream artifacts**:
- `paper/analysis.json` (model architecture, training pipeline, datasets)
- `paper/novelty.md` (delta table — every Δ row is a figure candidate)
- `plan.md` (figure list + section outline)
- `paper/refs.bib` (for venue-typical figure styles in cited papers)
- `results/_index.json` if exists (data availability)
- The target venue ("NeurIPS"|"CVPR"|"IEEE"|"Springer-LNCS")
</Step>

<Step>
**Run the figure-need detector**. For every section, ask:

| Section | Trigger questions |
|---------|------------------|
| Introduction | Does the paper introduce a non-trivial pipeline? → teaser figure |
| Related work | Are ≥3 method families compared in the delta table? → taxonomy diagram |
| Methodology | Are there ≥2 modules with data flow? → architecture diagram |
| Methodology | Is there a non-obvious algorithmic component? → algorithm-as-graph |
| Experiments | Is there a multi-axis hyperparameter sweep? → grid/heatmap |
| Results | Are there ≥3 baselines × ≥3 datasets? → grouped bar / line plot |
| Results | Is there a per-component contribution? → ablation bar chart |
| Results | Are there qualitative outputs (images, text, mol)? → qualitative grid |
| Discussion | Is there a failure mode worth illustrating? → failure-case panel |

If a trigger fires AND the section is in the venue's required list, produce a manifest entry. Mark figures as **required** (paper is incomplete without it) or **optional**.
</Step>

<Step>
**Determine figure type ontology**. Use this table to map intent → renderer:

| Intent | Type | Primary renderer | Fallback |
|--------|------|-----------------|----------|
| Show pipeline / data flow / module composition | `architecture` | Typst `cetz` + `fletcher` | hand-drawn SVG |
| Compare methods on a metric across datasets | `grouped_bar` or `line` | matplotlib + style sheet | lilaq |
| Show per-component contribution | `ablation_bar` | matplotlib | lilaq |
| Show parameter sweep | `heatmap` or `surface` | matplotlib | lilaq |
| Show qualitative samples | `qualitative_grid` | PIL grid composer (PaperBanana-style) | manual |
| Position vs. prior work taxonomically | `taxonomy_tree` | Typst `cetz` `tree` | fletcher |
| Visualize an equation's geometry | `equation_graph` | Typst `cetz` | matplotlib parametric |
| Show a failure case | `failure_panel` | grid + annotation | manual |
| Teaser / "money shot" | `teaser_composite` | composite (arch + result) | manual |

Architecture diagrams are FIRST-CLASS. Do not fall back to "discuss with the scientist" — generate a planned spec; the drafter will emit Typst CeTZ/fletcher code that the scientist may edit.
</Step>

<Step>
**Decide visual grammar per venue**. Write the venue palette into the
manifest so the drafter and critic both consume it:

| Venue | Color palette | Font policy | Aspect / size | Other |
|-------|---------------|-------------|---------------|-------|
| NeurIPS | monochrome-safe + 3-color accent (Okabe–Ito subset: `#000000`, `#0072B2`, `#D55E00`, `#009E73`) | New Computer Modern, 8pt body / 9pt title | width ≤ `\textwidth` (~5.5in single col) or `\columnwidth` (3.3in) | Captions descriptive (1–3 sentences) |
| CVPR / ICCV | similar palette, anonymized — no logos in arch diagrams | Times-equivalent, 8pt | column-width 3.3in default | Double-blind: strip institution branding |
| IEEE | grayscale-first, color used sparingly | IEEE Times, 7–8pt | 3.5in column | Index Terms style, IEEE-conventional |
| Springer-LNCS | Helvetica titles, Times body | similar | 4.6in single col | LNCS expects `\caption*{...}` style elsewhere |
| Nature-style | strong typography hierarchy, sans-serif annotations | Arial-equivalent | wide rectangles, 7in | Highlight panel-letter labels (a, b, c) |

Every figure spec inherits the venue grammar but may override `width`, `palette_extension`, or `font_size_floor`.
</Step>

<Step>
**Equation-aware composition**. For every architecture/methodology figure,
check `plan.md` methodology schema for equations associated with the same
sub-topic. If found, the manifest entry must include:

```json
"equations": [
  {"id": "eq:fusion", "tex": "\\alpha \\cdot z_{clip} + (1-\\alpha) z_{rep}", "anchor_in_diagram": "fusion_block"}
]
```

The drafter is required to render the equation **inside or adjacent to** the
diagram block it describes — never as detached text.
</Step>

<Step>
**Cross-modal alignment**. For each figure, list which other artifacts in the
paper it must visually echo:
- Same color for the same method across all figures (check against earlier `_manifest.json` entries)
- Architecture diagrams must use the same module names as `paper/sections/methodology.typ`
- Bar chart legend order must match table column order in the corresponding §5 table

Record echoes in the manifest:
```json
"echoes": {
  "method_color_map_ref": "_manifest.json#shared.color_map",
  "module_name_source": "sections/methodology.typ",
  "legend_order_source": "tables/main_results.tex_keys"
}
```
A shared `_manifest.json#shared` block holds the global color map, method
ordering, and module name list — populated on the first figure entry, reused
thereafter.
</Step>

<Step>
**Reviewer-oriented optimization**. For each figure, list anticipated
reviewer questions (sourced from `paper/novelty.md` "Reviewer risks"):
```json
"reviewer_targets": [
  "Q3: 'is the gain real or seed luck?' → error bars must be visible",
  "Q5: 'why this regularization?' → ablation panel must appear in same figure"
]
```
The critic agent will check whether the rendered figure actually addresses
each listed target.
</Step>

<Step>
**Emit `paper/figures/_manifest.json`**:
```json
{
  "venue": "neurips",
  "shared": {
    "color_map": {"baseline": "#999999", "ours": "#D55E00", "ours_pp": "#0072B2"},
    "method_order": ["CLIP", "CoOp", "MaPLe", "Ours", "Ours++"],
    "module_names": ["Image Encoder", "Text Encoder", "Representation Learner", "Fusion"]
  },
  "figures": [
    {
      "fig_id": "fig:teaser",
      "section": "introduction",
      "intent": "Convey one-sentence contribution at a glance",
      "type": "teaser_composite",
      "required": true,
      "renderer": "cetz+matplotlib",
      "narrative": "Left: our dual-branch architecture; right: H-mean improvement vs. baselines.",
      "data_sources": ["plan.md#contributions", "results/_index.json#main_h_mean"],
      "equations": [],
      "constraints": {"width_in": 5.5, "min_font_pt": 8, "monochrome_safe": true},
      "echoes": {"method_color_map_ref": "shared.color_map"},
      "reviewer_targets": []
    },
    {
      "fig_id": "fig:arch",
      "section": "methodology",
      "intent": "Show data flow through dual-branch with rep tokens injected at layers 6-12",
      "type": "architecture",
      "required": true,
      "renderer": "cetz",
      "narrative": "Two parallel paths from input image+text; rep tokens enter both; weighted fusion at the head.",
      "data_sources": ["analysis.json#model.modules"],
      "equations": [
        {"id": "eq:fusion", "tex": "alpha z_{clip} + (1-alpha) z_{rep}", "anchor_in_diagram": "fusion_block"},
        {"id": "eq:srra", "tex": "W_{shared} + Delta W_{lora}", "anchor_in_diagram": "srra_block"}
      ],
      "constraints": {"width_in": 5.5, "min_font_pt": 8},
      "echoes": {"module_name_source": "shared.module_names"},
      "reviewer_targets": ["Q3: dual-branch overhead → annotate parameter counts on each block"]
    },
    {
      "fig_id": "fig:main_results",
      "section": "results",
      "intent": "Headline: ours beats all baselines on H-mean across 11 datasets",
      "type": "grouped_bar",
      "required": true,
      "renderer": "matplotlib",
      "narrative": "Per-dataset H-mean, ours_pp highlighted; CLIP zero-shot dotted reference line.",
      "data_sources": ["results/_index.json#base_to_novel"],
      "constraints": {"width_in": 5.5, "min_font_pt": 7, "error_bars": "95%CI"},
      "echoes": {"method_color_map_ref": "shared.color_map", "method_order": "shared.method_order"},
      "reviewer_targets": ["Q1: significance → error bars + dataset-level deltas"]
    },
    {
      "fig_id": "fig:ablation",
      "section": "results",
      "intent": "Each component contributes positively",
      "type": "ablation_bar",
      "required": true,
      "renderer": "matplotlib",
      "narrative": "Cumulative deltas: +rep tokens, +cosine reg, +SRRA, +PRC.",
      "data_sources": ["results/_index.json#ablation"],
      "constraints": {"width_in": 3.3, "min_font_pt": 8}
    },
    {
      "fig_id": "fig:qualitative",
      "section": "results",
      "intent": "Show concrete novel-class examples where rep tokens win",
      "type": "qualitative_grid",
      "required": false,
      "renderer": "pil_grid",
      "narrative": "3x4 grid: rows=datasets (Pets, Flowers, EuroSAT); cols=samples; bottom row shows CLIP miss, ours hit.",
      "data_sources": ["results/qualitative/"],
      "constraints": {"width_in": 5.5, "tile_min_px": 96}
    }
  ]
}
```
</Step>

<Step>
**Hand-off and checkpoint**. Present the manifest as a markdown table to the
scientist:

| Fig | Section | Type | Required | Reviewer-target |
|-----|---------|------|----------|-----------------|
| teaser | §1 | teaser_composite | yes | — |
| arch | §3 | architecture | yes | param-count overhead |
| main_results | §5 | grouped_bar | yes | significance |
| ablation | §5 | ablation_bar | yes | regularization choice |
| qualitative | §5 | qualitative_grid | no | — |

Ask the scientist:
- Approve / amend the figure list
- Confirm color palette + venue grammar
- Add/remove reviewer targets

Only after approval (Checkpoint 6a) may `figure-drafter` start.
</Step>
</Steps>

## Refusal rules

- Do NOT skip an architecture figure on the grounds that "Bob can't draw" — the drafter has CeTZ/fletcher renderers that handle it. If the figure cannot be auto-generated, emit a TODO entry, not silence.
- Do NOT propose a generic figure (e.g. "loss curve") if the paper's claim isn't about training dynamics.
- Do NOT plan a figure whose `data_source` doesn't exist; mark it `blocked` and surface to scientist.
- Every required figure MUST have a `narrative` field and at least one `reviewer_target` if the corresponding novelty claim has a reviewer-risk row.
