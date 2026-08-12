# Candidate ledger — v1 through v6

**Status vocabulary:** `SCOUT -> FORMALIZING -> ATTACKING -> retired / CONJECTURE / READY_FOR_HUMAN_AUDIT`  
**Current outcome:** v6 NMI `NO_SURVIVOR`; NCS `FORMALIZING` but blocked before outcomes; V5 remains
`V5_NO_SURVIVOR`

**Scientific meaning:** the exact-controller NCS target remains prospectively sealable, but no real experiment is
admitted until a future controller change and independent replication exist

## 1. Shared object and identification target

For event index `n`, slow-update index `k` and intervention-regime index `r`, use

\[
A_n\sim\pi_\theta(\cdot\mid Q_n,Z_k,M_r),\qquad
Q_{n+1}=G_{M_r}(Q_n,A_n),\qquad
Z_{k+1}=U_\phi(Z_k,\mathcal H_{n_k:n_{k+1}},M_r).
\]

`G_M` is exact or separately audited, `A` is an observed primitive action/message, `Q` is observable mechanism
state, and `Z` is not interpreted as belief or trader identity. The most that anonymous observations may identify
is an equivalence class sufficient for predicting declared observables under a declared intervention family.

## 2. NMI lead NMI-T1 — known-mechanism excitation margin

**Version:** NMI-T1-v1  
**State:** `RETIRED_PRIOR_ART`
**Venue role if it survives:** transferable method/theory; EcoMD is one test environment, not the theorem domain

### 2.1 Candidate primitive

Let `H` be an observed trajectory segment and let `z` denote an initial adaptive predictive state. For a known
mechanism `m`, define the local score of the induced observable law

\[
s_m(H;z)=\nabla_z\log p(H\mid z,m),
\]

and the multi-mechanism information matrix

\[
\Gamma_{\mathcal M}(z)
=\sum_{m\in\mathcal M}w_m\,
\mathbb E\!\left[s_m(H;z)s_m(H;z)^\top\mid z,m\right],
\qquad
\lambda_{\mathcal M}=\operatorname*{ess\,inf}_z
\lambda_{\min}\!\left(\Gamma_{\mathcal M}(z)\right).
\]

The intended distinction is that each likelihood is induced by the same behavior/adaptation law composed with a
different known `G_m`; the mechanism maps might expose complementary behavioral directions without direct labels
for latent intervention targets.

### 2.2 Retired conjectural form — never admitted

Under smooth dominated observable laws, ergodicity/mixing, local structural invariance of `pi,U`, and an explicit
quotient removing predictive symmetries:

1. `lambda_M>0` may give local identifiability of the adaptive predictive state across mechanisms;
2. finite-sample local risk might scale as `O((n lambda_M)^-1)` plus separately measurable mechanism-residual and
   mixing terms;
3. `lambda_M=0` supplies a tangent direction along which two local models are observationally indistinguishable.

This is currently only a Fisher-information/observability-shaped conjecture. Its form is dangerously close to
standard persistent excitation, controlled-world-model identification and interventional causal representation
learning. The displayed equations define an audit target; they are not claimed as new.

### 2.3 Event-layer information identity

There is one exact identity worth retaining. Suppose

\[
Q_{n+1}=G_M(Q_n,A_n,\varepsilon^G_n),\qquad
\varepsilon^G_n\perp Z_k\mid(Q_n,A_n,M).
\]

Then the conditional distribution of `Q_{n+1}` does not depend on `Z_k` after the observed mechanism inputs are
given, so

\[
Z_k\rightarrow(Q_n,A_n,M)\rightarrow Q_{n+1},\qquad
I(Z_k;Q_{n+1}\mid Q_n,A_n,M)=0.
\]

For a deterministic exact mechanism this follows immediately because the conditional entropy of `Q_{n+1}` given
`Q_n,A_n,M` is zero. With independent residual noise, integrating that noise gives the same conditional
independence. This is a standard Markov/data-processing identity, not a new theorem. Its research consequence is
important: exact event-layer mechanics cannot directly reveal hidden adaptation once their observed inputs are
known. Any extra information from switching mechanisms must arrive through later feedback into actions or slow
updates, which is the established territory of controlled/switching system identification and active intervention
design.

