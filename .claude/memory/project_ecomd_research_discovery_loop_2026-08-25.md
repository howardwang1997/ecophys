---
name: EcoMD research Discovery Loop
description: Forward-only scientific topic-selection protocol installed after a primary-source audit of Discovery Loop, Science-Discovery, AI-scientist evaluation and falsification systems. The machine contract separates disposable question-search probes from confirmation and treats the 15% hostile-T0 floor as an active-only, uncalibrated brake rather than a terminal truth criterion. No Nature-grade topic is active and no exploration sandbox is currently authorized.
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
  lower bound of at least 15%. The floor is provisional and uncalibrated, applies only to
  `active` status, and cannot by itself set `failed_closed`; a terminal decision requires an
  independently evidenced scientific or contract failure.
- D-3/D-2 work has no probability floor. A bounded D-1 or DX information action below 15%
  requires no already-failed hard gate plus positive robust value of information. Comparable
  prospective forecasts are append-only in `research/discovery/forecast_ledger.yaml`; the
  floor is reviewed only after at least twenty full-T0 targets resolve.
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
- Prospective probability and resolution ledger: `research/discovery/forecast_ledger.yaml`
- Prospective topic-search counts and dispositions: `research/discovery/search_cycle_ledger.yaml`
- Validator: `scripts/validate_research_discovery.py`
- Pull-request history check: `.github/workflows/research-governance.yml`
- Fail-closed launcher and incident handler: `scripts/run_research_discovery_sandbox.py` and
  `scripts/quarantine_research_discovery_sandbox.py`
- Outcome-free OCI probe, source-bound report and verifier:
  `research/discovery/conformance/` and
  `scripts/test_research_discovery_oci_conformance.py`
- Operational topic-search runbook and worksheet:
  `docs/research_topic_exploration_runbook.md` and
  `research/discovery/templates/screening_topic_worksheet.md`
- Mutation tests: `tests/test_research_discovery.py`,
  `tests/test_run_research_discovery_sandbox.py`, and
  `tests/test_research_discovery_oci_conformance.py`
- First formal rerun: `papers/proposal/ecomd_discovery_loop_reselection_result_2026-08-25.md`

The protocol stages are D-3 question framing, D-2 evidence compilation, D-1 hostile
falsification, D0 outcome-blind freeze, D1 exploratory evidence, and D2 held-out
confirmation. Search history is append-only; revisions are child cards rather than edits
that erase a failed parent.

An optional asset-level DX sandbox sits outside route status. It repairs the circularity in
which all empirical feedback was forbidden until a topic had already passed a high-confidence
activation gate. Schema v2 requires hashed provenance/snapshot/partition inputs, explicit
unit membership, cumulative asset-campaign reservations, and one canonical event chain that
    freezes each hypothesis, falsifier, multiplicity family, test set, unit set and code/config
before its receipt. Every terminal result is `sandbox_exploratory_tainted`: it can appear
only in `sandbox_motivation_refs`, never in novelty, killer, decision, D2 or paper-claim
evidence. The validator now has a protected-base mode: old manifests, decisions, inputs and
artifacts are immutable, event ledgers and the taint registry are prefix-only, and a new
    sandbox must be merged as authorization-only before it can execute. The research baseline
    now requires the PR workflow check and forbids force pushes/deletion and administrator bypass.
    Schema v2 also binds an OCI image, launcher and incident-handler digest, no network, a read-only root, no
    repository-tree or secrets mount, CPU-only access, a single frozen config-file input, absent
    confirmation outcomes and a byte-bounded stdout tar. The launcher enforces and receipts this
    contract. Its source-bound, outcome-free local Colima/arm64 probe passed UID/GID, capability,
    seccomp, network, mount, cgroup, device, secret, repository and tar checks, including timeout,
    output-limit and invalid-tar rejection. An ambiguous interruption is never retried: the named
    container is removed, outcome exposure is assumed, the full branch budget is charged and the
    sandbox becomes permanently `quarantined`. Independent runtime review and separate asset-level
    authorization remain mandatory. Synthetic confirmation must use a frozen future-public-randomness seed
derivation; known reserved seed numbers are not a holdout. No sandbox is authorized.

