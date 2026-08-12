# Candidate ledger v1

**Status vocabulary:** `SCOUT -> FORMALIZING -> ATTACKING -> retired / CONJECTURE / READY_FOR_HUMAN_AUDIT`  
**Iteration outcome:** `CONJECTURE_ONLY`  
**Scientific meaning:** two hypotheses remain worth attacking; neither is an admitted theorem, identity or mechanism

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
**State:** `ATTACKING`  
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

### 2.2 Candidate conjecture — not admitted

Under smooth dominated observable laws, ergodicity/mixing, local structural invariance of `pi,U`, and an explicit
quotient removing predictive symmetries:

1. `lambda_M>0` may give local identifiability of the adaptive predictive state across mechanisms;
2. finite-sample local risk might scale as `O((n lambda_M)^-1)` plus separately measurable mechanism-residual and
   mixing terms;
3. `lambda_M=0` supplies a tangent direction along which two local models are observationally indistinguishable.

This is currently only a Fisher-information/observability-shaped conjecture. Its form is dangerously close to
standard persistent excitation, controlled-world-model identification and interventional causal representation
learning. The displayed equations define an audit target; they are not claimed as new.

### 2.3 Proof obligations

- Specify the predictive quotient before writing an injectivity statement.
- Prove whether exact `G_m` makes `Gamma_M` observable or only estimable under an already identified policy.
- Exhibit a mechanism family for which standard conditional action excitation is singular but the proposed margin
  is positive, without introducing extra observed labels that trivially explain the gain.
- Derive necessity or sufficiency beyond the inverse-Fisher asymptotics already expected from regular models.
- Bound mechanism misspecification separately; an “exact” exchange implementation cannot stand in for a true
  physical/behavioral transition.
- Produce a non-market witness and a nearest-composition oracle before training a neural model.

### 2.4 Kill attacks and status rule

| Attack | Failure condition |
|---|---|
| controlled-world-model reduction | `lambda_M` is only conditional action excitation after stacking environments |
| system-identification reduction | the theorem is a standard observability Gramian or persistent-excitation result |
| CRL reduction | mechanism variation acts exactly as labelled intervention diversity used by existing identifiability theorems |
| predictive-equivalence ambiguity | latent coordinates remain arbitrary beyond the claimed quotient |
| support failure | known mechanics drive policy inputs outside all training support, invalidating the likelihood score |

If any one reduction reproduces assumptions, conclusion and error dependence, NMI-T1 becomes
`RETIRED_PRIOR_ART`. A full-rank toy example does not prevent retirement.

### 2.5 Zero-cost witness specification

For a two-dimensional latent state and one-dimensional mechanism-specific observation matrices `C_1=[1,0]` and
`C_2=[0,1]`, each single-environment Gramian is rank one while the stacked Gramian is identity. This demonstrates
complementary excitation and nothing more. The required negative control relabels this exactly as a stacked
observability calculation; unless the candidate predicts something that baseline does not, it is not a novelty
witness.

## 3. NCS lead NCS-M1 — excess closed-loop adaptation response

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

### 3.3 Identification obligations

- Predeclare exact rule timestamps, anticipation windows, early mechanical and late adaptation horizons.
- Demonstrate that the frozen baseline reproduces pre-period transitions and negative-control mechanism loops.
- Include noncommuting fixed Markov and point-process baselines, not only static or instantaneous behavior.
- Establish enough relaxation/reset for the claimed endpoint observable, or model the residual finite-time state.
- Control simultaneous fee, routing, macro, composition and venue-spillover changes.
- Use a treated/control design for both forward and reverse legs; a multi-year rule repeal is not a physical reset.
- Replicate the sign and time profile in an independent intervention family frozen before opening its post-period.

Even if all obligations pass, the result is an empirical mechanism, not proof that private beliefs were recovered.

### 3.4 Nearest empirical coverage

The US Tick Size Pilot supplies an attractive forward/reverse development case, but it is not an untouched headline
replication. The SEC already estimated heterogeneous market-quality changes, and a 2025 *Journal of Financial
Markets* paper explicitly analyzed both imposition and conclusion with depth-of-book data. It may be used to test
the measurement protocol; the Nature-level claim needs an additional independent loop or intervention family.

### 3.5 Kill attacks and status rule

| Attack | Failure condition |
|---|---|
| frozen noncommutativity | a fixed Markov/point-process baseline reproduces the residual profile |
| incomplete relaxation | the residual vanishes when the horizon is extended or state is matched |
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
