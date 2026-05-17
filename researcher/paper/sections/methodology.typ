= Methodology

== Preliminaries and Motivation

CLIP #cite(<radford2021clip>) consists of dual encoders: a vision transformer #cite(<dosovitskiy2020vit>) $f_v$ and a text transformer $f_t$ trained with contrastive learning on image-text pairs. Given an image $bold(x)$ and text prompt $bold(p)$, CLIP computes normalized features $bold(v) = f_v(bold(x)) / ||f_v(bold(x))||$ and $bold(t) = f_t(bold(p)) / ||f_t(bold(p))||$, then predicts class $c$ via similarity: $P(c|bold(x)) prop exp(lr(angle.l bold(v), bold(t)_c angle.r) / tau)$ where $tau$ is a learned temperature parameter.

Recent prompt learning methods #cite(<zhou2022coop>) #cite(<khattak2023maple>) #cite(<guo2025mmrl>) introduce learnable tokens into the frozen CLIP encoders to enable efficient adaptation. However, these approaches face two key limitations. First, methods like MaPLe and MMRL employ *independent projection layers* for each transformer layer, resulting in parameter redundancy. For $L$ layers with representation dimension $d_r$ and encoder dimension $d_e$, this requires $L times d_r times d_e$ parameters per modality. Second, these methods treat each layer's adaptation independently, missing opportunities for inter-layer semantic composition that could enhance representation quality through progressive refinement.

Our approach addresses both limitations through two innovations: Shared-Residual Representation Aligner (SRRA) for parameter efficiency and Progressive Representation Composition (PRC) for inter-layer semantic flow. @fig:arch presents an overview of the full architecture.

#figure(
  image("../figures/fig_arch_image.jpg", width: 95%),
  caption: [
    MMRL++ architecture. Frozen CLIP image and text encoders (gray) receive
    trainable representation tokens via per-layer Shared-Residual
    Representation Aligners (SRRA, amber) that share a base projection
    $W_"base"$ and add layer-specific rank-$4$ residuals $A_l B_l$. Tokens
    are progressively composed across layers $6$--$12$ via the Progressive
    Representation Composition (PRC) module with weight $beta = 0.9$. The
    Weighted Fusion (blue) combines original CLIP logits with the
    representation-enhanced logits via $alpha = 0.7$. Only $0.78$M
    parameters are trainable; the encoders remain frozen.
  ],
) <fig:arch>

== Shared-Residual Representation Aligner

SRRA reduces parameter redundancy by decomposing the projection function into shared base weights and layer-specific low-rank residuals. For a projection from representation space $RR^(d_r)$ to encoder space $RR^(d_e)$, we define:

$ f_l (bold(x)) = (bold(W)_"base" + bold(A)_l bold(B)_l) bold(x) + bold(b)_l $

where $bold(W)_"base" in RR^(d_e times d_r)$ are shared base weights, $bold(A)_l in RR^(d_e times r)$ and $bold(B)_l in RR^(r times d_r)$ are layer-specific low-rank matrices with rank $r$, and $bold(b)_l in RR^(d_e)$ is a layer-specific bias. This design is inspired by LoRA #cite(<hu2021lora>) but differs in two key aspects: (1) the base weights $bold(W)_"base"$ are shared across all layers, enabling gradient flow between layers, and (2) the residuals $bold(A)_l bold(B)_l$ capture layer-specific adaptations while maintaining a low-rank structure.

The parameter count for SRRA is:

$ "Params"_"SRRA" = d_e times d_r + L times (d_e times r + r times d_r + d_e) $

For $L=7$ layers, $d_r = 512$, $d_e = 512$, and $r=4$, this yields approximately $262k + 7 times 6.7k = 309k$ parameters per modality, compared to $L times d_r times d_e = 1.8M$ for independent projections—a reduction of over 80%.

The shared base weights enable gradient sharing across layers during backpropagation. When computing $diff cal(L) / diff bold(W)_"base"$, gradients from all $L$ layers accumulate, providing richer training signals compared to independent projections where each layer's weights receive gradients only from that layer. The low-rank residuals $bold(A)_l bold(B)_l$ maintain layer-specific expressiveness while constraining the adaptation space, acting as a regularizer that prevents overfitting.

== Progressive Representation Composition

While SRRA addresses parameter efficiency, it does not capture inter-layer dependencies. PRC introduces semantic flow across layers through beta-weighted composition of representation tokens. Let $bold(R)_0 in RR^(n_r times d_r)$ denote the base learnable representation tokens (where $n_r = 5$ is the number of tokens). For layer $l$, we compute:

$ bold(R)_l = beta bold(R)_(l-1) + (1 - beta) bold(R)_0 $

where $beta in [0, 1]$ controls the composition weight. This creates a progressive refinement mechanism: early layers ($l$ small) rely more on the base tokens $bold(R)_0$, while deeper layers ($l$ large) accumulate information from previous layers through the recursive composition.

The composition can be expanded recursively:

$ bold(R)_l = beta^l bold(R)_0 + sum_(i=0)^(l-1) beta^i (1-beta) bold(R)_0 = bold(R)_0 $

However, in practice, the tokens $bold(R)_l$ are projected through SRRA at each layer, creating instance-specific adaptation paths. The projected tokens $bold(R)_l^"vis" = f_l^"vis"(bold(R)_l)$ and $bold(R)_l^"text" = f_l^"text"(bold(R)_l)$ are injected into the vision and text transformers at layer $l$, where they interact with image patches or text tokens through self-attention.

The beta parameter controls the trade-off between stability (low $beta$: each layer stays close to base tokens) and expressiveness (high $beta$: layers can deviate more from base tokens). Empirically, we find $beta = 0.9$ works well across most datasets, providing sufficient inter-layer flow while maintaining stability.

== Training Objective

Our training objective combines multi-modal alignment with regularization to maintain compatibility with pre-trained CLIP features. Given an image-label pair $(bold(x), y)$, we compute two sets of logits: original CLIP logits $bold(z) = lr(angle.l bold(v)_"clip", bold(t)_"clip" angle.r) / tau$ and enhanced logits with representation tokens $bold(z)_"rep" = lr(angle.l bold(v)_"rep", bold(t)_"rep" angle.r) / tau$. The classification loss is:

$ cal(L)_"cls" = alpha cal(L)_"CE"(bold(z), y) + (1 - alpha) cal(L)_"CE"(bold(z)_"rep", y) $

where $cal(L)_"CE"$ is cross-entropy loss and $alpha in [0, 1]$ balances the two terms. We set $alpha = 0.7$ to emphasize the enhanced features while maintaining alignment with original CLIP.

To prevent the enhanced features from deviating too far from CLIP's feature space, we add cosine similarity regularization:

$ cal(L)_"reg" = lambda (cal(L)_"cos"^"img" + cal(L)_"cos"^"text") $

where $cal(L)_"cos"^"img" = 1 - "cos"(bold(v)_"clip", bold(v)_"rep")$ and $cal(L)_"cos"^"text" = 1 - "cos"(bold(t)_"clip", bold(t)_"rep")$. The regularization weight $lambda = 1.0$ ensures the enhanced features remain in the vicinity of CLIP's feature manifold, preserving zero-shot capabilities.

The final loss is:

$ cal(L) = cal(L)_"cls" + lambda cal(L)_"reg" $

During training, only the representation tokens $bold(R)_0$, SRRA parameters ($bold(W)_"base"$, ${bold(A)_l, bold(B)_l}_(l=1)^L$, ${bold(b)_l}_(l=1)^L$), and projection heads are updated. The CLIP encoders remain frozen, ensuring efficient adaptation with minimal trainable parameters.