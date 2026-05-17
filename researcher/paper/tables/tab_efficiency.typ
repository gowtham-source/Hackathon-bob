// tab:efficiency  src: results/_index.json#parameter_efficiency
#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Method*], [*Trainable*], [*Total*], [*% Trainable*], [*Throughput*], [*HM*],
    [],         [(M)],          [(M)],     [],               [(img/s)],     [(%)],
    table.hline(stroke: 0.4pt),
    [CoOp],    [#underline[0.01]], [149.62], [#underline[0.007]], [*1485*],   [71.66],
    [CoCoOp],  [0.36], [149.98], [0.24],   [983],                 [75.83],
    [MaPLe],   [3.55], [153.17], [2.37],   [1320],                [78.55],
    [MMRL],    [4.21], [153.83], [2.81],   [1265],                [#underline[80.44]],
    table.hline(stroke: 0.4pt),
    table.cell(fill: rgb("#FFF3E0"))[*MMRL++*],
    table.cell(fill: rgb("#FFF3E0"))[*0.78*],
    table.cell(fill: rgb("#FFF3E0"))[*150.40*],
    table.cell(fill: rgb("#FFF3E0"))[*0.52*],
    table.cell(fill: rgb("#FFF3E0"))[#underline[1432]],
    table.cell(fill: rgb("#FFF3E0"))[*81.08*],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    Parameter-efficiency comparison. MMRL++ achieves the best harmonic
    mean (81.08%) while training only 0.52% of the network parameters
    --- $5.4 times$ fewer than MMRL and $4.6 times$ fewer than MaPLe
    --- and the second-highest inference throughput.
    Throughput measured at batch size 32 on a single A100 GPU.
  ],
) <tab:efficiency>
