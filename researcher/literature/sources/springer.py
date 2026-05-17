"""Springer Nature — meta and open-access endpoints. Needs SPRINGER_API_KEY."""
from __future__ import annotations

import os

import httpx

from ..models import Paper
from ._base import BaseSearcher

META_URL = "https://api.springernature.com/meta/v2/json"
OA_URL = "https://api.springernature.com/openaccess/json"


class _SpringerBase(BaseSearcher):
    requires_key = "SPRINGER_API_KEY"
    endpoint: str = ""

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        params = {
            "q": query,
            "p": max_results,
            "api_key": os.environ["SPRINGER_API_KEY"],
        }
        r = httpx.get(self.endpoint, params=params, timeout=30.0)
        r.raise_for_status()
        out: list[Paper] = []
        for rec in r.json().get("records", []) or []:
            authors = [a.get("creator", "") for a in rec.get("creators", []) or []]
            year_str = (rec.get("publicationDate", "") or "")[:4]
            out.append(
                Paper(
                    title=rec.get("title", "") or "",
                    abstract=rec.get("abstract", "") or "",
                    authors=authors,
                    year=int(year_str) if year_str.isdigit() else None,
                    venue=rec.get("publicationName", "") or "",
                    doi=rec.get("doi", "") or "",
                    url=(rec.get("url", []) or [{}])[0].get("value", ""),
                    source=self.name,
                )
            )
        return out


class SpringerMetaSearcher(_SpringerBase):
    name = "springer_meta"
    endpoint = META_URL


class SpringerOpenAccessSearcher(_SpringerBase):
    name = "springer_oa"
    endpoint = OA_URL
