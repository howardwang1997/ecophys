# Compound III chain-metadata v1 result

**Execution date:** 2026-08-16

**Protocol commit:** `ba40179d2a0a18d6c8bc9859d98646a68e5be665`

**Decision:** `INFRASTRUCTURE_FAILURE_UNSUPPORTED_FINALIZED_TAG_NO_CHAIN_METADATA_RESULT`

## What happened

The sealed v1 command was run once from a clean detached worktree after its protocol commit was pushed. Fifteen
combined Compound source-selection/source-metadata/chain-metadata tests passed before collection.

The first logical RPC call, `eth_chainId`, succeeded and returned Ethereum mainnet. The second logical call,
`eth_getBlockByNumber("finalized", false)`, returned JSON-RPC error `Invalid block number` on each of the three
allowed transport attempts. The collector then stopped as required.

This is endpoint-capability failure, not a result on any of the twelve scientific gates. The deployed Blockscout
endpoint did not accept the frozen `finalized` block tag in this run.

## Access and artifacts

- one chain-ID call succeeded;
- three finalized-header HTTP/RPC attempts returned errors;
- no proxy, implementation, storage slot, getter, Configurator or historical-block query was issued;
- no account, participant action, liquidation, price, transaction, receipt, log or response row was opened;
- neither `artifacts/summary.json` nor `artifacts/rpc_response_hashes.json` exists; and
- no paid data, remote worker or GPU was used.

The v1 protocol, command and failure remain immutable. It must not be rerun or repaired in place.

## Consequence

V1 does not pass or fail the chain-deployment metadata question. Account/action/response access, G1 and all model
or GPU work remain locked. A new version may repair only the unsupported snapshot transport while preserving the
endpoint, markets, getters, archive block, caps, access boundary and scientific decision.
