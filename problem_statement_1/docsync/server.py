"""DocSync MCP stdio server.

Exposes three tools:
- search_docs(query, library)         -> semantic search over indexed docs
- refresh_docs(library, version)      -> re-scrape & re-index a library
- list_models(provider)               -> live model listing via subprocess
"""
from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

from mcp.server.fastmcp import FastMCP

from .executor import list_models as _list_models
from .scraper import ScrapeConfig, crawl_and_chunk
from .vector_store import VectorStore

# Lazy singleton — sentence-transformers is heavy.
_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


mcp = FastMCP("docsync")


@mcp.tool()
def search_docs(query: str, library: str = "", top_k: int = 6) -> dict[str, Any]:
    """Semantic search over indexed SDK/library documentation.

    Args:
        query: Natural-language question or code snippet to look up.
        library: Optional library filter (e.g. "google-genai", "openai").
        top_k: Max number of chunks to return (default 6).
    """
    store = get_store()
    results = store.search(query=query, library=library or None, top_k=top_k)
    return {
        "query": query,
        "library": library or None,
        "count": len(results),
        "results": [
            {
                "url": r["metadata"].get("url"),
                "title": r["metadata"].get("title"),
                "library": r["metadata"].get("library"),
                "version": r["metadata"].get("version"),
                "scraped_at": r["metadata"].get("scraped_at"),
                "distance": r["distance"],
                "text": r["text"],
            }
            for r in results
        ],
    }


@mcp.tool()
def refresh_docs(library: str, version: str = "") -> dict[str, Any]:
    """Re-scrape and re-index documentation for a library.

    Args:
        library: PyPI package name (e.g. "google-genai").
        version: Optional version. Empty -> latest.
    """
    cfg = ScrapeConfig()
    resolved_version, seed, chunks = asyncio.run(
        crawl_and_chunk(library=library, version=version or None, config=cfg)
    )
    store = get_store()
    # Replace prior content for this library+version, then upsert.
    store.delete_library(library, resolved_version)
    written = store.upsert_chunks(chunks)
    return {
        "library": library,
        "version": resolved_version,
        "seed_url": seed,
        "pages_indexed": len({c.url for c in chunks}),
        "chunks_indexed": written,
    }


@mcp.tool()
def list_models(provider: str) -> dict[str, Any]:
    """List currently available models from a provider's live SDK.

    Args:
        provider: One of "google", "openai", "anthropic".
    """
    return _list_models(provider)


def print_client_config() -> None:
    """Print an MCP client config snippet to stderr on startup."""
    py = sys.executable
    cfg = {
        "mcpServers": {
            "docsync": {
                "command": py,
                "args": ["-m", "docsync"],
                "env": {
                    "GOOGLE_API_KEY": "${GOOGLE_API_KEY}",
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
                },
            }
        }
    }
    banner = (
        "\n=== DocSync MCP Server ===\n"
        "Add this to your MCP client config (e.g. Claude Desktop, Windsurf):\n"
        f"{json.dumps(cfg, indent=2)}\n"
        "Tools: search_docs, refresh_docs, list_models\n"
        "==========================\n"
    )
    print(banner, file=sys.stderr, flush=True)


def run() -> None:
    print_client_config()
    mcp.run()  # stdio transport by default


if __name__ == "__main__":
    run()
