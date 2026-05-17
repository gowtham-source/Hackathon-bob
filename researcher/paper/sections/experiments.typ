= Experimental Setup

== Datasets

We evaluate MMRL++ across three settings using 15 datasets, summarized in @tab:dataset_stats. For *base-to-novel generalization* and *few-shot learning*, we use 11 recognition datasets: ImageNet, Caltech101, OxfordPets, StanfordCars, Flowers102, Food101, FGVCAircraft, SUN397, DTD, EuroSAT, and UCF101. Each dataset is split into base and novel classes following the protocol of #cite(<zhou2022coop>). For *cross-dataset transfer*, we train on ImageNet and evaluate zero-shot transfer to the remaining 10 target datasets plus 4 ImageNet variants (ImageNet-V2, ImageNet-Sketch, ImageNet-A, ImageNet-R).

#include "../tables/tab_dataset_stats.typ"

== Baselines

We compare against state-of-the-art prompt learning methods: CoOp #cite(<zhou2022coop>), CoCoOp #cite(<zhou2022cocoop>), MaPLe #cite(<khattak2023maple>), and MMRL #cite(<guo2025mmrl>). For ablation studies, we also compare against LoRA-CLIP (standard LoRA applied to CLIP without SRRA or PRC).

== Implementation Details

*Architecture*: We use CLIP with ViT-B/16 backbone #cite(<radford2021clip>) #cite(<dosovitskiy2020vit>). Representation tokens are injected into transformer layers 6-12 ($L=7$ layers). Each modality uses 5 representation tokens of dimension 512 ($n_r = 5$, $d_r = 512$). SRRA employs rank-4 residuals ($r=4$).

*Training*: We use AdamW optimizer with learning rate 0.001, batch size 4, and train for 10 epochs for base-to-novel and few-shot settings, 20 epochs for cross-dataset. We employ automatic mixed precision (AMP) for efficiency. The composition weight is $beta = 0.9$, classification loss weight $alpha = 0.7$, and regularization weight $lambda = 1.0$. All experiments are run with 3 random seeds (1, 2, 3) and we report mean and standard deviation.

*Evaluation Protocol*: For base-to-novel generalization, we train on base classes with 16 shots per class and evaluate on both base and novel classes, reporting harmonic mean (HM). For few-shot learning, we vary shots per class in {1, 2, 4, 8, 16} and report accuracy. For cross-dataset transfer, we train on ImageNet base classes and evaluate zero-shot on target datasets without fine-tuning.

== Metrics

We report top-1 accuracy for all settings. For base-to-novel generalization, we additionally report base accuracy (H), novel accuracy (N), and their harmonic mean: $"HM" = 2 times "H" times "N" / ("H" + "N")$. Statistical significance is assessed via paired t-tests across the 3 seeds.