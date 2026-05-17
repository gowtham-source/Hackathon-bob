---
name: results-runner
description: Fill experimental gaps identified in analysis.json — write missing experiment scripts, get scientist approval, execute, and parse results into results/_index.json
---

Activate when `paper/analysis.json.gaps` lists missing experiments (e.g., a
required ablation, a missing baseline, a per-seed std-dev sweep) that the
paper's claims will rely on.

<Steps>
<Step>
**Re-read** `paper/analysis.json` and `plan.md` to understand exactly which
experiments are required and which are missing.
</Step>

<Step>
**For each missing experiment**, draft a standalone script under
`experiments/<exp_id>.py`. Conventions:
- Reads config from `configs/<exp_id>.yaml`
- Writes raw output to `results/raw/<exp_id>/`
- Emits a summary JSON at `results/<exp_id>.json` with schema:
  ```json
  {"exp_id": "...", "metric": "...", "value": 0.0, "std": 0.0, "seeds": [0,1,2], "config_hash": "...", "git_commit": "...", "produced_at": "ISO-8601"}
  ```
</Step>

<Step>
**Show the script to the scientist** before executing. They may edit it. Wait
for explicit approval.
</Step>

<Step>
**Execute**:
```
uv run python experiments/<exp_id>.py --config configs/<exp_id>.yaml
```
For long-running experiments (>10 min), spawn as a background command and
poll its log file every 60s. Report progress.
</Step>

<Step>
**Aggregate** all `results/<exp_id>.json` into `results/_index.json` after
each run:
```
uv run python -m literature.aggregate_results --in results/ --out results/_index.json
```
</Step>

<Step>
**Never fabricate** a number. If a run crashes, report the crash to the
scientist with the traceback and ask whether to retry, debug, or omit the
claim from the paper.
</Step>
</Steps>
