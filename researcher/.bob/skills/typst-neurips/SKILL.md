---
name: typst-neurips
description: Initialize a NeurIPS-formatted Typst paper using the bloated-neurips package and provide drafting conventions specific to NeurIPS submissions
---

Set up `paper/main.typ` for NeurIPS using the
[bloated-neurips](https://typst.app/universe/package/bloated-neurips/) package.

<Steps>
<Step>
**Pre-flight: verify Typst version**. The `bloated-neurips:0.5.0` package
requires Typst ≥ 0.11.1. Run:
```
typst --version
```
If the major.minor.patch is below 0.11.1, STOP and ask the scientist to
upgrade with one of:
```
winget upgrade typst
scoop update typst
cargo install --locked typst-cli
```
If the scientist cannot upgrade, fall back to either:
- An older NeurIPS Typst template (set `package: "@preview/bloated-neurips:0.4.0"` if your Typst is 0.10.x), OR
- A vanilla Typst layout (`paper/main_vanilla.typ`) with manual NeurIPS-style margins; record the choice in `paper/COMPILE_REPORT.md`.

Record the detected version in `paper/.stage_status.json` under `tooling.typst_version`.
</Step>

<Step>
**Initialize** `paper/main.typ` from `template.typ` in this skill folder.
Replace placeholders: `<TITLE>`, `<AUTHORS>`, `<KEYWORDS>`. Pull the title
from the **Selected title** field in `plan.md` — NOT from the codebase's
README/arxiv title.
Set the option `accepted: false` until the scientist confirms acceptance
status.
</Step>

<Step>
**Install** the package once via:
```
typst init @preview/bloated-neurips:0.5.0
```
or rely on Typst's package auto-fetch on first compile.
</Step>

<Step>
**Drafting rules for NeurIPS**:
- Page limit: 9 pages of main text + unlimited references + appendix
- Author block hidden during double-blind review (`accepted: false`)
- **Broader Impact** section is mandatory before References for accepted papers
- Use `\citet` style via Typst's `#cite(<key>, form: "prose")` for in-text
  author citations and `#cite(<key>)` for parenthetical
- Math: prefer aligned environments via `$ ... $` blocks
- Algorithms: use the `lovelace` Typst package
</Step>

<Step>
**Compile** with:
```
typst compile paper/main.typ paper/main.pdf
```
Watch mode for iterative drafting:
```
typst watch paper/main.typ paper/main.pdf
```
</Step>

<Step>
**Section file convention**: Bob writes section bodies to
`paper/sections/<name>.typ` and includes them in `main.typ` via
`#include "sections/intro.typ"`.
</Step>
</Steps>
