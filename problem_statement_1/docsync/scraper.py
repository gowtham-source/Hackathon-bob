"""Doc Scraper Agent.

Resolves a Python library's official docs site via PyPI's `project_urls`,
crawls the site (same host, polite & bounded), strips HTML to clean markdown,
and chunks it for indexing.
"""
from __future__ import annotations

import asyncio
import re
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag

PYPI_JSON = "https://pypi.org/pypi/{name}/json"
PYPI_VERSION_JSON = "https://pypi.org/pypi/{name}/{version}/json"

# Keys in PyPI project_urls (case-insensitive) that likely point at docs.
DOC_URL_KEYS = (
    "documentation",
    "docs",
    "documentation, en",
    "homepage",
    "home",
    "source",
    "repository",
)

DEFAULT_HEADERS = {
    "User-Agent": "DocSyncMCP/0.1 (+https://github.com/local/docsync-mcp)",
    "Accept": "text/html,application/xhtml+xml",
}

# Heuristic: priority content tends to live in these elements/classes.
MAIN_SELECTORS = [
    "main",
    "article",
    "div.document",
    "div.content",
    "div#content",
    "div.markdown-body",
    "div.rst-content",
    "section",
]


@dataclass
class DocChunk:
    library: str
    version: str
    url: str
    title: str
    text: str
    scraped_at: str
    chunk_index: int = 0
    priority: int = 0  # higher = more important (code/changelog)

    def chunk_id(self) -> str:
        # Stable id so upserts replace prior content for same url+chunk.
        safe_url = re.sub(r"[^a-zA-Z0-9]+", "_", self.url)[:180]
        return f"{self.library}::{self.version}::{safe_url}::{self.chunk_index}"

    def metadata(self) -> dict:
        return {
            "library": self.library,
            "version": self.version,
            "url": self.url,
            "title": self.title,
            "scraped_at": self.scraped_at,
            "chunk_index": self.chunk_index,
            "priority": self.priority,
        }


@dataclass
class ScrapeConfig:
    max_pages: int = 40
    max_depth: int = 2
    request_timeout: float = 20.0
    concurrency: int = 5
    chunk_size: int = 1200  # characters
    chunk_overlap: int = 150
    polite_delay: float = 0.0  # seconds between batches; 0 ok with low concurrency


# ---------- PyPI resolution ----------

async def resolve_docs_url(
    client: httpx.AsyncClient, library: str, version: str | None
) -> tuple[str, str]:
    """Return (resolved_version, docs_url) for a library."""
    url = (
        PYPI_VERSION_JSON.format(name=library, version=version)
        if version
        else PYPI_JSON.format(name=library)
    )
    r = await client.get(url, timeout=20.0)
    r.raise_for_status()
    data = r.json()
    info = data.get("info", {})
    resolved_version = info.get("version") or version or "latest"
    project_urls: dict[str, str] = info.get("project_urls") or {}

    # Score candidates by key name preference.
    candidates: list[tuple[int, str]] = []
    for key, val in project_urls.items():
        if not val:
            continue
        k = key.strip().lower()
        for i, want in enumerate(DOC_URL_KEYS):
            if want in k:
                candidates.append((i, val))
                break
    # Fallback: home_page or package_url
    if info.get("home_page"):
        candidates.append((len(DOC_URL_KEYS), info["home_page"]))
    if info.get("package_url"):
        candidates.append((len(DOC_URL_KEYS) + 1, info["package_url"]))

    if not candidates:
        raise RuntimeError(
            f"No documentation/home URL found in PyPI metadata for {library}"
        )
    candidates.sort(key=lambda x: x[0])
    return resolved_version, candidates[0][1]


# ---------- HTML -> Markdown ----------

_BLOCK_TAGS = {
    "p", "div", "section", "article", "li", "tr", "br", "h1", "h2", "h3",
    "h4", "h5", "h6", "pre", "blockquote",
}


def _html_to_markdown(soup: BeautifulSoup) -> tuple[str, str]:
    """Return (title, markdown). Preserves code blocks & headings."""
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Pick main container if available
    root: Tag | None = None
    for sel in MAIN_SELECTORS:
        root = soup.select_one(sel)
        if root:
            break
    if root is None:
        root = soup.body or soup

    # Drop noise
    for sel in ["nav", "footer", "script", "style", "aside", "form", "noscript"]:
        for t in root.select(sel):
            t.decompose()

    out: list[str] = []

    def render(node) -> None:
        if isinstance(node, NavigableString):
            text = str(node)
            if text.strip():
                out.append(text)
            return
        if not isinstance(node, Tag):
            return
        name = node.name.lower()
        if name in {"script", "style"}:
            return
        if name == "pre":
            code = node.get_text("\n", strip=False)
            lang = ""
            code_tag = node.find("code")
            if code_tag and code_tag.get("class"):
                for c in code_tag.get("class"):
                    if c.startswith("language-"):
                        lang = c[len("language-"):]
                        break
                    if c.startswith("highlight-"):
                        lang = c[len("highlight-"):]
                        break
            out.append(f"\n\n```{lang}\n{code.strip()}\n```\n\n")
            return
        if name == "code" and node.parent and node.parent.name != "pre":
            out.append(f"`{node.get_text('', strip=True)}`")
            return
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(name[1])
            out.append("\n\n" + ("#" * level) + " " + node.get_text(" ", strip=True) + "\n\n")
            return
        if name == "a":
            text = node.get_text(" ", strip=True)
            href = node.get("href") or ""
            if text:
                out.append(f"[{text}]({href})" if href else text)
            return
        if name == "li":
            out.append("\n- ")
            for c in node.children:
                render(c)
            return
        if name == "br":
            out.append("\n")
            return

        for c in node.children:
            render(c)
        if name in _BLOCK_TAGS:
            out.append("\n")

    for c in root.children:
        render(c)

    md = "".join(out)
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return title, md


