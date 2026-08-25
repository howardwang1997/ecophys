# EcoPhys / EcoMD

EcoMD is research software for differentiable, stochastic, molecular-dynamics-style
multi-agent market simulation.

> **Pre-release status.** The simulator source is under active validation. There is
> currently no endorsed EcoMD model checkpoint, no claim that its latent dynamics are
> real market physics, and no claim of order-level execution fidelity. Historical
> checkpoints were trained under an incomplete state-continuation contract and are not
> release candidates.

## What is implemented

- Langevin-style multi-agent dynamics with learned stochastic interactions;
- differentiable rollout and moment-based calibration infrastructure;
- a versioned `SimulatorState` that carries recurrent, price, integrator, neighbour-cache,
  shock, clock, and RNG state across chunks and checkpoints;
- aggregate-bin observation operators and explicit semantic-contract tests;
- stationarity and stylized-fact diagnostics, baselines, and experiment provenance.

The repository also contains historical architectures and experiments. Their presence is
not evidence that they belong to the release model. In particular, MACE/equivariant,
universal heavy-tail, crash-precursor, and real-market-physics claims are not active claims.

## Current research status

There is currently no active Nature-grade simulated-market or financial-physics topic.
Plan v4's invariant-calibration route and its successor theorem cards failed their frozen
novelty or identification gates; Plan v4 is retained as a quality, compute, and data-
governance record rather than an active paper plan. The canonical route status and reopening
conditions live in the [research-route knowledge graph](.claude/memory/research_route_knowledge_graph.yaml).

The first selection under the new Discovery Loop initially parked one narrow question—
proof-carrying discovery of transportable interventional laws across independent adaptive
market simulators—but its outcome-blind D-1 audit has now **failed-closed** the generic
formulation. The theorem decomposes into established causal-abstraction, transportability,
selective-inference, change-of-measure, rank, and bisimulation modules. ABIDES and PAMS also
lack a common native physical clock and paired RNG contract, and no real bridge passed the
state, intervention, identification, prospective-holdout, and publication-rights gates.
Its hostile T0 estimate is now 1–7% (3.5% point estimate). A recurring CME SR3 price-grid
change was the strongest new field residual, but an independent hostile screen puts it at
only 4–12% and therefore creates no topic card. No simulation, model implementation, EcoMD
integration, data purchase, or GPU work is authorized. The separate verification-liquidity
field protocol retains its existing sealed status and is not evidence that a market-physics
route is active.

A second outcome-blind rerun then searched controlled human--algorithm markets, on-chain
complete-state mechanisms, AI-scientist market benchmarks, and active interventional
fidelity for LOB generators. It again produced no topic card. Solana SIMD-0525 was the
strongest information watch, but its 12--17% hostile-T0 interval has a 12% lower bound and
the protocol jointly changes slot duration, leader-window time, capacity limits, epoch time,
and accounting. The other formulations failed direct-prior, target-counterfactual, hidden-
state, or same-estimand gates. The full reductions, exact counterexamples, probabilities,
and reopen conditions are in the
[post-Discovery-Loop reselection result](papers/proposal/ecomd_post_discovery_reselection_gminus1_result_2026-08-25.md).

A third rerun searched the structural complement of the route registry and announced
two-scale mechanisms. Conditional-order closure reduced to fixed-point/event-rule theory;
queue “holonomy” disappeared on complete MBO state; and iceberg regeneration collided with
latent-liquidity instability. Project EnergyConnect was the strongest prospective setting,
but its hostile-T0 lower bound was 6% because capacity release is test-contingent and the
market operator is not independently assigned. All other lower bounds were 1--7%. The
[structural-complement result](papers/proposal/ecomd_structural_complement_reselection_gminus1_result_2026-08-25.md)
therefore creates no topic card or execution authorization.

A fourth complement search examined atomic temporary credit, cross-margin liquidation
grammar, exchange-native implied matching, and public randomized laboratory markets. The
strongest laboratory bridge reached only a 10% hostile-T0 lower bound and lacked the joint
contract of a complete event ledger, independent replication and an untouched holdout.
Cross-margin and flash-credit formulations reduced to established reachability or
liquidation optimization. Implied liquidity was genuinely market-native, but its static
core is the shortest-path/path-packing mechanism already used by exchanges, while aggregate
virtual depth changes under redundant instrument listing. The
[atomic/margin/experimental result](papers/proposal/ecomd_atomic_margin_experimental_reselection_gminus1_result_2026-08-25.md)
therefore also creates no topic card or execution authorization.

