"""Federated search CLI: ``uv run python -m literature.search``.

Reads ``paper/queries.json``, fans out across configured sources, and writes
one JSON file per source under ``literature/raw/``.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

from .sources import ALL_SEARCHERS

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("literature.search")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    spec = json.loads(args.queries.read_text(encoding="utf-8"))
    queries = spec["queries"]
    sources = spec.get("sources") or list(ALL_SEARCHERS)
    args.out.mkdir(parents=True, exist_ok=True)

    for src_name in sources:
        cls = ALL_SEARCHERS.get(src_name)
        if not cls:
            log.warning("unknown source %s — skipping", src_name)
            continue
        searcher = cls()
        if not searcher.available():
            log.warning("[%s] not available (missing %s) — skipping", src_name, searcher.requires_key)
            continue
        merged: list[dict] = []
        for q in queries:
            log.info("[%s] querying %r", src_name, q["text"])
            papers = searcher.safe_search(q["text"], max_results=q.get("max_results", 30))
            for p in papers:
                d = p.to_dict()
                d["_query_id"] = q["id"]
                merged.append(d)
        out_file = args.out / f"{src_name}.json"
        out_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("[%s] wrote %d records -> %s", src_name, len(merged), out_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
