# Code2Paper

Bob custom mode + skills that turn a working research codebase into a
publication-ready Typst paper for **NeurIPS / CVPR / IEEE / Springer**.

📖 **Full design doc** → [`CODE2PAPER_DESIGN.md`](./CODE2PAPER_DESIGN.md)

## Quick start

```powershell
uv sync
```

Open this folder as a project in Bob, then:

1. Bob auto-loads `.bob/custom_modes.yaml` → mode **📜 Code2Paper** appears.
2. Switch to it.
3. Bob greets you as a **scientist** and asks 3 questions: target venue,
   one-line claim, codebase path.
4. Bob walks you through 8 stages with hard checkpoints. You edit
   `plan.md` directly between stages.

## What's inside

| Path | What it is |
|------|------------|
| `.bob/custom_modes.yaml` | The mode definition |
| `.bob/rules-code2paper/` | The 8-stage workflow brain |
| `.bob/skills/` | 11 skills (analyzer, literature, novelty, plan, drafter, runner, viz, 4 venue templates) |
| `literature/` | Federated search across arXiv, CrossRef, OpenAlex, NCBI, CORE, IEEE, Elsevier, Springer, Wiley |
| `scripts/viz_*.py` | Figure draft + critic loop |
| `paper/` | Typst manuscript artifacts (Bob's writable area) |
| `plan.md` | The contract document — scientist edits to steer the paper |

## Why no MCP?

Embedding loads + multi-source search + experiment runs trip MCP's request
timeout. Skills + the `command` tool work without that ceiling.

See [`CODE2PAPER_DESIGN.md`](./CODE2PAPER_DESIGN.md) for the full story.
