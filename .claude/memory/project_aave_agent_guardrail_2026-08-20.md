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
