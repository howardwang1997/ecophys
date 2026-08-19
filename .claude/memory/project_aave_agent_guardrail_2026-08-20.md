---
name: aave-agent-guardrail-2026-08-20
description: "Outcome-blind support gate for proposed versus injected Aave Risk Agent actions near deterministic guardrails."
metadata:
  node_type: memory
  type: project
---

# Aave automated-agent guardrail field design — frozen 2026-08-20

The completed Aave rate-response D1B rules out that event panel but leaves reusable source, governance and log
infrastructure. Two immediate generalizations do not survive novelty/logic review. Intervention frequency times
mixing time is not a universal identification number because informative fast inputs can identify and sparse
confounded inputs can fail. Generic trace-to-controller conformance is not an NCS contribution because system
identification, runtime verification, smart-contract specification mining and data-driven formal verification
already occupy the broad problem.

The remaining AMBER candidate uses a specific property of deployed Aave Risk Agents: a Risk Oracle emits a
typed proposed `ParameterUpdated` action, while AgentHub separately emits a successful `UpdateInjected` after
expiration, replay, minimum-delay and agent-specific checks. If proposal scores cross a deterministic guardrail
with continuous local support, the eligibility boundary could provide a field design for controller execution.
If the informed off-chain proposer clips or bunches every action inside the allowed range, the design fails
before any market outcome is opened.

The D0 protocol and executable configuration were frozen in
`papers/proposal/aave_agent_guardrail_d0_freeze_2026-08-20.md` and
`configs/empirical_physics/aave_agent_guardrail_d0_v1.yaml` before retrieving proposal values or matching them
to executions. D0 may read only official pinned source, AgentHub/RangeValidation configuration events, Risk
Oracle proposals, injection events and block/transaction provenance. It must not read utilization, rates,
balances, positions, prices, liquidations, user transactions or response windows.

D0 passes only with at least 30 unambiguous proposals, 20 exact injections, two update types, five markets,
three agents, ten resolved non-immediate proposals and one reconstructable deterministic boundary with at least
20 scores, five observations on each side and five near observations on each side. At least 90% of
administratively resolved proposals must have an unambiguous terminal class, and universal boundary clipping or
bunching fails. Any failed criterion stops this threshold-causal route before D1 and before outcomes; no
multi-chain or simulated-action rescue is allowed without a new freeze.

This is a CPU/network audit capped at 20 core-hours and 2 GB, with zero GPU. The two V100 32 GB workers and RTX
2060 intentionally remain idle because the uncertainty is treatment support, not model capacity. Passing D0
would authorize only a separately frozen exact policy-state replay; it would not establish identification or
authorize an EcoMD experiment.

The D0 implementation uses source-ordered, exact-field proposal/injection matching and reconstructs expiration
and minimum-delay exposure from AgentHub configuration events. Minimum-delay boundaries are grouped by agent and
unchanged delay value; agents or epochs cannot be pooled. Before any proposal value was retrieved, exact-boundary
bunching was fixed as at least five zero margins making up at least 50% of a boundary's scores. Exact zeros count
on neither side. Amplitude range scores remain unavailable because pinned source proves `previousValue` is only
the previous oracle proposal while the deployed agents validate against contemporaneous protocol state.

Five pinned official repositories pass a source-only audit: AgentHub, Risk Agents, Chaos Agents, address book and
proposals. The Aave/Chaos/proposals AgentHub interfaces agree, the Risk Agents submodule pins the frozen Chaos
commit, and the Ethereum AgentHub and RangeValidation addresses occur in the frozen address book. Six decoder,
matching, terminal-class and boundary-support tests pass without adding an ABI dependency. The formal chain run
must start from a clean implementation commit; until then no proposal value has been opened.

