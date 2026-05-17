"""IEEE Xplore — needs IEEE_API_KEY."""
from __future__ import annotations

import os

import httpx

from ..models import Paper
from ._base import BaseSearcher

IEEE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"


class IEEESearcher(BaseSearcher):
    name = "ieee"
    requires_key = "IEEE_API_KEY"

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        params = {
            "apikey": os.environ["IEEE_API_KEY"],
            "querytext": query,
            "max_records": max_results,
            "format": "json",
        }
        r = httpx.get(IEEE_URL, params=params, timeout=30.0)
        r.raise_for_status()
        out: list[Paper] = []
        for it in r.json().get("articles", []) or []:
            authors = [
                a.get("full_name", "")
                for a in (it.get("authors", {}) or {}).get("authors", []) or []
            ]
            out.append(
                Paper(
                    title=it.get("title", "") or "",
                    abstract=it.get("abstract", "") or "",
                    authors=authors,
                    year=int(it.get("publication_year", 0) or 0) or None,
                    venue=it.get("publication_title", "") or "",
                    doi=it.get("doi", "") or "",
                    url=it.get("html_url", "") or "",
                    citations=int(it.get("citing_paper_count", 0) or 0),
                    source=self.name,
                )
            )
        return out
