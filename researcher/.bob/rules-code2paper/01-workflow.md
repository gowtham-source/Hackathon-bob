# Code2Paper Workflow Rules

You operate in **9 sequential stages**. Each stage has a hard **refusal rule** —
if its precondition is not met, you MUST stop and ask the scientist instead of
proceeding. You MUST NOT declare the task complete until **Stage 9** finishes.

After every stage you write the stage status into `paper/.stage_status.json`:
```json
{ "stage": 1, "name": "analysis", "status": "done", "checkpoint_approved": true, "produced_at": "ISO" }
```

## Stage 0 — Intake (no skill)
Ask three questions:
1. **Target venue** (NeurIPS / CVPR / ICML / IEEE / Springer-LNCS).
2. **One-sentence claim of contribution.**
3. **Codebase root** (default: project root).

Refuse to proceed if any are unanswered.

## Stage 1 — Codebase analysis
Skill: `codebase-analyzer` → `paper/analysis.json`.
**Checkpoint 1**: present the 10-bullet summary; require explicit `approved` from scientist.

## Stage 2 — Literature search
Skill: `literature-search` → `literature/shortlist.json`, `paper/refs.bib`.
**Refusal**: do not proceed if `paper/refs.bib` has fewer than 10 entries OR foundational seeds for the domain are missing (see `literature-search/SKILL.md` foundational-seeds clause).
**Checkpoint 2**: shortlist table; scientist may add/remove papers.

## Stage 3 — Novelty synthesis
Skill: `novelty-finder` → `paper/novelty.md`.
**Checkpoint 3**: scientist must approve the 5 novelty claims and accept reviewer-risk mitigations OR amend them.

## Stage 4 — Publication plan
Skill: `plan-writer` → `plan.md`.
**Refusal**: title candidates section MUST contain ≥5 candidates AND none may be string-equal (case-insensitive) to the codebase's existing arxiv/README title. If the codebase has a method name (e.g. "MMRL"), the plan must explicitly select either (a) keep the method name with a NEW reframing subtitle, or (b) propose a new name with rationale.
**Checkpoint 4**: scientist edits `plan.md` directly; you re-read it before continuing.

## Stage 5 — Results runner (gap closure)
Skill: `results-runner` → `experiments/<exp_id>.py`, `results/<exp_id>.json`, `results/_index.json`.
**Refusal**: do not skip this stage when `analysis.json.gaps` lists missing experiments AND `plan.md` references their numbers. If the scientist explicitly waives execution (e.g. results live elsewhere), they must paste a `results/_index.json` themselves; you record the waiver in `.stage_status.json`.
**Checkpoint 5**: present `results/_index.json` summary table.

## Stage 6 — Figures & Tables (multi-agent)

This stage runs as a four-phase pipeline:

**6a. Figure planning** — Skill: `figure-planner` → `paper/figures/_manifest.json`.
- Decides where figures belong, intent, type, venue grammar, equation integration, reviewer-target coverage.
- **Refusal**: do not include a figure whose `data_source` doesn't exist; mark it `blocked`.
- **Checkpoint 6a**: scientist approves the figure list + palette.

**6b. Table planning** — Skill: `table-generator` (planning phase) → `paper/tables/_manifest.json`.
- Emits standard table set (main results, ablation, efficiency, dataset stats, etc.).
- **Refusal**: do not skip a `required: true` table. A research paper without a main-results table is incomplete.
- **Checkpoint 6b**: scientist approves the table list + schemas.

**6c. Drafting** — Skill: `figure-drafter` + `table-generator` (rendering phase) → `paper/figures/*` + `paper/tables/*.typ`.
- Architecture diagrams via Typst CeTZ/fletcher.
- Plots via matplotlib with venue stylesheet.
- Qualitative grids via PIL composer (PaperBanana-style but stricter).
- Tables via `scripts/table_gen.py`.

**6d. Critique loop** — Skill: `figure-critic` → `paper/figures/<id>.critique.json`.
- Six independent passes per figure: legibility, formula correctness, palette, narrative alignment, venue grammar, reviewer-target coverage.
- Max 3 refine iterations per figure/table; escalate on persistent fail.
- **Refusal**: do not enter Stage 7 while any required figure or table has `overall: "fail"` and no scientist waiver.

**Checkpoint 6**: scientist reviews the rendered figure+table portfolio with critique summary.

## Stage 7 — Section drafting
Skill: `section-drafter` (orchestrates the venue skill `typst-<venue>`).
**Refusal**: do not begin drafting `results.typ`, `experiments.typ`, `discussion.typ`, or `abstract.typ` until `results/_index.json` exists. Do not begin drafting *any* section until `plan.md` is approved AND `paper/refs.bib` is verified by `literature.verify_bib`.
**Per-section gate** (enforced by section-drafter): after writing each `.typ`, run `verify_bib` and `verify_numbers`; the section is "done" only when both exit 0.
**Checkpoint 7**: After ALL 9 sections (including `broader_impact.typ` for NeurIPS/CVPR) reach "done", present a section-completion checklist.

## Stage 8 — Paper assembly + compile
Skill: `paper-assembler` → `paper/main.pdf`, `paper/COMPILE_REPORT.md`.
**Refusal**: do not enter Stage 9 until `main.pdf` exists and `COMPILE_REPORT.md` lists zero unresolved gaps OR the scientist has accepted each remaining gap in writing.
**Checkpoint 8**: scientist reviews compiled PDF.

## Stage 9 — Final review handoff
Produce a final summary in chat with:
- Path to `paper/main.pdf`
- Path to `paper/COMPILE_REPORT.md`
- Outstanding TODOs (must be empty unless scientist accepted them)
- Reproducibility command set (one block of shell commands that regenerates the PDF from scratch)

Only after Stage 9 may you say the task is complete.

## Hard refusal rules (apply across all stages)

- **No fabricated numbers**: every `%`, `±`, count, or scaling factor in any `.typ` file must be traceable. If unsure, write `[NUM:?]` and add a TODO.
- **No fabricated citations**: every `#cite(<key>)` must resolve in `paper/refs.bib`. The verifier runs after every section.
- **No silent skipping**: if a stage's preconditions fail, stop and present the missing artifact to the scientist; do not invent it.
- **No premature completion**: the only valid "task complete" message is the Stage 9 final summary.
