# Compound III all-candidate mechanics preflight v1 result

**Execution date:** 2026-08-16

**Protocol commit:** `2ee8a87442b6e5a912354362bddcef572876eb59`

**Decision:** `INFRASTRUCTURE_FAILURE_PUBLICNODE_DEBUG_TRACE_UNAVAILABLE_NO_CANDIDATE_MECHANICS_RESULT`

## What happened

The sealed command was run once from a clean detached worktree after the protocol commit was pushed and confirmed
on the remote branch. The four parent hashes reproduced, all 14 candidates re-derived exactly, the three output
paths were absent, and 35 bounded Compound tests plus Ruff, formatting and strict mypy passed before collection.

The program completed the ten logical operations preceding the first call trace: chain ID, execution-finalized
header, Beacon finality update, its explicit execution-header replica, two contamination-neighbor headers, and the
first candidate's transaction, receipt and two-provider block headers. PublicNode then returned JSON-RPC error
`-32601` with message `the method debug_traceTransaction does not exist/is not available` on each of the three
allowed attempts for candidate `borrow_cf_22273296_0080d1f7`. The collector stopped as frozen.

This is an endpoint-capability failure, not a pass or fail on any candidate-mechanics scientific gate. No endpoint
was substituted and v1 must not be rerun or repaired in place.

## Access and artifacts

- the first candidate's public governance transaction and receipt were opened as authorized;
- no successful call-trace result was returned;
- no ERC-1967 slot, implementation-code or asset-getter query was issued for any candidate;
- no later candidate transaction or receipt was queried;
- no account state, participant action/trace, liquidation, price/oracle or realized-response row was opened;
- no paid data, remote worker or GPU was used; and
- `artifacts/summary.json`, `artifacts/candidates.json` and `artifacts/rpc_response_hashes.json` do not exist.

Because v1 writes artifacts only after a complete collection, the successful responses' hashes, bytes and retry
counts were not durably emitted. The terminal failure proves that the ten earlier logical operations completed and
that all three trace attempts returned `-32601`, but it is not a substitute for a partial response ledger. A future
version must make bounded failure evidence durable before execution.

## Consequence

V1 yields no mechanics-conforming candidate set and authorizes no D1 design or acquisition. `G1`, participant rows,
responses and all GPU work remain locked. A new protocol version may repair only the trace transport and failure-
artifact behavior while preserving the 14 candidates, their order, every scientific check, access boundaries and
resource caps. It must be committed and pushed before any new capability request or collection.
