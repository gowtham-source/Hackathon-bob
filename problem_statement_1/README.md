# DocSync MCP Server

Local MCP server that keeps coding agents grounded on the **latest** SDK & library
documentation. Scrapes official docs (resolved via PyPI `project_urls`), embeds
them locally with `sentence-transformers`, stores in `chromadb`, and exposes
the index over MCP stdio.

Also includes a live **`list_models`** tool that runs each provider's SDK in a
fresh subprocess so transient SDK errors never crash the server.

## Tools

| Tool | Args | What it does |
|---|---|---|
| `search_docs` | `query`, `library?`, `top_k?` | Semantic search over indexed docs |
| `refresh_docs` | `library`, `version?` | Re-scrape & re-index a library |
| `list_models` | `provider` (`google`/`openai`/`anthropic`) | Live model list via subprocess |

## Install

```powershell
uv sync
```

(or `uv add httpx beautifulsoup4 chromadb sentence-transformers mcp python-dotenv`)

Set API keys (for `list_models`) in `.env` or your shell:

```
GOOGLE_API_KEY=...   # or GEMINI_API_KEY
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## CLI

```powershell
# scrape & index
uv run main.py scrape google-genai
uv run main.py scrape openai 1.51.0
uv run main.py scrape anthropic

# start MCP stdio server
uv run main.py serve

# debug helpers
uv run main.py search "how to stream chat" google-genai
uv run main.py models google
uv run main.py stats
```

## Plug into an MCP client

The server prints a config block on startup. Typical entry:

```json
{
  "mcpServers": {
    "docsync": {
      "command": "python",
      "args": ["-m", "docsync"],
      "env": {
        "GOOGLE_API_KEY": "${GOOGLE_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

For Claude Desktop / Windsurf / Cursor, point `command` at the absolute path of
the `python` inside your `uv` venv (printed at server startup).

## Layout

```
problem_statement_1/
├── main.py                 # CLI
├── pyproject.toml
├── docsync/
│   ├── __init__.py
│   ├── __main__.py         # `python -m docsync` -> MCP stdio
│   ├── scraper.py          # PyPI resolve + crawl + html->markdown + chunk
│   ├── vector_store.py     # ChromaDB persistent + sentence-transformers
│   ├── executor.py         # subprocess list_models for google/openai/anthropic
│   └── server.py           # FastMCP server with 3 tools
└── .docsync_db/            # local Chroma persistence (auto-created)
```

## Notes

- Pure Python, no Docker. ChromaDB runs in local PersistentClient mode.
- Re-running `scrape` / `refresh_docs` for the same `library` + `version` deletes
  the prior chunks and upserts fresh ones — no duplication.
- Code blocks and changelog/release sections are tagged with higher `priority`
  metadata so a downstream client can prefer them.
- `list_models` always runs in a subprocess — missing SDKs or bad keys produce
  helpful error strings, never a server crash.
