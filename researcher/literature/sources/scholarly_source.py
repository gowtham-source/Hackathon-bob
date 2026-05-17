"""OpenAlex (keyless) — used as a stand-in for Google Scholar to avoid scraping."""
from __future__ import annotations

import httpx

from ..models import Paper
from ._base import BaseSearcher

OPENALEX_URL = "https://api.openalex.org/works"


class ScholarlySearcher(BaseSearcher):
    name = "openalex"
    requires_key = None

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        params = {
            "search": query,
            "per-page": min(max_results, 100),
            "select": "id,doi,title,abstract_inverted_index,authorships,publication_year,primary_location,cited_by_count",
        }
        r = httpx.get(OPENALEX_URL, params=params, timeout=30.0)
        r.raise_for_status()
        out: list[Paper] = []
        for w in r.json().get("results", []):
            abstract = self._reconstruct_abstract(w.get("abstract_inverted_index"))
            authors = [
                (a.get("author") or {}).get("display_name", "")
                for a in w.get("authorships", []) or []
            ]
            primary = w.get("primary_location") or {}
            source = primary.get("source") or {}
            venue = source.get("display_name", "") or ""
            out.append(
                Paper(
                    title=w.get("title") or "",
                    abstract=abstract,
                    authors=[a for a in authors if a],
                    year=w.get("publication_year"),
                    venue=venue,
                    doi=(w.get("doi") or "").replace("https://doi.org/", ""),
                    url=w.get("id") or "",
                    citations=int(w.get("cited_by_count", 0) or 0),
                    source=self.name,
                )
            )
        return out

    @staticmethod
    def _reconstruct_abstract(inv_idx: dict | None) -> str:
        if not inv_idx:
            return ""
        positions: list[tuple[int, str]] = []
        for word, idxs in inv_idx.items():
            for i in idxs:
                positions.append((i, word))
        positions.sort()
        return " ".join(w for _, w in positions)
