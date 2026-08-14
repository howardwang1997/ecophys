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

## CoW 100-ID retention and schema audit

**Decision:** `FAIL_SAMPLING_FRAME_AND_TIMESTAMP_LOOKUP`. The exact ID ledger is retained; no 404 was replaced and
the 1,000-ID expansion is not authorized.

**Collection commit:** `280a261ce`

**Failure-preserving summary commit:** `e88c4249f`

**Compact artifact:** `artifacts/cow_initial_summary.json`

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact ordered request ledger | 100/100 | 100/100 | PASS |
| HTTP-200 coverage | 33/100 = 33% | >=80% | **FAIL** |
| Parse rate among HTTP 200 | 33/33 = 100% | 100% | PASS |
| Requested/payload ID agreement | 33/33 = 100% | 100% | PASS |
| Duplicate payload IDs | 0 | 0 | PASS |
| Start-block timestamps before cutoff | unresolved | all available auctions | **FAIL** |
| Every terminal request outcome retained | 100/100 | 100/100 | PASS |

The 33 available competitions contain 506 solver solutions, 53 winner flags, 38 filtered solutions, 456 null
solution transaction hashes and 260,020 auction orders. Their raw payloads occupy about 31 MB. All available V2
payloads satisfy the frozen field/type parser.

The 67 HTTP 404s do **not** establish 33% historical retention. They show that arithmetic sampling over auction ID
space is not a valid high-coverage frame for persisted competition records: some IDs may never have produced the
endpoint object. Resampling only successful IDs would condition on availability and violate the contract. A repair
needs a separately frozen, outcome-blind enumerator of competition-eligible auctions or an auditable database
export; it cannot silently replace these IDs.

The runner then submitted the 33 unique start blocks in one fixed Cloudflare JSON-RPC batch. Cloudflare preserved
an error stating that its maximum batch size is ten. The 109-byte error response and its SHA-256 were retained, and
the summary was generated from the immutable request ledger without repeating any CoW request. Splitting the block
lookup into batches may be a later metadata-only repair, but cannot change the failed 33% sampling-frame gate.

This audit establishes schema parseability for available records, not score recomputation or exact mechanism
replay. It provides no participant-adaptation, policy-effect or prospective evidence.
