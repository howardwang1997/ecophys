# V14 open-data feasibility results

## Generated-data calibration

**Decision:** `FAIL_UNDERPOWERED` under the frozen contract. The failure is retained and the same protocol/seeds
will not be tuned and rerun as a confirmatory pass.

**Run commit:** `8d2e6d184`

**Scientific artifact:** `artifacts/synthetic_calibration.json`

**Scientific-result SHA-256:**
`6fc0146f99a807ea4c2ee4743d1d4cad9c71a4077fcb291ee46a7f8acf59f715`

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Null false-positive rate | 5.8% (29/500) | <=8% | PASS |
| Exact binomial calibration p-value | 0.411 | >=0.01 | PASS |
| Declared-effect power | 38.6% (193/500) | >=80% | **FAIL** |
| Correct-clock selection rate | 56.0% | >=80% | **FAIL** |
| Leakage detection | 100% | 100% | PASS |
| Effective-identity violation detection | 100% | 100% | PASS |
| Missing/failed action-status detection | 100% | 100% | PASS |
| Valid-record acceptance | 100% | 100% | PASS |

The paired energy-score randomization procedure is calibrated under its generated null, and the structural
contract catches the three deliberately invalid record classes. It does not have enough information at 48
independent blocks to distinguish the declared `0.55` standardized response reliably, nor to separate the frozen
response clock from a four-block delay. Treating auctions, participants or five-minute rows as extra independent
events would not repair that limitation.

This result blocks E2 model-ranking claims under the current sample contract. A repair must use a new protocol and
fresh root seed after choosing a scientifically plausible minimum effect and independent-block count. Increasing
the effect merely to pass this experiment is not allowed. CoW retention/schema and AEMO archive/schema E1 checks
remain separately executable because they do not use this statistical-power result to select outcomes.

No market row, target event, GPU or remote worker was used by this run. Runtime on the Mac CPU was 5.15 seconds.
