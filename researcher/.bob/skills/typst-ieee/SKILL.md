---
name: typst-ieee
description: Initialize an IEEE-formatted Typst paper using the charged-ieee package for transactions/conference submissions
---

Set up `paper/main.typ` for IEEE using the
[charged-ieee](https://typst.app/universe/package/charged-ieee/) package.

<Steps>
<Step>
**Pre-flight: verify Typst version** (≥ 0.11.1 required). Run `typst --version`; if older, fall back to a compatible package version or ask the scientist to upgrade. Record in `paper/.stage_status.json` under `tooling.typst_version`. Pull the title from `plan.md`'s **Selected title** field, NOT from the codebase's README.
</Step>

<Step>
**Initialize** `paper/main.typ` from `template.typ` in this skill folder.
Choose the `paper-type`: `"conference"` (default) or `"journal"` for
IEEE Transactions.
</Step>

<Step>
**IEEE drafting rules**:
- Two-column, 10pt
- Page limit varies by venue — confirm with scientist
- Mandatory "Index Terms" block after the abstract
- Author bios at end for journal papers (`paper-type: "journal"`)
- BibTeX style: `ieeetran`-equivalent provided by the package
- Figures: place at top of column; cross-reference with `@fig:label`
</Step>

<Step>
**Compile**:
```
typst compile paper/main.typ paper/main.pdf
```
</Step>
</Steps>
