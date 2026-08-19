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
