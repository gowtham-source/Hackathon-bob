// tab:dataset_stats  src: results/_index.json#dataset_stats
#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, left),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Dataset*], [*Classes*], [*Train*], [*Val*], [*Test*], [*Domain*],
    table.hline(stroke: 0.4pt),
    [ImageNet],     [1000], [1{,}281{,}167], [50{,}000], [50{,}000], [General],
    [Caltech101],   [100],  [4{,}128],       [1{,}649],  [2{,}465],  [General],
    [OxfordPets],   [37],   [2{,}944],       [736],      [3{,}669],  [Fine-grained],
    [StanfordCars], [196],  [6{,}509],       [1{,}635],  [8{,}041],  [Fine-grained],
    [Flowers102],   [102],  [4{,}093],       [1{,}633],  [2{,}463],  [Fine-grained],
    [Food101],      [101],  [50{,}500],      [20{,}200], [30{,}300], [Fine-grained],
    [FGVCAircraft], [100],  [3{,}334],       [3{,}333],  [3{,}333],  [Fine-grained],
    [SUN397],       [397],  [15{,}880],      [3{,}970],  [19{,}850], [Scene],
    [DTD],          [47],   [2{,}820],       [1{,}128],  [1{,}692],  [Texture],
    [EuroSAT],      [10],   [13{,}500],      [5{,}400],  [8{,}100],  [Satellite],
    [UCF101],       [101],  [7{,}639],       [1{,}898],  [3{,}783],  [Action],
    table.hline(stroke: 0.8pt),
  ),
  caption: [
    The 11 datasets used in our base-to-novel and few-shot evaluations.
    For base-to-novel, each dataset is split into base and novel classes
    following #cite(<zhou2022coop>). For cross-dataset transfer, we train on
    ImageNet and evaluate on the remaining 10 plus four ImageNet variants.
  ],
) <tab:dataset_stats>
