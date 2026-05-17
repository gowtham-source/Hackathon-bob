---
name: novelty-finder
description: Cross-tabulate the codebase analysis against the literature shortlist to identify novelty claims, prior-art deltas, and reviewer-attack risks
---

Synthesize a sharp novelty statement by comparing this work to its 5 closest
prior-art papers feature-by-feature. Emit `paper/novelty.md`.

<Steps>
<Step>
**Load inputs**:
- `paper/analysis.json` (this work)
- `literature/shortlist.json` (prior art)
</Step>

<Step>
**Pick the 5 closest** prior-art papers via abstract embedding similarity to
`analysis.problem_statement` + `analysis.model.modules[*].name` joined.
</Step>

<Step>
**Build a delta table** with these columns:
| Aspect | This Work | [Author Year]₁ | … | [Author Year]₅ |
| Problem | ... | ... | ... | ... |
| Method  | ... | ... | ... | ... |
| Dataset | ... | ... | ... | ... |
| Metric  | ... | ... | ... | ... |
| Result  | ... | ... | ... | ... |

Mark cells as `=` (same), `Δ` (different), or `?` (unknown).
</Step>

<Step>
**Extract novelty claims** — at most 5, each:
- A single declarative sentence
- Backed by a row of the delta table where this column has `Δ` and at least 2
  competitors have `=`
- Tied to a specific section the paper will use to defend it
</Step>

<Step>
**List reviewer attack risks** — 3–5 likely reviewer questions and your
defense, e.g.:
- "Is the gain real or a seed-luck artifact?" → planned ablation in §4.3
- "Why not compare to [Recent Method]?" → cite + add to baselines table
</Step>

<Step>
**Emit `paper/novelty.md`**:
```markdown
# Novelty Synthesis

## Closest prior work
1. [Author Year] — one-line summary
...

## Delta table
<the table above>

## Novelty claims
1. ... (defends in §X.Y)
...

## Reviewer risks
1. ... → mitigation
...
```
</Step>
</Steps>

The scientist may rewrite this file directly. Re-read it before continuing.
