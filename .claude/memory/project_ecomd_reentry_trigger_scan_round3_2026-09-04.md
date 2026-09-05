# EcoMD re-entry trigger scan round 3 (2026-09-04)

## Canonical decision

No qualified re-entry trigger was found. Cycle 17, candidate harvesting, implementation, outcome
access, simulation, SSH and all three GPU workers remain closed for this EcoMD route. The formal result is
`papers/proposal/ecomd_reentry_trigger_scan_round3_2026-09-04.md`.

## Durable findings

- Ni--Kamgarpour safe sim-to-real transfer is a real generic capability: in a finite-horizon tabular
  CMDP it can certify simulator-equal transition regions and restrict target learning to a sparse
  mismatch set. It requires active real rollouts, a known strictly feasible real policy and margin,
  common finite state/actions and a known separation for unequal transition triples. Wu et al.'s
  shifted hybrid RL likewise needs online target interaction and valid fine-grained bias bounds.
  These conditions do not hold for passive public market data.
- Passive simulator certification has a reusable impossibility twin. Two target MDPs can agree on
  every behavior-policy transition yet have opposite value or safety after an unvisited action.
  Passive observations cannot certify that action without coverage or structural restrictions.
- S3's smooth discrete-abstraction optimization is sound because a separate Taylor-model
  reachability analysis certifies known deterministic dynamics; it does not certify a surrogate
  gradient or an unknown real response. Hybrid discrete--continuous mixed gradients already have a
  direct unbiased parent, so neither route reopens the hard-event method family.
- Chen--Glasserman show that a transformer can generate valid synthetic LOB paths while learning the
  wrong known finite-state Markov kernel and spurious history dependence. This directly occupies a
  generic world-model mechanism diagnostic. In real L2, history dependence can instead be correct
  filtering over same-L2 states with different order age, identity or private policy; the null is not
  identified until the observation quotient is completed.
- Zenodo `10.5281/zenodo.18184441` is a valuable CC-BY-4.0 Hyperliquid L4 asset with accepted and
  rejected lifecycles, wallet/order IDs, book diffs, trades, positions and native TWAP identifiers.
  Only its outcome-blind schema and small public documentation/code were inspected. Public book
  diffs omit consensus blocks, timestamps and oracle data; the partial reconstruction repository
  synthesizes timing gates and block counters. Wallets are not verified beneficial owners, private
  strategy/belief/off-venue state and assigned counterfactuals are absent, one venue-month is not an
  independent confirmation lineage, and direct identity/rejection/TWAP work occupies broad claims.
- Hyperliquid native TWAPs are a genuine near-miss: the protocol optionally randomizes child size by
  up to plus or minus twenty percent. The public order-status schema does not link children to parent
  TWAP settings, and executed trades expose only `twap_id`, not the randomize flag, draw probability,
  seed or intended nonfill-inclusive child tape. Adaptive catch-up makes later and realized size
  depend on prior market outcomes. This is a partial capability, not an observed instrument.
- Axiomatic Market Making directly occupies quote-rule axiomatization and presupposes one maker's
  dynamic quote/inventory schedule for cost recovery. The same aggregate depth curve admits infinitely
  many maker-level decompositions with different inventory-cost derivatives; Hyperliquid wallet tags
  do not close that identification gap.
- Seven append-only trigger audits were added: three `partial_capability`, four `not_trigger`, zero
  blocker removals and zero candidate-harvest authority. The canonical totals are 278 evidence
  records and 23 trigger audits, still zero qualified.

## Re-entry condition

Require one written object before another review: a passive-transfer partial-identification or
abstention theorem with observable non-vacuous bounds; a representation-invariant world-model
diagnostic or independently established L4 Markov state; a lawful assigned complete-state market
intervention with sealed independent confirmation; or a maker-response partial-identification theorem
invariant to wallet splitting and aggregate superposition. Even a qualified trigger would authorize
only a bounded question screen; GPU use still needs a machine card and current machine decision.
