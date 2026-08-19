# Aave Agent Guardrail Multichain Holdout D0 Freeze — 2026-08-20

## Freeze statement

This protocol is frozen before any `eth_getLogs`, explorer-log query, Risk Oracle proposal value, AgentHub event
value or RangeValidation event value has been read on the nine non-Ethereum deployments below. Before the freeze,
only pinned source/address files, public RPC documentation, chain IDs, block headers and contract-code existence
were inspected. Those source-only probes cannot reveal proposal support, execution matching or market response.

The Ethereum pilot remains a formal stop. Its rows cannot be reclassified, pooled into this holdout or used as a
confirmation sample. The only pilot-derived design correction is temporal risk-set eligibility: an action cannot
be at risk of AgentHub execution before its unique agent is registered and initialized. This correction is now
prospective on an untouched panel.

Executable contract: `configs/empirical_physics/aave_agent_guardrail_holdout_d0_v1.yaml`.

## Fixed panel and time anchors

The panel is the complete non-Ethereum set named in the pinned Aave Risk Agents `Deploy.s.sol`: Arbitrum,
Avalanche, Base, BNB, Gnosis, Optimism, Polygon, Plasma and Linea. No chain may be removed because it is inactive,
inconvenient or yields an unfavorable result.

All windows begin at the first block whose timestamp is at least `2025-11-24 00:00:00 UTC`. For each chain, the
preceding block was checked to have an earlier timestamp. This calendar rule is common across chains and precedes
the source-verified deployment batch; it is not selected from event activity. Each endpoint is fixed at the exact
head observed during the source-only audit:

| Chain | ID | From block | To block | Agent types fixed by source |
|---|---:|---:|---:|---|
| Arbitrum | 42161 | 403,441,737 | 496,241,730 | supply cap, borrow cap |
| Avalanche | 43114 | 72,475,069 | 93,199,822 | supply cap, borrow cap |
| Base | 8453 | 38,576,527 | 50,185,771 | supply cap, borrow cap |
| BNB | 56 | 69,254,723 | 116,889,115 | supply cap, borrow cap |
| Gnosis | 100 | 43,299,823 | 47,809,063 | supply cap, borrow cap |
| Optimism | 10 | 144,171,812 | 155,781,056 | supply cap, borrow cap |
| Polygon | 137 | 79,418,684 | 92,303,909 | supply cap, borrow cap |
| Plasma | 9745 | 7,011,827 | 30,220,344 | discount rate, E-Mode |
| Linea | 59144 | 25,957,319 | 31,762,909 | interest rates |

Every chain ID, AgentHub, RangeValidationModule and Edge Risk Oracle address must match the pinned address book.
The two endpoint block hashes and all addresses are part of the executable contract. The source audit found
nonempty AgentHub bytecode at every end anchor. Archive-capable source-only probes independently located contract
creation on Gnosis, Optimism, Polygon, Plasma and Linea within 26 minutes on 2025-11-25, consistent with one
deployment batch; this timing is not an event or activity screen.