The operational search is now a two-speed funnel: at most twelve raw model forks, six quick
screens, three collision/truth-contract screens, two full hostile audits and one machine card.
Raw questions come from unresolved model disagreements, new truth/control capabilities,
market-native actions/constraints, or cross-domain theorems with an exact market obstruction.
They are routed as theory/mechanism, measurement, empirical intervention, or simulator method,
so a weak raw idea does not immediately incur every two-engine and real-bridge burden. Survivors
are selected by Pareto dominance and then their weakest link. Every raw program and disposition is
append-only. Before a program enters the full fifteen-work audit, freeze its exact subject and
full-T0 forecast; a later probability is diagnostic only.

Cycle 9 audited the probability rule and eight asset-triggered formulations. The previous
eight bounded cycles contained 48 formulations; zero of the 47 tabulated lower endpoints
reached 15%, but all 48 also failed an independent hard gate. Because those intervals were
elicited after audit rather than forecast prospectively, they do not calibrate the floor.
Cycle 9 therefore retained 15% only as a conservative brake on expensive activation, added
the forecast ledger and robust information-value rule, and prohibited probability-only
terminalization. Its first entry forecasts a narrow future Rule 605 bridge component and
does not count as a full-T0 calibration outcome.

Cycle 10 was the first prospective two-speed execution. Twelve raw questions became six quick
screens, three collision screens and two full audits. Metaorder-origin discrimination failed
because anonymous public order flow cannot identify a parent-order intervention and simulator
agreement only recovers programmed mechanisms. Quenched-liquidity recovery failed because static
rate mixtures can produce algebraic relaxation without rare regions and localized contact-process
coupling is imposed rather than market-native. `nonlinear_liquidity_echo` is deferred only as a
paper theorem question about whether an observable native phase exists; it is not a candidate.
No card, sandbox, outcome or execution was authorized.

Cycle 11 sampled market--physical coupling and anomalous relaxation. Twelve raw programs became
six quick screens and three six-work collision screens; no program reached F3. LLAMMA finite-rate
loop loss decomposed into the protocol's adiabatic conversion loss and established LVR or
arbitrage-timing terms. LOB Mpemba relaxation reduced to generic Markov slow-mode cancellation
under an analyst-chosen initial family and metric. Carbon-inventory condensation failed economic-
entity split invariance. The funnel now requires imported physical effects to have a market-native
control parameter and survive representation, unit, clock, initial-family and metric changes. No
card, forecast, sandbox, outcome or execution was authorized.

Cycle 12 began from same-estimand market-design disagreements and made EBS Conditional Price
Increments the first prospectively forecast F3 audit. The frozen candidate proposed a regime law
in `chi = sigma*sqrt(tau)/delta` and `rho = lambda*tau`; its full-T0 forecast was 5--25%, point
12%, before the fifteen-work neighborhood opened. The clean Brownian case reduced to the
reflection-principle first-passage probability. Holding both controls fixed while changing marked
informed-flow composition or matched-variance jump tails changed or reversed the response.
Official EBS MBP also does not use individual OrderID entries, CPI selection is state-gated and
trader-chosen, and neither two native physical-time simulator lineages nor an independent real
fine-price/slow-cancel mechanism closed the same-estimand contract. The forecast resolved false
with Brier 0.0144; one resolution does not calibrate the 15% active-status brake. The cycle added
same-estimand sign-disagreement and dimensionless parameter-completion quick gates. No card,
sandbox, outcome, data action, simulation, implementation, outreach or compute was authorized.

Cycle 13 moved from EBS price--time parameters to bilateral credit as the market-native interaction
state. Twelve programs became six quick screens and three six-work collision screens; none reached
F3. Aggregate credit, degree, and binary topology failed a labelled-capacity/quote-alignment twin.
One- versus two-pool credit split into static feasible-set inclusion and online class crowding.
Gross versus NOP exhaustion reduced to weighted path total variation versus net exposure. Direct
QCLOB, credit-network, resource-pooling, bilateral-credit ABM, OTC-network, and netting priors
occupied the broad core, while population credit state and controller history were not public. The
protocol now completes labelled capacities and allocation policy and separates static, online, and
endogenous response before escalating a network law. No card, forecast, sandbox, outcome, data
action, simulation, implementation, outreach, purchase or compute was authorized.

