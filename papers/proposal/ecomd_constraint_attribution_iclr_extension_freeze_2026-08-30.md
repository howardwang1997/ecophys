# ICLR extension freeze: constraint-attribution audit with paired equivalence and rollout tests

Date frozen: 2026-08-30, before any extension outcome was generated or inspected.

Target: ICLR 2027 (abstract deadline 2026-09-18 AOE; paper deadline 2026-09-25 AOE).
This is an outcome-blind extension of the historical D0 audit. The D0 records and the exploratory
family-E sweep are prior knowledge and may motivate this design, but they are not confirmation
data. The extension is a `simulator_method` study on generated data. The PI's 2026-08-30 request
authorizes implementation and execution on the existing three-server pool.

## Question and claim ladder

The primary question is whether the OOD accuracy attributed to an exact linear invariant is instead
explained by the output parameterization that accompanies it. The claim ladder is deliberately
narrow:

1. **Algebraic claim:** orthogonal post-hoc projection can remove only the invariant-violating
   component of one-step error for the linear invariants studied here.
2. **Equivalence claim:** at a frozen cell, hard residual prediction is practically equivalent to
   unconstrained residual prediction in the conserving error channel.
3. **Attribution claim:** when ID error and compute overlap, the OOD difference between absolute and
   residual prediction is larger than the difference between residual prediction with and without
   hard enforcement.
4. **Temporal claim:** the one-step attribution pattern persists at frozen autoregressive horizons.
5. **Mechanism claim:** contraction strength predicts when absolute rather than residual output is
   preferable on an independently constructed operator.

Claims 2--5 are empirical and may be accepted, restricted by family, or rejected independently.
No nonlinear invariant, field-market transfer, universal constraint, or broad physics claim is in
scope.

## Evidence partitions

- **Historical discovery:** all existing seeds and records in
  `experiments/constraint_attribution_audit/`, including the adaptive family-E values. These data
  are excluded from extension confidence intervals and tests.
- **Pilot/tuning:** seeds `{100, 101, 102}`. They may be used only for runtime checks, failure
  diagnosis, and deterministic cell selection under the algorithm below. Pilot outcome metrics are
  labelled pilot and never pooled with confirmation.
- **Confirmation:** seeds `{1000, ..., 1019}`. These 20 paired seeds are untouched until code,
  configs, cell-selection rules, and pilot gates are frozen. All arms for a seed share exactly the
  same train, ID, and OOD examples. A failed run is retried with the identical configuration; it is
  never replaced by a different seed.

## Systems and OOD cases

The production confirmation set is:

- **A-adv, A-diff, A-burg:** 1D periodic spectral advection, diffusion, and viscous Burgers maps at
  resolution 64 with an MLP. OOD cases: low-frequency data-flat mode, data-rich mode, and shifted
  mean.
- **B-adv, B-diff, B-burg:** fully convolutional 1D U-Nets trained at resolution 128. The A cases
  are augmented with amplitude extrapolation and band-limited evaluation at resolution 256.
- **C-ad2d:** 2D periodic advection--diffusion at 32 by 32 with a 2D U-Net. OOD cases: flat mode,
  rich mode, and shifted mean.
- **M2-FIFO:** a corrected synthetic continuous double auction with explicit price-time FIFO
  queues, settlement to the resting order, and a nonzero fee account. Invariants are total
  inventory and participant cash plus fee-account cash. OOD cases are held-out order-flow
  imbalance and volatility shock. This replaces, but does not rewrite, the historical family-M
  implementation; old M results cannot support the market claim.
- **H-near/H-strong:** an independent mean-preserving spectral holdout. Every nonzero Fourier mode
  receives the same advection phase and attenuation `exp(-gamma * dt)`. Frozen values are
  `dt=0.1`, `gamma=0.5` (near identity) and `gamma=50` (strong contraction). The directional
  prediction, made before outcomes, is residual better for H-near and absolute better for H-strong.

All PDE truth maps are evaluated in float64 when generating targets and checked to preserve the
mean to numerical tolerance. Training tensors may be float32.

## Arms and training controls

