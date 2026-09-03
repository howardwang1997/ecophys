# Novelty boundary audit for the ICLR attribution paper

Checked 2026-09-01 and updated 2026-09-02 after the complete fresh intervention-cube reveal. This
is a reviewer-risk audit, not a proof of priority.

## Closest established lines

- Analytic output constraints can enforce identities exactly in neural physical emulators:
  [Beucler et al., PRL 2021](https://doi.org/10.1103/PhysRevLett.126.098302).
- Probabilistic correction and its neural-operator/OOD extension use conservation information to
  update predictions:
  [Hansen et al., ICML 2023](https://proceedings.mlr.press/v202/hansen23b.html) and
  [Mouli et al., ICML 2024](https://proceedings.mlr.press/v235/mouli24a.html).
- Learned-invariant projection and hard/invariant neural operators provide exact or architectural
  guarantees:
  [ConCerNet, ICML 2023](https://proceedings.mlr.press/v202/zhang23ao.html),
  [INO, AISTATS 2023](https://proceedings.mlr.press/v206/liu23f.html), and
  [clawNO, ICML 2024](https://proceedings.mlr.press/v235/liu24p.html).
- Hard constraint layers and energy-aware objectives broaden the class of physical restrictions:
  [Harder et al., JMLR 2023](https://www.jmlr.org/papers/v24/22-1438.html) and
  [Tanaka et al., AISTATS 2025](https://proceedings.mlr.press/v258/tanaka25a.html).
- Learned adaptive correction guarantees linear or quadratic conservation while distributing the
  correction flexibly:
  [Liu et al., arXiv:2505.24579](https://arxiv.org/abs/2505.24579).
- The closest established projection ablation is
  [Duruisseaux et al., ICML AI for Science 2024](https://openreview.net/forum?id=Zvxm14Rd1F).
  It compares an unconstrained FNO, post-hoc projection, constraint finetuning, and fully
  constrained training, explicitly establishing that the layer can be used during or after
  training. It does not remove projection from the same fully constrained checkpoint, cross
  absolute/residual output coordinates, or propagate that same-weight intervention through an
  autoregressive rollout. The present paper must define ``plug-and-play'' as this stronger
  compositional claim and must not imply that software compatibility itself has been disproved.
- The closest inspected contemporaneous system is the public ICLR 2026 submission
  [Flow-Based Automatic Neural Operator with Hard Physical Constraints](https://openreview.net/forum?id=lRGAMx3f6N).
  Its Physics-Manifold Flow Matching model combines hard tangent-space projection with a residual
  geometric-guidance branch. Its revised public PDF reports Pure Net, Projection Only,
  Projection+GGM, Projection+Gate, and Full-model variants, including a projection-versus-GGM
  accuracy comparison. This materially narrows any novelty claim based on residual compensation
  or a projection-only ablation.
- Gradient imbalance and directional conflict between composite physics-loss terms are established
  in PINNs, including optimizer interventions:
  [MultiAdam, ICML 2023](https://proceedings.mlr.press/v202/yao23c.html),
  [Dual Cone Gradient Descent, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/b2b781badeeb49896c4b324c466ec442-Abstract-Conference.html), and
  [Gradient Alignment in PINNs, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f655706547885b8e32ef46f1c067ece2-Abstract-Conference.html).
- FNO supplies the shared resolution-transfer backbone, while residual update prediction is a
  known simulation inductive bias:
  [Li et al., ICLR 2021](https://openreview.net/forum?id=c8P9NQVtmnO) and
  [Pfaff et al., ICLR 2021](https://openreview.net/forum?id=roNqYL0_XP).

## Defensible contribution boundary

The paper does not introduce a new projection or conservation law. Its defensible methodological
contribution is the combination of:

1. an eight-cell output-coordinate-by-training-by-inference intervention cube, including both
   adding projection to free-trained checkpoints and removing it from hard-trained checkpoints
   without changing weights;
2. a projection-gauge non-identification result showing that projected training identifies raw
   outputs only modulo the projected invariant direction, together with a direct same-checkpoint
   input-gauge intervention that resolves material transfer into the next conserving prediction;
3. a minimal non-identification result for the usual three-cell comparison without an additivity
   assumption, and a fully crossed trained intervention over absolute/residual output coordinates
   and free/exact-hard training, with fresh paired seeds and identical initialized tensors;
4. an invariant-violating versus conserving error decomposition and fixed-prediction projection
   control;
5. a channel-separable training-null proposition that identifies when enforcement cannot change
   conserving predictions;
6. an orthogonal-channel gradient-coupling diagnostic tied to an exact matched enforcement
   intervention (not a claim to have introduced gradient alignment);
7. a finite-width tangent-kernel identity showing that the off-diagonal conserving/violating
   channel block is exactly the first-order route by which enforcement can alter admissible
   predictions (not a claim to have introduced NTK analysis);
8. prospectively frozen three-way interaction and path-averaged intervention credits that expose
   large countervailing training and inference paths hidden by their bundled comparison; and
9. public-benchmark OOD evaluation with one primary cell, mandatory secondary cells, a SESOI, and
   integrity-gated one-shot analysis; and
10. an independent nonlinear 2D shallow-water replication that jointly measures conservation,
    conserving dynamics, and positivity, resolving a conservation--positivity synergy rather than
    treating exact invariance alone as success.

The prospectively frozen same-checkpoint input-gauge intervention now strengthens item 2. It
changes only the invariant-direction component of the first predicted history and measures the
second-step conserving-output response. The complete 60-record primary ratio is 8.68398 with a
95% paired interval [7.91007, 9.50538], wholly above the frozen 10% practical threshold; all three
mandatory resolutions agree. The revised outcome-blind numerical identity gate bounds maximum
non-invariant contamination at 6.55e-5 of the projected baseline, below its frozen 0.001 ceiling.
This supports material gauge-to-conserving channel transfer. It does not support the stronger
seed-level magnitude claim: the secondary association with final rollout harm is 0.28765
[-0.09679, 0.62675] and must remain explicitly unresolved.

The inspected primary sources focus on constructing/enforcing physical structure or improving
prediction. The audit did not identify an established paper reporting this exact paired 2 x 2 x 2
coordinate-by-training-by-inference design or its same-checkpoint removal intervention. That
negative search result is not sufficient for a "first" claim. The manuscript should say that the
audit asks a complementary compositional question, not that no prior work has ever separated
training and inference use of a projector.

In particular, the inspected INO and clawNO experiments compare a conservation-aware hypothesis
class with other neural-operator architectures; those comparisons can establish end-to-end
performance but do not hold output coordinates and enforcement interventions fully crossed. PMFM
goes closer by separating projection and residual guidance, but its module ablation is not the
absolute/residual-coordinate by free/hard-training factorial: it does not supply the missing
absolute-hard intervention needed for this paper's interaction and Shapley estimands. The PINN
gradient-conflict papers intervene on optimization of composite PDE objectives, whereas the
present mechanism audit decomposes orthogonal prediction-error channels under a matched exact
enforcement intervention. These distinctions define scope, not superiority over those methods.

## Claims to avoid

- first hard-constrained neural operator, first conservation projection, or first use of Shapley;
- a universal percentage of credit belonging to parameterization or physics;
- causal attribution outside the explicitly randomized seed-paired training interventions;
- generalization from one linear mass invariant to nonlinear energy or entropy;
- treating synthetic pilot-selected systems as pooled independent replications;
- using a null/unresolved interaction as generic robustness evidence;
- claiming that the magnitude of the direct second-step gauge response predicts seed-level final
  rollout harm; that prespecified secondary association is unresolved;
- implying that projection-only versus projection-plus-residual-guidance is a new ablation; PMFM
  publicly reports that comparison.
- implying that post-hoc versus fully constrained training is a new comparison; Duruisseaux et al.
  already report baseline, post-hoc projection, constraint finetuning, and fully constrained arms.
- equating ``compatible during or after training'' with a claim that a projector may safely be
  removed from a checkpoint trained through it; the latter is the new diagnostic intervention.
