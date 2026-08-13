# Plan v7 — Gauge-invariant controller probes under latent drift

**Frozen:** 2026-08-13

**Branch:** `gauge-invariant-controller-probes-v7`

**Parent:** `main@d89a2dc59fa4e8ad0c0b7755a39b37ba3fe389a8`

**Initial state:** `SCOUT`; literature and symbolic analysis only; zero outcome, remote-host or GPU authorization

## 1. Why this iteration exists

V6 established a precise failure rather than a market law. In one known feedback regime, distinct response and
latent-dynamics parameters can generate the same observed path. A sufficiently diverse controller change removes
the fixed alias only if latent dynamics are shared across regimes; allowing regime-specific latent changes restores
the alias. More generated paths or a larger model cannot repair this information deficit.

V7 asks a narrower constructive question:

> Is there a controller-probe functional, identified set or path-comparison quantity that is invariant to the V6
> latent-coordinate gauge, remains informative under an explicitly bounded class of latent drift and can be
> estimated from safe, prospectively randomized feedback perturbations?

The objective is not to recover an ontological hidden demand state. It is to find the strongest observable claim
that survives the equivalence class exposed by V6, or prove that the proposed exits reduce to existing system
identification, robust control, causal switchback or partial-identification results.

## 2. Frozen mathematical object

Let a known controller family be indexed by probe `a_t` and let observed state/use be `o_t`. A latent model
`m=(A,Psi)` induces an interventional law `P_m(o_{0:H} | a_{0:H-1})`. Define observational gauge equivalence over
a declared safe probe class `A_safe` by

