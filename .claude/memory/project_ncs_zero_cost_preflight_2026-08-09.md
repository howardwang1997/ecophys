---
name: ncs-zero-cost-preflight-2026-08-09
description: "Lasting results from G0 and exp128-130: novelty remains AMBER, state/force/jump semantics repaired, analytic AR(1) exposes persistent-state bias, and free LOBSTER samples validate only the parser/reconstruction bridge."
metadata:
  node_type: memory
  type: project
---

# NCS zero-cost preflight — 2026-08-09

Branch: `ncs-invariant-calibration-v4`. Core implementation commit: `1f4e8a69e`; CUDA gate versioning
commits: `31773cc95`, `4704d2446`, `9fbcf4870`.

## G0 novelty status

- G0 is **AMBER, not passed**. Broad claims around steady-state sensitivity, persistent chains, unbiased
  estimators, stochastic/jump AD, constant-memory SDE gradients and generic simulator calibration are occupied.
- Do not name or advertise a new estimator until E0--E3 expose an algorithmically substantive gap relative to
  Poisson-equation/generator, likelihood-ratio, coupling/unbiased, finite-difference CRN and long-BPTT baselines.
- The only defensible candidate space is a fail-visible, mixing-aware invariant-gradient workflow with explicit
  initialization, truncation, event-gradient and Monte Carlo error decomposition. This is a research question,
  not a current claim.
- Audit: `papers/proposal/ncs_g0_novelty_audit.md`.

## WP1 state/force/jump semantics

- New `SimulatorState` contains particle/current-previous state, all price and recurrent states, absolute clock,
  fundamental/shocks/pending exogenous return, integrator path buffers, pairwise cache and explicit RNG state.
- `rollout_state` preserves arbitrary-chunk trajectories and attached gradients; `detached()` is the explicit
  truncated-BPTT boundary; versioned checkpoint payloads resume exactly in the single-process setting.
- Historical force evaluation depended on autograd graph topology: attached context could induce a total
  derivative, while detach/checkpoint produced the intended partial derivative. Default semantics now isolate
  the current differentiation node; a reproduction-only legacy flag remains.
- Training and inference now sample the same compound-Poisson jump law. Jump rate/scale are still config scalars;
  no pathwise-learning claim is allowed. A reproduction-only legacy proxy flag remains.
- Unknown dataset/period combinations now hard fail instead of silently loading SPX.
- Six CPU properties pass, including exact forward chunk/resume and attached-chunk parameter-gradient parity.
- Single-process `train_ecomd` has an opt-in state-complete path. Atomic DDP checkpoint/resume, per-rank RNG,
  data cursor, optimizer/scheduler/scaler and preemption tests remain open.

## Experiment 128

- Five arms are required: A historical; A' partial force; B state+force; C jump+force; D combined.
- Tiny CPU smoke used SPX/BTC, 5 arms, one seed, four iterations. All 10 cells were finite and every factor was
  numerically active. D--A smoke-loss contrasts were -0.00922 SPX and -0.01886 BTC, but this is explicitly not
  a performance or fidelity result.
- V100 v1 at N=500, dt=0.02 preserved bit-exact chunk/resume but failed the bit-exact autograd-mode rule by
  2.38e-7 and produced a non-finite 512-step random-model rollout. The failure artifact is retained.
- Diagnostic controls showed the same fp32 discrepancy with jumps disabled and exact RNG equality. Full dt=0.02
  first became non-finite at step 362 for the diagnostic seed; no-feedback and dt=0.005 variants completed 512.
- Post-diagnostic v2 at dt=0.005 passed 11/11 mechanics checks with exact RNG, <=1e-6 CUDA parity, live finite
  gradients, exact chunk/resume and finite 512 steps. Peak memory was 496,798,720 allocated / 526,385,152
  reserved bytes; wall time 4.78 s on the node reporting `Tesla PG503-216`, PyTorch 2.3.1/CUDA 12.1.
- V2 demonstrates CUDA feasibility under a stable integration setting; it does not erase v1 or prove production
  stability. Formal five-arm multi-seed WP2 and T=8,000 evaluation have not started.

## Experiment 129

- Analytic AR(1), 2,000 repetitions. At a=0.97, truth derivative 49.9884: fresh-short relative bias -56.1%,
  persistent-detached -27.5%, long rollout +3.8%, stationary oracle -3.6%, FD-CRN -3.0%, and the implemented
  Rhee--Glynn linear coupling +14.3% with high variance.
- Persistent state improves initialization but is not an invariant-gradient estimator. The current coupling
  implementation is not yet competitive and cannot support a method claim.

## Experiment 130

- Streamed all eight existing free LOBSTER sample archives, 1,381,420 events total, without loading the large
  SPY L50 CSV into memory.
- Timestamp/order/cross/negative-size checks had zero violations; visible message types 1--4 reconstructed the
  displayed book exactly in every archive; hidden executions left displayed state unchanged exactly.
- L1 OFI/message-proxy correlation ranged roughly 0.384--1.000 and OFI/midprice-delta correlation 0.064--0.379.
- This proves parser and observation-definition feasibility only. It does not produce an EcoMD L2 emission
  layer, synthetic parameter recovery, or real-data validation.

## Resource conduct

- Only the idle V100 at `100.80.236.112` was used for exp128 CUDA probes. The occupied V100 at
  `100.123.220.57` was not touched. No H20, paid data or compute expansion was used.