### 2.4 Proof obligations that were not met

- Specify the predictive quotient before writing an injectivity statement.
- Prove whether exact `G_m` makes `Gamma_M` observable or only estimable under an already identified policy.
- Exhibit a mechanism family for which standard conditional action excitation is singular but the proposed margin
  is positive, without introducing extra observed labels that trivially explain the gain.
- Derive necessity or sufficiency beyond the inverse-Fisher asymptotics already expected from regular models.
- Bound mechanism misspecification separately; an “exact” exchange implementation cannot stand in for a true
  physical/behavioral transition.
- Produce a non-market witness and a nearest-composition oracle before training a neural model.

### 2.5 Kill attacks and final status

| Attack | Failure condition |
|---|---|
| controlled-world-model reduction | `lambda_M` is only conditional action excitation after stacking environments |
| system-identification reduction | the theorem is a standard observability Gramian or persistent-excitation result |
| CRL reduction | mechanism variation acts exactly as labelled intervention diversity used by existing identifiability theorems |
| predictive-equivalence ambiguity | latent coordinates remain arbitrary beyond the claimed quotient |
| support failure | known mechanics drive policy inputs outside all training support, invalidating the likelihood score |

The stacked-observability reduction, switching-dynamics identifiability results, active intervention-design prior
art and the event-layer identity jointly meet the retirement rule. No mechanism-specific weaker-assumption theorem
or distinct error law was found.

### 2.6 Zero-cost witness result

For a two-dimensional latent state and one-dimensional mechanism-specific observation matrices `C_1=[1,0]` and
`C_2=[0,1]`, each single-environment Gramian is rank one while the stacked Gramian is identity. This demonstrates
complementary excitation and nothing more. The required negative control relabels this exactly as a stacked
observability calculation; unless the candidate predicts something that baseline does not, it is not a novelty
witness.

**Formal result:** Experiment 144 confirmed every expected property. The summed and vertically stacked Gramians
were bit-for-bit equal (`max_abs_error=0`), and the stacked eigenvalues were exactly `(1,1)`. NMI-T1 therefore
is `RETIRED_PRIOR_ART`; this fixture cannot be cited as candidate support.

## 3. NCS lead NCS-M1 — relaxation exceedance after a closed rule loop

**Version:** NCS-M1-v1  
**State:** `RETIRED_IDENTIFIABILITY` in v2 (historical v1 state: `ATTACKING`)

**Venue role if it survives:** real market response mechanism; the digital twin estimates a counterfactual baseline

### 3.1 Candidate estimand

Let `gamma=(m_0,m_1,...,m_K=m_0)` be a declared rule loop and `Y` an event-time observable. Define the loop response
relative to an untreated matched path,

\[
R_{\mathrm{obs}}(\gamma,\tau)
=\mathbb E[Y_{T+\tau}\mid\gamma]
-\mathbb E[Y_{T+\tau}\mid m_0\ \text{throughout}],
\]

and a prospectively frozen baseline `R_frozen` obtained from audited mechanics with behavior and adaptive state held
at the pre-intervention law. The candidate residual is

\[
H_{\mathrm{adapt}}(\gamma,\tau)
=R_{\mathrm{obs}}(\gamma,\tau)-R_{\mathrm{frozen}}(\gamma,\tau).
\]

The word “holonomy” is provisional shorthand for a residual around a rule loop. It is not a claim of a new
geometric invariant.

### 3.2 Exact counterexample to the naive certificate

Take a fixed two-state Markov system with no adaptation,

\[
P_A=\begin{bmatrix}0.9&0.1\\0.2&0.8\end{bmatrix},\qquad
P_B=\begin{bmatrix}0.6&0.4\\0.05&0.95\end{bmatrix},\qquad
p_0=(1,0),\quad y=(0,1)^\top.
\]

Then

\[
p_0(P_AP_B-P_BP_A)y=0.075\ne0.
\]

The transition laws are fixed and memoryless; the order effect comes only from noncommuting dynamics. In longer
cyclic stochastic systems, geometric pump currents give the same warning. Therefore `R_obs != 0`, loop area and a
raw response commutator do not identify adaptation.

