# V14 open-data feasibility data runbook

This file implements, but does not alter, the sample frozen in
`data/manifests/open_data_development_sample_v1.yaml` and its resolved CoW manifest.

## CoW initial sample

`collect_cow_initial.py` must run from a clean commit. It reads exactly the 100 IDs in the resolved manifest, in
order, at no more than one request per second. It retries transport failures at most twice, never replaces an ID,
and does not retry an HTTP status merely because it is inconvenient. Every terminal request outcome is appended to
`artifacts/v14_open_data_feasibility/cow/request_ledger.jsonl`; every HTTP-200 body is stored byte-for-byte with its
SHA-256. This raw directory is ignored by Git. The compact aggregate summary is committed.

The contract requires block time, while CoW reports block numbers. The runner therefore makes one fixed batch
JSON-RPC request to `https://cloudflare-eth.com` for the returned `auctionStartBlock` values. The raw batch response
is hashed and retained locally. This timestamp lookup cannot change IDs, replace failures or affect parsing.

A partial run may resume only when its ledger is an exact prefix of the frozen ID list. Existing payloads are never
overwritten. The 1,000-ID expansion remains locked unless the initial retention, parsing, ID and time gates pass.

This stage measures retention and schema conformance. It does not yet recompute CoW scores or claim exact mechanism
replay, participant adaptation, policy prediction or prospective evidence.

## AEMO two-date header sample

`data/manifests/aemo_development_objects_v1.yaml` freezes ten individual table archives: five logical roles for
2021-03 and 2025-01. `collect_aemo_headers.py` downloads only those objects, verifies their declared byte lengths,
SHA-256 values, ZIP CRCs, single CSV members, MMSDM information headers, table names and minimum official fields.
It deliberately does not count, filter, join or replay data records.

Completed archives live under the ignored raw-artifact root. A partial transfer may resume the same object by HTTP
Range; it cannot substitute a URL, month, date or table. The generated header contract keeps row joins locked and
must itself be committed before a selected-date row parser is run. This phase uses CPU and no GPU.
