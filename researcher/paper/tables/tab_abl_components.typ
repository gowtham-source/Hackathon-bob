// tab:abl_components  src: results/_index.json#ablation_components
#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Variant*], [*SRRA*], [*PRC*], [*Base*], [*Novel*], [*HM*], [*$Delta$*],
    table.hline(stroke: 0.4pt),
    table.cell(fill: rgb("#FFF3E0"))[*Full MMRL++*],
    table.cell(fill: rgb("#FFF3E0"))[$checkmark$],
    table.cell(fill: rgb("#FFF3E0"))[$checkmark$],
    table.cell(fill: rgb("#FFF3E0"))[*84.85*],
    table.cell(fill: rgb("#FFF3E0"))[*77.62*],
    table.cell(fill: rgb("#FFF3E0"))[*81.08*],
    table.cell(fill: rgb("#FFF3E0"))[--],
    [w/o SRRA],     [],          [$checkmark$], [83.21], [75.98], [79.42], [#text(fill: rgb("#B71C1C"))[-1.66]],
    [w/o PRC],      [$checkmark$],[],           [82.89], [75.62], [79.05], [#text(fill: rgb("#B71C1C"))[-2.03]],
    [w/o both],     [],          [],            [81.95], [74.10], [77.84], [#text(fill: rgb("#B71C1C"))[-3.24]],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    Ablation of the two MMRL++ components on base-to-novel
    generalization, averaged over 11 datasets. Both SRRA and PRC
    contribute positively and their gains are nearly additive,
    confirming that they address complementary aspects: SRRA reduces
    parameter redundancy while PRC introduces inter-layer semantic flow.
  ],
) <tab:abl_components>
