---
name: project_workshop_2xv100_execution_2026-08-07
description: Authoritative workshop completion plan, two-node hardware audit, and checkpoint blocker
metadata:
  type: project
---

## Authoritative execution plan

`papers/proposal/workshop_completion_2xv100_plan_2026-08-07.md` is the current execution plan. Paper E
for Sim2Science is P0; Paper S for STODY remains conditional and must pass a new norm-matched causal
diagnostic plus estimator integrity. The user confirmed V100 hardware, full retraining because H20 is
unreachable, and that Paris/Sydney are both feasible; venue choice is by scientific fit. Formal exp127
execution is active.

## Hardware audit

The two user-provided 32 GB nodes are reachable with the existing root SSH key. Both report
Tesla PG503-216, compute capability 7.0, driver 550.127.05, CUDA 12.4, 32768 MiB VRAM, and 31 GiB host
RAM. They must be treated as Volta/V100 32 GB rather than Blackwell B100. One has about 180 GiB free on
`/data`, the other about 98 GiB. Both are now provisioned under `/data/ecophys_workshop/` with Python
3.11, PyTorch 2.3.1+cu121 including `sm_70`, the required source/config snapshot, and hash-validated
data. Addresses remain only in gitignored `scripts/machines.local.json`; no long-lived R2 credential was
copied.

## Checkpoint blocker

The Mac has no exp108/113/114/126 checkpoints. A read-only scan of 7,856 objects under the R2
`checkpoints/` prefix found no exp108/113/114 keys; standard experiment checkpoint directories in that
archive stop at exp096. Common alternate prefixes were also empty. Exp125/126 locally retain windowed
reports but zero production trajectory NPZ files, so new stationarity scoring and recovery audits cannot
be reconstructed from the checkout.

Preferred route: recover the exact exp108 `sv_d3_both` seeds 0/1/2, exp113 SPX concave/baseline, and
exp114 NDX/Gold/EURUSD/BTC concave plus BTC baseline checkpoints from H20/GPFS and hash them. Fallback:
retrain under the original configs/data and treat every result as a new artifact; old exp126 summaries
cannot be silently paired with retrained checkpoints.

## Scientific correction

Exp108 `sv_d3_both` is not an independent neural-SDE generator family. Its YAML instantiates the same
EcoMDSimulator with stochastic_mlp/SPS agent dynamics and adds stochastic-volatility components. It is
only a within-EcoMD architectural variant. It can support Paper E robustness but cannot by itself pass
Paper S's cross-model/generalizability gate. Paper S's feasible rescue is a pre-registered
`balanced_state_kick`: same selected fraction, coordinate, absolute per-agent displacement, and total L2
norm as coherent state_kick, but frozen balanced signs and zero mean displacement. Standalone value
requires stable coherent-vs-balanced separation across checkpoints plus estimator integrity; otherwise
merge a single shock positive control into Paper E.

## Execution status and measured performance

- Exp127 implementation commit: `2734ee9351293bd72c1afe73bd5af2ef7c0a1e7e`.
- PyTorch 2.3 AMP compatibility commit: `22a6e41628d7cca7688ecdf5513e5a5bb014e462`.
- The original remote probe failed before iteration 0 on missing `torch.amp.custom_fwd`; the compatibility
  shim fixed it without changing scientific configs/seeds. Failed logs are retained.
- Exact ten-iteration N=10k/FP32/chunk24 probes passed: 480.3/478.7 s, 14.14 GiB peak allocated,
  15.03 GiB reserved, identical checkpoint SHA-256.
- Identical-seed 8,000-return probes passed: 388.3/383.9 s, 3.81 GiB reserved, bitwise-identical NPZ and
  identical canonical JSON after removing wall time. V100 32GB needs no scientific downgrade.
- Production retraining started 2026-08-07 05:21 NZST as persistent systemd services
  `ecophys-exp127-train-a/b`, five frozen 200-iteration jobs per node.
- An unattended controller now polls both services, retrieves and validates every checkpoint, launches
  calibration shards on both nodes, freezes and hashes all gate fits, and only then releases held-out
  shards. It writes controller records under ignored `outputs/exp127_remote_artifacts/control/` and
  cannot refit from held-out data. At 07:38 NZST each node completed its first checkpoint (SPX
  concave/base in 8,205.4/8,160.4 s, 14.14 GiB allocated and 15.03 GiB reserved) and immediately
  started the second frozen job; no rollout split had been opened.

## Analytic result and paper state

The clean formal analytic run generated seven conditions x 1,000 trajectories x 8,000 returns. The
energy gate passed stationary specificity (1/62 false positives; Wilson95 upper 8.59%) but detected only
28/124 cold pseudo-checkpoints (22.58%), mainly GARCH cold-high. It is a conservative, low-power audit,
not a universal transient detector. ADF/KPSS had 50% stationary false positives. Energy improved pooled
median Hill error over fixed W=500/1000 but worsened the mean; both must be reported.

A post-primary literature audit added MSER-5 under a timestamped exploratory amendment that cannot
change the registered tier. On the same pseudo-checkpoints it selected nonzero warm-up in 16/62
stationary cases (25.81%) and 76/124 cold starts (61.29%); pooled cold Hill error was 0.0491 by median
and 0.0847 by mean. The defensible distinction is therefore high specificity/conservative selection,
not uniform score-error superiority. The frozen 217-row record has SHA-256
`4940621cb88518438d2e4340a4f8af29257bd310deb39e5a4aa21eec0c74c566` and is reported in commit
`d66156f898259a4d9acdb61838b648015e8db5b9`.

