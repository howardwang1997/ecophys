# Truth-asset A-2 platform qualification authorized (2026-09-05)

## What was authorized

The PI authorized opening the **A-2 rung** of the frozen A-3 truth-asset capability-build plan
(`papers/proposal/ecomd_truth_asset_capability_build_plan_2026-08-26.md`, SHA-256
`553f773b...431`): platform implementation/qualification, conformance runs, and synthetic robot
pilots. Machine decision:
`research/discovery/decisions/truth_asset_a2_platform_qualification_20260905.yaml`
(SHA-256 `d4007a21...712`), pointed to by `research/discovery/current_machine_decision.yaml`.

## Scope (memorize exactly)

- Platform seed: `scripts/lab_asset/` (schema, matching engine, replay verifier, robot pilot,
  conformance runner; retained from the closed 2026-08-27 C4 preflight).
- Goal: satisfy A-3 Part 4 — full lifecycle with client/server/matching timestamps, reason-coded
  rejections, pre/post best quotes, full-book state hash per accepted action, replay prestate
  (endowments, induced-value draws, schedule, initial book, rule config, RNG state, assignment
  key). Deterministic replay must reproduce every state hash on fixtures and robot pilots.
- Compute: local Mac CPU only. Arms: FIFO vs random-unit-within-price under one arm-invariant
  grammar (treatment *selection* is a separate future A-3 audit).
- Stop rule: conformance/replay failure after **two engineering iterations** terminates the asset
  build (A-3 Part 8 rule 1). Any arm-dependent schema drift voids the iteration.

## Still forbidden (unchanged)

Human participants, outreach, site contact, ethics filing (A-1); treatment adjudication; candidate
harvesting; topic cards; route re-entry; EcoMD integration; GPU use; market-data outcome access.
A-2 success alone reopens no route; a qualified trigger-ledger entry is still required for any
topic cycle.

## Context at authorization

All EcoMD/ICLR discovery families are saturated (99 trigger audits, zero qualified); Paper D's
machine-decision chain is terminal (`complete_gate_not_passed`), the manuscript is committed
(`3aae4926a` and descendants) and the GitHub repository was made private on 2026-09-05 to resolve
the double-blind blocker (abstract deadline 2026-09-18). The verification-liquidity holdout stays
sealed until 2026-10-17 UTC.
