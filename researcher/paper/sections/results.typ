= Results

== Main Results

=== Base-to-novel generalization

@tab:base_to_novel reports base-to-novel generalization averaged over 11
recognition datasets and 3 seeds. MMRL++ achieves a harmonic mean of
$bold(81.08%)$ ($plus.minus 0.27$), outperforming MMRL ($80.44%$) and MaPLe
($78.55%$) while using only $0.78$M trainable parameters --- a
$bold(81.5%)$ reduction relative to MMRL.
// src: results/_index.json#base_to_novel.averages

The harmonic-mean improvement is driven primarily by stronger novel-class
performance: MMRL++ reaches $77.62%$ novel accuracy versus $76.91%$ for
MMRL and $75.14%$ for MaPLe, while preserving (and slightly improving)
base-class accuracy at $84.85%$. The gains are largest on fine-grained
datasets where prior-knowledge transfer matters most: StanfordCars
($79.00%$ HM vs. $77.88%$ for MMRL, $73.47%$ for MaPLe) and FGVCAircraft
($41.22%$ HM vs. $39.71%$ for MMRL, $36.50%$ for MaPLe).
// src: results/_index.json#base_to_novel.rows

#include "../tables/tab_base_to_novel.typ"

=== Few-shot learning

@tab:few_shot reports few-shot accuracy from $1$ to $16$ shots per class.
MMRL++ wins at every shot level, with the gap widest in the low-shot
regime: $bold(+0.91)$ percentage points over MMRL at 1-shot ($66.32%$ vs.
$65.41%$). Equally important, MMRL++ has the lowest seed-to-seed standard
deviation at every shot level (e.g.\ $plus.minus 0.31$ vs.\ $plus.minus 0.39$ for MMRL at
16-shot), indicating more stable optimization. This stability is a direct
consequence of the SRRA shared base, which receives gradient signal from
all layers simultaneously.
// src: results/_index.json#few_shot_curve

#include "../tables/tab_few_shot.typ"

=== Cross-dataset transfer

@tab:cross_dataset reports zero-shot transfer from ImageNet-trained
weights to ten downstream targets. MMRL++ leads the average ($67.08%$)
and wins on seven of ten datasets, including the most challenging
fine-grained transfer benchmark FGVCAircraft ($+0.62$ pp over MMRL).
Strikingly, MMRL++ matches or exceeds CoCoOp on StanfordCars despite
having $2.2 times$ more parameters --- the harmonic-mean wins are not
purchased by overfitting to base classes.
// src: results/_index.json#cross_dataset

#include "../tables/tab_cross_dataset.typ"

@tab:imagenet_var examines distribution shift on four ImageNet variants
(V2, Sketch, A, R). MMRL++ improves over MMRL on every variant, with the
largest gain on ImageNet-R ($+0.67$ pp). Because SRRA's residuals are
low-rank, the model cannot easily fit dataset-specific artifacts, and the
shared base preserves CLIP's pretrained robustness.
// src: results/_index.json#imagenet_variants

#include "../tables/tab_imagenet_var.typ"

== Parameter Efficiency

@tab:efficiency compares trainable parameter counts, total parameters,
inference throughput, and headline HM. MMRL++ trains only $0.78$M of
$150.40$M parameters ($0.52%$) and runs at $1432$ img/s --- the second
highest throughput after CoOp, which itself is $9.42$ pp behind on HM.
The cost of MMRL's per-layer independent projections is now quantified:
the extra $3.43$M trainable parameters yield $-0.64$ pp on HM.
// src: results/_index.json#parameter_efficiency

#include "../tables/tab_efficiency.typ"

@fig:pareto summarizes the efficiency-accuracy trade-off. MMRL++ sits on the Pareto frontier: no other method achieves higher harmonic mean with fewer trainable parameters. The gap to MaPLe (closest competitor in accuracy) is $2.53$ pp HM at $3.65 times$ fewer parameters; the gap to CoOp (closest in efficiency) is $9.42$ pp HM at only $0.19$M additional parameters.

#figure(
  image("../figures/fig_pareto.svg", width: 70%),
  caption: [
    Pareto frontier of parameter efficiency vs. accuracy. X-axis: trainable parameters (millions, log scale). 
    Y-axis: harmonic mean (%) averaged over 11 datasets. MMRL++ (orange star) dominates the upper-left quadrant,
    achieving the best accuracy-parameter trade-off among all compared methods.
  ],
) <fig:pareto>

== Ablation Studies

=== Component ablation

@tab:abl_components decomposes the contribution of SRRA and PRC. Removing
SRRA (i.e.\ falling back to independent per-layer projections) costs
$-1.66$ pp on HM at the cost of $3.14$ M extra trainable parameters,
while removing PRC (no inter-layer composition) costs $-2.03$ pp at the
same parameter budget. Removing both components reproduces a naïve
multi-modal prompt baseline and costs $-3.24$ pp, confirming that SRRA
and PRC address complementary failure modes and that their gains are
approximately additive.
// src: results/_index.json#ablation_components

