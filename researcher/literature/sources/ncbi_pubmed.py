"""NCBI E-utilities — PubMed. Keyless (rate-limited; NCBI_API_KEY raises limits)."""
from __future__ import annotations

import os
import re
from xml.etree import ElementTree as ET

import httpx

from ..models import Paper
from ._base import BaseSearcher

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class NCBIPubMedSearcher(BaseSearcher):
    name = "ncbi_pubmed"
    requires_key = None  # optional: NCBI_API_KEY for higher rate limits

    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        api_key = os.getenv("NCBI_API_KEY", "")
        common = {"db": "pubmed", "retmode": "xml"}
        if api_key:
            common["api_key"] = api_key
        # ESearch: get PMIDs
        es = httpx.get(ESEARCH, params={**common, "term": query, "retmax": max_results}, timeout=30.0)
        es.raise_for_status()
        ids = re.findall(r"<Id>(\d+)</Id>", es.text)
        if not ids:
            return []
        # EFetch: fetch metadata
        ef = httpx.get(EFETCH, params={**common, "id": ",".join(ids)}, timeout=60.0)
        ef.raise_for_status()
        root = ET.fromstring(ef.text)
        out: list[Paper] = []
        for art in root.findall(".//PubmedArticle"):
            title = (art.findtext(".//ArticleTitle") or "").strip()
            abstract = " ".join(
                (a.text or "") for a in art.findall(".//Abstract/AbstractText")
            ).strip()
            year_el = art.findtext(".//PubDate/Year") or art.findtext(".//PubDate/MedlineDate", "")
            year = int(year_el[:4]) if year_el and year_el[:4].isdigit() else None
            authors = [
                f"{a.findtext('ForeName', '') or ''} {a.findtext('LastName', '') or ''}".strip()
                for a in art.findall(".//Author")
            ]
            doi_el = art.find(".//ArticleId[@IdType='doi']")
            doi = (doi_el.text or "") if doi_el is not None else ""
            pmid_el = art.find(".//PMID")
            pmid = (pmid_el.text or "") if pmid_el is not None else ""
            out.append(
                Paper(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    venue=art.findtext(".//Journal/Title", "") or "",
                    doi=doi,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                    source=self.name,
                )
            )
        return out
