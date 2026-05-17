"""Verify every #cite key in a Typst section file resolves in paper/refs.bib.

Usage: ``uv run python -m literature.verify_bib paper/sections/related_work.typ``
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CITE_RE = re.compile(r"#cite\(<([^>]+)>")
BIB_KEY_RE = re.compile(r"^@\w+\{\s*([^,\s]+)\s*,", re.MULTILINE)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: verify_bib <typst_file> [<typst_file> ...]", file=sys.stderr)
        return 2
    bib = Path("paper/refs.bib")
    if not bib.exists():
        print(f"missing {bib}", file=sys.stderr)
        return 1
    keys = set(BIB_KEY_RE.findall(bib.read_text(encoding="utf-8")))
    missing: list[tuple[str, str]] = []
    for f in argv[1:]:
        text = Path(f).read_text(encoding="utf-8")
        for k in CITE_RE.findall(text):
            if k not in keys:
                missing.append((f, k))
    if missing:
        for f, k in missing:
            print(f"MISSING: {k} (cited in {f})")
        return 1
    print(f"[verify_bib] ok — all citations resolve in {bib}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
