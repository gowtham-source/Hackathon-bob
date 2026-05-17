"""Wiley TDM API — needs WILEY_TDM_TOKEN.

Note: Wiley's TDM API is primarily a content-download endpoint; metadata
discovery is best done via CrossRef. This searcher uses CrossRef filtered
to Wiley as a publisher when only WILEY_TDM_TOKEN-class access is intended,
to avoid violating ToS.
"""
from __future__ import annotations

import httpx

from ..models import Paper
from ._base import BaseSearcher


class WileySearcher(BaseSearcher):
    name = "wiley"
    requires_key = "WILEY_TDM_TOKEN"

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        params = {
            "query": query,
            "rows": max_results,
            "filter": "publisher-name:Wiley",
            "select": "DOI,title,abstract,author,issued,container-title,is-referenced-by-count,URL",
        }
        r = httpx.get(
            "https://api.crossref.org/works",
            params=params,
            headers={"User-Agent": "Code2Paper/0.1"},
            timeout=30.0,
        )
        r.raise_for_status()
        out: list[Paper] = []
        for it in r.json().get("message", {}).get("items", []):
            issued = it.get("issued", {}).get("date-parts", [[None]])[0]
            out.append(
                Paper(
                    title=(it.get("title") or [""])[0],
                    abstract=it.get("abstract", "") or "",
                    authors=[
                        f"{a.get('given', '')} {a.get('family', '')}".strip()
                        for a in it.get("author", []) or []
                    ],
                    year=issued[0] if issued else None,
                    venue=(it.get("container-title") or [""])[0],
                    doi=it.get("DOI", ""),
                    url=it.get("URL", ""),
                    citations=int(it.get("is-referenced-by-count", 0) or 0),
                    source=self.name,
                )
            )
        return out
