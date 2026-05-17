// tab:base_to_novel  src: results/_index.json#base_to_novel
#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Method*], [*Base*], [*Novel*], [*HM*], [*$Delta$ HM*], [*Trainable*],
    table.hline(stroke: 0.4pt),
    [CoOp],    [82.69], [63.22], [71.66 #h(0.2em)±0.61], [-9.42], [0.01M],
    [CoCoOp],  [80.47], [71.69], [75.83 #h(0.2em)±0.42], [-5.25], [0.36M],
    [MaPLe],   [82.28], [75.14], [78.55 #h(0.2em)±0.38], [-2.53], [3.55M],
    [MMRL],    [84.31], [76.91], [#underline[80.44] #h(0.2em)±0.34], [-0.64], [4.21M],
    table.hline(stroke: 0.4pt),
    table.cell(fill: rgb("#FFF3E0"))[*MMRL++ (ours)*],
    table.cell(fill: rgb("#FFF3E0"))[*84.85*],
    table.cell(fill: rgb("#FFF3E0"))[*77.62*],
    table.cell(fill: rgb("#FFF3E0"))[*81.08* #h(0.2em)±0.27],
    table.cell(fill: rgb("#FFF3E0"))[-],
    table.cell(fill: rgb("#FFF3E0"))[*0.78M*],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    Base-to-novel generalization averaged over 11 datasets, 3 seeds.
    HM is harmonic mean of base and novel accuracy. Best in *bold*,
    second best _underlined_. MMRL++ achieves the highest HM with
    $bold(5.4 times)$ fewer trainable parameters than MMRL.
  ],
) <tab:base_to_novel>
