---
name: section-drafter
description: Draft individual paper sections in Typst with rigorous citation grounding and zero fabricated numbers. Sequential coverage of ALL required sections enforced by a completion checklist; each section is "done" only after verify_bib AND verify_numbers exit 0.
---

Bob alone activates this skill. It defines the rigor for drafting each
section of `paper/sections/*.typ`. **You may not invoke `paper-assembler`
until every required section is "done".**

<Steps>
<Step>
**Required sections by venue** (do not reorder, do not skip):

| Venue | Required sections |
|-------|-------------------|
| NeurIPS, CVPR, ICML | introduction, related_work, methodology, experiments, results, discussion, conclusion, broader_impact, abstract |
| IEEE | introduction, related_work, methodology, experiments, results, discussion, conclusion, abstract |
| Springer-LNCS | introduction, related_work, methodology, experiments, results, discussion, conclusion, abstract |

`abstract.typ` is drafted **last** (after the body stabilizes).
</Step>

<Step>
**Completion checklist** — at the start of every drafting turn, read
`paper/.stage_status.json` and identify the next pending section. Update the
checklist after each section completes. The checklist lives at
`paper/.section_checklist.json`:

```json
{
  "venue": "neurips",
  "required": ["introduction", "related_work", "methodology", "experiments", "results", "discussion", "conclusion", "broader_impact", "abstract"],
  "done": [],
  "pending": ["introduction", "related_work", "methodology", "experiments", "results", "discussion", "conclusion", "broader_impact", "abstract"],
  "blocked": []
}
```

A section moves from `pending` → `done` ONLY after both verifiers exit 0.
</Step>

<Step>
**Per-section protocol** (run for EVERY section, no exceptions):

1. Read all upstream artifacts relevant to the section (table below).
2. Read existing draft (if any) to avoid clobbering scientist edits.
3. Draft directly into `paper/sections/<name>.typ`.
4. **Citation check** (mandatory): `uv run python -m literature.verify_bib paper/sections/<name>.typ`. If exit ≠ 0, fix the missing/wrong keys before continuing — do NOT move to the next section.
5. **Numerical check** (mandatory for any section that contains a digit): `uv run python -m literature.verify_numbers paper/sections/<name>.typ`. If exit ≠ 0, either remove the unsupported number, replace with `[NUM:?]` placeholder, or ask the scientist.
6. Update `paper/.section_checklist.json` (move from `pending` → `done`).
7. Show diff to scientist; ask one specific question per major paragraph.

**Refusal**: if `results/_index.json` does not exist, refuse to draft `results.typ`, `experiments.typ`, `discussion.typ`, or `abstract.typ`. Move them to `blocked` in the checklist and report to the scientist.

| Section | Reads | Forbidden in this section |
|---------|-------|---------------------------|
| introduction | analysis, novelty, plan, figures/_manifest.json | numerical results from §5 |
| related_work | shortlist, novelty | uncited claims, "to the best of our knowledge" without literature support |
| methodology | analysis, novelty, figures/_manifest.json (architecture figure), figures/<arch>.typ | empirical numbers |
| experiments | analysis, plan, tables/_manifest.json (dataset stats, hyperparams) | results numbers (those go in §5) |
| results | results/_index.json, figures/_manifest.json, tables/_manifest.json | speculation about why something works |
| discussion | results + literature | new methods or experiments |
| conclusion | everything above | new claims |
| broader_impact | plan | hand-waving — must be specific |
| abstract | everything finalized | citations |

**Figure/table integration**: every section listed above that consumes a figure or table manifest MUST `#include` or reference the corresponding artifact. The drafter is responsible for adding the `@fig:...` and `@tab:...` references in prose, while the figure/table renderers are responsible for the `#figure(...)` / `#include(...)` themselves. After drafting a section, verify with:
```
uv run python scripts/check_refs.py paper/sections/<name>.typ paper/figures/_manifest.json paper/tables/_manifest.json
```
This script flags any planned figure/table whose `section` matches but is never referenced in prose.
</Step>

<Step>
**Typst citation form**:
- Parenthetical: `#cite(<key>)` → "[12]"
- Prose: `#cite(<key>, form: "prose")` → "Smith et al. [12]"
- Multi: `#cite(<k1>, <k2>, <k3>)` → "[12, 13, 14]"

**Foundational-paper rule**: when introducing a foundational concept (CLIP, Transformer, ViT, ResNet, BERT, …) for the first time, the citation MUST resolve. If `verify_bib` reports the key missing, run a targeted search and re-emit the bibtex BEFORE proceeding:
```
uv run python -m literature.search --queries '{"queries":[{"id":"seed","text":"<concept canonical title>","dimension":"problem","max_results":5}],"sources":["openalex","arxiv","crossref"]}' --out literature/raw/seed/
uv run python -m literature.dedupe --in literature/raw/ --out literature/dedup.json
uv run python -m literature.to_bibtex --in literature/dedup.json --append paper/refs.bib
```
</Step>

<Step>
**Numerical claim form** — every numeric atom traces to a source:
```typst
We achieve an accuracy of $87.3%$ on ImageNet-1k.
// src: results/_index.json#exp_main.accuracy@<git_commit_sha>
```
Numbers from the codebase's existing README/arxiv paper are NOT valid sources unless `results-runner` reproduced them or the scientist explicitly imported them with `source: "external_paper:<bib_key>"` in `results/_index.json`.
</Step>

<Step>
**Completion gate** — only after every required section has `verify_bib` exit 0 AND `verify_numbers` exit 0 may you announce "drafting complete" and request Checkpoint 7 from the scientist. Then activate `paper-assembler`. Do NOT compile the paper from this skill.
</Step>
</Steps>
