# EcoMD stochastic hard-projection measure audit

**Date:** 2026-09-05  
**Stage:** D-3 re-entry trigger screen; exact reduction plus minimal primary-work collision  
**Archetype:** `simulator_method`  
**Decision:** `not_trigger`; route `failed_closed`  
**Outcome, implementation, SSH and GPU access:** none

## Decision first

The proposed paper claim does not survive. A stochastic extension of the existing hard-constraint
study cannot claim that it newly discovers projection-induced invariant-measure bias or supplies the
first measure-correct correction. Constrained Langevin dynamics, the affine nonreversible case and a
current ML co-area correction already cover the central mathematical and algorithmic objects. The
obvious EcoMD-related cash and inventory projection is even less informative: it is an affine,
constant-Jacobian orthogonal projection, so the co-area/Fixman factor is constant and the curvature
drift vanishes.

This is a useful theorem-level negative control for future stochastic-surrogate work, not a new ICLR
topic. No machine card, experiment plan or compute authorization is created.

## Frozen question contract

### Market-native object

The object is the transition and stationary law of a stochastic market-state surrogate after every
clearing update is projected to preserve total cash-plus-fees and total inventory.

### Rival explanations

- **H1 — plug-and-play projection.** Orthogonal projection only deletes infeasible normal motion;
  the intended tangent path law and conditional invariant measure are otherwise unchanged.
- **H2 — geometric measure change.** For a nonlinear constraint, projected noise is
  state-dependent. Its Itô/Stratonovich conversion, curvature drift and the reference measure on the
  constraint manifold alter the generator and invariant law unless an explicit correction is used.

### Cheapest discriminating result

Write the implemented constraint map as `c(x)=0`, compute its Jacobian Gram determinant and tangent
projector, and compare the normalized co-area conditional measure with the manifold-volume target.
A nonconstant determinant or projector would leave a nontrivial correction; a constant determinant
and projector would make the proposed geometric effect identically zero in the native case.

A positive result would identify a specific path-law bias that must be corrected. A null result is
also valuable because it certifies that affine conservation is not an example of this geometric
bias and prevents an unnecessary stochastic training campaign.

## Repository reduction

The core `ecomd/` package contains no generic per-step hard projection of stochastic state onto cash
or inventory constraints. The directly relevant implementation is the auxiliary market-surrogate
experiment in `scripts/run_constraint_iclr_market.py`, not the molecular-dynamics core.

For `n` agents, let `y` collect the predicted state increment. The implemented constraints are

\[
 a_1^\top y=\sum_{i=1}^n \Delta C_i+\Delta F=0,
 \qquad
 a_2^\top y=\sum_{i=1}^n \Delta I_i=0.
\]

The code subtracts the mean from the `n+1` cash-and-fee coordinates and separately from the `n`
inventory coordinates. This is exactly

\[
 P y,\qquad P=I-A^\top(AA^\top)^{-1}A,
 \quad A=\begin{bmatrix}a_1^\top\\a_2^\top\end{bmatrix},
\]

with constant `A` and constant orthogonal projector `P`.

## Exact killer lemma

Let `c: R^d -> R^m` have full-row-rank Jacobian `J(x)` on
`M={x:c(x)=0}`. Under the small-residual-noise conditioning convention, the co-area formula gives
the limiting density on `M`, relative to Hausdorff volume, as

\[
  \mu_{\mathrm{tube}}(dx) \propto
  \frac{\pi(x)}{\sqrt{\det(J(x)J(x)^\top)}}\,d\mathcal H^{d-m}(x).
\]

A sampler targeting `pi(x) dH` therefore differs whenever the Gram determinant varies. Likewise,
the tangent-noise projector

\[
  P(x)=I-J(x)^\top[J(x)J(x)^\top]^{-1}J(x)
\]

is multiplicative for nonlinear constraints, so the desired stochastic convention and invariant
measure require the corresponding geometric drift.

For an affine constraint `c(x)=Ax-b`, however, `J=A`, `det(AA^T)` and `P` are all constant. The
co-area factor cancels in normalization and every derivative-of-projector curvature term is zero.
Thus the implemented cash/inventory projection cannot exhibit the proposed Fixman effect.