**Formal result:** Experiment 144 reproduced `r_AB=0.455`, `r_BA=0.38` and the `0.075` difference at the frozen
`1e-12` tolerance. This formally falsifies the naive certificate inside this iteration. Only the more demanding
excess-over-frozen estimand remains under attack.

### 3.3 Frozen-mechanics relaxation envelope

The candidate is narrowed to a standard but useful rejection inequality. Let `P_0^(b)` be the post-return baseline
kernel for a prospectively frozen model `b`, `pi_0^(b)` its invariant law and `delta_b<1` its Dobrushin contraction
coefficient. For a bounded observable `f` and any distribution `mu_gamma` left by the prior rule path,

\[
\left|\mu_\gamma(P_0^{(b)})^L f-\pi_0^{(b)}f\right|
\le \operatorname{osc}(f)\,\delta_b^L
\left\|\mu_\gamma-\pi_0^{(b)}\right\|_{\mathrm{TV}}
\le \operatorname{osc}(f)\,\delta_b^L.
\]

Add preregistered reconstruction, estimation and control errors `epsilon_b(L)` and define the robust frozen-class
envelope

\[
B_L=\sup_{b\in\mathcal B}
\left\{\operatorname{osc}(f)\delta_b^L+\varepsilon_b(L)\right\}.
\]

The admissible empirical test is whether a simultaneous lower confidence bound for the observed post-return
residual exceeds `B_L` over a predeclared late window. This rejects every frozen baseline in `B`; it does **not**
logically distinguish agent adaptation from omitted slow state, nonstationarity or an unmeasured concurrent shock.
Matched controls, placebo loops and independent replication supply that second layer.

The inequality is a standard Markov contraction result, not new mathematics. The potential NCS contribution is an
empirically replicated separation between the true response timescale and a verified mechanical/frozen envelope.
The digital twin exists to calculate and falsify the envelope; it is not declared market physics.

### 3.4 Identification obligations

- Predeclare exact rule timestamps, anticipation windows, early mechanical and late adaptation horizons.
- Demonstrate that the frozen baseline reproduces pre-period transitions and negative-control mechanism loops.
- Use a class of adequate frozen baselines and simultaneous uncertainty, not one favored simulator fit.
- Bound or estimate the return-to-baseline contraction rate before the target post-period is opened.
- Include noncommuting fixed Markov and point-process baselines, not only static or instantaneous behavior.
- Establish enough relaxation/reset for the claimed endpoint observable, or model the residual finite-time state.
- Control simultaneous fee, routing, macro, composition and venue-spillover changes.
- Use a treated/control design for both forward and reverse legs; a multi-year rule repeal is not a physical reset.
- Replicate the sign and time profile in an independent intervention family frozen before opening its post-period.

Even if all obligations pass, the result is an empirical mechanism, not proof that private beliefs were recovered.

### 3.5 Nearest empirical coverage

The US Tick Size Pilot supplies an attractive forward/reverse development case, but it is not an untouched headline
replication. The SEC already estimated heterogeneous market-quality changes, and a 2025 *Journal of Financial
Markets* paper explicitly analyzed both imposition and conclusion with depth-of-book data. It may be used to test
the measurement protocol; the Nature-level claim needs an additional independent loop or intervention family.

### 3.6 Kill attacks and status rule

| Attack | Failure condition |
|---|---|
| frozen noncommutativity | a fixed Markov/point-process baseline reproduces the residual profile |
| incomplete relaxation | the residual vanishes when the horizon is extended or state is matched |
| envelope instability | equally adequate frozen baselines make the exceedance change sign |
| event-study prior art | the claimed forward/reverse response is already the same estimand in existing work |
| contemporaneous shock | placebo dates, controls or unaffected venues reproduce the effect |
| model dependence | `H_adapt` changes sign across equally adequate frozen baselines |
| no replication | only the already-studied Tick Size Pilot supports the result |

NCS-M1 cannot become `READY_FOR_HUMAN_AUDIT` until a feasible real intervention pair and sealed replication are
identified from metadata alone.

### 3.7 V2 attribution attack and final status

V2 separates two statements that v1 had left coupled:

