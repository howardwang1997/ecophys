# EcoMD re-entry trigger scan, round 2

**Date:** 2026-09-04

**Mode:** outcome-blind incremental trigger audit; this is not a new topic cycle

**Decision:** **NO QUALIFIED TRIGGER. Cycle 17 remains closed; no implementation, simulator run, data
outcome access, machine card, SSH session, or GPU job is authorized.**

## 1. What changed since the first 2026-09-04 audit

The incremental search found one especially relevant result that was absent from the prior audit:
[Propensity Straight-Through Gradients for Discrete Stochastic Systems](https://arxiv.org/abs/2608.25631),
submitted on 2026-08-26. It differentiates normalized event propensities while retaining an exact hard
categorical CTMC trajectory. The paper proves exactness for a one-step conditional mean and gives the local
multistep discrepancy in closed form. This is meaningful epistemic progress: the hard-event question now has
a precise error term rather than only a generic statement that straight-through gradients are biased.

It is not yet an EcoMD paper opportunity. The discrepancy is exactly the unresolved scientific issue, and the
nearest literature already contains exact-forward Gumbel straight-through simulation, score-function and
alternative-path estimators, coupled and unbiased CTMC sensitivities, differentiable queueing simulation, and
hard-contact soft-gradient methods. No new correction, global certificate, or cost--accuracy theorem has been
derived here. Moreover, EcoMD's scientific transition is a fixed-step Langevin update with neural forces; its
order-event streams are principally observation adapters. Replacing that transition by a Gillespie CTMC merely
to use PST would change the research object rather than extend it.

A subsequent theorem-level killer test found a more basic obstruction: a surrogate gradient through a discrete
state is not determined by the exact forward model unless its off-state continuous extension is frozen. The
result is elementary and decisive, but not a publishable new primitive. AISTATS 2026 already axiomatizes and
optimizes a broad generalized straight-through class, and model-specific descent versus instability from good
and bad straight-through choices is established prior work.

The other new materials sharpen old boundaries but do not remove them: one licensed exact-counterfactual
time-series suite is now usable; a second epidemic ABM repository lacks an explicit software licence; new
stationary-SDE sign-identifiability theory assumes a known linear graph; and a new financial generalized
Langevin model directly occupies gauge-reduced option calibration.

## 2. The only method question worth retaining as a watch item

### Exact question

For a legal rate or policy perturbation in an exact discrete-event stochastic simulator, when does an
exact-forward, surrogate-backward gradient preserve the **sign and ranking** of the true expected response over
long horizons and hard event-boundary regimes?

### Rival explanations

- **H1 — mixing-damped surrogate error.** The local finite-difference-to-directional-derivative discrepancy is
  damped by contraction or mixing, so PST or another straight-through estimator remains a safe descent
  direction even when its magnitude is biased.
- **H0 — curvature-driven sign failure.** Queue depletion, changing event support, and nonlinear continuation
  values accumulate local curvature error, so the surrogate can reverse a true response sign while the forward
  path remains statistically exact.

### Decisive result

A defensible method paper would need either:

1. a computable global error bound whose observable certificate guarantees the true gradient sign and becomes
   non-vacuous in hard-event regimes; or
2. a new estimator correcting the multistep discrepancy with a proved bias--variance--cost advantage over
   PST, Gumbel straight-through, score-function, alternative-path, coupled finite-difference, and established
   unbiased CTMC sensitivity estimators.

The comparison must use analytic or finite-state truth, at least two independently maintained non-EcoMD
systems, hard negative regimes, and equal wall-clock or event-evaluation budgets. A market application would
come last and would need a native intervention rather than a relabelled chemical reaction.

### Why positive and null answers both matter

A positive result would turn a heuristic backward pass into an auditable optimizer. A null result would still
produce a useful abstention boundary showing where exact-forward simulation must fall back to an unbiased or
zeroth-order estimator. This is therefore a scientifically valid question.

### Decisive forward-equivalence counterexample

Let (Y\sim\operatorname{Bernoulli}(p)) and let the discrete objective be (Q(0)=0), (Q(1)=1). The exact
expected objective is (J(p)=p), so (J'(p)=1). Now define an entire family of smooth extensions,

\[
Q_c(x)=x+c\,x(1-x)(1-2x).
\]

Every (Q_c) agrees with (Q) on all reachable forward states, so it produces exactly the same samples,
losses, and true gradient. But (Q_c'(0)=Q_c'(1)=1+c). An identity straight-through backward rule therefore
returns (1+c) for every sample: its value can have arbitrary magnitude and has the wrong sign whenever
(c<-1), despite identical forward semantics.

The same construction can be inserted as a continuation value after a hard event. Thus, a sign or ranking
certificate cannot be a property of the exact discrete forward process alone. It must either declare and
justify a canonical off-lattice extension, or replace directional derivatives by reachable-state differences,
likelihood ratios, couplings, or additional queries. The latter choices return to the already named unbiased
and finite-difference estimator families. This obstruction occurs before any long-horizon mixing argument, so
mixing cannot repair an unspecified backward representation.

### Why it is not currently a candidate

[Vilar and Saiz](https://arxiv.org/abs/2608.25631) already derive the one-step result, local curvature bound, and
affine exactness condition. [Burger et al.](https://arxiv.org/abs/2604.02121) compare Gumbel straight-through,
score-function, and alternative-path estimators and show both variance explosions and bias-driven incorrect
optima. [Vilar and Saiz's earlier exact-forward method](https://doi.org/10.1002/advs.76297),
[differentiable discrete-event queueing control](https://arxiv.org/abs/2409.03740),
[mixed-order differentiable-simulator gradients](https://proceedings.mlr.press/v162/suh22b.html), and
[DiffMJX](https://proceedings.iclr.cc/paper_files/paper/2026/hash/44039e59aaf6a41b16f1fc5b27bcd409-Abstract-Conference.html)
occupy the surrounding method space. The obvious unbiased residual correction reduces to established
score-function/control-variate or auxiliary-path constructions; the obvious event-branch correction reduces to
coupled CTMC sensitivity methods. A new name or market benchmark would not escape those parents.

The representation-level escape is also occupied. [Hooper and
Shekhovtsov](https://proceedings.mlr.press/v300/hooper26a.html) axiomatize generalized straight-through
estimators and derive bias-constrained minimum-variance members; [Yin et
al.](https://arxiv.org/abs/1903.05662) prove descent alignment only for properly chosen coarse gradients under
specific assumptions and exhibit instability for a poor choice. A canonical multilinear-extension route does
not restore novelty: [Sornwanee](https://arxiv.org/abs/2602.05119) already proposes unbiased single-query
gradients for product-Bernoulli combinatorial objectives. The binary construction above is therefore a kill
test for an under-specified claim, not an ICLR contribution by itself.

This question is retained only as a **watch item**, not a D-3 program. Re-entry requires an actual theorem or
estimator sketch that survives those reductions before any implementation.

## 3. External truth and testbed audit

### DoTime: one usable exact-counterfactual system

[DoTime](https://arxiv.org/abs/2607.27263) provides paired interventions and shared-noise counterfactuals across
eight causal structures and four frozen suites. The pinned `dotime` 0.1.3 package is Apache-2.0, its suites are
CC-BY-4.0, and its PyPI provenance binds the release to commit
`cc18c0ec2d5e2a02130b39b8b4c582216f71c295`. This is a useful analytic/synthetic truth system.

It does not contain interacting agents, hard categorical market events, or exact transaction semantics. It can
be one negative-control system for a future method but cannot establish a market claim or the required
two-system hard-event contract by itself.

### Epidemic counterfactual benchmark: scientifically useful, not contract-ready

The 2026 [epidemic counterfactual benchmark](https://arxiv.org/abs/2606.05692) uses a calibrated ABM to generate
static and time-varying policy counterfactuals for more than 150 US counties. Its public repository exposes
intervention scenarios and differentiable calibration. At audit time, however, GitHub reported no repository
licence for commit `824ca2a9785038eaec4e277903856d796ac4adb3`, and data preparation requires external API keys.
The paper and code therefore provide a second conceptual lineage, not a lawful pinned reusable implementation
contract.

Together these sources partially improve test infrastructure but do not remove `two_system_contract_missing`:
there are not yet two licensed, independently maintained systems implementing one common gradient estimand and
hard negative event regimes.

## 4. Identifiability audit

[van Seeventer and Salehkaleybar](https://proceedings.mlr.press/v337/seeventer26a.html) establish a genuine new
trichotomy for edge-sign identifiability in stationary linear SDEs with known causal structure and unknown
diffusion. That theorem does not cover EcoMD's unknown graph, nonlinear neural interactions, latent private
agent states, or aggregate market observation. The apparent partial-observation extension is also not empty:
[Browning et al.](https://arxiv.org/abs/2503.19241) already give exact moment-based structural-identifiability
analysis for partially observed linear and near-linear SDEs.

[DIML](https://arxiv.org/abs/2601.17678) further occupies inverse mechanism learning from multi-agent learning
trajectories, with payoff-difference identifiability under a conditional-logit response model. Real market data
do not reveal the assumed learning dynamics, payoff observations, or joint action state, so applying DIML to
EcoMD would substitute assumptions for the missing information.

The market-specific neighborhood has also tightened. The 2026
[Lean Marketron](https://arxiv.org/abs/2608.20589) explicitly removes scaling gauges and sign symmetries,
calibrates a reduced model to an SPX option surface, and derives a closed-form generalized Langevin memory
kernel. Its two relaxation rates remain weakly identified from one surface, but the paper directly occupies the
broad claim that gauge reduction makes a Langevin market model identifiable. A second EcoMD gauge/calibration
paper would need a theorem or external intervention that is false in Marketron, not another fit.

Result: the new sources reinforce rather than invalidate the repository's observation-quotient and
standard-parent closures.

## 5. Market truth and LOB control audit

[K-nearest-neighbor LOB resampling](https://arxiv.org/abs/2409.06514) is a serious historical-data baseline for
off-policy strategy evaluation, interactive impact, and pro-rata liquidation. Its convergence result and
direct action injection make it mandatory for any later interventional LOB benchmark. It does not assign a real
market intervention or reveal a same-state counterfactual, so it cannot validate EcoMD prospectively.

[Persistent Private Information in Experimental Asset Markets](https://onlinelibrary.wiley.com/doi/full/10.1002/soej.70010)
contains a controlled manipulation of the informed-trader share and rich human-market behavior, but its raw data
are available only on reasonable request and all reported outcomes are already published. It supplies neither a
public licensed replay package nor an untouched confirmation source. The open 104-market Ikica archive remains
the stronger event-rich laboratory asset, but that source was already audited in Cycle 9. The new
[inverse market-efficiency study](https://link.springer.com/article/10.1140/epjds/s13688-026-00684-9) uses those
published data and an independent published classroom-market archive; it explicitly treats field validation as
future work. It does not create new assigned outcomes.

Result: no new field or laboratory truth asset removes the assignment, replay, rights, or prospective-holdout
blockers.

## 6. Trigger decisions

| Proposed trigger | Decision | What genuinely changed | Fatal remaining blocker |
|---|---|---|---|
| PST and exact-forward surrogate gradients | `partial_capability` | Exact one-step conditional-mean sensitivity and an explicit multistep discrepancy now exist. | Forward-equivalent extensions can flip the surrogate sign; no new invariant EcoMD-native estimator/certificate; direct generalized-ST, CTMC, queueing, contact, and discrete-gradient parents. |
| DoTime plus epidemic counterfactual suites | `partial_capability` | One licensed frozen exact-counterfactual suite and one independent ABM lineage exist. | Only one is contract-ready; no common hard-event gradient estimand or real-market bridge. |
| Stationary SDE sign identifiability | `not_trigger` | A new linear known-graph sign theorem exists. | Partial observation/nonlinear latent dynamics remain outside its assumptions and already have direct structural-identifiability prior art. |
| KNNR interactive LOB resampling | `partial_capability` | A convergent historical-data OPE baseline supports legal synthetic trade actions. | Observational support is not assigned intervention truth or a same-state field counterfactual. |
| Private-information laboratory market | `partial_capability` | A controlled human-market manipulation is available in primary work. | Request-only raw data, published outcomes, no sealed source, and no independent same-estimand replication. |
| Lean Marketron gauge/GLE result | `not_trigger` | A new direct financial model removes exact gauges and derives a GLE kernel. | It occupies the broad claim and offers neither a same-state rival prediction nor a truth asset that rescues EcoMD. |

All six decisions are recorded append-only in the re-entry ledger. None removes a named route blocker, so
`candidate_harvest_authorized` remains false.

## 7. Compute and publication decision

No experiment plan is scientifically authorized. The three servers remain outside this proposal:

- `100.80.236.112` and `100.123.220.57`: zero V100 allocation;
- `100.113.230.38`: zero A800 allocation;
- no SSH, environment creation, repository sync, data staging, process launch, or remote write was performed.

The ICLR 2027 paper deadline is 2026-09-25 AoE. Even if the PST-derived watch item later becomes viable, a new
theorem/estimator, two-system contract, implementation, experiments, and paper cannot be completed rigorously in
the remaining window. It should not compete with the already completed Paper D submission.

## 8. Exact next review condition

Continue only with outcome-blind algebra and source work. Re-open this family if and only if one of the following
exists in writing:

1. a representation-invariant global sign-preservation or abstention theorem for exact-forward surrogate
   gradients that freezes or eliminates the off-state extension, remains non-vacuous at event-support changes,
   and is not a restatement of a local Hessian bound;
2. an estimator whose correction cannot be rewritten as a known score-function control variate, auxiliary-path,
   coupled finite-difference, randomized-truncation, or mixed-order estimator, together with a preliminary
   bias--variance--cost theorem; or
3. a second licensed, pinned external hard-event system with the same intervention/gradient semantics as the
   first and a complete reproducibility fixture.

Until then, more literature labels, EcoMD architecture variants, seeds, or GPU throughput have zero decision
value for topic selection.
