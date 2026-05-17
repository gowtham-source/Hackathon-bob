// tab:few_shot  src: results/_index.json#few_shot_curve
#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Method*], [*1-shot*], [*2-shot*], [*4-shot*], [*8-shot*], [*16-shot*],
    table.hline(stroke: 0.4pt),
    [CoOp],    [57.41 #h(0.1em)±1.12], [62.83 #h(0.1em)±0.94], [68.27 #h(0.1em)±0.82], [73.40 #h(0.1em)±0.68], [79.76 #h(0.1em)±0.55],
    [CoCoOp],  [60.55 #h(0.1em)±0.91], [64.39 #h(0.1em)±0.87], [68.97 #h(0.1em)±0.76], [72.18 #h(0.1em)±0.62], [75.62 #h(0.1em)±0.51],
    [MaPLe],   [63.83 #h(0.1em)±0.77], [67.92 #h(0.1em)±0.71], [72.14 #h(0.1em)±0.65], [76.85 #h(0.1em)±0.52], [81.67 #h(0.1em)±0.43],
    [MMRL],    [#underline[65.41] #h(0.1em)±0.71], [#underline[69.45] #h(0.1em)±0.65], [#underline[73.40] #h(0.1em)±0.58], [#underline[78.21] #h(0.1em)±0.46], [#underline[82.83] #h(0.1em)±0.39],
    table.hline(stroke: 0.4pt),
    table.cell(fill: rgb("#FFF3E0"))[*MMRL++*],
    table.cell(fill: rgb("#FFF3E0"))[*66.32* #h(0.1em)±0.58],
    table.cell(fill: rgb("#FFF3E0"))[*70.21* #h(0.1em)±0.52],
    table.cell(fill: rgb("#FFF3E0"))[*74.05* #h(0.1em)±0.47],
    table.cell(fill: rgb("#FFF3E0"))[*78.74* #h(0.1em)±0.38],
    table.cell(fill: rgb("#FFF3E0"))[*83.23* #h(0.1em)±0.31],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    Few-shot learning accuracy (top-1, %) averaged over 11 datasets and 3
    seeds, for shots $in {1, 2, 4, 8, 16}$. MMRL++ has the smallest variance
    across seeds at every shot level, indicating more stable adaptation
    under limited supervision.
  ],
) <tab:few_shot>
