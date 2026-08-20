---
name: morpho-public-allocator-pressure-2026-08-20
description: "Fresh AMBER source-bound route for JIT liquidity routing, spatial demand-signal displacement, and AdaptiveCurveIRM memory."
metadata:
  node_type: memory
  type: project
---

# Morpho Public Allocator pressure displacement — 2026-08-20

This is a new route on branch `morpho-public-liquidity-contagion-feasibility-2026-08-20`, created from the
immutable close of the hidden-bot Morpho D0A. It does not identify or use private bots. The actor is the official,
publicly callable, code-bound Public Allocator contract.

For an atomic target borrow `x` accompanied by routed supply `r=sum f_i`, pressure
`q_i=B_i-0.9S_i` changes by `+0.9f_i` at each donor and `x-0.9r` at the target. Network pressure rises by exactly
`x`. When `0<=r<=x`, every touched market receives nonnegative pressure even though demand occurs only at the
target. A fully JIT-funded borrow displaces 90% of new pressure to donor markets and leaves 10% at the target.
This is a source-bound accounting lemma, not new theory.

The official contract at commit `51f92e57624099c5c3a4c9fdd88ed1ec2b16ac84` updates each donor's flow caps as
`(maxIn+f,maxOut-f)` and the target's as `(maxIn-r,maxOut+r)`. Hence per-market `maxIn+maxOut` is conserved between
admin resets: caps are directional displacement budgets, not replenishing rate limits. One-vault target capacity
is `min(maxIn_target, sum_i min(maxOut_i, vault_supply_i))` under the stated enabled/reallocation assumptions.

The broad story is occupied: Morpho and Contango already document shared liquidity and donor-rate effects;
Zbandut--Goldstein already describe mutualized liquidity stress/curator contagion; 2026 industry analyses already
attribute Resolv loss amplification to Public Allocator flows; max-flow and conservation are classical. The only
eligible residual is a prospective event-level field result that routed fraction predicts delayed local
AdaptiveCurveIRM memory and participant response along the vault--market graph. A contemporaneous balance check
or known exploit retelling fails novelty.

T0 plan/config:

- `papers/proposal/morpho_public_allocator_pressure_t0_plan_2026-08-20.md`;
- `configs/empirical_physics/morpho_public_allocator_pressure_t0_v1.yaml`.

T0 uses pinned source and synthetic arrays only. Historical events, flows, rates, utilization, Resolv data,
EcoMD and GPUs remain forbidden. A mathematical pass authorizes nothing beyond a separately frozen event-support
D0. NMI requires a prospective agent externality/design intervention; NCS additionally needs a general
reaction--transport inference method and a second independent adaptive-resource system.

Implementation was completed locally after the frozen plan commit `f26595061`: typed pressure/cap/capacity
utilities, a deterministic 10,000-trial formal runner, and focused tests. The runner also rejects dirty tracked
worktrees in either pinned upstream source clone, closing the `HEAD`-matches-but-files-differ audit hole. Seventeen
targeted tests, Ruff and strict mypy pass. This is not yet a formal scientific result: commit/push and a clean-SHA
run remain required, and all historical/event/outcome data plus GPUs remain untouched.
