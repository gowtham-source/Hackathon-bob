"""Emit BibTeX from a shortlist JSON."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def cite_key(rec: dict) -> str:
    authors = rec.get("authors") or []
    first = (authors[0].split()[-1] if authors else "anon").lower()
    first = re.sub(r"[^a-z]", "", first) or "anon"
    year = str(rec.get("year") or "nd")
    title = rec.get("title", "")
    word = next((w for w in re.findall(r"[A-Za-z]{4,}", title)), "work").lower()
    return f"{first}{year}{word}"


def bibtex_entry(rec: dict, key: str) -> str:
    fields: dict[str, str] = {}
    if rec.get("title"):
        fields["title"] = rec["title"]
    authors = rec.get("authors") or []
    if authors:
        fields["author"] = " and ".join(authors)
    if rec.get("year"):
        fields["year"] = str(rec["year"])
    if rec.get("venue"):
        fields["booktitle" if rec.get("source") == "arxiv" else "journal"] = rec["venue"]
    if rec.get("doi"):
        fields["doi"] = rec["doi"]
    if rec.get("url"):
        fields["url"] = rec["url"]
    if rec.get("arxiv_id"):
        fields["eprint"] = rec["arxiv_id"]
        fields["archivePrefix"] = "arXiv"
    entry_type = "article" if rec.get("source") != "arxiv" else "misc"
    body = ",\n  ".join(f"{k} = {{{v}}}" for k, v in fields.items())
    return f"@{entry_type}{{{key},\n  {body}\n}}"


_KEY_RE = re.compile(r"^@[a-zA-Z]+\{([^,\s]+),", re.MULTILINE)


def existing_keys(bib_path: Path) -> set[str]:
    if not bib_path.exists():
        return set()
    return set(_KEY_RE.findall(bib_path.read_text(encoding="utf-8")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--append", type=Path, help="Append entries to an existing .bib file, skipping duplicate keys")
    args = ap.parse_args()
    if not args.out and not args.append:
        ap.error("either --out or --append is required")

    shortlist = json.loads(args.inp.read_text(encoding="utf-8"))
    target = args.append or args.out
    seen: set[str] = existing_keys(target) if args.append else set()
    entries: list[str] = []
    for rec in shortlist:
        key = cite_key(rec)
        # ensure unique
        base = key
        i = 1
        while key in seen:
            i += 1
            key = f"{base}{chr(ord('a') + i - 2)}"
        seen.add(key)
        rec["_bib_key"] = key
        entries.append(bibtex_entry(rec, key))

    target.parent.mkdir(parents=True, exist_ok=True)
    if args.append:
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        sep = "\n\n" if existing and not existing.endswith("\n\n") else ""
        target.write_text(existing + sep + "\n\n".join(entries) + "\n", encoding="utf-8")
        mode = "appended"
    else:
        target.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
        mode = "wrote"
    # Persist keys back into shortlist so other tools can map them
    args.inp.write_text(json.dumps(shortlist, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[to_bibtex] {mode} {len(entries)} entries -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
