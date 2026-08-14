# AEMO semantic-crosswalk held-out validation results

**Decision:** `FAIL_PACKAGE_NAMESPACE_DRIFT`. The frozen canonical source-field projection and internal table names
generalized to all ten held-out objects, but the frozen legacy bid-package namespace did not. Row access remains
locked.

**Crosswalk freeze commit:** `1d83133ce`

**Resolved HEAD metadata commit:** `6120759da`

**Collection and audit commit:** `16f0a7431`

**Held-out header contract:** `data/manifests/aemo_semantic_crosswalk_v2_headers.yaml`

**Header-contract SHA-256:**
`2e659468472383ae2b0bf860ce21e2fb6600e8f56312364fa7a2e7c9d1d27edc`

**Compact summary:** `artifacts/header_summary.json`

**Summary SHA-256:**
`35df57b5a76eb621b01b89c7e9cb6e96fcb1b2850f768534ddf59db709565afe`

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| Exact frozen objects | 10/10 | 10/10 | PASS |
| HEAD and GET HTTP 200 | 10/10 | 10/10 | PASS |
| Expected byte length | 10/10 | 10/10 | PASS |
| SHA-256 present | 10/10 | 10/10 | PASS |
| ZIP CRC | 10/10 | 10/10 | PASS |
| Exactly one CSV member | 10/10 | 10/10 | PASS |
| Frozen internal table | 10/10 | 10/10 | PASS |
| Frozen crosswalk source fields | 10/10 | 10/10 | PASS |
| Frozen header package | 8/10 | 10/10 | **FAIL** |
| Overall held-out header contract | 8/10 | 10/10 | **FAIL** |

The exact held-out archives total 1,557,149,667 compressed bytes and 43,677,147,189 uncompressed CSV bytes. The
2021-09 and 2025-07 months were selected mechanically and committed before their HEAD requests; no object was
replaced. All historical objects reported a 2026-04 `Last-Modified` timestamp, so the retained byte hashes rather
than the archival file names define this retrieval.

Both legacy bid objects expose package `BIDS`, whereas the discovery 2021-03 objects expose package `OFFER` and
the crosswalk froze `OFFER`. Their internal tables (`BIDDAYOFFER`, `BIDOFFERPERIOD`) and every source field required
by the canonical projection pass. The other eight objects pass completely. The current per-period bid header also
moves from version 3 in 2025-01 to version 4 in 2025-07 while retaining the full projection.

This does not prove that bid economics changed between 2021-03 and 2021-09. It proves that a two-regime mapping in
which the package token is a fixed semantic identifier is incomplete. Deleting that gate after seeing the result
would make 2021-09 a tuning sample, not held-out evidence.

The official postmortem identifies a staged 5MS mechanism transition, not a cosmetic alias. From 1 April through
30 September 2021, legacy 30-minute and new 5-minute submission paths coexisted; AEMO's technical specification
maps the old `OFFER` report types to the new `BIDS` report types. September is therefore transition data, not a
stationary legacy validation month. See
`papers/proposal/v14_aemo_5ms_schema_transition_audit_2026-08-14.md`.

The next admissible contract must be piecewise across pre-transition, transition and post-5MS regimes and must
resolve the republished March archive's non-canonical `OFFER,BIDOFFERPERIOD,1` combination before selecting fresh
months. The discovery and first held-out months cannot be used again as validation. No row was counted, filtered,
transformed or joined; no prospective outcome, paid data or GPU compute was used.
