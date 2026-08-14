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

## AEMO two-regime exact-object and header audit

**Decision:** `FAIL_SCHEMA_CONTRACT`. The immutable archives are obtainable and intact, but the preregistered
file-name-to-internal-table identity and minimum-field contract is false. Row filtering and joins remain locked.

**Collection and audit commit:** `cd00c7169`

**Header contract:** `data/manifests/aemo_development_headers_v1.yaml`

**Compact artifact:** `artifacts/aemo_header_summary.json`

**Header-contract SHA-256:**
`4668132789160bafd2676a8ad8c963c9dfa6c298c608f56bd3c31f9700c6b78b`

**Summary SHA-256:**
`63b5bdc70090d73ebef0d15f876d4a9f1526b3c9bb2a67755621cd7b5a4b345d`

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact frozen-object ledger | 10/10 | 10/10 | PASS |
| HTTP 200 | 10/10 | 10/10 | PASS |
| Expected byte length | 10/10 | 10/10 | PASS |
| SHA-256 present | 10/10 | 10/10 | PASS |
| ZIP CRC | 10/10 | 10/10 | PASS |
| Exactly one CSV member | 10/10 | 10/10 | PASS |
| Frozen archive/internal table identity | 5/10 | 10/10 | **FAIL** |
| Frozen minimum fields | 9/10 | 10/10 | **FAIL** |
| Overall header contract | 5/10 | 10/10 | **FAIL** |

The ten exact archives total 1,177,771,842 compressed bytes and 31,878,556,073 uncompressed CSV bytes. This
establishes free acquisition, integrity and bounded streaming feasibility; it does not establish a stable semantic
panel. The audit ran on the CPU of V100-A with CUDA hidden. It opened information headers and streamed ZIP CRCs,
but counted no data rows, performed no row join and used no target-event outcome.

The failures are informative rather than transport errors. `DISPATCHOFFERTRK` archives identify their internal MMS
table as `DISPATCH/OFFERTRK` in both periods, and `DISPATCHLOAD` archives identify it as
`DISPATCH/UNIT_SOLUTION`. The legacy per-period bid archive is `OFFER/BIDOFFERPERIOD` version 1 and uses
`TRADINGDATE`, not the frozen `SETTLEMENTDATE`; the current archive is `BID/BIDPEROFFER_D` version 3. Other version
changes include `UNIT_SOLUTION` 2 to 5 and `DUDETAILSUMMARY` 4 to 7. Renaming files would hide these distinctions.

The clean repair is a new protocol, not an edit to this result: treat these two periods as schema-discovery data,
freeze an explicit field-level semantic crosswalk, and validate it on separately selected, previously unopened
legacy and current months. Only a committed held-out header pass can unlock selected-date row filtering. The v1
artifacts and failed gates remain immutable.

The separately frozen held-out repair also failed its strict package-namespace gate while passing all ten internal
table and required-source-field projections. Official 5MS records subsequently established that the 2021-09
failure lies inside a real 30-minute/5-minute bidding transition rather than a cosmetic namespace change. See
`experiments/v14_aemo_semantic_validation/RESULTS.md` and
`papers/proposal/v14_aemo_5ms_schema_transition_audit_2026-08-14.md`. This keeps row access locked and prevents the
discovery months from being relabeled as validation.

## AEMO two-clock loader-control validation

**Decision:** `PASS_TWO_CLOCK_LOADER_ENDPOINTS_ONLY`. Six exact, previously unrequested official SQLLoader
controls from mechanically selected 2020-09 and 2022-04 months passed HTTP, parse, owner, target-table, required-
column and non-`FILLER` gates. See `experiments/v14_aemo_loader_control_audit/RESULTS.md`.

This resolves the March anomaly at the loader layer. AEMO deployed an emulated reporting compatibility layer on
8 March 2021 before bidding transition began on 1 April: the March period export uses the new-shaped
`BIDOFFERPERIOD` header but its official control appends into legacy `BIDPEROFFER` and discards the new clock and
ramp columns. The observation clock therefore changes before the mechanism clock.

The result is a metadata feasibility pass, not a reversal of either failed archive-header audit. No CSV/ZIP,
market row, GPU or paid data was opened. Row access remains locked pending a separately frozen two-clock header
protocol.

The subsequent bounded ZIP-prefix audit preserved another failed gate. All ten exact 2020-09/2022-04 range
requests and parsers passed, as did every member, package, table and required-field projection, but exact versions
passed only 7/10. The failures were legacy `BIDPEROFFER` version 1 versus 2 frozen, post-5MS `UNIT_SOLUTION`
version 3 versus 2, and `DUDETAILSUMMARY` version 5 versus 4. See
`experiments/v14_aemo_prefix_header_audit/RESULTS.md`.

This establishes that required numerical/key fields may be bridgeable while table-version clocks remain
source-specific. The failure is not repaired post hoc and no market row was opened. Post-run safety correction:
the preserved `Content-Range` metadata shows that the two small `DUDETAILSUMMARY` responses contained every
compressed byte, despite the original collector's contrary flag. See the authoritative correction in
`experiments/v14_aemo_prefix_header_audit/RESULTS.md`.
