---
name: project_workshop_experiment_addenda_v100_2026-08-07
description: Ranked workshop experiment addenda and conservative V100 feasibility envelope
metadata:
  type: project
---

## Experiment priority

The frozen Paper E E0--E3 package remains the P0 evidence chain. Do not replace it with new exploratory
experiments. Add one low-cost reviewer control to Paper E: compare the frozen energy-distance gate with
fixed burn-in and standard stationarity baselines (at minimum no discard, fixed W=500/1000, and
ADF/KPSS on returns and absolute returns) under exactly the same calibration/held-out split and
fixed-length scoring. This addresses whether the proposed gate adds anything beyond discarding an
arbitrary prefix or using an off-the-shelf test. It is CPU work and cannot be tuned on held-out results.

If Paper S remains alive after S0 and its planned neural-SDE S1 stress test, the highest-value additional
control is an L2/norm-matched incoherent latent kick. Match the selected-agent fraction, coordinate,
and total displacement norm of `state_kick`, but center the perturbation with balanced or frozen random
signs. The current `state_kick` gives every selected agent the same positive displacement, while the
temperature spike is not energy/norm matched. This new arm therefore distinguishes coherent direction
from perturbation magnitude more directly. Pre-register the construction and primary contrast before
running it; do not search variants after seeing results. Prefer this control over trained-Levy scoring.

Do not add new assets, more dose cells, a large self-averaging sweep, new paid data, or a new architecture
before the workshop deadline. A casual changed-dt rollout is also not a valid convergence study because
the checkpoint was trained at dt=0.01; run such a test only with a defensible continuous-time/physical-time
mapping.

## V100 feasibility

- Existing exp126 production training measured 14.19 GiB allocated and 14.85 GiB reserved at N=10k,
  fp32, `chunk_steps=24`.
- V100 32 GB is memory-feasible for forward rollouts and likely for exact-protocol retraining, subject to
  one full T=8000 inference probe and one exact 10-iteration training probe. The PyTorch/CUDA build must
  expose `sm_70`.
- V100 16 GB should be used only for inference after a peak-memory probe. It is not an acceptable
  production retraining device: the measured reserved peak leaves about 1.15 GiB and is too sensitive to
  allocator, library, and fragmentation differences. Do not change `chunk_steps` and call it the same
  training protocol.
- V100 has no native bf16 path, but current workshop production configs use fp32, so bf16 support is not
  a blocker.
- Run H20, A100, and V100 as separate single-GPU worker pools rather than one heterogeneous `torchrun`
  job. Preserve explicit seeds: current `run_large` derives them from rank, so changing GPU count without
  a manifest changes the experiment.

Until a measured V100 rollout exists, schedule with a conservative 3--5x slowdown relative to the
repository's 168 s H20 T=8000 rollout; this is a planning envelope, not a hardware benchmark. Under that
envelope, Paper E E1+E3 (320 rollouts) costs about 45--75 V100 GPU-hours, and Paper S S1 (480 rollouts)
about 67--112 V100 GPU-hours. CPU-only E2 and the gate-baseline comparison should not consume V100 time.
