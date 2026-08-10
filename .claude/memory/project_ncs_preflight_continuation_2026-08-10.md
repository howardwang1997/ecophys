---
name: ncs-preflight-continuation-2026-08-10
description: "Exp131-139 lasting outcomes: no novel estimator, exact CPU/distributed/CUDA state semantics, synthetic observation passes, and external continuous-time baseline/numerical-repair failures; G0 and G3 remain open."
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
- Both V100s were initially occupied by unrelated graphene production processes and were not touched. The
  supervised `ecophys-exp133-queued.service` waited for the blocker to stop, no compute process, ten consecutive
  low-utilization polls and no graphene release marker. It later launched on V100-A and passed all 12 frozen
  uninterrupted-versus-resume CUDA comparisons with zero difference counts in 16.81 seconds.

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
- Exp137 passed all 9 frozen gates on 64 streams and 2,560,000 dynamic aggregate-L5 events. Two clean, exact-
  commit CPU-only shards on the V100 hosts finished in about 194 seconds each. State/chunk/resume and independent
  reconstruction were bit-exact; all streams had both price-move signs. Under latent-incremental truth, the
  combined model beat the full queue-reactive plus discrete marked-Hawkes-logit observation model by
  `0.0566--0.1136` held-out nats/event. Under observation-only truth the added latent gain was between
  `-4.30e-5` and `-3.41e-7`, with median absolute latent coefficients `0.00415--0.00704`. All controls survived
  prospective 20% censoring.
- Exp138 froze its protocol at `e4fa739b` before implementation or target fits and ran exact-commit
  `09ded226` on five free LOBSTER streams totaling 2,641,557 external messages. It validated vendor sign/schema,
  two deterministic timestamp-tie policies, causal row-`i-1` queue features, an exact continuous-time six-mark
  Hawkes/queue likelihood and eight generated Hawkes recovery controls. Both CPU-only V100-host shards exited
  zero in about 9.0 and 7.2 CPU minutes; the GPUs were hidden and unused.
- Exp138 is a frozen **FAIL (8/9 gates)**. Provenance, timestamp/marks, no-lookahead, generated recovery,
  training nesting, aligned queue control, tie robustness and full reporting passed. Real-fit convergence
  failed: aligned combined queue--Hawkes was 0/10 converged and shifted was 1/10, with failed-cell gradients
  `0.245--0.644` versus the `1e-5` fallback. Aligned-minus-shifted was positive for all five symbols under both
  tie policies and had cross-symbol medians `0.003731`/`0.003913` nats/event, but this is diagnostic only.
- G3 remains open. Exp137 is still synthetic, while exp138 contains no EcoMD latent and its combined external
  fits are not converged. A separately preregistered optimizer/KKT repair may use generated/development and
  training-only data; the now-inspected exp138 test split cannot independently confirm it. Unseen days/markets,
  a frozen EcoMD-to-message map and individual-order or explicitly limited aggregate semantics remain absent.
  Paid L2 is still locked.

## Compute and repository handoff

- No production process was stopped or shared. After graphene released V100-A, exp133 used that card and
  completed. Exp137 then used one CPU process on each V100 host with CUDA explicitly hidden; the two GPUs were
  untouched by exp137 and both formal shard services exited successfully.
- The broad Mac pytest attempt was killed under memory pressure; focused suites had already passed. macOS File
  Provider then exposed roughly 15,000 repository/Git-object files as `dataless`, making the original clone's
  Git commands fail with `SIGBUS`. The eight unpushed commits were reconstructed in a fresh sparse clone and
  each recovered commit SHA/tree was checked exactly before the final result/document commit. The original
  cloud-backed worktree must be rehydrated or replaced before it is used again.
- In the healthy recovery clone, 45 focused tests and new-module Ruff passed. A bounded strict-mypy check on the
  four new observation/experiment modules passed after type-only fixes; the full historical import graph is not
  strict-mypy clean. Temporary reruns of exp135/136 kept every gate PASS and matched the frozen scientific
  payloads exactly after removing environment/runtime metadata.
