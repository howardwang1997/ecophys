# Compound III chain-deployment metadata preflight

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this protocol and
`data/manifests/compound_v3_chain_metadata_preflight_v1.yaml`.

## Question

At one finalized Ethereum block, do the six source-audited Comet proxies and their shared Configurator expose
nonempty proxy/implementation code, valid ERC-1967 implementation/admin slots and the expected non-account
configuration getters? Does the same public endpoint return coherent code and implementation state for the two
oldest source-listed markets at fixed block 17,000,000?

This tests deployment and bounded archive metadata. It does not test accounts, actions, event completeness,
controls, outcomes or continuous archive history.

## Frozen evidence chain

- source result SHA-256:
  `643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11`;
- official Comet source commit: `f766f51583c23acc33b2a7824654ef2029a96804`;
- exact six proxy/base-token/governor/pause-guardian tuples from that source;
- shared Configurator proxy `0x316f...36e3`;
- ERC-1967 implementation/admin slots; and
- Blockscout's documented no-key per-instance Ethereum endpoint.

The four getter selectors were calculated locally from the source signatures using OpenSSL Keccak-256 before any
RPC access: `baseToken()` `0xc55dae63`, `governor()` `0x0c340a24`, `pauseGuardian()` `0x24a3d622`, and
`numAssets()` `0xa46fe83b`. No chain response was preflighted before freeze.

## Exact request plan

The collector issues exactly 61 successful calls in this order:

1. one `eth_chainId` and one `eth_getBlockByNumber("finalized", false)`;
2. for each of six proxies: current proxy code, implementation slot, admin slot, implementation code and four
   frozen `eth_call` getters (48 calls);
3. current Configurator proxy code, implementation slot, admin slot and implementation code (four calls);
4. the header at block 17,000,000; and
5. for mainnet USDC then WETH at that block: proxy code, implementation slot and implementation code (six calls).

Method counts are exactly 24 `eth_call`, one `eth_chainId`, two `eth_getBlockByNumber`, 18 `eth_getCode` and 16
`eth_getStorageAt`. No other method is permitted. Current calls use the explicit finalized block number returned
by the frozen first header, never a drifting `latest` tag.

## Retention boundary

Raw RPC bodies and bytecode are not retained. The artifact keeps request parameters, request/response/result
SHA-256, byte counts, attempts and timestamps, plus decoded public addresses, bounded integers and code SHA-256/
length. This is still provider-mediated data. Blockscout transport terms do not by themselves establish a bulk
chain-data redistribution licence.

Forbidden fields and methods include:

- `userBasic`, `userCollateral`, balances or arbitrary storage keys;
- `eth_getLogs`, transactions, receipts, governance payloads or revert traces;
- supply/borrow totals, prices, oracle calls or liquidations;
- participant actions, post-change responses or candidate effects; and
- paid endpoints, remote workers or GPUs.

## Frozen gates

All twelve are conjunctive:

1. committed source-result bytes match the frozen hash;
2. chain ID is Ethereum mainnet;
3. a valid finalized header later than block 17,000,000 is returned;
4. all six current proxy codes are nonempty;
5. all six current implementation slots and implementation codes are nonempty;
6. all six current admin slots are nonzero addresses;
7. base token, governor and pause guardian match source and `1 <= numAssets <= 24` for every market;
8. Configurator proxy/implementation code and both ERC-1967 slots are nonempty/nonzero;
9. the historical header is exactly block 17,000,000 and predates the finalized header;
10. both historical proxies retain the same immutable proxy code as current and have nonempty historical
    implementation state/code;
11. exactly 61 successful calls use the frozen method counts within 80 attempts and 8 MiB; and
12. the machine access boundary remains metadata-only.

A pass is `PASS_CHAIN_METADATA_AUTHORIZE_EXPOSURE_PROTOCOL_DESIGN_ONLY`. It authorizes only writing—never yet
executing—a pre-event exposure/control protocol. Any failed gate yields
`FAIL_CHAIN_METADATA_KEEP_ACCOUNT_AND_RESPONSE_ACCESS_LOCKED`. No failed market, getter or historical check may be
removed.

## Resource contract

At two requests per second, the expected path is about 31 seconds plus local parsing. Hard caps are 80 HTTP
attempts and 8 MiB. Required paid data, remote-worker and GPU-hours are zero. Both V100s and the RTX 2060 remain
idle.
