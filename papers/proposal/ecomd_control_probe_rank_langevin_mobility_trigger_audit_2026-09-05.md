# EcoMD control-probe rank and Langevin-mobility trigger audit

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

The candidate asked whether the 2026 conditional-score Langevin method could become a new ICLR
paper by observing the same system under several known external controls and using response
differences to identify a state-dependent mobility tensor. The strongest possible version assumes
that each control contributes a known vector field `u_k(x)` and that the controlled drift difference
`delta b_k(x)` is itself recoverable. Even under those oracle assumptions, the identification result
is exactly the pointwise matrix equation

\[
\Delta B(x)=M(x)U(x).
\]

Full row rank of `U(x)` gives one pseudoinverse formula for `M(x)`; deficient rank leaves a
positive-definite null direction. This is useful as a design diagnostic, but it is elementary linear
algebra rather than a new learning method or theorem.

The apparent extension is also directly crowded. Lorch et al. already learn stationary diffusions
across intervention environments; Zweig et al. give intervention-count identification bounds for
linear and small-noise nonlinear SDEs; and the 2026 ICML spotlight *One Intervention per Component
Is Enough* proves graph-structured steady-state recovery with an estimator. Known-force mobility
probing is the established premise of active microrheology.

Most importantly, the oracle control contract is false for the proposed market examples. A fee,
rebate, tick, auction, funding or execution-rule change alters agents' information, feasible actions,
objectives and policies. It is not a calibrated additive force in a fixed observable EcoMD state.
Writing an unknown response field as a known `u_k` would assume the mechanism that the paper is
supposed to learn.

The decision is therefore `not_trigger`. This formulation is an exact reduction to the already
closed `multi_stationary_drift_tomography_v11`, `solenoidal_excitation_gap_v12`,
`observation_quotient_response`, and `oscillatory_liquidity_microrheology` routes. It creates no new
route node and authorizes no computation.

## 2. Question, rivals, and cheapest discriminator

Let `X_t` be a declared market-native observable state and consider controlled diffusions

\[
dX_t=\{b_0(X_t)+M(X_t)u_k(X_t)\}\,dt+\sigma(X_t)\,dW_t,
\qquad k=0,\ldots,K,
\]

where `u_0=0`. The proposed object is the mobility `M(x)`, not merely a predictive transition
model.

- **H1 -- calibrated probe:** protocol controls provide known, linearly independent `u_k`; their
  drift responses identify `M`, including directions passive finite-lag constraints cannot see.
- **H0 -- unknown strategic mechanism:** the rule changes the policy population and observation
  process through an unknown field `g_k(x, history)`; controls add environments but do not reveal a
  physical force or a common Markov generator.

**Cheapest discriminator.** Before data or simulation, require a source-level derivation showing
that a legal market action changes the generator by the declared `M(x)u_k(x)` while preserving the
state, noise, observation kernel and strategic policy law. No audited action satisfies that
contract. The theorem screen below then shows that even granting it produces only a rank test.

A positive result would supply an active identification instrument for otherwise hidden mobility.
A null result remains valuable because it distinguishes extra regimes from calibrated forces and
prevents rule-response correlations from being given physical mobility semantics.

## 3. Exact probe-span lemma

At a fixed state `x`, stack the known probes and controlled drift differences as

\[
U=[u_1,\ldots,u_K]\in\mathbb R^{d\times K},\qquad
\Delta B=[\delta b_1,\ldots,\delta b_K]\in\mathbb R^{d\times K}.
\]

Under the candidate model, `Delta B=M U`.

1. If `rank(U)=d`, then
   \[
   M=\Delta B U^\top(UU^\top)^{-1}.
   \]
   Identification is an ordinary full-row-rank linear solve.
2. If `rank(U)<d`, choose nonzero `v` with `v^T U=0`. For any symmetric positive-definite
   solution `M`,
   \[
   M_\epsilon=M+\epsilon vv^\top
   \]
   is also positive definite for every sufficiently small positive `epsilon` and satisfies
   `M_epsilon U=M U`. Thus even symmetry and positive definiteness do not remove the ambiguity.
3. If only projected responses `H Delta B` or selected finite-lag observable constraints are
   available, the identified operator is no larger and can be strictly smaller. A pointwise
   mobility claim therefore requires both full probe span and full response recovery.

This lemma is a useful falsifier: adding more environments helps only through the span they create
in a fixed state representation. It does not by itself supply a nonparametric rate, an intervention
selection algorithm, partial-observation recovery or a market interpretation.

## 4. Information-regime trilemma

The proposal has no unoccupied information regime.

| Available information | Consequence |
|---|---|
| Full short-time transition law in every coordinate | The generator's drift and diffusion are already given by infinitesimal conditional moments; controls are unnecessary for generic generator identification. |
| Stationary distributions under several interventions | This is the setting of stationary-diffusion learning and current interventional-SDE identifiability work. |
| Selected finite-lag correlations or projected observables | Conditional-score fitting constrains only the chosen generator action; probe differences add linear equations but do not imply pointwise mobility uniqueness. |
| Market rule labels without a known generator action | The controlled response field is unknown, so `Delta B=M U` is a parametrization, not an identified physical law. |

The route would need a theorem that is neither full-information generator estimation, nor existing
multi-environment stationary-SDE recovery, nor generic rank-deficient inverse design. None was
found.

## 5. Collision audit

The minimum primary-work screen is already decisive.

1. **Conditional-score effective Langevin dynamics (2026).** Giorgini fits state-dependent
   mobility from stationary lagged pairs and conditional transition scores, matching selected
   finite-lag dynamical sectors without repeated integration. Its general object is an
   observable-dependent projected generator or mobility equivalence class, not an automatically
   pointwise-identified mobility.
