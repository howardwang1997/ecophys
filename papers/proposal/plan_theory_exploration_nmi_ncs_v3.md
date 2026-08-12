# Dual-track theory exploration v3 — falsifiable state closure and long-horizon operator calibration

**Frozen:** 2026-08-12

**Branch:** `theory-exploration-nmi-ncs-v3`

**Base:** `main@490fffe426b94967f0262984f1e5c8e3681617d9`

**Inherited results:** v1 NMI `NO_SURVIVOR`; v2 NMI `NMI_NO_SURVIVOR`; v2 NCS
`NCS_C0_FAIL_IDENTIFICATION`; exp144 `NEGATIVE_CONTROLS_CONFIRMED`; exp145
`ATTRIBUTION_NOT_IDENTIFIED`

**Initial resource boundary:** primary literature, algebra and generated exact fixtures only; <=50 CPU core-hours,
zero GPU-hours, no worker contact, no market-outcome inspection, no sealed-period access and no data purchase

## 1. Objective and permitted topic pivot

The NMI/NCS venue ambition is unchanged, but the scientific question may change. V3 abandons the non-identifiable
claim that a long response residual by itself reveals adaptation, beliefs or learning. It asks instead whether a
candidate observable state is *closed* for controlled prediction, how closure failure propagates across time
scales, and whether a simulator can be calibrated directly against the resulting long-horizon operator error.

The intended headline is conditional:

> A controlled system should not be called a predictive world model until its declared state passes a falsifiable
> closure test, or its missing memory is repaired with a quantitatively sufficient state extension.

This is not yet a contribution. V3 is a bounded theorem-selection and kill-test stage. It may end with no survivor.

## 2. Binding interpretation rules

- A closure rejection means that the declared state/model class is insufficient for the declared interventions,
  horizon and observables. It does **not** identify psychological adaptation or a unique hidden mechanism.
- Hidden-state Markovization is always a live alternative. A useful method must do more than announce generic
  non-Markovianity.
- Exact event mechanics remain fixed and non-learned unless a separate adaptive component is explicitly modelled
  and identified. They can supply controlled probes, not semantic labels for a residual.
- NMI needs a general measurement or modelling contribution with theorem-level non-equivalence and validation
  beyond finance. NCS needs that method plus a reproducible scientific finding about a real computational system;
  an EcoMD-only simulator diagnostic is insufficient.
- A standard identity, a composition of standard estimators or a new name for PSR, causal states, Koopman,
  Mori--Zwanzig, Stein discrepancy or Markov perturbation is not novelty.
- Automation may reject or route a candidate but may never issue a novelty `PASS`.

## 3. Candidate C1 — interventional state-closure certificate

For a proposed state statistic `S_t=s(H_t)` of observed history `H_t`, future intervention sequence `u` and bounded
test class `F`, define the finite-horizon closure defect

\[
\Delta_L(s;\mathcal U,\mathcal F)
=\sup_{\substack{h,h':s(h)=s(h')\\u\in\mathcal U,\,f\in\mathcal F}}
\left|\mathbb E[f(O_{t+L})\mid h,u]
-\mathbb E[f(O_{t+L})\mid h',u]\right|.
\]

Exact controlled predictive closure requires `Delta_L=0` for all declared horizons, probes and tests. An empirical
certificate must state its history-matching assumptions, intervention support, uncertainty and power; failure to
reject is never evidence of universal closure.

### C1 nearest-method attacks

Audit at equation/theorem level:

- predictive-state representations, observable-operator models, causal states and Hankel-rank realization;
- controlled bisimulation, state abstraction and sufficient statistics;
- conditional-independence/Markov-order tests and process-tensor causal breaks;
- active system identification, persistent excitation and reset/replay experiments;
- state-aliasing diagnostics in POMDPs and learned world models.

C1 survives only if it supplies at least one of the following under weaker or structurally different assumptions:

1. a finite, intervention-designed witness with a valid population implication not equal to an ordinary
   conditional-independence test;
2. a lower bound on the necessary predictive-state repair from observable cross-probe defects;
3. a computable certificate linking a specific state extension to a guaranteed reduction in long-horizon error.

Retire C1 if it is only `history matters after conditioning on the current state`, stacked observability, Hankel
rank estimation or PSR learning.

