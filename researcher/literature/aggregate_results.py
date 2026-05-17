"""Aggregate results/<exp_id>.json files into results/_index.json.

Schema for each input file:
    {"exp_id": "...", "metric": "...", "value": 0.0, "std": 0.0, "seeds": [0,1,2],
     "config_hash": "...", "git_commit": "...", "produced_at": "ISO-8601"}

Output (results/_index.json):
    {"<exp_id>": {"<metric>": {"value": ..., "std": ..., "source": "...", "git_commit": "...", "produced_at": "..."}}}
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=Path, default=Path("results"))
    ap.add_argument("--out", type=Path, default=Path("results/_index.json"))
    args = ap.parse_args()

    idx: dict[str, dict[str, dict]] = {}
    for f in sorted(args.inp.glob("*.json")):
        if f.name == "_index.json":
            continue
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        exp_id = rec.get("exp_id")
        metric = rec.get("metric")
        if not exp_id or not metric:
            continue
        idx.setdefault(exp_id, {})[metric] = {
            "value": rec.get("value"),
            "std": rec.get("std"),
            "seeds": rec.get("seeds"),
            "source": str(f),
            "config_hash": rec.get("config_hash"),
            "git_commit": rec.get("git_commit"),
            "produced_at": rec.get("produced_at"),
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[aggregate_results] indexed {sum(len(v) for v in idx.values())} (exp,metric) pairs  -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
