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

The first bounded execution of the operational runbook then froze eight mechanism-native
worksheets instead of continuing open-ended ideation. Reduce-only and close-only were the
strongest ideas, but complete state reduced them to account-capacity projection and open-
interest monotonicity; MinQty/AON, market-maker protection, cancel-on-disconnect, protection
collars, Rule 611, and Rule 201 failed parent-problem, hidden-state, same-estimand, assignment,
or saturated-prior gates. Those hard failures closed the formulations; their conservative
hostile-T0 lower bounds were 0--6%, so none was eligible for active status. The
[topic-cycle-1 result](papers/proposal/ecomd_discovery_loop_topic_cycle_1_result_2026-08-25.md)
creates zero cards and authorizes no sandbox or outcome access.

The second bounded cycle began from theorem objects rather than venue features. Exact finite
counterexamples closed universal liquidity submodularity and literal cross-venue tick moire;
the remaining no-passing, stability-radius, integer-lattice, funding-control, liquidation and
verified-matching formulations reduced to established mathematics or conformance work. With
hostile-T0 lower bounds of 0--1%, the
[theorem-first topic-cycle-2 result](papers/proposal/ecomd_discovery_loop_topic_cycle_2_theorem_first_result_2026-08-25.md)
also creates zero cards and authorizes no execution.

The third bounded cycle required a public replay capability before constructing another
physics analogy. Pinned Manifest, Mangrove, OpenBook and Phoenix implementations exposed
real shared-capital, settlement, expiry, regeneration and scheduling mechanisms, but none
survived reduction and truth-contract gates. Shared-capital global orders were the strongest
near miss at hostile T0 5--17% (10% point): fixed-policy dynamics are online packing/loss
networks, unrestricted offers are arbitrary programs, the protocols do not share failure and
cleanup semantics, and confirmed ledgers omit losing submissions. The
[capability-first topic-cycle-3 result](papers/proposal/ecomd_discovery_loop_topic_cycle_3_capability_first_result_2026-08-25.md)
therefore creates zero cards and authorizes no chain query, simulation, sandbox, or outcome
access.

The strongest cycle-3 residual was then narrowed to a formal trilemma. One bounded balance
cannot simultaneously support amplified cross-market promises, guarantee every displayed
quote, and let markets execute without shared coordination. The statement is correct, but
its two-market proof is exactly bounded-counter non-confluence; escrow rights are the
established remedy, and price priority only selects the winner after coordination. The
[shared-capital trilemma audit](papers/proposal/ecomd_discovery_loop_topic_cycle_4_shared_capital_trilemma_result_2026-08-25.md)
closes at hostile T0 1--6% and does not create a “liquidity CAP” topic card.

The fifth bounded cycle began from a stronger truth capability: complete submitted, rejected,
cancelled, replaced and executed intent logs. Such logs repair the loser/failed-message blind spot,
but they do not reveal private values, unsubmitted demand or strategic responses to a changed rule.
Complete-message latency races and Hyperliquid rejected-order flow already occupy the strongest
empirical claims; six other objects failed message-refinement invariance, reflected-queue,
client-policy or experimental-restriction gates. The
[intent-truth capability audit](papers/proposal/ecomd_discovery_loop_topic_cycle_5_intent_truth_result_2026-08-26.md)
therefore closes eight more routes, creates zero cards and authorizes no sandbox or outcome access.

The sixth bounded cycle began from a precise recent theory rather than another venue feature.
One core-flow persistence parameter is proposed to determine signed-flow persistence, rough
volume, rough volatility and power-law impact. A same-market joint residual test would be a
valuable falsifier, but the relation is already the direct 2026 theory claim, anonymous public
trades do not identify parent-order impact or core/reaction provenance, and 24/7 cryptocurrency
trading retains funding, settlement, quarter-hour and global-session regimes. Event-time memory
and physical-time impact are also not interchangeable under stochastic clocks. The
[scaling-closure audit](papers/proposal/ecomd_discovery_loop_topic_cycle_6_scaling_closure_result_2026-08-26.md)
therefore closes four descendants on independent hard gates. Its largest hostile-T0 lower bound
is 5%, so none was eligible for active status; the audit creates no topic card, sandbox or
execution authorization.

