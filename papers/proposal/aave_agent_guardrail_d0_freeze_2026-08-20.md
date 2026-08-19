# Aave automated-agent guardrail — D0 action-support freeze

## Status and purpose

This protocol is frozen before retrieving any `ParameterUpdated` proposal value or matching any proposal to an
`UpdateInjected` execution. It asks only whether Aave's historical Risk Agent deployment contains the action
support needed for a later guardrail-based causal design.

D0 is not an outcome analysis. It must not retrieve Aave pool balances, utilization, borrow/supply rates,
positions, transactions by users, prices, liquidations or post-action market responses.

## Fixed source identity

The formal run uses the exact official repositories and commits in
`configs/empirical_physics/aave_agent_guardrail_d0_v1.yaml`. The primary Ethereum contracts are:

- AgentHub proxy: `0x95E3015c67EF62B866cC28ca5A9AB5017A55e336`;
- RangeValidationModule: `0x9240a6669CC4782FC98620212862DF5CB2e0Df10`;
- chain: Ethereum mainnet, chain ID 1;
- inclusive block interval: `24,000,000` through `25,790,047`;
- frozen end block hash: `0xdc25498b91d330723928b6528f81e4a1022166276ad2f8b0f96973a730cb8362`.

The lower bound predates the January 2026 Risk Agent activation. The upper bound is frozen on 20 August 2026
NZST and includes the later offboarding. No moving `latest` tag is allowed in the formal result.

The first clean formal attempt was rejected before any log was returned because dRPC's free-plan transport now
limits `eth_getLogs` to 10,000 blocks, not the source-freeze probe's 50,000. The formal transport therefore uses
10,000-block inclusive shards and an identity-bound decoded-event checkpoint outside the repository. This changes
request scheduling and recoverability only; the inclusive block union, events, matching and thresholds do not
change. JSON-RPC `-32000/method handler crashed` is retried with the same bounded exponential backoff as transport
limits and recorded separately; evidence from failed singleton bisection rules out treating it as a range-size
error. A 14-topic Hub filter fails while fixed groups of at most four allowed topics succeed on the same shard,
so formal queries use `10,000 blocks x <=4 allowed topics` and union logs by canonical identity. Rate limits and
genuine range/response-size failures retain their separate handling. Empirical public-endpoint failure begins at
about 128 calls in one minute, so requests are paced at 0.75 seconds (at most 80 starts per minute) rather than
0.5 seconds. When a compound allowed-topic query still times out or returns the exact handler crash, the query
splits the topic set first while preserving its block range. Only a singleton-topic range/size timeout may split
the block interval. Topic and block split counts are reported separately.

Google's current Blockchain Analytics table covers the frozen endpoint, but a result-equivalent address query has
a 789.9 GB dry-run upper bound. The visible query project has zero billed bytes this month, yet another project on
the same billing account cannot be audited with the available permissions. Because Google's 1 TiB free allowance
is account-level, BigQuery is not executed and is not a hidden paid fallback.

## Allowed event surface

D0 may retrieve and decode only:

1. AgentHub registration and configuration events needed to reconstruct agent ID, Risk Oracle, update type,
   enabled state, market allow/restrict lists, expiration, minimum delay, agent contract and context;
2. `RangeValidationModule` default and market-specific range-configuration events;
3. `RiskOracle.ParameterUpdated`, including typed proposal value, previous proposal value, update ID, market,
   timestamp and additional metadata;
4. `AgentHub.UpdateInjected`, including agent ID, update type, update ID, market and injected value;
5. block headers and transaction identities needed for ordering, timestamps and provenance.

Raw RPC responses must not be committed. The result retains decoded policy fields, transaction/block provenance,
classification summaries and cryptographic digests. Source and ABI parsing must be pinned to the listed commits.

## Frozen matching and classification

A proposal matches an execution only when Risk Oracle address, update type, update ID, market and proposed/injected
value agree. Transaction ordering breaks same-block ties.

For every proposal, D0 records one terminal class:

- `injected`: an exact later `UpdateInjected` match exists while the agent is enabled;
- `overwritten_uninjected`: a newer proposal for the same Risk Oracle, update type and market appears first;
- `expired_uninjected`: the configured expiration horizon ends without an injection or overwrite;
- `disabled_or_offboarded`: the relevant agent is disabled before injection;
- `right_censored`: none of the above is resolved by the frozen end block;
- `unmatched_or_ambiguous`: source identity or exact matching cannot be established.

Delay exposure is a non-terminal annotation: whether a proposal arrives before the configured minimum delay from
the prior injection has elapsed. Range-boundary distance is computed only when the exact validation input can be
reconstructed from policy state without reading behavioral outcomes. A Risk Oracle `previousValue` may be
reported separately but cannot silently substitute for the protocol value used by the agent contract.

## Hard pass/stop criteria

D0 passes to a separately frozen D1 exact-validation replay only if all conditions hold:

1. at least 30 unambiguous proposals and 20 exact injections;
2. at least two update types, five markets and three registered agents represented;
3. at least ten resolved non-immediate proposals in total, defined as overwritten, expired, disabled/offboarded,
   or delay-exposed before eventual injection;
4. at least one deterministic guardrail has at least 20 reconstructable scores, with at least five observations
   on each side of its boundary and at least five observations within 25% of the permitted change or time margin
   on each side;
5. no evidence of exact clipping/bunching that makes the proposal density discontinuous at every otherwise
   eligible boundary;
6. at least 90% of proposals have an unambiguous terminal class, excluding administratively right-censored rows.

Criterion 4 is deliberately demanding. A large number of successful actions with no rejected/delayed comparison
does not identify a guardrail effect. If any criterion fails, stop the threshold-causal route before D1 and before
all market outcomes. A descriptive controller ledger may survive only as infrastructure.

Before proposal values are read, exact-boundary bunching is operationalized as at least five exactly zero margins
and at least 50% of all scores for the same agent and unchanged minimum-delay boundary. Each delay boundary is
kept agent-specific; heterogeneous agents or delay epochs are not pooled. Negative and positive near-boundary
counts exclude exact zeros. An amplitude range score is unavailable in D0 unless the exact contemporaneous
protocol value read by the agent is present on the allowed policy surface; the Risk Oracle's prior proposal is
not that value.

## Forbidden rescues

- do not redefine ordinary injected actions as independent shocks;
- do not count multiple assets from one bulk proposal as independent threshold experiments;
- do not replace an absent rejected-action group with simulated proposals;
- do not widen the 25% boundary neighborhood after seeing support;
- do not infer exact range validity from the oracle's prior proposal when the contract validates against a
  different protocol state;
- do not read outcomes to choose the most favorable update type, market, chain or threshold;
- do not pool other chains to rescue an Ethereum failure without a new frozen multi-chain D0;
- do not launch EcoMD, CPU outcome jobs or GPU models.

## Resource cap and next decision

D0 is a network/CPU metadata audit capped at 20 core-hours, 2 GB retained derived data and zero GPU hours. A pass
authorizes only an exact policy-state replay specification. It does not establish causal identification or
authorize response data.