Primary trained arms are `free`, `free_res`, `hard`, and `soft30`; `projection` is derived from the
trained `free` output and consumes no extra optimization. `soft30` is secondary and cannot rescue a
failed primary attribution test. Adam, batch size, training set, initialization seed, minibatch
order, and number of examples seen are paired across arms. Output heads have identical trainable
parameter counts within an architecture/capacity cell.

Pilot grids:

| family | capacity grid | epoch grid | learning-rate grid |
|---|---:|---:|---:|
| A and H | hidden `{32, 64, 128, 256}` | `{100, 200, 400, 800}` | `{0.001, 0.003, 0.01}` |
| B and C | base channels `{8, 16, 32}` | `{200, 400, 800}` | `{0.0003, 0.001, 0.003}` |
| M2 | hidden `{32, 64, 128, 256}` | `{100, 200, 400}` | `{0.001, 0.003, 0.01}` |

The pilot may be thinned after the first timing job, before metric inspection, to satisfy the
budget. Thinning order is: remove largest capacity, then longest epoch, while retaining at least
two capacities, two epoch counts, and two learning rates. The exact executed grid is recorded.

Compute proxy is `trainable_parameters * examples_seen`, where `examples_seen` is epochs times the
number of training examples. Wall-clock and peak GPU memory are recorded but are not matching
variables.

## Frozen selection and overlap rules

Cell selection uses pilot **ID RMSE only**; no OOD metric is read by the selector.

For each system and comparison (`free`--`free_res`, `free_res`--`hard`, and
`free`--`soft30`), enumerate pairs whose mean compute proxies differ by at most 5%. Among pairs
whose mean ID RMSE differs by at most 5% relative to their mean, choose the pair with: (i) smallest
relative ID gap, (ii) lowest mean ID RMSE, (iii) lowest mean compute, then (iv) lexicographic config
ID. Confirmation reruns those locked arm-specific configs on the 20 confirmation seeds.

If no pair passes both windows, lock the same-capacity/same-epoch/same-learning-rate cell having
the lowest average ID RMSE for a **fixed-compute** comparison. This branch is reported as
non-overlap; the tolerance is never widened and no matched-ID causal attribution claim is made.
Confirmation ID overlap is checked again on confirmation means. Failure at confirmation likewise
downgrades the result to fixed-compute.

## Metrics and temporal evaluation

For prediction error `e`, `P e` is the orthogonal invariant-violating component and `(I-P)e` the
conserving component. Per-example quantities are reduced within each seed first; seeds, not samples,
are the inferential units.

Primary metric: OOD conserving RMSE. Secondary metrics: total RMSE, absolute invariant drift, and
ID RMSE. At horizon one, projection/free conserving error must agree within relative `1e-5`
(absolute `1e-8` near zero), a stricter implementation check than the historical 1% rule.

For deterministic PDE systems, frozen autoregressive horizons are `H={1,4,16,64}`. Starting states
are generated once per confirmation seed and shared across arms. The learned predictor is composed
recursively; truth is advanced by the exact operator. We report conserving RMSE and accumulated
invariant drift at every horizon. M2 has no rollout claim because its learned observation omits the
full latent queue and is intentionally not Markov-complete.

## Estimation and decision rules

All standard deviations use `ddof=1`. Confidence intervals are seed-paired and computed by a
deterministic 50,000-draw bootstrap over the 20 seed differences (analysis RNG seed 20260830).

1. **Hard/free-res practical equivalence:** define the system/case-specific SESOI as 10% of the
   confirmation mean `free_res` conserving RMSE. Equivalence passes only if the 90% paired-bootstrap
   CI for `hard - free_res` lies wholly within `[-SESOI, +SESOI]`. A nonsignificant difference is
   not equivalence.
2. **Parameterization effect:** the 95% paired-bootstrap CI for `free - free_res` excludes zero.
   Direction is reported, not assumed.
3. **Attribution:** only for a pair that passes ID+compute overlap, the absolute mean
   parameterization effect must be at least twice the absolute mean hard-enforcement effect, while
   rule 1 passes. The ratio is descriptive when the denominator CI includes zero.