This lemma does **not** say that arbitrary projected drift or state-dependent covariance is always
correct. It says that any remaining error is a constrained-SDE design question rather than the
claimed new geometric correction, and that question is directly covered by the parents below.

## Minimal primary-work collision

The screen stopped after three exact anchors, as required by the bounded funnel.

| Primary work | Occupied object | Consequence |
|---|---|---|
| Lelièvre, Rousset & Stoltz, *Mathematics of Computation* 2012, [DOI](https://doi.org/10.1090/S0025-5718-2012-02594-4) | Constrained Langevin processes, invariant constrained canonical measures, splitting schemes and exact-bias correction | “Hard stochastic constraints need measure-correct dynamics/numerics” is mature constrained-MD theory. |
| Hartmann, Neureither & Sharma, *SIAM Journal on Applied Dynamical Systems* 2026, [DOI](https://doi.org/10.1137/25M175843X) | Affine constraints in nonreversible SDEs with degenerate noise; pathwise strong-confinement limit, explicit projection and conditions matching the conditional invariant measure | This is an exact collision with the native affine and potentially nonequilibrium stochastic-surrogate setting. |
| Xu et al., 2026, [arXiv:2606.04804](https://arxiv.org/abs/2606.04804) | Hard physics projection/guidance samples the wrong co-area posterior when the Jacobian factor varies; gives the factor, controlled tests and a corrected sampler | The most ICLR-like statement and correction are already claimed directly in scientific generative modeling. |

The literature also makes an important semantic point: a distribution “conditioned on a
measure-zero constraint” is not defined by the constraint set alone. One must freeze whether the
target is a small-noise tube limit, surface-volume restriction, or another physical reference
measure. Calling one of them universally correct would overclaim.

## Escape attempts and why they fail

1. **Use wealth rather than cash.** Mark-to-market wealth changes with price, so it is not an exact
   conservation law of the market transition. Choosing it only to obtain a nonlinear Jacobian
   changes the scientific object.
2. **Use positivity or inventory bounds.** These are inequality constraints. Their continuous limit
   is a reflected/Skorokhod process with boundary local time, already represented by the closed
   `constraint_boundary_rejection_local_time` route.
3. **Use a CFMM invariant such as `xy=k`.** This supplies genuine nonlinear geometry, but CFMM
   invariant curvature and response are already direct theory and the route
   `cfmm_invariant_curvature_response` is closed.
4. **Combine the existing training/inference projection cube with Fixman correction.** That is a
   composition of an already completed deterministic attribution paper with occupied constrained
   sampling theory. It does not create an irreducible stochastic method, and in the implemented
   affine case the advertised correction is zero.

## Gate result

| Gate | Result | Reason |
|---|---|---|
| Market-native nontriviality | fail | Native cash/inventory conservation is affine; the geometric correction vanishes. |
| Residual novelty | fail | Constrained Langevin, affine nonreversible diffusion and ML co-area correction occupy the centerpiece. |
| Scientific identifiability | fail | The target reference measure must be declared; the constraint set alone does not identify it. |
| Two-system truth contract | fail | No new estimator/theorem remains to validate, and no two-system contract was frozen. |
| Positive/null value | pass as QA only | The affine null is a reusable guardrail against a false stochastic-extension claim. |
| Cost of decisive update | complete | Source algebra plus three primary works decide the current formulation without simulation. |

Post-audit diagnostic ICLR survival is **0.5--2%**. This is not a prospective forecast or a reason by
itself for closure; the exact reduction and direct collisions are the reasons.

## Re-entry boundary

Re-entry requires all of the following, not a relabeling of hard projection:

1. a genuinely market-native nonlinear equality constraint whose curvature is not analyst-created;
2. an explicit physical/reference-measure semantics and a nonconstant correction in that native
   system;
3. a theorem or algorithm not contained in constrained Langevin, strong-confinement, manifold
   diffusion or co-area/Fixman methods, with a matching failure boundary;
4. analytic or gold-standard truth on two independent non-EcoMD stochastic systems before a market
   application; and
5. a new current machine decision before implementation, outcome access, SSH or GPU use.

Until then, the A800 and both V100 workers remain idle for this route.
