# EcoMD action-counterfactual re-entry trigger audit

**Date:** 2026-09-04

**Mode:** outcome-blind theorem, primary-work, source-code and truth-asset audit. This is not
Discovery Cycle 17 and does not authorize candidate harvesting.

**Decision:** **NO QUALIFIED TRIGGER.** Adversarial intervention selection is now directly occupied;
the strongest self-computed action-weighting lead contains an exact paper-specification failure that
its released implementation already repairs; and two new executable-world benchmarks do not satisfy
the common-estimand or field-truth contracts. No outcome data, simulator run, implementation, EcoMD
change, SSH session or GPU job is authorized.

## 1. Frozen question

This audit tests three narrow claims against already recorded EcoMD blockers:

1. Does adversarial disagreement among simulators now identify which real market intervention should
   falsify them?
2. Does self-computed action-effect reweighting introduce a new mechanism class capable of escaping
   EcoMD's failed fixed-dynamics objective route?
3. Do newly released executable counterfactual benchmarks supply the missing second hard-event truth
   system and a common market bridge?

The relevant closed routes are
`cross_simulator_disagreement_intervention_certificate`,
`prospective_counterfactual_market_simulator_validity`,
`task_conditioned_market_simulator_adequacy`, and
`explicit_objective_coverage_path_a`. A development qualifies only if it removes one of their
recorded blockers for the same state, legal action, response and conditioning set. A useful method in
another domain is not, by itself, a re-entry trigger.

## 2. Adversarial intervention selection: direct collision, not missing theory

