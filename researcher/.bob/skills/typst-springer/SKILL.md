---
name: typst-springer
description: Initialize a Springer Lecture Notes / journal-formatted Typst paper using the springer-spaniel package
---

Set up `paper/main.typ` for Springer (LNCS, LNAI, or generic journal) using
[springer-spaniel](https://typst.app/universe/package/springer-spaniel/).

<Steps>
<Step>
**Pre-flight: verify Typst version** (≥ 0.11.1 required). Run `typst --version`; if older, fall back to a compatible package version or ask the scientist to upgrade. Record in `paper/.stage_status.json` under `tooling.typst_version`. Pull the title from `plan.md`'s **Selected title** field, NOT from the codebase's README.
</Step>

<Step>
**Initialize** `paper/main.typ` from `template.typ` in this skill folder.
</Step>

<Step>
**Springer drafting rules**:
- Single-column for LNCS, two-column for some journal variants
- Mandatory `keywords` block immediately after the abstract
- Springer's BibTeX style: `splncs04` — emit `paper/refs.bib` in a Springer-
  compatible form (the package handles the citation rendering)
- Acknowledgements and Funding go in dedicated unnumbered sections at the end
- Page limits vary widely by series — confirm with scientist
</Step>

<Step>
**Compile**:
```
typst compile paper/main.typ paper/main.pdf
```
</Step>
</Steps>
