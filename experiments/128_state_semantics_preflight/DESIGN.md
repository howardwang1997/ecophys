# Experiment 128 — state / force / jump semantics preflight

**Date frozen:** 2026-08-09  
**Status:** CPU mechanics preflight; not confirmatory evidence  
**Cost boundary:** existing repository data, Mac CPU or one already-available V100; no data purchase,
no compute expansion, no H20

## Question

Before spending the WP2 budget, determine whether the historical training path and the repaired scientific
path are executable under a common harness, whether every factor produces a measurable intervention, and
whether all arms can train without NaN or broken gradients.

During implementation, checkpoint-resume testing exposed a third mismatch beyond the two factors in Plan v4:
the historical force helper sometimes computed a total derivative through price/global context sharing the
history graph, while a detach or checkpoint boundary computed the intended partial derivative with context
held fixed. Therefore a four-arm design no longer identifies all relevant defects.

## Frozen five-arm screening design

| Arm | complete state + absolute clock | partial-force semantics | train/inference jump parity | Interpretation |
|---|---|---|---|---|
| A historical | no | no | no | reproduction control |
| A' force | no | yes | no | isolates force-definition defect |
| B state+force | yes | yes | no | adds full state continuity |
| C jump+force | no | yes | yes | adds jump parity |
| D combined | yes | yes | yes | repaired path |

Comparisons are `A'−A` (force), `B−A'` (state/clock), `C−A'` (jump), and `D` versus all controls.
Formal WP2 screening will use this five-arm design unless this preflight proves one factor is an exact no-op.

## CPU preflight

- Markets: existing SPX daily and BTCUSDT 2024Q1 minute returns.
- Simulator: deliberately tiny (`N=32`, `d=8`, hidden 16), with regime, agent memory, global state,
  non-resampling stochastic edges, integrator EMAs, multi-timescale updates and compound-Poisson jumps active.
- Default budget: 4 optimizer iterations × 32 steps, one training seed per market and arm; evaluation uses a
  fixed 256-step forward rollout.
- Target/loss: the existing three differentiable moment surrogates, used only as an end-to-end smoke signal.
- Recorded: final train loss, evaluation loss/components, gradient norm, parameter hash, finite-value flags,
  wall time and exact configuration.

This run is intentionally underpowered. It may establish only:

1. arms are mechanically distinct;
2. repaired training has live gradients and finite outputs;
3. the V100 screening harness is worth launching.

It may not establish superiority, market fidelity, statistical significance, or NCS viability.

## Hard preflight gates

- all 10 default cells (5 arms × 2 markets × 1 seed) finish;
- no NaN/Inf in train or evaluation outputs;
- parameter hashes are not all identical after training;
- A and A' differ when context/history features are active;
- A' and C differ when jumps are active;
- A' and B differ when agent/global/regime state is active;
- D passes state chunking, detach, jump and checkpoint regression tests.

If an intervention is numerically inactive, debug the harness before any V100 run. No ranking of arms will be
used to modify the formal primary metric.

## Commands

```bash
conda run -n ecophys python experiments/128_state_semantics_preflight/run_cpu_preflight.py
conda run -n ecophys pytest -q tests/test_simulator_state.py
```

The production WP2 run is not authorized by a CPU smoke result alone. Its configs, seeds, main metric and
training budget must be frozen in a separate preregistration after this experiment closes.