1. `|R_obs(L)| > B_L` rejects the prospectively declared frozen class `B`, provided the causal comparison and
   simultaneous uncertainty are valid.
2. The same inequality does not identify the omitted mechanism as learning, beliefs or adaptation.

Experiment 145 freezes two exact non-adaptive witnesses. First, a fixed hidden mode `S_{t+1}=0.9 S_t` exceeds a
declared `0.6^L` envelope at every lag `1,...,8`. Second, for any declared finite path `r_0,...,r_L`, a deterministic
time-homogeneous Markov clock on states `0,...,L`, with `P(i,i+1)=1` and `f(i)=r_i`, reproduces that path exactly.
The latter lies outside a strict Dobrushin class; this demonstrates that the test diagnoses omitted state or class
incompleteness, not adaptation.

The equation-level audit adds three independent closures:

- Markov perturbation and contraction-estimation literature already supplies uncertain relaxation envelopes.
- Modern event studies already estimate dynamic treatment paths and make their no-anticipation/parallel-trend
  assumptions explicit.
- Simulator-discrepancy and causal-digital-twin results show why agreement on a finite validation design cannot
  identify an arbitrary target counterfactual or label a residual without structural assumptions.

The metadata-only registry screened ten cases. Tick Size Pilot and NYSE American speed bump remain
`development_only`; eight are rejected, and zero are untouched `sealed_candidate` cases. The registry therefore
cannot route a C1 data contract.

**Final state:** `RETIRED_IDENTIFIABILITY`; NCS decision `NCS_C0_FAIL_IDENTIFICATION`. The envelope remains reusable
as a model-checking diagnostic, not as the main NCS mechanism.

## 4. Retired starting candidates

| ID | Final state | Mathematical reason |
|---|---|---|
| S1 action lift | `RETIRED_PRIOR_ART` | structural replay / sequential policy g-formula plus unchanged support and confounding requirements |
| S2 single-environment impossibility | `RETIRED_IDENTIFIABILITY` | generic observational equivalence without a new constructive boundary |
| S3 fast/slow response | `RETIRED_PRIOR_ART` | Markov perturbation, Duhamel and singular averaging |
| S4 predictive quotient | `RETIRED_PRIOR_ART` | PSR, bisimulation and causal abstraction |
| S5 unseen composition | `RETIRED_PRIOR_ART` | soft-intervention composition, homomorphism and effect invariance |

## 5. V2 NMI target-conditioned search

| ID | Proposed primitive | Decisive coverage | Final state |
|---|---|---|---|
| NMI-v2-T1 | target completeness: which target forces retention of a parameter | masked-prediction Definition 1 and Theorems 2/5; minimal predictive sufficiency | `RETIRED_PRIOR_ART` |
| NMI-v2-T2 | a general critical prediction horizon | matrix-power nonidentifiability and ordinary observability/delay-index dependence | `RETIRED_PRIOR_ART` |
| NMI-v2-T3 | complementary targets identify what no single target does | task-family injectivity, tensor targets and partition intersection | `RETIRED_PRIOR_ART` |
| NMI-v2-T4 | universal target-informativeness order for transfer | Blackwell comparison/garbling and sufficient-statistic refinement | `RETIRED_PRIOR_ART` |

The strongest compact identity is

\[
\sim_{\mathcal F_1\cup\mathcal F_2}
=\sim_{\mathcal F_1}\cap\sim_{\mathcal F_2},
\]

where two parameters are task-equivalent when they induce the same optimal predictor. This is definitional
partition refinement, not a new theorem. The two formal cards and the NCS impossibility construction are preserved
in `formal_cards_v2.md`.

## 6. V3 state-closure and operator-calibration pivot

| ID | Proposed primitive | Decisive coverage | Final state |
|---|---|---|---|
| C1 | interventional state-closure certificate and minimal predictive repair | controlled PSR/causal states, operational Markov condition, finite Markov order, PSR-f rank completion | `RETIRED_PRIOR_ART` |
| C2 | controlled cross-scale semigroup defect linked to task-relevant memory repair | process-tensor recovery bound, Chapman--Kolmogorov tests and data-driven Mori--Zwanzig | `RETIRED_PRIOR_ART` |
| C3 | Poisson-weighted finite/infinite-horizon operator calibration | Markov Poisson perturbation, Stein generator comparison, long-term Koopman bounds and invariant-measure regularization | `RETIRED_PRIOR_ART` |

