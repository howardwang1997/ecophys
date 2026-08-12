# Experiment 142 — Plan v4 G0 re-entry contract validation

**Frozen:** 2026-08-12

**Status:** preregistered; formal suite has not run

**Plan commit:** `fd99b1262`

**Contract implementation commit:** `f33db765f`

**Fixture SHA-256:** `6da9c773512a7b7c642e8ef7c0ba1e231a59c720c8ba9a83618299660d19bf2e`

**Runner SHA-256:** `3538ab7633e5a0a460e4bd7c88928637f505107d9ec0b4a1c05e024663f49d44`
**Scientific status before run:** G0 FAIL; no real candidate exists

## Question

Does the machine-readable G0 admission contract reproduce the frozen decision hierarchy on controlled fixtures,
reject the known v0 composition and policy violations, preserve semantic hashes under irrelevant ordering, and
make it impossible for software alone to emit a novelty PASS?

This experiment validates a research-process guard. It does not test an estimator, discover a theorem, establish
novelty or update the probability of an NCS paper.

## Frozen cases

| Case | Expected outcome | Exact reason codes |
|---|---|---|
| `review_ready_hypothetical` | `READY_FOR_HUMAN_AUDIT` | `HUMAN_AUDIT_REQUIRED` |
| `review_ready_hypothetical_reordered` | `READY_FOR_HUMAN_AUDIT` | `HUMAN_AUDIT_REQUIRED` |
| `rejected_v0_composition` | `REJECTED_EQUIVALENT` | `DECLARED_COMPOSITION_ONLY`, `NOVELTY_BASIS_NOT_FORMAL` |
| `performance_only_ecomd` | `REJECTED_EQUIVALENT` | `NOVELTY_BASIS_NOT_FORMAL` |
| `incomplete_new_label` | `INCOMPLETE` | `PROOF_SKETCH_MISSING`, `THEOREM_OBLIGATION_MISSING` |
| `ecomd_only_formal_claim` | `ECO_MD_ONLY` | `ECO_MD_ONLY_BENCHMARK`, `INDEPENDENT_SYSTEMS_INSUFFICIENT` |
| `pre_g0_resource_violation` | `INCOMPLETE` | `DATA_SCOPE_BEFORE_G0_INVALID`, `GPU_BEFORE_G0`, `MARKET_DATA_BEFORE_G0`, `SEALED_DATA_BEFORE_G0` |
| `unknown_schema_field` | schema error containing `paper_claim` | none |

The two review-ready cases contain the same deliberately hypothetical object. One recursively reverses mapping and
collection order; their semantic SHA-256 values must be identical. They are not a real candidate and their status
means only that a complete document can be routed to humans.

## Frozen gates

All seven gates must be true:

1. Every case exactly matches its expected status, ordered reason-code list and schema-error condition.
2. Every declared semantic-equivalence group contains exactly one candidate SHA-256.
3. `automated_novelty_pass` is false for every case.
4. `AdmissionStatus` contains no state whose value is `PASS`.
5. The suite declares `contains_real_candidate=false`.
6. The runner reads zero market files and opens zero sealed periods.
7. Actual GPU usage is zero.

If any gate fails, the result is `FAIL_PROCESS_VALIDATION`. A software-only defect may be diagnosed, but thresholds,
expected scientific outcomes and the experiment-142 raw result are not rewritten. A repaired formal protocol uses
a new experiment number.

If all gates pass, the result is `PASS_PROCESS_VALIDATION` and the scientific status remains
`NO_ADMISSIBLE_REAL_CANDIDATE`. Plan v4's G0 remains FAIL, candidate implementation stays blocked, and no V100,
market-data acquisition or compute expansion is authorized.

## Data and compute

- Inputs: this generated YAML fixture suite and the committed contract implementation only.
- Literature strings reproduce the already frozen 2026-08-10 audit; no web search occurs during execution.
- Forbidden: market data, historical checkpoints, exp141 artifacts, sealed periods and network access.
- Compute: Mac CPU in Conda environment `ecophys`; one process; expected below one minute; 0 GPU-hours.

## Execution chronology

1. Commit and push this preregistration, fixture and runner after static checks only.
2. From that exact clean commit run once:

   ```bash
   conda run -n ecophys python experiments/142_ncs_g0_reentry_contract/run_contract.py \
     --output /private/tmp/exp142_contract_validation.json
   ```

3. Copy the raw JSON into `experiments/142_ncs_g0_reentry_contract/artifacts/raw/` without transformation and record
   its file SHA-256.
4. Write the result document from the frozen gates; do not change code, fixture or expected outcomes.
