"""DocSync CLI entry point.

Usage:
  uv run main.py scrape <library> [version]   # scrape & index docs
  uv run main.py serve                        # start MCP stdio server
  uv run main.py search "<query>" [library]   # quick local search (debug)
  uv run main.py models <provider>            # live list_models (debug)
  uv run main.py stats                        # vector store stats
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))


def _cmd_scrape(args: argparse.Namespace) -> int:
    from docsync.scraper import ScrapeConfig, crawl_and_chunk
    from docsync.vector_store import VectorStore

    cfg = ScrapeConfig(max_pages=args.max_pages, max_depth=args.max_depth)
    print(f"[scrape] resolving + crawling {args.library} (version={args.version or 'latest'})...", file=sys.stderr)
    version, seed, chunks = asyncio.run(
        crawl_and_chunk(library=args.library, version=args.version, config=cfg)
    )
    print(f"[scrape] resolved version={version} seed={seed}", file=sys.stderr)
    print(f"[scrape] fetched {len({c.url for c in chunks})} pages, {len(chunks)} chunks", file=sys.stderr)
    store = VectorStore()
    store.delete_library(args.library, version)
    written = store.upsert_chunks(chunks)
    print(f"[scrape] indexed {written} chunks into {store.stats()}", file=sys.stderr)
    return 0


def _cmd_serve(_: argparse.Namespace) -> int:
    from docsync.server import run
    run()
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    from docsync.vector_store import VectorStore

    store = VectorStore()
    res = store.search(args.query, library=args.library, top_k=args.top_k)
    print(json.dumps(res, indent=2, default=str))
    return 0


def _cmd_models(args: argparse.Namespace) -> int:
    from docsync.executor import list_models

    print(json.dumps(list_models(args.provider), indent=2))
    return 0


def _cmd_stats(_: argparse.Namespace) -> int:
    from docsync.vector_store import VectorStore

    print(json.dumps(VectorStore().stats(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="docsync", description="DocSync MCP CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scrape", help="Scrape and index a library's docs")
    s.add_argument("library")
    s.add_argument("version", nargs="?", default=None)
    s.add_argument("--max-pages", type=int, default=40)
    s.add_argument("--max-depth", type=int, default=2)
    s.set_defaults(func=_cmd_scrape)

    sv = sub.add_parser("serve", help="Start MCP stdio server")
    sv.set_defaults(func=_cmd_serve)

    sq = sub.add_parser("search", help="Local semantic search over indexed docs")
    sq.add_argument("query")
    sq.add_argument("library", nargs="?", default=None)
    sq.add_argument("--top-k", type=int, default=6)
    sq.set_defaults(func=_cmd_search)

    sm = sub.add_parser("models", help="List live models from a provider")
    sm.add_argument("provider", choices=["google", "openai", "anthropic"])
    sm.set_defaults(func=_cmd_models)

    st = sub.add_parser("stats", help="Show vector store stats")
    st.set_defaults(func=_cmd_stats)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
