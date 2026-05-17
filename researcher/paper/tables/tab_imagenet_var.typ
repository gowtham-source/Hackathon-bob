// tab:imagenet_var  src: results/_index.json#imagenet_variants
#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Method*], [*INet-V2*], [*INet-S*], [*INet-A*], [*INet-R*], [*Avg*],
    table.hline(stroke: 0.4pt),
    [CoOp],    [64.20], [47.99], [49.71], [75.21], [59.28],
    [CoCoOp],  [64.07], [48.75], [50.63], [76.18], [59.91],
    [MaPLe],   [64.07], [49.15], [50.90], [76.98], [60.27],
    [MMRL],    [#underline[65.55]], [#underline[49.47]], [#underline[50.94]], [#underline[77.18]], [#underline[60.78]],
    table.hline(stroke: 0.4pt),
    table.cell(fill: rgb("#FFF3E0"))[*MMRL++*],
    table.cell(fill: rgb("#FFF3E0"))[*65.91*],
    table.cell(fill: rgb("#FFF3E0"))[*49.83*],
    table.cell(fill: rgb("#FFF3E0"))[*51.20*],
    table.cell(fill: rgb("#FFF3E0"))[*77.85*],
    table.cell(fill: rgb("#FFF3E0"))[*61.19*],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    Domain generalization on four ImageNet variants. MMRL++ improves over
    MMRL on every variant, demonstrating that the shared-residual design
    preserves CLIP's robustness to distribution shift.
  ],
) <tab:imagenet_var>
