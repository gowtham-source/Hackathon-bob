"""CrossRef public REST API. Keyless."""
from __future__ import annotations

import httpx

from ..models import Paper
from ._base import BaseSearcher

CROSSREF_URL = "https://api.crossref.org/works"


class CrossRefSearcher(BaseSearcher):
    name = "crossref"
    requires_key = None

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        params = {"query": query, "rows": max_results, "select": "DOI,title,abstract,author,issued,container-title,is-referenced-by-count,URL"}
        r = httpx.get(
            CROSSREF_URL,
            params=params,
            headers={"User-Agent": "Code2Paper/0.1 (mailto:user@example.com)"},
            timeout=30.0,
        )
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        out: list[Paper] = []
        for it in items:
            title = (it.get("title") or [""])[0]
            abstract = it.get("abstract", "") or ""
            authors = [
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in it.get("author", []) or []
            ]
            issued = it.get("issued", {}).get("date-parts", [[None]])[0]
            year = issued[0] if issued else None
            container = (it.get("container-title") or [""])[0]
            out.append(
                Paper(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    venue=container,
                    doi=it.get("DOI", ""),
                    url=it.get("URL", ""),
                    citations=int(it.get("is-referenced-by-count", 0) or 0),
                    source=self.name,
                )
            )
        return out
