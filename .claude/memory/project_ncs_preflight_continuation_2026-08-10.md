---
name: ncs-preflight-continuation-2026-08-10
description: "Exp131-134 lasting outcomes: event baselines passed without a new estimator, bistable diagnostic failed, two-rank CPU exact resume passed, and a minimal correctly specified synthetic L2 bridge passed while exposing latent sign non-identifiability."
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
  not touched. Single-V100 exact resume remains pending.

## Priority implication

Do not turn additional baseline smokes into G0 evidence. Next method work is the mathematical candidate spec,
five-nearest-method non-equivalence table and a separately preregistered candidate E0--E3 comparison.

## Synthetic observation bridge

- Exp134 emitted and reconstructed 2,160,000 aggregate-L5 events across 72 independent streams. All frozen
  correctly-specified recovery, future-split likelihood and permutation-control gates passed.
- Nonzero flow slopes had cell-median relative errors of about 1.0--2.1%; permuting the latent reduced fitted
  slopes and held-out gains to numerical noise. Median size-slope relative error was 1.08%.
- Reversing the latent sign exactly reverses the fitted slope with identical likelihood. Real/EcoMD use needs a
  fixed buy/sell sign anchor; L2 messages cannot orient an arbitrary latent coordinate.
- G3 remains open. The operator lacks an EcoMD adapter, price/order-level dynamics, misspecification tests and
  observation-only/Hawkes/queue-reactive comparisons. Paid L2 is still locked.
