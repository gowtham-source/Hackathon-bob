"""ChromaDB-backed vector store with sentence-transformers embeddings."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.utils import embedding_functions

from .scraper import DocChunk

DEFAULT_DB_DIR = Path(os.getenv("DOCSYNC_DB_DIR", ".docsync_db")).resolve()
DEFAULT_COLLECTION = "docsync"
DEFAULT_EMBED_MODEL = os.getenv(
    "DOCSYNC_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)


class VectorStore:
    def __init__(
        self,
        db_dir: Path | str = DEFAULT_DB_DIR,
        collection: str = DEFAULT_COLLECTION,
        embed_model: str = DEFAULT_EMBED_MODEL,
    ):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.db_dir))
        self._embed_model = embed_model
        self._collection_name = collection
        self._embed_fn = None  # lazy init
        self._collection = None  # lazy init

    def _get_embed_fn(self):
        if self._embed_fn is None:
            self._embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self._embed_model
            )
        return self._embed_fn

    def _get_collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._get_embed_fn(),
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    @property
    def collection(self):
        return self._get_collection()

    # --- writes ---

    def upsert_chunks(self, chunks: Iterable[DocChunk]) -> int:
        ids: list[str] = []
        docs: list[str] = []
        metas: list[dict] = []
        for c in chunks:
            ids.append(c.chunk_id())
            docs.append(c.text)
            metas.append(c.metadata())
        if not ids:
            return 0
        # Batch to avoid memory spikes
        BATCH = 64
        for i in range(0, len(ids), BATCH):
            self.collection.upsert(
                ids=ids[i : i + BATCH],
                documents=docs[i : i + BATCH],
                metadatas=metas[i : i + BATCH],
            )
        return len(ids)

    def delete_library(self, library: str, version: str | None = None) -> None:
        where: dict = {"library": library}
        if version:
            where = {"$and": [{"library": library}, {"version": version}]}
        self.collection.delete(where=where)

    # --- reads ---

    def search(
        self, query: str, library: str | None = None, top_k: int = 6
    ) -> list[dict]:
        where = {"library": library} if library else None
        res = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
        )
        out: list[dict] = []
        ids = (res.get("ids") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for i, doc_id in enumerate(ids):
            out.append(
                {
                    "id": doc_id,
                    "text": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None,
                }
            )
        return out

    def stats(self) -> dict:
        try:
            count = self.collection.count()
        except Exception:
            count = -1
        return {"db_dir": str(self.db_dir), "collection": self.collection.name, "count": count}
