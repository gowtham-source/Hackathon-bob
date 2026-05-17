"""Verify every numeric value next to a // src: comment in a Typst file
matches the value recorded in results/_index.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Match patterns like:
#   ... 87.3% ...
#   // src: results/_index.json#exp_main.accuracy@<commit>
NUMBER_RE = re.compile(r"([-+]?\d+\.?\d*)\s*%?")
SRC_RE = re.compile(r"//\s*src:\s*results/_index\.json#([\w.-]+)\.([\w.-]+)(?:@\S+)?")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: verify_numbers <typst_file> [<typst_file> ...]", file=sys.stderr)
        return 2
    idx_path = Path("results/_index.json")
    if not idx_path.exists():
        print(f"missing {idx_path}", file=sys.stderr)
        return 1
    idx = json.loads(idx_path.read_text(encoding="utf-8"))

    issues: list[str] = []
    for f in argv[1:]:
        lines = Path(f).read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = SRC_RE.search(line)
            if not m:
                continue
            exp_id, metric = m.group(1), m.group(2)
            entry = idx.get(exp_id, {}).get(metric)
            if entry is None:
                issues.append(f"{f}:{i+1}  unknown {exp_id}.{metric}")
                continue
            # number on the same or previous line
            target = lines[i] + " " + (lines[i - 1] if i > 0 else "")
            nums = [float(x) for x in NUMBER_RE.findall(target)]
            if not nums:
                continue
            recorded = float(entry["value"])
            if not any(abs(n - recorded) < 1e-3 or abs(n - recorded * 100) < 1e-3 for n in nums):
                issues.append(
                    f"{f}:{i+1}  number mismatch — {nums} vs recorded {recorded}"
                )
    if issues:
        for x in issues:
            print(x)
        return 1
    print("[verify_numbers] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
