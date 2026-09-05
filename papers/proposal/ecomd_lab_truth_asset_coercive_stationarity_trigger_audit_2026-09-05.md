# EcoMD laboratory truth-asset and coercive-stationarity trigger audit

**Date:** 2026-09-05 NZST  
**Stage:** three bounded D-3 trigger screens; source/rights and exact-reduction work only  
**Archetypes:** `empirical_intervention`, `simulator_method`, `theory_mechanism`  
**Decision:** three `not_trigger`; zero removed blockers; no machine card or compute authorization

## Decision first

None of the three formulations survives as a new ICLR topic.

1. Friedman, Gu and Zheng provide a scientifically attractive randomized human bond-market
   experiment, but INFORMS licenses its replication files only for reproducing the same paper with
   the same data and models. Any other use requires explicit permission from every author or data
   originator. EcoMD training, benchmarking and intervention validation are therefore prohibited
   under the published terms. The files and row-level outcomes were not downloaded or opened.
2. EcoMD M0 has no architectural coercivity guarantee: its active pair and external potentials are
   unconstrained SiLU MLPs, and the optional positive power-law confiner is disabled. A learned
   energy can therefore be nonintegrable even when a finite rollout looks stable. This is a real QA
   and claim-scope issue, but stable Neural SDE work and UIDD already occupy dissipativity,
   integrable neural energies and the exact ``neural residual + fixed quadratic confinement``
   repair.
3. Exact common-shift invariance creates a translation zero mode: the full-space Gibbs normalizer
   diverges and the noisy population mean is Brownian. Stationarity is possible only after fixing a
   gauge, quotienting the common coordinate, or breaking the symmetry with a confiner. This is
   established translation-invariant particle theory, while ICLR 2026 already develops general
   quotient-space diffusion. It also does not describe current EcoMD M0: v2 gauge enforcement is
   off by default and the top-level absolute-state external potential breaks that symmetry anyway.

The A800 and both V100 workers remain idle. No implementation, simulator run, stored outcome,
replication-file acceptance, author outreach, SSH session or data download occurred.

## 1. Randomized laboratory bond market

### Question contract

**Market-native object.** Human order submission, transaction prices, liquidity and volatility in a
bond market under assigned default rate, private-information cost schedule and market format.

**Rivals.** Under H1, a structurally faithful market simulator predicts treatment response because
it captures information acquisition and aggregation. Under H0, a simulator can match passive price
statistics while producing the wrong response to those assigned market conditions.

**Discriminating result.** Freeze some randomized sessions or treatment cells before fitting and
rank at least two independent simulator lineages on the same treatment-response distribution. A
positive result would provide unusually strong simulator-validity evidence; a null would expose the
limits of passive stylized-fact calibration.

### Rights-first killer

The official article says the laboratory experiment exogenously varies the bond default rate,
private-information cost schedule and market format. The official supplement links replication
files. The linked INFORMS agreement, however, states that downloads may be used only to verify the
paper's main results with the same data and models, and that any other use is prohibited absent
explicit permission from all authors or third-party data originators.

That restriction fails before schema inspection:

- EcoMD training, model comparison, altered estimands and new publication use are not same-model
  replication;
- clicking agreement, downloading the archive or treating availability as reuse permission would
  not be lawful;
- requesting permission would be external outreach and is not authorized by the current machine
  decision; and
- the paper reports its treatment results publicly, so even a later permission grant would not turn
  the same source into an untouched confirmation partition. A separate independent experiment
  would still be required.

The source remains useful as a design template for a future licensed prospective laboratory asset,
not as an executable truth asset now. This is the same blocker family already recorded for LEEPS,
Halim and other public-laboratory candidates, so no new discovery cycle is opened.

**Decision:** `not_trigger`.

## 2. Learned-potential coercivity

### Question contract

**Object.** Existence of a normalizable invariant law and stable long-horizon rollout for a learned
interacting Langevin simulator that is fitted on finite trajectory windows.

**Rivals.** H1 says finite-window loss plus numerical stability is enough to learn a physically
meaningful stationary simulator. H0 says the unconstrained neural energy can be nonconfining or
unbounded below, so finite-window success does not imply any invariant probability.

**Discriminating result.** Determine whether every admitted parameter value satisfies a Lyapunov or
integrability condition such as

\[
  \int_{\mathbb R^{Nd}}\exp[-V_\theta(s)/T],ds < \infty.
\]

A positive architectural theorem would certify the claimed stationary object. A counterexample is
valuable because it prevents finite-rollout metrics from being reported as equilibrium evidence.

### Exact repository witness

M0 uses `StochasticPairwisePotential` and `ExternalPotential`. Both end in an unconstrained linear
readout after SiLU layers, and M0 sets `power_law_external: false`. The admitted class therefore
contains, for example, an external potential with a negative linear tail along one state ray. Along
that ray, `V_theta(s) -> -infinity` and the Gibbs integral diverges. Pair-input LayerNorm does not
repair the independent external MLP and does not prove a closed-loop Lyapunov condition.

