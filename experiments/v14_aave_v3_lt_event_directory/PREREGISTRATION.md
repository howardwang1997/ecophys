# Aave V3 Ethereum LT event directory v1

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document,
`data/manifests/aave_v3_ethereum_lt_event_directory_v1.yaml` and
`ecomd/research/aave_lt_event_directory.py`.

## Question and evidential status

This A1a audit asks whether the canonical Aave V3 Ethereum deployment has a source-conforming proxy history and
enough log-level candidates for a later all-candidate liquidation-threshold mechanics audit. It is a zero-account
directory, not an event study. It does not establish authoritative pre-event reserve state, a valid intervention,
an enumerable treated cohort, causality or prediction.

The source and address boundary is frozen before collection. The official `aave-v3-origin` commit is
`cff15de6...`; the official address-book commit is `70e2f303...`. Six exact source files are identified by path,
Git blob and SHA-256. The fixed Ethereum addresses are:

- PoolAddressesProvider `0x2f39...4e9e`;
- Pool proxy `0x8787...a4e2`;
- PoolConfigurator proxy `0x64b7...bb27`; and
- price oracle `0x5458...a0c2`.

The address book declares terminal Pool and PoolConfigurator implementations `0x728a...03cf` and
`0xff42...ce99`. The collector tests those identities at the fixed end block; it does not assume them.

## Frozen window and log plan

The inclusive directory is block 0 through block 25,760,572. The end hash
`0xd2bb...a4ca4` is inherited from the hash-pinned chain-metadata parent. Both Blockscout and PublicNode must return
Ethereum chain ID 1 and identical start/end headers. This is provider replication, not local consensus proof.

The exact 250,000-block partition has 104 inclusive roots per stream. Blockscout is queried in this order:

1. every PoolAddressesProvider log;
2. every PoolConfigurator-proxy log; and
3. only `Upgraded(address)` logs at the Pool proxy.

There are 312 root log calls. A response containing exactly 1,000 rows is discarded and recursively bisected;
single-block saturation fails. The all-Configurator stream is deliberate: a nominal LT row cannot be called
unbundled when another Configurator event is visible in the same transaction.

After the directory is complete, Blockscout alone supplies five fixed-end state calls: the provider's Pool,
PoolConfigurator and oracle getters, plus the two ERC-1967 implementation slots. PublicNode is intentionally not
used for historical state because the earlier Compound audit established that its free endpoint is a historical-
header rather than general archive-state source. This avoids repeating a known transport failure, while leaving
state replication explicitly unresolved.

Finally, one end-block `eth_getCode` call is made for the provider, both proxies and every unique implementation
derived from the complete upgrade histories. Unique implementations are sorted by address and capped at 128.
With no saturated log root, the successful request count is `326 + N_impl`, not a post-outcome choice.

## Strict decoding and version crosswalk

Every log must match the requested address and interval, use canonical identifiers and ABI words, and have
`removed=false`. The provider is not upgradeable, so its complete fixed-source event vocabulary is decoded;
an unknown provider topic fails the audit. Unknown Configurator-version events retain only topic/data hashes,
counts and log identity.

For each Pool component, exactly one matching `ProxyCreated` row is required. Provider transitions from
`PoolUpdated`, `PoolConfiguratorUpdated` or the corresponding `AddressSetAsProxy` ID must form a continuous
old-to-new implementation chain. They must match proxy `Upgraded` rows one-for-one by transaction and new
implementation. Direct `AddressSet` of either component ID is forbidden. The final history entry must equal the
fixed-block implementation slot and official address book, and all inventoried code must be nonempty.

## Provisional directory-candidate rule

For each asset, rows are ordered by block, transaction index and log index. The previous
`CollateralConfigurationChanged` row supplies a **previous emitted configuration**, not authoritative T−1 state.
A provisional row requires:

1. a previous emitted configuration for the same asset;
2. a strict positive LT decrease;
3. unchanged emitted LTV;
4. unchanged emitted liquidation bonus;
5. exactly one total Configurator log in that transaction; and
6. no provider or Pool/Configurator proxy-upgrade log in that transaction.

The support gate is frozen at at least three provisional rows, two distinct assets and three distinct
transactions. This is only enough to justify inspecting every candidate under a new protocol. It does not assign
development or confirmation events. Proposal 204 was exposed during reconnaissance and can never be untouched
confirmation evidence.

Historical T−1/T configuration, frozen state, ConfigEngine `KEEP_CURRENT` normalization, receipt/calldata/call-
path isolation, eMode/oracle/index/pause/grace spillovers, source identity for every active historical
implementation and proposal mapping are all deferred. No threshold may be relaxed after collection.

## Gates and decisions

All sixteen gates are conjunctive: parent/source identities; two-provider chain/header agreement; exact bounded
partitions and strict decoding; no duplicate/conflicting log; complete provider ABI; fixed-end getter, slot and
address-book conformance; complete proxy histories; nonempty code; the frozen support minimum; request/byte caps;
and the zero-account access lock.

A pass is
`PASS_AAVE_LT_EVENT_DIRECTORY_AUTHORIZE_ALL_CANDIDATE_MECHANICS_PROTOCOL_ONLY`. It authorizes only a separately
committed audit of every provisional row using historical configuration, receipts, payloads, call paths and
version-matched source. A failure is
`FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED`. If only support fails while integrity passes,
a new precommitted cross-deployment directory may be designed; Ethereum thresholds or rows cannot be changed.

## Data, compute and retention boundary

Allowed durable data are normalized deployment/configuration/upgrade logs, terminal protocol addresses and code
hashes, request metadata and cryptographic response hashes. Raw RPC bodies are discarded. Transactions, receipts,
calldata, traces, historical reserve calls, accounts, participant actions, liquidations, price values and realized
responses are forbidden.

The hard limits are 2,000 HTTP attempts, 256 MiB of responses, 100,000 normalized logs and 128 unique
implementations at no more than two requests per second across both endpoints. Expected runtime is roughly three
to five minutes on local CPU/network. Paid data, remote workers and GPU-hours are zero. Both V100s and the RTX 2060
remain idle; no H20 is assumed.
