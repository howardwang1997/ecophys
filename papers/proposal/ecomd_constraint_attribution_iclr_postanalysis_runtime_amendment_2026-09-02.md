# Outcome-blind post-analysis runtime amendment (2026-09-02)

Registered at `2026-09-02T03:05:45Z`, after all parent records had completed and
before any SWE or gauge-feedback scientific metric was accessed.

## Scope and observed structural failures

The completed SWE artifacts passed their record-count, checkpoint, provenance,
merge, and core-analysis integrity gates. The zero-training cube also completed
all 90 frozen records. Its analyzer then stopped at the algebra-only check with
`SWE cube path identity failed for id_r64, h=31`. No SWE scientific summary was
read. The gauge-feedback runner stopped before writing any of its 60 records
with `parent cube analysis is not integrity-bound`. No gauge-feedback metric was
produced or read.

This amendment authorizes only two deterministic runtime corrections:

1. Retain the frozen SWE `algebra_atol=1e-12` as an absolute floor and add a
   floating-point rearrangement allowance of
   `64 * float64_epsilon * max(1, sum(abs(identity operands)))`. This allowance
   is fixed from the operation count and IEEE-754 precision, not fitted to an
   observed effect. It applies only to the two redundant algebra identities.
   It does not change a cell value, estimator, bootstrap draw, confidence
   interval, SESOI, hypothesis test, multiplicity correction, trade-off rule,
   or classification.
2. Validate the frozen Advection cube analysis against the hash fields actually
   emitted by its registered analyzer: `core_input_sha256` and
   `derived_input_sha256`. The previously coded names,
   `core_records_sha256` and `input_sha256`, do not occur in that analysis
   schema. Exact SHA-256 equality and `integrity_gates_passed=true` remain
   mandatory; no binding is removed or weakened.

## Immutable completed SWE inputs

- V100a shard, 75 records:
  `f4b679b039547d44500a00a59ee109bfb898ec269a142b9748c9dbbf4bd4896c`
- V100b shard, 75 records:
  `b7b6e7e67bf9e2cfb1e50051a56e5b21d30e898fe5237ce9e093103331ee6e49`
- merged core, 150 records:
  `5e486167a2a8eb5099339422f9a0040b2f52b31d5ab3c10c4bb5db6ad6cef5bc`
- core analysis:
  `d194df9d3f8d0c19964a61006809adfd7fbc95efde41d26231cb812405f32ffd`
- checkpoint lock, 120 checkpoints:
  `772c52f9dbaa79f193aea1a17715dc8486f6e84e330ec11d5004a3b80a1037b5`
- zero-training cube, 90 records:
  `69dfa936fd838fa7ddc7c95e89a93e824c2ee6a6970daf0835517c95cd5723fa`

The repair must verify these hashes before rerunning only the SWE cube analyzer.
It must not rerun or rewrite a SWE worker, merge, core analyzer, checkpoint lock,
or cube record.

## Immutable Advection parents and gauge design

All parent hashes, seeds 3000--3029, two parent coordinates, three cases,
primary case `ood_r512`, ratio threshold 0.10, bootstrap settings, and the
expected 60 zero-optimization records remain exactly as frozen in the original
gauge-feedback protocol and decision. The failed attempt wrote zero records, so
there are no partial gauge records to retain, exclude, or inspect.

## Activation and disclosure gates

- Focused tests and Ruff must pass before deployment.
- A deployment manifest must bind the exact amended scripts, tests, this
  amendment, and its registered decision.
- SWE scientific summaries remain blinded until the amended analyzer exits
  successfully with 150 core records, 120 locked checkpoints, and 90 cube
  records bound to the immutable hashes above.
- Gauge scientific summaries remain blinded until exactly 60 finite,
  integrity-valid records exist and its analyzer exits successfully.
- Failed, negligible, or unresolved results must not be reframed as a positive
  contribution or forced into the manuscript.

