# Experiment 127 — Workshop claim gates

**Frozen:** 2026-08-07 NZST, before implementation outputs or new rollouts were inspected.

**Primary paper:** Sim2Science Paper E, stationarity-aware fixed-length evaluation.

**Conditional paper:** STODY Paper S, retained only after Paper E is complete and the causal diagnostic
gate passes.

## 1. Provenance reset

H20 is no longer accessible and the exp108/113/114 checkpoints are absent from the current local and R2
checkpoint inventories. All learned checkpoints used by this experiment will therefore be retrained from
the committed original configs and original data snapshots on the two V100 32GB nodes. They are new
artifacts. No old exp123--126 aggregate is treated as paired output from these retrained checkpoints.

Required learned checkpoints:

| ID | Original config | Role |
|---|---|---|
| E1-spx-concave | `experiments/113_gabaix_solve/config_concave_d050_seed0.yaml` | learned case |
| E1-spx-base | `experiments/113_gabaix_solve/config_baseline_seed0.yaml` | family contrast |
| E1-ndx-concave | `experiments/114_concave_confirm/config_ndx_concave_d050_seed0.yaml` | learned case |
| E1-gold-concave | `experiments/114_concave_confirm/config_gold_concave_d050_seed0.yaml` | learned case |
| E1-eurusd-concave | `experiments/114_concave_confirm/config_eurusd_concave_d050_seed0.yaml` | learned case |
| E1-btc-concave | `experiments/114_concave_confirm/config_btcusdt_concave_d050_seed0.yaml` | learned case |
| E1-btc-base | `experiments/114_concave_confirm/config_btcusdt_baseline_seed0.yaml` | family contrast |
| E3-sv-0 | `experiments/108_neural_sde_scout/config_sv_d3_both_seed0.yaml` | within-family variant |
| E3-sv-1 | `experiments/108_neural_sde_scout/config_sv_d3_both_seed1.yaml` | within-family variant |
| E3-sv-2 | `experiments/108_neural_sde_scout/config_sv_d3_both_seed2.yaml` | within-family variant |

Every checkpoint record includes original-config SHA256, execution-config SHA256, data snapshot hash,
training seed, execution git SHA, GPU UUID, software versions, checkpoint SHA256, and whether the config
was changed. A changed scientific hyperparameter is a deviation, not an equivalent reproduction.

## 2. Paper E protocol

### 2.1 Rollouts and split

Each learned checkpoint produces 32 no-shock rollouts with `T=8000` usable returns. Because the current
EcoMD inference writer removes its initialization return, the launcher requests 8001 simulator steps
and asserts exactly 8000 saved returns. The explicit seeds in
`SEEDS.json` are paired across checkpoints. Sixteen are calibration trajectories and sixteen are
held-out trajectories. The machine shards each contain eight calibration and eight held-out seeds so
hardware is not confounded with the split.

No held-out trajectory is inspected until the checkpoint's scale, late-vs-late tolerance, and W-star
have been serialized from calibration data and SHA256-frozen.

### 2.2 Fixed-length scoring

Every comparison scores exactly `L=4000` usable returns from `[W,W+L)`. The sensitivity grid is
`W={0,50,100,200,500,1000,1500,2000,3000}`. A method may report no valid W; it may not shorten L or
change T to force a result.

### 2.3 Energy-distance gate

For each checkpoint:

1. Convert returns to delay rows `x_t=(r_t, |r_t|, |r_{t+1}|)`.
2. On calibration trajectories only, robust-standardize each dimension by the pooled median and MAD of
   `[6000,8000)`; apply a pre-specified numerical floor to zero MAD.
3. Use non-overlapping 500-step blocks. Gate starts are `{0,500,1000,1500,2000,2500,3000,3500,4000}`;
   late-reference blocks start at `{6000,6500,7000,7500}`.
4. For trajectory i and candidate block w, define `D_i(w)` as the median multivariate energy distance
   from that block to the four same-trajectory late blocks.
5. Form the late-stationary null from all six pairwise distances among the four late blocks. Resample
   trajectories, not individual delay rows, to obtain the checkpoint-level tolerance for the median
   distance. The tolerance quantile and bootstrap replicate count are frozen in `PREREG.md`.
