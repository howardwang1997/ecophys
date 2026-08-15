# Uniswap v3 treatment conformance v1 result

**Protocol commit:** `647da77a3987f3009af1c5a9462d574c1ce353d4`

**Contract SHA-256:** `3bf8d454f1c2fa8ef091c4ac4fc00e8d6c9c99d7084e52314a925a121d194279`

**Decision:** `FAIL_RPC_HISTORICAL_STATE_FORBIDDEN_BEFORE_TRANSITION_ACCESS`

## Execution

The first shell launch stopped before Python because the detached sparse checkout did not yet include the new
experiment directory. It made zero RPC calls and is not a consumed scientific run. After adding that exact sparse
path, the clean detached worktree remained at the protocol commit and the runner started once.

The consumed runner reached only:

1. `eth_chainId`, which succeeded and returned Ethereum mainnet chain 1;
2. `eth_getCode(0xf237..., 0x1775a89)`, which returned HTTP 403 on the initial request and both frozen transport
   retries.

The runner then stopped as specified. It did not request the governance transaction, governance receipt,
governance block, either propagation transaction, either propagation receipt or either propagation block. It
therefore did not decode any old/new fee argument or activation class. No LP, swap, liquidity, price or volume
response was accessed.

## Artifacts and resources

No result artifact was produced because failure occurred before the fail-fast collector's write phase. The
terminal error and exact request stage are recorded here; no scientific result is inferred from the 403.

- successful JSON-RPC calls: 1;
- HTTP-403 `eth_getCode` attempts: 3;
- paid data: zero;
- GPU-hours: zero;
- remote workers: zero.

## Disposition

This is a transport-capability failure, not a treatment-conformance failure. Do not label U0 passed or failed on
scientific grounds. A new protocol may change only the bytecode provenance query to `latest`, because this check
does not define the frozen governance or per-pool treatment clocks. It must retain both batch hashes, every gate
and the complete response-access lock. No endpoint or sample may be changed after that repair is executed.