## 4. Candidate C2 — cross-scale semigroup and memory defect

Let `T_u(t)` be the observed conditional prediction operator under a frozen intervention path. A closed,
time-homogeneous Markov state obeys the Chapman--Kolmogorov/semigroup relation. Define

\[
\mathcal D_u(t,s)=T_u(t+s)-T_{\theta_tu}(s)T_u(t),
\]

where `theta_t u` is the shifted intervention path. V3 will ask whether a family of such defects can identify a
minimal useful memory repair or bound downstream prediction error, not merely reject one Markov kernel.

### C2 nearest-method attacks

Audit:

- Chapman--Kolmogorov and Markov-order tests;
- Mori--Zwanzig projection and generalized Langevin memory kernels;
- Koopman semigroups, transfer operators and semigroup-consistency losses;
- hidden Markov/OOM/PSR minimal realization and block-Hankel rank;
- classical and process-tensor notions of operational non-Markovianity.

Retire C2 if every defect can be read directly as a standard memory-kernel, CK-test or Hankel-rank statistic. A
survivor needs an exact relation or sharp bound connecting controlled cross-scale defects to the *minimal repair
needed for a declared task*, with a non-equivalence witness against those nearest methods.

## 5. Candidate C3 — Poisson-weighted long-horizon operator calibration

For Markov operators `P` and `Q`, invariant laws `pi_P, pi_Q`, observable `f`, and a solution
`(I-Q)h_Q=f-pi_Q f`, the exact bias identity is

\[
(\pi_P-\pi_Q)f=\pi_P(P-Q)h_Q.
\]

Finite-time errors also admit the standard telescoping/Duhamel decomposition

\[
P^n-Q^n=\sum_{k=0}^{n-1}P^k(P-Q)Q^{n-1-k}.
\]

These equations are baselines, not proposed theorems. C3 asks whether controlled, partially observed systems admit
a new *estimable* witness or optimization principle that jointly certifies state closure and controls both
finite-horizon and invariant-observable error.

### C3 nearest-method attacks

Audit:

- Poisson-equation perturbation bounds and Markov-chain sensitivity;
- Stein operators/discrepancies, generator matching and score matching;
- Koopman/operator inference and spectral matching;
- invariant-measure-preserving numerical schemes and long-time weak error;
- adversarial moment matching, simulation-based calibration and neural operator objectives.

Retire C3 if the method is simply a learned Poisson test function, generator Stein discrepancy or weighted
one-step loss already implied by existing perturbation theory. A survivor needs an assumption/result not obtained
by direct substitution into the two standard identities above and an exact counterexample showing why existing
one-step or stationary objectives are insufficient.

## 6. Formal-card and experiment protocol

At most two candidates may enter formal cards. Each card must contain:

- mathematical objects, observable sigma-algebras, intervention class and estimand;
- exact closest theorem/equation and an equation-by-equation non-equivalence claim;
- theorem, proposition or explicitly labelled conjecture;
- one positive exact witness and at least two adversarial controls, including hidden-state Markovization;
- falsification conditions and scope limitations;
- consequences in at least two structurally distinct non-market systems;
- separate NMI-method and NCS-science routes.

Experiment 146 is authorized only for deterministic algebra checks and tiny generated finite-state or linear
Gaussian fixtures on the Mac CPU. It must be preregistered and committed before execution. No neural training,
market fitting or worker queue is permitted at this stage.

## 7. Decision states and gates

Candidate decisions:

- `RETIRED_PRIOR_ART`: nearest methods contain the result.
- `RETIRED_NONIDENTIFIABLE`: exact controls admit the same observable witness without the claimed conclusion.
- `RETIRED_NO_REPAIR`: the diagnostic rejects closure but cannot quantify or validate a repair.
- `CONJECTURE_ONLY`: non-equivalence is plausible but proof or observable estimator is missing.
- `READY_FOR_HUMAN_NOVELTY_AUDIT`: exact distinction, proof obligations and kill tests survive. This is never a
  novelty pass.

V3 closes as `V3_NO_SURVIVOR`, `V3_CONJECTURE_ONLY` or `V3_READY_FOR_HUMAN_AUDIT`. Only the last state may unlock a
data/compute preregistration, and only after a human equation-level novelty review.

