# Uniswap v3 fee-expansion treatment conformance v1

**Frozen:** 2026-08-15 09:27:12 UTC  
**Role:** historical development; mechanism/treatment metadata only  
**Outcome lock:** no LP action, swap, liquidity, price, volume or post-treatment response event may be opened

## Question

Can Proposal 94 supply an exact M2 treatment clock and a sufficiently large deterministic development frame
without relying on the proposal prose, a commercial indexer or realized LP responses?

This is not an effect study. It tests whether the on-chain transition itself is reconstructible. Earlier
mechanism reconnaissance accessed the governance transaction and the first two direct propagation transactions,
including calldata lengths and receipt event-type counts. That access established two 500-pool calls with 500
pool and 500 adapter events each. It did not decode or retain the old/new fee arguments, classify activation
states, or access any LP-response event. This discovery is disclosed, so the frame is neither pristine nor
representative. The activation-count gates were fixed before old/new fee-transition decoding.

## Frozen authority order

1. Ethereum block header, transaction calldata and successful receipt;
2. verified deployed bytecode/source;
3. proposal and Seatbelt source as explanatory metadata only.

The proposal description names `0x3e40...`, but the Seatbelt calldata constant and the factory's executed
`OwnerChanged` event name `0xf237...`. The experiment must use the latter. The displayed Agora execution time
also differs from the execution block timestamp; the block header is authoritative.

## Exact frame

- Governance proposal: on-chain ID 94.
- Execution transaction:
  `0xd6c4c93eaaac3b6cf144853655f91b326c5e3019b022baeec08eaf74c8af9833`.
- Factory owner transition: `0x5E74...` to `0xf237...`.
- Propagation transactions, in chain order:
  1. `0x0c49a2013d5c008bf2f07c939071753c3dbcbfefa43265095c55d0e8a36f849b`;
  2. `0x95b0b34aad5322027abe65c4f35468809039f6648798d8905a9de918fe7d9f65`.
- Each must be a successful direct `batchTriggerFeeUpdateByPool(address[])` call containing exactly 500 unique
  pool addresses.
- No transaction, pool or block may be replaced.

## Reconstruction

For every calldata pool, the receipt must contain exactly one pool-level
`SetFeeProtocol(uint8,uint8,uint8,uint8)` and exactly one adapter-level
`FeeUpdateTriggered(address,address,uint8)`. Their pool order must equal calldata order. The pool event must occur
first, and its new token-side denominators must equal the packed adapter fee.

The ledger classifies each row as:

- `activated_from_zero`: `(0,0)` to a nonzero fee;
- `reapplied_same_fee`: old and new fees equal;
- `changed_nonzero_fee`: another nonzero transition; or
- `disabled_to_zero`.

This classification is exact contract state transition metadata. It is not LP behavior or a causal outcome.

## Gates

All gates are conjunctive:

1. the governance receipt is successful and contains exactly the frozen factory owner change;
2. both propagation hashes, blocks, callers, selector and 500-address calldata lengths match;
3. all 1,000 calldata addresses are unique across both batches;
4. all 1,000 rows have one-to-one pool/adapter event pairing in calldata order;
5. every new fee is symmetric and exactly `(4,4)` or `(6,6)`;
6. at least 100 pools change from `(0,0)` to nonzero;
7. at least 10 newly activated pools occur under packed fee `0x44` and at least 10 under `0x66`;
8. deployed runtime code is 7,266 bytes and matches frozen SHA-256
   `37bd11b8fd174245af62b4a67691566c2df3d544d12b57cdcf5ebc1039f66bef`.

Pass permits only a separately frozen **pre-treatment** pool/activity/identity coverage design. It does not permit
post-treatment response access. Failure blocks LP-response collection; thresholds or batches cannot be changed on
the same frame.

## Data and compute

The runner makes read-only calls for chain ID, runtime code, the governance transaction/receipt/block and the two
propagation transactions/receipts/blocks. It stores normalized treatment rows and hashes of RPC envelopes, not a
commercial dataset. Expected volume is well below 20 MB.

- paid data: zero;
- local CPU: under one core-hour;
- GPU: zero hours;
- V100/RTX2060: intentionally idle;
- H20: excluded.

## Claim boundary

A pass supports: “the first deterministic 1,000-pool propagation prefix exposes exact old/new protocol-fee
transitions and per-pool treatment clocks.” It does not support “all pools were activated,” representativeness,
LP adaptation, welfare, liquidity loss, causal identification or a Nature-level result.
