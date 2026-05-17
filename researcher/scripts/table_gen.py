"""Comparative-table emitter.

Reads paper/tables/_manifest.json + results/_index.json, emits Typst tables
into paper/tables/*.typ. Each cell carries an inline `// src: ...` comment so
verify_numbers can trace it.

Conventions enforced:
- booktabs style (no vertical rules)
- best-per-column in **bold**, second-best _underlined_
- highlight row gets fill color
- ± std rendered if num_seeds > 1
- source comments after every numeric cell
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _fmt_num(v: float, decimals: int = 2) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "--"
    return f"{v:.{decimals}f}"


def _resolve_data(ref: str, results: dict) -> Any:
    """Resolve a path like 'results/_index.json#base_to_novel' to its value."""
    if "#" not in ref:
        return None
    _, key = ref.split("#", 1)
    cur: Any = results
    for part in key.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _rank_per_col(rows: list[list[Any]], col_idx: int) -> tuple[int, int]:
    """Return (best_row, second_best_row) indices for a numeric column."""
    vals = [(i, r[col_idx]) for i, r in enumerate(rows) if isinstance(r[col_idx], (int, float))]
    if not vals:
        return -1, -1
    vals.sort(key=lambda x: x[1], reverse=True)
    best = vals[0][0]
    second = vals[1][0] if len(vals) > 1 else -1
    return best, second


def render_table(spec: dict[str, Any], results: dict[str, Any]) -> str:
    tab_id = spec["tab_id"]
    schema = spec["schema"]
    data = _resolve_data(spec.get("data_source", ""), results) or {}
    rows_data = data.get("rows", [])  # list of {method: ..., values: [...], std: [...]}
    highlight_row = spec.get("highlight_row")
    decimals = spec.get("decimals", 2)
    bold_best = spec.get("best_per_col_bold", True)
    underline_second = spec.get("second_best_underline", True)

    # Build raw matrix of values (rows x cols, including method name col)
    matrix: list[list[Any]] = []
    src_matrix: list[list[str]] = []
    for r in rows_data:
        row = [r["method"]]
        srcs = [""]
        for i, col_name in enumerate(schema[1:]):
            v = (r.get("values") or [None] * len(schema))[i] if r.get("values") else None
            row.append(v)
            srcs.append(f"{spec.get('data_source','')}.rows[{r['method']}].values[{i}]")
        matrix.append(row)
        src_matrix.append(srcs)

    # Compute best/second per numeric column
    best_second = [
        _rank_per_col(matrix, ci) for ci in range(1, len(schema))
    ]

    # Build Typst cells
    cells: list[str] = []
    for col in schema:
        cells.append(f'[*{col}*]')

    for ri, row in enumerate(matrix):
        for ci, val in enumerate(row):
            content: str
            if ci == 0:
                content = f"[{val}]"
            else:
                best, second = best_second[ci - 1]
                num_str = _fmt_num(val, decimals) if isinstance(val, (int, float)) else str(val)
                # Add std if available
                stds = rows_data[ri].get("std") if ri < len(rows_data) else None
                if stds and ci - 1 < len(stds) and stds[ci - 1] is not None:
                    num_str = f"{num_str}#h(0.2em)±{_fmt_num(stds[ci-1], decimals)}"
                if bold_best and ri == best and isinstance(val, (int, float)):
                    num_str = f"*{num_str}*"
                elif underline_second and ri == second and isinstance(val, (int, float)):
                    num_str = f"#underline[{num_str}]"
                content = f"[{num_str}] // src: {src_matrix[ri][ci]}"
            # Highlight row
            if highlight_row and row[0] == highlight_row:
                content = f'table.cell(fill: rgb("#FFF3E0"), {content[1:]}' if content.startswith("[") else content
            cells.append(content)

    n_cols = len(schema)
    cell_block = ",\n  ".join(cells)
    caption = spec.get("caption") or spec.get("intent", "Results table.")

    return (
        f"// Auto-generated from tables/_manifest.json#{tab_id}\n"
        f"#figure(\n"
        f"  table(\n"
        f"    columns: {n_cols},\n"
        f"    stroke: none,\n"
        f"    table.hline(stroke: 0.8pt),\n"
        f"    {cell_block},\n"
        f"    table.hline(stroke: 0.4pt),\n"
        f"  ),\n"
        f"  caption: [{caption}],\n"
        f") <{tab_id.replace(':', '_')}>\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--tab-id", required=True)
    ap.add_argument("--results", type=Path, default=Path("results/_index.json"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    manifest = json.loads(args.spec.read_text(encoding="utf-8"))
    spec = next((t for t in manifest.get("tables", []) if t["tab_id"] == args.tab_id), None)
    if spec is None:
        raise SystemExit(f"table {args.tab_id} not found in manifest")

    results = {}
    if args.results.exists():
        results = json.loads(args.results.read_text(encoding="utf-8"))
    else:
        print(f"[table_gen] WARNING: {args.results} missing — cells will be '--'")

    typ_code = render_table(spec, results)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(typ_code, encoding="utf-8")
    print(f"[table_gen] wrote {args.out} (tab_id={args.tab_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
