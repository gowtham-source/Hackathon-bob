"""Base searcher interface."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from ..models import Paper

log = logging.getLogger(__name__)


class BaseSearcher(ABC):
    name: str = "base"
    requires_key: str | None = None  # env var name, or None for keyless

    def available(self) -> bool:
        if self.requires_key is None:
            return True
        import os
        return bool(os.getenv(self.requires_key))

    @abstractmethod
    def search(self, query: str, max_results: int = 30) -> list[Paper]:
        ...

    def safe_search(self, query: str, max_results: int = 30) -> list[Paper]:
        if not self.available():
            log.warning(
                "[%s] skipping — missing env var %s", self.name, self.requires_key
            )
            return []
        try:
            return self.search(query, max_results)
        except Exception as e:  # pragma: no cover
            log.exception("[%s] search failed for %r: %s", self.name, query, e)
            return []
