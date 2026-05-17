"""Rank deduplicated papers via 0.5*relevance + 0.3*recency + 0.2*log(citations+1).

Relevance = max cosine similarity between the paper abstract and any query
text, computed with sentence-transformers (lazy-loaded, downloads on first use).
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np


def load_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=Path, required=True)
    ap.add_argument("--queries", type=Path, default=Path("paper/queries.json"))
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    records: list[dict] = json.loads(args.inp.read_text(encoding="utf-8"))
    queries = json.loads(args.queries.read_text(encoding="utf-8")).get("queries", [])
    query_texts = [q["text"] for q in queries] or ["research"]

    model = load_embedder()
    q_emb = np.array(model.encode(query_texts, normalize_embeddings=True))
    abstracts = [(r.get("abstract") or r.get("title") or "")[:2000] for r in records]
    a_emb = np.array(model.encode(abstracts, normalize_embeddings=True))
    sims = a_emb @ q_emb.T  # shape (N, Q)
    relevance = sims.max(axis=1)

    cur_year = datetime.utcnow().year
    for i, r in enumerate(records):
        year = int(r.get("year") or cur_year - 10)
        recency = math.exp(-(cur_year - year) / 5.0)
        cites = math.log((int(r.get("citations") or 0)) + 1)
        cites_norm = cites / 10.0  # cap-ish
        r["_relevance"] = float(relevance[i])
        r["_recency"] = float(recency)
        r["_citations_norm"] = float(min(cites_norm, 1.0))
        r["_score"] = 0.5 * r["_relevance"] + 0.3 * r["_recency"] + 0.2 * r["_citations_norm"]

    records.sort(key=lambda r: r["_score"], reverse=True)
    top = records[: args.top]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(top, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[rank] kept top {len(top)} of {len(records)}  -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
