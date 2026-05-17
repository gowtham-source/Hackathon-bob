---
name: figure-critic
description: Multi-pass critic for every drafted figure. Evaluates text legibility, formula correctness, color contrast, narrative alignment, venue grammar conformance, and reviewer-target coverage. Returns structured critique JSON; the drafter loops until status="ok" or scientist overrides.
---

The critic is the quality gate that distinguishes a "scientific
communication object" from a generic graphic. Each figure passes through
six independent critic passes; any FAIL forces a re-draft.

<Steps>
<Step>
**Read** `paper/figures/_manifest.json`, the rendered artifact (SVG/PNG/typ),
the per-figure render report, and `paper/refs.bib` (for venue convention
sampling).
</Step>

<Step>
**Pass 1 — Text legibility**.
For raster outputs: rasterize at print DPI (300), use `pytesseract` or
similar OCR to extract on-image text; flag any text whose bounding box
height < `constraints.min_font_pt × dpi/72`. For vector SVG/typ: parse
font-size attributes directly.

Failure modes:
- Text below font-size floor
- Text outside figure bounding box
- Overlapping labels (axis ticks vs. data, legend vs. data)
- Truncated labels (ending in `…` or cut by margin)

Output: `legibility: {status: "ok"|"warn"|"fail", offenders: [{text, size_pt, bbox}, ...]}`.
</Step>

<Step>
**Pass 2 — Formula correctness**.
For each `equations[*]` entry in the spec:
1. Confirm the equation appears in the rendered figure (OCR or text-search in `.typ`).
2. Confirm it appears **adjacent to its `anchor_in_diagram`** block (not floating).
3. Compile the equation's Typst math snippet alone with `typst compile --root .` to verify it parses.
4. Check that variables in the equation are also annotated (block label or arrow label) somewhere in the diagram.

Output: `formulas: {status, missing: [...], orphaned: [...], unparsed: [...]}`.
</Step>

<Step>
**Pass 3 — Color & contrast**.
- Extract the figure's color palette (vector: parse fill/stroke; raster: k-means on pixels).
- Verify subset of `shared.color_map ∪ venue_palette`. Foreign colors → `warn`.
- For methods listed in `shared.method_order`, verify color assignment matches `shared.color_map` (no swaps).
- Compute pairwise WCAG contrast ratio for adjacent semantic blocks; require ≥ 3:1 for non-text elements, ≥ 4.5:1 for text-on-fill.
- Verify monochrome safety: greyscale-convert the image and re-check whether categories remain distinguishable (Δ luminance ≥ 0.15 between adjacent groups).

Output: `palette: {status, foreign_colors, mono_safe_failures, contrast_failures}`.
</Step>

<Step>
**Pass 4 — Narrative alignment**.
Compare the figure to its `narrative` field:
- Does the figure visually emphasize what the narrative says it should?
  - "highlight: ours" → ours bar/curve must be the visually dominant element (boldest color or larger marker)
  - "left: arch; right: result" → composite must have two panels in that order
- Does the caption (in the section file) restate the narrative claim?

For the cross-figure echo check:
- Method colors match `shared.color_map` across ALL figures
- Module names in architecture diagrams match those in `methodology.typ` (case-sensitive)
- Legend order in plots matches `shared.method_order`

Output: `narrative: {status, echo_failures: [...], emphasis_failures: [...]}`.
</Step>

<Step>
**Pass 5 — Venue grammar**.
Compare against the venue's grammar rules (planner wrote them into the manifest):
- Width ≤ allowed column width
- Caption length within venue's typical bounds (NeurIPS ~ 2–4 lines, Nature panels with bold panel-letters)
- Anonymization for double-blind venues: no identifiable author logos, university shields, dataset watermarks revealing origin
- For IEEE: presence of `\subfloat` equivalents if the figure has sub-panels; for NeurIPS: descriptive caption with self-contained interpretation

Output: `venue: {status, violations: [{rule, evidence}, ...]}`.
</Step>

<Step>
**Pass 6 — Reviewer-target coverage**.
For each `reviewer_targets[*]` from the spec, verify the figure addresses it:
- "significance → error bars must be visible" → check error bars exist on the highlight group
- "param overhead → annotate parameter counts" → check numeric annotations appear next to the relevant blocks
- "regularization choice → ablation panel" → check the panel exists

Output: `reviewer_targets: {status, addressed: [...], unaddressed: [...]}`.
</Step>

<Step>
**Aggregate** all six passes into `paper/figures/<id>.critique.json`:
```json
{
  "fig_id": "fig:arch",
  "passes": {
    "legibility": {"status": "ok"},
    "formulas":   {"status": "warn", "orphaned": ["eq:srra"]},
    "palette":    {"status": "ok"},
    "narrative":  {"status": "ok"},
    "venue":      {"status": "ok"},
    "reviewer_targets": {"status": "fail", "unaddressed": ["param-count overhead"]}
  },
  "overall": "fail",
  "actionable_items": [
    "Move eq:srra adjacent to its srra_block",
    "Add #params annotation under each block (frozen=86M, learnable=2-5M)"
  ]
}
```

Overall status:
- `ok` if all passes ok
- `warn` if no fails and ≥1 warn (drafter may proceed; scientist sees the warning)
- `fail` if any fail (drafter MUST re-draft)
</Step>

<Step>
**Refine loop**. The drafter consumes `actionable_items`, regenerates the
spec with the patches applied, and re-runs the renderer. Maximum 3 refine
iterations per figure. If still failing, escalate to the scientist with the
critique attached.
</Step>
</Steps>

## Refusal rules

- Do NOT pass a figure whose narrative claim is not visible in the render. "Looks fine" is not a verdict — every pass must produce structured output.
- Do NOT downgrade `fail` to `warn` to unblock the pipeline. Escalate instead.
- Do NOT skip Pass 4 (narrative alignment) — it is the quality differentiator vs. generic-template output.
