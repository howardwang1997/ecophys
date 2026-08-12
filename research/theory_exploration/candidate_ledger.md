# Candidate ledger v1

**Status vocabulary:** `SCOUT -> FORMALIZING -> ATTACKING -> retired / CONJECTURE / READY_FOR_HUMAN_AUDIT`  
**Iteration outcome:** `CONJECTURE_ONLY`  
**Scientific meaning:** the NMI lead is retired; one NCS hypothesis remains worth attacking and is not an admitted mechanism

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
**State:** `ATTACKING`  
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

## 4. Retired starting candidates

| ID | Final state | Mathematical reason |
|---|---|---|
| S1 action lift | `RETIRED_PRIOR_ART` | structural replay / sequential policy g-formula plus unchanged support and confounding requirements |
| S2 single-environment impossibility | `RETIRED_IDENTIFIABILITY` | generic observational equivalence without a new constructive boundary |
| S3 fast/slow response | `RETIRED_PRIOR_ART` | Markov perturbation, Duhamel and singular averaging |
| S4 predictive quotient | `RETIRED_PRIOR_ART` | PSR, bisimulation and causal abstraction |
| S5 unseen composition | `RETIRED_PRIOR_ART` | soft-intervention composition, homomorphism and effect invariance |

## 5. Version history

| Date | Version | Change | Decision |
|---|---|---|---|
| 2026-08-12 | v1 | Audited S1–S5, retired all five, created NMI-T1 and NCS-M1, and added the frozen noncommutativity counterexample. | `CONJECTURE_ONLY`; no data/GPU authorization |
| 2026-08-12 | v1.1 | Exp144 confirmed stacked-observability reduction and a fixed-operator order effect; neither active lead advanced. | `CONJECTURE_ONLY`; continue symbolic attacks only |
| 2026-08-12 | v1.2 | Added the event-layer information identity and switching/active-design coverage; retired NMI-T1. | NMI `NO_SURVIVOR`; NCS `CONJECTURE_ONLY`; no data/GPU authorization |
| 2026-08-12 | v1.3 | Replaced raw NCS order effects with a contraction-envelope exceedance test over a validated frozen baseline class. | NCS remains `ATTACKING`; empirical identification and data contract absent |
