# Compound III supply-cap activation and estimand preflight v2

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document,
`data/manifests/compound_v3_supply_cap_activation_preflight_v2.yaml`,
`ecomd/research/compound_supply_cap_activation_v2.py` and its tests.

## Why v2 exists

V1 was executed once at protocol commit `1dfdecf47d60b3f78a1076d2a09ed60f7ad5fc7f`. After two chain-ID and
seven Blockscout source-metadata successes, PublicNode returned HTTP 403 on all three permitted attempts for the
first historical `eth_getCode`. It stopped before any historical code result, configuration getter or aggregate
total and recorded `INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT`. The immutable failure and result are
hash-pinned parents. V1 will not be changed or rerun.

The [PublicNode Ethereum page](https://ethereum.publicnode.com/) advertises archive data behind a separate
“Get Archive Access” action. No authenticated PublicNode archive access is available in this free-data protocol,
so the public endpoint is no longer treated as a historical-state provider. The
[Blockscout ETH RPC reference](https://docs.blockscout.com/devs/apis/rpc/eth-rpc) explicitly documents per-instance
`eth_call` with a block parameter and requires no API key. D0b already completed fixed historical Blockscout code
and configuration calls. This evidence is the transport basis; no candidate address was probed while designing
v2.

## Narrow repair boundary

V2 changes only transport and partial-failure durability:

1. Blockscout is the sole historical configuration/aggregate-state provider;
2. PublicNode remains only for chain identity and historical block headers;
3. both providers return every lookback header, so the Blockscout state height is anchored to an identical
   canonical block hash and timestamp;
4. eight redundant PublicNode historical code calls and four redundant post-event configuration calls are
   removed—D0b's code/T state and v2's source-deployed-bytecode hashes remain pinned; and
5. a v2 failure artifact retains all completed normalized source and completed-candidate evidence, in addition to
   every request/attempt hash, without raw bodies.

V2 does not pretend that equal headers provide independent state replication. Configuration and aggregate values
remain one-provider evidence without locally verified Ethereum state proofs. This limits what a pass means and is
reported in every artifact.

All outcome-relevant rules inherit byte-for-byte from v1: four candidates in parent order, seven old/new source
implementations, exact ABI and source-enforcement markers, six block offsets, contemporaneous caps, strict integer
decoding, exact T−1 saturation, diagnostic-only 90/95/99% utilization, no post-event total and all zero-account
access locks. Candidate replacement, threshold changes and endpoint substitution remain forbidden.

## Fixed source and state evidence

All seven implementation source records are requested again because v1's failure artifact retained only their
response hashes, not normalized conformance. Each must be fully verified unchanged Solidity, match the parent
runtime-bytecode SHA-256, expose exact `totalsCollateral`/`getAssetInfoByAddress` ABI, and contain every normalized
storage/cap-enforcement marker. Only compiler, ABI, bytecode and source-file inventory hashes and check booleans are
retained.

For each candidate and each fixed offset `1`, `300`, `1,800`, `7,200`, `21,600`, `50,400` from event block `T`:

- Blockscout and PublicNode headers must agree exactly on number, hash and timestamp;
- Blockscout returns the contemporaneous `getAssetInfoByAddress(asset)`; and
- Blockscout returns `totalsCollateral(asset)` as exactly two `uint128` ABI words with zero reserved field.

The T−1 configuration must reproduce D0b's old asset getter. D0b's hash-pinned T record must contain the declared
new cap. At every snapshot, aggregate total must be no greater than its contemporaneous cap. No account, action,
log, trace, price, liquidation or event/post-event aggregate state is queried.

## Decisions remain unchanged

All ten v2 integrity gates are conjunctive. They cover the immutable v1 failure and D0b/source ancestry, mainnet
identities, seven source matches, 24 two-provider header identities, Blockscout configuration/aggregate
conformance, all four complete candidates, exact request order, resource caps and access locks.

- Integrity plus at least one exact `totalSupplyAsset == supplyCap` at T−1 returns
  `PASS_EXACT_CAP_ACTIVATION_AUTHORIZE_MARKET_LEVEL_D1B_DESIGN_ONLY`.
- Integrity with no exact T−1 saturation returns
  `FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE`.
- Source/state/integrity nonconformance returns
  `FAIL_SOURCE_OR_STATE_CONFORMANCE_KEEP_ALL_D1_ROWS_LOCKED`.
- A collection exception returns only
  `INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT_V2`.

A pass still licenses only a separately frozen market-level collateral-flow D1b design. The account-level route is
retired for every outcome because would-be blocked suppliers have no pre-event enumerable denominator. Near-cap
diagnostics cannot authorize a pass.

## Exact request and resource contract

The no-retry vector has 105 successful operations:

- 98 JSON-RPC calls: two `eth_chainId`, 48 `eth_getBlockByNumber` and 48 `eth_call`;
- seven Blockscout verified-source REST calls;
- provider counts of 73 Blockscout RPC, seven Blockscout source REST and 25 PublicNode execution.

Every ordered provider, label, method/parameters or path is checked. The global rate is one request per second,
with two retries, 384-attempt, 128-MiB response, 2,048-source-file and 64-MiB source-text caps. Success writes three
artifacts. Failure writes only a bounded artifact containing the request/attempt ledger and completed normalized
evidence, explicitly marked incomplete and non-scientific.

This is local CPU/network work using free public data. The throttle lower bound is 1.75 minutes; budget 15 minutes.
No external worker or GPU is needed, and both V100s and the RTX 2060 remain idle.
