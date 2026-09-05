# EcoMD counterfactual-coupling re-entry audit (2026-09-04)

## Canonical decision

No qualified re-entry trigger was found. The coupling-invariant differentiable-market-
counterfactual subroute is `failed_closed`; candidate harvesting, Cycle 17, implementation,
outcome access, EcoMD changes, SSH and all three GPU workers remain closed for it. The formal result
is `papers/proposal/ecomd_counterfactual_coupling_reentry_audit_2026-09-04.md`.

## Durable findings

- Deterministic Event-Graph Substrates (arXiv:2605.15967v1, CC BY 4.0) provide typed append-only
  state, deterministic replay and exact log forks under closed-event assumptions. In physical
  domains, post-intervention deltas are supplied by an external deterministic simulator. The work
  therefore has no stochastic hard-event propensity, shared-noise gradient target or market-native
  action mapping. A public paper repository was not located at the audit cutoff despite the paper's
  reproducibility wording; this is an availability finding, not proof of absence.
- Fixed-noise sample gradients are not determined by all intervention-indexed marginal laws. For
  `U~Unif[0,1)`, `X_a=a+U` and `Xtilde_a=a+((U-ca) mod 1)` have the same law for every `a` and the
  same correct population-mean derivative `1`, but their almost-everywhere fixed-noise derivatives
  are `1` and `1-c`. The moving wrap boundary supplies the omitted derivative term. This witness
  separates population response, individual counterfactual and naive hard-boundary pathwise
  derivative.
- The witness is an interpretation/conformance gate, not ICLR novelty. Bongers et al. already
  separate interventional from counterfactual equivalence; Nasr-Esfahany and Kiciman prove learned-
  SCM counterfactual non-identification; Jankowiak and Obermeyer cast pathwise derivatives as
  transport-equation velocity fields; NeurIPS 2025 dynamic OT freezes conditions selecting a unique
  counterfactual map.
- WorldKernel (arXiv:2606.10934v1, CC BY 4.0) and its MIT v0.2.0 repository directly occupy generic
  coupling bounds and interval-honest world-model benchmarking. The paper says it is not a new
  identifiability result and describes its SDP as a second-moment instance of existing
  counterfactual partial identification. An EcoMD benchmark row is application-only without a
  market-observable restriction and external truth.
- QuantReplay has no later checkpoint commit/tag than the previously audited August 12 head.
  `orderbook` has 26 commits after v0.26.0 but no new tag and still no complete population/RNG/
  scheduler/latency/calendar/policy checkpoint or independent scientific lineage. Neither re-entry
  condition is met.
- Seven evidence records and one `not_trigger` audit were added. Canonical totals are 312 evidence
  records and 29 trigger audits, zero qualified. The event-graph paper does not materially improve
  the existing partial testbed capability, so it does not supersede that entry merely by adding
  another semantically different exact world.

## Re-entry condition

Require a market-observable non-vacuous bound or estimator that is invariant to admissible noise
recouplings and event refinements, is not a restatement of counterfactual equivalence, response-type/
moment partial identification, transport gradients, dynamic OT or known boundary corrections, and
uses the same assigned action and complete filtration in two independent executable systems plus an
untouched confirmation source. Matched seeds, a canonical coupling assumption, an interval score or
another deterministic event log alone does not qualify.
