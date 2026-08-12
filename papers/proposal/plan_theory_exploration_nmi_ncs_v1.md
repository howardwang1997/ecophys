# Dual-track theory exploration v1 — NMI method and NCS mechanism

**Frozen:** 2026-08-12

**Status:** exploration protocol; no theorem, identity, mechanism law or venue claim is admitted

**Branch:** `theory-exploration-nmi-ncs-v1`

**Base:** `main@fdf0c5f722bb39a31888b3b7793aea29674e60a3`

**Binding exclusions:** the Plan v4 invariant-gradient v0/v1 G0 FAIL and the entropy/TUR T0 G0 FAIL remain intact

**Compute boundary:** current 2xV100 32 GB plus optional RTX2060 compatibility host; expandable non-H20 resources only

## 1. Objective

Build a durable, falsifiable search program for one of three genuinely load-bearing objects:

1. a new theorem with assumptions, conclusion and proof obligations;
2. a new estimator or response identity that is not a composition of mapped prior art;
3. an irreducible empirical mechanism whose predictions differ from strong observational and adaptive baselines.

The search is split by evidentiary burden rather than by codebase:

- **Nature Machine Intelligence (NMI):** the headline must be a transferable AI/world-model method for learning
  behavior under known mechanisms and generalizing to unseen interventions across multiple environments.
- **Nature Computational Science (NCS):** the headline must be a replicated computational-science discovery about
  how real markets respond to institutional interventions, supported by a validated digital-twin workflow.

One shared mechanism-separated simulator may support both tracks. A result may enter only one headline ledger
unless it independently satisfies both sets of gates.

## 2. Binding non-revival rules

- Persistent state, short/long BPTT, pathwise/LR gradients, Rhee--Glynn correction, SMC/Jarzynski reweighting and
  mixing diagnostics remain mapped prior art. Renaming or recombining them cannot reopen Plan v4 G0.
- Path KLD, hidden/coarse-grained entropy, waiting-time bounds, TUR and market-temperature language remain closed.
- A synthetic multi-clock recovery, exact exchange implementation or constraint-preserving architecture is
  feasibility evidence, not a paper-level theorem or mechanism.
- Anonymous L2 cannot identify trader beliefs, intent or identity without additional assumptions or data.
- Simulator error and generated heavy-tail transients are not market physics.
- Automation may rank, reject or route candidates; it may never output a novelty `PASS`.

## 3. Shared mathematical setting

Use a mechanism-separated asynchronous system

\[
A_n\sim\pi_\theta(\cdot\mid Q_n,Z_k,M_r),\qquad
Q_{n+1}=G_{M_r}(Q_n,A_n),\qquad
Z_{k+1}=U_\phi(Z_k,\mathcal H_{n_k:n_{k+1}},M_r),
\]

where `G` is a known or audited fast mechanism, `pi` is learned event-generating behavior, `U` is slower
adaptation and `M` is an explicit institutional mechanism/intervention. Unknown parts of `G` must be represented
as constrained residuals with uncertainty, not silently absorbed into `pi`.

The initial search neighborhoods are not claims:

| ID | Candidate neighborhood | Key question | Primary kill attack |
|---|---|---|---|
| S1 | action-lift under singular mechanism changes | Can behavior transfer in pre-mechanism action space when state-path laws have disjoint support? | reduction to SCM modularity, off-policy evaluation or standard change of variables |
| S2 | adaptive-response impossibility/identifiability | What cannot be predicted about post-intervention adaptation from one pre-intervention environment? | generic no-free-lunch or latent-state non-identifiability already states the result |
| S3 | fast/slow intervention response decomposition | Can mechanical and behavioral response terms be separated with a controlled finite-timescale error? | direct Duhamel, averaging or linear-response theorem |
| S4 | mechanism-conditioned predictive quotient | Is there a minimal observable state sufficient for unseen mechanism sequences without identifying beliefs? | standard PSR, causal-state or bisimulation equivalence |
| S5 | composition of unseen interventions | Under what conditions do learned behavioral responses compose across rule changes and clocks? | standard simulation lemma/domain-generalization bound |

Every neighborhood is presumed occupied until an equation-level audit and non-equivalence witness say otherwise.

## 4. Knowledge graph and exploration history

Create both human-readable and machine-readable views under `research/theory_exploration/`:

- `knowledge_graph.yaml`: canonical nodes and typed edges;
- `knowledge_graph.md`: rendered Mermaid topology plus reading guide;
- `candidate_ledger.md`: one versioned card per candidate;
- `source_matrix.md`: primary-source theorem/equation coverage and exact claim blocked;
- `failure_ledger.md`: retired candidates, counterexamples and reusable lessons;
- `venue_routes.md`: shared evidence and NMI/NCS-specific gates.

Required node types are `source`, `known_result`, `concept`, `candidate`, `proof_obligation`, `counterexample`,
`benchmark`, `dataset`, `compute_gate`, `venue_claim` and `decision`. Required edge types are `proves`, `covers`,
`reduces_to`, `requires`, `falsified_by`, `distinguished_by`, `supports`, `forbids`, `branches_to` and `retired_by`.

Candidate states are:

`SCOUT -> FORMALIZING -> ATTACKING -> {RETIRED_PRIOR_ART, RETIRED_IDENTIFIABILITY,
RETIRED_NO_WITNESS, CONJECTURE, READY_FOR_HUMAN_AUDIT}`.

There is no automated `PASS`. Every transition records date, evidence, author/reviewer decision and predecessor
version. Retired candidates remain in the graph; they are never deleted or relabelled as active.

## 5. NMI track

### 5.1 Candidate headline

Develop a mechanism-conditioned, constraint-preserving, asynchronous world-model method whose learned behavioral
state transfers to unseen mechanisms or intervention sequences. The contribution must be useful outside markets.

### 5.2 Theory obligations

At least one of the following must survive a fresh audit:

- an identifiability theorem for the behaviorally sufficient state under multiple known mechanisms;
- a finite-horizon or long-horizon interventional error bound that separates behavior, adaptation, mechanism and
  clock-scheduling errors and is sharper than a standard simulation lemma under stated structure;
- an action-space transport identity that remains usable when post-mechanism state laws are singular;
- a compositionality theorem for unseen sequences of exact mechanism changes and slow adaptation;
- an impossibility theorem paired with a constructive minimal-assumption estimator, not an impossibility result alone.

### 5.3 Evidence gates

| Gate | Pass requirement | Failure action |
|---|---|---|
| N0 novelty | equation-level non-equivalence against SCM, OPE, causal representation, PSR/bisimulation, modular world models and multi-timescale learning | retire candidate before code |
| N1 formal | complete statement, proof sketch, explicit counterexample and quantitative witness | remain a conjecture |
| N2 controlled systems | at least two non-market mechanism families with analytic or high-precision references | no general AI claim |
| N3 method | compute-matched gain on unseen mechanisms against learned world models, modular baselines and oracle ablations | fallback to systems/audit venue |
| N4 real transfer | blind prediction on at least two independent interventions/environments | no NMI submission |

### 5.4 Data and compute

- N0--N1: primary literature and generated symbolic fixtures only; <=50 CPU core-hours; 0 GPU-hours.
- N2 pilot: generated queue/exchange system plus a structurally different public simulator such as a reaction,
  traffic, epidemiological or resource-allocation system; <=200 CPU core-hours and <=20 V100-eq hours only after N1.
- N3 screening: 3--5 seeds and multiple mechanism families; approximately 200--800 V100-eq hours.
- N3/N4 confirmation: at least 20 independent training seeds for headline stochastic comparisons; provisional
  4,000--12,000 V100-eq hours, 10,000--50,000 CPU core-hours and 2--10 TB. Recommend 8--16 non-H20 workers.
- Real data may expand across environments, but no purchase or sealed split opens before N0--N2 pass.

## 6. NCS track

### 6.1 Candidate headline

Use a verified adaptive market digital twin to separate the immediate mechanical effect of a rule change from
slower behavioral re-centering, then establish a response mechanism that replicates across independent real
institutional interventions.

### 6.2 Mechanism obligations

The paper needs an empirical law or mechanism with prospective predictions, not merely a better simulator. Candidate
forms include a transferred response spectrum, a conservation-constrained response decomposition or a measurable
condition under which behavioral re-centering reverses/amplifies the immediate mechanical effect. Each must specify:

- the exact intervention and treated/control estimand;
- an early mechanical window and later adaptation window fixed before opening the target post-period;
- predictions that differ among frozen behavior, instantaneous response, slow adaptation, point-process and
  statistical controls;
- confound, anticipation, spillover and concurrent-rule-change falsifications;
- the independent replication unit and failure threshold.

