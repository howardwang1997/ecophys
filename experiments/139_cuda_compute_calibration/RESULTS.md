# Experiment 139 results — CUDA compute calibration

**Run date:** 2026-08-19
**Frozen source commit:** `1046a8d01`
**Decision:** overall FAIL; `N=500` supported, `N>=2,000` numerically unsupported under the frozen configuration

## Result

Both V100 nodes completed all eight declared cells; the RTX 2060 completed its four cells after switching from
an incompatible `ecophys` PyTorch build to the already-installed `ecophys-g0-regression` Conda environment.
Every `N=500` cell passed all mechanics checks (6/6 across three GPUs). No `N>=2,000` cell passed (0/14).

| N | GPU cells | Full PASS | Median cell wall time | Maximum reserved HBM |
|---:|---:|---:|---:|---:|
| 500 | 6 | 6 | 7.01 s | 0.49 GiB |
| 2,000 | 6 | 0 | 6.33 s | 2.66 GiB |
| 5,000 | 4 | 0 | 7.96 s | 6.62 GiB |
| 10,000 | 4 | 0 | 8.28 s | 12.81 GiB |

The two V100s reproduced the same qualitative and seed-specific failure pattern. At `N=2,000`, seed 0 retained
exact chunk/resume parity but the 1,024-step rollout became non-finite and train/inference differences exceeded
the frozen `1e-6` tolerance. Seed 1 developed NaNs in the parity paths. Both seeds at `N=5,000` and `N=10,000`
developed NaNs. The 2060 showed the same pattern at `N=2,000`.

## Interpretation

This is not a capacity failure: even `N=10,000` used only 12.81 GiB on a 32 GiB V100. It is a numerical/
dynamical stability failure of the random-weight state-complete configuration at `dt=0.005`, amplified by the
longer 1,024-step probe. Consequently, future compute estimates cannot assume that more HBM permits a larger
valid EcoMD system.

Production scientific work remains capped at the already supported `N=500` until a separately pre-registered
stability diagnosis varies integration step, initialization/weight scale and stabilizing parameterization.
Runtime numbers from failed non-finite cells must not be used as throughput estimates. This result upgrades no
NCS scientific gate, but it prevents wasting the V100s on invalid large-`N` trajectories.

## Environment finding

The RTX 2060's `ecophys` environment contains a PyTorch build whose CUDA requirement exceeds the installed
driver. The existing `ecophys-g0-regression` environment (`torch 2.6.0+cu124`) is CUDA-compatible and completed
the matrix. No driver or system package was changed.
