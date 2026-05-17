---
name: codebase-analyzer
description: Analyze a research codebase and extract problem statement, model architecture, datasets, training pipeline, evaluation protocol, and existing results into paper/analysis.json
---

Perform a structured analysis of the active codebase to extract every fact
needed to write a research paper. Output a single JSON file at
`paper/analysis.json`.

<Steps>
<Step>
**Discover entry points**
- Read `README.md`, `pyproject.toml` / `requirements.txt`, top-level `*.py` files.
- Identify the training script (`train.py`, `main.py`), eval script
  (`eval.py`, `test.py`), and config files (`*.yaml`, `*.json` under `configs/`).
</Step>

<Step>
**Extract problem statement**
- Pull the first 2 paragraphs of README.md.
- Pull docstrings of the top-level modules.
- Synthesize a 3-sentence problem statement.
</Step>

<Step>
**Map the model architecture**
- Locate model definitions (subclasses of `nn.Module`, `keras.Model`,
  `flax.linen.Module`, `torch.nn.Module`).
- For each module: name, file:line, layer composition, input/output shapes
  if computable from forward signatures.
- Compute parameter count by running:
  `uv run python -c "from <model_module> import <Model>; m=<Model>(); print(sum(p.numel() for p in m.parameters()))"`
  in a try/except. If construction fails, record the error and move on.
</Step>

<Step>
**Identify datasets**
- Search for `Dataset`, `DataLoader`, `tf.data`, `datasets.load_dataset`.
- Capture: name, path, splits (train/val/test sizes if available), preprocessing.
</Step>

<Step>
**Extract training pipeline**
- Optimizer + learning rate + scheduler.
- Loss function(s).
- Batch size, epochs/steps.
- Mixed precision / distributed setup.
- Random seed handling.
</Step>

<Step>
**Extract evaluation protocol**
- Metrics computed (accuracy, F1, BLEU, FID, etc.).
- Splits used, number of runs / seeds.
</Step>

<Step>
**Harvest existing results**
- Scan `results/`, `outputs/`, `logs/`, `runs/`, `wandb/`, `tensorboard/`, `*.csv`, `*.json`.
- Parse what you can; record raw paths for the rest.
- Build `results/_index.json` mapping `(experiment_id, metric)` → value + source file + last-modified time.
</Step>

<Step>
**Identify gaps**
- Missing baselines (no comparable model run).
- Missing ablations (no config-variant runs).
- Missing plots / figures.
- Missing dataset statistics tables.
- Missing reproducibility info (seed sweeps, std deviations).
</Step>

<Step>
**Emit paper/analysis.json** with this exact schema:

```json
{
  "problem_statement": "string (3 sentences)",
  "model": {
    "modules": [{"name": "...", "file": "...", "params": 12345, "shape": "..."}],
    "total_params": 0,
    "framework": "pytorch|tensorflow|jax|..."
  },
  "datasets": [{"name": "...", "path": "...", "splits": {...}, "preprocessing": "..."}],
  "training": {"optimizer": "...", "lr": 0.001, "scheduler": "...", "loss": "...", "batch_size": 0, "epochs": 0, "seed": 0, "distributed": false, "mixed_precision": false},
  "evaluation": {"metrics": ["..."], "splits": ["..."], "num_seeds": 1},
  "results": {"available": [...], "missing": [...]},
  "gaps": ["missing baseline X", "no ablation on Y", "..."],
  "produced_at": "ISO-8601"
}
```
</Step>
</Steps>

Use `read` and `command` tools only. Do not edit source code. Do not write
Typst. Do not invent numbers — if a value cannot be extracted, set it to `null`
and add a string to `gaps`.
