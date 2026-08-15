# AEMO modern bundle-bridge stability panel v1 — implementation failure

**Decision:** `FAIL_PANEL_IMPLEMENTATION_PRE_PARSE`

**Protocol commit:** `1f44811e75a455f161532fbfdd3bde2092508bf5`

## What passed

All eight frozen AEMO source requests returned HTTP 200 exactly once with their exact byte counts, totalling
70,593,936 bytes. All eight were uploaded and verified at their frozen R2 keys. The two prior June/July identity
objects were verified and materialized from their original R2 keys with no new AEMO source request. All ten local
and remote size/SHA checks passed; staged compressed bytes were 71,350,764.

Receipt SHA-256 values are:

- download: `5a9735d0a427bdc5f34e99bb4933dd5ce2c08ffa4ece65d5f108a01ab7b2fabc`;
- R2 retention/materialization: `1eba9a2d9440c2e44edc9af99a236f9500707b1f9c592f9e6e086d69b10776c7`.

## Failure

The analyzer failed on the first day with `KeyError: 'resource_contract'`. The day-level derived manifest omitted
the resource section required by `parse_conformance_archives`.

This happened at `ecomd/research/aemo_row_conformance.py:693`, before the archive loop and before
`parse_mmsdm_archive` was called. Therefore:

- ZIP open attempts: 0;
- CSV rows opened: 0;
- market content observed: false;
- day summaries produced: 0;
- scientific relation result: none.

The failure is preserved in `artifacts/analysis_failure.json`; no v1 result summary exists. The missing field is an
implementation defect, not evidence for or against bridge stability.

## Admissible repair boundary

The v1 protocol is not rerun or silently edited. Because the failure preceded all content access, a separate
pushed repair protocol may reuse the exact verified R2 bytes without issuing any new AEMO source request. That
repair may add only the missing parser resource contract and associated preflight test. It may not change the four
dates, relation rule, thresholds, table contracts or claim boundary.

GPU, paid data, target outcomes and model runs used: none.
