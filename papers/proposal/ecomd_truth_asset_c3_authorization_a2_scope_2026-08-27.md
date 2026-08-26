# C3 authorization record and A-2 platform-qualification scope freeze

Date: 2026-08-27 (Session 19)

## 1. Authorization

Precondition C3 of `ecomd_truth_asset_treatment_selection_audit_2026-08-26.md` is the explicit
user authorization to open stage A-2 of the capability-build plan
(`ecomd_truth_asset_capability_build_plan_2026-08-26.md`). The user authorized A-2 on
2026-08-27 ("然后再做 C3") after C1, C2 and the C4 conditional pass were committed and pushed
(commit `a233cb441` and this session's C4 record).

Authorized A-2 actions (from the plan's stage ladder): implement or modify a market platform,
run conformance fixtures and deterministic replay checks, and collect **synthetic** (robot)
pilot outputs. Still unauthorized: A-1 (site contact, recruitment quotes, ethics filing,
registration) and A0 (human sessions, outcomes, confirmation-site unsealing). GPU use remains
unauthorized by this record; all A-2 work is local CPU.

## 2. A-2 deliverables (frozen exit contract)

1. **D-2.1 Frozen event schema** (`scripts/lab_asset/schema.py`): arm-invariant grammar with
   immutable request/order/execution/rejection identifiers, replacement chains, reason-coded
   rejections, three timestamps per action (client decision, server receipt, matching), and a
   full-book state hash after every accepted action.
2. **D-2.2 Reference matching engine** (`scripts/lab_asset/matching.py`): continuous double
   auction, unit-lot core with quantity support; two arms — strict FIFO time priority and
   uniform random priority within the equal-price tie set — selectable behind the identical
   grammar; deterministic given (request tape, arm, seed).
3. **D-2.3 Deterministic replay validator** (`scripts/lab_asset/replay.py`): re-execution of a
   recorded accepted-action tape from the session prestate must reproduce every state hash
   exactly; any mismatch voids the session (per the plan's Part 4).
4. **D-2.4 Conformance fixture suite** (`tests/test_lab_asset_conformance.py`): golden
   scenarios (marketable cross, partial fills, tie-set allocation distribution, cancel-too-late,
   reason-coded rejections, replacement ancestry), grammar arm-invariance (identical request
   tape across arms produces identical grammar fields except allocation identities), and
   bit-level determinism under fixed seed.
5. **D-2.5 Platform binding (deferred sub-stage D-2b)**: port the schema and arms onto a
   hardened oTree fork seeded from the audited `domidt/CDA` layout; the reference engine is
   the conformance oracle the fork must match event-for-event on the same synthetic tapes.

## 3. Boundary conditions

- The reference engine is truth-asset infrastructure, not EcoMD integration; it lives outside
  the `ecomd` package and must not be imported by it.
- Synthetic pilots may use robot populations (including the C2 fixtures' ZI behavior) to
  exercise the pipeline end-to-end; their outputs are engineering evidence only, never route
  evidence, and are labeled as such in any artifact.
- The randomized arm's draw is a semantic event: the draw seed and the realized allocation are
  part of the released tape so third parties can replay exactly (the plan's
  semantic-randomness contract from Cycle 8's lessons).
- Stop conditions inherited from the plan: platform conformance or deterministic replay
  failure after two engineering iterations terminates the asset build (stop condition 1).
- This record creates no topic status, card, or forecast, and does not authorize candidate
  harvesting; the re-entry ledger remains untouched.
