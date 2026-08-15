# Uniswap v3 fee-expansion treatment conformance v2

**Frozen:** 2026-08-15 10:00:59 UTC

**Role:** transport-only repair of U0 v1; historical mechanism metadata only

**Outcome lock:** unchanged—no LP action, swap, liquidity, price, volume or post-treatment response access

## Parent failure

V1 at commit `647da77a3987f3009af1c5a9462d574c1ce353d4` passed `eth_chainId`, then the public RPC endpoint returned HTTP
403 for all three allowed historical `eth_getCode` attempts. It stopped before any governance or propagation
transaction/receipt call and before old/new fee-transition decoding. See `RESULTS_V1.md`.

## Sole repair

V2 changes only `source.runtime_bytecode_block` from frozen block `24,599,177` to block tag `latest`. The bytecode
query is only a deployed-code provenance gate against the already frozen 7,266-byte SHA-256. It is not used as a
treatment clock, pool selector, covariate or outcome.

Everything scientific remains byte-identical to v1:

- governance proposal, execution transaction, block and owner transition;
- the two ordered 500-pool propagation transaction hashes;
- calldata/event pairing and allowed fee transitions;
- activation-count thresholds;
- no-replacement rule and non-representative conformance-prefix claim;
- reconnaissance disclosure and every data-access prohibition.

The v2 manifest pins the v1 contract hash, protocol commit, exact failure stage and sole repaired field. If the
latest-code query fails, v2 stops; do not substitute another RPC endpoint inside this protocol.

## Requests and outputs

On successful transport, the runner makes exactly 11 successful read-only RPC calls: chain ID, latest runtime
code, one governance transaction/receipt/block triple and two propagation transaction/receipt/block triples.
Outputs go only to `artifacts_v2/` and refuse overwrite.

All v1 scientific gates remain conjunctive. A pass unlocks only design of a separately committed pre-treatment
U1 support/identity audit. A failure blocks all LP-response access. Paid data, remote workers and GPUs remain
unauthorized.
