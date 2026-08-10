# NCS G0 forward audit and binding decision

**Frozen:** 2026-08-10
**Search horizon:** primary literature available through 2026-08-10
**Decision:** **FAIL — stop the current NCS invariant-calibration method route**
**Scope:** `ncs_candidate_estimator_spec_v0.md` and WP3/WP4 of `plan_v4_ncs.md`

## 1. Decision in one paragraph

The v0 candidate has no irreducible mathematical primitive. Its four substantive pieces are already established:
persistent warm-started Markov states under changing parameters; pathwise, likelihood-ratio or discrete-event
gradient estimators; randomized/coupled debiasing toward equilibrium; and empirical mixing diagnostics. The
2024--2026 forward audit closes the three escape clauses that had kept G0 AMBER. In particular, SOUL already
analyzes warm-started parameter-dependent kernels, Jarzynski/SMC methods propagate weighted particles across an
evolving sequence of parameter-dependent targets, the 2025 persistent-contrastive-divergence analysis gives
uniform-in-time errors for coupled parameter/sampling dynamics under explicit assumptions, and SOSMC places
these ideas in a general optimization framework with ESS-triggered resampling. No new coupling, weaker-assumption
residual theorem, or variance--cost theorem has been derived in this repository. Under the frozen G0 rule, the
current method route therefore fails before candidate coding or benchmark tuning.

This is a novelty failure, not evidence that invariant-measure calibration is useless. The existing components
remain valid baselines and engineering tools. They cannot be presented as a new NCS method.

## 2. Audit protocol

The audit used backward references from the original ten anchors and a forward search through 2026-08-10.
Thirty-three primary papers were scope-checked. The closest papers were checked at the algorithm/equation or
theorem level; boundary papers were checked at the abstract and claimed-scope level. Secondary summaries were
not used to decide the gate.

The candidate was tested against three necessary non-equivalence questions fixed in v0:

1. Does it introduce a new cross-parameter coupling with a proved state-staleness correction?
2. Does it give a computable finite-budget residual under materially weaker assumptions than contraction,
   minorization, coupling or known mixing bounds?
3. Does it prove a variance--cost improvement not inherited from LR/pathwise, stochastic adjoints,
   StochasticAD, GGE, SMC or Rhee--Glynn composition?

A single negative answer would prevent G0 PASS. All three answers are negative.

## 3. Nearest-method findings

| Candidate element | Closest established result | Consequence for EcoPhys |
|---|---|---|
| Persist a chain while `theta` changes | SOUL explicitly warm-starts `X_0^n = X_{m_{n-1}}^{n-1}` for a family of parameter-dependent kernels and proves convergence/bias controls under uniform ergodicity assumptions | A versioned state bank is a correctness feature, not a novel estimator |
| Correct particles for an evolving `pi_theta` | Jarzynski EBM training, JALA-EM and SOSMC use recursively weighted particles/SMC across changing targets; SOSMC gives the Feynman--Kac identity, gradient estimator and ESS-triggered resampling | “Cross-parameter reweighting + ESS” is occupied whenever the needed density or path-weight ratio is evaluable |
| Joint slow sampling and parameter dynamics | Continuous-time PCD models sampling and optimization as a coupled multiscale SDE and derives uniform-in-time and discretization error bounds under stated assumptions | A two-timescale persistent simulator plus an error ledger is not itself new |
| Debias a finite horizon | Rhee--Glynn exact estimation and coupled unbiased MCMC already provide randomized telescoping/coupling constructions | Random horizon or coupled truncation is a named baseline |
| Differentiate continuous and jump dynamics | Stochastic adjoints, centered steady-state LR, StochasticAD and GGE cover continuous paths, discrete randomness and general jump SDEs | Hybrid pathwise/LR is direct composition; high parameter dimension is already addressed |
| Automatically certify that mixing is adequate | Empirical ESS, IACT, split-chain and rank-normalized diagnostics can expose failures but do not upper-bound unseen-mode or truncation bias without model-specific assumptions | `empirically_resolved` can be a safety label, but not a rigorous residual certificate |
| Avoid knowing the mixing time in optimization | Adaptive Markov-data optimization exists, while lower bounds retain hitting/mixing-time dependence | Budget adaptation is useful but cannot erase the information-theoretic dependence |
| Learn long-time statistics rather than trajectories | DySLIM directly trains dynamics using invariant-measure objectives | The invariant-measure objective itself is occupied |

The remaining application-specific differences—large particle systems, EcoMD state schema, an L2 observation
operator and market calibration—may support a simulator paper, but do not make the estimator mathematically
non-equivalent.

## 4. Thirty-three-paper claim matrix

