# Solenoidal excitation gap — V12 equation and closest-source audit

**Audit date:** 2026-08-13

**Branch:** `global-drift-identifiability-gap-audit-v12`

**Final decision:** `V12_THEOREM_ONLY`

**Compute state:** no experiment preregistered; no remote worker contacted or queued

## 1. Result of the proof attack

V12 strengthens V11's pointwise immersion obstruction into an exact three-regime statement for unrestricted
smooth ambiguity currents on a closed state manifold:

1. fewer than `d` nonbaseline stationary densities leave an explicit nonzero divergence-free ambiguity;
2. exactly `d` densities generically identify the drift globally, but can never provide a positive unrestricted
   `L^2` stability margin; and
3. abstract uniform stability becomes possible at the Euclidean immersion dimension of the state manifold.

The gap in the middle is real. The stationary continuity equation propagates information across the pointwise
rank-defect set, so exact identification can survive, while solenoidal fields concentrate anisotropically near a
critical point and destroy coercivity.

For the two-dimensional standard fold, the concentration is governed by the Grushin energy. An `H^s`-bounded
ambiguity has the sharp deterministic conditional-stability exponent `2s/(2s+1)`. This is more informative than
V11's pointwise rank observation, but it is not by itself an NMI contribution.

## 2. Exact status by object

| V12 object | Status | Reason |
|---|---|---|
| ambiguity operator `T_R` | retained identity | exact reformulation of V11 |
| `gamma(R)>0` iff immersion | proved, no novelty claim | explicit localized solenoidal wave; classical wave-cone mechanism |
| `K<d` nonidentification | proved | compactly supported closed-form/Nambu construction, including variable rank |
| generic `K=d` exact identification | proved modulo standard jet transversality | regular set has full measure, but compactness forces critical points |
| abstract stable count `imm(M)` | proved | V11 immersion construction plus the coercivity equivalence |
| two-dimensional fold exponent | proved in the exact chart | harmonic oscillator/Grushin inequality and matching anisotropic scaling |
| higher Morin/stratified rate | conjecture | normal-form and global-stratum analysis incomplete |
| finite-sample stationary-SDE rate | not established | density/score estimation and dependence are not represented by deterministic observation noise |
| feasible perturbation design | not established | arbitrary density families need not be actuator-reachable |

## 3. Closest primary sources inspected

| Source | Decision-relevant result | Consequence for V12 |
|---|---|---|
| Arroyo-Rabasa et al., [*Higher integrability for measures satisfying a PDE constraint*](https://arxiv.org/abs/2106.03077), Theorem 1.1 | `A`-free fields gain regularity when their values lie near a convex set contained in a subspace disjoint from the wave cone. | Stability away from the wave cone is established machinery. For vector divergence in `d>=2`, the wave cone contains every amplitude direction, matching V12's local instability. |
| Arroyo-Rabasa and Aussedat, [*Compensated compactness of A-free measures on cones with quantified aperture*](https://arxiv.org/abs/2606.16762), Theorem 1.11 | Quantifies compactness when a target cone remains within an aperture controlled by its distance from an elliptic subspace to the wave cone. | A quantitative wave-cone separation principle is already explicit; V12 cannot claim that principle as new. |
| Bal, [*Hybrid inverse problems and redundant systems of partial differential equations*](https://arxiv.org/abs/1210.0265), Sections 2.5 and 2.6 | Redundant internal measurements yield parametrices and optimal stability when the linearized system is elliptic; underdetermined variants can be subelliptic. | “More stationary environments turn an inverse PDE from subelliptic to elliptic” has a mature neighboring theory. |
| Monard and Bal, [*Inverse diffusion problems with redundant internal information*](https://arxiv.org/abs/1106.4277), condition (6) and Theorem 2.3 | Reconstruction assumes a finite cover on which selected solution gradients form a uniformly positive frame and proves global uniqueness/stability. | Gradient-frame redundancy and stable reconstruction are not V12 primitives. The closed-manifold topology and solenoidal ambiguity are the only distinctions. |
| Arnaiz and Sun, [*Sharp resolvent estimate for the Baouendi--Grushin operator and applications*](https://arxiv.org/abs/2201.08189) | Gives sharp subelliptic resolvent regimes and constructs concentrating quasimodes for a Grushin operator. | Fold-scale quasimodes and rate degradation are occupied analytic mechanisms, even though the observation operator differs. |
| Whitney, [*On Singularities of Mappings of Euclidean Spaces I*](https://doi.org/10.2307/1970070), and Thom/Boardman transversality theory | Generic equal-dimensional maps are organized by rank and higher singularity strata; in the surface case folds and cusps occur. | V12 may use standard genericity, but may not say generic maps have only folds in arbitrary dimension. |
| Bal and Uhlmann, [*Reconstructions for some coupled-physics inverse problems*](https://doi.org/10.1016/j.aml.2012.05.013) | Uses ratios of multiple elliptic solutions and their gradients to reconstruct coefficients up to explicit gauges with stability estimates. | Ratios, gradient spanning and gauge removal are established inverse-PDE patterns. |
| Lippner, [*Singularities of projected immersions revisited*](https://doi.org/10.2140/agt.2009.9.1623), Definition 2.4 and following remark | A Morin map lifts through one extra scalar coordinate to an immersion exactly when its kernel line bundle is trivialized. | Adding one density-ratio coordinate to remove folds is the classical projected-immersion lifting problem and can be topologically obstructed. |
| Schmisser, [*Nonparametric estimation of derivatives of the stationary density for stationary processes*](https://doi.org/10.1051/ps/2011102) | Gives adaptive derivative rates for beta-mixing stationary samples and, for a scalar diffusion with known diffusion coefficient, a low-frequency quotient estimator of the drift. | Density/score derivatives and quotient drift estimation are occupied nuisance components; V12's deterministic modulus is not itself a sample-rate result. |

The decision-relevant theorem pages of the first five PDFs were extracted, rendered and visually checked. Keyword
absence was not treated as evidence of novelty.

## 4. Why this is not yet NMI

The obvious computational method is constrained Tikhonov regularization,

\[
 \min_{\mathop{\rm div}_{\mu}j=0}
 \lVert T_Rj-y\rVert_2^2+\lambda\lVert j\rVert_{H^s}^2,
\]

which is standard once the Grushin structure is recognized. Merely implementing it with a neural field would not
create a method contribution. A credible NMI re-entry needs at least one of:

- a minimax theorem for stationary samples whose rate is not a routine composition of density estimation and the
  deterministic modulus;
- an adaptive intervention rule that provably removes the singular strata using feasible controls without
  knowing the true drift; or
- a computational representation that exploits the solenoidal constraint and stratified degeneracy with a
  provable advantage over DyNoSeD, KDS and ordinary regularization.

Until one exists, Experiment 154 is not preregistered and no synthetic outcome may be generated.

## 5. Why this is even farther from NCS

NCS additionally requires a controlled real system with quantitative perturbation fields, stationary ensembles,
an independently checked non-gradient recovered mechanism and a frozen unseen-intervention prediction. Neither
EcoMD nor passive market regimes provide that intervention semantics. The current result is an inverse-problem
theorem scaffold, not a discovered physical law.

## 6. Resource decision

- Mac CPU use was limited to source extraction and exact symbolic reasoning.
- GPU use was `0.0` hours.
- The two V100 workers and RTX2060 were not contacted or queued.
- H20 is excluded.
- No current dataset was opened, purchased or generated.

The next admissible work is an independent human novelty/value audit of the three-regime theorem or a new topic
search. Compute remains locked unless a genuinely non-equivalent statistical or design claim survives.
