---
name: ecomd-collision-cone-replay-t0-2026-08-24
description: "FAIL/RED at G0: Hanai et al. 2019 already provide exact differential replay of altered DES events and recursive causal effects; generic from-scratch and trace-distance theory absorb the remaining theorem shape. No implementation, outcomes, data, EcoMD or GPU."
metadata:
  node_type: memory
  type: project
---

# EcoMD collision-cone exact counterfactual replay T0

After the random-clock route failed its protocol/schema gate, a fresh zero-compute selection activated one
theorem-first card: exact counterfactual replay of only the collision cone affected by a local simulator-rule
intervention. The intended output was a persistent trace delta and terminal-state delta, with exact equality to
a full rerun and work controlled by the affected event set rather than the full baseline trajectory.

The route **closed FAIL/RED at G0 on 2026-08-24**. Hanai et al., *ACM TOMACS* 29(3), Article 18 (2019), DOI
`10.1145/3301499`, already store baseline events/states/anti-messages, accept event addition/deletion/state update,
recursively propagate causal changes through rollback and reprocess only altered portions while returning the
same result as a complete rerun. The method is transparent to application event handlers and was evaluated on
PHOLD and Tokyo traffic. Replacing those handlers with price-time matching or hard-particle collisions is a
specialization, not a new core result.

The residual theorem stack does not survive independently. Self-adjusting computation already proves
from-scratch consistency with update cost governed by execution-trace distance, including reordered traces. If
the number of new affected events at each propagation depth has conditional expectation at most $\rho<1$ times
the previous layer, $\mathbb E|D|\leq k/(1-\rho)$ is the standard geometric offspring bound. An
$\Omega(|D|)$ inspection/output claim is an output-size observation unless it separates the harder online cone
discovery problem from generic incremental computation.

A baseline executed-event read/write graph and a common sequential RNG seed are unsound. Lasting guardrails are:
use stable causal event and draw-site keys; record guards including false candidates; include event creation,
cancellation, rescheduling, priority/order and queue-minimum/absence dependencies; roll back across newly
inserted earlier events; and abstain when a local intervention has a global scheduler cone. The true cone is an
online fixed point over baseline and newly generated counterfactual events, not merely a baseline-graph closure.

The frozen first-failure rule stopped the 40-work minimum after eight decisive primary works and did not reach the
external-system gate. No market outcome, paid data, implementation, benchmark, EcoMD execution or GPU was used.

Reopen only with a collision-specific theorem that cannot be expressed for arbitrary DES callbacks: sound online
cone discovery without a full counterfactual oracle, disabled-event and schedule-inversion coverage, a uniform
subcritical certificate derived from pre-intervention quantities, a separating lower bound and a scientific
result beyond software acceleration. Event-keyed randomness, persistent deltas, market terminology or a first
collision application are insufficient.

Artifacts:

- Selection: `papers/proposal/ecomd_post_random_clock_problem_selection_2026-08-24.md`
- Freeze: `papers/proposal/ecomd_collision_cone_replay_t0_freeze_2026-08-24.md`
- Machine gate: `configs/empirical_physics/ecomd_collision_cone_replay_t0_v1.yaml`
- Formal result: `papers/proposal/ecomd_collision_cone_replay_t0_result_2026-08-24.md`
- Route graph: `.claude/memory/research_route_knowledge_graph.yaml`
