# Dual-track theory exploration v2 — target sufficiency and relaxation exceedance

**Frozen:** 2026-08-12

**Branch:** `theory-exploration-nmi-ncs-v2`

**Base:** `main@648fd96daca9e4ec2a1e6a478033b8c9b35a0f77`

**Inherited result:** v1 NMI `NO_SURVIVOR`; v1 NCS `CONJECTURE_ONLY`; exp144
`NEGATIVE_CONTROLS_CONFIRMED`

**Resource boundary:** literature, public rule metadata and generated symbolic fixtures only; <=50 CPU core-hours,
zero GPU-hours, no H20, no market-value inspection, no sealed-period access and no data purchase

## 1. Objective

Run one bounded continuation with two independent decisions:

1. **NCS C0:** determine whether real post-rule persistence outside a prospectively frozen relaxation envelope is a
   scientifically distinct, identifiable response mechanism rather than a repackaging of mixing bounds, event
   studies, hysteresis, structural breaks or digital-twin residuals.
2. **NMI N0:** search for one symbolic primitive about prediction-target-conditioned identifiability that is not
   excitation, observability, causal representation learning, PSR/bisimulation, active intervention design or a
   standard sufficient-statistic result.

This iteration may honestly end with no candidate on either branch. It cannot admit novelty, open paid data or
start training.

## 2. Binding inherited facts

- The invariant-gradient, entropy/TUR, simulator-heavy-tail, generic fast/slow, action-lift, predictive-quotient,
  intervention-composition and known-mechanism-excitation routes remain closed.
- Exp144 proves that a multi-mechanism rank gain may be ordinary stacked observability and that fixed non-adaptive
  Markov operators can generate order effects.
- For exact or conditionally independent-noise event mechanics,
  `I(Z;Q_next | Q,A,M)=0`; the event update supplies no new hidden-state information after its observed inputs.
- Anonymous L2 does not identify beliefs, identity or intent.
- A standard theorem used to define a falsifiable null is useful infrastructure, not theorem novelty.
- Automation may retire or route a candidate but may never output novelty `PASS`.

## 3. NCS C0 — relaxation-exceedance audit

### 3.1 Frozen candidate object

For a rule path returning to baseline, a bounded observable `f`, a prevalidated frozen baseline class
`B` and return-to-baseline lag `L`, define

\[
B_L=\sup_{b\in\mathcal B}\left\{
\operatorname{osc}(f)\,\delta_b^L+\varepsilon_b(L)
\right\},
\]

where `delta_b<1` is a declared contraction/mixing coefficient and `epsilon_b` includes mechanism reconstruction,
estimation and matched-control uncertainty. The candidate empirical rejection is

\[
\inf_{L\in\mathcal L_{late}}
\operatorname{LCB}_{1-\alpha}^{sim}\{|R_{obs}(L)|-B_L\}>0.
\]

This rejects the declared frozen class. It does not, by itself, distinguish adaptation from omitted slow state,
nonstationarity, anticipation, spillovers or concurrent shocks.

### 3.2 Equation-level prior-art audit

Cover at least:

- Dobrushin/conductance/spectral-gap and coupling bounds for Markov relaxation;
- perturbation and linear/nonlinear response, stochastic pumps and hysteresis;
- structural-break, change-point, interrupted-time-series and synthetic-control inference;
- model-set, partial-identification and robust digital-twin residual tests;
- market microstructure studies of temporary/reversed tick, speed, fee, priority, resting-time, auction and
  short-sale rules.

Retire the candidate if its entire contribution is “observed decay is slower than a fitted Markov model”. A
survivor needs a prospectively testable response vector or cross-intervention scaling relation that existing event
studies do not already estimate.

### 3.3 Metadata-only intervention registry

Create `research/theory_exploration/intervention_registry_v2.yaml` with, for each candidate:

- exact rule and jurisdiction/venue;
- announcement, implementation, reversal/end and transition dates;
- treatment/control construction available from documents;
- required event fields, depth and clock precision;
- public/vendor coverage and licence status without opening outcome values;
- anticipation, overlap, spillover and concurrent-change risks;
- role: inspected development only, possible sealed replication or reject;
- source URLs and source-access date.

The registry may inspect rule documents, schemas, date coverage, licences and published study designs. It may not
inspect or compute treatment outcomes, post-event summary values or model-fit statistics. Previously published
effects make a case development-only, not sealed confirmation.

### 3.4 C0 decision states

- `NCS_C0_FAIL_PRIOR_ART`: no distinct estimand or prediction.
- `NCS_C0_FAIL_IDENTIFICATION`: distinct quantity but not attributable under available designs.
- `NCS_C0_CONJECTURE_ONLY`: residual mechanism survives conceptually, but no valid development/replication pair.
- `NCS_C0_READY_FOR_DATA_CONTRACT`: equation-level distinction plus one development and at least one untouched
  replication candidate exist. This is a routing state, never novelty pass or purchase authority.

## 4. NMI N0 — new-primitive search

### 4.1 Search neighborhoods

| ID | Primitive under test | Immediate kill attack |
|---|---|---|
| T1 | prediction-target completeness: which future targets force retention of an adaptive parameter? | minimal sufficient statistics, observability, predictive information and recent physical-parameter world-model work |
| T2 | horizon threshold: a parameter is recoverable from histories but absent from every `h`-step optimal predictive state below a critical horizon | delay embedding, observability index, finite-memory PSR and system-identification horizon results |
| T3 | complementary targets: no single target identifies the state, but a declared target family does | stacked observability, multi-view identifiability and information decomposition |
| T4 | target-induced partial order: one prediction task is strictly more informative for intervention transfer than another | Blackwell ordering, experiment comparison and sufficient-statistic refinement |

The search stops at two formal cards. Any primitive expressible as a direct specialization of the kill method is
retired before code.

### 4.2 Admission burden

A surviving NMI card needs:

- formal target family, observable sigma-algebra, predictive-state equivalence and intervention family;
- a theorem/conjecture whose conclusion is not ordinary injectivity, rank or sufficient statistics;
- at least one non-equivalence witness and one impossibility/counterexample;
- usefulness in at least two structurally different non-market systems;
- a method consequence beyond adding more prediction heads or horizons.

Decision states are `NMI_NO_SURVIVOR`, `NMI_CONJECTURE_ONLY` and `NMI_READY_FOR_HUMAN_AUDIT`. None is a novelty pass.

## 5. Knowledge-graph and history rules

- Append v2 sources, candidates, counterexamples, intervention metadata and decisions to the v1 graph; do not
  delete or reactivate retired nodes.
- Record exact theorem/equation coverage in `source_matrix.md` and all failed ideas in `failure_ledger.md`.
- Add a v2 topology layer and preserve exp144 as immutable evidence.
- Update `logs/2026-08-12.md`, `.claude/memory/`, `docs/research_lineage.md` and venue routes at each decision.
- A metadata registry needs its own validator and focused tests before it can route a case to a data contract.

## 6. Chronology and stop rules

1. Commit and push this plan before the v2 literature graph, registry or formal cards.
2. Complete NCS equation audit before classifying intervention candidates.
3. Metadata screening may run in parallel with NMI paper-and-pencil search but cannot open outcome values.
4. Do not implement a learned model, download bulk data, contact workers or queue GPU jobs in v2.
5. Stop NCS if no distinct prediction or valid replication design remains.
6. Stop NMI if all four primitives reduce to mapped results; do not manufacture a replacement candidate.
7. End with separate NMI and NCS decisions, explicit remaining proof/data obligations and an immutable exploration
   history.
