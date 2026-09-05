# Thesis v2: randomized unit allocation and the human value of queue speed

Date: 2026-08-27

Status: **current paper-only scientific contract; no topic card, participant authorization, or
route activation. FROZEN (PARKED) by PI direction 2026-08-27 (later session) pending topic
re-selection outcome; the variance-pilot ethics draft is not submitted; reopening requires the
four freeze decisions recorded in `ecomd_variance_pilot_ethics_package_draft_2026-08-27.md` plus
unchanged C4 gates**

This document supersedes the *scientific interpretation* and proposed primary outcome in
`ecomd_truth_asset_thesis_statement_2026-08-27.md`. It does not erase that historical record or
change any machine status.

## One-sentence question

**When every unit resting at the same price has an equal chance of execution, do human traders
stop paying to arrive first—and, if so, does that behavioral response transfer to liquidity in a
full induced-value continuous double auction?**

The identified population is the two laboratory participant pools. “Real market,” universal
market-design superiority, and field transfer are not claimed.

## Exact treatment

Price priority is identical in both arms. At the execution price:

- **FIFO:** orders execute by receipt time; a partially filled order retains its original queue
  position.
- **Random unit:** for each incoming executed unit, the engine draws uniformly without replacement
  from all remaining resting units at that price. The semantic draw is recorded. An order with
  quantity `q` therefore has probability proportional to `q`, and splitting `q` into child orders
  does not change the actor's allocation probability.

All depth outcomes are measured in units, not order count. Order-count depth and child-order
activity are diagnostic outcomes only.

## Two linked experimental modules

### Module A — priority-rent race (primary causal module)

Participants each place one unit at a common price and choose how much of a fixed endowment to
spend on lower message latency. The liquidity-demanding order arrives only after every passive
unit is resting. Under FIFO, speed changes queue rank; under random-unit allocation, speed cannot
change the allocation probability. The first incentivized round occurs before any own allocation
feedback. Later rounds measure adaptation.

For `N` otherwise symmetric resting units, participant `i`'s random-arm execution probability is
`1/N`, independent of speed effort. With a strictly increasing effort cost, zero effort is the
unique best response in the isolated random arm. Under FIFO, effort changes the probability of
arriving first and can have a positive marginal return. This is a local design theorem, not a
universal prediction for an unconstrained continuous market where speed may also affect price
improvement or whether an order is present at all.

### Module B — full induced-value CDA (transfer module)

Independent cohorts trade in the same replay-complete multi-price CDA under their assigned rule.
Cash, inventory, induced values, public information, clocks, allocation draws and the initial book
are frozen in the session prestate. Time-weighted touch depth, spread, price efficiency,
cancel/replace activity, surplus and payoff concentration are secondary outcomes. Their signs are
not claimed to be universal.

## Operational model ladder

The old binary “zero intelligence versus strategic market maker” fork was not identified. The
replacement ladder classifies observable policies, not unobservable cognition:

| Level | Policy restriction | Discriminating signature |
|---|---|---|
| M0 aggregate-lumpable | Actions depend only on anonymous book state; allocation identity never feeds back | Anonymous request-boundary paths remain invariant; only maker identity changes |
| M1 identity/resource myopic | Actions may depend on current inventory, cash and induced value, but not on the announced future allocation kernel | No pre-feedback arm response; any later response is mediated by differential fills and holdings |
| M2 feedback-adaptive | Actions update from realized fills/payoffs across rounds | Little or no first-round response, followed by a prespecified treatment-by-round trend |
| M3 rule-aware forward-looking | Current action prices the announced allocation probability | A treatment effect on first-round speed investment before own fill feedback |

An aggregate liquidity effect rejects M0 but does **not** by itself establish M3. A null aggregate
effect does **not** falsify every strategic model. The pre-feedback speed choice, the post-fill
resource mediation contrast and the across-round learning trend are required to locate the result
on the ladder.

## Statistical contract

- **Sole primary endpoint:** the session mean of first-round latency investment divided by the
  available latency endowment.
- **Primary contrast:** random unit minus FIFO, with the economically relevant prediction `Δ < 0`.
- **Three decisions:** materially lower, practically equivalent, or inconclusive. A nonsignificant
  superiority test is never called equivalence.
- **Provisional smallest effect of scientific interest:** 0.10 of the latency endowment. The final
  payoff schedule must make this a meaningful welfare amount before registration.
- **Mechanism secondaries:** repeated-round treatment-by-round slope; arrival-rank/fill gradient;
  fill-conditioned inventory and value mediation.
- **Market secondaries:** unit depth, spread, efficiency, cancellations, realized surplus and
  payoff concentration in Module B, with multiplicity control and no universal sign claim.

The earlier 16-sessions-per-arm calculation is withdrawn. At `n=16` independent sessions per arm,
a two-sided 5% test has 80% power only for approximately `d=1.02`, an unusually large session-level
effect. No valid session count can be frozen until a relevant between-session variance anchor and
the latency-payoff scale exist; the current C4 and its cost-ceiling pass are therefore reopened.

## Novelty boundary

The mechanism, simulation and adjacent human-speed lanes are occupied:

- [Lim (2026)](https://doi.org/10.2139/ssrn.6574208) compares FIFO with randomized priority on
  identical simulated order flow and provides the speed-rent theory.
- [Yang et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0957417426003672)
  compare time, pro-rata and equal-sharing rules in a heterogeneous-agent artificial market.
- [Khapko and Zoican (2021)](https://doi.org/10.1016/j.finmar.2020.100601) measure human investment
  in low latency under speed bumps.
- Field and theory work already establish strategic time-priority submission, pro-rata adaptation,
  queue uncertainty and NYSE parity.

The defensible unoccupied intersection is narrower: a preregistered human comparison of FIFO and
uniform random-unit allocation, with a pre-feedback costly-speed endpoint and a replay-complete CDA
transfer module. The bounded audit found no exact collision, but the manuscript must say “to our
bounded search” rather than make an unconditional first-ever claim.

## Positive and null value

- A material first-round reduction identifies anticipatory pricing of queue rents; transfer to the
  CDA shows whether that clean mechanism changes market quality.
- Practical equivalence rejects an order-one human extrapolation of the random-priority arms-race
  theorem in this environment, even though the mechanical maker redistribution still works.
- An inconclusive interval is not publishable evidence for either explanation; it triggers the
  frozen stop rule rather than a narrative rescue.

The reusable event tape and simulator-prediction benchmark remain secondary assets. They become a
paper contribution only if their models and prediction freeze are completed prospectively; their
mere presence does not upgrade the experimental result.