# ---------- Chunking ----------

def _chunk_markdown(
    md: str, chunk_size: int, overlap: int
) -> list[tuple[str, int]]:
    """Split markdown into chunks. Returns list of (chunk_text, priority)."""
    if not md:
        return []

    # Split into blocks by blank lines, keeping fenced code blocks intact.
    blocks: list[str] = []
    buf: list[str] = []
    in_code = False
    for line in md.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            buf.append(line)
            continue
        if not in_code and not line.strip():
            if buf:
                blocks.append("\n".join(buf))
                buf = []
        else:
            buf.append(line)
    if buf:
        blocks.append("\n".join(buf))

    chunks: list[tuple[str, int]] = []
    cur: list[str] = []
    cur_len = 0

    def flush():
        if cur:
            text = "\n\n".join(cur).strip()
            if text:
                prio = 2 if "```" in text else (1 if re.search(r"changelog|release", text, re.I) else 0)
                chunks.append((text, prio))

    for block in blocks:
        b_len = len(block)
        if b_len > chunk_size and "```" not in block:
            # Hard wrap large prose blocks
            for i in range(0, b_len, chunk_size - overlap):
                piece = block[i : i + chunk_size]
                chunks.append((piece, 0))
            continue
        if cur_len + b_len + 2 > chunk_size and cur:
            flush()
            # carry overlap (last block) for context
            if overlap and cur:
                tail = cur[-1][-overlap:]
                cur = [tail]
                cur_len = len(tail)
            else:
                cur = []
                cur_len = 0
        cur.append(block)
        cur_len += b_len + 2
    flush()
    return chunks


# ---------- Crawler ----------

@dataclass
class _CrawlState:
    seen: set[str] = field(default_factory=set)
    queue: deque = field(default_factory=deque)


def _normalize_url(u: str) -> str:
    u, _ = urldefrag(u)
    return u.rstrip("/")


def _same_site(seed: str, candidate: str) -> bool:
    a = urlparse(seed)
    b = urlparse(candidate)
    if b.scheme not in ("http", "https"):
        return False
    if not b.netloc:
        return False
    # Allow same host or subdomain of host
    return b.netloc == a.netloc


async def _fetch(client: httpx.AsyncClient, url: str, timeout: float) -> str | None:
    try:
        r = await client.get(url, timeout=timeout, follow_redirects=True)
        if r.status_code != 200:
            return None
        ctype = r.headers.get("content-type", "")
        if "html" not in ctype and "text" not in ctype:
            return None
        return r.text
    except Exception:
        return None


async def crawl_and_chunk(
    library: str,
    version: str | None = None,
    config: ScrapeConfig | None = None,
) -> tuple[str, str, list[DocChunk]]:
    """Resolve library docs URL, crawl it, return (version, seed_url, chunks)."""
    cfg = config or ScrapeConfig()

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS) as client:
        resolved_version, seed = await resolve_docs_url(client, library, version)
        seed = _normalize_url(seed)
        state = _CrawlState()
        state.queue.append((seed, 0))
        state.seen.add(seed)

        all_chunks: list[DocChunk] = []
        scraped_at = datetime.now(timezone.utc).isoformat()
        sem = asyncio.Semaphore(cfg.concurrency)

        async def process(url: str, depth: int) -> list[str]:
            async with sem:
                html = await _fetch(client, url, cfg.request_timeout)
            if html is None:
                return []
            soup = BeautifulSoup(html, "html.parser")
            title, md = _html_to_markdown(soup)
            for idx, (text, prio) in enumerate(
                _chunk_markdown(md, cfg.chunk_size, cfg.chunk_overlap)
            ):
                all_chunks.append(
                    DocChunk(
                        library=library,
                        version=resolved_version,
                        url=url,
                        title=title or url,
                        text=text,
                        scraped_at=scraped_at,
                        chunk_index=idx,
                        priority=prio,
                    )
                )
            # Discover links
            links: list[str] = []
            if depth >= cfg.max_depth:
                return links
            for a in soup.find_all("a", href=True):
                nxt = _normalize_url(urljoin(url, a["href"]))
                if not _same_site(seed, nxt):
                    continue
                if nxt in state.seen:
                    continue
                links.append(nxt)
            return links

        pages_done = 0
        while state.queue and pages_done < cfg.max_pages:
            batch: list[tuple[str, int]] = []
            while state.queue and len(batch) < cfg.concurrency and pages_done + len(batch) < cfg.max_pages:
                batch.append(state.queue.popleft())
            results = await asyncio.gather(*(process(u, d) for u, d in batch))
            pages_done += len(batch)
            for (u, d), new_links in zip(batch, results):
                for nxt in new_links:
                    if nxt in state.seen:
                        continue
                    state.seen.add(nxt)
                    state.queue.append((nxt, d + 1))
            if cfg.polite_delay:
                await asyncio.sleep(cfg.polite_delay)

        return resolved_version, seed, all_chunks
