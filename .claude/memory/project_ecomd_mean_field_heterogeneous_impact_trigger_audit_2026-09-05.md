# EcoMD heterogeneous-horizon mean-field impact trigger audit (2026-09-05)

## Durable decision

- Leclere and Rosenbaum, arXiv:2609.03115v1, is a genuine post-closure theorem source but is
  `not_trigger`; no topic card, implementation, outcome access, SSH, or GPU work is authorized.
- The balance condition is `G(0)(1-alpha)=1`. The advertised Hawkes relation
  `alpha=||h||_1` follows only after identifying the source's dimensionless position-impact kernel
  with the Hawkes propagator. `alpha` is not independently observed, and the source warns that
  forecast-unit positions and unit-trade flow do not have directly comparable absolute scales.
- Exact nonidentification witness: set `alpha=0`, `G(t)=1`, and `K(t)=exp(-r t)`. Then cancellation
  holds, `S_nu K=m_nu(r)K`, `phi=(m_nu(r)-1)K`, and the signal-driven price kernel is
  `m_nu(r)K`. The full observed common-signal/aggregate-position/price law depends on the horizon
  distribution only through one Laplace moment. Infinitely many distributions, including a
  continuum of Gamma `(xi,beta)` pairs, are observationally equivalent.
- Price regularity is many-to-one: it stays at `H` without cancellation and usually saturates at
  `1/2` for every `xi>1/2-H` under cancellation. It cannot identify the horizon law, behavioral
  `alpha`, and cancellation jointly; the martingale residual has the same headline regularity.
- Finite-agent sampling near `alpha -> 1` can be amplified by the equilibrium resolvent and the
  `1/(1-alpha)` impact scale, but this is ordinary empirical-operator fluctuation, condition-number
  amplification, and mean-field CLT unless a new uniform correction/lower bound is proved.
- EcoMD's particle count remains an analyst-selected resolution and fails weighted agent-split
  invariance. The source does not reopen `fluctuation_aware_population_size_transfer`.
- Re-entry requires independently observed forecast/position/horizon/impact/provenance truth or an
  injective stable inverse theorem plus a singular-limit finite-population correction beyond CLT
  and conditioning parents, two same-estimand truth systems, and a market-native split-invariant
  population unit.

## Canonical artifacts

- Formal audit:
  `papers/proposal/ecomd_mean_field_heterogeneous_impact_trigger_audit_2026-09-05.md`
- Trigger ledger entry:
  `mean_field_heterogeneous_impact_cancellation_screen_20260905`
- Primary source: https://arxiv.org/abs/2609.03115

