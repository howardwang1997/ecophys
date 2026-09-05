# EcoMD transient-population identifiability trigger audit

**Date:** 2026-09-05  
**Stage:** bounded D-3 re-entry-trigger audit; no candidate harvest  
**Archetype:** `theory_mechanism` / `measurement_method` boundary  
**Decision:** `partial_capability`, zero removed project blockers, no qualified trigger  
**Outcome, implementation, SSH and GPU access:** none

## Decision first

AISTATS 2026 supplies a real new theorem: outside equilibrium, exact temporal population marginals
jointly identify a time-homogeneous gradient drift and its constant scalar diffusivity. It also
confirms the exact common-scale nonidentifiability at equilibrium. This does not yet create an EcoMD
or ICLR topic.

The theorem's observation and model contracts are the decisive issue. EcoMD has endogenous
price/history feedback, generically nonconservative force after closing the context loop,
state-dependent noise, jumps and latent interacting agents. One observed market path is not a set of
independent systems sampled at the same physical times. Once the gradient restriction is removed,
nonstationarity alone no longer identifies probability current: a radially evolving density cannot
distinguish any added rotational drift. The surviving mathematical condition is a temporal
score-ratio frame, which is an immediate time-indexed counterpart of the already audited
multi-density solenoidal operator, not yet a new estimator or finite-sample theorem.

The nearest method space is occupied by APPEX for linear non-gradient additive SDEs and nn-APPEX for
nonlinear gradient SDEs. No feasible market population-snapshot asset, actuator, response truth or
independent replication is present. Candidate harvesting, implementation and compute remain closed.

## 1. Frozen question

**Market-native object.** The nonconservative drift/current of a resolved market state during a
repeatable non-equilibrium relaxation, and the resulting response to a market action.

**Rival explanations.** Under H1, observing several non-equilibrium population marginals breaks the
stationary scale and solenoidal gauges and makes the EcoMD generator identifiable. Under H2, the new
theorem owes uniqueness to a gradient-flow restriction and full synchronized population snapshots;
general market dynamics retain weighted-divergence-free ambiguities and the available data do not
instantiate its observation operator.

**Discriminating result.** H1 requires either a uniqueness theorem for EcoMD's nonconservative class
under a verifiable temporal excitation condition or a legal data asset that actually supplies the
theorem's independent population marginals. A counterexample or contract mismatch supports H2 and
prevents synthetic self-identification from being presented as a market result.

Both signs matter: a positive theorem-plus-asset could reopen a method route, while the null result
gives an exact boundary between population-dynamics inference and one-path market calibration.

## 2. What the new theorem establishes