The official Sim2Science 2026 double-blind paper now lives at
`papers/paper_a_methods/workshops/sim2science/`. It uses the official style/checklist, has two generated
vector figures, compiles with the isolated `ecophys-tex` Conda environment, and keeps the body within
the five-page limit with references beginning on page 5. The analytic figure now exposes the ED/MSER-5
sensitivity-specificity tradeoff. The deterministic anonymous draft artifact passes all 61 bundled
tests and its identity scan; it remains intentionally incomplete until learned gate fits, results, and
the learned figure exist. Learned-result macros are synchronized from one frozen JSON source with
tests; the simulator equation and empirical-target language have been checked against implementation.
Those integration changes are in `13dbd7c78`, and the verified volatility-based tail citation is in
`3cd2e7672`. The manuscript now says ``pre-specified/frozen'' rather than ``pre-registered'' because
the pre-result protocol had an internal Git freeze but no independent public registration; this
anti-overclaim correction is in `d274047bc`. Learned-result macros/figure remain placeholders until
E1/E3 freeze. The main text also reports the previously omitted intermediate nominal-GARCH outcome
(4/31 nonzero warm-up selections), committed as `aedc4f5df`; a real-size figure layout check still
places references on page 5. The exact trajectory/late-pair null bootstrap is now stated in the main
method rather than left implicit in code (`5fd19b0d3`). The conclusion now calls the transient an
internal simulator dynamical property, not a ``physical property,'' to avoid any possible market-
physics reading (`c6bdd308d`).

Before either rollout split existed, a 06:57 NZST amendment froze a secondary dependence-aware check
for the shared rollout seeds: resample checkpoints plus one common seed-index vector, and report
market-balanced leave-one-out effects. The original interval/tier is unchanged; disagreement cannot
be hidden or used to upgrade the claim. Code, tests, paper disclosure, and the final-artifact
requirement are committed as `49f95327a`; `40fc550e8` records the 06:57 declaration, 07:02 commit,
and zero-rollout checks on both sides of that commit. Release instructions/checklist enforce the new
derived result in `aecf88379`. The paper's synchronization tool now owns seven macros, including the
common-seed interval and leave-one-market-out range, in `2c06de3c1`; deterministic artifact and
59-test packaged QA still pass. The paper now explicitly says the learned intervals condition on one
frozen calibration split and omit W-star selection uncertainty (`4a2304bb2`), and that the finite
checkpoint suite was chosen from prior model-development runs (`f27e028f6`).

A second pre-held-out amendment at 07:12 NZST froze Hill `k_frac={0.025,0.05,0.10}` sensitivity on
the same fixed windows and gates. Five percent remains the only primary value; the others cannot
upgrade the tier, and sign/interval disagreement must be reported. The implementation recomputes raw
held-out trajectories, asserts exact agreement at 5%, applies common-seed/market diagnostics at each
fraction, and synchronizes the positive-interval count into the paper. It is committed as
`33975c7c6`; `ff8d05ba6` records the 07:19 commit and zero-rollout audit. Deterministic artifact QA now
passes 61 bundled tests. The manuscript also discloses that most asset/configuration cells have one
training seed. The abstract/conclusion now say the audit tests consistency with a frozen late-time
reference and does not certify stationarity (`0ad94281b`).

## Final exp127 outcome and release candidate (2026-08-08)

Exp127 completed all ten retrainings and 320 rollout trajectories. The gate was frozen at
`2026-08-07T16:42:36.931108+00:00` with zero held-out trajectories; the first held-out trajectory was
written 6 minutes 36 seconds later. All calibration and held-out shards passed local hash validation.
Raw gate/result hashes are `8c3ac123c999dc1bffee03b7bc31083312ffc13f60294879ff7aaa693e02f074`
and `2c3d3c5e266b7327482867146edccf3799cd681d88ce1c334e9fd6622aae1b8e`.

Paper E freezes at **E-B**. All seven E1 checkpoints were scorable and the aggregate paired Hill effect
was +6.1192 with hierarchical 95% CI [+5.4287,+6.9879], but gold failed held-out gate transfer, so
confirmation was 6/7. Common-seed CI [+5.4437,+7.0558], all-positive market leave-one-out range
[+5.8417,+6.6672], and positive intervals at all three Hill fractions make the direction robust.
E3 does not pass the frozen broad-transfer rule: variants 0/1 are positive, variant 0 fails transfer,
and variant 2 has no W-star. Baseline advantage remains mixed. The defensible paper is a strong
simulator-specific discrepancy/audit case study, not a universal method or market-physics claim.

The final PDF is `output/pdf/sim2science_ecomd_2026_submission.pdf` (SHA-256
`518cc620c04e2dbb3e9df2d88696f3f105d009656351c61cc4dca5a6827df8b4`): nine total pages with the
five-page body limit met, automated checks passed, fonts embedded, and all pages visually inspected.
The complete deterministic anonymous artifact is
`output/artifacts/sim2science_ecomd_2026_artifact.zip` (SHA-256
`1b17784acf7fee16885331f1e13d2991fce4466e73d3b5540f097e7fc4f6c272`); two builds matched, archive
integrity/identity scans passed, and 61/61 packaged tests passed. Remaining tasks are user-owned
OpenReview metadata, reviewer identity, artifact hosting, upload, and post-download verification.
The frozen review-source commit is `c5c33a482`.
