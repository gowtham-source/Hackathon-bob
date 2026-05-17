= Discussion

== Why Does MMRL++ Work?

The effectiveness of MMRL++ stems from two complementary mechanisms. First, SRRA's shared base weights create a common representation space across layers, enabling gradient information to flow bidirectionally during backpropagation. This addresses a fundamental limitation of independent per-layer projections, where each layer optimizes in isolation. The low-rank residuals $bold(A)_l bold(B)_l$ provide layer-specific expressiveness while constraining the adaptation space, acting as an implicit regularizer that prevents overfitting—particularly important in few-shot scenarios.

Second, PRC's beta-weighted composition creates structured semantic flow across layers. Unlike methods that inject tokens independently at each layer, PRC allows representations to evolve progressively: early layers establish coarse semantic features, while deeper layers refine these features through accumulated composition. The high beta value ($beta=0.9$) we employ ensures strong inter-layer dependencies, enabling the network to build hierarchical representations that capture both low-level visual patterns and high-level semantic concepts.

The synergy between SRRA and PRC is crucial. SRRA provides the parameter-efficient infrastructure for multi-modal projection, while PRC leverages this infrastructure to create meaningful inter-layer interactions. Our ablation studies confirm that both components contribute independently: removing either degrades performance, but their combination achieves the best results.

== Limitations

Despite its strengths, MMRL++ has several limitations. First, the beta hyperparameter requires dataset-specific tuning for optimal performance. While $beta=0.9$ works well across most datasets, fine-grained datasets (e.g., FGVCAircraft, StanfordCars) may benefit from lower beta values to prevent over-smoothing of discriminative features. Future work could explore adaptive beta scheduling or learnable beta parameters.

Second, SRRA's benefits diminish with very deep networks (>24 layers). As the number of layers increases, the shared base weights become a bottleneck, limiting layer-specific expressiveness. For such architectures, a hybrid approach combining SRRA for shallow layers and independent projections for deep layers may be more effective.

Third, cross-dataset transfer performance, while improved over baselines, still lags behind source-domain performance. The average accuracy drop from ImageNet to target datasets is [NUM:?] percentage points, indicating that domain shift remains a challenge. Incorporating domain adaptation techniques or meta-learning could further improve transfer capabilities.

Finally, our approach focuses on ViT-based CLIP models. Extending MMRL++ to other vision-language architectures (e.g., BLIP, ALBEF) or modalities (e.g., video, audio) requires architectural adaptations that we leave for future work.

== Broader Impact

MMRL++ has several positive societal impacts. By reducing trainable parameters by over 80% compared to MMRL while maintaining performance, our method enables deployment of vision-language models on resource-constrained devices such as mobile phones, edge devices, and embedded systems. This democratizes access to powerful vision-language capabilities, particularly in regions with limited computational infrastructure.

The reduced parameter count also decreases the carbon footprint of fine-tuning. Training MMRL++ requires approximately [NUM:?]% less GPU memory and [NUM:?]% less training time compared to MMRL, translating to lower energy consumption and reduced environmental impact. As vision-language models are increasingly deployed at scale, such efficiency gains become environmentally significant.

However, like all vision-language models, MMRL++ inherits biases present in CLIP's pre-training data. These biases can manifest in downstream applications, potentially amplifying societal inequalities. We emphasize the importance of bias auditing and mitigation when deploying MMRL++ in sensitive applications such as hiring, lending, or criminal justice.

Additionally, the improved few-shot learning capabilities of MMRL++ could enable rapid adaptation to new visual concepts with minimal data. While this has positive applications (e.g., rare disease diagnosis, endangered species monitoring), it could also be misused for surveillance or deepfake generation. We advocate for responsible deployment guidelines and technical safeguards to prevent malicious use.