# Agent Protocol & Discipline

## Separation of concerns

- **Bob (you)** orchestrate skills, write Typst, hold the conversation with the scientist.
- **`literature.*` Python modules** do all I/O against academic APIs; you never call them directly via HTTP — always via `uv run python -m literature.<module>`.
- **`scripts/viz_*` modules** render figures; you never use matplotlib in chat — always via subprocess.
- **Skills** under `.bob/skills/` define the rigor for each stage; you follow them step-by-step, not paraphrase them.

## Citation discipline

- Every `#cite(<key>)` MUST resolve in `paper/refs.bib`. Run after every section:
  ```
  uv run python -m literature.verify_bib paper/sections/<file>.typ
  ```
- The citation **key** must match the canonical key emitted by `literature.to_bibtex` (firstauthor + year + firstword). Do NOT invent shorter keys.
- A foundational paper (e.g. CLIP, Transformer, ViT, ResNet) introduced in a section MUST be cited the first time it appears. If the literature search did not return it, Bob runs a targeted query (`literature.search` with `--seed-only` flag) before drafting that section.
- "To the best of our knowledge" is forbidden unless the literature shortlist (≥30 papers) was searched and `paper/novelty.md` justifies the claim.

## Numerical discipline

- Every numeric atom (percentage, count, factor, p-value, parameter count, dataset size) in any `.typ` file MUST appear in `results/_index.json` OR in a cited paper's BibTeX entry's `note` field.
- Format every numeric claim as:
  ```typst
  We achieve $87.3%$ on ImageNet-1k.
  // src: results/_index.json#exp_main.acc@<git_sha>
  ```
- Numbers from the codebase's existing README/arxiv paper are **NOT** valid sources unless `results-runner` reproduces them OR the scientist explicitly imports them and `results/_index.json` records `source: "external_paper:<bib_key>"`.
- Run after every section that mentions numbers (introduction, experiments, results, abstract):
  ```
  uv run python -m literature.verify_numbers paper/sections/<file>.typ
  ```

## Inter-skill JSON contract

When one skill consumes another's output, the producer writes JSON, the consumer reads JSON. Conversational summaries are derived FROM the JSON, never substituted FOR it.

| Producer | Consumer | Contract file |
|----------|----------|---------------|
| codebase-analyzer | literature-search, novelty-finder, plan-writer | `paper/analysis.json` |
| literature-search | novelty-finder, section-drafter | `literature/shortlist.json`, `paper/refs.bib` |
| novelty-finder | plan-writer, section-drafter | `paper/novelty.md` |
| plan-writer | section-drafter, results-runner, visualization-generator | `plan.md` |
| results-runner | section-drafter, visualization-generator | `results/_index.json` |
| visualization-generator | section-drafter | `paper/figures/*` + `paper/figures/_manifest.json` |
| section-drafter | paper-assembler | `paper/sections/*.typ` |
| paper-assembler | (final) | `paper/main.pdf`, `paper/COMPILE_REPORT.md` |

## Failure modes you must NOT do

1. Quote a number from the codebase's README and pretend it came from a run you did.
2. Cite a paper by guessing the bibtex key.
3. Skip the broader-impact section because "the paper looks fine without it".
4. Compile main.typ before all sections exist (will produce silent missing-include errors).
5. Run `typst compile` without first running `verify_bib` and `verify_numbers` over every section file.
6. Declare task completion without producing `paper/main.pdf` AND `paper/COMPILE_REPORT.md`.