2. **Causal stationary diffusions (AISTATS 2024).** Lorch, Krause and Schölkopf fit nonlinear
   stationary SDEs jointly across intervention environments with an RKHS generator-stationarity
   objective and evaluate unseen interventions. Cross-environment SDE learning is not open.
3. **Interventional SDE identifiability (UAI 2026).** Zweig et al. give the first provable bounds
   for unique parameter recovery from multiple interventional stationary distributions, with tight
   linear counts and nonlinear small-noise bounds. Broad intervention-count framing is occupied.
4. **One intervention per component (ICML 2026 spotlight).** The paper proves generic OU recovery
   up to global scale with one intervention per strongly connected component under graph and
   spectral conditions, and provides a regularized moment estimator. A rank/count theorem plus
   least squares would be incremental.
5. **Active microrheology.** Constant and oscillatory known forces have long been used to measure
   tracer mobility. Importing this probe-response template into a market is analogy, not novelty;
   the missing contribution is a valid market actuator map.

This is stronger than a keyword collision: the proposed positive theorem reduces to a special,
more oracle-rich case of the existing interventional identification problem, while its physical
interpretation is already the core design of active microrheology.

## 6. Why ordinary repairs do not work

- **Learn `u_k` jointly.** For any invertible field `A(x)`, replacing `M` by `M A^{-1}` and every
  `u_k` by `A u_k` preserves all controlled drifts. Joint learning creates a gauge rather than
  identifying mobility.
- **Use more fee or tick levels.** Many scalar levels can remain collinear in state space; number of
  regimes is not probe rank. Strategic response can also make the field level-dependent.
- **Use EcoMD's differentiability.** Simulator gradients describe the chosen EcoMD mechanism. They
  cannot verify that the real rule change has the same generator action or that the learned state
  is Markov and common across regimes.
- **Call policy adaptation part of mobility.** Then `M` ceases to be a transport coefficient shared
  across controls and becomes an arbitrary conditional response model. Predictive evaluation may
  remain possible, but the mobility-identification claim disappears.
- **Fit only synthetic controlled systems.** This can validate code against the assumed equation,
  not distinguish H1 from H0 or provide an independent market truth system.

## 7. Gate matrix

| Gate | Result |
|---|---|
| Market-native state common across controls | Not established |
| Legal action has known additive generator field | Fail |
| Probe span is pointwise full rank | Not established; scalar rule grids do not imply it |
| Full controlled drift difference is observable | Fail under aggregate/partial market state |
| Markov closure and common noise are preserved | Not established |
| Identification theorem beyond pseudoinverse/nullspace | Fail |
| Method beyond stationary interventional-SDE parents | Fail |
| Physical probe concept unoccupied | Fail |
| Independent same-estimand truth systems | Fail |
| EcoMD adds falsifiable information | Fail |

## 8. Preserved reusable result

The reusable asset is the **probe-span audit**. Every future “active microrheology for markets” or
“controlled mobility tomography” proposal must expose, in one coordinate system:

1. the legal action-to-generator fields `u_k(x)`;
2. the rank of their pointwise span over the declared support;
3. the actually observed response projection; and
4. invariance of the state, noise, observation and strategic policy contracts across actions.

Failure of any item demotes the result to an environment-conditioned predictive model. This screen
can stop misleading physics claims cheaply, but it is not itself an ICLR paper.

## 9. Exact re-entry conditions

Re-audit only if all of the following are supplied before outcome access:

1. a legal market or controlled non-market system with an externally calibrated action whose
   generator perturbation is known in observable coordinates and does not require assuming the
   response mechanism;
2. a nonparametric finite-lag identification theorem under partial observation, with an explicit
   estimator, finite-sample upper bound and matching or separating lower bound that is not reducible
   to the probe-span rank condition or existing stationary-intervention results;
3. a policy/state/noise invariance or a valid model of their controlled change that preserves a
   common estimand;
4. two independently governed same-estimand truth systems, one with a frozen untouched
   confirmation partition; and
5. an equation-level distinction from conditional-score Langevin fitting, KDS, Zweig et al., the
   ICML 2026 OU result, active experimental design and standard microrheology.

More regimes, larger synthetic sweeps, a learned force encoder, another fee/tick dataset, an EcoMD
gradient or a neural pseudoinverse is not a trigger.

## 10. Primary sources

1. Giorgini, *Conditional Score-Based Modeling of Effective Langevin Dynamics*, arXiv v2, 2026,
   https://arxiv.org/abs/2604.23952
2. Lorch, Krause and Schölkopf, *Causal Modeling with Stationary Diffusions*, AISTATS 2024,
   https://proceedings.mlr.press/v238/lorch24a.html
3. Zweig et al., *Towards Identifiability of Interventional Stochastic Differential Equations*, UAI
   2026, https://proceedings.mlr.press/v337/zweig26a.html
4. Salehkaleybar et al., *One Intervention per Component Is Enough: Towards Identifiability in
   Linear Stochastic Dynamics from Steady State*, ICML 2026 spotlight,
   https://openreview.net/forum?id=vjI9tsebtP
5. Knezevic, Aviles Podgurski and Stark, *Oscillatory active microrheology of active suspensions*,
   Scientific Reports 11, 22706 (2021), https://doi.org/10.1038/s41598-021-02103-7

## 11. Compute decision

This audit is `not_trigger`; `candidate_harvest_authorized=false`. Do not generate a synthetic probe
dataset, implement a control-conditioned score model, modify EcoMD, access market outcomes, SSH to
a worker, or schedule the A800/V100 pool under this route. The existing constraint-attribution
machine decision is unrelated and grants no authority here.
