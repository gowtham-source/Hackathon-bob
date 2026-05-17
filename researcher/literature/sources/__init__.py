"""Literature search sources.

Each source exports a class with a ``search(query: str, max_results: int) -> list[Paper]``
method. Sources requiring API keys gracefully no-op when the env var is missing.
"""
from .arxiv_source import ArxivSearcher
from .crossref_source import CrossRefSearcher
from .core_api import CORESearcher
from .elsevier import ElsevierSearcher
from .ieee import IEEESearcher
from .ncbi_pubmed import NCBIPubMedSearcher
from .scholarly_source import ScholarlySearcher
from .springer import SpringerMetaSearcher, SpringerOpenAccessSearcher
from .wiley import WileySearcher

ALL_SEARCHERS = {
    "arxiv": ArxivSearcher,
    "crossref": CrossRefSearcher,
    "core": CORESearcher,
    "openalex": ScholarlySearcher,  # OpenAlex is the keyless backend used by ScholarlySearcher
    "ncbi_pubmed": NCBIPubMedSearcher,
    "ieee": IEEESearcher,
    "elsevier": ElsevierSearcher,
    "springer_meta": SpringerMetaSearcher,
    "springer_oa": SpringerOpenAccessSearcher,
    "wiley": WileySearcher,
}

__all__ = [
    "ArxivSearcher",
    "CrossRefSearcher",
    "CORESearcher",
    "ElsevierSearcher",
    "IEEESearcher",
    "NCBIPubMedSearcher",
    "ScholarlySearcher",
    "SpringerMetaSearcher",
    "SpringerOpenAccessSearcher",
    "WileySearcher",
    "ALL_SEARCHERS",
]
