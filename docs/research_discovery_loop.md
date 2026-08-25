# EcoMD research discovery loop

**Effective date:** 2026-08-25
**Scope:** successor-topic selection for simulated markets, market physics, and financial physics
**Machine contract:** [`research/discovery/protocol.yaml`](../research/discovery/protocol.yaml)

This document governs forward topic selection. It does not reopen a closed route. The
[research-route graph](../.claude/memory/research_route_knowledge_graph.yaml) remains the
source of truth for route status and lineage. [Plan v4](../papers/proposal/plan_v4_ncs.md)
is retained as a closed gate and budget record, not as an active scientific plan. A route
that survives this loop receives a new route-specific plan.

## What was learned from public discovery systems

The public landscape supports a useful architecture, but no single system supplies a
scientifically sufficient topic selector.

- [Discovery Loop](https://www.discoveryloop.com/) describes a high-throughput
  propose--run--learn vision. As of the audit date it exposes no public technical paper,
  code, benchmark, or license, so it is inspiration rather than an implementation
  dependency.
- [Aether](https://github.com/Science-Discovery/Aether) is a capable research workbench
  with literature tools, RAG, skills, sessions, and workflow memory. It does not establish
  that a generated claim is new or true.
- [AI-Newton](https://github.com/Science-Discovery/AI-Newton) shows the value of explicit
  concepts, laws, and cross-experiment generalization. Its current proof of concept
  rediscovers classical laws inside human-specified experiments and a physical DSL; it is
  not an open-topic novelty test.
- [*Measuring AI Scientists: From Exams to Discovery*](https://doi.org/10.26434/chemrxiv.15007582/v1)
  is a ChemRxiv v1 Perspective posted on 2026-08-18. It proposes the discovery episode
  as the evaluation unit, but provides no companion task set, scoring protocol, code,
  data, or leaderboard. It must not be treated as a released “AI Scientist Benchmark.”
  The executable nearby work is
  [Scientific Discovery Evaluation](https://arxiv.org/abs/2512.15567), whose scenario and
  project levels show why quiz accuracy is not a substitute for iterative discovery.
- [SDE-Harness](https://github.com/HowieHwong/sde-harness) and
  [AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2) contribute history-aware
  loops and explicit experiment trees. Branching, debugging, and paper generation are
  workflow capabilities, not evidence of scientific value. AI Scientist v2 also uses a
  restricted source-code license and executes model-written code, so EcoMD does not vendor
  it.
- [AutoDiscovery](https://github.com/allenai/asta-autodiscovery) is the closest public
  system for data-driven question search. Its belief-change reward is useful for allocating
  exploratory attention, but model surprise is not correctness, novelty, or confirmation;
  repeated adaptive search on one dataset creates a multiplicity problem.
- [ResearchBench](https://aclanthology.org/2026.findings-acl.644/) usefully decomposes
  ideation into inspiration retrieval, hypothesis composition, and ranking. Its gold
  hypotheses are published successes and it does not execute or update from experiments,
  so the decomposition is an ideation front end rather than proof of discovery.
- [DiscoveryWorld](https://github.com/allenai/discoveryworld),
  [DiscoveryBench](https://github.com/allenai/discoverybench), and
  [ScienceAgentBench](https://github.com/OSU-NLP-Group/ScienceAgentBench) make tasks,
  actions, code, costs, and histories more measurable. Much of their target material is a
  fixed world or a published workflow, so success can still be rediscovery.
- [petri-bench](https://www.petri-labs.org/bench/report) is a particularly important
  collision: it already includes procedurally fresh causal-discovery tasks over a market
  simulator, objective process scoring, and multiplicity auditing. A simple disciplined
  experimental design substantially outperforms the tested frontier agents. Therefore a
  new “hidden parameter in a simulated market” benchmark is not a viable EcoMD topic.
- [POPPER](https://github.com/snap-stanford/POPPER) motivates sequential falsification,
  while [XScientist](https://github.com/smileformylove/XScientist),
  [Robin](https://github.com/Future-House/robin), and
  [Finch](https://github.com/Future-House/finch) motivate immutable failure branches,
  claim-to-evidence links, and multiple analysis paths. These mechanisms improve process
  integrity; they do not turn agent agreement into independent replication.

The nearby evaluations form a capability ladder, not interchangeable discovery scores:

| Layer | Representative evaluation | What it measures | Why it is not prospective discovery |
|---|---|---|---|
| Closed academic knowledge | [HLE](https://doi.org/10.1038/s41586-025-09962-4) | Expert-level exact or multiple-choice answers and calibration | No autonomous question choice or experiment loop |
| Research subtask | [FrontierScience](https://arxiv.org/abs/2601.21165) | Original Olympiad problems and supplied PhD research subtasks | The problem is already specified; execution is mainly a textual answer |
| Ideation | [ResearchBench](https://aclanthology.org/2026.findings-acl.644/) | Inspiration retrieval, hypothesis composition, and ranking | Gold hypotheses are published successes and no experiment updates them |
| Data-driven rediscovery | [DiscoveryBench](https://github.com/allenai/discoverybench) and [BAISBench](https://doi.org/10.1093/bioinformatics/btag227) | Reconstructing workflows or established conclusions from data | Published targets create hindsight and contamination risk |
| End-to-end rediscovery | [ResearchClawBench](https://arxiv.org/abs/2606.07591) | Code, artifacts, and reports against a hidden published target | The target result already exists; exceeding its rubric is not independent validation of novelty |
| Interactive simulated loop | [DiscoveryWorld](https://github.com/allenai/discoveryworld) | Hypothesis--experiment--analysis actions in procedural worlds | Success is bounded by the simulator and public task family |

[NLPCC 2026 Task 9 AISB](https://github.com/ResearAI/NLPCC-2026-Task9-AISB) is
a separate shared task with replay and fabrication checks; it is not an implementation of
the ChemRxiv Perspective, and it had no final public leaderboard at the audit date. The
acronym `AISB` is therefore not a stable project identity.

The version, license, role, and limitation used in this audit are frozen in the
[evidence registry](../research/discovery/evidence_registry.yaml). Repositories without a
usable license are not copied into EcoMD. We reuse protocol ideas through an independent,
small implementation.

## Evidence pattern at the target journals

A separate audit of adjacent *Nature Computational Science* and *Nature Machine
Intelligence* papers prevents the loop from optimizing only for novelty wording. The
recurrent pattern is stronger than “a new market effect in two simulators”:

- an object, theorem, or algorithm that does not reduce to a mature parent problem;
- analytic truth, a gold-standard simulator, or a real instrument measuring the **same
  estimand**;
- transfer across genuinely different systems, scales, or out-of-distribution regimes;
- hard negatives, known failure regions, uncertainty or formal error control;
- strong equal-budget baselines and a recovery--cost or accuracy--cost advantage for a
  method claim;
- for sim-to-real claims, the same action--state--observation loop in simulation and the
  real system; and
- reproducible artifacts plus explicit nonclaims.

Representative evidence includes
[machine-guided path sampling](https://doi.org/10.1038/s43588-023-00428-z),
[TrajCast](https://doi.org/10.1038/s42256-026-01227-7),
[synthetic Lagrangian turbulence](https://doi.org/10.1038/s42256-024-00810-0),
[pySTED](https://doi.org/10.1038/s42256-024-00903-w), a
[chemical digital twin](https://doi.org/10.1038/s43588-025-00857-y), and
[parallel symbolic enumeration](https://doi.org/10.1038/s43588-025-00904-8). Their role
and limitation are frozen in the evidence registry. These are evidence-shape precedents,
not scientific dependencies or permission to transfer their claims to markets.

## Unit of work: a discovery episode

The unit of work is a versioned trajectory of decisions and evidence, not a topic sentence
or a generated paper. Each episode has three separately attributable layers:

1. **Question:** a checkable scientific object, intervention, observable, competing
   explanations, and value if either the positive or null result holds.
2. **Execution:** exact simulator/data contracts, controls, budget, provenance, and a
   distinction between exploratory and confirmatory evidence.
3. **Interpretation:** uncertainty, counterevidence, abstentions, claim boundaries, and the
   reason a branch advanced or stopped.

Agent fluency, number of generated ideas, number of trials, and workshop acceptance are
not scientific metrics. The loop ranks candidates by validity, residual novelty,
falsification efficiency, value of information, calibration, transfer, and traceability.

## Forward stages

### D-3 — frame the question

Begin with a market-native object, not a borrowed physics name or a preferred method. A
topic card must state:

- native state, admissible intervention, observable, and equivalences under which the
  object should be invariant;
- one exact question and one directional falsifiable statement;
- the theorem or phenomenon that would be new;
- explicit nonclaims and the venue-dependent scientific value.

If the question cannot be stated without naming an algorithm, analogy, or desired result,
it is not ready.

### D-2 — compile scenarios and evidence

Run literature-driven and data-driven exploration separately.

- Literature-driven branches start from contradictions, limiting assumptions, failed
  replications, measurement gaps, and mechanism boundaries in primary work.
- Data-driven branches may use only an exploratory split. Surprise or anomaly scores rank
  what to inspect; they never confirm a claim.

Each branch queries the route graph and maps local failure language to the canonical
[failure families](../research/discovery/failure_families.yaml). A novelty manifest freezes
the cutoff date, verbatim queries, inclusion/exclusion rules, at least 15 primary works,
claim-overlap classifications, and unresolved direct collisions.

### Optional DX — disposable exploration sandbox

The broad pre-activation ban has one narrow, separately authorized exception. A qualified
asset may be placed in a disposable sandbox before any topic becomes active. This is an
asset-level information-acquisition step, not a weaker topic status and not D1 evidence.
It avoids a circular process in which a topic must already be mature before any cheap
propose--run--learn feedback is permitted.

Every sandbox must freeze a machine-readable manifest and separate decision before access:

- one exploration split and at least one confirmation holdout, each represented by a sorted
  file of actual unit identifiers rather than only a split label;
- source, version, licence, hashed provenance, hashed snapshot manifest, asset fingerprint,
  partition hash, and a campaign identifier that aggregates repeated reservations;
- at most 28,800 CPU-seconds, 5,000,000,000 stored bytes, 16 branches, zero GPU-seconds,
  and zero monetary cost across the campaign;
- one canonical hash-chained `events.jsonl`: each `branch_opened` entry freezes the hypothesis,
  falsifier, multiplicity family, tests, seeds, and code/config digests before its
  `branch_finished` receipt and artifacts;
- an RFC3339 expiry, a stop rule, the exact authorized actions, and a terminal result whose
  epistemic class is permanently `sandbox_exploratory_tainted`; and
- explicit bans on confirmation access, paid data, production model work, EcoMD integration,
  external outreach, paper-claim support, and topic-status promotion.

Sandbox results may only motivate a new child topic card. They cannot raise an existing
route's status, count as confirmation, support a paper claim, or bypass D-3 through D0.
The validator scans all retained sandboxes, rejects unit reuse across campaigns or an
exploration/confirmation role reversal, aggregates reservations by asset campaign, and
requires every terminal result to appear exactly once in the taint registry. Topic cards
have separate evidence-use slots: tainted IDs are accepted only by
`sandbox_motivation_refs` and rejected from novelty, killer, decision-history, D2, and
paper-claim evidence. The schema is
[`research/discovery/exploration_sandbox.schema.json`](../research/discovery/exploration_sandbox.schema.json),
and the validator checks its authorization, budgets, hashes, event chain, receipts, and
holdout separation.

The validator's `--base-ref` mode now checks Git-history immutability. Every sandbox present
in the protected base must retain byte-identical manifests, decisions, inputs, and existing
artifacts; its ledger must retain the base ledger as an exact byte prefix; and the taint
registry must preserve its prior entry prefix. A sandbox absent from the base may contain
only the authorization genesis and no run artifacts or terminal result. This enforces a
separate authorization merge before execution. The pull-request workflow is installed in
`.github/workflows/research-governance.yml`, with third-party actions and validator
dependencies pinned. The research baseline branch requires the `research-governance` check,
forbids force pushes and deletion, enforces linear history and conversation resolution, and
does not permit administrator bypass. Runtime changes are developed on child branches and
reviewed through pull requests to that baseline.

The governance validator is not an operating-system security boundary. Schema v2 now binds
every authorization to an OCI image digest and launcher digest, no network, a read-only root
filesystem, no host repository-tree or secrets mount, CPU-only device access, a single
read-only frozen config-file input enumerating exploration units, no generated/staged/mounted
confirmation outcomes, and a byte-bounded stdout tar channel. Each branch request freezes its
hypothesis, falsifier, multiplicity family, tests, units, CPU/output bounds and code/config
digests before execution; each receipt repeats the execution contract. The fail-closed launcher
enforces these constraints, but still requires an outcome-free conformance run against a
pinned test image and independent runtime review before any sandbox may be authorized. For a
synthetic simulator, known withheld seed numbers are not an admissible
confirmation split: seeds must be derived from a frozen public-randomness rule whose pulse
values do not exist until after sandbox termination and D0 freeze. Until runtime qualification,
the repository truthfully reports zero authorized sandboxes.

The first possible generator is specified only as an outcome-blind
[Bourse counterexample preflight](../papers/proposal/bourse_disposable_market_counterexample_preflight_2026-08-25.md).
It limits exploration to minimal market-native transformation twins and treats every known
failure-family explanation as a rejection. It is neither a topic card nor an authorization.

### D-1 — try to kill the topic cheaply

Before outcomes or implementation, perform:

1. an exact-primary-work and standard-parent reduction audit;
2. at least two minimal killer tests covering necessity, sufficiency, identification,
   invariance, or a negative control;
3. a same-estimand contract for two independently maintained simulators;
4. a versioned real-observation bridge;
5. a contamination and simulator-oracle audit;
6. a conservative hostile probability and value-of-information estimate.

The preferred order is analytic sanity check, synthetic identifiability, negative/null
control, strongest simple baseline, mechanism ablation, competing mechanism,
cross-simulator transfer, then a frozen external test. A branch stops at the first decisive
failure.

### D0 — freeze before learning from outcomes

An outcome-blind decision manifest freezes the estimand, simulator and data versions,
seeds, metrics, baseline budget, exclusion rules, multiplicity correction, stop rules,
confirmation split, artifact hashes, and the exact authorized actions. Search history is
append-only: a scientific revision creates a child rather than rewriting a failed parent.
A later gate may move the same frozen claim from `candidate` or `parked` to
`failed_closed`; the formal result must append the earlier status, card hash, decision hash,
new evidence, and terminal rationale before the canonical status is updated.

### D1/D2 — explore, then confirm

D1 may branch under its explicit budget, but its results remain exploratory. D2 uses a
held-out simulator family, mechanism, time period, or real-data target that was not used to
select the claim. Every final claim links to code, configuration, data provenance, raw
result, counterevidence, and a frozen evaluator. Failure and honest non-identification are
retained as results.

## Activation rule

`candidate` authorizes only bounded literature, source, schema, metadata, and theorem
work. `parked` authorizes nothing. `active` does not mean unrestricted execution: only the
actions listed in the decision manifest are allowed.

An authorized DX sandbox is not a candidate or active route. Its narrow permissions attach
only to its named disposable asset split and expire with its manifest. The global
pre-activation prohibitions remain in force everywhere else.

A card can become active only when all of the following hold:

- conservative hostile T0 lower bound is at least 15%;
- the novelty manifest contains at least 15 primary works and no unresolved direct
  collision;
- at least two frozen killer tests survived;
- at least two simulator contracts have different lineage groups and implement the same
  state, intervention, and observable;
- the real-data observation bridge is qualified;
- every inherited failure family is explicitly distinguished by a named test;
- contamination controls and an exploration/confirmation split are frozen;
- an outcome-blind decision lists the authorized actions.

The machine validator fails closed on these rules:

```bash
conda run -n ecophys python scripts/validate_research_discovery.py
conda run -n ecophys python scripts/validate_research_discovery.py \
  --base-ref origin/dependabot-cooldown-verification-liquidity-2026-08-21
conda run -n ecophys python -m pytest tests/test_research_discovery.py \
  tests/test_run_research_discovery_sandbox.py -q
```

The route graph is validated separately because it records terminal decisions and lineage,
whereas the discovery layer records why a topic was worth testing in the first place.
