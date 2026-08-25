---
name: EcoMD research Discovery Loop
description: Forward-only scientific topic-selection protocol installed after a primary-source audit of Discovery Loop, Science-Discovery, AI-scientist evaluation and falsification systems. The machine contract freezes the evidence pattern seen in adjacent NCS/NMI papers and now separates disposable question-search probes from confirmatory evidence. No Nature-grade topic is active and no exploration sandbox is currently authorized.
node_type: memory
type: project
---

# EcoMD research Discovery Loop (2026-08-25)

## Binding decision

- Forward topic selection is governed by `research/discovery/protocol.yaml` and
  `docs/research_discovery_loop.md`.
- `.claude/memory/research_route_knowledge_graph.yaml` remains the canonical registry for
  route status, lineage, terminal evidence, forbidden actions, and reopen conditions.
- Plan v4's paper route is closed. Its state, observation, compute, data, and reproducibility
  standards remain inherited quality constraints, not authority to execute a topic.
- A topic becomes active only if every hard gate passes, including a conservative hostile-T0
  lower bound of at least 15%. Scores and narratives cannot average away a failed gate.
- Adjacent NCS/NMI evidence adds a noncompensatory target: an irreducible core, same-estimand
  truth, cross-system/OOD breadth, hard negatives, error control, equal-budget baselines,
  and the same real action--state--observation loop whenever sim-to-real is claimed.
- A pre-active disposable exploration sandbox is permitted only through its own hashed
  v2 manifest and decision. It may use an explicitly enumerated exploration split under a zero-cost CPU-only
  budget, but cannot access confirmation data, support a paper claim, promote a route, or
  alter the 15% activation floor. No such sandbox is currently authorized.

## Source audit that changed the workflow

- Discovery Loop's public site is a vision page, not an available implementation or benchmark;
  no relationship to the Science-Discovery GitHub organization was established.
- Science-Discovery/Aether is a research workbench. AI-Newton performs structured law
  rediscovery inside supplied experiments and a DSL. Neither validates open topic selection.
- *Measuring AI Scientists: From Exams to Discovery* is a public ChemRxiv v1 Perspective dated
  2026-08-18 with nine formal authors. It is not a released benchmark: no companion task set,
  scorer, code, leaderboard, reliability study, or contamination result was found.
- Its durable contribution is the `discovery episode`: separately attribute hypothesis
  generation, execution, interpretation, revision, nulls, failures, and provenance.
- HLE measures closed academic knowledge; FrontierScience measures supplied research
  subtasks; ResearchBench measures ideation; DiscoveryBench and BAISBench measure
  data-driven rediscovery; ResearchClawBench measures end-to-end published-result
  rediscovery; DiscoveryWorld measures a simulated loop. None alone demonstrates
  prospective discovery.
- NLPCC 2026 Task 9 AISB is an independent shared task, not the ChemRxiv Perspective's
  implementation; the acronym is ambiguous and must not be used as an identity shortcut.
- ResearchBench informs retrieval--composition--ranking; AutoDiscovery informs exploratory
  acquisition; POPPER informs sequential falsification; Robin, Finch, and XScientist inform
  immutable evidence trails. None of these makes agent agreement or retrospective
  rediscovery into confirmation.
- petri-bench already includes fresh causal-discovery tasks over a market simulator with
  objective process scoring and a multiplicity audit. A generic hidden-parameter market-law
  benchmark is therefore not a viable novelty claim.

Versions, licenses, roles, and limitations are frozen in
`research/discovery/evidence_registry.yaml`. Repositories without a usable license are not
vendored.

## Installed artifacts

- Topic schema: `research/discovery/topic_card.schema.json`
- Disposable-sandbox schema: `research/discovery/exploration_sandbox.schema.json`
- Sandbox partition/decision/result schemas and taint registry:
  `research/discovery/exploration_partition.schema.json`,
  `research/discovery/exploration_sandbox_decision.schema.json`,
  `research/discovery/exploration_sandbox_result.schema.json`, and
  `research/discovery/sandbox_taint_registry.yaml`
- Failure-family registry: `research/discovery/failure_families.yaml`
- Evidence registry: `research/discovery/evidence_registry.yaml`
- Validator: `scripts/validate_research_discovery.py`
- Pull-request history check: `.github/workflows/research-governance.yml`
- Mutation tests: `tests/test_research_discovery.py`
- First formal rerun: `papers/proposal/ecomd_discovery_loop_reselection_result_2026-08-25.md`

The protocol stages are D-3 question framing, D-2 evidence compilation, D-1 hostile
falsification, D0 outcome-blind freeze, D1 exploratory evidence, and D2 held-out
confirmation. Search history is append-only; revisions are child cards rather than edits
that erase a failed parent.

