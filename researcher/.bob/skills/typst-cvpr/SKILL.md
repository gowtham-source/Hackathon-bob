---
name: typst-cvpr
description: Initialize a CVPR/ICCV-formatted Typst paper using the blind-cvpr package; enforce double-blind anonymization and CVPR style rules
---

Set up `paper/main.typ` for CVPR/ICCV using the
[blind-cvpr](https://typst.app/universe/package/blind-cvpr/) package.

<Steps>
<Step>
**Pre-flight: verify Typst version** (≥ 0.11.1 required). Run `typst --version`; if older, ask the scientist to upgrade or fall back to a compatible package version. Record the detected version in `paper/.stage_status.json` under `tooling.typst_version`.
</Step>

<Step>
**Initialize** `paper/main.typ` from `template.typ` in this skill folder.
</Step>

<Step>
**Anonymization invariants** (MUST hold during review):
- Set `anonymous: true` until the camera-ready phase
- Pull the title from `plan.md`'s **Selected title** field — NOT from the codebase's README/arxiv title.
- Replace placeholder self-citations of the form "we previously showed [our prior]"
  with "[Anonymous] showed [11]" patterns
- Strip institution names, acknowledgments, and grant numbers from drafts
- The `blind-cvpr` package automatically blanks the author block when
  `anonymous: true`
</Step>

<Step>
**CVPR drafting rules**:
- Page limit: 8 pages of main text + 2 pages of references (no appendix in
  main submission)
- Two-column layout, 10pt font (handled by package)
- Figures: prefer single-column when possible to save space; use `figure.where(placement: top)` rules
- Math: numbered equations with `#math.equation(numbering: "(1)", ...)`
</Step>

<Step>
**Compile**:
```
typst compile paper/main.typ paper/main.pdf
```
</Step>
</Steps>