Cycle 14 resolved the Cycle 10 paper-level echo question and then sampled protocol-native stored
state and ranked loss transfer. Twelve programs became six quick screens and two collision
screens; none reached F3. The paired-minus-singles liquidity residual is generically a second-order
Volterra cross-kernel, and native order age moves with one characteristic velocity rather than a
heterogeneous phase field. Ranked ADL is directly occupied by current impossibility, online-
learning and risk-minimization work. GMX pending impact is a documented closeability corner that
reduces to deterministic feasibility when the complete protocol state is supplied; dynamics still
need future flow, oracle, keeper and policy kernels. Vega parked pegs and Eurex synthetic-path
allocation deduplicated against existing closures. The funnel now tests any echo claim for a native
phase coordinate and a legal state-preserving phase operation. No card, forecast, sandbox, outcome,
data action, simulation, implementation, outreach, purchase or compute was authorized.

Cycle 15 screened publicly specified market-maker obligations and liquidity-reward controllers.
Twelve programs became six quick screens and three collision screens; none reached F3. MRX
cross-role compliance aggregation strictly enlarges a feasible set but does not assign quote
migration; Phlx is the same Nasdaq rule family. JPX daily sponsorship is selected jointly with
security, target interval, weight, payment, ranking and quote obligations, so it is not a scalar
clock intervention. Polymarket relative rewards reduce to a proportional contest and fail common-
scale and quote-owner-permutation invariance. MOEX sufficient-volume crossing only releases an
obligation at an endogenous stopping time. The durable lesson is to separate compliance from
action, a contract label from an isolated intervention, and relative score from absolute market
state. No card, forecast, sandbox, outcome, data action, simulation, implementation, outreach,
purchase or compute was authorized.

Cycle 16 returned to the core simulated-market validity question. Twelve programs became six quick
screens, three collision screens and one prospectively frozen F3 audit. No exact paper was found
that uses a predeclared simulator-interventional score to predict several unseen real market-rule
responses, but the formulation failed off-support adaptation, independent-intervention replication,
common action-language and prospective field-asset contracts. Task-conditioned adequacy reduced to
established ABM surrogate, model-criticism, discrepancy and discrimination parents; stored-order
release after a volatility interruption failed assignment and no-pause-counterfactual gates and had
direct pause/auction priors. The frozen 10% forecast resolved false with Brier 0.0100. Two
all-negative full-T0 resolutions remain insufficient to recalibrate the 15% active-status brake.
The runbook now prevents a third zero-card cycle in the same parent/failure family unless a new
primary model fork, truth/control asset, or theorem removes a recorded blocker. No card, sandbox,
outcome, data action, simulation, implementation, outreach, purchase or compute was authorized.

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

