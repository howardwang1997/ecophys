# EcoMD causal forecasting, cyclic latent-state, and herding trigger audit

**Date:** 2026-09-05  
**Archetypes:** simulator_method, measurement_method, theory_mechanism  
**Decisions:** one partial_capability and one not_trigger  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

This audit tested five recent, unusually relevant primary artifacts:

1. [CEDAR](https://arxiv.org/abs/2608.25871), a KDD 2026 action-conditioned
   e-commerce forecasting system trained on 32 million private Alibaba 1688 trajectory windows and
   used inside an online budget-planning experiment;
2. [CIR-ACTIVA](https://arxiv.org/abs/2608.03715), an amortized distributional
   interventional forecaster trained and evaluated on a causal multivariate CIR generator calibrated
   to real CDS marginals;
3. [Equilibrium Causal Games](https://arxiv.org/abs/2607.19531), a theorem-heavy
   treatment of cyclic latent equilibria, unknown sensors, and mechanism interventions;
4. [Herding and Liquidity in Order-Book Markets I](https://arxiv.org/abs/2607.08907),
   a public phase-diagram study of a smooth one-sided-book crossover; and
5. the paper's pinned [MIT-licensed implementation](https://github.com/hanssmail/darkcorners-abm/tree/021b3108d597baf47e4582dc2dc1e8c2dc94894e).

The sources are scientifically useful, but they do not create an executable EcoMD/ICLR topic.

| Lead | Genuine update | Decisive failure for this project |
|---|---|---|
| CEDAR | Real action histories, large industrial scale, and a deployed composite policy experiment | Historical action prediction does not identify intervention response by architecture; the private data and bundled online policy do not expose simulator counterfactual truth |
| CIR-ACTIVA | Open paired observational/interventional synthetic benchmark for temporal causal-effect estimation | The causal response is defined by the source simulator prior; passive CDS calibration cannot validate its graph or intervention law |
| Equilibrium Causal Games | Exact passive non-identification and intervention-count boundaries for cyclic latent equilibria | Its positive theorem consumes aligned population response matrices acquired with known full-rank latent-coordinate probes in every environment; neither public markets nor EcoMD external validation supply them |
| Herding paper and code | Reproducible smooth crossover and internal structural ablations | The paper calls its control an agent fraction, while the implementation has no persistent agents and uses an order-level mixture probability; the resulting population interpretation is not identified, and the simulator-native phenomenon is already the source paper's contribution |

The causal cluster is recorded as partial_capability because the ECG theorems and the two executable
forecasting systems are real advances. It removes zero recorded EcoMD blockers. The herding lead is
not_trigger. No machine card, experiment plan, route node, simulator run, or accelerator allocation
is justified.

## 2. Frozen question programs

### 2.1 Action-conditioned market counterfactuals

The market-native target is a future path distribution

\[
\mathcal L(Y_{t+1:t+h}\mid do(A_{t+1:t+h}=a),H_t)
\]

for a declared legal action, pre-action history, clock, and interference unit.

The rival explanations are:

- **H1 — structural action response:** the action token changes a stable transition mechanism, and
  a learned simulator recovers that intervention response;
- **H2 — policy selection and omitted state:** the historical actor selected actions using
  information absent from the model, so action-conditioned prediction learns an observational
  association that can reverse under intervention.

The cheapest decisive result is either an assigned same-action response with complete pre-state and
independent confirmation, or a theorem giving a non-vacuous identified set under explicit
restrictions. Better passive rollout error is not discriminating. A positive answer would support a
counterfactual world model; a null answer is valuable because it forces abstention rather than
turning a conditional forecast into a causal stress test.

### 2.2 Cyclic latent market mechanisms

The target is a query of a feedback matrix or nonlinear cyclic equilibrium mechanism observed
through an unknown market sensor map. The rivals are:

- **H1 — intervention-separated mechanism:** sufficiently rich external mechanism changes separate
  the hidden sensor from the cyclic interaction;
- **H2 — latent-frame gauge:** different mechanisms and sensors generate the same complete
  multi-environment observation law while giving different intervention responses.

The decisive object is the legal data fibre: the query must be constant on every observationally
equivalent model, not merely locally stable or accurately reconstructed.

### 2.3 Herding and one-sided-book stress

The observable is the fraction of event times at which one side of the book is empty. The rivals
are:

- **H1 — reflexive directional feedback:** correlated momentum-following flow depletes one side of
  the book;
- **H2 — composition, placement, and representation:** replacing fundamental-anchored flow with
  mid-anchored flow, changing the event mixture, or changing the hidden actor/activity
  representation creates the crossover without identifying a real population mechanism.

A market-level positive result would require a dose observable before outcomes, invariant to actor
splitting and activity-rate reparameterization, together with an external intervention or labelled
participant truth. A simulator-native ablation can validate a mechanism inside one declared source
model, but cannot adjudicate real markets.

## 3. CEDAR: architecture cannot create causal identification

CEDAR models weekly product states and two merchant actions, discount ratio and advertising spend.
Its first stage interleaves state and action tokens in the order
\(S_{t-1}\rightarrow A_t\rightarrow S_t\); its second stage predicts an event-conditioned residual.
The final 2025 window is held out from a private Alibaba 1688 corpus of approximately 32 million
overlapping 15-week examples. The public Kaggle experiment has promotions and calendar events but,
as the paper states, lacks merchant actions with explicit budget-planning semantics.

The appendix posits

\[
S_{t+1}=f(H_t,A_{t+1})+\mathcal E(Z_{t+1},U_t)
\]

and assumes sequential ignorability,

\[
S_{t+1}(a)\perp A_{t+1}\mid H_t.
\]

This gives a sharp dichotomy.

1. If sequential ignorability, consistency, positivity, and a sufficient history hold, the
   conditional causal mean is identified by the ordinary longitudinal g-formula. Token ordering may
   improve estimation, but does not supply new identification.
2. If the assumption fails, interleaving action tokens and fitting a residual do not block an
   unobserved backdoor path.

### Proposition 1: two observationally identical action worlds

Let \(U\sim\mathrm{Bernoulli}(1/2)\), let the historical policy choose \(A=U\), and compare:

\[
\mathcal M_1:\;Y=A,\qquad
\mathcal M_0:\;Y=U.
\]

Under the historical policy both worlds produce exactly \(A=Y=U\), so every observational
state-action sequence and every predictive loss is identical. Under intervention,

\[
\mathbb E_{\mathcal M_1}[Y\mid do(A=1)]
-
\mathbb E_{\mathcal M_1}[Y\mid do(A=0)]=1,
\]

whereas the same contrast is zero in \(\mathcal M_0\). An arbitrarily expressive action-interleaved
Transformer cannot distinguish the worlds from the historical law. Residual decomposition does not
alter this fibre.

### The online experiment does not score counterfactual fidelity

The paper reports a January 1--30, 2026 production experiment involving 239 merchants and 245
orders. The treatment combines CEDAR simulation, budget planning, and traffic allocation; the
control uses an existing diffusion forecaster with total budgets. It reports 13 percent higher LTV
and 15 percent higher store-level ROI.

Those figures may support the value of the composite deployed pipeline. They do not identify the
calibration of CEDAR's predicted potential outcomes:

- a planner can rank two actions correctly while its predicted response magnitudes are arbitrarily
  wrong;
- the treatment changes the simulator and the downstream allocation policy together;
- the paper does not report the randomization unit, assignment probability, interference mapping,
  assignment key, standard errors, or confidence intervals needed to reconstruct a field estimand;
- the private trajectory and assignment records are not currently released; the paper says a
  partially anonymized release is being pursued.

This is a meaningful industrial capability, not a public truth asset for EcoMD.

## 4. CIR-ACTIVA: a strong synthetic benchmark, not market causal truth

CIR-ACTIVA learns an amortized distribution over multi-horizon responses to a soft intervention.
Its source generator samples three-variable causal CIR systems, permits directed cycles by unrolling
them into a fixed number of acyclic layers, and generates paired observational and interventional
trajectories. The model is trained across tasks sampled from a simulator prior
\(p_{\mathrm{tr}}(\mathcal M)\); test-time validity requires tasks from that prior.

The real-data bridge calibrates univariate CIR parameters from 661 five-year CDS series and compares
synthetic and real passive traces. It does not observe a CDS intervention, causal graph, or
descendant set. The authors state the boundary clearly: synthetic ground truth establishes internal
validity regardless of market resemblance; real shock responses remain untestable without
interventional data.

### Proposition 2: passive target fit cannot select an interventional simulator prior

Let two simulator priors \(\Pi_0,\Pi_1\) induce the same distribution over every observed target
history \(X\),

\[
P_{\Pi_0}(X)=P_{\Pi_1}(X),
\]

but different intervention responses for query \(a\),

\[
P_{\Pi_0}(Y^a)\ne P_{\Pi_1}(Y^a).
\]

Every model-selection, calibration, or misspecification test measurable only from target histories
has the same distribution under both priors. It therefore cannot consistently select the correct
interventional law. This remains true with perfect passive likelihood or stylized-fact matching.

EcoMD can manufacture another member of this ambiguity class, but cannot adjudicate which member is
the external market. The broad methodological descendants are also occupied by amortized causal
effect estimation, interventionally consistent surrogates, policy/value equivalence, causal
partial identification, and simulator-misspecification work already recorded in the route graph.
A new paper would need a non-vacuous certificate under a restricted, observable prior-shift class,
not an additional synthetic market row.

## 5. Equilibrium Causal Games: the exact identification boundary reinforces the blocker

The ECG source supplies a particularly useful theorem-level audit.

### Passive data are maximally insufficient

In the stable zero-diagonal linear model

\[
V=BV+U,\qquad X=HV,
\]

with unknown full-column-rank sensor \(H\), ECG shows that for \(d\ge2\) every legal stable
zero-diagonal \(B'\) can be paired with a sensor \(H'\) that preserves the complete passive law.
Thus passive fit cannot recover the cyclic interaction even at population level.

This is stronger than an optimization failure and matches the repository's
observation-quotient blocker: a more expressive EcoMD encoder cannot separate a sensor-mechanism
factorization when the data map itself is many-to-one.

### The positive theorem uses information the market does not expose

The linear recovery theorem consumes aligned population response matrices
\(M_0^{(e)}=H(I-B^{(e)})^{-1}\) for the baseline and single-target mechanism environments. When
those matrices are not directly given, acquisition requires, in every environment, the same
labelled known latent-coordinate shift design \(\mathsf D\) with full row rank, no direct sensor
effect, and invariant or known probe-arm sensor means.

Under the source's unknown-support assumptions, all \(d\) mechanism targets are generally needed;
\(d-1\) suffice exactly when the sole untargeted node directly parents every other node. Shift
interventions alone identify only \(H(I-B)^{-1}\), not its sensor and feedback factors. With
nonlinear sensing, further within- and cross-block twists remain, and the positive result identifies
only a source-block representation up to blockwise coordinate changes, not the downstream
mechanisms or sensor/interaction split.

Public market rule changes, fees, announcements, and price paths are not known latent-coordinate
probes. EcoMD can expose its own latent variables and program interventions, but then both the
mechanism labels and response truth come from the same source simulator. The ECG paper itself uses
synthetic or calibrated examples and explicitly disclaims real-data or high-fidelity-simulator
validation.

### Why the narrow nonlinear-cyclic descendant is not a current candidate

There may be a legitimate open mathematical region between ECG's nonlinear negative results and
its linear positive theorem. It is not yet a question program for this project because:

- no legal market intervention has been shown to satisfy a weaker identifying condition;
- no candidate query has been proved invariant to the remaining block diffeomorphisms;
- BackShift, nonlinear-mixing causal representation learning, unknown multi-node intervention CRL,
  interventional SDE identification, and ECG itself densely occupy the surrounding theorem space;
- no finite-sample estimator or separating lower bound has been constructed; and
- no two independent non-EcoMD systems expose the required latent target and response semantics.

Naming the region is not a theorem. It may be re-audited only after a written construction exists.

## 6. Herding crossover: paper/code semantics are not the same object

The source reports a smooth, not discontinuous, crossover in the fraction of one-sided-book events.
It uses a \(7\times6\) grid over \(\varphi\) and \(\kappa\), real versus independently seeded
scrambled-sign controls, an OFI rule variant, horizon sweeps, and open-loop shadow/replay
decompositions. The source appropriately avoids calling the smooth ramp a tipping transition.

The first code-level check materially changes the audit. The paper defines \(\varphi\) as the
fraction of agents that are herders. The pinned implementation states:

- there are no persistent strategic agents, budgets, or inventories;
- every event is a fresh order-generation decision; and
- \(\varphi\) is the probability that an event uses the herding order kernel.

Thus the implementation varies a labelled order-flow mixture \(q\), not a population share
\(\phi_{\mathrm{agent}}\).

### Proposition 3: order share does not identify agent share

Suppose a hypothetical persistent-agent implementation has \(H\) herders and \(Z\) liquidity
providers with per-agent activation rates \(\lambda_h\) and \(\lambda_z\). Its stationary herding
order share is

\[
q=\frac{H\lambda_h}{H\lambda_h+Z\lambda_z}.
\]

For any fixed \(q\in(0,1)\) and any proposed population share
\(\phi_{\mathrm{agent}}=H/(H+Z)\in(0,1)\), choose

\[
\frac{\lambda_h}{\lambda_z}
=
\frac{q(1-\phi_{\mathrm{agent}})}
     {(1-q)\phi_{\mathrm{agent}}}.
\]

The same event-type mixture and, with matched order kernels, the same aggregate event law can
therefore arise from arbitrarily different population fractions. No order-level phase diagram in
\(q\) identifies a phase diagram in agent share without an activity-rate restriction and
participant labels.

This also corrects a tempting but invalid criticism: because the actual implementation has no
persistent actor count, an actor-splitting counterexample does not directly change its \(\varphi\).
The failure is the paper-to-code semantic lift from flow mixture to actor composition, not a
path-level bug in the order-mixture experiment.

### The source's internal claims and the external claim must be separated

Within the declared code, the scrambled-sign experiment is a valid structural ablation in
distribution: it preserves the order-kernel mixture and randomizes correlated direction. Its use of
independent seeds is not itself a flaw. The result supports a statement about that simulator.

It does not establish that real one-sided-book stress is caused by a known fraction of herding
participants:

- herding labels are generated by the model and are not observed in ordinary public L2/L3 data;
- momentum and OFI are different state-dependent rules, not two measurements of one externally
  assigned treatment;
- the onset \(\varphi^\ast\) is the first point where a smooth statistic crosses the analyst-chosen
  level 0.02 and is explicitly sensitive near onset to placement bandwidth;
- the paper already owns the simulator-native crossover and mechanism decomposition; reproducing it
  in EcoMD is an application, not a new method; and
- EcoMD does not implement the same price-time-priority order kernel, event clock, cancellations,
  hidden labels, or flow-mixture action, so the two codes are not same-estimand replications.

The paper/code conformance mismatch is a useful reviewer finding and a reusable unit test for future
ABMs. By itself it is too small for an ICLR main-track contribution and reduces to mixture
identifiability and representation-contract checking.

## 7. Gate decisions

### 7.1 Causal forecasting and cyclic latent state

| Gate | Result |
|---|---|
| New capability | Pass: industrial decision-conditioned forecasting, an open causal-CIR benchmark, and exact cyclic-latent theorems are real |
| Identification beyond historical prediction | Fail: CEDAR assumes the needed ignorability; architecture does not imply it |
| External causal truth | Fail: CEDAR data/assignment are private and bundled; CIR truth is simulator-defined; ECG examples are synthetic/calibrated |
| Irreducible method residual | Fail today: no constructed theorem or estimator beyond recorded surrogate, CRL, SDE, value-equivalence, and partial-ID parents |
| Two-system common intervention | Fail: no shared latent probes, action clock, complete state, or untouched response target |

**Decision:** partial_capability, removed_blockers empty, candidate_harvest_authorized false.

### 7.2 Herding liquidity crossover

| Gate | Result |
|---|---|
| Reproducible simulator phenomenon | Pass: public MIT code and a detailed internal robustness suite |
| Market-native control | Fail: implemented herding order share does not identify the claimed agent fraction |
| Critical law | Fail: the source itself reports a smooth thresholded crossover |
| Novel EcoMD contribution | Fail: the source owns the finding and a second simulator row is application-only |
| External and cross-engine truth | Fail: hidden labels, different kernels/clocks, and no assigned field response |

**Decision:** not_trigger, removed_blockers empty, candidate_harvest_authorized false.

## 8. Exact re-entry boundaries

The causal cluster may be re-audited only when one written package provides either:

1. a versioned public field or laboratory asset containing the action assignment, propensity,
   complete pre-state, interference mapping, outcomes, rights, untouched confirmation family, and
   independently governed same-action replication; or
2. a theorem and finite-sample estimator for a declared nonlinear cyclic query that is invariant on
   the full latent-data fibre, uses weaker legally observable interventions than ECG's aligned
   latent probes, has a matching impossibility boundary, and is validated on two independent
   non-EcoMD systems.

The herding route may be re-audited only when a pre-outcome market observable distinguishes
participant share from activity-weighted order share, survives actor split/merge and rate
reparameterization, supports the same intervention and event clock in two independent engines, and
has external labelled or assigned response truth. Another \((\varphi,\kappa)\) sweep, finer onset
grid, EcoMD reproduction, or stylized-fact table is not a trigger.

Until one of those conditions is met, the A800 and both V100 workers receive zero jobs from these
leads.