The first clean formal invocation from `c8aed2a12` was rejected before its first log response because dRPC's
free-plan `eth_getLogs` maximum is now 10,000 blocks. This did not open a proposal value or write a result.
Transport is amended to 10,000-block shards with an external decoded-event/header checkpoint bound to code,
config, source SHAs, RPC and endpoint block. The scientific block union, events and gates are unchanged.
The next shard then reproduced JSON-RPC `method handler crashed` twice after the checkpoint reached block
24,309,999. A later run crossed that shard but cascaded through bisection to a singleton block, falsifying the
range-size interpretation. Treat only exact code `-32000` plus `method handler crashed` as a bounded, separately
metered transient retry; do not split it or generalize to other `-32000` errors.
Further probes localize the backend fault to compound topic filters: the same shard succeeds when the 14 allowed
Hub topics are partitioned into groups of at most four. Formal transport therefore uses 10,000-block by four-topic
cells and unions canonical log identities. Flashbots is unusable because it silently omitted a dRPC-verified
68-event deployment shard; LlamaRPC and 1RPC also failed availability/plan checks.
The implemented four-topic partition independently re-fetches and exactly matches all 68 deployment-shard log
identities in four calls without retry. This is the required transport sanity check before a new formal run.
Formal degradation begins near 128 calls/minute despite the documented nominal CU allowance, so D0 pacing is
fixed at 0.75 seconds (80 starts/minute). A current Google Blockchain Analytics fallback would scan 789.9 GB.
Although `rooy-data` reports zero billed bytes this month, another inaccessible project shares its billing
account; because the 1 TiB free allowance is account-level, BigQuery must not be executed as a purportedly free
rescue.
The 0.75-second run remains complete but slows severely when some four-topic cells repeatedly back off. D0 now
uses evidence-based two-dimensional recovery: compound-topic handler/timeout/size errors split topics first;
only singleton-topic range failures split blocks. D1B retains block-first behavior, and both split counts are
reported.
dRPC remains fatal after roughly 128 cumulative calls even after topic splitting. Blockscout's documented no-key
Ethereum ETH RPC exactly reproduces two complete dRPC identity sets (68/68 deployment, 5/5 sparse). It becomes the
formal replaceable transport with 10,000-block shards, 0.75-second pacing and 14 allowed Hub topics; the documented
1,000-log cap exceeds the observed 68-log shard maximum. Chain ID and frozen endpoint block hash also match.
The Blockscout instance rejects one-element address arrays, so single-contract log requests use the standard
scalar form; multi-address requests remain arrays. The failed attempt returned no log or result.

Formal D0 completed from clean commit `cce8d234e7eb8d208c4bb2731bb61f63baee5ad7`. The immutable result is
`results/empirical_physics/aave_agent_guardrail_d0_result.json`, canonical SHA-256
`764f08a7a02c550f28f8b7ace275cf4e451ba5430ea5768aff55f374c1226460`. Its binding and decision are independently
recomputed in `tests/test_aave_agent_guardrail_result.py` without calling the runner's gate or ledger helpers.

The decision is a hard `stop_threshold_causal_route_before_market_outcomes`. Eight of nine gates pass: 155
proposals, 133 unambiguous, 127 exact injections, five update types, 17 markets, five represented agents, 38
resolved non-immediate proposals and one qualifying unbunched three-day delay boundary with 68 scores. The only
failure is the terminal-classification rate, 133/155 = 85.81% versus the frozen 90% minimum. No D1 or market
outcome is authorized.

Post-hoc diagnosis must not be mistaken for a pass: 21 of the 22 unmatched rows precede the unique registration
of their eventual source agent and one update type is never registered; all 133 post-registration proposals are
classified. This exposes left truncation in the original risk-set definition. Any correction requires a new
freeze and untouched holdout. A complete non-Ethereum deployment panel can prospectively validate measurement
and support, with eligibility only after unique registration plus required initialization and with synchronized
cross-chain proposals deduplicated. It does not by itself provide independent causal shocks. GPU, EcoMD, D1 and
outcomes remain locked.

A new untouched protocol is frozen in
`papers/proposal/aave_agent_guardrail_holdout_d0_freeze_2026-08-20.md` and
`configs/empirical_physics/aave_agent_guardrail_holdout_d0_v1.yaml` before any non-Ethereum `eth_getLogs` or agent
event value. It covers the complete nine-chain panel fixed by pinned Risk Agents source: Arbitrum, Avalanche,
Base, BNB, Gnosis, Optimism, Polygon, Plasma and Linea. Ethereum is excluded from every holdout count and its
failed D0 cannot be reclassified.

All nine chain IDs, calendar start blocks, exact start/end hashes and AgentHub code existence were checked using
only source, block headers and `eth_getCode`. The common start is the first block at or after 2025-11-24 00:00 UTC,
before the synchronized deployment batch. No non-Ethereum event has yet been queried.

