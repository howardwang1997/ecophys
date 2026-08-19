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

Initial scientific freeze: `configs/empirical_physics/aave_agent_guardrail_holdout_d0_v1.yaml`. Current executable
transport amendment: `configs/empirical_physics/aave_agent_guardrail_holdout_d0_v2.yaml`. Version 2 changes only
transport and qualification metadata after outcome-blind policy-event diagnostics; every chain, block union,
event family, eligibility rule, gate and stop rule remains identical to version 1.

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

Each initialization event must itself follow the matching registration; an earlier event with the same numeric
agent ID cannot activate a later registration. This is a causal-order clarification, not an activity-dependent
screen.

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
under the frozen header rate, unless a transport-only amendment records a smaller explicit free-provider cap.
Explicit range/timeout/result-size failures recursively split that span without changing the block union; this
prevents short-block-time chains from requiring tens of thousands of knowingly redundant requests. No API key,
paid endpoint, IP fan-out or raw RPC retention is allowed.

## Implementation lock before event access

The formal implementation is `scripts/audit_aave_agent_guardrail_holdout_d0.py`. Its `chain` mode re-verifies the
failed Ethereum pilot digest and exclusion, all five pinned source repositories, 26 source/address files, chain
anchors and nonzero AgentHub code before querying an allowed event. It then qualifies two listed transports on
one identical nonempty 10,000-block Hub shard. Its repository-external checkpoint contains only decoded allowed
policy events and canonical headers and is bound to the code SHA, config digest, source SHAs, chain, anchors and
formal RPC. The `merge` mode accepts all nine fixed chain artifacts or none and applies the frozen global gate
once.

The runner and core are covered by tests for source-independent pilot binding, exact log identity and duplicate
rejection, checkpoint digest/identity/blinding, topic partitioning, nonzero contract code, causal activation,
cross-chain connected batching, row/batch boundary support and the immutable contract. Ruff, strict mypy and the
58-test complete Aave suite pass. The scientific implementation choices were fixed before the first
non-Ethereum event query; later changes are explicitly recorded transport repairs, and none changes a sample,
threshold or stop rule.

The first post-freeze qualification attempt produced no chain artifact or checkpoint and exposed three transport
facts: Avalanche's official endpoint caps a request at 2,048 blocks, Polygon dRPC requires a nominal 10,000-block
shard to be subdivided, and BNB's initial candidates did not both provide historical state. The fixed 10,000-block
qualification *union* is therefore retained while explicit provider cap errors may recursively subdivide its RPC
requests. Chain ID and both hashes are verified on the fixed anchor RPC. The first archive-capable endpoint in the
fixed anchor/formal-candidate order separately verifies nonzero Hub code at the frozen endpoint; each of the two
log transports independently verifies chain ID and both hashes, then must return the identical complete
log-identity set. This avoids requiring historical state from either a fixed header anchor or a service used only
for logs.