6. W-star is the earliest start not exceeding 3000 for which the checkpoint-level median distance at
   w, w+500, and w+1000 is within tolerance. If none exists, label the checkpoint “not verifiably
   stationary within the evaluation horizon.”
7. Freeze W-star from calibration. Apply it without modification to held-out trajectories.

### 2.4 Primary and secondary outcomes

Primary learned-model outcome: the held-out paired difference
`Hill([W-star,W-star+4000)) - Hill([0,4000))`, summarized at checkpoint level with a hierarchical
bootstrap that resamples checkpoints and trajectories in their correct layers.

Secondary outcomes:

- all 11 stylized-fact sensitivity curves on the fixed-length W grid;
- target distance and pass count before/after the frozen gate;
- checkpoint-specific W-star and no-W-star rate;
- rank changes, reported descriptively and never used as a success criterion;
- within-EcoMD replication on `sv_d3_both` seeds 0/1/2.

## 3. Analytic controls and method baselines

Use one frozen fitted-parameter record from exp080 for GARCH-t and one for AR(1)-SV; do not refit or
select parameters using exp127 outputs.

Conditions:

- GARCH-t: long-burn, nominal unconditional-variance start, cold-low variance 0.1x, cold-high 10x;
- AR(1)-SV: stationary log-variance start, cold-low variance 0.1x, cold-high 10x.

For GARCH-t the multiplier scales the unconditional initial variance. For AR(1)-SV, the unshifted
initial log variance is sampled from its analytic stationary Gaussian law and the multiplier is added
as `log(multiplier)`; the initial return is sampled conditionally, with the frozen AR(1) variance
correction. These definitions are fixed before analytic trajectories are generated.

Each condition has 1000 `T=8000` CPU trajectories. The first 992 are divided deterministically into 31
pseudo-checkpoints of 32 trajectories (16 calibration, 16 held-out); eight are reserved for file-format
sanity checks. This makes the false-positive/detection unit a pseudo-checkpoint, not a time step.

Compare at the same calibration split and nominal false-positive budget:

- no discard (`W=0`);
- fixed `W=500`;
- fixed `W=1000`;
- ADF/KPSS block gate on returns and absolute returns;
- the frozen energy-distance gate.

Primary analytic outcomes are false-positive rate on long-burn/stationary starts, detection rate on
cold starts, detection delay, and fixed-length Hill-score error relative to the matched pseudo-checkpoint's
long-burn/stationary `[0,4000)` reference. A selected `W>0` or unresolved no-W outcome counts as transient
detection; the unresolved rate is also reported separately. Under stationary starts this same indicator
is the unnecessary-discard/false-positive event, including for the fixed-W protocols.

## 4. Conditional Paper S rescue

This block is not queued until Paper E is frozen at E-A or E-B.

Add `balanced_state_kick`: select the same agent fraction and coordinate as `state_kick`; give every
selected agent the same absolute displacement; assign a frozen equal number of positive and negative
signs. Thus total L2 displacement matches the coherent kick while mean displacement is zero.

Use the separate conditional seeds in `SEEDS.json`. On the SPX concave checkpoint and `sv_d3_both`
seeds 0/1/2, compare control, coherent state kick, balanced state kick, temperature spike, and temporary
reduced friction. The primary contrast is the coherent-minus-balanced post-shock Hill deficit. Recovery
must agree in direction across first-passage, exponential-fit, and integrated-relaxation estimators for
window sizes 200, 500, and 1000.

Paper S survives only if the coherent-minus-balanced direction is stable across checkpoints and the
recovery statement is estimator-robust. Otherwise delete the coherence mechanism and merge at most one
intentional-nonstationarity positive control into Paper E.

## 5. Compute and artifact flow

The two V100 nodes run independent one-GPU workers. They never form a heterogeneous or multi-node
`torchrun` job. Formal execution begins only after both pass:

- PyTorch architecture list contains `sm_70`;
- one identical full `T=8000` inference rollout;
- if retraining, one exact N=10000, fp32, `chunk_steps=24`, 10-iteration training probe;
- finite outputs, expected schema/counts, peak-memory capture, and result return to Mac.

Code, environments, checkpoints, and temporary results live under `/data/ecophys_workshop/`. Long-lived
R2 credentials are not copied to the nodes. Each completed shard is checksummed and returned before the
next disposable shard is removed.
