# Compound III governance-log inventory v1

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document,
`data/manifests/compound_v3_governance_log_inventory_v1.yaml` and
`ecomd/research/compound_governance_inventory.py`.

## Question and evidential status

This D0 audit asks only whether the six frozen Ethereum-mainnet Comet markets contain at least one historical,
log-level candidate for a clean collateral-parameter intervention. It does not estimate exposure, behavior or an
effect. A candidate remains provisional until a separately frozen audit checks the transaction receipt, calldata,
complete governance call path, deployed getters, consensus finality and the contamination window.

The eligible Configurator events are fixed before collection:

- `UpdateAssetBorrowCollateralFactor(address,address,uint64,uint64)`;
- `UpdateAssetLiquidateCollateralFactor(address,address,uint64,uint64)`; and
- `UpdateAssetSupplyCap(address,address,uint128,uint128)`.

The first two preserve the collateral identity while changing one declared risk factor; the third changes one
declared asset cap. `AddAsset`, pause, price-feed, reward, reserve and implementation-only changes are ineligible.

## Frozen window and query plan

The inclusive window is block 14,000,000 through block 25,760,572. Its end hash is frozen from the passing chain-
metadata parent. The collector verifies the start and end headers with PublicNode, then uses Blockscout for logs.

The root partition is deterministic: 250,000 inclusive blocks, yielding 48 intervals per address. It queries:

1. every Configurator log at `0x316f...36e3`; and
2. only the canonical ERC-1967 `Upgraded(address)` topic at each of six frozen Comet proxies.

This is 336 root log calls plus chain ID and two headers, or exactly 339 successful calls when every root response
contains fewer than 1,000 logs. A response with exactly 1,000 logs is treated as saturated: its rows are discarded
and its inclusive interval is recursively bisected. Saturation at one block is a hard failure. No endpoint,
window, address, event, threshold or partition rule may be substituted after this freeze.

## Strict normalization

Every returned row must have the requested address, a block inside its requested interval, canonical block/
transaction/log identifiers, `removed` absent or false, and the exact event ABI shape. Indexed addresses must be
canonical 32-byte address words. Eligible values must fit their declared 64- or 128-bit width. Unknown
Configurator events retain only event identity and hashed data, not decoded payload fields. Raw RPC bodies are
discarded after bounded validation and hashing.

Rows are keyed by `(blockHash, transactionHash, logIndex)`. A duplicate or conflicting row is a hard failure.

## Provisional atomic-candidate rule

For one eligible event to qualify, its transaction must contain all and only the following relevant frozen rows:

1. exactly one eligible Configurator parameter event with `old != new`;
2. exactly one `CometDeployed(proxy, implementation)` for that same proxy;
3. exactly one `Upgraded(implementation)` from that same Comet proxy with a matching implementation;
4. no other Configurator log; and
5. no upgrade from another frozen Comet market.

The operative clock is the proxy `Upgraded` log, not proposal creation or Configurator setter time. The rule is
deliberately conservative, but it still cannot see actions in other contracts or hidden payload/call-path
spillovers. Therefore it creates a candidate, not a valid treatment.

## Gates and decision

All ten gates are conjunctive:

- exact parent hashes and Ethereum chain ID;
- matching fixed-window headers and exact partition plan;
- complete unsaturated leaves and strict log decoding;
- zero duplicates or conflicts;
- at least one provisional atomic candidate;
- request, byte and normalized-row caps; and
- preservation of the governance-log-only access boundary.

A pass is `PASS_GOVERNANCE_LOG_INVENTORY_AUTHORIZE_RECEIPT_PAYLOAD_PREFLIGHT_ONLY`. It authorizes only a new,
separately committed candidate receipt/calldata/call-path/finality protocol. A failure is
`FAIL_GOVERNANCE_LOG_INVENTORY_KEEP_ACCOUNT_AND_RESPONSE_ROWS_LOCKED` and leaves all downstream access locked.

## Access and resource boundary

Permitted durable data are normalized public governance/configuration logs, request parameters, timestamps and
cryptographic response hashes. Forbidden are transaction or receipt rows, calldata, call traces, account state,
participant actions, liquidations, prices/oracles and realized responses. No raw response body is retained.

The hard caps are 2,000 HTTP attempts, 256 MiB of responses and 100,000 normalized logs at at most two requests
per second across both providers. The expected unsaturated runtime is about three minutes and durable storage is
small. Paid data, remote workers and GPU-hours are zero. Both V100s and the RTX 2060 remain idle.

## Known limitations

The fixed end block was previously observed at 64-block depth; that is not consensus finality. Header agreement
across the prior Blockscout artifact and this PublicNode query is provider replication, not a proof of finality.
Provider access and redistribution terms for later bulk account data remain unresolved. This inventory cannot
establish control overlap, an exposure denominator, complete successful actions or any causal response.