An optional asset-level DX sandbox sits outside route status. It repairs the circularity in
which all empirical feedback was forbidden until a topic had already passed a high-confidence
activation gate. Schema v2 requires hashed provenance/snapshot/partition inputs, explicit
unit membership, cumulative asset-campaign reservations, and one canonical event chain that
freezes each hypothesis, falsifier, multiplicity family, test set, seed set and code/config
before its receipt. Every terminal result is `sandbox_exploratory_tainted`: it can appear
only in `sandbox_motivation_refs`, never in novelty, killer, decision, D2 or paper-claim
evidence. The validator now has a protected-base mode: old manifests, decisions, inputs and
artifacts are immutable, event ledgers and the taint registry are prefix-only, and a new
sandbox must be merged as authorization-only before it can execute. The PR workflow exists,
but the repository owner must still make it required and forbid force pushes. Schema v2 also
binds an OCI image and launcher digest, no network, a read-only root, no repository or
secrets mount, CPU-only access, an exploration-only mount, absent confirmation outcomes and
an artifact-only output mount. Receipts repeat the contract, but a reviewed launcher must
still enforce it. Synthetic confirmation must use a frozen future-public-randomness seed
derivation; known reserved seed numbers are not a holdout. No sandbox is authorized.

The first proposed synthetic generator is retained only as the outcome-blind Bourse
counterexample preflight in
`papers/proposal/bourse_disposable_market_counterexample_preflight_2026-08-25.md`. Bourse
0.4.0 is suitable for cheap seeded from-scratch question generation, not for confirmation,
continuous-time claims or full agent-plus-RNG branch replay. The preflight estimates only a
5--10% chance of motivating a new D-3 card and therefore authorizes no run.

## First protocol-governed rerun and D-1 closure

Broad topic `AI discovers laws in simulated markets` is closed under direct benchmark and
causal-discovery prior art. The only residual is
`transportable_interventional_market_law_discovery`: discover a common intervention-response
path law across independent adaptive market simulators, or emit a machine-checkable pair of
transcript-equivalent worlds separated by a target intervention.

The first-pass status was **parked**, not active:

- hostile T0 range 7--18%, point 12%; complete NMI 3--4%, NCS 1--2%;
- causal abstraction, transportability, and selective-identification collisions unresolved;
- `schedule_nullspace_alias` and `identity_clock_erasure` killers pending;
- ABIDES and PAMS common state/intervention/clock/RNG contract unqualified;
- no qualified real-market observation and intervention bridge.

At that first pass no work was authorized while parked. The follow-up therefore remained
limited to theorem, source-contract and public-schema audit: no outcomes, simulator runs,
model implementation, EcoMD changes, data purchase or GPU.

The subsequent outcome-blind D-1 audit closes that generic card:

- Dyer et al. 2024 directly occupy interventionally consistent state/intervention
  abstractions for complex simulators; finite-sample interventional CRL and UAI 2026 work on
  transportable causal bandits, adaptive intervention fidelity, and selective coverage fill
  the proposed generic finite-sample residual.
- A law-or-witness procedure reduces to confidence-set target diameter plus selective
  inference. The schedule witness is a rank/null-space certificate and the identity-clock
  witness is controlled probabilistic bisimulation. General source-code completeness is
  impossible.
- ABIDES and PAMS fail the strict same-estimand contract: PAMS has no native physical-time
  domain and its global runner RNG consumption changes when one arm emits an order list and
  another emits none. Replacing the runner or inventing a physical clock is not an
  independent native mechanism.
- No field bridge passed state, intervention, identification, prospective-holdout, and
  publication-rights gates. Repeated CME SR3 tick refinement survived only as a 4--12%
  failed screening residual because implied liquidity is missing, maturity/roll is exactly
  confounded, placement policy is not identified, and the engines do not implement CME's
  native allocation semantics. No topic card was created.

Final status is **failed-closed** with hostile T0 1--7%, point 3.5%. A successor must be a
new market-native restricted-model descendant with a theorem formally separated from
controlled bisimulation/causal abstraction, compatible native clocks and RNG namespaces,
and a qualified prospective bridge. The current generic card authorizes no further work.

Four later outcome-blind rounds also created no card. The graph-complement round
showed that apparent queue holonomy closes only after deleting PriorityID, conditional-order
closure is fixed-point/ECA semantics, and iceberg regeneration is directly anticipated by
latent-liquidity theory. Its prospective mechanisms had hostile-T0 lower bounds of 2--7%.
See `papers/proposal/ecomd_structural_complement_reselection_gminus1_result_2026-08-25.md`.

The latest asset-first round required the truth contract before the question. No public
laboratory, on-chain, or exchange-L3 asset passed assignment, complete state, independent
same-estimand replication, sealed holdout, rights, and the 15% hostile-T0 lower-bound gate.
TSE's announced 2027 STR tick controller was strongest at 10--17%, so it remains a watch
rather than a card or sandbox. See
`papers/proposal/ecomd_external_truth_asset_first_reselection_gminus1_result_2026-08-25.md`.

## Validation state

At installation, both validators passed with 119 route nodes, 125 typed edges, 364 route
locators, one parked discovery card, 39 evidence records, 12 failure families, and 20
primary-work assignments. The terminal audit changes that card to failed-closed and adds
five decisive primary-work records. Current validation is 148 route nodes, 154 edges and
476 route locators; Discovery governance has one failed-closed card, 53 clean external
evidence records, zero tainted sandbox results, 12 failure families, 25 primary assignments,
one transition and zero authorized sandboxes.