\[
m\sim_{A_{safe}}m'
\quad\Longleftrightarrow\quad
P_m(o_{0:H}\mid a_{0:H-1})=P_{m'}(o_{0:H}\mid a_{0:H-1})
\]

for every admitted probe path and horizon. V7 may target only:

- a functional constant on these equivalence classes;
- a sharp identified set over a declared latent-drift class;
- or a probe design that provably refines the equivalence partition under safety and support constraints.

Any parameter that varies inside `~_{A_safe}` is inadmissible as a scientific estimand.

## 3. Candidate cards

### V7-C1 — observable quotient response

Construct a minimal response functional of controlled future observables that is invariant to latent similarity and
the V6 coordinate alias, yet changes under scientifically meaningful cross-resource adaptation. Candidate forms
include Markov parameters, closed-loop transfer functions and finite controlled-test operators.

**Immediate kill test:** if the object is exactly a transfer function, minimal realization, predictive-state row,
bisimulation quotient or standard closed-loop response parameter, retire as `RETIRED_PRIOR_ART`.

### V7-C2 — sharp drift-budget identified set

Replace unsupported latent invariance with an explicit drift budget `d(Psi_r,Psi_0)<=rho` and derive the sharp set
of response functionals compatible with observed probe paths. Seek a lower bound showing when no safe controller
sequence can shrink the set below a scientifically consequential diameter.

**Immediate kill test:** if the set is ordinary set-membership/robust system identification or generic sensitivity
analysis with the market mechanism only changing notation, retire. A survivor needs a sharper geometry, weaker
observable contract or matching lower bound produced by the exact controller structure.

### V7-C3 — loop/curvature probe under paired randomization

Use a prospectively randomized closed controller path, such as `K0 -> K1 -> K2 -> K0`, and compare forward/reverse
or paired pulse responses after subtracting exact mechanics. The admissible target must vanish for the entire
declared fixed/allowed-drift class and remain nonzero for a narrower adaptive alternative.

**Immediate kill test:** raw noncommutativity, hysteresis area or path order is already falsified by Exp144 and
fixed stochastic pumps. If the design is ordinary switchback, crossover, optimal input design or dynamic treatment
effect estimation without a new invariant or bound, retire.

## 4. Nearest-result attack matrix

Before code, compare every candidate equation by equation against:

1. minimal realization, transfer functions, Markov parameters and subspace/closed-loop system identification;
2. predictive-state representations, operational process states, causal states and bisimulation quotients;
3. multi-environment/interventional LTI and switching-system identifiability;
4. active/optimal input and intervention design under safety constraints;
5. set-membership, robust and distributionally robust identification under bounded disturbances/model drift;
6. partial identification and sensitivity analysis under unmeasured confounding or environment shifts;
7. switchback/crossover experiments, carryover-aware dynamic treatment effects and marketplace interference;
8. stochastic pumps, geometric phases and noncommuting response operators.

Search failure, a paper's future-work sentence or a new application name is never novelty evidence. A candidate
survives N0 only if its estimand, assumptions, construction and guarantee differ explicitly from every nearest
result.

## 5. Proof and falsification gates

### N0 — non-equivalence

- Write one formal card per candidate with theorem/conjecture status.
- Map every symbol to the nearest result and identify the exact non-reducible line.
- Produce at least one counterexample against the candidate's broad form.
- No candidate may advance on architectural novelty or empirical usefulness alone.

### I0 — equivalence-class validity

- Prove the target is constant on the declared observational equivalence class.
- State the weakest probe-support, excitation, drift and reset assumptions.
- Construct a matching impossibility or lower-bound witness when an assumption is removed.
- Separate controller/mechanical, workload, latent-drift and behavioral components.

### E0 — executable probe contract

- Specify a safe discrete controller set, dwell time, washout/carryover model and randomization unit.
- Demonstrate that the probe is implementable in at least one non-market controlled resource system before
  claiming generality.
- Require prospective scheduling and complete-vector scoring; no historical post-hoc path selection.

### P0 — generated discrimination

Only after N0/I0/E0 survive, freeze a generated CPU experiment comparing the candidate with its exact nearest
baselines. It must include null aliases, bounded drift, fixed pumps, carryover, weak excitation and model
misspecification. Passing is algebra/implementation evidence only.

## 6. Venue routing

### Nature Machine Intelligence

Requires a genuinely non-equivalent method or theorem for learning/identifying gauge-invariant controlled
functionals under latent drift, with formal guarantees and validation in at least two non-market systems. A market
application plus standard transfer-function or robust-ID machinery is insufficient.

### Nature Computational Science

Requires a substantive computational-science phenomenon enabled by the method: a prospectively predicted response
law under controlled resource interventions, with independent replication and relevance beyond Ethereum. A
negative alias theorem or generated benchmark alone is insufficient.

### Honest initial probability

- NMI-ready survivor after nearest-result attack: `1%--3%`.
- NCS-ready phenomenon after identification plus prospective replication: `2%--5%`.
- Reusable negative theorem/design paper after a sharp lower bound and multi-system evidence: `5%--15%`.

These are research-planning priors, not venue acceptance predictions.

## 7. Data requirements

### T0 — authorized now

- primary papers, official specifications and metadata-only catalogs;
- symbolic/generated counterexamples without formal seeded experiment loops;
- no market outcome, paid data, human/LLM interaction or chain response row.

### T1 — after N0/I0/E0

- generated controlled trajectories with immutable seed/config contracts;
- public laboratory/controller logs only if licences, intervention assignments and raw trajectories are frozen;
- at least one independently administered non-market system for NMI method validation.

### T2 — only after a full survivor

- prospectively randomized controller probes or pre-announced policy changes with exact assignment records;
- a separate independent replication system and untouched scoring window;
- market data only when the estimand, confounder graph, attribution fields and licence are all frozen before values.

Buying data does not reopen a failed theorem or identification gate.

## 8. Compute requirements

### T0 — current authorization

- at most 20 local Mac CPU core-hours for literature maps, symbolic algebra, graph validation and tiny hand
  fixtures;
- zero contact with the two V100 hosts or RTX2060, zero queued job and zero GPU-hours.

### T1 — generated formal gate

- 100--2,000 CPU core-hours, <=64 GB aggregate RAM and <=100 GB storage;
- CPU work may use the V100/RTX2060 hosts with GPUs idle after a separate preregistration;
- at most 20 V100-equivalent GPU-hours only if a surviving estimator demonstrably needs acceleration.

### T2 — multi-system/real probe validation

- 2,000--50,000 CPU core-hours, 0--1,000 V100-equivalent GPU-hours and 0.1--5 TB storage, measured after T1;
- capacity may expand to additional compatible non-H20 workers; H20 is excluded;
- heterogeneous pools remain separate and benchmarked against canonical V100 jobs.

Compute cannot create probe randomization, excitation, invariance or replication.

## 9. Immediate queue

1. Commit and push this plan before extending the graph or deriving candidate outcomes.
2. Audit the eight nearest-result neighborhoods using primary sources.
3. Write at most three formal candidate cards and one counterexample per card.
4. Retire candidates immediately when they reduce to standard objects.
5. Create no experiment directory until one candidate survives N0/I0/E0 and receives a separate preregistration.

## 10. Stop rules

- Do not reopen V6 or read its sealed outcomes under the V7 name.
- Do not call a transfer function, predictive quotient, confidence set, switchback or optimal input design new by
  application alone.
- Do not infer adaptation from a loop area, noncommutativity or residual outside a chosen baseline.
- Do not choose probe directions after viewing responses.
- If all three cards reduce to prior art or fail identification, close V7 before data and compute.
- Preserve negative results, counterexamples and source mappings append-only.
