# EcoMD switching-friction long-memory trigger audit

**Date:** 2026-09-05  
**Archetype:** `theory_mechanism` with an `empirical_intervention` rescue examined  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU status:** not authorized

## 1. Capability claim under audit

[Rodriguez Dominguez (2026)](https://arxiv.org/abs/2609.02525), posted after the
August long-memory route closures, derives a new economic route from heterogeneous portfolio-
representation switching frictions to persistent signed flow. If this result supplied a public
observable that distinguishes representation residence from parent-order splitting, or made the
previously frozen dYdX funding-carry intervention mechanism-specific, it could be a legitimate
re-entry trigger.

The native response is execution-weighted signed order-flow covariance. The rival explanations are:

- **H1 -- representation residence:** an institution keeps a factor set, model family, or other
  portfolio representation until an opportunity coordinate first reaches a switching threshold;
  the resulting residence spell carries a persistent component of desired demand;
- **H0 -- parent-order or public-event persistence:** long episodes instead arise from gradual
  execution of parent orders, history-dependent public-event dynamics, or common regimes, without
  an observed representation switch.

A discriminating result must concern the same accounts, actions, clock, conditioning set, and
execution weights. A positive result would identify an upstream source of memory beyond individual
metaorders. A null result would reject use of a representation-residence kernel in an execution
model. Aggregate exponent agreement alone has neither implication.

## 2. What the new paper establishes

For portfolio \(a\), the paper uses reflected Brownian opportunity accumulation with threshold
\(\kappa_a\), volatility \(\sigma_a\), residence scale \(R_a=\kappa_a/\sigma_a\), and spell duration

\[
  \tau_a \overset{d}{=} R_a^2\tau_0.
\]

If the execution-weighted tail of \(R\) is regularly varying with index \(\theta\), the stationary
renewal mixture gives order-flow covariance proportional to
\(L(\sqrt{t})t^{-\theta/2}\). Under aligned execution weights, the spell-duration tail and flow-
memory exponent obey

\[
  \beta=\alpha_F=\theta/2.
\]

The paper also proves that a truncated-Pareto residence mixture loses its apparent power-law window
near the square of the largest residence scale, with the iid finite-population proxy of order
\(N^{2/\theta}\). Independent Poisson execution preserves the exponent after weighting by
\(q_a^2\lambda_a^2v_a\).

These are substantive results. They are also the contribution of the new paper, not an unoccupied
EcoMD contribution. Its experiments are explicitly structural simulations with 500 portfolios and
4,096 periods, not market evidence. The paper itself says a direct test needs dated representation
states, account identifiers, signed executions, parent-order links, common-shock controls, and the
same execution weights for durations and covariance.

## 3. Exact observational-equivalence witness

The joint exponent restriction does not distinguish H1 and H0 without an independently recorded
representation state. Consider the admissible submodel in which each representation spell has
duration \(\tau_{a,n}\), centered binary demand component \(B_{a,n}\in\{-1,+1\}\), no transitory
component, and executions from the declared Poisson clock.

Construct a parent-order model pathwise as follows: call every spell a parent order, give it the
same duration \(\tau_{a,n}\), direction \(B_{a,n}\), execution intensity \(\lambda_a\), and child
quantity \(q_a\), and use the same Poisson tape. The account-level marked execution process is then
identical on every realization, not merely in covariance. Its duration exponent, flow exponent,
execution weights, and finite-sample cutoff are also identical.

This witness lies inside both mechanism classes. Relabeling the latent episode as a representation
spell or a parent order cannot be resolved by anonymous flow, and account identifiers alone do not
help if neither episode boundary has external provenance. A learned segmentation merely chooses a
latent model. The new paper recognizes this point by requiring both independently dated
representation states and reconstructed parent orders.

There is a second representation problem in the finite-market statement. Splitting one beneficial
owner into several wallet or subaccount clones changes the observed account count while leaving the
largest residence scale and aggregate executed path unchanged. The iid \(N^{2/\theta}\) proxy is
valid for its declared portfolio population; public wallet count is not that population without
ownership and dependence truth.

## 4. Why fixed funding carry is not the missing exclusion

The repository's earlier dYdX route used a governance change in `default_funding_ppm` at an
unchanged hourly clock. Its signed pre-boundary exit/post-boundary re-entry prediction was a clean
test of response to carrying cost, but it was not a representation-state intervention.

Let \(z\) be the fixed carry. Under H1, choose a carry-dependent representation-residence law
\(F_{\tau\mid z}\). Under H0, let the same carry alter desired position duration, metaorder size, or
execution horizon and choose the identical \(F_{\tau\mid z}\). Couple directions and execution
tapes as in the witness above. Then the complete conditional law of observed signed flow is the
same for every value of \(z\). The boundary dipole is compatible with ordinary position exit and
re-entry and does not require replacing a factor set or model family.

Thus funding carry violates the needed exclusion: it can change both portfolio-state persistence
and execution decisions. The new paper lists funding as one possible component of its reduced-form
switching threshold but supplies no theorem that carry affects representation replacement while
leaving parent-order behavior fixed.

The field asset also already failed its outcome-blind activity gate. Only HYPE, one of 21
development markets, met the frozen activity rule; the stop line was 15. Treating many accounts or
hourly boundaries as independent assignments would be pseudoreplication because the treatment is a
single market-level governance transition. See the
[T0 result](dydx_funding_carry_t0_result_2026-08-20.md) and
[D1A result](dydx_funding_carry_d1a_activity_result_2026-08-20.md).

## 5. Public-data and EcoMD contract

| Required object | New paper's direct-test contract | Current public/EcoMD status |
|---|---|---|
| Persistent decision unit | same portfolio or account | wallets need not equal beneficial owners; EcoMD agents are programmed units |
| Representation spell | dated model, factor set, or production-state change | absent from dYdX public market data |
| Parent-order control | reconstructed parent links and child schedule | absent generally; a subset of native TWAP identifiers does not cover all flow |
| Signed execution | account-linked signed executions | partially available, but insufficient without the two latent labels |
| Aligned weight | \(q_a^2\lambda_a^2v_a\) applied to both samples | \(v_a\), representation-conditioned demand variance, is unavailable without representation state |
| Carry assignment | treatment excluded from rival mechanism | failed: carry also changes position and execution economics |
| Independent support | repeated active treated units and independent replication | one of 21 dYdX development markets passed; no same-estimand second system |

Programming switching thresholds into EcoMD and recovering the induced exponent would validate the
implementation of the programmed renewal model. It would not determine whether representation
residence, parent-order splitting, or a public-event mechanism generated a real tape. Fitting EcoMD
to aggregate covariance would inherit the same observational quotient.

## 6. ICLR novelty boundary

The obvious routes all fail an irreducibility test:

1. **Implement the first-passage mechanism in EcoMD.** This reproduces the new paper's structural
   simulation and its theorem.
2. **Fit the joint duration--flow exponent on public trades.** Without external representation
   spells and parent links, this is compatibility evidence that the paper explicitly rejects as
   identification.
3. **Use funding as an intervention on the exponent.** The treatment changes both rival mechanisms,
   and the only frozen field design lacks treated-unit support.
4. **Infer latent spells with a neural semi-Markov model.** Flexible latent segmentation cannot
   resolve the pathwise equivalence; predictive fit is not provenance.
5. **Predict the cutoff from account count.** Wallet splitting and cross-account dependence make
   the count non-native unless ownership and portfolio units are independently established.

The new source is therefore a useful theorem and a sharper truth contract, but it directly occupies
the theoretical contribution and confirms rather than removes the earlier identification blocker.
It does not authorize an EcoMD paper, benchmark, or experiment.

## 7. Gate decision

| Gate | Result |
|---|---|
| Genuine post-closure primary source | Pass: arXiv v1 was submitted 2026-09-02 |
| New quantitative restriction | Pass: aligned half-index and finite-cutoff restrictions |
| Market evidence or released labeled truth asset | Fail: structural simulations only |
| Distinction from splitting on current observables | Fail: exact pathwise relabeling witness |
| Funding-carry exclusion | Fail: carry affects representation and execution horizons |
| dYdX support | Fail: one of 21 active development markets versus a frozen stop line of 15 |
| Representation- and split-invariant population state | Fail |
| Irreducible ICLR method or theorem | Fail: the new paper owns the positive theorem; latent fitting cannot repair nonidentification |
| External same-estimand EcoMD truth | Fail |
| Recorded blocker removed | Fail |

**Decision:** `not_trigger`, with `removed_blockers: []` and
`candidate_harvest_authorized: false`. The pathwise equivalence witness, aligned-weight checklist,
and funding-exclusion test are reusable. Re-entry requires either (i) a lawful panel with externally
dated representation versions, participant identity, complete signed executions, parent-order
links, aligned weights, a sealed period, and an independently governed same-estimand replication;
or (ii) an assigned intervention proven to change representation-replacement cost while excluding
parent-order duration and execution-clock responses. It must also leave a contribution beyond the
2026 half-index and cutoff theorems. Until then, outcome access, implementation, simulation, SSH,
and all three GPU workers remain closed.
