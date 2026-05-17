"""Verify that every required figure/table in the manifests is referenced
in the matching section file at least once, AND that no @fig:/@tab: label
in section files points to an unknown id.

Exit code: 0 on success, 1 if any unresolved reference or missing reference.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REF_RE = re.compile(r"@(fig|tab):([A-Za-z0-9_:\-]+)")


def collect_refs(typ_path: Path) -> list[tuple[str, str]]:
    if not typ_path.exists():
        return []
    text = typ_path.read_text(encoding="utf-8", errors="replace")
    return [(m.group(1), m.group(2)) for m in REF_RE.finditer(text)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sections", nargs="+", type=Path, help="Section .typ files to scan")
    ap.add_argument("--figures-manifest", type=Path, default=Path("paper/figures/_manifest.json"))
    ap.add_argument("--tables-manifest", type=Path, default=Path("paper/tables/_manifest.json"))
    args = ap.parse_args()

    fig_manifest = json.loads(args.figures_manifest.read_text(encoding="utf-8")) if args.figures_manifest.exists() else {"figures": []}
    tab_manifest = json.loads(args.tables_manifest.read_text(encoding="utf-8")) if args.tables_manifest.exists() else {"tables": []}

    # Build lookup tables
    fig_by_id = {f["fig_id"].replace("fig:", ""): f for f in fig_manifest.get("figures", [])}
    tab_by_id = {t["tab_id"].replace("tab:", ""): t for t in tab_manifest.get("tables", [])}

    # Refs found in section files
    refs_by_section: dict[str, list[tuple[str, str]]] = {}
    for section_file in args.sections:
        refs_by_section[section_file.stem] = collect_refs(section_file)

    errors: list[str] = []

    # 1. Every required figure/table referenced at least once in its section
    for fig in fig_manifest.get("figures", []):
        if not fig.get("required"):
            continue
        section = fig.get("section", "")
        target_id = fig["fig_id"].replace("fig:", "")
        section_refs = refs_by_section.get(section, [])
        if not any(kind == "fig" and rid == target_id for kind, rid in section_refs):
            errors.append(f"figure {fig['fig_id']} not referenced in section '{section}'")

    for tab in tab_manifest.get("tables", []):
        if not tab.get("required"):
            continue
        section = tab.get("section", "")
        target_id = tab["tab_id"].replace("tab:", "")
        section_refs = refs_by_section.get(section, [])
        if not any(kind == "tab" and rid == target_id for kind, rid in section_refs):
            errors.append(f"table {tab['tab_id']} not referenced in section '{section}'")

    # 2. Every reference in section files resolves to a manifest entry
    for section, refs in refs_by_section.items():
        for kind, rid in refs:
            if kind == "fig" and rid not in fig_by_id:
                errors.append(f"section '{section}' references unknown figure @fig:{rid}")
            if kind == "tab" and rid not in tab_by_id:
                errors.append(f"section '{section}' references unknown table @tab:{rid}")

    if errors:
        print("[check_refs] FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[check_refs] OK: {sum(len(v) for v in refs_by_section.values())} refs across {len(refs_by_section)} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
