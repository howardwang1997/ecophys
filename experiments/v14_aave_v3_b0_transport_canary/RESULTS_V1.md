# Aave V3 B0 target-row-free transport canary v1 result

**Decision:** `FAIL_TARGET_ROW_FREE_TRANSPORT_CANARY_KEEP_B0_V2_B1_G1_GPU_LOCKED`

## Sealed execution and integrity

- Protocol commit: `4f18e81850102023ce802109f47bb5727f6315a0` (pushed and remotely verified).
- Manifest SHA-256: `a524b694b761e324571c74f0d4131295722c0d6094e9fc2e0abe5f5e84864c33`.
- Source SHA-256: `6f56b9fa956d7c8ab2cc7d48ab776bdeedc428211cb644c06ad0eeeea0a1155f`.
- Aggregate summary SHA-256: `28946aa8439804b9a69f0e9a0793adece6e5903a33c8fba47f4475dfd917bab3`.
- Host artifact SHA-256 values: V100-A `2443e736...`, V100-B `a989a01d...`, RTX 2060
  `c3aec562...`, Mac `61c6016d...`.
- The independent aggregate validation has zero errors. It recomputed every request hash, zero-address filter,
  attempt/byte total, endpoint identity, endpoint decision and host coverage before applying the frozen order.

## Host results

| Host | Covered deployments | Logical calls | HTTP attempts | Bytes | Wall time |
|---|---:|---:|---:|---:|---:|
| V100-A | 5/9 | 77 | 83 | 6,541 | 150.8 s |
| V100-B | 5/9 | 77 | 83 | 6,541 | 169.5 s |
| RTX 2060 | 6/9 | 84 | 90 | 7,204 | 47.6 s |
| Mac | 6/9 | 84 | 91 | 7,315 | 97.3 s |

No single host covers all nine deployments, so the aggregator selected no host. Total use was 322 logical calls,
347 HTTP attempts and 27,601 response bytes.

## Endpoint findings

- Arbitrum passes through the replica at a 250,000-block prefix; the PublicNode primary rejects the single-block
  log query.
- Avalanche passes through primary at 31,250 blocks and replica at 1,954 blocks.
- Optimism passes through the replica at 7,813 blocks on RTX 2060 and Mac. Its primary rejects the single-block
  query; the two V100 egresses also fail replica chain identity transport.
- Gnosis passes at 7,813 blocks on primary and 250,000 on replica.
- Linea and Scroll pass at 31,250 blocks on primary and 7,813 on replica.
- Polygon fails primary because genesis history is explicitly pruned. Replica passes block 0 but returns HTTP 400
  on the 250,000-block range; v1 correctly treats every HTTP error as terminal.
- Base primary returns HTTP 403 at block 0. Replica passes block 0 but returns HTTP 413 on the large range.
- BNB primary returns HTTP 403 at block 0. Replica returns JSON-RPC `-32005 limit exceeded` even for block 0 alone.

The near-identical pattern across four egresses rules out a Mac-only explanation. Polygon/Base expose a range-error
classification issue suitable for a versioned target-free canary repair. BNB has no viable genesis-log route among
the two frozen candidates and requires an official-source endpoint/archive audit before another protocol.

## Scientific and access interpretation

This canary contains no Aave address or topic. Every successful log response was an empty list; unexpected rows
would have been discarded and none occurred. No program count, target event row, transaction, state, account,
price or response was observed. No GPU process or library ran; CUDA was hidden on all four hosts, paid data use was
zero and H20 was excluded.

The FAIL does not estimate program breadth and does not authorize B0 v2. The next allowed work is documentation/
official-source research plus a separately frozen transport-canary repair. The deployment universe, split, cutoff,
program definition, support thresholds and downstream locks remain unchanged.
