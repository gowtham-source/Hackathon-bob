// tab:abl_rank_beta  src: results/_index.json#ablation_rank, ablation_beta
// Single figure containing two side-by-side sub-tables.
#figure(
  grid(
    columns: (1fr, 1fr),
    gutter: 1.2em,
    [
      #set align(center)
      *(a) SRRA rank ablation*
      #v(0.3em)
      #table(
        columns: (auto, auto, auto),
        align: (center, center, center),
        stroke: none,
        table.hline(stroke: 0.8pt),
        [*Rank $r$*], [*HM*], [*Trainable*],
        table.hline(stroke: 0.4pt),
        [1],  [78.91], [0.62M],
        [2],  [79.42], [0.68M],
        table.cell(fill: rgb("#FFF3E0"))[*4*],
        table.cell(fill: rgb("#FFF3E0"))[*81.08*],
        table.cell(fill: rgb("#FFF3E0"))[0.78M],
        [8],  [80.84], [0.92M],
        [16], [80.63], [1.21M],
        table.hline(stroke: 0.8pt),
      )
    ],
    [
      #set align(center)
      *(b) PRC composition-weight ablation*
      #v(0.3em)
      #table(
        columns: (auto, auto, auto, auto),
        align: (center, center, center, center),
        stroke: none,
        table.hline(stroke: 0.8pt),
        [*$beta$*], [*Base*], [*Novel*], [*HM*],
        table.hline(stroke: 0.4pt),
        [0.1], [83.45], [74.21], [78.55],
        [0.3], [83.30], [75.10], [78.99],
        [0.5], [83.41], [76.05], [79.55],
        [0.7], [84.05], [76.85], [80.29],
        table.cell(fill: rgb("#FFF3E0"))[*0.9*],
        table.cell(fill: rgb("#FFF3E0"))[*84.85*],
        table.cell(fill: rgb("#FFF3E0"))[*77.62*],
        table.cell(fill: rgb("#FFF3E0"))[*81.08*],
        table.hline(stroke: 0.8pt),
      )
    ],
  ),
  caption: [
    (a) Effect of SRRA rank $r$ on harmonic mean and trainable parameter
    count. $r = 4$ is the sweet spot; lower ranks underfit, higher ranks
    add parameters without further accuracy gains.
    (b) Effect of the PRC composition weight $beta$ on base, novel, and
    harmonic-mean accuracy. Higher $beta$ improves novel-class accuracy
    monotonically while preserving base-class accuracy.
  ],
) <tab:abl_rank_beta>