## 8. Conditional data and compute ladder

### Locked tier T0 — current v3 authorization

- Data: generated exact fixtures and source metadata only; no market outcome values.
- Compute: Mac CPU, <=50 core-hours; 0 GPU-hours; no V100/RTX2060 contact.

### T1 — only after a formal survivor and preregistration

- Data: existing free/open datasets with immutable provenance and time splits; at least one non-market controlled
  benchmark plus development-only market data. Crash and sealed periods remain untouched.
- Compute: <=500 CPU core-hours and <=100 aggregate V100-equivalent GPU-hours. The two V100 32 GB workers run
  independent jobs; the RTX2060 is limited to compatible smoke or CPU work.

### T2 — paper-scale method validation

- Data: multiple open dynamical-system domains, multiple markets/assets/periods, and a separate untouched
  replication domain. Full message/L2 data are required for event-state claims; minute/daily bars cannot validate
  event-level closure. Every source needs licence and provenance records.
- Compute: approximately 2,000--10,000 V100-equivalent GPU-hours plus 5,000--50,000 CPU core-hours, scheduled as
  independent seed/domain arrays. Capacity may expand to additional heterogeneous non-H20 workers after canonical
  V100 benchmarks.

### T3 — conditional NCS confirmation

- Data: vendor-quality multi-venue order messages/L2, predeclared normal and stress periods, independent exchange
  or jurisdiction replication, plus non-financial external validation. Purchases occur only after design,
  licensing and leakage gates.
- Compute: budgeted from measured T2 scaling; additional non-H20 GPU/CPU pools are allowed. No plan or estimate may
  assume H20 availability.

Passing a compute tier cannot repair a failed theorem or identification gate.

## 9. Knowledge graph, history and chronology

- Extend the existing 108-node graph append-only with v3 candidate, source, theorem, counterexample, decision and
  experiment nodes. Never delete or reactivate v1/v2 failures.
- Preserve exact identities, tempting-but-failed claims and reusable controls in `source_matrix.md`,
  `failure_ledger.md`, formal cards and the rendered topology.
- Keep `docs/research_lineage.md`, `logs/2026-08-12.md`, `.claude/memory/` and venue routes synchronized.
- Commit and push this frozen plan before literature conclusions, formal cards or exp146 artifacts.
- Complete primary-source and equation audits before writing code.
- Preregister exp146 before its single clean-checkout execution.
- Stop immediately if all three candidates reduce to mapped methods. Do not preserve the round by inventing a
  market-specific name for a generic diagnostic.

## 10. Completed outcome

**Closed:** 2026-08-13

**Decision:** `V3_NO_SURVIVOR`

The mandatory equation-level audit fired the stop condition before any experiment:

- C1 is `RETIRED_PRIOR_ART`: the proposed controlled closure defect is a restricted controlled-system-dynamics or
  predictive-state row distance. Operational Markov causal breaks already test the same instrument-relative
  closure, and PSR-f already characterizes finite linear state completion through ranks.
- C2 is `RETIRED_PRIOR_ART`: process-recovery theory already bounds supported multi-time observable error by
  operational memory strength, while Mori--Zwanzig supplies the exact resolved Markov/memory/orthogonal split and
  data-driven reduced operators.
- C3 is `RETIRED_PRIOR_ART`: its exact identities are standard Poisson perturbation and Stein generator
  comparison. Long-horizon Koopman bounds and invariant-measure training already occupy the proposed practical
  objective.

The retained noisy-XOR construction proves a binding scope restriction: an observed process can match an iid
model exactly in its stationary one-time law and one-step kernel while disagreeing in its three-time law. Thus
Poisson or invariant-measure calibration cannot repair a state representation that has already erased relevant
history. This construction is elementary and is recorded as a future negative control, not a theorem claim.

Experiment 146 was neither preregistered nor run. V3 opened no market data, sealed period or purchased data; used
0.0 GPU-hours; contacted neither V100 nor the RTX2060; and left no job queued. The canonical graph contains 135
validated nodes. NMI/NCS remain the targets, but the next topic search must start from a specific observable or
randomizable scientific phenomenon rather than another generic state, memory or long-horizon objective.
