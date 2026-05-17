"""arXiv via the public OAI/Atom search API. Keyless."""
from __future__ import annotations

import re
from xml.etree import ElementTree as ET

import httpx

from ..models import Paper
from ._base import BaseSearcher

ARXIV_URL = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivSearcher(BaseSearcher):
    name = "arxiv"
    requires_key = None

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        r = httpx.get(ARXIV_URL, params=params, timeout=30.0)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        out: list[Paper] = []
        for entry in root.findall("a:entry", NS):
            title = (entry.findtext("a:title", "", NS) or "").strip()
            summary = (entry.findtext("a:summary", "", NS) or "").strip()
            published = entry.findtext("a:published", "", NS) or ""
            year = int(published[:4]) if published[:4].isdigit() else None
            arxiv_id_url = entry.findtext("a:id", "", NS) or ""
            arxiv_id = re.sub(r"^.*?abs/", "", arxiv_id_url).split("v")[0]
            authors = [
                (a.findtext("a:name", "", NS) or "").strip()
                for a in entry.findall("a:author", NS)
            ]
            doi = entry.findtext("arxiv:doi", "", NS) or ""
            out.append(
                Paper(
                    title=re.sub(r"\s+", " ", title),
                    abstract=re.sub(r"\s+", " ", summary),
                    authors=authors,
                    year=year,
                    venue="arXiv",
                    doi=doi,
                    arxiv_id=arxiv_id,
                    url=arxiv_id_url,
                    source=self.name,
                )
            )
        return out