[Adversarial Causal Intervention Falsification
(ACIF)](https://arxiv.org/abs/2608.06427) formalizes exactly the proposed high-level move: candidate
structural generators are compared under an intervention-indexed critic, while an experimentalist
chooses the intervention on which surviving models disagree most. Its population objective reduces
to a worst-intervention IPM; for finite model and intervention classes it proves equivalence-class,
finite-sample and balanced-separation results.

This does not rescue the EcoMD route. The implementable prospective algorithm explicitly conducts
the selected intervention and collects a new batch from the real system. It can identify only the
equivalence class separated by the admissible intervention family. Its logarithmic elimination
result assumes a finite version space and balanced separation, while theory for the continuous
neural formulation is left as future work. Support, latent confounding, adaptive overfitting,
feasibility and ethics are stated limitations rather than solved contracts.

[Adversarial Causal Tuning
(ACT)](https://arxiv.org/abs/2506.02084) already supplies the neighboring time-series route: search
over temporal causal pipelines and discriminators to fit observational distributions and simulate
candidate interventions. Crucially, ACT states that its discriminator establishes distributional
fit rather than causal fit, and that causal fit can be validated only with experiments.

Therefore:

- selecting the maximum EcoMD--alternative-simulator disagreement is an acquisition rule, not truth;
- passive market tapes still do not reveal the selected action's post-intervention law;
- the market lacks a common complete state and legal action map shared by the candidate simulators;
- a continuous-neural ACIF extension would be a generic extension already named by the source, not a
  market-specific residual; and
- adding EcoMD as one generator does not create scientific novelty beyond ACIF or ACT.

This is a **direct-prior collision** and leaves the external-assigned-truth blocker unchanged.

## 3. CAER: exact boundary failure, followed by an already released repair

[Causal Action Effect Reweighting
(CAER)](https://arxiv.org/abs/2608.30897) computes, at each token,

\[
S_i(\theta)=\|f_\theta(x,a)_i-f_\theta(x,\varnothing)_i\|_2,
\qquad
\rho_i=\frac{S_i}{\max\{\bar S,\varepsilon\}},
\]

detaches `rho`, and weights the action-conditioned prediction loss. The paper correctly notes that
this is an action-conditional predictive contrast, not a `do`-calculus estimand, because the noisy
future input is downstream of the observed action. Its claimed first-order advantage is conditional
on positive covariance between the learned weight and token utility; the method does not prove that
its self-computed score has that covariance. The paper also derives an explicit covariance term by
which outcome-dependent weighting can move the population optimum.

### Proposition 1: the paper formula does not always preserve coefficient mass

For one sample, let `mu` be the mean over valid future tokens. Direct substitution gives

\[
\mu(\rho)=\frac{\mu(S)}{\max\{\mu(S),\varepsilon\}}.
\]

Thus `mu(rho)=1` only when `mu(S) >= epsilon`. If `0 <= mu(S) < epsilon`, the mean is strictly below
one, and if `S=0`, every weight is zero. This contradicts the unconditional unit-mean identity stated
beside the published formula.

### Proposition 2: zero action effect can be an absorbing action-blind manifold

Partition parameters as `theta=(phi, psi)`, where `psi` is used only by the action-injection path.
Assume:

1. the action path is initialized at `psi=0` and then
   \(f_{\phi,0}(x,a)=f_{\phi,0}(x,\varnothing)\);
2. on action-dropped samples, action injection is disabled, so the loss has zero derivative with
   respect to `psi`; and
3. the optimizer leaves `psi=0` unchanged when its gradient and regularizer derivative are zero.

At `psi=0`, `S_i=0` for every token. On a non-dropped sample, the detached paper weight is zero, so

\[
\nabla_\psi L_{\mathrm{focus}}
=\frac{1}{|\Omega|}\sum_i \rho_i\nabla_\psi \ell_i=0.
\]

On a dropped sample, the action path is inactive and its gradient with respect to `psi` is also zero.
Consequently the expected update of `psi` is zero and the action-blind manifold is absorbing. Shared
backbone training does not change this conclusion while the zero action injection keeps the two
queries equal. This is particularly relevant because the paper says new control pathways are
zero-initialized where possible.

The proposition is a boundary statement about the written objective, not a claim that all reported
runs entered the boundary.

### The released implementation closes the simple route

The Apache-2.0 [CAER repository](https://github.com/manifoldai-research/CAER.code/tree/1f46972f1b15a12e82626a0b4a0e0be385cafc99)
already implements

```text
rho = effect / clamp(mean_effect, eps)
rho = where(mean_effect > eps, rho, ones)
```

and tests that a zero effect map receives uniform weights. Its weighted loss also divides by the
realized coefficient sum per sample. Therefore the obvious repair supplies action-conditioned
gradient at the zero map and restores the budget convention. A paper whose centerpiece is merely
"add a uniform fallback" would rediscover the released implementation.

The wider contribution is also crowded. [TEMPO](https://papers.nips.cc/paper_files/paper/2023/hash/a995960dd0193654d6b18eca4ac5b936-Abstract-Conference.html)
learns task-aware world-model sample weights through a bilevel objective;
[Policy-Shaped Prediction](https://papers.nips.cc/paper_files/paper/2024/hash/17af43527227c5c96db0f8d4c6aadc4e-Abstract-Conference.html)
focuses world-model capacity with task-aware reconstruction, segmentation and adversarial learning;
and [World Action Verifier](https://arxiv.org/abs/2604.01985) uses forward--inverse verification plus
new environment interactions to find under-covered action consequences. These methods do not prove
CAER correct, but they remove generic task-aware weighting, sparse action relevance and
self-improving world-model verification as unoccupied claims.

The empirical record further argues for falsification rather than promotion. CAER improves its four
reported aggregate scores, but several nominally action-relevant component metrics decline, including
camera trajectory accuracy (`0.6211 -> 0.5474`) and RoboTwin trajectory accuracy
(`0.2781 -> 0.2610`). The paper reports eight H20 GPUs for every experiment. Its aggregate result is
not an equal-cost V100/A800 reproduction contract, and the current EcoMD architecture is not the
paper's action-conditioned video-model setting.

Most importantly, changing loss weights does not introduce a new EcoMD market mechanism. Experiment
107 already gave explicit long-rollout per-fact losses a valid terminal test (`p=0.81`), and its route
can reopen only for a new mechanism class, not another weight schedule. CAER therefore supplies a
reusable specification/code-conformance theorem and a watch item, but **not an EcoMD ICLR route**.

## 4. New executable worlds: useful truth assets without a common contract

[ScratchWorld](https://arxiv.org/abs/2606.31689) uses a pinned Scratch VM to produce replay-verified
state transitions, hidden variables, execution traces and paired counterfactual outcomes. Its
changed-field metric correctly avoids rewarding copied persistent state. This is a meaningful exact
counterfactual benchmark. However, the paper is under the arXiv non-exclusive licence, reports no
public repository, withholds identifier mappings and does not redistribute the underlying public
Scratch projects. Its interventions are program actions and state edits, not a parameterized
hard-event gradient shared with DoTime or EcoMD.

[DSGE-Gym](https://arxiv.org/abs/2607.03144) treats structural macroeconomic models as world models and
tests off-path tail and policy-regime generalization across eight benchmarked economies. It directly
occupies the broad claim that a structured economic simulator can manufacture counterfactual
coverage for a learned world model. The paper says an OSI-licensed artifact is supplied anonymously
to reviewers and de-anonymized at camera ready, but no public artifact URL is present at this audit
cutoff. Its one-step task supplies realized structural shocks as inputs and uses continuous DSGE
policy regimes; it is neither a second public hard-event gradient system nor real-market field
truth.

Adding these sources to the previously audited DoTime and epidemic systems still fails the joint
contract:

| Asset | Exact executable counterfactual | Public pinned reusable artifact | Same hard-event gradient estimand | Market field bridge |
|---|---:|---:|---:|---:|
| DoTime | yes | yes | reference system | no |
| Epidemic benchmark | partial | no complete licensed fixture | no | no |
| ScratchWorld | yes | no public complete fixture found | no | no |
| DSGE-Gym | yes inside structural models | reviewer-only at cutoff | no | no |

The result is a broader capability watchlist, not two contract-ready systems.

## 5. Machine decision

All three audited leads fail to remove a named route blocker. The append-only decisions are two
`not_trigger` entries and one `partial_capability` entry, with zero removed blockers and
`candidate_harvest_authorized: false` throughout.

The current machine decision authorizes only the already frozen Paper D held-out continuation. It
cannot be reused for this audit. Therefore:

- do not open Cycle 17 or a renamed EcoMD/world-model candidate;
- do not port CAER, train an action-conditioned EcoMD variant or reproduce its video experiments;
- do not download benchmark outcomes or build adapters;
- do not SSH to `100.113.230.38`, `100.80.236.112` or `100.123.220.57`; and
- allocate zero A800/V100 jobs to these leads.

## 6. Exact re-review conditions

Re-audit only after one of the following written developments exists:

1. **Market intervention truth:** an assigned, lawful market action with complete pre-state,
   propensity, interference grammar, untouched confirmation and a deterministic mapping shared by
   at least two simulator lineages.
2. **Nontrivial self-weighting result:** a theorem that survives a strictly positive action-present
   floor, proves when self-computed relevance is aligned or necessarily misaligned with target
   utility, and an estimator with an equal-cost advantage on two open executable systems. A zero-map
   fallback alone is explicitly insufficient.
3. **Common hard-event testbed:** a second licensed pinned system implementing the same intervention,
   replay/noise and gradient target as the first, plus a market-native mapping that preserves the
   estimand.

Even a qualified trigger would authorize only a bounded question screen. Implementation, outcomes
and accelerator use would still require a topic card and a new current machine decision.
