"""Pre-warm DocSync embedding model and verify MCP tools work.

Run this before starting Bob to prevent MCP timeouts:
  uv run python warmup.py
"""
from __future__ import annotations

import sys

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

from docsync.vector_store import VectorStore
from docsync.executor import list_models


def main() -> int:
    print("[warmup] Initializing vector store (loading embedding model)...")
    store = VectorStore()
    # Force model load via a dummy search
    _ = store._get_embed_fn()
    stats = store.stats()
    print(f"[warmup] Vector store ready: {stats}")

    print("[warmup] Testing live model listings...")
    for provider in ["google", "openai", "anthropic"]:
        result = list_models(provider)
        if "error" in result:
            print(f"  ⚠ {provider}: {result['error']}")
        else:
            print(f"  ✓ {provider}: {len(result.get('models', []))} models")

    print("\n[warmup] All systems ready. You can now start Bob.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