The retained noisy-XOR warning has exact one-step kernel and invariant marginal agreement with an iid chain but a
different three-time law. It proves that stationary and one-step objectives cannot repair a missing state. This is
elementary and is not an admitted theorem. With no formal survivor, exp146 was neither preregistered nor run.

## 7. Version history

| Date | Version | Change | Decision |
|---|---|---|---|
| 2026-08-12 | v1 | Audited S1–S5, retired all five, created NMI-T1 and NCS-M1, and added the frozen noncommutativity counterexample. | `CONJECTURE_ONLY`; no data/GPU authorization |
| 2026-08-12 | v1.1 | Exp144 confirmed stacked-observability reduction and a fixed-operator order effect; neither active lead advanced. | `CONJECTURE_ONLY`; continue symbolic attacks only |
| 2026-08-12 | v1.2 | Added the event-layer information identity and switching/active-design coverage; retired NMI-T1. | NMI `NO_SURVIVOR`; NCS `CONJECTURE_ONLY`; no data/GPU authorization |
| 2026-08-12 | v1.3 | Replaced raw NCS order effects with a contraction-envelope exceedance test over a validated frozen baseline class. | NCS remains `ATTACKING`; empirical identification and data contract absent |
| 2026-08-12 | v2 | Audited target-conditioned identifiability, contraction estimation, dynamic causal response and digital-twin discrepancy; exp145 confirmed two non-adaptive exceedance witnesses; metadata screening found no sealed replication. | NMI `NMI_NO_SURVIVOR`; NCS `NCS_C0_FAIL_IDENTIFICATION`; no data/GPU authorization |
| 2026-08-12 | v3 | Audited controlled state closure, memory repair and Poisson/operator calibration; all three reduce equation-by-equation to PSR/process-tensor/Mori--Zwanzig/Stein/Koopman results. | `V3_NO_SURVIVOR`; exp146 not run; no data/GPU authorization |
| 2026-08-13 | v4 | Audited cross-population mechanism response, aggregation loss and strategic memory against direct human/LLM experiments, surrogate inference, interference theory and free repository metadata. | `V4_NO_SURVIVOR`; no experiment, outcome file, worker or GPU authorization |
| 2026-08-13 | v5 | Audited annual ADNT--tick feedback, then ran the single frozen generated RD preflight after a serial execution repair. Only 9/16 gated cells passed; one rounded null over-rejected and every 5% effect cell missed the power gate. | `V5_NO_SURVIVOR`; no market outcome, remote worker or GPU authorization |
| 2026-08-13 | v6 freeze | Changed the object to exact multi-resource fee controllers coupled to adaptive demand; made pre-change no-refit transfer the NCS target and a non-equivalent closed-loop method the conditional NMI target. | `SCOUT`; specifications/literature/catalog metadata only; no outcome or GPU authorization |
| 2026-08-13 | v6 audit | Audited exact EIP arithmetic, BPO schedules, closed-loop/multi-resource/IV prior art and Xatu metadata; preregistered official-fixture replay. | NMI `NO_SURVIVOR`; NCS `FORMALIZING` but blocked on BPO3 plus independent replication; Exp149 only |

## 8. V4 phenomenon-first candidates

| ID | Proposed phenomenon | Decisive coverage or missing witness | Final state |
|---|---|---|---|
| P1 | matched intervention-response spectrum across human, classical-algorithmic and agentic-AI populations | dynamic human/LLM market studies, institution-dependent comparisons, effect-prediction/surrogacy work; no signed law or free sealed pair | `RETIRED_PRIOR_ART` |
| P2 | stable adaptation information lost from participant trajectories under anonymous aggregation | direct same-protocol macro--micro dissociation plus standard information/partial-identification theory | `RETIRED_PRIOR_ART` |
| P3 | population-specific strategic memory after randomized causal breaks and rule transfer | no free randomized memory-erasure/replay market dataset or independent replication; session boundaries do not identify memory | `RETIRED_NO_WITNESS` |

