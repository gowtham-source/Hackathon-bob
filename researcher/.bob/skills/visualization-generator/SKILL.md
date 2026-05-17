---
name: visualization-generator
description: DEPRECATED. Use the figure-planner -> figure-drafter -> figure-critic pipeline plus table-generator instead. This skill is kept only for backward compatibility and will not run; it forwards to the new skill chain.
---

> **DEPRECATED.** This skill has been superseded by the multi-agent figure
> pipeline:
>
> 1. `figure-planner` — decides where/what/why
> 2. `figure-drafter` — renders via CeTZ / matplotlib / PIL grid composer
> 3. `figure-critic` — six-pass quality gate
>
> Plus `table-generator` for comparative tables.
>
> If you opened this skill, switch to `figure-planner` instead. The workflow
> rule `.bob/rules-code2paper/01-workflow.md` Stage 6 uses the new pipeline
> exclusively.

For each entry in `plan.md`'s figure list, run a **draft → critic → refine**
loop. Two sub-agents cooperate via JSON specs on disk:

- **Draft agent** (`scripts/viz_draft.py`): produces a first figure
- **Critic agent** (`scripts/viz_critic.py`): re-reads the figure spec vs. the
  rendered image and proposes refinements

Figures must be **specific to this paper's story** — never a generic
"loss-vs-step" plot if the paper's contribution is a method, never a generic
"confusion matrix" if the contribution is a regression result.

<Steps>
<Step>
**Read** `plan.md`'s figure table. For each row:
- `fig_id`, `caption`, `data_source`, `viz_type`, `section`
</Step>

<Step>
**Write the spec** to `paper/figures/<fig_id>.spec.json`:
```json
{
  "fig_id": "fig_main",
  "caption": "...",
  "data_source": "results/main.json",
  "viz_type": "line | bar | scatter | heatmap | grid | architecture",
  "narrative": "what this figure proves about the paper's claim",
  "axes": {"x": "...", "y": "..."},
  "groups": ["baseline", "ours"],
  "highlight": "ours",
  "constraints": {
    "monochrome_safe": true,
    "min_font_pt": 8,
    "aspect_ratio": "1.6:1",
    "max_width_in": 3.3
  }
}
```
</Step>

<Step>
**Draft** the figure:
```
uv run python scripts/viz_draft.py --spec paper/figures/<fig_id>.spec.json --out paper/figures/<fig_id>.svg
```
The draft script uses matplotlib with the project's style sheet
(`paper/figures/_style.mplstyle`).
</Step>

<Step>
**Critique** the figure:
```
uv run python scripts/viz_critic.py --spec paper/figures/<fig_id>.spec.json --image paper/figures/<fig_id>.svg --out paper/figures/<fig_id>.critique.json
```
The critic reports issues against the spec's `constraints` and `narrative`:
- legend overlaps data?
- highlight group actually visually emphasized?
- axes labels readable at print size?
- does the figure actually support the narrative?
</Step>

<Step>
**Refine** until critic returns `status: "ok"` or the scientist overrides
with `--accept`.
</Step>

<Step>
**Optional Nano-Banana path**: for figures that benefit from generative
imagery (e.g., qualitative samples in a vision paper), set
`viz_type: "qualitative_grid"` in the spec. The draft agent will use the
nano-banana / paperbanana approach (see https://github.com/dwzhu-pku/PaperBanana)
to compose grids from `results/raw/qualitative/`. Critic still applies.
</Step>

<Step>
**Architecture diagrams**: use Typst's `cetz` package directly inside
`paper/sections/methodology.typ`. Discuss with the scientist before drawing
— this skill does not auto-generate architecture diagrams.
</Step>

<Step>
**Insert** into Typst:
```typst
#figure(
  image("figures/fig_main.svg", width: 90%),
  caption: [<caption>],
) <fig:main>
```
Reference with `@fig:main`.
</Step>
</Steps>