D0H prospectively conditions eligibility on one unique registration plus prior AgentAddressSet, enabled=true,
expiration and minimum-delay initialization. Pre-activation and never-registered proposals remain audited
exclusions, while any ambiguity after activation penalizes the 90% classification gate. Adjacent proposals no
more than 120 seconds apart form one conservative cross-chain action batch regardless of type. A pass needs three
represented chains and ten batches, plus two unbunched, two-sided chain-specific delay boundaries on two chains;
each boundary must pass both row and batch-median support. No chain may be dropped for low activity. D0H is capped
at 50 CPU core-hours, 5 GB, zero paid data and zero GPU; D1, outcomes and EcoMD remain locked.

Before the first holdout event query, D0H clarifies activation versus unambiguity: at least one prior initialized
registration enters the proposal into the risk set, while exactly one is required to classify its source. Multiple
initialized matches stay in the denominator as failures. Transport qualification uses 10,000-block shards;
formal scanning starts from a fixed per-chain span approximating seven UTC days and recursively splits explicit
range/timeout/result-size failures. This changes neither the block union nor any scientific threshold and avoids
pathological request counts on short-block-time chains.

The pre-event D0H implementation is now complete in
`scripts/audit_aave_agent_guardrail_holdout_d0.py`. It has isolated `chain`/`merge` modes, requires a clean code
snapshot, independently re-verifies the failed Ethereum pilot and all pinned sources, qualifies two transports
by exact nonempty-shard log identity, and writes only identity-bound decoded checkpoints outside the repository.
Required initialization must follow its matching registration. The initial focused 28-test suite, Ruff and strict
mypy passed; source audit binds nine chains and 26 files.

The first post-freeze qualification attempt from `4f826b2a3` produced no artifact/checkpoint. Avalanche and
Polygon exposed explicit provider block-range caps; BNB exposed a false coupling between log transport and
historical-state availability. A transport-only amendment keeps the exact 10,000-block qualification union but
allows recursive request subdivision, verifies chain/hashes on the fixed anchor RPC, and requires each log
transport to verify chain/hashes plus exact log identities. Documented public Avalanche dRPC and archive-capable BNB
OnFinality were added after source-blind anchor/code probes passed. Seven obsolete old-SHA runs were terminated;
no shard is reusable.

The next clean attempt from `700d39f92` showed that fixed Arbitrum/BNB anchors had retained exact headers but
pruned frozen state. It also wrote no artifact/checkpoint. State verification is now a separate, result-blind
witness: the first archive-capable endpoint in fixed anchor/candidate order must return nonzero Hub code at the
exact `to_block`. Header/code-only preflight found one on all nine chains (Arbitrum Blockscout, BNB OnFinality,
first fixed endpoint elsewhere). The expanded focused suite passes 38 tests plus Ruff/strict mypy. No chain, data union,
event family, eligibility rule, batch definition, scientific gate or stop rule changed. D1, outcomes, EcoMD and
GPUs remain locked pending a conjunctive D0H pass from the next clean SHA.

The clean attempt from `e9e4b3dc9` passed all nine separate state witnesses but produced no artifact: BNB log
sources failed through rate limiting/TLS and Linea exposed the explicit cap message `range ... exceeds limit of
10000`. No current-SHA checkpoint survived; one older Gnosis checkpoint is identity-incompatible and unusable.

BNB transport is now repaired without changing the scientific design. Pinned proposal history plus archive
`getAgentCount()` state locates the exact first registration-state transition at blocks 75,187,733 (0) and
75,187,734 (2), fixing aligned qualification shard 75,184,723--75,194,722 without screening market outcomes.
SQD Portal, public no-key Nodeflare and public no-key Pocket all return 30 identical Hub log identities; their
canonical digest is `2d50fe7f...5a4`. Nodeflare/Pocket are the first two log candidates and OnFinality remains the
state witness. Nodeflare also returns a valid empty result on the first frozen 10k interval, excluding the
immediate recent-history-only failure. BNB formal span is 10,000, matching the documented free cap. Linea's exact `exceeds limit of`
message is splittable while generic `limit exceeded` remains a fatal/quota error. Restart from a new clean SHA;
D1, outcomes, EcoMD and GPUs remain locked.

