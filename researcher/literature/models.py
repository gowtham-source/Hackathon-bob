"""Shared data models for literature records."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Paper:
    title: str
    abstract: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str = ""
    doi: str = ""
    arxiv_id: str = ""
    url: str = ""
    citations: int = 0
    source: str = ""  # which searcher produced this
    raw: dict[str, Any] = field(default_factory=dict)

    def key(self) -> str:
        if self.doi:
            return f"doi:{self.doi.lower()}"
        if self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        # fallback: title fingerprint
        norm = "".join(c for c in self.title.lower() if c.isalnum())
        return f"title:{norm[:80]}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