A fifth, asset-first round reversed the order of search: it required a lawful, complete,
prospective truth asset before deriving another physics story. Public laboratory markets,
on-chain mechanisms, and exchange L3 rule transitions all failed at least one assignment,
state-completeness, independent-replication, sealed-holdout, or reuse-rights gate. The
strongest residual was the Tokyo Stock Exchange's announced 2027 closed-loop tick controller
at a 10--17% hostile-T0 interval; its 10% lower bound, bundled fee/rule changes, paid data,
and lack of a second exact controller keep it below activation. The
[external-truth asset-first result](papers/proposal/ecomd_external_truth_asset_first_reselection_gminus1_result_2026-08-25.md)
therefore creates neither a topic card nor a disposable sandbox.

## Research Discovery Loop

Topic selection is a versioned scientific process rather than idea generation followed by
experimentation. The [protocol](research/discovery/protocol.yaml) and
[method note](docs/research_discovery_loop.md) evaluate a complete discovery episode across
question formation, execution, interpretation, revision, nulls, failures, and provenance.
The [topic-exploration runbook](docs/research_topic_exploration_runbook.md) gives the
operational worksheet, killer-twin, prior-art, ranking, and escalation sequence.

The forward stages are:

1. **D-3:** define a market-native state, admissible intervention, observable, invariances,
   falsifiable claim, and explicit nonclaims;
2. **D-2:** freeze search queries and a novelty manifest with at least 15 primary works, then
   map the topic against reusable failure families from the route graph;
3. **optional DX:** after a separate asset-level authorization, use only an explicitly
   enumerated disposable split for a zero-cost, CPU-only probe whose hypotheses, falsifiers,
   test family, unit IDs, code/config hashes, receipts, and terminal result share one hash chain;
4. **D-1:** try to kill it with exact-prior reductions, at least two minimal counterexamples,
   two independent simulator contracts, a real-observation bridge, and a contamination audit;
5. **D0:** hash and freeze the estimand, baselines, budget, stop rules, confirmation split,
   and exact authorized actions before outcomes;
6. **D1/D2:** preserve exploratory branches, then confirm only on a held-out simulator family,
   mechanism, market, vendor, or future period.

DX repairs a deliberate separation problem: a small disposable probe can inform question
formation without consuming the confirmation asset. It is not a topic status and cannot
support a paper claim or promote a route. Each sandbox is capped at 8 CPU-hours, 5 GB,
16 branches, no GPU and no paid data. Schema v2 verifies actual partition members, hashes,
one asset/campaign cumulative budget, cross-sandbox exposure roles, the event chain, receipts,
an OCI execution contract, and a terminal taint-registry entry. A sandbox result is admissible only in a topic card's
`sandbox_motivation_refs`; novelty, killer, decision, D2, and paper-claim uses fail closed.
The validator now has a `--base-ref` mode that requires old manifests, decisions, inputs and
artifacts to remain byte-identical and old ledgers to remain exact byte prefixes. A new
sandbox must be merged as authorization-only before any branch can run. The research baseline
branch requires `research-governance`, forbids force pushes and deletion, enforces linear
history and conversation resolution, and disables administrator bypass. The manifest also
freezes an OCI image, launcher digest and incident-handler digest, no network, a read-only root, no repository-tree or
secrets mount, CPU-only access, a single frozen read-only config-file input, and a byte-bounded
stdout tar output. The launcher enforces and receipts that contract, but it has not yet passed
an independent runtime review. Its pinned, outcome-free local Colima/arm64 conformance run
passed all isolation checks plus timeout, output-limit, and invalid-tar rejection; the
[recorded report](research/discovery/conformance/local_colima_arm64_report_2026-08-25.json)
is source-hash bound and CI rejects it after relevant runtime changes. An ambiguous interruption
cannot be retried: the incident handler removes the named container, assumes outcome exposure,
charges the branch's full reserved CPU/output budget, and terminalizes the sandbox as
`quarantined`. Synthetic confirmation must derive its seeds from public
randomness emitted only after sandbox termination and the D0 freeze; known reserved seeds
are rejected as a false holdout. No sandbox is currently authorized.

