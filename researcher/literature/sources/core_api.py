"""CORE academic search — needs CORE_API_KEY (free key from https://core.ac.uk/services/api)."""
from __future__ import annotations

import os

import httpx

from ..models import Paper
from ._base import BaseSearcher

CORE_URL = "https://api.core.ac.uk/v3/search/works"


class CORESearcher(BaseSearcher):
    name = "core"
    requires_key = "CORE_API_KEY"

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        headers = {"Authorization": f"Bearer {os.environ['CORE_API_KEY']}"}
        body = {"q": query, "limit": max_results}
        r = httpx.post(CORE_URL, headers=headers, json=body, timeout=30.0)
        r.raise_for_status()
        out: list[Paper] = []
        for it in r.json().get("results", []):
            authors = [a.get("name", "") for a in it.get("authors", []) or []]
            out.append(
                Paper(
                    title=it.get("title", "") or "",
                    abstract=it.get("abstract", "") or "",
                    authors=authors,
                    year=it.get("yearPublished"),
                    venue=(it.get("publisher") or "") or "",
                    doi=it.get("doi", "") or "",
                    url=it.get("downloadUrl") or it.get("sourceFulltextUrls", [""])[0] or "",
                    source=self.name,
                )
            )
        return out