`PowerLawExternalPotential` can supply a positive `|s|^alpha` tail when its exponent and weight make
it dominate every learned negative tail, but it is optional, permits exponents below or equal to
one, and is disabled in M0. More importantly, this obvious repair is already occupied. UIDD uses

\[
 V(Z)=\frac{\beta_1}{2}\sum_i(U_i(Z)+\beta_2\gamma_i^\top Z)^2
      +\beta_3\lVert Z\rVert^2,\qquad \beta_3>0,
\]

explicitly to make `exp(-V)` integrable, and proves a universal identifiable representation for
nondegenerate SDEs with a unique invariant distribution. Stable Neural SDEs already treat
dissipativity, existence, stochastic stability and unstable Euler discretization in an ICLR paper.

Thus ``add a confiner/Lyapunov penalty to EcoMD`` is a necessary model repair, not a residual ML
method. A new paper would need a theorem false for these parents, such as a population-uniform
guarantee under a genuinely different stochastic interaction semantics, plus two non-EcoMD truth
systems. No such theorem was found or derived here.

**Decision:** `not_trigger`.

## 3. Gauge symmetry versus stationarity

### Exact zero-mode lemma

Let `e` add the same scalar to one coordinate of every one of `N` agents, and suppose

\[
  V(s+c e)=V(s)\quad\text{for every }c\in\mathbb R.
\]

Write `m` for that population-mean coordinate and `r` for centered relative coordinates. The
Jacobian of `(s -> (m,r))` is constant and the integrand is independent of `m`, so, whenever the
relative integral is nonzero,

\[
 \int e^{-V(s)/T}ds
 = C\left(\int_{\mathbb R}dm\right)
     \left(\int e^{-\widetilde V(r)/T}dr\right)=\infty.
\]

For isotropic overdamped Langevin dynamics, translation invariance also gives zero drift for `m`,
while averaging the independent noises gives

\[
  dm_t=\sqrt{2T/(\gamma N)}\,dB_t.
\]

Hence there is no invariant probability on the full Euclidean state. Relative coordinates may have
an invariant law on the centered space; the common coordinate must be modeled separately, fixed or
confined.

### Why this is not the new topic

Translation-invariant mean-field systems are already studied through the process seen from its
centre of mass and Gibbs laws on a quotient. ICLR 2026's Quotient-Space Diffusion Models gives a
general group-quotient SDE, the horizontal lift and the required orbit-volume correction, with
molecular experiments. Projected-noise Langevin and constrained-measure work are also already
recorded in this repository.

The reduction moreover does not expose a live EcoMD architectural contradiction:

- `EcoMDv2Potential` mean-centers the Kyle input and optionally makes the pair kernel depend only
  on differences;
- the enclosing `ConservativePotential` always adds `ExternalPotential(s, context)`, which depends
  on absolute state and generally breaks the common-shift symmetry;
- `v2_gauge_enforce` is false by default after the old gauge ablation reduced fidelity; and
- M0 uses `pairwise_kind: stochastic_mlp`, not the v2 gauge architecture.

Separating a nonstationary price-level coordinate from stationary relative state is scientifically
sensible, but it is a standard state-definition choice. EcoMD does not add an unoccupied quotient
sampler, identifiability theorem or market-native response.

**Decision:** `not_trigger`.

## 4. Gate summary

| Formulation | Scientific value | Fatal gate | Decision |
|---|---|---|---|
| Randomized bond laboratory truth | Strong same-action design in principle | Explicit same-paper-only file rights; published outcomes; no independent confirmation | `not_trigger` |
| Coercive learned EcoMD potential | Real finite-window versus invariant-law distinction | Exact UIDD architecture and stable-Neural-SDE parents | `not_trigger` |
| Gauge-compatible stationarity | Correct zero-mode theorem and useful state hygiene | Classical centre-of-mass quotient plus ICLR 2026 quotient diffusion; not current M0 | `not_trigger` |

Post-audit diagnostic ICLR survival is below 2% for each current formulation. This is not a
prospective forecast or a probability-based closure; the license text, exact counterexamples and
direct primary collisions decide the result.

## 5. Re-entry boundary

Re-audit only after one of these materially new objects exists:

1. a license or author/data-originator permission that explicitly allows new-model analysis and
   publication of derived outputs for a complete assigned laboratory event tape, together with an
   independently governed untouched same-action confirmation experiment;
2. a population-uniform coercivity/ergodicity or discretization theorem for stochastic learned
   interactions that is false for fixed-confiner UIDD, stable Neural SDE and standard interacting-
   diffusion parents, with two gold systems; or
3. a market-native noncompact symmetry for which a new quotient learning/sampling theorem is not a
   specialization of centre-of-mass reduction, constrained/projected Langevin or general
   quotient-space diffusion.

Until then, do not accept the INFORMS terms, download the replication archive, add an EcoMD
confinement term as a paper method, create a quotient sampler, or schedule any of the three workers.