4. **Soft-penalty damage:** `soft30` is called dominated only when its 95% paired CI versus `free`
   is above zero in conserving error and its mean invariant drift is no smaller. The historical
   "laundering" label is not used in the main paper.
5. **Temporal persistence:** for each horizon, report rules 1--3 separately. A reversal or failed
   equivalence at any `H>1` restricts the broad result to the horizons that pass.
6. **Contraction holdout:** H-near passes its directional prediction when the 95% CI for
   `free - free_res` is above zero; H-strong passes when it is below zero. The mechanism claim
   requires both directions plus hard/free-res equivalence in both settings.

Family-level statements use no vote-counting shortcut: every included system/case is displayed,
and multiplicity is controlled by Holm correction within each claim family for sign tests. The
paired equivalence intervals remain unadjusted but are labelled family-wise exploratory if more
than the frozen primary OOD case is discussed. Primary OOD cases are `ood_flat` (A/B/H),
`ood_rich` (C), and `high_imbalance` (M2).

## Gates and stop rules

- Any truth-invariant, FIFO-priority, settlement, projection, or shared-dataset unit test failure
  blocks all runs that depend on it.
- A pilot must complete one seed and all primary arms, stay below 90% GPU memory, and produce finite
  metrics. Otherwise reduce batch size only; changing architecture or examples requires an amended
  freeze before outcome inspection.
- No matched pair means fixed-compute wording; it does not justify adaptive tolerances.
- Failed hard/free-res equivalence removes "no accuracy contribution" for that system and replaces
  it with the estimated effect and interval.
- A rollout reversal removes any unqualified simulator/trajectory claim.
- Failure of either contraction direction keeps the contraction explanation exploratory.
- Failure of M2 engine tests or confirmation equivalence removes the financial-domain claim.
- Any projection-control failure invalidates the affected metric pipeline and stops analysis.
- Missing provenance invalidates the run; it must be rerun, not patched after seeing results.

## Provenance and reproducibility contract

Each output contains the resolved Hydra config, seed list, command, git HEAD, dirty-worktree flag,
SHA-256 of every executed source/config file, hostname, platform, Python/NumPy/PyTorch/CUDA versions,
GPU model, parameter count, examples seen, runtime, and W&B URL (`null` when disabled). Because the
extension begins in a dirty research worktree, source hashes rather than a falsely clean git SHA are
the executable identity. Raw records are append-only and kept separate by stage.

## Budget and schedule

- Pilot hard cap: 25 V100-equivalent hours total.
- Confirmation hard cap: 120 V100-equivalent hours total; stop before exceeding it.
- The two 32 GB V100 workers are the production pool. The 8 GB RTX 2060S, when reachable, is used
  only for M2/lightweight jobs after a separate smoke timing; heterogeneous timings are reported
  separately.
- Target milestones: code/tests and pilots by 2026-09-02; locked cells by 2026-09-04; confirmation
  complete by 2026-09-10; figures and claim table by 2026-09-13; abstract freeze by 2026-09-16;
  paper freeze by 2026-09-23.

No experiment outside this document becomes confirmatory without a dated amendment written before
its outcome is inspected.

## Mathematical clarification, 2026-08-30 (before remote pilot)

The projection identity is an exact gate only at horizon one, where `free` and `projection` are
evaluated from the same input. At later autoregressive horizons their inputs differ because the
projected trajectory has already been altered; later conserving errors are scientifically reported
but cannot be an algebraic pipeline gate. This clarification corrects the scope of the theorem and
does not use any confirmation outcome.

## Compute-grid amendment, 2026-08-30 (before remote pilot)

The first remote pilot uses the predeclared budget-thinning branch based on historical D0 runtime
and local implementation-smoke timing, without consulting any remote pilot OOD metric. Executed
grids are A/H hidden `{32,64,128}`, B/C channels `{8,16,32}`, M2 hidden `{32,64,128}`; epochs are
`{100,200,400}` and the two lower learning rates in each family table are retained. Pilot rollout
evaluation is restricted to horizon one because selection reads ID RMSE only; all four frozen
horizons remain mandatory in confirmation. The exact job partition is
`configs/constraint_iclr/pilot_manifest.yaml`.