The seventh bounded cycle then searched complete-state, market-native conservation laws and
symmetries. Exact transaction balances restrict reachable states but do not determine event rates
or prices; perpetual open-interest creation/annihilation channels are bookkeeping rather than a
sufficient margin-risk state; and STP depends on a configurable identity partition. Exact L2
aggregation is the classical strong-lumpability problem, while cross-impact reciprocity and CFMM
curvature already have direct no-arbitrage and geometric parents. The
[conservation/symmetry audit](papers/proposal/ecomd_discovery_loop_topic_cycle_7_conservation_symmetry_result_2026-08-26.md)
therefore closes six descendants on independent hard gates. Its largest hostile-T0 lower bound
is 4%, so none was eligible for active status; the audit creates no topic card, sandbox or
execution authorization.

The eighth bounded cycle reversed the comparison: it asked whether disagreement between two
independent market simulators could reveal missing physics. If the complete transition kernel,
clock, actions, policy information and randomness coupling are identical, disagreement is a
conformance failure. With frozen policies, event-versus-batch disagreement reduces to established
operator-splitting error. With native adaptive agents, ABIDES, PAMS and Bourse expose different
histories and reaction opportunities, so they implement different market mechanisms rather than
one estimand. The
[cross-engine discrepancy audit](papers/proposal/ecomd_discovery_loop_topic_cycle_8_cross_engine_discrepancy_result_2026-08-26.md)
therefore closes three nonduplicate descendants on independent hard gates. Its largest
hostile-T0 lower bound is 3%, so none was eligible for active status; the audit creates no topic
card, sandbox or execution authorization.

The ninth bounded cycle started from prospective or controlled truth assets: amended Rule 605
execution reports, laboratory information treatments, Treasury central clearing, Uniswap-v4 fee
families, Solana capacity, HyperCore ordering, HIP-2 replenishment, and OMIE temporal refinement.
Five nonduplicate formulations failed independent novelty, identification, same-estimand, or
prospective-contract gates; three were exact descendants of existing closures. The
[asset-portfolio and probability-gate audit](papers/proposal/ecomd_discovery_loop_topic_cycle_9_asset_portfolio_and_probability_gate_result_2026-08-26.md)
creates zero cards and one prospective component-gate forecast. Across Cycles 1--8, none of the
47 tabulated hostile-T0 lower endpoints reached 15%, but all 48 formulations also failed an
independent hard gate. Those post-audit judgments cannot calibrate the threshold.

Cycles 10--13 then installed and exercised the two-speed funnel. Cycle 12 is the first completed
full audit with a genuinely prospective full-T0 forecast: EBS conditional price increments
motivated a proposed price--time commitment law in \(\chi=\sigma\sqrt{\tau}/\delta\) and
\(\rho=\lambda\tau\). The clean case reduced exactly to Brownian first passage; matching both
controls still allowed sign reversals under marked informed flow and different jump kernels;
public EBS MBP has no individual EBS order lifecycle; and the same-estimand simulator and field
replication contracts failed. The frozen 12% forecast therefore resolved false (Brier 0.0144), but
one outcome cannot calibrate the 15% active-status brake. The
[Cycle 12 result](papers/proposal/ecomd_discovery_loop_topic_cycle_12_price_time_commitment_result_2026-08-26.md)
creates zero cards and authorizes no execution.

Cycle 13 then kept the EBS setting but moved to its market-native bilateral-credit interaction.
Aggregate topology and total credit failed a labelled-capacity twin; one- versus two-pool credit
split into static feasible-set inclusion and online product crowding; and gross versus NOP
exhaustion reduced to weighted path variation versus net exposure. Direct QCLOB, credit-network,
resource-pooling, bilateral-credit ABM, OTC-network, and netting priors occupied the broad core,
while public data do not expose the population credit matrix or controller history. The
[Cycle 13 result](papers/proposal/ecomd_discovery_loop_topic_cycle_13_bilateral_credit_liquidity_result_2026-08-26.md)
therefore creates zero cards and no F3 forecast. The cycle adds a quick gate that separates static
pooling, online allocation, and endogenous response before a network statistic can be treated as
market state.

