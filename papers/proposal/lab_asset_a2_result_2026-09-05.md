# Formal A-2 result — truth-asset platform qualification (2026-09-05)

Machine decision: `research/discovery/decisions/truth_asset_a2_platform_qualification_20260905.yaml`
(SHA-256 `d4007a212fe6222df14859959dea6c2371524336e06f0e287263b372f5e64712`).
Governing contract: A-3 plan Parts 4, 7 and 8
(`papers/proposal/ecomd_truth_asset_capability_build_plan_2026-08-26.md`).

**Verdict: A-2 exit criteria MET in two engineering iterations with zero conformance or replay
failures. The stop rule (Part 8 rule 1) was never triggered.**

## Exit-criterion evaluation (from the machine decision)

1. **All A-3 Part 4 fields present in emitted tapes.** Iteration 1 closed the four seed gaps
   (`role`, replacement/parent lineage, `rejection_id`, pre/post best quotes on accepted
   actions); iteration 2 proved coverage mechanically: the exporter's self-check requires every
   payload key observed in the emitted fixture tapes (recursively, including nested
   `execution.*`, `allocation_draw.*`, `clocks.*`) to be declared in the frozen specification.
   Result: `experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json` (lab-asset-v3) covers
   every observed key; the check is a permanent part of the exporter.
2. **Deterministic replay reproduces every state hash on conformance fixtures and robot
   pilots.** Fixture verifier `scripts/lab_asset/verify_fixtures.py` re-loads the bundle from
   disk, verifies the SHA-256 manifest, re-executes both arm fixtures from their serialized
   prestates, and checks record-level replay equality plus byte-exact tape regeneration:
   `lab_asset_a2_bundle_verify=PASS` (21 records FIFO, 22 records random-unit; the random-unit
   arm emits one additional unit execution, as designed). Robot pilots (iteration 1): 4 paired
   sessions per arm, 5,000 steps, `all_replays_ok: true` on both arms. The conformance suite
   (27 tests) additionally proves bit-level determinism and tamper detection on replace tapes
   and on the exported bundle.
3. **Schema frozen as a versioned artifact.** `schema_spec.json` (SHA-256
   `c2341ce73f8c32d1b395fad81f0bd4c68a3ac0de0e235ea4d638acc48c24346a`) plus the two
   prestate/tape/replay-report fixture triples are sealed under the bundle manifest. Bundle
   directory: `experiments/lab_asset_a2/a2_exit_20260905/` (manifest lists all 7 file hashes).
   Schema version `lab-asset-v3` frozen as of this result; any future grammar change requires a
   new version tag and new fixtures.
4. **Formal A-2 result written.** This document.

## Frozen semantics carried forward

- Tape grammar per `schema_spec.json`: 14 event types; identifiers `O/E/R%08d` plus
  client-supplied ids; three clocks per event; reason-coded rejections (11 order, 6 cancel, 4
  latency, 13 replace codes); pre/post best quotes on accepted actions; identity and anonymous
  state hashes with engine RNG state; replacement lineage via `order_parent`/`lineage_root`;
  roles resolved from the prestate only.
- Replay contract: re-execute request events from the prestate; the regenerated tape must equal
  the recorded tape record-by-record including every state hash (canonical-JSON payload
  equality).
- Recorded schema decisions: `session_id` is tape-level; `role` is never client-supplied.

## Engineering iteration ledger

- Iteration 1 (2026-09-05, session 55): Part 4 gap audit + engine/schema/adapter/replay/pilot
  implementation; 31 tests PASS; both pilot arms replay-validated. Record:
  `papers/proposal/lab_asset_a2_iteration1_2026-09-05.md`.
- Iteration 2 (2026-09-05, session 56): versioned schema artifact, serialized fixtures,
  independent from-disk verifier, exporter self-check, bundle round-trip and tamper tests; 27
  conformance tests PASS (superset of iteration-1 checks relevant to the kernel), Ruff clean.

## Authorization state after this result

The A-2 machine decision's `effective_until: a2_exit_...` condition is now met; the decision
terminates with **exit criteria satisfied and no stop rule fired**. Per the frozen A-3 ladder,
the next legal rungs — the bounded outcome-blind treatment-selection audit (A-3, paper-only) or
A-1 site/ethics work — each require a new explicit PI authorization. No participant, outreach,
ethics, treatment-adjudication, candidate-harvest, EcoMD, GPU, or market-outcome action occurred
or is authorized by this result. This result creates no topic card and reopens no route: a
qualified re-entry trigger remains required for any topic cycle.
