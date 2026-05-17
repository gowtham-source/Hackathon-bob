"""Elsevier ScienceDirect / Scopus — needs ELSEVIER_API_KEY."""
from __future__ import annotations

import os

import httpx

from ..models import Paper
from ._base import BaseSearcher

SCOPUS_URL = "https://api.elsevier.com/content/search/scopus"


class ElsevierSearcher(BaseSearcher):
    name = "elsevier"
    requires_key = "ELSEVIER_API_KEY"

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        headers = {
            "X-ELS-APIKey": os.environ["ELSEVIER_API_KEY"],
            "Accept": "application/json",
        }
        params = {"query": query, "count": max_results}
        r = httpx.get(SCOPUS_URL, headers=headers, params=params, timeout=30.0)
        r.raise_for_status()
        out: list[Paper] = []
        for it in r.json().get("search-results", {}).get("entry", []) or []:
            authors_str = it.get("dc:creator", "") or ""
            year_str = (it.get("prism:coverDate", "") or "")[:4]
            out.append(
                Paper(
                    title=it.get("dc:title", "") or "",
                    abstract=it.get("dc:description", "") or "",
                    authors=[a.strip() for a in authors_str.split(",") if a.strip()],
                    year=int(year_str) if year_str.isdigit() else None,
                    venue=it.get("prism:publicationName", "") or "",
                    doi=it.get("prism:doi", "") or "",
                    url=next(
                        (l.get("@href", "") for l in it.get("link", []) if l.get("@ref") == "scopus"),
                        "",
                    ),
                    citations=int(it.get("citedby-count", 0) or 0),
                    source=self.name,
                )
            )
        return out
