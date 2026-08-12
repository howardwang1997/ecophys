# Formal cards v2 — target tasks and relaxation attribution

**Audit date:** 2026-08-12

**Binding decisions:** NMI `NMI_NO_SURVIVOR`; NCS `NCS_C0_FAIL_IDENTIFICATION`

**Novelty admission:** none

These cards preserve the strongest exact statements found in v2. They are not presented as new theorems. Each is
kept because it prevents a later iteration from relabelling a standard partition identity or a model-class
rejection as an irreducible mechanism.

## Card NMI-v2-A — prediction-task equivalence lattice

Let `Theta` be a model family, `H` the observed history and `T` a prediction task with target `Y_T`. Define

\[
\theta\sim_T\theta'
\quad\Longleftrightarrow\quad
p_\theta(Y_T\mid H)=p_{\theta'}(Y_T\mid H)
\quad P_H\text{-a.s.}
\]

For a family of tasks `F`, equality of every optimal predictor gives

\[
\theta\sim_{\mathcal F}\theta'
\quad\Longleftrightarrow\quad
\bigcap_{T\in\mathcal F}\{\theta\sim_T\theta'\},
\qquad
\sim_{\mathcal F_1\cup\mathcal F_2}
=\sim_{\mathcal F_1}\cap\sim_{\mathcal F_2}.
\]

Thus adding targets refines a partition of parameter space; identifiability occurs only when the remaining cell is
the declared symmetry orbit. Complementary tasks can identify a parameter even when neither task does alone, but
that statement is partition refinement or stacked information, not a new algebra.

### Decisive prior-art attack

[Liu et al., NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/85dd09d356ca561169b2c03e43cf305e-Abstract-Conference.html)
define identifiability from one or a collection of prediction tasks as injectivity from HMM parameters to optimal
predictors up to state permutation. Their Theorems 2 and 4 give nonidentification for a pairwise task and for all
pairwise tasks on three adjacent observations; Theorem 5 proves identification when the target is the tensor
product of two observations conditional on the third under their assumptions. This directly instantiates target
incompleteness and complementary-target repair.

[Shalizi and Crutchfield (2001)](https://csc.ucdavis.edu/~cmg/compmech/pubs/cmppss.htm) already define histories
as equivalent when they induce the same future law and prove that causal states are the unique minimal predictive
representation. For intervention-transfer tasks, [Blackwell (1953)](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-24/issue-2/Equivalent-Comparisons-of-Experiments/10.1214/aoms/1177729032.full)
already orders experiments by universal decision performance or garbling.

### Decision

This card simultaneously retires v2 neighborhoods T1, T3 and T4 as `RETIRED_PRIOR_ART`. A new paper cannot claim
that choosing more informative targets, intersecting task equivalence classes or ordering targets by universal
downstream usefulness is new. Reopening needs a quantitatively different obstruction or guarantee, not another
multi-head loss.

## Card NMI-v2-B — horizon does not monotonically recover dynamics

For a discrete HMM, a pairwise `h`-step conditional predictor has a matrix-product form such as

\[
\mathbb E[X_{t+h}\mid X_t]=O T^h\phi(X_t).
\]

Longer prediction is not automatically more identifying because different stochastic transition matrices can
share a power:

\[
T\ne\widetilde T,qquad T^h=\widetilde T^h.
\]

Liu et al.'s Claim 1 constructs exactly this nonidentification for every declared power in their setting. Their
positive result comes from changing the target to expose a uniquely decomposable tensor, not merely increasing a
pairwise horizon. Any horizon threshold therefore depends on the model class, observation map and algebra of the
target; it is not a general monotone law.

### Decision

V2 T2 is `RETIRED_PRIOR_ART`. A future horizon theorem would need a new setting and a conclusion not reducible to
an observability index, delay embedding, matrix-root ambiguity or tensor/moment identifiability. No such survivor
was found.

## NCS-v2 identification proposition — what an envelope exceedance proves

Let a prospectively declared class `B` provide valid upper bounds `B_L` for a bounded post-intervention response.
If a simultaneous confidence statement establishes

\[
\inf_{L\in\mathcal L_{late}}
\operatorname{LCB}^{sim}_{1-\alpha}
\{|R_{obs}(L)|-B_L\}>0,
\]

then, subject to the causal comparison being valid, the data reject `B`. Nothing in this inequality labels the
omitted mechanism.

### Exact non-adaptive construction

For any bounded finite sequence `r_0,...,r_L`, define states `0,...,L`, initial state zero, a fixed
time-homogeneous transition

\[
P(i,i+1)=1\quad(i<L),\qquad P(L,L)=1,
\]

and observable `f(i)=r_i`. Then

\[
\delta_0 P^\ell f=r_\ell,\qquad 0\le\ell\le L.
\]

The process has no learned parameter, adaptive update or time-varying kernel. It is deliberately outside every
strict one-step Dobrushin class because its coefficient is one. Likewise, the fixed omitted state
`S_{t+1}=rho S_t` exceeds a declared faster envelope `d^L` whenever `rho>d`. Experiment 145 verified both frozen
fixtures exactly.

### Interpretation and occupied neighborhoods

The construction is elementary state augmentation, not new mathematics. It proves the attribution boundary:
without a justified state-completeness or structural restriction, a finite response path cannot distinguish
adaptation from fixed hidden state. Standard Markov perturbation theory already relates kernel error and mixing;
modern event studies estimate dynamic treatment paths under no-anticipation and parallel-trend assumptions; model
discrepancy work warns that simulator residuals confound calibration and omitted structure; and causal-digital-twin
impossibility results show that finite validation designs cannot identify arbitrary target counterfactuals without
structural assumptions.

### Decision

NCS C0 is `NCS_C0_FAIL_IDENTIFICATION`. The envelope is a useful model-checking diagnostic, but “slower than the
frozen simulator” is not an identified adaptive mechanism and no untouched replication case survived metadata
screening. This result does not authorize market data, worker jobs or a paper claim.
