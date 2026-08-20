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

Implementation was committed and pushed at `4a480108e1090dc88460b52c4f8ffd6a81738b72`: typed
pressure/cap/capacity utilities, a deterministic 10,000-trial formal runner, and focused tests. The runner also
rejects dirty tracked worktrees in either pinned upstream source clone, closing the
`HEAD`-matches-but-files-differ audit hole. Seventeen targeted tests, Ruff and strict mypy pass.

The one formal T0 run from that clean upstream-matched SHA passed all seven frozen gates. Canonical payload
SHA-256 is `f6b765d249ca75a0355db3007508201b41eab257367a15194c0e52a8625ea2a6`; independent read-back matches.
The largest normalized residual was `4.3482e-16`. Scientific decision remains
`math_encoding_pass_novelty_and_field_support_remain_amber`: this verifies accounting only. All historical,
event and outcome data plus EcoMD and GPUs remained untouched. Next authorized step is a separately frozen D0
event-identity/support audit; do not retrieve history before that contract is committed and pushed.

D0 was subsequently designed without opening event history. It fixes only Ethereum and Base from the official
SDK at `eb27628b8`, with finalized endpoints at Ethereum block 25,795,523 and Base block 50,214,705; SQD and
independent RPC headers match. The outcome-blind identity proxy requires a Public Allocator withdrawal/terminal
sequence followed later in the same receipt by an exact-Morpho Borrow whose market topic matches the target.
Amounts remain undecoded, so these are atomic routing--borrow candidates, not yet genuine JIT events. Frozen
support requires 500 pooled, 100 per chain, 90-day spans, 30 active dates, 3 vaults and 4 edges per chain, 12
edges pooled, exact classification/receipt verification and no unresolved transport discrepancy. D1 must later
retain 300 after amount compatibility and AdaptiveCurveIRM binding. Plan/config are pending commit; no event count
has been queried and no D0 implementation exists yet.
