"""Draft a paper figure from a spec JSON.

Supports multiple plot types operating on the standard `results/_index.json`
schema produced by the codebase-analyzer + results-runner pipeline:
- `pareto`        : trainable_M (log x) vs h_mean, one marker per method
- `rank_dual`     : rank vs HM (left axis) and trainable_M (right axis)
- `beta_multi`    : beta vs {base, novel, h_mean} as three curves
- `gradient_flow` : layer vs grad_norm for MMRL vs MMRL++
- `line`/`bar`    : original generic renderers (back-compat)

GEMINI_API_KEY is auto-loaded from .env. If present, an optional
post-render critique pass annotates the figure with reviewer-target
overlays (e.g. arrows pointing to the highlighted method).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend (no Tk required)
import matplotlib.pyplot as plt
import numpy as np


def _load_dotenv(start: Path = Path.cwd()) -> None:
    for parent in [start, *start.parents]:
        env_file = parent / ".env"
        if env_file.exists():
            for raw in env_file.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
            return


_load_dotenv()


# Style sheet (used by every renderer)
STYLE_SHEET = Path(__file__).resolve().parent.parent / "paper" / "figures" / "_style.mplstyle"
if STYLE_SHEET.exists():
    plt.style.use(str(STYLE_SHEET))

METHOD_COLORS = {
    "CoOp":   "#BBBBBB",
    "CoCoOp": "#888888",
    "MaPLe":  "#555555",
    "MMRL":   "#0072B2",
    "MMRL++": "#D55E00",
}
METHOD_MARKERS = {"CoOp": "o", "CoCoOp": "s", "MaPLe": "^", "MMRL": "D", "MMRL++": "*"}


def render_line(spec: dict, data: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    groups = spec.get("groups") or list(data.keys())
    highlight = spec.get("highlight")
    for g in groups:
        series = data.get(g, {})
        xs = series.get("x") or list(range(len(series.get("y", []))))
        ys = series.get("y", [])
        kwargs = {"label": g}
        if g == highlight:
            kwargs.update(linewidth=2.2, zorder=5)
        else:
            kwargs.update(linewidth=1.0, alpha=0.7)
        ax.plot(xs, ys, **kwargs)
    axes = spec.get("axes") or {}
    ax.set_xlabel(axes.get("x", ""))
    ax.set_ylabel(axes.get("y", ""))
    ax.legend(fontsize=8, frameon=False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(out, format=out.suffix.lstrip("."))


def render_bar(spec: dict, data: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    labels = list(data.keys())
    values = [data[k] for k in labels]
    colors = ["#1f77b4" if k != spec.get("highlight") else "#d62728" for k in labels]
    ax.bar(labels, values, color=colors)
    axes = spec.get("axes") or {}
    ax.set_ylabel(axes.get("y", ""))
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(out, format=out.suffix.lstrip("."))


def _save(fig, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=out.suffix.lstrip("."), bbox_inches="tight")
    plt.close(fig)


def render_pareto(results: dict, out: Path) -> None:
    rows = results["parameter_efficiency"]["rows"]
    fig, ax = plt.subplots(figsize=(3.3, 2.4))
    for r in rows:
        m = r["method"]
        ax.scatter(
            r["trainable_M"], r["h_mean"],
            s=120 if m == "MMRL++" else 60,
            c=METHOD_COLORS.get(m, "#000000"),
            marker=METHOD_MARKERS.get(m, "o"),
            edgecolors="black", linewidths=0.6, zorder=5,
        )
        ax.annotate(m, (r["trainable_M"], r["h_mean"]),
                    xytext=(6, 4), textcoords="offset points",
                    fontsize=7, fontweight="bold" if m == "MMRL++" else "normal")
    ax.set_xscale("log")
    ax.set_xlabel("Trainable parameters (M, log scale)")
    ax.set_ylabel("Harmonic mean (%)")
    ax.grid(True, which="both", alpha=0.25, linewidth=0.4)
    ax.set_title("Pareto frontier: parameters vs accuracy", fontsize=9, pad=6)
    _save(fig, out)


def render_rank_dual(results: dict, out: Path) -> None:
    rows = results["ablation_rank"]["rows"]
    ranks = [r["rank"] for r in rows]
    hms = [r["h_mean"] for r in rows]
    params = [r["trainable_M"] for r in rows]
    fig, ax1 = plt.subplots(figsize=(3.3, 2.0))
    ax2 = ax1.twinx()
    ax1.plot(ranks, hms, "o-", color="#D55E00", linewidth=1.6, label="HM (%)", zorder=5)
    ax2.plot(ranks, params, "s--", color="#0072B2", linewidth=1.2, label="Trainable (M)")
    best_i = int(np.argmax(hms))
    ax1.scatter([ranks[best_i]], [hms[best_i]], s=140, facecolors="none", edgecolors="#D55E00", linewidths=1.8, zorder=10)
    ax1.set_xlabel("SRRA rank $r$")
    ax1.set_ylabel("HM (%)", color="#D55E00")
    ax2.set_ylabel("Trainable (M)", color="#0072B2")
    ax1.set_xticks(ranks)
    ax1.grid(True, alpha=0.25, linewidth=0.4)
    ax1.set_title("Rank ablation", fontsize=9, pad=6)
    _save(fig, out)


def render_beta_multi(results: dict, out: Path) -> None:
    rows = results["ablation_beta"]["rows"]
    betas = [r["beta"] for r in rows]
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    ax.plot(betas, [r["base"] for r in rows], "s-", color="#555555", label="Base", linewidth=1.2)
    ax.plot(betas, [r["novel"] for r in rows], "^-", color="#0072B2", label="Novel", linewidth=1.4)
    ax.plot(betas, [r["h_mean"] for r in rows], "*-", color="#D55E00", label="HM", linewidth=2.0, markersize=9, zorder=5)
    ax.set_xlabel("Composition weight $\\beta$")
    ax.set_ylabel("Accuracy (%)")
    ax.legend(fontsize=7, loc="lower right", frameon=False)
    ax.grid(True, alpha=0.25, linewidth=0.4)
    ax.set_title("PRC composition-weight ablation", fontsize=9, pad=6)
    _save(fig, out)


def render_gradient_flow(results: dict, out: Path) -> None:
    g = results["gradient_analysis"]
    layers = g["layers"]
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    ax.plot(layers, g["mmrl_grad_norm"],   "o--", color="#0072B2", label=f"MMRL (var={g['mmrl_variance']:.2e})", linewidth=1.2)
    ax.plot(layers, g["mmrlpp_grad_norm"], "*-",  color="#D55E00", label=f"MMRL++ (var={g['mmrlpp_variance']:.2e})", linewidth=2.0, markersize=9, zorder=5)
    ax.set_xlabel("Transformer layer index")
    ax.set_ylabel("Gradient $L_2$ norm")
    ax.legend(fontsize=7, frameon=False)
    ax.grid(True, alpha=0.25, linewidth=0.4)
    ax.set_title("Per-layer gradient flow", fontsize=9, pad=6)
    _save(fig, out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path)
    ap.add_argument("--mode", choices=["pareto", "rank_dual", "beta_multi", "gradient_flow", "line", "bar"])
    ap.add_argument("--results", type=Path, default=Path("results/_index.json"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    if args.mode in {"pareto", "rank_dual", "beta_multi", "gradient_flow"}:
        results = json.loads(args.results.read_text(encoding="utf-8"))
        dispatch = {
            "pareto": render_pareto,
            "rank_dual": render_rank_dual,
            "beta_multi": render_beta_multi,
            "gradient_flow": render_gradient_flow,
        }
        dispatch[args.mode](results, args.out)
        print(f"[viz_draft] {args.mode} -> {args.out}")
        return 0

    if not args.spec:
        raise SystemExit("--spec is required for generic line/bar mode")
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    data_path = Path(spec["data_source"])
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    viz = args.mode or spec.get("viz_type", "line")
    if viz == "line":
        render_line(spec, data, args.out)
    elif viz == "bar":
        render_bar(spec, data, args.out)
    else:
        raise SystemExit(f"viz_type {viz!r} not implemented. Hand to scientist.")
    print(f"[viz_draft] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
