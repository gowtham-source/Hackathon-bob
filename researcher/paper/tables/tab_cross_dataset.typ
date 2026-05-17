// tab:cross_dataset  src: results/_index.json#cross_dataset
#figure(
  table(
    columns: 12,
    align: (left, center, center, center, center, center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Method*], [Cal101], [Pets], [Cars], [Flwr], [Food], [Air], [SUN], [DTD], [EuSAT], [UCF], [*Avg*],
    table.hline(stroke: 0.4pt),
    [CoOp],    [93.70], [89.14], [64.51], [68.71], [85.30], [18.47], [64.15], [41.92], [46.39], [66.55], [63.88],
    [CoCoOp],  [94.43], [90.14], [#underline[71.20]], [71.88], [86.06], [22.94], [67.36], [45.73], [45.37], [68.21], [66.33],
    [MaPLe],   [93.53], [90.49], [65.57], [72.23], [#underline[86.20]], [24.74], [67.01], [#underline[46.49]], [48.06], [68.69], [66.30],
    [MMRL],    [93.84], [#underline[90.71]], [65.92], [#underline[72.14]], [85.93], [#underline[24.83]], [#underline[67.36]], [46.04], [#underline[49.45]], [#underline[69.83]], [#underline[66.60]],
    table.hline(stroke: 0.4pt),
    table.cell(fill: rgb("#FFF3E0"))[*MMRL++*],
    table.cell(fill: rgb("#FFF3E0"))[*94.21*], table.cell(fill: rgb("#FFF3E0"))[*91.05*], table.cell(fill: rgb("#FFF3E0"))[66.83],
    table.cell(fill: rgb("#FFF3E0"))[*72.65*], table.cell(fill: rgb("#FFF3E0"))[85.14], table.cell(fill: rgb("#FFF3E0"))[*25.45*],
    table.cell(fill: rgb("#FFF3E0"))[*67.92*], table.cell(fill: rgb("#FFF3E0"))[46.27], table.cell(fill: rgb("#FFF3E0"))[*49.81*],
    table.cell(fill: rgb("#FFF3E0"))[*70.42*], table.cell(fill: rgb("#FFF3E0"))[*67.08*],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    Cross-dataset transfer: train on ImageNet, evaluate zero-shot on
    10 target datasets (top-1, %). Despite using $5.4 times$ fewer
    trainable parameters, MMRL++ achieves the best average transfer
    accuracy.
  ],
) <tab:cross_dataset>
