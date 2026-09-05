# EcoMD stochastic-semantics re-entry audit

**Date:** 2026-09-04 NZST. **Literature and public-artifact cutoff:** 2026-09-04
10:35 UTC. **Mode:** outcome-blind blocker-specific re-entry audit; this is not Discovery Cycle 17.

## 1. Decision

No executable ICLR topic is activated by this audit.

| Formulation | Archetype | Decision | Decisive reason |
|---|---|---|---|
| Learn or choose a noise frame for stable EcoMD gradients | `simulator_method` | `not_trigger` | The forward law depends on the diffusion tensor, while a pathwise estimator depends on its factorization; transport-gradient and coupling-optimization work already owns the generic variance-reduction problem. |
| Use non-Gaussian Langevin baths as a refinement-invariant source of market tails | `theory_mechanism` | `not_trigger` | For finite-variance innovations the non-Gaussian stationary signature vanishes with the time step; the current alpha-stable option uses Brownian rather than Levy scaling and then clips the law. This is a numerical-semantics defect already covered by direct Langevin-integrator work. |
| Certify semantic correctness across exact-forward differentiable CTMC implementations | `measurement_method` | `partial_capability` | Several independent public implementations now exist, but the proposed forward/VJP/finite-difference and unbiased-gradient comparison is directly occupied. The artifacts do not yet provide one immutable matched clock, observable, RNG-replay and licensing fixture, and there is no irreducible certificate. |

The audit adds useful conformance tests and a more precise external testbed inventory. It removes no
route-level blocker. `candidate_harvest_authorized` remains false. No simulator or notebook was run,
no empirical or benchmark outcome was opened, and no EcoMD implementation was changed.

## 2. Question contracts

### 2.1 Noise-frame gradients

**Native object.** The derivative of an expected EcoMD trajectory functional with respect to a
continuous parameter.

**Rival explanations.** (A) gradient instability is intrinsic to the forward stochastic law; (B) it
is induced by the analyst's choice of noise factorization or coupling.

**Discriminating result.** A useful new result would have to be invariant to every factorization
that produces the same transition law, or prove a canonical factorization from independently
observable market structure. A positive answer could yield a robust estimator; a null answer is a
claim-scope gate against interpreting one matched-noise derivative as a physical response.

### 2.2 Non-Gaussian bath tails

**Native object.** The stationary return or excess-demand law under refinement of EcoMD's time
step, holding the continuous-time drift and diffusion scale fixed.

**Rival explanations.** (A) heavy stationary tails are a continuous-time mechanism implied by the
bath law; (B) they are a finite-step innovation artifact whose magnitude changes with resolution.

**Discriminating result.** A non-Gaussian tail statistic must converge to a nonzero limit under a
properly scaled continuous-time law. A positive answer would define a real stochastic mechanism; a
null answer is valuable because it invalidates an FDT or physical-bath interpretation while
retaining the option as an explicitly discrete market innovation model.

### 2.3 Cross-implementation semantic conformance

**Native object.** The derivative of the same expectation of the same cadlag CTMC state functional
at the same physical time.

**Rival explanations.** (A) disagreements reveal estimator bias or variance; (B) they reflect
different observation clocks, interpolation, stopping conventions, off-state extensions or random
couplings and therefore compare different estimands.

**Discriminating result.** A new certificate must distinguish these cases without reducing to an
analytic reference, unbiased stochastic AD, common-random-number finite differences or ordinary
gradient checking. Both a successful certificate and a proof that no such black-box certificate is
possible would be scientifically meaningful. No such residual was found here.

## 3. Noise-frame killer theorem

Consider

\[
  dX_t=b_\theta(X_t)\,dt+\sigma_\theta(X_t)\,dW_t,
  \qquad a_\theta=\sigma_\theta\sigma_\theta^\top.
\]

Weak path laws are determined by the generator and hence by `a`, not by a particular square root
`sigma`. For any orthogonal matrix `Q_theta`, replacing `sigma_theta` by
`sigma_theta Q_theta` leaves `a_theta` unchanged but changes fixed-noise derivatives.

A one-dimensional output driven by two Brownian coordinates makes the issue explicit. Let

\[
  X_\theta=\cos(c\theta)W_1+\sin(c\theta)W_2,
\]

where `W_1,W_2` are independent `N(0,t)`. The law of `X_theta` is `N(0,t)` for every `theta`, so for
every regular test function `phi`,

\[
  \frac{d}{d\theta}\,\mathbb E[\phi(X_\theta)]=0.
\]

At `theta=0`, ordinary pathwise AD returns

