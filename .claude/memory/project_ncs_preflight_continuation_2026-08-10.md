---
name: ncs-preflight-continuation-2026-08-10
description: "Exp131-136 lasting outcomes: no novel estimator, a frozen mixing-diagnostic failure, exact CPU/distributed state semantics, honest latent-flow naming, and synthetic L2 recovery/misspecification/state-complete adapter passes that do not clear G0 or G3."
metadata:
  node_type: memory
  type: project
---

# NCS zero-cost preflight continuation — 2026-08-10

## Scientific status

- G0 remains **AMBER / not passed**. Exp131 validates known LR and coupled-FD controls for two-state and
  compound-Poisson systems, but supplies no candidate estimator or accuracy--cost improvement.
- In exp131's slow two-state cell, fresh-short LR bias was `-12.61%`, persistent-detached LR `-38.01%`,
  stationary-oracle LR `+0.30%`, full-long LR `+0.47%`, and FD-CRN `-3.06%`.
- In the slow jump cell, coupled finite difference had `+5.64%` relative bias and `92.19%` 90% coverage;
  persistent-detached LR had `-31.63%` bias. Naive pathwise differentiation of the Poisson rate is invalid.
- Exp132 is a frozen **FAIL**: hard false-safe was `0%`, but easy resolved rate was `78.125%`, below the
  preregistered `80%`. The v1 threshold cannot be relaxed. Any diagnostic v2 needs an independent
  tuning/validation split.

## Distributed state semantics

- Exp133 added atomic checkpoint format v2 with model/optimizer/world size and a complete per-rank runtime:
  `SimulatorState`, primary and auxiliary generators, PyTorch CPU/local CUDA RNG, NumPy/Python RNG and history.
- The manual all-reduce trainer previously did not broadcast initial model parameters. This is fixed by a
  rank-zero parameter/buffer broadcast before optimizer construction.
- Formal two-rank CPU/Gloo uninterrupted 6-step versus `3 + new processes + 3` produced zero bit differences
  in model, optimizer and both rank runtimes. All formal checks passed at implementation commit `a54b4406f`.
- This is not yet a production-complete checkpoint contract: real sampler/data cursor, future scheduler/scaler,
  W&B, multi-node NCCL, asynchronous-write interruption and power-loss durability remain open.
- Both V100s were occupied by unrelated graphene production processes when checked on 2026-08-10; they were
  not touched. Exp133 is now held by `ecophys-exp133-queued.service` on V100-A. It requires the blocker service
  to be inactive, no compute process, ten consecutive one-minute low-utilization polls, and no graphene release
  marker before launch. At the last check it remained `waiting` with blocker/compute active.

## Priority implication

Do not turn additional baseline smokes into G0 evidence. The v0 mathematical candidate spec is complete but
fails non-equivalence: it is direct composition of persistent chains, hybrid pathwise/LR, Rhee--Glynn and
diagnostics. E0--E3 candidate runs are blocked until a new theorem/estimator identity survives citation audit.

## Synthetic observation bridge

- Exp134 emitted and reconstructed 2,160,000 aggregate-L5 events across 72 independent streams. All frozen
  correctly-specified recovery, future-split likelihood and permutation-control gates passed.
- Nonzero flow slopes had cell-median relative errors of about 1.0--2.1%; permuting the latent reduced fitted
  slopes and held-out gains to numerical noise. Median size-slope relative error was 1.08%.
- Reversing the latent sign exactly reverses the fitted slope with identical likelihood. Real/EcoMD use needs a
  fixed buy/sell sign anchor; L2 messages cannot orient an arbitrary latent coordinate.
- The misleading model field is now canonically `latent_flow_alignment`; legacy `ofi` API/artifact keys remain
  explicit aliases for historical compatibility.
- Exp135 passed all frozen gates on 144 streams/4.32M events. It correctly separated current-latent,
  observation-only, combined, lagged, nonlinear-even and null truths. The lag/current likelihood gap collapsed
  to `0.00844` nats/event at `rho=0.98`, preserving a real temporal-identifiability warning.
- Exp136 added a checkpointable absolute-clock EcoMD-to-L2 adapter. Eight `N=64,T=3000` simulator paths and
  20,000 emitted messages passed bit-exact chunk/resume and reconstruction gates. Median recovered slope was
  `2.010` for truth 2.0; latent beat observation-only by `0.0543` nats/visible event; the permutation gain was
  `1.15e-4`; the positive structural anchor beat its sign flip by `0.232`.
- G3 remains open. Exp136 uses fixed random EcoMD weights and a correctly specified synthetic emission family;
  its structural sign convention is not external market validation. Dynamic price/queue semantics,
  latency/censoring and Hawkes/queue-reactive/empirical baselines remain absent. Paid L2 is still locked.

## Queue and repository handoff

- At the final 2026-08-10 check, V100-A's `ecophys-exp133-queued.service` was active and correctly waiting:
  graphene's blocker service and one compute process were active, current GPU utilization was 20%, and the
  stable-idle counter remained `0/10`. V100-B had no duplicate EcoPhys queue and also had an active compute
  process. No production process was stopped or shared.
- The broad Mac pytest attempt was killed under memory pressure; focused suites had already passed. macOS File
  Provider then exposed roughly 15,000 repository/Git-object files as `dataless`, making the original clone's
  Git commands fail with `SIGBUS`. The eight unpushed commits were reconstructed in a fresh sparse clone and
  each recovered commit SHA/tree was checked exactly before the final result/document commit. The original
  cloud-backed worktree must be rehydrated or replaced before it is used again.
- In the healthy recovery clone, 45 focused tests and new-module Ruff passed. A bounded strict-mypy check on the
  four new observation/experiment modules passed after type-only fixes; the full historical import graph is not
  strict-mypy clean. Temporary reruns of exp135/136 kept every gate PASS and matched the frozen scientific
  payloads exactly after removing environment/runtime metadata.
