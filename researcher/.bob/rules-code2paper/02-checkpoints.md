# Checkpoint Protocol

A checkpoint is a forced stop. You present a structured summary, then you wait
for the scientist's reply before invoking the next skill.

## Checkpoint message template

```
### Checkpoint <N> — <stage name>

**Artifact produced**: `<path>`
**Summary** (≤10 bullets):
- ...

**Decisions needed from you**:
- [ ] Approve / amend bullet 1
- [ ] Approve / amend bullet 2
- [ ] (specific question)

Reply with: `approved`, `approved with edits: <text>`, or paste edits directly.
I will re-read the artifact before continuing.
```

## Editable artifacts (scientist may freely edit)

| Stage | Artifact | Bob re-reads before continuing |
|-------|----------|--------------------------------|
| 1 | `paper/analysis.json` | yes |
| 2 | `literature/shortlist.json`, `paper/queries.json` | yes |
| 3 | `paper/novelty.md` | yes |
| 4 | `plan.md` | yes |
| 5 | `results/_index.json`, `experiments/*.py`, `configs/*.yaml` | yes |
| 6 | `paper/figures/*` | yes |
| 7 | `paper/sections/*.typ`, `paper/main.typ`, `paper/refs.bib` | yes |
| 8 | `paper/COMPILE_REPORT.md` | yes |

## Refusal conditions (do NOT proceed past a checkpoint if)

- The scientist has not given an explicit approval signal.
- A required upstream artifact is missing or empty.
- A verifier (`verify_bib`, `verify_numbers`) reported errors that have not been fixed.
- The skill output contains placeholder `<...>` tokens that should have been filled.

## Stage status tracking

After every stage, append/update `paper/.stage_status.json`:
```json
{
  "stages": [
    {"n": 1, "name": "analysis", "status": "done", "checkpoint_approved": true, "produced_at": "..."},
    {"n": 2, "name": "literature", "status": "done", "checkpoint_approved": true},
    {"n": 7, "name": "drafting", "status": "in_progress", "sections_done": ["abstract", "introduction"], "sections_pending": ["related_work", "methodology", "experiments", "results", "discussion", "conclusion", "broader_impact"]}
  ]
}
```

Bob reads this file at the start of every conversation turn to know where it
left off. No section is "done" until its `verify_bib` and `verify_numbers`
checks pass.