The narrower “LLM surrogate under market interference” question remains a legitimate technical gap, but v4 found
only a direct composition of existing surrogacy and interference frameworks and no sealable market evidence. It is
not promoted to an active candidate.

## 9. V5 endogenous market-rule feedback

| ID | Proposed object | Decisive audit | Current state |
|---|---|---|---|
| V5-NCS-1 | discontinuity from annual ADNT band assignment to next annual ADNT/assignment across repeated cycles | Experiment 148: 9/16 gated cells pass; rounded-null cutoff 10 rejects 8.33% with Wilson upper 12.01%; all six 5% effect cells have only 33.67%--56.33% power | `RETIRED_FEASIBILITY`; NCS `NO_SURVIVOR` |
| V5-NMI-1 | transferable estimator/theorem for endogenous threshold feedback | robust bias-corrected, multi-cutoff, dynamic and discrete-score RD plus threshold systems cover the method components | `RETIRED_PRIOR_ART`; NMI `NO_SURVIVOR` |

The retired NCS candidate was narrower than “tick affects liquidity.” Its frozen estimand was the local discontinuity in
`log(ADNT_(y+1)/c)` at an annual statutory cutoff, where the outcome is the next controller input. AMF already
identified the circular relation qualitatively, so only a robust, repeated and externally replicated quantitative
effect can be new. Because the next calendar-year ADNT contains about nine months under the newly assigned column,
the estimate is an assignment ITT with mixed exposure rather than a full-year tick elasticity.

Cutoff 10 was the clean lead. Cutoff 600 required a date-correct nonzero price-row first stage. The 80 and 2,000
boundaries coincide with RTS 28 grouped reporting and cannot anchor a tick-only claim. Experiment 148 completed all
6,600 fits and 1,800 oracle constructions without numerical failure, and all five diagnostic guards passed. The
design nevertheless failed its frozen statistical gate: one rounded null exceeded both false-positive thresholds,
while all six `|tau|=0.05`, `sigma=0.10` effect cells missed 80% power. The current annual-RD route therefore stops
before market outcomes. It may be reconsidered only as a prospectively new design with substantially more
independent cutoff information or a stronger exogenous first stage, never by changing the seed, lowering the
effect floor, opening real signs, adding ordinary years post hoc or increasing GPU compute.

## 10. V6 algorithmic fee-market dynamics

| ID | Proposed object | Required discriminator | Current state |
|---|---|---|---|
| V6-NCS-1 | joint execution/blob resource response under an exact new fee-controller regime | estimate behavior before the change; combine it with the exact new controller; predict the full post-change direction/damping without refitting; replicate independently | `FORMALIZING`; prospective BPO3 candidate, outcomes blocked |
| V6-NMI-1 | mechanism-constrained identification of adaptive cross-resource demand | distinct estimand, assumptions or guarantee beyond closed-loop system ID, IV and structural demand; validate outside blockchain | `RETIRED_PRIOR_ART`; NMI `NO_SURVIVOR` |

The lead system is a computational resource market, not a cryptocurrency-price series. Exact protocol arithmetic
is a controlled mechanism, while resource demand remains endogenous and partly latent. The known controller cannot
serve as its own instrument, and raw persistence cannot be called adaptation. Common workload, batching, concurrent
fork changes, anticipation, integer reflection/saturation and fixed latent demand are mandatory countermodels.

The audit found exact controller specifications and a free CC BY 4.0 Xatu reconstruction route. It also found that
closed-loop system identification, multi-resource dynamic-fee optimization and IV gas-demand elasticity directly
cover the generic NMI method composition. The continuous scaling identity, inherited-state defect and EIP-7918
one-sided accumulation are protocol reductions/negative controls, not new theorems.

BPO1/2 may be used only for development: BPO1 is within six days of the broad Fusaka fork, both outcomes have
public analyses, and neither is an independently administered replication. Draft EIP-8138 leaves the BPO3
activation and parameters unset, so it is a prospective sealing opportunity rather than an executable data
contract. Experiment 149 is preregistered as a Mac CPU-only bit-exact conformance test over official fixtures. All
chain outcomes, remote workers, the two V100s, RTX2060 and all GPUs remain locked.