[Guan et al., AISTATS 2026](https://proceedings.mlr.press/v300/guan26a.html) study

\[
  dX_t=-\nabla\Psi(X_t)\,dt+\sigma\,dW_t
\]

from the full family of temporal population marginals `p(x,t)`. Their main theorem says that the
gradient drift and constant scalar diffusivity are jointly identifiable from exact marginals if and
only if the process is observed outside equilibrium. At equilibrium,

\[
  (\nabla\Psi,\sigma^2)\mapsto(\alpha\nabla\Psi,\alpha\sigma^2),
  \qquad \alpha>0,
\]

leaves the stationary law unchanged. This is the continuous-time form of the energy--friction--
temperature scale gauge found in the EcoMD code audit.

The paper also proves an almost-sure three-distinct-marginal result within a countable class of smooth
candidate gradient SDEs when measurement times are drawn from separated intervals. Its practical
nn-APPEX method alternates a multi-marginal Schrödinger bridge with drift and diffusion estimation.
The paper explicitly leaves nonconservative drift, finite-sample/noisy-marginal stability and
convergence of the alternating estimator open.

## 3. Why non-equilibrium alone does not identify EcoMD current

Assume first that two time-homogeneous drifts `b` and `b_tilde` share a known diffusion and generate
the same positive temporal density `p_t`. Their difference `u=b-b_tilde` must satisfy

\[
  \nabla\!\cdot(p_tu)=0
  \quad\Longleftrightarrow\quad
  \nabla\!\cdot u+u^\top\nabla\log p_t=0
  \qquad\text{for every observed }t.
\]

After fixing `t_0` and subtracting its equation,

\[
  u^\top\nabla\log\frac{p_t}{p_{t_0}}=0.
\]

Therefore a sufficient pointwise uniqueness condition is that the temporal score-ratio gradients
span the state tangent space. This is the same density-ratio frame that appeared in the closed
multi-stationary V11/V12 route, with time replacing intervention environment. A stable result would
need a positive lower frame bound, not merely different-looking marginals.

There is an exact transient counterexample. Let every `p_t(x)=rho_t(||x||)` be radial and let
`u(x)=Omega x` for a nonzero skew-symmetric matrix `Omega`. Then

\[
  \nabla\!\cdot(p_tu)
  =p_t\operatorname{tr}(\Omega)+(\Omega x)^\top\nabla p_t=0
\]

for all `t`, even while `p_t` changes. The models have identical temporal marginals but different
rotational currents. Thus the AISTATS theorem cannot be extended by replacing “gradient” with
“general drift” and retaining nonstationarity as the only hypothesis.

If constant scalar diffusion is also unknown, writing
`q=(sigma^2-sigma_tilde^2)/2` augments the pointwise equations with
`q Delta p_t/p_t`. Uniqueness requires an augmented score/Laplacian frame of dimension at least
`d+1`; different clock times alone do not guarantee it. State-dependent diffusion introduces a
field-valued ambiguity rather than one extra scalar.

## 4. Nearest-work collision

[Guan et al. 2024](https://arxiv.org/abs/2410.22729) already prove generic identification for linear
non-gradient additive-noise SDEs from temporal marginals and introduce APPEX. The algorithm is
presented for general additive-noise drift even though its uniqueness theorem is linear. The 2026
paper supplies the nonlinear gradient case and nn-APPEX. In the stationary-intervention branch,
[Lorch et al., AISTATS 2024](https://proceedings.mlr.press/v238/lorch24a.html) already fit causal
diffusions across intervention environments, while [Zweig et al., UAI
2026](https://proceedings.mlr.press/v337/zweig26a.html) give intervention-count bounds for parameter
identification.

Consequently, “learn a Langevin/SDE from population snapshots,” “jointly learn drift and diffusion,”
and “use multiple interventions” are all occupied claims. A residual would need a finite-sample,
nonconservative temporal-excitation theorem and estimator that outperform these parents for a reason
tied to the frame singularity. Merely applying a neural Fokker--Planck loss to EcoMD is not enough.

## 5. Observation-contract failure for markets

Temporal population inference observes many independent systems from `p_t` at the same elapsed time,
usually with a common initial population law. Public market data normally supply one chronological
system. Treating rolling windows as independent replicates erases the very nonstationarity used for
identification and confounds clock time, regime and initial condition.

EcoMD's agents do not repair this mismatch. Their states are latent, coupled through prices and
pairwise forces, and heterogeneous; they are not independent draws from a common full-state marginal.
A propagation-of-chaos or exchangeable mean-field theorem plus observable agent states would be
needed before their cross-section could instantiate the population contract. Neither is available.

Scheduled openings, auctions, halts or rule changes could in principle align repeated relaxations,
but no current asset freezes a common event kernel, initial law, full state, assignment mechanism,
rights, untouched response partition and independent replication. That is a future truth-asset
precondition, not authorization to inspect outcomes.

## 6. Gate decision

| Gate | Result |
|---|---|
| Real exogenous capability | Pass: transient gradient-flow drift and scalar diffusion are identifiable |
| Same EcoMD estimand | Fail: feedback/nonconservative current, memory, multiplicative noise and jumps are excluded |
| Irreducible theorem | Fail today: temporal score-frame criterion reduces to the V11/V12 density-ratio operator |
| Novel algorithm | Fail today: APPEX and nn-APPEX directly occupy temporal-marginal inference |
| Market truth contract | Fail: no independent synchronized full-state populations or valid actuator |
| Finite-sample/stability contract | Fail: no market-dimensional rate or robust frame certificate |

**Decision:** `partial_capability`, with `removed_blockers: []` and
`candidate_harvest_authorized: false`. The new theorem sharpens the boundary and independently
confirms the equilibrium scale gauge; it changes the observation operator rather than solving the
closed stationary/current problem.

## 7. Exact re-entry boundary

Re-audit only if both sides below become concrete:

1. a theorem and estimator for nonlinear nonconservative drift under an explicit temporal
   score-frame condition, with finite-sample stability near rank loss and a result not reducible to
   APPEX/nn-APPEX or ordinary inverse-PDE regularization; and
2. a legal market asset with repeated synchronized full-state populations, or an externally assigned
   actuator with sufficient pre-state, untouched response truth and independent replication.

Until then, no topic card, experiment plan, simulator execution, outcome access, SSH connection or
GPU job is authorized. The A800 and both V100 workers remain idle for this route.