The first candidate generator is only a
[Bourse preflight](papers/proposal/bourse_disposable_market_counterexample_preflight_2026-08-25.md):
it would search for minimal counterexamples to market-native invariance claims, not optimize
stylized facts. It creates no sandbox and authorizes no simulator run.

A topic cannot become `active` unless its conservative hostile-T0 lower bound is at least
15%, every hard contract passes, and an outcome-blind decision explicitly authorizes the
next action. High story quality, LLM consensus, retrospective rediscovery, or a benchmark
score cannot compensate for a failed gate. The source audit and first rerun are recorded in
the [formal selection result](papers/proposal/ecomd_discovery_loop_reselection_result_2026-08-25.md),
and the subsequent controlled/on-chain rerun is recorded in the
[post-discovery result](papers/proposal/ecomd_post_discovery_reselection_gminus1_result_2026-08-25.md).
The latest graph-complement and prospective-mechanism audit is in the
[structural-complement result](papers/proposal/ecomd_structural_complement_reselection_gminus1_result_2026-08-25.md).
The subsequent atomic, cross-margin, implied-liquidity and experimental-asset audit is in
the [atomic/margin/experimental result](papers/proposal/ecomd_atomic_margin_experimental_reselection_gminus1_result_2026-08-25.md).
The subsequent asset-first truth-contract audit is in the
[external-truth result](papers/proposal/ecomd_external_truth_asset_first_reselection_gminus1_result_2026-08-25.md).

```bash
conda run -n ecophys python scripts/validate_research_discovery.py
conda run -n ecophys python scripts/validate_research_discovery.py \
  --base-ref origin/dependabot-cooldown-verification-liquidity-2026-08-21
conda run -n ecophys python scripts/validate_research_route_graph.py
conda run -n ecophys python -m pytest tests/test_research_discovery.py \
  tests/test_run_research_discovery_sandbox.py \
  tests/test_research_discovery_oci_conformance.py tests/test_research_route_graph.py -q
conda run -n ecophys python scripts/test_research_discovery_oci_conformance.py \
  --verify-recorded-report
```

## Current software-release gates

The simulator-audit paper route failed its prior-art novelty gate. EcoMD work is therefore
focused on a narrower sequence:

1. produce a source-only research preview with synthetic smoke tests and no raw market data;
2. freeze one state-complete model specification and retrain from scratch;
3. require post-stationarity, time-out-of-sample fidelity before releasing a checkpoint or
   drafting a positive model-paper claim;
4. add strong baselines, ablations, generalization, gradient-utility, and scaling evidence.

See the [release scope](papers/proposal/ecomd_v1_release_scope_2026-08-10.md), the
[model-paper plan](papers/proposal/ecomd_model_paper_release_plan_2026-08-09.md), and the
[research-preview contract](docs/ecomd_research_preview_contract.md).

## CPU quick start

```bash
conda create -n ecophys python=3.11 -y
conda run -n ecophys pip install -e ".[dev]"
conda run -n ecophys python examples/ecomd_cpu_smoke.py
conda run -n ecophys python -m pytest tests/test_ecomd_smoke.py \
  tests/test_simulator_state.py tests/test_release_contract.py -q
```

The smoke path generates synthetic trajectories and downloads no data. New production
training is not launched until the release configuration passes the versioned training
contract. CPU validation comes first; the available V100 32 GB cards are reserved for the
subsequent frozen single-card reference run. H20 is not part of the forward compute plan.

## Data boundary

No raw Yahoo Finance, LOBSTER, or Binance files are part of the planned public release.
The historical `data/sample/` cache is research-internal pending redistribution review.
Public artifacts use generated synthetic inputs plus acquisition instructions and hashes
for data users obtain under their own terms. See [`data/sample/README.md`](data/sample/README.md).

## Repository layout

```text
ecomd/          simulator, training, observation, evaluation, and baseline code
experiments/    immutable experiment protocols and results
tests/          unit, semantic-contract, and exact-resume tests
examples/       data-free executable examples
docs/           release-facing technical contracts
papers/         paper drafts, proposal gates, and release plans
research/       forward topic cards, novelty manifests, evidence, and discovery decisions
scripts/        current utilities plus clearly marked historical launch scripts
logs/           dated research work log
```

## License

Source code is licensed under the [MIT License](LICENSE). Dataset licenses and rights are
separate from the code license.