Seven bounded runbook cycles have now also completed. Cycle 1 closed eight mechanism-native
worksheets under complete-state projection, exact-parent, same-estimand and field-contract
gates. Cycle 2 reversed the search direction and began with theorem objects. Its eight
formulations separated into false universals (including liquidity submodularity and literal
tick-grid moire) and exact reductions to monotone coupling, program sensitivity, integer
feasibility, sampled-data control, hybrid reachability or formal CDA conformance. Cycle 2's
hostile-T0 lower bounds were zero or one percent and its largest upper bound was seven
percent. Cycle 3 required a public replay capability before writing a physics narrative and
inspected pinned Manifest, Mangrove, OpenBook and Phoenix implementations. Its strongest
near miss, shared-capital global orders, exposed a real cross-market conservation coupling
but reduced to online packing/loss networks under fixed policy and arbitrary program dynamics
under unrestricted offer code; the protocols also lacked same-estimand failure/cleanup
semantics and public submission denominators. Its other seven objects reduced to queueing,
lazy deletion, grid strategies, sub-penny priority, scheduling, or deterministic program
execution. Cycle 4 then narrowed the strongest shared-capital residual to a theorem:
capital amplification, strong executable-quote integrity and coordination-free execution
cannot coexist under one bounded balance. The proof is valid but is exactly bounded-counter
non-confluence with escrow rights as the established remedy; price priority does not alter
the safety core. No cycle created a card or sandbox. See
`papers/proposal/ecomd_discovery_loop_topic_cycle_1_result_2026-08-25.md` and
`papers/proposal/ecomd_discovery_loop_topic_cycle_2_theorem_first_result_2026-08-25.md`, and
`papers/proposal/ecomd_discovery_loop_topic_cycle_3_capability_first_result_2026-08-25.md`, and
`papers/proposal/ecomd_discovery_loop_topic_cycle_4_shared_capital_trilemma_result_2026-08-25.md`.
Cycle 5 then required complete submitted/rejected/landed intent exposure before proposing a
physics object. This capability is valuable, but complete-message latency races and Hyperliquid
rejected-order flow already occupy the strongest claims. Eight objects failed direct-prior,
message-refinement invariance, strategic-counterfactual or private-demand identification gates;
the largest hostile-T0 lower bound was three percent. See
`papers/proposal/ecomd_discovery_loop_topic_cycle_5_intent_truth_result_2026-08-26.md`.
Cycle 6 began from a precise one-parameter theory linking signed-flow persistence, rough volume,
rough volatility and power-law impact. A joint same-unit residual test is scientifically useful,
but the 2026 anchor already owns the central relation, public tapes do not identify parent-order
impact or core/reaction provenance, 24/7 crypto retains deterministic and global-session regimes,
and stochastic clocks separate event-time memory from physical-time impact. Four descendants
failed closed; the largest hostile-T0 lower bound was five percent. See
`papers/proposal/ecomd_discovery_loop_topic_cycle_6_scaling_closure_result_2026-08-26.md`.
Cycle 7 then required a complete-state, representation-invariant conservation law or symmetry
that forced a nontrivial response. Transaction charges reduced to incidence-matrix nullspaces;
open-interest channels were bookkeeping rather than sufficient margin state; STP depended on a
configurable identity partition; L2 aggregation was classical strong lumpability; and cross-impact
and CFMM response laws had direct no-arbitrage or geometric parents. Six descendants failed closed
and the largest hostile-T0 lower bound was four percent. See
`papers/proposal/ecomd_discovery_loop_topic_cycle_7_conservation_symmetry_result_2026-08-26.md`.
Cycle 8 then asked whether disagreement between independent market simulators could expose a
missing physical mechanism. Equal complete kernels imply conformance, while event-versus-batch
propagation under a frozen generator is established operator splitting. Native adaptive ABIDES,
PAMS, and Bourse policies instead receive different histories, so their disagreement compares
different market mechanisms rather than one numerical estimand. Three nonduplicate descendants
failed closed and the largest hostile-T0 lower bound was three percent. See
`papers/proposal/ecomd_discovery_loop_topic_cycle_8_cross_engine_discrepancy_result_2026-08-26.md`.

After Cycle 16, a separate source-only capability audit tested five possible exceptions to the
new search-family saturation rule. QuantReplay v12 and `orderbook` v0.26.0 improve exchange-engine
recovery but do not checkpoint complete adaptive populations, RNG namespaces, scheduling/calendar,
and external strategy state. `lobsim` remains replay; DiffLOB conditions on future regimes rather
than legal actions; and the current latency/impact queue-reactive model adds no field
counterfactual. The append-only `research/discovery/reentry_trigger_ledger.yaml` records zero
qualified triggers, so Cycle 17 remains unopened. See
`papers/proposal/ecomd_reentry_capability_trigger_audit_2026-08-26.md`.

A subsequent registry-first truth-asset audit screened the live AEA RCT metadata and bounded OSF
registration queries without opening outcomes or mutable source projects. It found immutable
pre-data randomized asset-market registrations, but no source that jointly freezes a complete
order lifecycle, replayable pre-state, dated licensed raw release, untouched confirmation source,
and independently governed same-estimand replication. This is a hard contract failure rather than
a probability closure. The sixth trigger entry is `not_trigger`; Cycle 17 remains unopened. See
`papers/proposal/ecomd_reentry_truth_asset_registry_audit_2026-08-26.md`.

## Validation state

At installation, both validators passed with 119 route nodes, 125 typed edges, 364 route
locators, one parked discovery card, 39 evidence records, 12 failure families, and 20
primary-work assignments. The terminal audit changes that card to failed-closed and adds
five decisive primary-work records. After sixteen bounded topic cycles, current validation is
235 route nodes, 243 edges and 850 route locators; Discovery governance has one failed-closed
card, 212 clean external evidence records, zero tainted sandbox results, 12 failure families,
25 primary assignments, one transition, zero authorized sandboxes, seven prospective search cycles
with 84 raw questions, six re-entry trigger audits with zero qualified, and three prospective
forecasts. Both resolved full-T0 forecasts are false;
the Rule 605 component forecast remains unresolved. Two all-negative full-T0 resolutions are still
insufficient to calibrate the 15% floor.
