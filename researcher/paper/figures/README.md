# Paper Figures

This directory contains figure specifications and placeholder files for the MMRL++ paper.

## Status: PLACEHOLDER MODE

All figures (except Fig 1 - architecture diagram) are currently in **placeholder mode** pending real data from the Model Zoo. Each figure has:

1. **Specification file** (`fig*.spec.json`) - Complete metadata including:
   - Caption and narrative
   - Data source references
   - Visualization type and constraints
   - Placeholder data structure

2. **Style sheet** (`_style.mplstyle`) - NeurIPS-compatible matplotlib styling

3. **Manifest** (`_manifest.json`) - Central registry of all figures

## Figure List

| Fig | Type | Status | Data Source |
|-----|------|--------|-------------|
| 1 | Architecture diagram | To be drawn in Typst (cetz) | N/A |
| 2 | Pareto frontier scatter | Placeholder | `results/_index.json` |
| 3 | Rank ablation line plot | Placeholder | `results/ablation_rank.json` |
| 4 | Beta ablation line plot | Placeholder | `results/ablation_beta.json` |
| 5 | Gradient flow heatmap | Placeholder | `results/gradient_analysis.json` |
| 6 | Representation similarity heatmap | Placeholder | `results/representation_similarity.json` |
| 7 | Qualitative examples grid | Placeholder | `results/qualitative/*.png` |

## Generating Real Figures

Once real data is available from Model Zoo:

1. Update `results/_index.json` with actual experimental results
2. Run the draft script for each figure:
   ```bash
   uv run python scripts/viz_draft.py --spec paper/figures/fig2_pareto.spec.json --out paper/figures/fig2_pareto.svg
   ```
3. Run the critic to validate:
   ```bash
   uv run python scripts/viz_critic.py --spec paper/figures/fig2_pareto.spec.json --image paper/figures/fig2_pareto.svg
   ```
4. Refine based on critique feedback

## Figure 1: Architecture Diagram

The architecture diagram will be drawn directly in `paper/sections/methodology.typ` using Typst's `cetz` package. It should show:

- CLIP backbone (frozen)
- Learnable representation tokens (5 × 512-dim)
- Shared-Residual Representation Aligner (SRRA) with:
  - Shared base weights
  - Layer-specific rank-4 residuals
- Progressive Representation Composition (PRC) flow
- Dual-path feature extraction

## Notes

- All figures use monochrome-safe color schemes for print compatibility
- Font sizes meet NeurIPS minimum requirements (≥8pt)
- Maximum width constrained to 3.3 inches (single column) or 6.5 inches (double column)
- Aspect ratios optimized for readability

## Placeholder Markers

Throughout the paper, numerical values are marked with `[NUM:?]` to indicate they need to be filled from Model Zoo results. The same applies to figure data.