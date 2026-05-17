"""Deduplicate raw search results across sources.

Strategy:
  1. group by DOI when present
  2. group remaining by normalized title prefix
  3. merge fields, prefer the record with the longest abstract / most citations
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def norm_title(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        if not out.get(k) and v:
            out[k] = v
    out["abstract"] = a["abstract"] if len(a.get("abstract", "")) >= len(b.get("abstract", "")) else b["abstract"]
    out["citations"] = max(int(a.get("citations") or 0), int(b.get("citations") or 0))
    sources = set(a.get("sources") or [a.get("source")] if a.get("source") else [])
    sources.update(b.get("sources") or [b.get("source")] if b.get("source") else [])
    out["sources"] = sorted(s for s in sources if s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    records: list[dict] = []
    for f in sorted(args.inp.glob("*.json")):
        records.extend(json.loads(f.read_text(encoding="utf-8")))

    by_doi: dict[str, dict] = {}
    by_title: dict[str, dict] = {}
    for r in records:
        doi = (r.get("doi") or "").strip().lower()
        if doi:
            by_doi[doi] = merge(by_doi[doi], r) if doi in by_doi else r
            continue
        t = norm_title(r.get("title", ""))
        if not t:
            continue
        key = t[:80]
        by_title[key] = merge(by_title[key], r) if key in by_title else r

    deduped = list(by_doi.values()) + list(by_title.values())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(deduped, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[dedupe] {len(records)} -> {len(deduped)} records  -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