- Exp138 development added eight focused continuous-time tests; 21 focused observation tests, Ruff and the
  bounded strict-mypy target passed before formal execution. Its formal shard hashes are `3c28a680...172f5e`
  and `624ffd91...43c6d`; the merged hash is `0e25df8c...2fecf2` and a temporary re-merge was byte-identical.

## Exp139 numerical repair — formal FAIL (8/9)

- A read-only training-objective audit showed that exp138's raw gradients overstate boundary violations, but
  the correct cell-level projected residuals were still `1.318e-4--1.092e-2`, above `1e-5`; exp138 remains FAIL.
- Exp139 was preregistered at `338e0165`, with finite-difference tolerances frozen at `732e1e7b`, before any
  candidate optimization. The clean implementation `e6a7eaaf` adds bound-aware KKT diagnostics, two-start
  deterministic refinement, generated direct-Hawkes equivalence and a loader that materializes real data only
  through the 60% training boundary (plus timestamp-only tie sentinel).
- Thirty-one focused observation tests, Ruff and bounded strict mypy passed. Two dirty 20k-row smokes completed
  all 120 target fits: maximum selected KKT `4.21e-7`, 120 dual-qualified starts, maximum start gap `3.69e-8`,
  generated objective gap `1.11e-15` and matching anchor hashes. These are execution diagnostics only.
- Both clean formal CPU-only shards completed with one BLAS thread and CUDA hidden. Shard0 used 1,412.49 worker
  seconds and has SHA-256 `2fe252db3ef0533b06c08cfcfd3a6e9aa5b75d190148f2421a7d27e784e28276`; shard1 used
  819.84 seconds and has SHA-256 `4e4879d823c5672dd5ca0428efee3058996c14c751d7e679e6362844dd9aed35`.
  The recovered services had deactivated successfully, no duplicate shard was launched, and both V100s stayed
  unused. The merged artifact hash is `21818f9d9798b0c213239efa19160ac9bf46be1759cb98643367d221a8b08984`;
  an independent re-merge was byte-identical.
- Exp139 formally **FAILS 8/9 gates**. All 120 real selected targets and all 240 individual starts met the
  `1e-5` KKT selection threshold; maximum selected KKT was `8.91e-7`, maximum complementarity `7.62e-9`, and
  maximum dual-start objective gap `6.52e-9`. Every selected objective improved on the legacy rerun. All 32
  generated combined starts met `1e-7` and matched the direct-reference objectives within `1.79e-14` nats/event.
- The sole failed gate is generated equivalence because direct-Hawkes references for replicate/target `(1,0)`
  and `(5,0)` stopped at `1.62e-8` and `2.02e-8`, above the separately frozen `1e-8` reference threshold after
  all six refinement stages. This localizes the failure to strict reference-solver convergence but cannot turn
  the formal decision into PASS. Any new numerical gate needs a separately preregistered solver family and
  fresh generated seeds; real empirical confirmation still requires unseen dates or markets.

## Exp140 independent reference solver — formal pending

- A temporary development prototype used only exp139's eight already exposed generated streams. One analytic-
  Hessian Newton step reduced all 16 direct-reference projected residuals to at most `4.39e-15`, with objective
  changes at most `1.33e-15`. No future formal stream or real data was inspected.
- Exp140 was preregistered at `6d3940b9` before implementation and before generating root `140202608`. It freezes
  16 new two-mark Hawkes streams, two starts, an L-BFGS-B warm stage, at most eight no-fallback active-set Newton
  steps, `1e-10` KKT/complementarity gates, analytic gradient/Hessian checks, algebraic direct/intercept-only
  identity, cross-node determinism and complete reporting. It opens no real archive.
- The separate-root dirty smoke passed execution diagnostics: 8/8 endpoints qualified, maximum projected KKT
  `6.87e-12`, maximum complementarity `4.72e-13`, maximum start gap `2.22e-16`, objective-identity error
  `2.22e-16`, gradient-chain error `5.23e-17` and identical anchors. Twenty-five focused observation tests,
  Ruff and bounded strict mypy pass. Formal execution awaits a clean implementation commit.
