---
name: plan-writer
description: Write the publication plan (plan.md) — title candidates, abstract skeleton, full section/subsection outline, methodology schema, figure & table lists, citation map, and open questions
---

Produce `plan.md` at the project root. This file is the contract between Bob
and the scientist; the scientist edits it directly to steer the rest of the
paper.

<Steps>
<Step>
**Read all upstream artifacts**:
- `paper/analysis.json`
- `literature/shortlist.json`
- `paper/novelty.md`
</Step>

<Step>
**Use the template** at `plan-template.md` (in this skill folder) and populate
every placeholder. Do not leave any `<...>` placeholders unfilled — if you
genuinely don't know, write `[OPEN QUESTION: ...]` and add it to the
"Open questions" section at the end.
</Step>

<Step>
**Title generation (mandatory)**: produce at least 5 candidate titles. Run
this distinctness check before writing them:
1. Extract the codebase's original title from `README.md` (first H1) and
   `paper/analysis.json.related_work_context.arxiv_links` (if present, fetch
   the arxiv page title).
2. Normalize: lowercase, drop punctuation, collapse whitespace.
3. For each candidate, ensure normalized form differs from the codebase
   title by Levenshtein ≥ 8 characters.
4. At least 2 candidates must reframe from non-method angles
   (problem/application/theory/result).
5. Record the codebase original title in the template's "Codebase original
   title" field for the scientist's review.
If you cannot produce 5 distinct candidates, STOP and ask the scientist
for angle preferences before writing `plan.md`.
</Step>

<Step>
**Methodology schema** — break the method down into:
- Sub-topics (one per algorithmic component)
- For each sub-topic: a one-paragraph summary, an equation if applicable
  (Typst math syntax `$ ... $`), a reference to the source-code symbol that
  implements it, and the citations that motivate it
</Step>

<Step>
**Figure list** — one row per planned figure:
| Fig | Caption | Data source | Visualization type | Section |

**Table list** — one row per planned table:
| Tab | Title | Schema (columns) | Data source | Section |
</Step>

<Step>
**Citation map** — list every `@key` you intend to cite, with the section it
supports. The set must be a subset of `literature/shortlist.json` keys.
</Step>

<Step>
**Open questions** — anything you couldn't decide alone. The scientist will
answer these in their edit pass.
</Step>
</Steps>

After saving, present a 5-line summary to the scientist and invite edits.
Re-read `plan.md` before activating the venue skill.
