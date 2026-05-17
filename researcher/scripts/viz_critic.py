"""Heuristic critic for paper figures.

Reads a figure SVG and its spec, returns issues against the constraints.
This is a deterministic rule-based critic — for an LLM-based critic
(e.g., nano-banana / paperbanana), swap the body of `critique` with a
multimodal call.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def critique(spec: dict, svg_text: str) -> list[dict]:
    issues: list[dict] = []
    constraints = spec.get("constraints", {})
    # Font check (very rough — looks for font-size attrs in SVG)
    sizes = [float(m) for m in re.findall(r'font-size="([\d.]+)', svg_text)]
    min_pt = constraints.get("min_font_pt", 8)
    if sizes and min(sizes) < min_pt:
        issues.append({"severity": "high", "msg": f"font-size {min(sizes)}pt < min {min_pt}pt"})
    # Highlight visibility — check if highlight color appears
    highlight = spec.get("highlight")
    if highlight and highlight not in svg_text and "#d62728" not in svg_text:
        issues.append({"severity": "medium", "msg": f"highlight group {highlight!r} not visually emphasized"})
    # Narrative check — placeholder; a real critic should re-render and OCR
    if not spec.get("narrative"):
        issues.append({"severity": "low", "msg": "spec.narrative is empty — figure has no claim"})
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    svg_text = args.image.read_text(encoding="utf-8") if args.image.suffix == ".svg" else ""
    issues = critique(spec, svg_text)
    status = "ok" if not issues else "needs_refinement"
    out = {"status": status, "issues": issues, "spec": str(args.spec), "image": str(args.image)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
