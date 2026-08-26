---
name: EcoMD re-entry capability trigger audit
description: Five recent simulator/model developments were source-audited after Cycle 16; all are useful watch assets but none removes a recorded blocker, so Cycle 17 remains unopened.
node_type: memory
type: project
---

# EcoMD re-entry capability trigger audit

The outcome-blind audit is
`papers/proposal/ecomd_reentry_capability_trigger_audit_2026-08-26.md`. It is not a topic-search
cycle and creates no topic card, forecast, sandbox, or execution authorization.

## Durable result

- QuantReplay v12 (`a58c7c6d...`, Apache-2.0) is a credible new open FIX venue with seeded order
  generation, matching, replay, L2 and persistence, but its snapshot is only venue/instrument/book
  state. It omits generator RNG, future scheduling, current phase and external strategy state, and
  explicitly skips resting auction market orders and Trade-at-Last orders.
- `orderbook` v0.26.0 (`51d480cd...`, MIT) has a strong exact matching-engine snapshot/WAL
  contract, including conditional orders and counters. It does not checkpoint the simulator
  population, external RNG, scheduler, latency, calendar, or adaptive-policy state.
- `lobsim` (`0cb48ed8...`, Apache-2.0) is deterministic L3 replay and strategy injection rather
  than an adaptive population or a field counterfactual.
- DiffLOB's future trend/volatility/liquidity/OFI regime is an outcome-conditioned path label, not
  a legal market `do` action. It therefore does not remove the closed interventional-fidelity
  route's truth target or generic-parent blockers.
- The current latency-race/impact-memory queue-reactive model is a useful simulator prior but adds
  no independently assigned complete-state field response.

All five entries have `candidate_harvest_authorized: false` in the new append-only
`research/discovery/reentry_trigger_ledger.yaml`. The validator now binds proposed triggers to
registered routes, failure families, pinned clean evidence, audited claims, and exact re-entry
scope. It also protects both search-cycle and trigger-ledger prefixes under `--base-ref`.

## Re-entry rule

Re-audit only if a later entry supplies either two independent full-population checkpoints with a
common legal action/clock, a licensed assigned field response with complete state, or a theorem that
invalidates a recorded reduction. Another matching engine, replay tape, regime-conditioned model,
or interactive simulator is not sufficient.

No outcome access, simulator run, implementation, data action, purchase, outreach, EcoMD change,
sandbox, GPU, or CPU experiment is authorized.