The transport-only candidate list adds the documented public
[Avalanche dRPC](https://drpc.org/docs/avalanche-api) and public archive-capable
[BNB OnFinality](https://documentation.onfinality.io/support/bnb-chain) endpoints. Both passed source-blind
chain/hash/code probes before inclusion. No chain, block, event family, eligibility rule, batch definition,
scientific threshold or stop rule changed.

The next clean attempt confirmed why the state witness must be separate: the fixed Arbitrum and BNB anchors still
returned both exact headers but had already pruned the frozen endpoint's state. An all-chain header/code-only
preflight found an archive-capable witness for every chain: Arbitrum Blockscout, BNB OnFinality, and each other
chain's first fixed candidate or anchor. No event value was used to select a witness. The failed attempt again
wrote no artifact or checkpoint.

The third clean attempt from `e9e4b3dc9` passed the independent state-witness check on all nine chains, then
stopped without a chain artifact. BNB OnFinality repeatedly rate-limited log queries and the remaining listed
services did not yield two qualifying log transports. Linea's formal scan returned the explicit provider error
`range 151199 exceeds limit of 10000`, whose wording was not yet recognized as a range cap. The only checkpoint
found afterward was a Gnosis checkpoint bound to an older code SHA and is therefore unusable. All current-SHA
processes were terminated; no partial result can be merged.

The BNB recovery is a transport-only, auditable amendment. Pinned Aave proposal history identifies the first
multichain risk-agent registration deployment without inspecting a proposal value or market outcome. Historical
`getAgentCount()` state on the frozen Hub is zero at block 75,187,733 and two at the consecutive block
75,187,734. This fixes, before a formal rescan, the aligned 10,000-block qualification shard
75,184,723--75,194,722. It is the unique frozen grid shard containing the first positive registration state;
earlier grid shards cannot contain a registered-agent event under the contract state.

The public [SQD Portal](https://docs.sqd.dev/en/portal/evm/examples/query-logs) returned 30 allowed Hub events on
that complete shard. Two independently operated, no-key transports—[Nodeflare](https://nodeflare.app/chains/bnb)
and [Pocket](https://docs.pocket.network/developers/supported-chains/)—each returned the same 30 canonical
identities, with SHA-256
`2d50fe7fd5bcb03ca93f6783a94047a9664c28daf21acfc490e168f5591985a4`. The executable contract freezes the shard,
digest and exact consecutive state transition. Nodeflare is the first formal candidate, Pocket is the second
identity source, and OnFinality remains the archive state witness. Because Nodeflare's public tier explicitly
caps one log query at 10,000 blocks, BNB formal extraction now uses 10,000-block requests over the exact original
union. A source-blind preflight on the first frozen BNB interval, blocks 69,254,723--69,264,722, returned a valid
empty log set rather than a pruned-history error, so the primary is not limited to the later qualification shard.
Linea recognizes only the observed phrase `exceeds limit of` as splittable; the generic `limit exceeded` message
remains non-splittable because a tested provider returned it even for one block. No chain, block union, event
family, sample rule, threshold or stop rule changed.

The next clean attempt from `e7bf9a015` exposed a reproducibility failure in Pocket's public routing before any
BNB artifact or checkpoint was written: the service no longer returned the frozen start anchor from the V100
egress, and the same absence was reproduced from the RTX 2060 host and Mac. A transient earlier response is not
sufficient evidence. One candidate that passed both headers, FastNode, silently returned zero events on the
30-event shard and is explicitly rejected by the identity gate. This is exactly why endpoint availability and
log completeness are separate requirements.

The current ChainList registry supplied two further source-blind candidates. Sentio and bloXroute each passed
chain ID, both anchor hashes and all 30 identities from Mac, but only bloXroute was usable from a designated
compute node. On the RTX 2060 host's single egress, Nodeflare returns the exact 30-event digest, the documented
public [bloXroute BSC Protect RPC](https://docs.bloxroute.com/introduction/protect-rpcs/bsc-protect-rpc) returns
the same digest, and OnFinality independently verifies Hub code plus the consecutive zero-to-two state
transition. bloXroute documents the exact endpoint and a three-request-per-second public limit; the frozen
0.75-second pacing is below it. Because bloXroute routes to a nearby regional server, BNB must run entirely from
the one preflighted RTX-host egress—no cross-IP identity assembly is permitted.

The `e7bf9a015` attempt also demonstrated the clean-SHA fleet launcher. Its first invocation failed locally at
module import and made no RPC request; the corrected `python -m` invocation completed Gnosis and made progress on
other chains. Once the BNB reference changed, every old-SHA result and checkpoint became deliberately
unmergeable. All remaining processes were terminated by exact PID and their files retained as attempt
provenance. The complete nine-chain panel must restart from the next single clean SHA.

## Outcome-blind transport amendment v2

The clean version-1 run from `ac99559212dd0a0943c669b5d0981908e44d81e8` was a transport diagnostic, not a
holdout result. Arbitrum, Gnosis and Linea completed, while Base failed three independent qualification attempts
and the slower public transports made several other full scans impractical. Only allowed AgentHub policy events,
contract state witnesses and block headers were inspected. No pool state, price, utilization, liquidation,
position, user transaction or response window was queried. Because the diagnostics informed transport choices,
all version-1 artifacts and checkpoints are permanently diagnostic-only and cannot be pooled with version 2.

The following fixed qualification shards now cover all nine chains. Each canonical identity digest was reproduced
by at least two independently operated public sources before it was written into version 2. The event count is a
transport-completeness checksum, not a sample-selection criterion; formal extraction still covers every original
frozen block.

| Chain | Fixed qualification blocks | Events | Canonical identity SHA-256 | Fast primary | Independent reference |
|---|---:|---:|---|---|---|
| Arbitrum | 421,201,737--421,211,736 | 48 | `653120b4...ecc69bda` | Tenderly | Blockscout |
| Avalanche | 75,715,069--75,725,068 | 45 | `8ab51afa...311fca` | Tenderly | official Avalanche RPC |
| Base | 40,786,527--40,796,526 | 38 | `31b2e41e...12090` | Tenderly | official Base RPC |
| BNB | 75,184,723--75,194,722 | 30 | `2d50fe7f...985a4` | Sentio | bloXroute |
| Gnosis | 44,149,823--44,159,822 | 30 | `50c3b3df...3f52a` | Tenderly | Blockscout |
| Linea | 27,827,319--27,837,318 | 12 | `5fe9ba21...293ff0` | Tenderly | official Linea RPC |
| Optimism | 146,381,812--146,391,811 | 32 | `5f54a007...50fb54` | Tenderly | official Optimism RPC |
| Plasma | 11,441,827--11,451,826 | 30 | `2968ed41...f65b` | Sentio | official Plasma RPC and thirdweb |
| Polygon | 81,628,684--81,638,683 | 38 | `e93d2393...ba2b0b` | Tenderly | Sentio and dRPC |

Tenderly can return the tested dense formal ranges in one request on seven chains; Sentio can do so on Plasma.
Sentio's BNB endpoint enforces a 10,000-block cap but completed six consecutive test shards in 0.35--0.93 seconds
per shard, reducing the projected three-stage scan from roughly two days to roughly three hours. The version-2
configuration digest is `93be07281ff57e853d32f5caadc2f08d9a38e9e91728c35c8126a22aab25246c`.

This speedup concentrates seven primary scans at one provider. Therefore a version-2 scientific pass is not yet
permission to read market outcomes. Before D1 or outcome access, the complete decoded event union on every chain
must be independently reproduced from a non-primary provider and compared by canonical event identity and decoded
payload. A mismatch is a transport failure and stops the route; it cannot be resolved by choosing the favorable
provider. All nine primary artifacts must also come from one clean repository SHA and the one version-2 digest.

### Version-2 execution and first full-union audit

Version 2 was committed and pushed at clean SHA `c9ab42a64295ec6bd3ea6868050cb9ca4dd05d15`. Exact-SHA roots on
the two V100 hosts and RTX 2060 host launched all nine chains with CUDA hidden. Eight primary artifacts have
completed and passed independent canonical-digest, SHA, config, blinding and compute checks: Arbitrum, Avalanche,
Base, Gnosis, Linea, Optimism, Plasma and Polygon. Their current combined inventory is 366 raw proposals, 211
eligible proposals, 155 exclusions and 198 injections. BNB is still running at its frozen 10,000-block cadence;
there is no partial-panel decision.

The first no-new-RPC full-union comparison reused v1 files only as transport diagnostics. Gnosis and Linea have
byte-identical complete action surfaces across their independent v1 providers and v2 fast primaries. Arbitrum
does not: Blockscout's v1 full scan contains 89 Hub events and 26 injections, while Tenderly's v2 scan contains 90
and 27. The missing identity is block 436,939,422, transaction
`0xbf1e4f224eca8081e0d4699008f48de384e41521799ab9e58ce014682a81da1a`, log index 1. Exact-block queries to
the official Arbitrum RPC and Tenderly return the same `UpdateInjected` payload and block hash; Blockscout returns
an empty set. This confirms a silent Blockscout omission and changes one old derived terminal label from expired
to injected. It does not invalidate the Tenderly primary, but it disqualifies Blockscout as the final Arbitrum
full-union reference. The incident demonstrates why a matching 10,000-block qualification shard cannot
substitute for the pre-outcome full-union audit. A complete official-Arbitrum replication has now completed: its
full action surface is byte-identical to the Tenderly primary, with canonical
digest `11ee6f153425f1ddb34c692af9e2bf242ca2533f279af59856282248159237c2`. The independent result therefore
confirms the v2 Arbitrum ledger and isolates the fault to Blockscout.

## Resources and interpretation

D0H is capped at 50 CPU core-hours, 5 GB retained derived data, zero paid-data spend and zero GPU hours. The two
V100 32 GB workers and RTX 2060 remain available for other justified work; this audit cannot benefit from them.
Future planning excludes H20.

Even a pass is not an NMI/NCS result. It would show that a prospectively defined, multi-deployment action ledger
has sufficient real variation to justify exact mechanism replay. The paper-level claim still requires a valid
treatment definition, real market outcomes, interference-aware inference, independent mechanism transfer and a
frozen future confirmation.