Cycle 14 resolved the strongest paper-only question deferred by Cycle 10 and sampled current
protocol-native residual state. The paired-pulse liquidity residual reduced to a generic
second-order Volterra cross-kernel, while common-velocity order age supplied no native phase
coordinate or state-preserving rephasing operation. Ranked ADL was directly occupied by current
impossibility, online-control, and risk-minimization work. GMX pending impact was a documented
complete-state closeability predicate rather than a new collective law, and Vega/Eurex descendants
deduplicated against existing hosted-order and implied-liquidity closures. The
[Cycle 14 result](papers/proposal/ecomd_discovery_loop_topic_cycle_14_residual_state_result_2026-08-26.md)
creates zero cards and no F3 forecast.

Cycle 15 then tested whether public market-making obligations and liquidity rewards supply a
stronger control object. MRX/Phlx role aggregation reduced to compliance feasible-set pooling plus
private member policy; JPX daily sponsorship bundled its clock with selected securities, weights,
targets, payments, rankings and quote requirements; and Polymarket/dYdX normalized rewards reduced
to proportional contests that fail common-scale and quote-owner-permutation invariance. A MOEX
volume hit merely releases an obligation at an endogenous stopping time. The
[Cycle 15 result](papers/proposal/ecomd_discovery_loop_topic_cycle_15_market_maker_obligation_result_2026-08-26.md)
therefore creates zero cards and no F3 forecast. Its reusable rule is simple: a compliance or
reward controller is not an assigned market action.

Cycle 16 returned to the central simulator question: can a score computed before a field rule
change predict which market simulator will forecast the change correctly? The narrow empirical
gap survived the exact-paper search, but the frozen formulation did not. Simulator-native
interventional consistency leaves real off-support adaptation unidentified; two rule changes are
only two independent policy environments; learned and structural simulators lack a frozen common
action language; and prospective TSE, CME, SEC and pause assets do not close one assignment, state,
licence and same-estimand contract. The
[Cycle 16 result](papers/proposal/ecomd_discovery_loop_topic_cycle_16_prospective_simulator_validity_result_2026-08-26.md)
therefore creates zero cards. Its prospectively frozen 10% full-T0 forecast resolved false (Brier
0.0100). Two all-negative resolutions are insufficient to recalibrate the 15% active-status brake.

The subsequent capability-trigger audit checked recent open engines and simulator papers before
allowing another cycle. QuantReplay v12 persists detailed resting-book state, and `orderbook`
v0.26.0 has a strong matching-engine checkpoint, but neither captures the complete adaptive market
population, all RNG namespaces, scheduler/calendar, and external strategy state. `lobsim` is
deterministic replay; DiffLOB conditions on future regimes rather than legal market actions; and the
latest latency/impact queue-reactive model supplies another simulator rather than external
counterfactual truth. The
[trigger audit](papers/proposal/ecomd_reentry_capability_trigger_audit_2026-08-26.md) therefore
records five watch entries and **zero qualified triggers**. A second outcome-blind screen then
searched the live AEA RCT Registry and bounded OSF registration queries for randomized,
event-level asset-market truth. Prospective laboratory market episodes exist, but none freezes a
complete order lifecycle, dated licensed raw release, untouched confirmation source, and
independent same-estimand replication. The
[registry audit](papers/proposal/ecomd_reentry_truth_asset_registry_audit_2026-08-26.md) adds one
`not_trigger` entry. A third source-only check then audited Sfendourakis's 2026 unified
signal-driven/queue-reactive framework. It supplies two serious models, but they do not share a
complete state and legal intervention, make no opposite same-estimand response prediction, and
retain an unobserved efficient price rather than assigned external truth. The
[discovery-bottleneck and truth-asset preflight](papers/proposal/ecomd_discovery_bottleneck_truth_asset_preflight_2026-08-26.md)
therefore records the seventh `not_trigger`; zero triggers qualify and Cycle 17 remains unopened.

## Research Discovery Loop

