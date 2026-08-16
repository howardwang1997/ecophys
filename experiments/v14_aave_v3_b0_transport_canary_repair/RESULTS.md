# Aave V3 B0 target-row-free transport repair canary v2 result

**Decision:** `FAIL_TARGET_ROW_FREE_TRANSPORT_REPAIR_KEEP_B0_V2_B1_G1_GPU_LOCKED`

## Sealed execution and integrity

- Protocol commit: `91188042c798709ecbc4a11784cdf0a8864c7923`, pushed and remotely verified before
  any v2 RPC request.
- Manifest SHA-256: `e8d286f83218183afb9ab56ee25b48578dc7eaceb4c6b1dd32f6e8f4eb44f2c8`.
- Repair source SHA-256: `89b0f179222ec922dbbeda92a93043948c2e83d275ec62aafe73e0ae7b022870`.
- Pinned v1 dependency SHA-256: `6f56b9fa956d7c8ab2cc7d48ab776bdeedc428211cb644c06ad0eeeea0a1155f`.
- RTX 2060 artifact SHA-256: `593040382bf6866b682974f66109940f9c297480ac910d23f4d659f24d4f2e27`.
- Mac artifact SHA-256: `296327dbb6f0372ed016f43d7f0cf01aede467287c8cb16da1064e6747ec175d`.
- Aggregate SHA-256: `4cd70d0ef198a88f8e2e6014cbb4de10c24a2f357259432212bdc2a57fe4df33`.

The detached-commit preflight passed all 15 focused v1/v2 tests, format/Ruff, strict mypy, manifest validation and
every parent hash/structure check. The RTX staged files matched the detached worktree byte for byte. Both hosts
completed before aggregation; the independent aggregate rerun was byte-identical. Aggregate validation errors are
empty.

## Host results

| Host | Repairs passed | Logical calls | HTTP attempts | Bytes | Sealed duration |
|---|---:|---:|---:|---:|---:|
| RTX 2060 | 2/3 | 25 | 42 | 4,299 | 21.115 s |
| Mac | 2/3 | 24 | 42 | 4,211 | 52.812 s |
| **Total** | — | **49** | **84** | **8,510** | parallel |

CUDA was hidden on both hosts. No V100, GPU library, paid endpoint, purchased data or raw response payload was
used.

## Endpoint findings

- **Polygon replica passed on both hosts.** Chain ID and the zero-address single block were valid. Persistent HTTP
  400 responses required deterministic bisection down to `[0,61]`, giving the same conservative span of 62 blocks
  on both egresses.
- **Base replica passed on both hosts.** Persistent HTTP 413 responses stopped at `[0,7812]`, giving the same
  conservative span of 7,813 blocks on both egresses.
- **The sole frozen BNB candidate failed on both hosts.** RTX returned the correct chain ID, then JSON-RPC `-32000`
  rate limiting for the zero-address block-0 log request. Mac returned HTTP 429 on both allowed chain-ID attempts.
  Both outcomes are terminal under the preregistered rule; no range query was made.

The agreement for Polygon and Base validates the revised range-error classification. It does not show that a
62-block Polygon span can satisfy B0's unchanged scientific request cap; that would need to be proved in a later
protocol even if BNB transport existed.

## Scientific interpretation and access decision

No Aave address, topic or event row was queried. The only successful log responses were empty zero-address lists;
target rows retained are zero. Therefore this is an infrastructure decision, not a measurement of cross-chain
program support.

No host covers all three repairs, so the six inherited v1 routes cannot be combined into a valid nine-deployment
plan. B0 v2 is not authorized; B1, transactions/receipts/state, accounts, outcomes, G1 and GPU training remain
locked. The current no-auth free-RPC route is closed. The BNB candidate cannot be replaced after observation, and
the scientific design cannot drop BNB or weaken its split/support gates to rescue the result.

A future reopening requires a new, documented archive-data resource decision—such as institutionally provided,
partner-provided, self-hosted or purchased access—followed by a separately committed target-free qualification
protocol. Endpoint guessing is not the next experiment.