#include "../tables/tab_abl_components.typ"

=== Rank and composition-weight sweeps

@tab:abl_rank_beta reports two sweeps: SRRA rank $r in {1, 2, 4, 8, 16}$
and PRC composition weight $beta in {0.1, 0.3, 0.5, 0.7, 0.9}$. Rank
$r = 4$ is the sweet spot: lower ranks underfit (rank-$1$: $78.91%$ HM)
and higher ranks provide no gain at increased parameter cost (rank-$16$:
$80.63%$ HM with $1.55 times$ the parameters). The PRC weight $beta$
shows a monotone trend: higher composition weight improves both base and
novel accuracy. We attribute this to the recursive accumulation of
representation tokens across layers, which allows later layers to
condition on a richer, instance-specific token state. At $beta = 0.9$
MMRL++ reaches its peak HM of $81.08%$.
// src: results/_index.json#ablation_rank, ablation_beta

#include "../tables/tab_abl_rank_beta.typ"

@fig:rank_ablation visualizes the rank sweep: accuracy rises steeply from rank-1 to rank-4, then plateaus. The parameter cost grows linearly with rank, making rank-4 the clear sweet spot.

#figure(
  image("../figures/fig_rank.svg", width: 70%),
  caption: [
    SRRA rank ablation. Left Y-axis: harmonic mean (%); Right Y-axis: trainable parameters (M). 
    Rank $r=4$ achieves $81.08%$ HM with only $0.78$M parameters. Higher ranks provide diminishing returns 
    at increased cost (rank-16: $80.63%$ HM, $1.55 times$ parameters).
  ],
) <fig:rank_ablation>

@fig:beta_ablation shows the monotonic improvement with increasing $beta$, confirming that progressive composition of representation tokens across layers is beneficial. At $beta=0.9$, MMRL++ achieves peak performance.

#figure(
  image("../figures/fig_beta.svg", width: 70%),
  caption: [
    PRC composition weight $beta$ ablation. X-axis: composition weight $beta in {0.1, 0.3, 0.5, 0.7, 0.9}$. 
    Higher $beta$ (more progressive composition) consistently improves both base and novel accuracy, 
    reaching optimal harmonic mean of $81.08%$ at $beta=0.9$.
  ],
) <fig:beta_ablation>

== Analysis

=== Gradient flow

A central claim of SRRA is that the shared base weight $W_"base"$
receives gradient signal from every layer simultaneously, equalizing the
gradient magnitudes across the network. We measure this directly:
under MMRL, the per-layer gradient $L_2$ norm rises from $0.083$ at
layer $6$ to $0.247$ at layer $12$ (variance $3.21 times 10^(-3)$),
whereas MMRL++ produces nearly uniform gradients $in [0.124, 0.149]$
(variance $8 times 10^(-5)$ --- a $bold(40 times)$ reduction).
// src: results/_index.json#gradient_analysis

This uniform gradient flow has two consequences: (i) deeper layers no
longer dominate optimization, reducing the risk of late-layer
overfitting, and (ii) earlier layers receive sufficient signal to adapt
their representations to the downstream task, which we hypothesise
explains MMRL++'s improved novel-class accuracy.

@fig:gradient_flow visualizes the gradient $L_2$ norms across layers 6--12. The flat curve for MMRL++ confirms that the shared base $W_{"base"}$ receives balanced gradient signal from all layers, while MMRL exhibits the classic "vanishing gradient" pattern in early layers.

#figure(
  image("../figures/fig_gradient.svg", width: 70%),
  caption: [
    Gradient flow analysis across layers 6--12. Y-axis: gradient $L_2$ norm. 
    MMRL (blue) shows increasing gradient magnitude toward deeper layers (variance $3.21 times 10^{-3}$), 
    indicating poor signal in early layers. MMRL++ (orange) produces nearly uniform gradients 
    (variance $8 times 10^{-5}$, $40 times$ reduction), confirming effective gradient equalization 
    via the shared base $W_{"base"}$.
  ],
) <fig:gradient_flow>

=== Representation similarity

We measure inter-layer Centered Kernel Alignment (CKA) of the
representation-token outputs $bold(R)_l$ at layers $6$--$12$. Baseline
CLIP (no PRC, no rep tokens) gives an average inter-layer CKA of
$0.42$ --- representations across layers are weakly related. MMRL++
yields $0.71$ on average and $bold(0.89)$ for adjacent layers,
confirming that the PRC recursion successfully creates structured
semantic flow rather than seven independent token streams.
// src: results/_index.json#cka_analysis
