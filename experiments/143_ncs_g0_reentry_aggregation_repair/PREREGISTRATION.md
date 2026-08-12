# Experiment 143 — repair of exp142 aggregate pass semantics

**Frozen:** 2026-08-12

**Status:** preregistered before repair implementation

**Parent result:** exp142 `FAIL_PROCESS_VALIDATION`, raw SHA-256
`ec41af58e886d111b5fdedb5c5ce12de57d3f8ebda19dc762d427741ef4671db`

**Reused fixture:** `experiments/142_ncs_g0_reentry_contract/fixtures.yaml`, SHA-256
`6da9c773512a7b7c642e8ef7c0ba1e231a59c720c8ba9a83618299660d19bf2e`

**Unchanged candidate contract:** `ecomd/invariant_calibration/g0_contract.py`, SHA-256
`96aed45ceba1e7c98bc3648c036c7302364bb4799ad0c6b2d9cd657c2a0a0f8e`

**Scientific status before run:** `NO_ADMISSIBLE_REAL_CANDIDATE`; Plan v4 G0 FAIL

## Frozen defect and repair scope

Exp142's eight case outcomes, reason codes and semantic-hash check all matched. Its runner nevertheless emitted
`FAIL_PROCESS_VALIDATION` because it stored the compliant raw observation `actual_market_data_read=false` in the
gate mapping and then called `all(gates.values())`.

Exp143 changes only experiment-level aggregation semantics:

1. Raw resource facts live under `observations`, never under `gates`.
2. Every item under `gates` is a positive pass predicate.
3. `market_data_files_read=0` maps to `no_market_data_read=true`.
4. `sealed_periods_opened=0` maps to `no_sealed_period_opened=true`.
5. `gpu_hours=0.0` maps to `no_gpu_usage=true`.
6. Overall PASS is `all(gates.values())` only after the mapping above.

Forbidden changes include edits to the exp142 fixture, the candidate-contract implementation, expected case
statuses or reason codes, state priority, semantic canonicalization and scientific status.

## Frozen inputs and expected outcomes

The exp142 fixture is read byte-for-byte at its frozen SHA. All eight cases retain the exact expected outcomes in
the exp142 preregistration. In addition, both review-ready hypothetical cases must retain semantic SHA-256
`a29bbf74fd20e47bf80f2de529e4eef03f0254681052763341f8033924413343`.

No fixture is a real candidate. `READY_FOR_HUMAN_AUDIT` remains a process-routing state, not novelty PASS.

## Frozen gates

All gates must be true:

1. `exact_expected_outcomes`: all eight frozen case outcomes match.
2. `semantic_hash_invariance`: the differently ordered pair has one semantic hash, equal to the frozen value.
3. `no_automated_novelty_pass`: every case records false.
4. `no_pass_state`: the candidate state enum contains no `PASS` value.
5. `no_real_candidate`: the reused suite declares false.
6. `no_market_data_read`: observation equals zero files.
7. `no_sealed_period_opened`: observation equals zero periods.
8. `no_gpu_usage`: observation equals 0.0 GPU-hours.
9. `positive_gate_namespace`: every gate value is boolean and no gate key begins with `actual_`.
10. `frozen_parent_inputs`: fixture and candidate-contract SHA-256 values equal those above.

The decision is `PASS_AGGREGATION_REPAIR` only if all ten gates are true. Otherwise it is
`FAIL_AGGREGATION_REPAIR`; the raw result is retained and another experiment number is required.

## Data and compute

- Mac CPU, Conda `ecophys`, expected below one minute.
- Inputs are one generated YAML fixture and committed Python source only.
- Zero market files, zero sealed periods, zero network access and zero GPU-hours.
- The current 2xV100 workers and RTX2060 are not contacted.

## Chronology

1. Commit and push this preregistration before implementing the repaired runner.
2. Implement a new exp143 runner; do not edit the exp142 runner or raw result.
3. Add focused unit tests for raw-observation-to-positive-gate mapping.
4. Commit and push the runner/tests, record their SHA-256 values in an immutable freeze manifest, then run once from
   a clean checkout.
5. Archive the raw JSON byte-for-byte before writing the result.

Even a PASS only validates the process guard. It leaves G0 FAIL and authorizes no candidate implementation, market
data, V100 use or NCS claim.