Attempt `e7bf9a015` proved the new Nodeflare primary but failed BNB before artifacts because Pocket stopped serving
the frozen start anchor from all three tested egresses. FastNode passed headers but silently returned zero of the
30 qualification logs and is rejected. ChainList candidates bloXroute and Sentio matched all 30 identities on
Mac; on the designated RTX-host single egress, Nodeflare plus documented public bloXroute both match digest
`2d50fe7f...5a4`, while OnFinality verifies code and the consecutive state transition. Use bloXroute as BNB's
second candidate and run all BNB roles from that one preflighted egress; never combine identities across IPs.
The initial fleet command's script-path import failure made no RPC call; corrected module launches produced some
old-SHA files, all now identity-incompatible and retained only as attempt provenance. Restart all nine chains from
the next clean SHA.

Version-1 clean run `ac99559212dd0a0943c669b5d0981908e44d81e8` is now classified as an outcome-blind transport
diagnostic. It completed valid but unmergeable Arbitrum (29 eligible/5 excluded), Gnosis (1/0) and Linea (14/40)
artifacts and exposed Base qualification failure plus deterministic latency/range bottlenecks elsewhere. No
market outcome was queried. Fixed qualification shards and exact canonical identity digests were independently
established for all nine chains: Arbitrum `653120b4...`, Avalanche `8ab51afa...`, Base `31b2e41e...`, BNB
`2d50fe7f...`, Gnosis `50c3b3df...`, Linea `5fe9ba21...`, Optimism `5f54a007...`, Plasma `2968ed41...` and
Polygon `e93d2393...`.

The outcome-blind transport amendment is executable as
`configs/empirical_physics/aave_agent_guardrail_holdout_d0_v2.yaml`, digest
`93be07281ff57e853d32f5caadc2f08d9a38e9e91728c35c8126a22aab25246c`. Seven chains use Tenderly as a fast
primary; BNB and Plasma use Sentio. Each qualification shard has an independent provider match, but primary
provider concentration creates correlated omission risk. Therefore even a D0H pass cannot unlock market
outcomes until every chain's complete decoded event union is reproduced by a non-primary provider and compared
by identity and payload. All nine primary artifacts must also be rerun from one clean v2 code SHA/config digest;
v1 files remain diagnostic-only. This changes no chain, block union, event family, sample rule, threshold or stop
rule. GPUs, EcoMD, D1 and outcomes remain locked.

Version 2 was committed and pushed as clean SHA `c9ab42a64295ec6bd3ea6868050cb9ca4dd05d15`, then deployed to
isolated exact-SHA roots on both V100 hosts and the RTX 2060 host with CUDA hidden. Eight primary chain artifacts
are complete and independently digest-verified locally: Arbitrum `1b02c48b...`, Avalanche `810fc3b4...`, Base
`6554a05c...`, Gnosis `ea60ec3c...`, Linea `cdf9cec6...`, Optimism `552bdb4c...`, Plasma `832af1cb...` and
Polygon `327f8ae5...`. Together they contain 366 raw proposals, 211 eligible proposals, 155 audited exclusions
and 198 injections. These partial counts do not authorize a pass; BNB remains mandatory and is running through
Sentio at the frozen 10,000-block/0.75-second cadence. Plasma was safely migrated from a slow official-RPC
checkpoint to a fresh RTX/Sentio run after the new checkpoint proved its SHA/config/endpoint identity.

The first full-union transport comparison found Gnosis and Linea action surfaces byte-for-byte equal between v1
independent providers and v2 fast primaries. Arbitrum did not match: the v1 Blockscout artifact has 89 Hub events
and 26 injections, while Tenderly v2 has 90 and 27. The missing identity is block 436,939,422, transaction
`0xbf1e4f224eca8081e0d4699008f48de384e41521799ab9e58ce014682a81da1a`, log index 1. Both official
`arb1.arbitrum.io` and Tenderly return the same `UpdateInjected` payload/hash at that exact block; Blockscout
returns an empty set. This is a confirmed silent Blockscout omission, not a reorg or Tenderly overcount. It changes
one v1 proposal from falsely expired to correctly injected and proves that one matching qualification shard is
insufficient to guarantee full-window completeness. A full official-Arbitrum v2 replication completed on
V100-A with artifact digest `d5eed01f...`; its complete action surface is byte-identical to the
Tenderly primary, canonical action-surface digest `11ee6f153425f1ddb34c692af9e2bf242ca2533f279af59856282248159237c2`.
Blockscout cannot serve as the final Arbitrum full-union reference. The eight complete primary artifacts are now
staged beside the running BNB task on the RTX host; watchdog PID 286331 will merge only if BNB writes a result,
and otherwise records failure without attempting a partial merge. No market outcome was queried.