Topic selection is a versioned scientific process rather than idea generation followed by
experimentation. The [protocol](research/discovery/protocol.yaml) and
[method note](docs/research_discovery_loop.md) evaluate a complete discovery episode across
question formation, execution, interpretation, revision, nulls, failures, and provenance.
The [topic-exploration runbook](docs/research_topic_exploration_runbook.md) gives the
operational two-speed funnel, archetype routing, killer-twin, prior-art, ranking, and
escalation sequence. Prospective cycle counts and dispositions are append-only in the
[search-cycle ledger](research/discovery/search_cycle_ledger.yaml).
Proposed exceptions to search-family saturation are append-only in the
[re-entry trigger ledger](research/discovery/reentry_trigger_ledger.yaml); only a qualified entry
can authorize another candidate-harvest cycle in that family.

The first seven prospective funnel cycles exposed a portfolio imbalance: 53 of 84 raw programs
were theory/mechanism questions, while only four were measurement methods. In a future
**unsaturated** 12-program cycle, F0 sampling therefore targets at least two measurement methods,
at least two empirical interventions, and at most six theory/mechanism programs. These targets do
not reserve advancement slots. If the family is saturated and no trigger qualifies, the loop may
instead retain a paper-only capability-build preflight for the named blocker. Such a preflight is
infrastructure, not a topic status; it must freeze the estimand family, assignment/interference,
event lifecycle and replay state, rights/ethics/release, untouched confirmation, independent
replication, cost, and stop rules. It cannot authorize candidate harvesting, outreach,
implementation, outcomes, or execution.

The forward stages are:

1. **D-3:** harvest at most 12 market-native model forks, quick-screen at most 6, and expand
   only the strongest 3 into complete question contracts; imported physical effects must expose
   a market-native control parameter and survive legal representation, unit, clock, initial-family,
   and metric changes; claimed opposite-sign priors must share one estimand, and proposed
   dimensionless laws must survive a parameter-completion twin; network/shared-capacity claims
   must retain labelled capacities and allocation policy and separate static, online, and
   endogenous response layers;
2. **D-2:** route each survivor as theory/mechanism, measurement, empirical intervention, or
   simulator method; only the strongest 2 receive a novelty manifest with at least 15 primary
   works and full failure-family mapping;
3. **optional DX:** after a separate asset-level authorization, use only an explicitly
   enumerated disposable split for a zero-cost, CPU-only probe whose hypotheses, falsifiers,
   test family, unit IDs, code/config hashes, receipts, and terminal result share one hash chain;
