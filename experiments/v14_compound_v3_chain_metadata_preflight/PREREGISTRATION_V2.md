# Compound III chain-deployment metadata preflight v2

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document and
`data/manifests/compound_v3_chain_metadata_preflight_v2.yaml`.

## Transport-only repair

V1 stopped before any contract query because the frozen Blockscout endpoint returned `Invalid block number` for
the `finalized` tag on all three allowed attempts. V2 keeps that endpoint and every scientific field, market,
getter, archive block, access prohibition, cap and downstream lock. It changes only the current-state snapshot:

1. read the `latest` header once;
2. derive `snapshot_number = latest_number - 64` locally;
3. read that explicit numeric block header once; and
4. use the returned explicit snapshot block number for every current code, storage and getter query.

The 64-block lag is a bounded confirmation-depth convention. It is **not** Ethereum consensus finality and must
not be called finalized. The latest head and snapshot come from one provider. Any later intervention clock or
participant-response study requires a separately frozen consensus-finality and provider-replication check.

## Exact request plan

The collector issues exactly 62 successful calls in this order:

1. one `eth_chainId`;
2. `eth_getBlockByNumber("latest", false)` and then
   `eth_getBlockByNumber(hex(latest_number - 64), false)`;
3. for each of six frozen Comet proxies: snapshot proxy code, implementation slot, admin slot, implementation
   code and four non-account getters (48 calls);
4. snapshot Configurator proxy code, implementation slot, admin slot and implementation code (four calls);
5. the header at fixed block 17,000,000; and
6. for mainnet USDC then WETH at that block: proxy code, implementation slot and implementation code (six calls).

Method counts are exactly 24 `eth_call`, one `eth_chainId`, three `eth_getBlockByNumber`, 18 `eth_getCode` and 16
`eth_getStorageAt`. No other method is permitted. The success-count gate is exactly 62; hard caps remain 80 HTTP
attempts and 8 MiB.

## Evidence and access boundary

The source-result SHA-256 remains
`643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11`, pinned to official Comet source commit
`f766f51583c23acc33b2a7824654ef2029a96804`. The six proxies, expected base tokens/governor/pause guardian, shared
Configurator, exact ERC-1967 slots, four getter selectors and archive pair/block are unchanged from v1.

Raw RPC bodies and bytecode are discarded after bounded decoding and hashing. Forbidden access remains:

- account mappings, balances and arbitrary storage;
- logs, transactions, receipts, governance payloads and revert traces;
- totals, prices, oracles and liquidations;
- participant actions and realized responses; and
- paid endpoints, remote workers and GPUs.

## Frozen gates and decision

The same twelve conjunctive checks apply, except the unsupported finalized-header gate is replaced by a
confirmed-snapshot-header gate requiring:

- both latest and explicit snapshot headers exist;
- `latest_number - snapshot_number == 64`;
- snapshot is later than block 17,000,000; and
- snapshot time is not later than latest-head time.

Every other current code/slot/getter, Configurator, historical header/state, request-cap, source-hash and access
gate is unchanged. A full pass is `PASS_CHAIN_METADATA_AUTHORIZE_EXPOSURE_PROTOCOL_DESIGN_ONLY`; any failed gate
is `FAIL_CHAIN_METADATA_KEEP_ACCOUNT_AND_RESPONSE_ACCESS_LOCKED`. A pass permits writing a separate exposure and
control protocol only—not acquiring account/action/response rows and not launching a model or GPU job.

No endpoint, depth, market, getter or historical block may be substituted after execution.

## Resource contract

At two requests per second, the expected path is about 31 seconds plus local parsing. Durable output is two small
JSON artifacts. Required paid data, remote-worker and GPU-hours are zero; both V100s and the RTX 2060 remain idle.