### 6.3 Evidence gates

| Gate | Pass requirement | Failure action |
|---|---|---|
| C0 mechanism gap | direct microstructure/intervention prior art does not already establish the same response law | retire before data acquisition |
| C1 data contract | one development intervention and at least one sealed independent replication with rule timestamps, event coverage and controls | stop Nature route |
| C2 identifiability | mechanical/adaptive decomposition survives synthetic and negative controls under realistic missingness | narrow to descriptive study |
| C3 blind pilot | frozen response vector beats fixed, point-process and statistical controls without post-period fitting | stop or specialist fallback |
| C4 replication | direction, magnitude and uncertainty transfer across independent real interventions | no general mechanism claim |
| C5 artifact | event reconstruction, numerical verification, uncertainty and source-to-figure rebuild pass | delay submission |

### 6.4 Data and compute

- C0: literature and rule documents only; <=50 CPU core-hours; 0 GPU-hours.
- C1 sample audit: free/vendor samples for schema, sequence and license checks only; no confirmatory values.
- C2 generated feasibility: current exact exchange kernel and generated paths; <=500 CPU core-hours and <=20
  V100-eq hours only if a learned component is necessary.
- C3 pilot: newly frozen event-level pre/post data, matched controls and metadata; at most 100--400 V100-eq hours.
- C4/C5 confirmation: provisional 1,000--4,000 V100-eq hours, 50,000--250,000 CPU core-hours and 10--30 TB;
  4--8 GPU workers plus 128--512 CPU cores are more valuable than a large single GPU model.
- Commercial data expansion remains approximately USD 10k--25k core and USD 25k--50k expanded capacity planning,
  subject to current quotes, samples, licences and preceding gates. These are not purchase authorizations.

## 7. Exploration protocol

### T0 — topology and source audit

1. Populate primary sources and known-result nodes.
2. Map every candidate to its nearest equations/theorems, not only keywords.
3. Record venue scope separately from scientific novelty.
4. Retire any candidate already expressible as a mapped result plus application details.

### T1 — formal cards

For each survivor write state space, transition law, observables, intervention operator, assumptions, formal
statement, proof sketch, nearest composition, symbolic difference, counterexamples, rejection rule and benchmark.

### T2 — paper-and-pencil attacks

Attempt reduction to Duhamel/linear response, stochastic averaging, Doob--Meyer, SCM modularity, importance
sampling/OPE, PSR/bisimulation, causal representation identifiability and standard simulation lemmas. Construct at
least one observational-equivalence counterexample and one support/mixing/clock failure per candidate.

### T3 — zero-cost numerical witnesses

Only candidates surviving T2 may receive generated CPU tests. Tests distinguish equations; they do not establish
novelty. Freeze each protocol before execution and assign a new experiment number. Do not use market or sealed data.

### T4 — human audit and venue fork

A candidate may reach `READY_FOR_HUMAN_AUDIT` only with complete source coverage, proof obligations and a controlled
non-equivalence witness. NMI and NCS reviews are separate. No GPU/data expansion occurs before the relevant human
gate passes.

## 8. Immediate deliverables and chronology

1. Commit and push this plan before creating the graph, candidate cards or numerical witnesses.
2. Build the graph schema and validator; populate binding negative results first.
3. Audit S1--S5 using primary literature current through the search date.
4. Write at most three formal candidate cards; retire weak candidates rather than keeping an inflated backlog.
5. Select at most one NMI and one NCS lead for deeper proof/mechanism work.
6. Record all decisions in `logs/YYYY-MM-DD.md` and durable memory; update `docs/research_lineage.md`.
7. End this iteration with an explicit decision among `NO_SURVIVOR`, `CONJECTURE_ONLY` and
   `READY_FOR_HUMAN_AUDIT`; none is a novelty PASS.

## 9. Stop rules

- Stop a candidate immediately if its symbolic statement is a direct specialization of mapped prior art.
- Stop if the only distinction is markets, EcoMD, exact engineering, scale, performance or a new name.
- Stop if anonymous observations cannot identify the claimed latent object and no additional observable is available.
- Stop if a toy advantage disappears under an oracle nearest-composition baseline or a differently generated system.
- Stop the NMI route if evidence remains market-specific; stop the NCS route if no blind replicated real mechanism
  exists. A specialist paper remains acceptable but must not inherit a Nature-level claim.
