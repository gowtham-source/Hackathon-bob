---
name: paper-assembler
description: Final-stage skill. Verify all required sections present, run verify_bib + verify_numbers across the entire manuscript, compile main.typ to PDF, and emit COMPILE_REPORT.md listing any unresolved gaps. The ONLY skill allowed to produce paper/main.pdf.
---

This skill runs as Stage 8. It is the gate that turns a directory of `.typ`
files into a single deliverable PDF. Bob must NOT compile the paper from any
other skill.

<Steps>
<Step>
**Read** `paper/.section_checklist.json` and `paper/.stage_status.json`. If
any required section is in `pending` or `blocked`, STOP and ask the scientist:
they must either (a) approve a partial-paper compile (recorded as a waiver in
COMPILE_REPORT.md) or (b) return to `section-drafter` to finish the missing
sections.
</Step>

<Step>
**Whole-manuscript citation check**:
```
uv run python -m literature.verify_bib paper/main.typ paper/sections/*.typ
```
Collect every unresolved key. Do NOT silently drop them — list each in
COMPILE_REPORT.md under "Unresolved citations" with the source file + line.
</Step>

<Step>
**Whole-manuscript numerical check**:
```
uv run python -m literature.verify_numbers paper/sections/*.typ
```
List each unsupported number under "Unverified numbers" in COMPILE_REPORT.md.
If `results/_index.json` does not exist at all, the report's first line must
be a bold warning to the scientist.
</Step>

<Step>
**Title sanity check**: read the `title:` argument in `paper/main.typ`. Read
the codebase's original title (README H1 + arxiv link). If they are
string-equal (case-insensitive, ignoring punctuation), STOP and request a new
title from `plan.md`'s "Selected title" field. Refuse to compile until
`main.typ`'s title matches `plan.md`.
</Step>

<Step>
**Figure & table portfolio check**:
1. Load `paper/figures/_manifest.json` and `paper/tables/_manifest.json`.
2. Every entry with `required: true` MUST have a corresponding rendered artifact on disk AND a passing critique (`overall: "ok"` or scientist-waived `warn`).
3. Every `required: true` figure/table MUST be referenced (`@fig:...` / `@tab:...`) at least once in the section file matching its `section` field.
4. Run `uv run python scripts/check_refs.py paper/sections/*.typ paper/figures/_manifest.json paper/tables/_manifest.json` and append unresolved references under "Missing figure/table references" in COMPILE_REPORT.md.
5. Cross-figure echo check: confirm `shared.color_map` and `shared.method_order` from the figures manifest are consistent with column order in the tables manifest.
</Step>

<Step>
**Section-include sanity check**: parse `paper/main.typ` for every
`#include "sections/<name>.typ"`. Confirm each file exists and is non-empty
(>200 chars). Missing or stub sections go in COMPILE_REPORT.md under
"Missing section bodies" and abort the compile.
</Step>

<Step>
**Compile** to PDF:
```
typst compile paper/main.typ paper/main.pdf --root .
```
Capture stdout/stderr to `paper/.compile.log`. If exit ≠ 0:
- Parse the first error.
- If it's a Typst version mismatch, link to `typst-<venue>` skill's pre-flight step and STOP.
- If it's a missing package, run `typst install <package>` and retry once.
- If it's a syntax error, locate the offending `.typ` file:line, fix only obvious typos, and retry once. Otherwise STOP and surface the error.
</Step>

<Step>
**Emit `paper/COMPILE_REPORT.md`** with this template:

```markdown
# Compile Report — <ISO timestamp>

**PDF**: `paper/main.pdf` (<size> bytes, <pages> pages)
**Typst version**: <version>
**Git commit**: <sha>

## Section completion
- [x] introduction
- [x] related_work
- ...

## Verification status
- verify_bib: <PASS | N errors>
- verify_numbers: <PASS | N errors>
- title distinctness: <PASS | FAIL>

## Unresolved citations
| File | Line | Key | Action |
|------|------|-----|--------|

## Unverified numbers
| File | Line | Number | Suggested source |
|------|------|--------|------------------|

## Open TODOs (must be empty before submission)
- [ ] ...

## Reproducibility
```bash
uv run python -m literature.search --queries paper/queries.json --out literature/raw/
uv run python -m literature.dedupe --in literature/raw/ --out literature/dedup.json
uv run python -m literature.rank --in literature/dedup.json --top 30 --out literature/shortlist.json
uv run python -m literature.to_bibtex --in literature/shortlist.json --out paper/refs.bib
uv run python -m literature.aggregate_results --in results/ --out results/_index.json
typst compile paper/main.typ paper/main.pdf --root .
```
```
</Step>

<Step>
**Hand back** to Bob a 5-line chat summary:
- PDF path + page count
- Verifier statuses (PASS/FAIL counts)
- Number of open TODOs
- Whether the title differs from the codebase's original
- Stage 9 next-action prompt for the scientist

Only after this summary may Bob announce task completion (Stage 9).
</Step>
</Steps>

## Refusal rules
- Do not compile if any required section is missing AND no waiver is recorded.
- Do not compile if `verify_bib` reports an unresolved foundational citation.
- Do not compile if `paper/main.typ`'s title equals the codebase's original title.
- Do not declare success while `paper/main.pdf` does not exist on disk.