Official public endpoint documentation is recorded for
[Arbitrum](https://docs.arbitrum.io/arbitrum-essentials/reference/node-providers),
[Avalanche](https://build.avax.network/docs/api-reference/data-api/data-vs-rpc),
[Base](https://docs.base.org/base-chain/api-reference/rpc-overview),
[BNB](https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/),
[Gnosis](https://docs.gnosischain.com/about/networks/),
[Optimism](https://docs.optimism.io/op-mainnet/network-information/connecting-to-op),
[Polygon](https://docs.polygon.technology/pos/reference/rpc-endpoints),
[Plasma](https://www.plasma.org/docs/plasma-chain/network-information/connect-to-plasma) and
[Linea](https://docs.linea.build/network/build/connect). BNB's official public endpoint documents that
`eth_getLogs` is disabled, so it is an anchor reference rather than a formal log transport.

## Allowed information

D0H may retrieve only:

1. the pinned official source and address-book files;
2. the 14 allowed AgentHub configuration/registration/injection event families;
3. DefaultRangeConfigSet and MarketRangeConfigSet;
4. ParameterUpdated from the address-book Edge Risk Oracle, after registration identity is verified;
5. canonical block, transaction and log provenance needed to order and validate those records.

It may not retrieve Pool state, balances, utilization, rates, prices, positions, liquidations, user transactions
or market-response windows. Risk Oracle `previousValue` remains only a prior oracle proposal and cannot substitute
for contemporaneous protocol state. D0H therefore tests delay-boundary action support only; amplitude/range replay
remains a later D1 question.

## Prospective risk set

A proposal is eligible only when all of the following occur earlier in canonical block/transaction/log order:

1. at least one AgentRegistered maps its chain, Risk Oracle and update-type hash to an agent;
2. the registered Risk Oracle equals that chain's pinned Edge Risk Oracle;
3. AgentAddressSet, AgentEnabledSet(true), ExpirationPeriodSet and MinimumDelaySet have initialized that agent.

Pre-activation and never-registered proposals remain in an exclusion ledger with a reason; they do not enter any
support or terminal-classification denominator. Exactly one initialized prior registration is required for an
unambiguous source. If multiple initialized registrations match, the proposal has entered the risk set but remains
in the denominator as an ambiguity failure. This distinction repairs left truncation without hiding later data
loss.

## Dependence and batch rule

The off-chain proposer can synchronize many markets or chains. Treating each emitted proposal as independent
would be pseudoreplication. Sort all eligible holdout proposals by oracle timestamp and canonical identity. Join
adjacent proposals separated by at most 120 seconds into one connected action batch, even if chain or update type
differs. The batch ID is the SHA-256 digest of its sorted canonical proposal identities. This conservative rule was
fixed from the separated batch cadence visible in the excluded Ethereum pilot, before any holdout event query.

Report both row and batch counts. Later inference must cluster by batch. A qualifying delay boundary is never
pooled across chains, agents or delay epochs. At the batch level, its score is the median margin among rows in the
same boundary and batch.

## Matching and terminal classes

Exact injection matching requires chain, Risk Oracle/agent identity, update type, update ID, market and byte-exact
proposed value. Terminal classes and time-varying expiration follow the Ethereum D0 implementation. The result
must separately report raw proposals, exclusions, eligible rows, batches, exact injections, overwritten, expired,
disabled/offboarded, right-censored and post-activation ambiguous rows.

## Hard pass/stop gates

All global gates must pass:

- at least 30 eligible proposal rows, 20 exact injections, two update types, five chain-market pairs, three
  chain-agent pairs and three represented chains;
- at least ten independent action batches;
- at least ten resolved non-immediate rows spanning at least five batches;
- at least 90% terminal classification among eligible non-right-censored rows.

At least two chain-specific boundaries on at least two chains must each satisfy:

- 20 row scores, five on each side and five within 25% on each side;
- ten batch-median scores, three on each side and three within 25% on each side;
- neither row-level exact-zero bunching (at least five and at least 50%) nor batch-level exact-zero bunching (at
  least three and at least 50%).

Any failure stops before exact state replay and before outcomes. Low activity cannot be rescued by dropping a
chain, pooling heterogeneous boundaries, adding Ethereum pilot rows or simulating rejected actions. A pass grants
permission only to freeze and run D1 exact validation replay.

## Transport qualification

Transport is replaceable, but data identity is not. After this freeze, each chain must pass chain ID and both
anchor-hash checks. At least one nonempty AgentHub shard must have the same complete canonical
`(blockHash, transactionHash, logIndex)` set from two listed sources, or one RPC plus an independent explorer API.
Qualify transports on 10,000-block shards, with at most 14 topics and 0.75 seconds between requests to one
endpoint. Formal extraction then starts from a chain-specific span corresponding to approximately seven UTC days
under the frozen header rate. Explicit range/timeout/result-size failures recursively split that span without
changing the block union; this prevents short-block-time chains from requiring tens of thousands of knowingly
redundant requests. No API key, paid endpoint, IP fan-out or raw RPC retention is allowed.

## Resources and interpretation

D0H is capped at 50 CPU core-hours, 5 GB retained derived data, zero paid-data spend and zero GPU hours. The two
V100 32 GB workers and RTX 2060 remain available for other justified work; this audit cannot benefit from them.
Future planning excludes H20.

Even a pass is not an NMI/NCS result. It would show that a prospectively defined, multi-deployment action ledger
has sufficient real variation to justify exact mechanism replay. The paper-level claim still requires a valid
treatment definition, real market outcomes, interference-aware inference, independent mechanism transfer and a
frozen future confirmation.