### 4.1 Steady-state sensitivity and stochastic differentiation

| # | Primary source | Scope checked | Claim blocked |
|---:|---|---|---|
| 1 | Glynn and Olvera-Cravioto, [Likelihood Ratio Gradient Estimation for Steady-State Parameters](https://doi.org/10.1287/stsy.2018.0023) (2019) | General-state geometrically ergodic Markov chains; steady-state LR limits | First steady-state gradient |
| 2 | Wang and Plecháč, [Steady-State Sensitivity Analysis of Continuous Time Markov Chains](https://doi.org/10.1137/18M119402X) (2019) | Centered LR, Poisson equation and time-stable variance for CTMCs | First slow-mixing/jump steady-state sensitivity |
| 3 | Assaraf et al., [Computation of sensitivities for the invariant measure of a parameter dependent diffusion](https://arxiv.org/abs/1509.01348) | Invariant-average derivatives and tangent-process analysis | First pathwise invariant-measure derivative |
| 4 | Li et al., [Scalable Gradients for Stochastic Differential Equations](https://proceedings.mlr.press/v108/li20i.html) (AISTATS 2020) | Stochastic adjoint, constant memory and cached noise | First scalable/constant-memory SDE differentiation |
| 5 | Arya et al., [Automatic Differentiation of Programs with Discrete Randomness](https://proceedings.neurips.cc/paper_files/paper/2022/hash/43d8e5fc816c692f342493331d5e98fc-Abstract-Conference.html) (NeurIPS 2022) | Unbiased AD for discrete Markov chains, ABMs and particle filters | First discrete-event/ABM AD |
| 6 | Wang, Blanchet and Glynn, [An Efficient High-dimensional Gradient Estimator for Stochastic Differential Equations](https://proceedings.neurips.cc/paper_files/paper/2024/hash/a0cd56b91305239e2580dd9440b2e155-Abstract-Conference.html) (NeurIPS 2024) | Unbiased GGE, near-constant parameter-dimension cost, general jump SDEs | First scalable high-dimensional jump gradient |
| 7 | Badolle, Gupta and Khammash, [The generator gradient estimator is an adjoint state method for stochastic differential equations](https://arxiv.org/abs/2407.20196) (2024) | Relates GGE to adjoints and the exact Integral Path Algorithm for reaction-network CTMCs | Treating GGE-like composition as a new identity |

### 4.2 Debiasing, coupling and randomized horizons

| # | Primary source | Scope checked | Claim blocked |
|---:|---|---|---|
| 8 | Glynn and Rhee, [Exact Estimation for Markov Chain Equilibrium Expectations](https://arxiv.org/abs/1409.4302) (2014) | Unbiased equilibrium expectations for Harris recurrent/contractive chains | First equilibrium debiasing |
| 9 | Rhee and Glynn, [Unbiased Estimation with Square Root Convergence for SDE Models](https://doi.org/10.1287/opre.2015.1404) (2015) | Randomized approximation levels, finite variance/cost conditions and optimal randomization | Newness of randomized truncation |
| 10 | Jacob, O'Leary and Atchadé, [Unbiased Markov Chain Monte Carlo Methods with Couplings](https://doi.org/10.1111/rssb.12336) (2020) | Meeting-time couplings, telescoping debiasing and parallel confidence intervals | Newness of coupled finite-horizon correction |
| 11 | Heng and Jacob, [Unbiased Hamiltonian Monte Carlo with couplings](https://doi.org/10.1093/biomet/asy074) (2019) | Practical coupling specialized to HMC | Generic coupling implementation claim |
| 12 | Ruiz et al., [Unbiased gradient estimation for variational auto-encoders using coupled Markov chains](https://proceedings.mlr.press/v161/ruiz21a.html) (UAI 2021) | Coupled-MCMC unbiased log-likelihood gradients | First coupled unbiased learning gradient |

### 4.3 Persistent chains, evolving targets and particle optimization

| # | Primary source | Scope checked | Claim blocked |
|---:|---|---|---|
| 13 | Tieleman, [Training Restricted Boltzmann Machines Using Approximations to the Likelihood Gradient](https://doi.org/10.1145/1390156.1390290) (ICML 2008) | Persistent contrastive-divergence chains | First cross-update state persistence |
| 14 | De Bortoli et al., [Efficient stochastic optimisation by unadjusted Langevin Monte Carlo](https://doi.org/10.1007/s11222-020-09986-y) (2021) | Warm-started parameter-dependent kernels, biased MCMC and non/asymptotic controls | State-bank staleness as a new optimization setting |
| 15 | Gruffaz et al., [Stochastic Approximation with Biased MCMC for Expectation Maximization](https://proceedings.mlr.press/v238/gruffaz24a.html) (AISTATS 2024) | Asymptotic and non-asymptotic effects of biased MCMC inside SAEM | First explicit MCMC-bias accounting in training |
| 16 | Kuntz, Lim and Johansen, [Particle algorithms for maximum likelihood training of latent variable models](https://proceedings.mlr.press/v206/kuntz23a.html) (AISTATS 2023) | Joint parameter/distribution gradient flows and particle discretizations | First particle-based joint fitting dynamics |
| 17 | Lim et al., [Momentum Particle Maximum Likelihood](https://proceedings.mlr.press/v235/lim24b.html) (ICML 2024) | Momentum, underdamped Langevin and particle MLE | Generic accelerated particle optimizer claim |
| 18 | Carbone et al., [Efficient Training of Energy-Based Models Using Jarzynski Equality](https://proceedings.neurips.cc/paper_files/paper/2023/hash/a4ddb865e0a8ca3cca43fd7387b4b0da-Abstract-Conference.html) (NeurIPS 2023) | Recursively weighted walkers avoid uncontrolled CD sampling bias | First nonequilibrium reweighting across training steps |
| 19 | Cuin, Carbone and Akyildiz, [Learning Latent Variable Models via Jarzynski-adjusted Langevin Algorithm](https://openreview.net/forum?id=LpY1jgtk8I) (NeurIPS 2025) | Weighted ULA/SMC, recursive weights and non-asymptotic optimization analysis | Newness of Jarzynski state-staleness correction |
| 20 | Valsecchi Oliva, Akyildiz and Duncan, [Uniform-in-time convergence bounds for Persistent Contrastive Divergence Algorithms](https://arxiv.org/abs/2510.01944) (2025) | Coupled multiscale sampling/parameter SDE, uniform-in-time and discretization errors | Newness of persistent two-timescale error bounds |
| 21 | Cuin et al., [Efficient Stochastic Optimisation via Sequential Monte Carlo](https://arxiv.org/abs/2601.22003) (ICML 2026) | Feynman--Kac flow over evolving `pi_theta`, weighted particle reuse, ESS resampling and convergence | Cross-parameter coupling/reweighting as the v1 primitive |

### 4.4 Controlled Markov stochastic approximation and mixing dependence

| # | Primary source | Scope checked | Claim blocked |
|---:|---|---|---|
| 22 | Andrieu, Tadić and Vihola, [On the stability of some controlled Markov chains and its applications to stochastic approximation with Markovian dynamic](https://doi.org/10.1214/13-AAP953) (2015) | Joint Lyapunov stability for parameter-controlled kernels and time-scale separation | First analysis of a learner-controlled state process |
| 23 | Fort, [Central Limit Theorems for Stochastic Approximation with controlled Markov chain dynamics](https://arxiv.org/abs/1309.3116) (2015) | CLTs, averaging and randomized truncation for controlled-chain SA | First uncertainty theory for controlled-chain updates |
| 24 | Fort et al., [Convergence of Markovian Stochastic Approximation with discontinuous dynamics](https://arxiv.org/abs/1403.6803) (2016) | Parameter-dependent controlled chains under weak continuity | First discontinuous controlled-chain convergence |
| 25 | Li, Wai and Scaglione, [State Dependent Performative Prediction with Stochastic Approximation](https://proceedings.mlr.press/v151/li22c.html) (AISTATS 2022) | Biased gradients from learner-state-dependent controlled Markov chains; finite-time analysis | First state-dependent data/learner feedback analysis |
| 26 | Mou et al., [Optimal and instance-dependent guarantees for Markovian linear stochastic approximation](https://proceedings.mlr.press/v178/mou22a.html) (COLT 2022) | Upper/lower bounds with explicit mixing-time dependence | Assumption-free finite-budget accuracy |
| 27 | Dorfman and Levy, [Adapting to Mixing Time in Stochastic Optimization with Markovian Data](https://proceedings.mlr.press/v162/dorfman22a.html) (ICML 2022) | Optimization adaptive to unknown mixing time | First budget adaptation to mixing |
| 28 | Even, [Stochastic Gradient Descent under Markovian Sampling Schemes](https://proceedings.mlr.press/v202/even23a.html) (ICML 2023) | Hitting-time lower bound plus MC-SGD/MC-SAG | Claim that diagnostics remove mixing/hitting-time cost |

### 4.5 Diagnostics, invariant objectives and differentiable simulation

| # | Primary source | Scope checked | Claim blocked |
|---:|---|---|---|
| 29 | Cowles and Carlin, [Markov Chain Monte Carlo Convergence Diagnostics: A Comparative Review](https://doi.org/10.1080/01621459.1996.10476956) (1996) | Limits and disagreement of practical stopping diagnostics | Treating an empirical diagnostic as a proof |
| 30 | Vehtari et al., [Rank-normalization, folding, and localization: An improved R-hat](https://doi.org/10.1214/20-BA1221) (2021) | Failures of classical `R-hat`, improved rank/local diagnostics and ESS | Novelty or sufficiency of split-chain checks |
| 31 | Schiff et al., [DySLIM: Dynamics Stable Learning by Invariant Measure for Chaotic Systems](https://proceedings.mlr.press/v235/schiff24b.html) (ICML 2024) | Training dynamics against invariant-measure objectives | First invariant-statistics learning objective |
| 32 | Hu et al., [DiffTaichi: Differentiable Programming for Physical Simulation](https://openreview.net/forum?id=B1eB5xSFvr) (ICLR 2020) | End-to-end differentiable high-performance physical simulation | Differentiable simulation as the contribution |
| 33 | Suh et al., [Do Differentiable Simulators Give Better Policy Gradients?](https://arxiv.org/abs/2202.00817) | Bias--variance and failure modes from stiffness/discontinuity | Generic claim that long-rollout AD is reliable |

## 5. Why each v1 escape clause fails

### 5.1 Cross-parameter coupling

For evaluable unnormalized targets, SOSMC already supplies the exact Feynman--Kac path-weight identity and a
particle implementation across `pi_(theta_k)`. Jarzynski EBM/JALA are close specializations. For implicit
simulators without an evaluable invariant-density ratio, a path-space likelihood ratio can be formed only when
the transition-law ratio is evaluable and supported; this returns to standard sequential importance sampling,
LR or Girsanov-type weighting and can suffer weight collapse. The repository contains no alternative coupling
identity and no theorem showing improved support, variance or cost. Merely recording parameter age does not
correct it.

**Verdict:** no irreducible v1 primitive.

### 5.2 Finite-budget residual under weaker assumptions

A diagnostic can reject obvious non-mixing, as exp132 demonstrated, but passing IACT, split-chain, coupling-
distance or ESS checks does not upper-bound mass in an unseen metastable mode. Rhee--Glynn/Jacob remove finite-
horizon bias only under coupling and summability conditions; SOUL/PCD bounds require explicit uniform
ergodicity, curvature or Lyapunov assumptions. Markovian optimization lower bounds retain mixing/hitting-time
dependence. No observable-only certificate in the current candidate can replace those conditions.

**Verdict:** `fail-visible` is a valuable protocol, not a new certified residual theorem.

### 5.3 Variance--cost theorem

Centered LR, stochastic adjoints, StochasticAD, GGE, coupled debiasing and SMC each carry their own known
variance/cost behavior. Combining their terms gives no automatic Pareto improvement, and v0 derives none.
Exp131/132 validate baselines and diagnostic failure behavior only; they do not establish a new rate.

**Verdict:** no new theorem or estimator identity to benchmark.

## 6. Binding project consequences

1. **G0 is FAIL, not AMBER.** The invariant-gradient method described in v0 must not be named, implemented as
   a candidate algorithm, or used as the C1 claim of an NCS submission.
2. **WP3 and WP4 are stopped.** E0--E3 candidate experiments remain blocked. More toy or solver runs cannot
   repair a mathematical non-equivalence failure.
3. **The current NCS submission route is stopped.** G0 was a hard gate. Existing NCS probabilities and the
   42-week scale-up budget no longer apply to this route.
4. **No data purchase or compute expansion is unlocked.** The two V100s remain sufficient for free audit work;
   paid L2 remains gated.
5. **Reusable work survives.** State-complete execution, exact resume, observation semantics, external
   baselines and negative-result discipline become the foundation of a rigorous simulator-audit/benchmark and
   EcoMD release paper.
6. **Reopening requires genuinely new mathematics.** A future NCS-method branch may start only after a written
   theorem/identity survives a new audit and proves something not covered by the 33 sources above. Application
   complexity or an EcoMD-only empirical win is insufficient.

## 7. Immediate free-work queue

The next allowed work is independent of the failed estimator claim:

1. freeze the EcoMD-state-to-external-message observation map and list every non-identifiable latent;
2. test that map on synthetic state-complete trajectories without opening new real held-out data;
3. assemble a cross-defect simulator audit showing how missing state, train/inference law mismatch and an
   invalid observation proxy change calibration conclusions;
4. define the fallback paper's claim ledger, external simulator requirements, data ladder and compute ladder;
5. only then preregister a genuinely unseen free-data confirmation, if a license-safe panel exists.

No GPU production run is scientifically justified before items 1--4 are frozen.
