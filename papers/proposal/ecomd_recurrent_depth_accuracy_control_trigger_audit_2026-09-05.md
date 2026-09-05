# EcoMD recurrent-depth accuracy-control trigger audit

**Date:** 2026-09-05  
**Archetype:** `simulator_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU status:** not authorized

## 1. Exact question and early truth contract

The proposed object is an autoregressive simulator trajectory

\[
 \widehat U_{1:H}^{(K)}(x),
\]

generated from the same declared pre-state (x), rollout horizon (H), and recurrent inference
depth (K). The possible EcoMD use is a learned surrogate or recurrent refinement layer whose
compute can be increased at deployment. The scientific question is not whether (K) changes
runtime. It is whether the observed nested outputs support a truthful statement of the form

> choose the least expensive (K) whose independently defined trajectory loss is below a declared
> tolerance with finite-sample error control.

Two explanations concern the same depth intervention and trajectory response:

- **H1 — progressive correction:** repeated application of the learned block refines an
  approximation to the true transition operator, so a depth-disagreement, residual, or calibrated
  stopping statistic can select the smallest accurate (K);
- **H0 — self-consistent wrong equilibrium:** the recurrence approaches a learned fixed point that
  need not equal the physical or market truth, while average accuracy curves conceal
  instance-specific reversals and deployment shift breaks calibration.

The cheapest discriminating result would be a prospectively fixed stopping policy evaluated against
independent trajectory truth, with selection-valid control over all inspected depths and rollout
horizons. A positive result would turn a compute knob into an operational accuracy controller. A
null result remains useful because it separates *dialability*--the ability to change (K)--from
*control*--an externally calibrated guarantee about error.

For a new ICLR simulator-method topic, the early truth contract would require all of the following:

1. an observable stopping statistic tied to true trajectory error by a theorem or a prospectively
   valid calibration procedure;
2. honest selection over depths, horizons, statistics, and thresholds without reusing the
   confirmation set;
3. explicit behavior when depth error is nonmonotone, recurrence randomness changes, or the rollout
   distribution shifts;
4. equal-budget comparisons against deep-equilibrium stopping, adaptive neural simulators, and
   generic risk-control selection;
5. two independent non-EcoMD truth systems, with a real-market bridge only for the exact same
   pre-state, action, observation, and loss semantics.

The audit finds that the negative distinction is real, but the obvious positive repair is already a
direct instantiation of established methods. The EcoMD market bridge also lacks external same-action
trajectory truth.

## 2. What RecurrSim establishes, and what it does not

[Majid, Sittoni, and Tudisco (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a3b73551d62d7758bdd99fc018b167a9-Abstract-Conference.html)
introduce RecurrSim, with encoder (E), a weight-tied recurrent block (R), decoder (D), random
training depth, and user-selected inference depth (K). The paper reports favorable average
accuracy--cost curves on Burgers, KdV, Kuramoto--Sivashinsky, compressible Navier--Stokes, active
matter, and ShapeNet-Car tasks.

This establishes a useful *compute dial*: one trained model can be evaluated at several depths. It
does not establish accuracy control in the numerical-analysis or statistical sense:

- no theorem makes trajectory error monotone in (K);
- no procedure maps a requested error tolerance to a per-instance depth;
- no upper error bound or calibrated abstention event is returned at inference;
- the reported curves aggregate examples and training seeds, so they do not imply that an
  individual trajectory improves when (K) increases;
- the latent fixed-point discussion concerns convergence of (R), not equality of its decoded
  fixed point to the true simulator solution.

The distinction is visible inside the paper: adaptive baselines can oscillate with depth, and the
extended discussion calls RecurrSim's observed curves smooth and monotone rather than proving a
model-class property. Thus the proposed research question is scientifically valid, but it is not an
unresolved theorem already supplied by RecurrSim.

## 3. Three exact negative results

### 3.1 Latent convergence can accompany increasing truth error

Let (0<\rho<1), let the decoder be the identity, and define the recurrent map

\[
 T(z)=\rho z+(1-\rho)c.
\]

It is a global contraction with unique fixed point (c). Choose a target (y\ne c) and initialize at
(z_0=y). Then

\[
 z_K=c+\rho^K(y-c),
 \qquad
 |z_K-y|=(1-\rho^K)|c-y|,
\]

so truth error increases monotonically from zero to (|c-y|), while the observable update residual

\[
 |z_{K+1}-z_K|=(1-\rho)\rho^K|c-y|
\]

converges to zero. Therefore contraction, fixed-point convergence, and a small successive-depth
disagreement do not certify accuracy. A residual-to-truth theorem must additionally establish that
the fixed point solves the independently defined target problem.

### 3.2 Mean monotonicity does not imply trajectory-level control

Consider two equally likely trajectories. Their losses at depths one and two are

\[
 (L_1^{(1)},L_1^{(2)})=(0,2),
 \qquad
 (L_2^{(1)},L_2^{(2)})=(4,0).
\]

Mean loss improves from (2) to (1), yet the first trajectory strictly worsens. Arbitrarily smooth
mean accuracy--cost curves can be constructed by mixing such pairs. Consequently, a population
curve is not an instance-level controller and cannot justify the phrase "increase (K) for a more
accurate critical simulation" without an additional conditional or selective guarantee.

### 3.3 Label-free nested outputs cannot yield a uniform truth certificate

Fix any stopping or certification rule that observes only (x), costs, and the complete nested
prediction sequence

\[
 \widehat U^{(1)}(x),\ldots,\widehat U^{(K_{\max})}(x).
\]

Construct two worlds with the same (x) and identical learned outputs but different true
trajectories: in one world the selected output is correct, and in the other it is farther than the
claimed tolerance. The rule has the same observable input and must return the same decision in both
worlds, so it cannot provide a distribution-free uniform error certificate. Calibration data, a
governing-equation residual equivalent to truth error, or another explicit link between outputs and
truth is necessary. Self-consistency alone is not such a link.

These counterexamples kill a direct "latent convergence implies accuracy control" thesis. They do
not constitute a sufficient new method paper: the needed calibrated repair is already covered by
the parent literature below.

## 4. Official supplemental-code audit

The official RecurrSim supplement was inspected outcome-blind as source code; no package was run.
The released main `recurrent-depth-pde` package contains several implementation facts that prevent
its current curves from serving as a clean verification fixture without repair:

1. **The sampled training depth is not the executed depth below the TBPTT floor.** In
   `models/wrappers/recurrent.py`, the no-gradient loop receives `k - recurrent_tbptt_steps`, for
   which Python `range` is empty when negative, and the gradient loop then always executes
   `recurrent_tbptt_steps`. The actual depth is therefore
   (max(K,B)), not Algorithm 1's sampled (K), when the TBPTT floor is (B).
2. **Fresh latent randomness enters every forward call.** `_sample_z` draws a new normal latent,
   including evaluation calls. The autoregressive generator consequently resamples latent noise at
   successive rollout steps, and separate (K)-curve evaluations do not share a declared latent
   tape. Differences across (K) are not a pure depth intervention unless randomness is coupled.
3. **The in-memory best checkpoint is a shallow copy.** `best_model_state =
   model.state_dict().copy()` copies the mapping but not its tensor storage. Subsequent optimizer
   updates can mutate the stored tensors, so the later "restore best model" step is not a reliable
   frozen best-validation checkpoint.
4. **The main sweep is validation-set evaluation.** The package constructs and repeatedly evaluates
   `valid_traj` for its trajectory and depth curves. No separate `test_traj` path appears in this
   entry point. This may be a development harness rather than the complete paper pipeline, but it
   cannot itself establish untouched confirmation.
5. **The trajectory metric remains marked for repair.** `evaluate_traj_loss` uses an unnormalized
   whole-trajectory (L_2) norm and `todo.md` contains `Fix traj_loss`. A TODO is not evidence that
   paper numbers are false; it is evidence that the released package needs a metric/provenance lock
   before reuse.

These are reproducibility and intervention-integrity findings, not empirical refutations of the
paper. Correcting them would improve a replication package but would not create an irreducible ICLR
contribution.

## 5. Direct-parent reduction

| Proposed component | Nearest primary parent | Collision or residual |
|---|---|---|
| More recurrent iterations increase expressivity in an implicit scientific model | [Liu et al., ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/1cced9d3dbc4dc83a96c6a5d7f6f4dc9-Abstract-Conference.html) | Gives a nonparametric test-time-scaling theory and scientific-computing case study. Expressivity is not accuracy, but the broad recurrent-depth explanation is occupied. |
| Tune an early-exit threshold while controlling degradation | [Jazbec et al., NeurIPS 2024](https://papers.neurips.cc/paper_files/paper/2024/hash/ea5a63f7ddb82e58623693fd1f4933f7-Abstract-Conference.html) | Applies CRC/UCB/LTT to early exits and arbitrary bounded quality losses. Its LTT fallback explicitly handles nonmonotone risks. A bounded trajectory loss can be substituted directly. |
| Select among depths, horizons, scores, and thresholds with finite-sample risk control | [Angelopoulos et al., Learn then Test](https://arxiv.org/abs/2110.01052) | Treats the candidate configuration as a hypothesis and controls selection error over a discrete family without model refitting. The tuple ((K,H,s,\tau)) is just a hyperparameter. |
| Minimize compute among risk-valid stopping policies | [Wang et al., ICML 2026](https://arxiv.org/abs/2602.03814) | Conformal Thinking searches signal--threshold pairs, constrains premature-stop risk, and uses an efficiency loss to select the cheapest feasible policy. Changing tokens to recurrent simulator steps is a domain substitution. |
| Data-adaptive risk control by instance difficulty | [Blot et al., AISTATS 2025](https://proceedings.mlr.press/v258/blot25a.html) | Supplies approximate conditional risk control with learned conditioning classes, occupying a generic "hard trajectories get more depth" calibration claim. |
| Adaptively test configurations while preserving selection validity | [Zecchin, Park, and Simeone, ICML 2025](https://arxiv.org/abs/2409.15844) | Adaptive LTT uses e-processes for sequential, data-dependent hyperparameter testing. Inspecting candidate depths adaptively is not an unoccupied extension. |
| Use two temporal resolutions as a label-free simulator trust signal | [Lakshmanan and Chopra (2026)](https://arxiv.org/abs/2605.28317) | Hybrid Neural World Models already use semigroup step-doubling to gate solver fallback across PDE and collision systems, and explicitly report a below-chance far-OOD failure. It proposes conformal magnitude calibration as future work. |
| Conformal sets for function-valued neural-operator outputs and autoregressive diagnostics | [Millard, Lindemann, and Baheri, ICLR 2026](https://arxiv.org/abs/2509.04623) | Provides discretize--then--lift function-space coverage and internal-agreement/conformal-ensemble diagnostics for autoregressive degradation. |
| Finite-sample neural-operator bands over a continuum or grid | [Stent and Boullé (2026)](https://arxiv.org/abs/2608.28515) | This genuine post-closure theorem calibrates a generic measurable residual field and controls the fraction of the evaluation domain covered. It treats a fixed predictor and does not solve adaptive depth, but it occupies the missing fixed-model function-space guarantee. |
| Computable error bounds from physical residuals | [Qiu, Dahmen, and Chen (2025/2026)](https://arxiv.org/abs/2512.21319) | Constructs a variationally correct operator whose residual is provably equivalent to solution error. Where such a governing-equation contract exists, a posteriori accuracy control is stronger than output self-consistency. |

The straightforward proposed algorithm is therefore already implied by existing machinery:

1. define each complete stopping policy, including its inspected depths and statistic, before
   confirmation;
2. use a bounded path loss, for example
   (L=\min\{1,\max_{h\le H}\ell_h/c\}), so horizon-uniform failure is a single trajectory-level
   event;
3. run LTT or an appropriate risk upper bound over the finite policy family;
4. among the risk-valid policies, choose the least expensive using a separate efficiency criterion.

Taking a maximum over time supplies pathwise simultaneity; including all choices inside the tested
policy supplies selection validity. Neither operation requires new simulator mathematics. Adding a
step-doubling statistic and applying this pipeline would be a useful implementation, but it is a
composition of Hybrid Neural World Models with established risk control.

## 6. Why a distribution-shift variant does not rescue the topic

Conformal and risk-control guarantees require a declared relationship between calibration and test
examples. The output-only impossibility above rules out a universal, label-free repair under
arbitrary shift. A total-variation degradation bound is mathematically valid only to the extent that
the shift distance is known or defensibly bounded; it does not make that distance observable from a
single unlabeled rollout.

Consequently, "detect market regime shift from recurrent disagreement and retain coverage" is not a
free residual. It would require a new assumption and theorem connecting an observable market-native
state change to a sharp error bound, plus a lower bound showing why generic weighted conformal,
online risk control, or abstention cannot attain the same result. No such obstruction or result was
identified here.

## 7. EcoMD bridge audit

EcoMD does not currently supply the truth contract needed to turn this method composition into
market science:

- treating an EcoMD trajectory as ground truth would evaluate compression of EcoMD, not the
  validity of EcoMD's market counterfactuals;
- a learned recurrence and its source EcoMD rollouts share the same mechanism omissions, so low
  surrogate error is not external market validity;
- stochastic interaction tapes, agent states, and hard-event timing must be coupled across (K)
  before depth is an isolated intervention;
- historical markets expose only one realized path, not the same-pre-state counterfactual trajectory
  required to label a depth-selected policy;
- no second independently governed system and untouched market intervention currently expose the
  same state, action, rollout loss, and truth.

A narrow engineering project could compress EcoMD with a recurrent surrogate, but it would inherit
the direct adaptive-compute and neural-operator parents and would not answer a market-native
scientific question. It is not authorized under the current discovery state.

## 8. Gate decision

| Gate | Result |
|---|---|
| Genuine post-closure source | Pass: Stent--Boullé appeared on 2026-08-28 and gives a new rigorous neural-operator coverage result |
| Same-observable rival explanations | Pass: progressive correction and wrong-equilibrium convergence make opposite claims about depth and truth error |
| Exact killer tests | Fail for H1 as stated: a contraction can have vanishing residual and increasing truth error; mean monotonicity can hide trajectory reversals |
| Irreducible adaptive-depth risk-control method | Fail: early-exit CRC/UCB/LTT and Conformal Thinking already select compute policies under bounded risk |
| Irreducible trajectory/function-space guarantee | Fail: function-space conformal and neural-operator coverage parents occupy the fixed-predictor result; path-max loss is elementary |
| Irreducible label-free discrepancy signal | Fail: semigroup step-doubling is already implemented and evaluated by Hybrid Neural World Models |
| Official implementation matches a clean depth intervention | Fail: TBPTT floors the realized depth, evaluation resamples latent state, and the released checkpoint/split path is not a frozen confirmation fixture |
| Two independent same-estimand truth systems | Fail |
| Market-native external truth bridge | Fail |
| Recorded blocker removed | Fail: neither the market validity nor generic simulator-audit blocker is removed |
| Prospective full-T0 forecast | Not applicable: this was a bounded trigger audit, and the literature neighborhood was opened before any exact F3 subject freeze |

**Decision:** `not_trigger`, with `removed_blockers: []` and
`candidate_harvest_authorized: false`. The distinction between a compute dial and accuracy control,
the three counterexamples, and the source-code checks are reusable. They do not authorize a topic
card, implementation, outcome access, simulation, SSH, or GPU use.

## 9. Exact re-entry boundary

Do not reopen this family for another conformal wrapper, early-exit threshold, uncertainty head,
step-doubling score, or recurrent-depth benchmark. A future trigger must first supply at least one of
the following for a prospectively frozen child:

1. a simulator-specific theorem in which an inference-observable statistic gives a sharp true-error
   or abstention guarantee under hard events and dependent rollouts, with assumptions that can be
   checked without the unknown trajectory and a matching impossibility/lower bound outside those
   assumptions;
2. a selection-valid procedure with a risk or cost guarantee that cannot be represented as LTT,
   CRC/UCB, adaptive LTT, or a path-level bounded loss over a fixed policy family;
3. a lawful market intervention asset with complete pre-state, externally defined trajectory truth,
   repeated same-action assignments, and untouched independent replication, so that the research
   target is market counterfactual validity rather than surrogate fidelity.

A corrected RecurrSim release, a new PDE benchmark, or smoother average (K)-curves is not such a
trigger. If a qualifying theorem or truth asset appears, freeze the exact subject and full-T0
forecast before opening its full fifteen-work F3 neighborhood.

## 10. Operational disposition

- No historical or simulated outcome was opened.
- No code was modified or executed from the external supplement.
- No EcoMD model or data pipeline was run.
- No SSH connection was made.
- The A800 and both V100 workers remain idle for EcoMD discovery.