4. **D-1:** try to kill it with exact-prior reductions, at least two minimal counterexamples,
   the archetype-specific truth contract, the project-wide validation contract required by the
   intended claim, and a contamination audit; freeze the F3 subject and its full-T0 forecast
   before opening the full evidence neighborhood;
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
next action. The 15% floor is a provisional, uncalibrated brake on costly D0/D1 activation,
not a confidence bound or a truth criterion. Probability alone cannot set `failed_closed`.
D-3/D-2 work has no probability floor; bounded D-1 or DX information acquisition instead
requires positive robust value of information and no already-failed hard gate. Prospective
forecasts and later resolutions are append-only in the
[forecast ledger](research/discovery/forecast_ledger.yaml); the floor is reviewed only after
at least twenty comparable T0 forecasts resolve. High story quality, LLM consensus,
retrospective rediscovery, or a benchmark score cannot compensate for a failed gate. The
source audit and first rerun are recorded in
the [formal selection result](papers/proposal/ecomd_discovery_loop_reselection_result_2026-08-25.md),
and the subsequent controlled/on-chain rerun is recorded in the
[post-discovery result](papers/proposal/ecomd_post_discovery_reselection_gminus1_result_2026-08-25.md).
The latest graph-complement and prospective-mechanism audit is in the
[structural-complement result](papers/proposal/ecomd_structural_complement_reselection_gminus1_result_2026-08-25.md).
The subsequent atomic, cross-margin, implied-liquidity and experimental-asset audit is in
the [atomic/margin/experimental result](papers/proposal/ecomd_atomic_margin_experimental_reselection_gminus1_result_2026-08-25.md).
The subsequent asset-first truth-contract audit is in the
[external-truth result](papers/proposal/ecomd_external_truth_asset_first_reselection_gminus1_result_2026-08-25.md).
The first bounded worksheet cycle is in the
[topic-cycle-1 result](papers/proposal/ecomd_discovery_loop_topic_cycle_1_result_2026-08-25.md).
The second bounded theorem-first cycle is in the
[topic-cycle-2 result](papers/proposal/ecomd_discovery_loop_topic_cycle_2_theorem_first_result_2026-08-25.md).
The third bounded capability-first cycle is in the
[topic-cycle-3 result](papers/proposal/ecomd_discovery_loop_topic_cycle_3_capability_first_result_2026-08-25.md).
The narrow fourth-cycle theorem audit is in the
[shared-capital trilemma result](papers/proposal/ecomd_discovery_loop_topic_cycle_4_shared_capital_trilemma_result_2026-08-25.md).
The fifth capability-first audit is in the
[intent-truth result](papers/proposal/ecomd_discovery_loop_topic_cycle_5_intent_truth_result_2026-08-26.md).
The sixth theory-led falsification audit is in the
[scaling-closure result](papers/proposal/ecomd_discovery_loop_topic_cycle_6_scaling_closure_result_2026-08-26.md).
The seventh conservation/symmetry audit is in the
[conservation/symmetry result](papers/proposal/ecomd_discovery_loop_topic_cycle_7_conservation_symmetry_result_2026-08-26.md).
The eighth discrepancy-first simulator audit is in the
[cross-engine discrepancy result](papers/proposal/ecomd_discovery_loop_topic_cycle_8_cross_engine_discrepancy_result_2026-08-26.md).
The ninth asset-first and probability-policy audit is in the
[asset-portfolio result](papers/proposal/ecomd_discovery_loop_topic_cycle_9_asset_portfolio_and_probability_gate_result_2026-08-26.md).
The first two-speed funnel execution is in the
[model-discrimination Cycle 10 result](papers/proposal/ecomd_discovery_loop_topic_cycle_10_model_discrimination_funnel_result_2026-08-26.md):
twelve raw questions became six quick screens, three collision screens, two full audits, one
paper-only deferred question, and zero machine cards.
The market--physical relaxation follow-up is in the
[Cycle 11 result](papers/proposal/ecomd_discovery_loop_topic_cycle_11_market_physical_relaxation_result_2026-08-26.md):
twelve raw questions became six quick screens and three collision screens; all three closed on
exact decomposition, generic-parent, or economic-unit invariance gates before F3, with zero cards.
The price--time commitment follow-up is in the
[Cycle 12 result](papers/proposal/ecomd_discovery_loop_topic_cycle_12_price_time_commitment_result_2026-08-26.md):
twelve raw questions became six quick screens, three collision screens and one prospectively
forecast full audit; the sole F3 program failed exact-parent, parameter-completion, lifecycle and
same-estimand gates, so its 12% full-T0 forecast resolved false and no card was created.
The bilateral-credit follow-up is in the
[Cycle 13 result](papers/proposal/ecomd_discovery_loop_topic_cycle_13_bilateral_credit_liquidity_result_2026-08-26.md):
twelve raw questions became six quick screens and three collision screens; all three closed on
labelled-state insufficiency, resource-pooling, path-geometry, direct-prior, or private-state gates
before F3, with zero cards and no new forecast.
The residual-state and loss-transfer follow-up is in the
[Cycle 14 result](papers/proposal/ecomd_discovery_loop_topic_cycle_14_residual_state_result_2026-08-26.md):
twelve raw questions became six quick screens and two collision screens; the deferred echo,
ranked ADL, stored pending impact, parked pegs, and synthetic allocation all closed or
deduplicated before F3, with zero cards and no new forecast.
The market-maker obligation and liquidity-reward follow-up is in the
[Cycle 15 result](papers/proposal/ecomd_discovery_loop_topic_cycle_15_market_maker_obligation_result_2026-08-26.md):
twelve raw questions became six quick screens and three collision screens; compliance pooling,
selected temporal contracts, normalized reward contests and endogenous obligation release all
closed before F3, with zero cards and no new forecast.
The prospective simulator-validity follow-up is in the
[Cycle 16 result](papers/proposal/ecomd_discovery_loop_topic_cycle_16_prospective_simulator_validity_result_2026-08-26.md):
twelve raw questions became six quick screens, three collision screens and one prospectively
forecast full audit; off-support adaptation, intervention-level pseudoreplication, common-action
semantics and field-asset contracts closed the F3 route, with zero cards.

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