\[
  G_c=c\,\phi'(W_1)W_2, \qquad
  \mathbb E[G_c]=0, \qquad
  \operatorname{Var}(G_c)=c^2t\,\mathbb E[\phi'(W_1)^2].
\]

The arbitrary representation constant `c` can therefore set the estimator variance to any
nonnegative scale while the forward law and true gradient stay fixed. Its sign also reverses every
sample derivative when `c` is negated. This is an exact representation witness, not an empirical
anomaly.

The witness does not establish novelty. [Jankowiak and
Obermeyer](https://proceedings.mlr.press/v80/jankowiak18a.html) characterize pathwise estimators as
nonunique transport-equation velocity fields and optimize their variance. [Hall, Katsoulakis and
Rey-Bellet](https://arxiv.org/abs/1609.02739) prove optimality of common-random-path coupling for a
class of generalized-Langevin finite-difference estimators. [Bras and
Pages](https://arxiv.org/abs/2307.12703) learn same-marginal SDE correlations for variance
reduction, while [Rousse et al.](https://arxiv.org/abs/2512.00987) explicitly optimize equivalent
noise implementations through diffusion gauges. A generic learned gauge, canonical coupling or
minimum-variance pathwise field is therefore occupied. EcoMD's production core also uses additive
iid noise rather than a learned full diffusion square root, so its native residual is especially
weak.

**Decision:** `not_trigger`. Preserve the theorem as an interpretation test. Re-entry requires a
market-observable restriction that identifies a unique noise frame, or a representation-invariant
gradient certificate false for the transport and coupling parents.

## 4. Non-Gaussian bath refinement audit

### 4.1 Finite-variance innovations

For the Euler discretization of a scalar Ornstein-Uhlenbeck process,

\[
  X_{n+1}=rX_n+s\epsilon_n, \qquad r=1-\lambda h,
\]

with unit-variance iid innovations having excess kurtosis `kappa_epsilon`, stationarity gives

\[
  \kappa_X=\kappa_\epsilon\frac{1-r^2}{1+r^2}
           =\kappa_\epsilon\lambda h+O(h^2).
\]

EcoMD's Student-t option normalizes the innovation variance. With `nu=5`,
`kappa_epsilon=6`, so the bath-only stationary excess kurtosis is `6 lambda h + O(h^2)` and vanishes
under refinement. Matching the first two moments preserves the intended one-step covariance, not a
non-Gaussian continuous-time equilibrium law. [Gronbech-Jensen's direct
analysis](https://link.springer.com/article/10.1007/s10955-023-03104-8) already shows that
non-Gaussian discrete-time Langevin noise can retain first and second moments while distorting
higher and Boltzmann statistics in a time-step-dependent manner.

### 4.2 Alpha-stable option

The current source samples a symmetric alpha-stable variate, multiplies it by the Brownian factor
`sqrt(h)`, and clips it at a fixed configured threshold. If clipping were removed, an AR(1) driven
by stable increments would have stationary scale

\[
  \Sigma_h=
  \left(\frac{s_h^\alpha}{1-|1-\lambda h|^\alpha}\right)^{1/\alpha}.
\]

With the implemented `s_h proportional sqrt(h)`,

\[
  \Sigma_h\asymp h^{1/2-1/\alpha},
\]

which diverges for `alpha<2`. A Levy-process increment instead scales as `h^(1/alpha)`; classical
Euler-limit theory for Levy-driven SDEs treats precisely this different small-step regime
([Jacod](https://arxiv.org/abs/math/0410118)). Fixed clipping restores finite variance, but the
central-limit refinement is then Gaussian and the clipped variate is not variance-normalized, so
both the effective diffusion scale and the tail shape depend on the chosen clip and time step.

This is a concrete EcoMD QA finding: past trained-Levy results describe one discrete transition
kernel and must not be called a refinement-invariant physical bath without a step-size study. It is
not a new ICLR method or market mechanism. The direct statistical-physics parent already owns the
core observation, and the stable scaling correction is standard Levy-SDE numerics.

**Decision:** `not_trigger`. A future paper child would require a market-native event law whose
heavy-tail limit survives simultaneous time-step, clip and observation-clock refinement and yields
a prediction not inserted through the innovation distribution itself.

## 5. Public CTMC artifact audit

Only source, metadata and release contracts were inspected. No notebook, package, test or figure
script was executed.

| Asset | Frozen identity | Rights/release state | Relevant semantics | Contract failure |
|---|---|---|---|---|
| [CTMCDL/codeExactDL](https://github.com/CTMCDL/codeExactDL/tree/f191cd435ade065ff4356d8721ac1cac0f992a83) | `f191cd435ade065ff4356d8721ac1cac0f992a83` | No tag and no repository licence found | Exact hard Gumbel-max event choice with softmax backward; exponential waiting time | Notebook collection rather than a reusable package; no complete RNG export; dimerization uses linear interpolation of jump states |
| [stochastix 0.2.0](https://github.com/fmottes/stochastix/tree/2d83fe64ac1bff9d80367338e3b4fc222357fb66) | tag `v0.2.0`, commit `2d83fe64ac1bff9d80367338e3b4fc222357fb66` | Apache-2.0; citation metadata; tagged release | Exact hard event forward, soft backward, cadlag forward-fill helper, event/time/propensity trace | Returned result omits final PRNG key and sampled uniforms; no shared-noise intervention fixture |
| [stochastix-paper](https://github.com/fmottes/stochastix-paper/tree/cc09f8c77b8009b4987a335e19680b7217ef7450) | `cc09f8c77b8009b4987a335e19680b7217ef7450` | Apache-2.0; no tag | Five published inference/design tasks and analytic thermodynamic bounds | Requirements specify broad lower bounds such as `stochastix>=0.1.0`; the paper fixture is not dependency-frozen |
| [DifferentiableGillespie](https://github.com/gerland-group/DifferentiableGillespie/tree/a3ee28b3081f42cef7f0d0f85c32d8d4c67ec556) | `a3ee28b3081f42cef7f0d0f85c32d8d4c67ec556` | No tag or root licence file; package metadata declares MIT | GS-ST, score-function and alternative-path estimators; event-count and physical-time objectives; analytic CME truth for association | Distribution rights are incompletely packaged; dependencies are unpinned; no common fixture with the other implementations |

The public portfolio is materially better than the earlier scan: there are now multiple
independently maintained exact-forward hard-event implementations and at least one analytic-gradient
reference. This narrows the old raw asset gap. It does not remove the route-level two-system
contract because the systems do not yet share an immutable observable, physical clock, stopping
rule, perturbation, event-level random tape and dependency lock.

There is also a specific semantic warning. `codeExactDL`'s dimerization notebook takes an exact
cadlag jump path at event times but linearly interpolates adjacent count states onto the loss grid.
The resulting between-event states are not the CTMC state. Its ion-channel task instead uses
step/integral-style time binning. `stochastix` explicitly forward-fills states, while Burger et al.
include a separate smooth temporal cutoff and show that omitting waiting-time contributions gives a
wrong physical-time gradient. “Exact forward” therefore does not by itself identify the
observation-time loss or its derivative.

## 6. Collision with the proposed semantic benchmark

The obvious experiment would freeze a small analytic CTMC and compare forward law, VJP direction,
bias, variance, optimization and compute across the implementations. That does not survive the
novelty screen:

- [Burger et al. v2](https://arxiv.org/abs/2604.02121) already compare GS-ST, score-function and
  alternative-path estimators against analytic gradients for event-count and physical-time
  observables, including waiting-time terms, divergent variance and biased optima.
- [StochasticAD](https://proceedings.neurips.cc/paper_files/paper/2022/hash/43d8e5fc816c692f342493331d5e98fc-Abstract-Conference.html)
  constructs unbiased derivatives of expectations for discrete stochastic programs and evaluates
  Markov chains and agent-based programs.
- [ADEV](https://doi.org/10.1145/3571198) gives a denotationally sound source transformation for
  expected values of mixed discrete/continuous probabilistic programs.
- [Mosaic](https://arxiv.org/abs/2606.27895) already standardizes forward and VJP interfaces across
  differentiable physics solvers and evaluates finite-difference accuracy, conditioning, cost,
  compatibility and optimization outcomes.

Finite differences alone are not a semantic oracle at discontinuities, but analytic CME and the
unbiased estimators cover the small truth systems proposed here. A benchmark of interpolation and
clock mistakes would be useful software engineering; it has no new estimand, theorem, estimator or
market bridge. An EcoMD row would further compare a fixed-step Langevin process with CTMCs and thus
change the scientific object.

**Decision:** `partial_capability`, with zero removed route blockers. Re-entry requires a theorem-level
certificate that is invariant to forward-equivalent program refactorings, distinguishes clock and
boundary terms that analytic/finite-difference/unbiased references cannot, and has a nontrivial
power or sample-complexity result on two independently maintained systems.

## 7. Compute and publication decision

There is no experiment plan because no formulation passed the truth and novelty gates. In
particular:

- no SSH session was opened to `100.113.230.38`, `100.80.236.112` or `100.123.220.57`;
- the A800 and both V100 workers received zero jobs from this audit;
- no environment, branch, data shard, W&B run or remote directory was created;
- the current Paper D machine decision cannot authorize this unrelated work.

The three formulations are terminal children, not a new discovery cycle. A future qualified
trigger, topic card and current machine decision are all required before implementation or GPU use.

## 8. Exact re-entry conditions

Re-audit only if at least one written object exists:

1. a noise-frame-invariant gradient or abstention theorem with a market-observable identifying
   restriction and a claim false for transport-field and optimal-coupling parents;
2. a properly scaled non-Gaussian continuous-time market mechanism whose nontrivial tail prediction
   survives time-step, clip and observation-clock refinement without inserting the desired tail
   index as an innovation hyperparameter; or
3. an irreducible stochastic-simulator semantic certificate, with a power or complexity theorem,
   that cannot be replaced by analytic CME, unbiased stochastic AD, common-random finite
   differences or Mosaic-style VJP checking, plus a licensed immutable matched fixture on two
   independent systems and a market-native action/response bridge.

Until one exists, extra implementations, seeds, temperatures or GPU throughput have no topic-
selection value.
