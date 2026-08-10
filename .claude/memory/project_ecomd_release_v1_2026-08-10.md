---
name: ecomd-release-v1-2026-08-10
description: "Active EcoMD source-preview/model-release boundary, state-law repairs, data-license exclusions, package evidence and hard gates after G0/F0 closure."
metadata:
  node_type: memory
  type: project
---

# EcoMD v1 source preview and model-release gates — 2026-08-10

## Binding release decision

- NCS method G0 and general simulator-audit F0 both failed. The active path is an EcoMD-specific transparent
  software/model release, not another audit paper or an immediate high-impact physics claim.
- Split release into S0 source research preview and S1 model release candidate. S0 contains source, contract,
  synthetic smoke and selected tests only. S1 requires a newly trained state-complete checkpoint that passes
  frozen stationary-fidelity gates.
- Do not release or tag the current research monorepo as the artifact. It has 60,570 tracked paths and 6,861
  `.pt` paths; a truncated GitHub tree response already accounted for about 6.55 GB of blobs. Build from an
  explicit allow-list instead. Do not rewrite history as an incidental release step.

## State/law audit and repair

- Exp127 candidate configs used `stochastic_mlp`, global state, two populations, jumps and the excess-demand
  price path, but omitted `training.state_complete`; old 24-step chunks therefore reset agent/global recurrent
  state while inference carried it through the full horizon. Those checkpoints are permanently ineligible.
- The newer `SimulatorState`/`rollout_state` implementation carries price, recurrent, clock, shock, integrator,
  neighbour-cache and RNG state and passes arbitrary-chunk and checkpoint-resume equality tests.
- A 2026-08-10 audit found a second mismatch: `_compute_rollout_reg_loss` still used legacy `rollout_chunk` even
  when the main trainer enabled complete state. It now takes the state-complete path and detaches the graph, not
  the forward values, at chunk boundaries.
- Release contract v1 hard-requires `state_complete: true`, explicit `persistent_state: true`, explicit
  `jump_legacy_train_proxy: false`, `bptt_checkpoint_every: 0` and `bptt_custom_function: false`. Historical
  configs remain runnable only as legacy provenance.

## Data and artifact boundary

- Yahoo Finance explicitly restricts redistribution of Yahoo Finance information. LOBSTER sample material has
  no recorded explicit redistribution grant; require written permission. No applicable explicit Binance Data
  Vision redistribution license is recorded. Exclude all three raw/derived datasets by default.
- Public smoke inputs are generated synthetically. Empirical replication gets provider acquisition instructions,
  raw hashes when permissible, deterministic preprocessing, split manifests and derived hashes—not vendor bytes.
- An allow-listed source-preview builder rejects checkpoint/data archive suffixes, result/output directories,
  credential names, prefix escapes and archives over 10 MiB. It emits the commit, manifest hash, artifact hash,
  byte count and file count. The first `git archive` implementation stalled on missing partial-clone objects;
  the builder now requires a clean allow-list against `HEAD`, enumerates only tracked/materialized files and
  writes a deterministic normalized tar without implicit network access.

## Current verification

- A no-data CPU smoke checks exact arbitrary chunking, serialized-state resume and finite nonzero gradients. It
  produced 35 nonzero finite gradient-bearing parameters and deterministic return hash
  `38398a13e5ce56cf6bd3dd789884c517488c8d39b3da8aa035968845b8d1db71` under the current environment.
- Twenty-seven extracted-artifact release/state/training tests and all 76 tests in the sparse research checkout
  pass. The strict package target passes on all 66 source modules. Commit-delta Ruff has zero findings on added
  lines; the separate full-package historical Ruff baseline is 342 findings and remains maintenance debt.
- Wheel `ecomd-0.0.1` built successfully, installed to an isolated target directory, imported from that target
  and passed the same CPU smoke. A pre-commit build hash was
  `131e8250c052a2c2198a2b635aed017e02b9b154d2cd7303eab4abe16e22f099`; it is diagnostic, not a release hash.
- Final clean-commit operational QA for `16a822c843db` built the 245,445-byte/89-file source archive twice with
  identical SHA-256 `e45bef6d6617880c84fd38afdbf4cc763d356c25fb987f39c2c60805b76bb454`. Two
  independent extracted trees built identical 246,664-byte wheels with SHA-256
  `53bb866aef886ecbb05a02756d7325d7ec1d57b1f14f4154265ff9dc5fcc0386`; isolated install, CPU
  smoke, 27 tests and changed-file Ruff passed. Machine report:
  `release/verification/16a822c843db.json`.
- The original machine report understated the full strict-mypy baseline as 83 errors/17 files because it checked
  only `train_distributed.py` plus its import graph. The true `mypy ecomd` baseline was 121 errors/26 files. Commit
  `4b741d6692e934540f9849c13d3d89b3878c5426` reduces the configured full-package target to zero errors across
  66 modules.
- Clean-commit QA for `4b741d6692e9` produced the same 246,840-byte/89-file source archive twice, SHA-256
  `7bec028d8a3468f546792b868b4991d1eb900b1e2b6af825294183faaf1afba6`. Two independent extracted source
  directories produced identical 248,107-byte wheels, SHA-256
  `5535add9760a4627698cfbe0d76148f83baaabc32622490a32a9dd29e77a3caa`; isolated import/smoke, 27 artifact
  tests and extracted-package strict mypy all pass. Machine report: `release/verification/4b741d6692e9.json`.

## Compute and next gate

- Keep both V100s idle until R0--R3 and one canonical M0 configuration are frozen. Then use one V100 32 GB for
  an fp32 reference pilot/checkpoint-resume/long-rollout run and the second for an independent host/seed repeat.
  Future expansion may use more non-H20 hardware; H20 remains excluded.
- R0--R3 are operationally complete for S0, which is ready but not published. S1 remains blocked. Next freeze one
  M0 model configuration and its traceability/resource contract; only then may an M1 V100 pilot be queued.

## M0 freeze and implementation — 2026-08-11

- The unique pre-implementation contract is committed at `2701833bcf7ba42803995745cd0fd338762b9ce0` and
  implemented by `configs/ecomd_v1/m0_reference.yaml`. Its raw SHA-256 is
  `8e161bee28a4712e9a152539894ad6a9193d2311498fa066d24e16427e9ffa33`.
- Reference architecture: N=256, d=32, hidden=96, stochastic symmetric k=50 pair MLP with Kac normalization,
  global GRU, four fixed friction/temperature types, Gaussian bath, zero jumps, normalized aggregate demand and
  fixed square-root impact. The model has 36,541 parameters. Long-rollout regularization is disabled.
- Kac/full-neighbour tests now lock dense-vs-stochastic energy and force equality. The stochastic estimator also
  scales by the actual sampled partner count when N is smaller than configured k, removing a small-N bias.
- A formal clean-worktree run on implementation commit `8951208ffd2f83e044a1094b5b98b206c9e839bb` passed
  the production-trainer CPU gate in 6.85 seconds. Model, optimizer, complete dynamic state/RNG, history and an
  eight-step continuation are bit-exact; 18 parameter tensors have finite nonzero gradients. Report:
  `release/verification/8951208ffd2f-m0-cpu.json`. This authorizes only the fixed 10-iteration V100 pilot, not
  market-fidelity or physics claims.
- The V100 runner fixes the effective pilot to N=256, 10 iterations, chunk 64 and FP32 (effective config SHA
  `0adb0ef6a5a3e9693e9b91fe301ab1ada19360a2b58de3bc0ec2173580937a88`). It compares 10 continuous iterations
  with exact 5+5 resume and hard-fails above 26 GiB reserved HBM or a 12-hour projected 600-iteration runtime.
  The first host must pass before the second host runs.
- V100-A exposes the 32 GB GV100 card under the board string `Tesla PG503-216` (PCI device `10de:1df2`), not a
  literal `V100` product string. The pilot hardware check explicitly accepts this deployed name plus standard
  V100 names, and rejects 16 GB cards and H20. At the 2026-08-11 preflight it was idle with no compute process;
  the separate Graphene 375 K queue was validation-locked with no release marker.
- V100-A formal pilot on `f1e3cd4fb312cdf484aa65564953e17e8125f00b` passed every gate. Ten uninterrupted
  iterations took 17.02 seconds; the full 10-vs-5+5 process took 32.05 seconds. Peak allocated/reserved HBM was
  11.475/11.994 GiB and the 600-iteration linear projection is 0.284 hours. Model, optimizer, dynamic state/RNG,
  history and eight-step continuation are bit-exact; 18 gradient tensors are finite/nonzero. Remote/local report
  SHA is `c99df8708de58119769a24069ff53da3049b6ea6da0c56d6048d15990b1410d7`; archived at
  `release/verification/f1e3cd4fb312-v100a.json`. V100-B is now authorized for the same-SHA host repeat.
- V100-B passed the identical pilot on a distinct GPU UUID. The complete 10-record history, continuation hash,
  memory profile, software environment, synthetic target and parameter count are exactly equal across hosts.
  V100-B took 16.54 seconds for ten iterations versus 17.02 on A (2.83% absolute difference over their mean).
  B report SHA: `1830a8527bd03e181a487b766aeea9a81c33403163fe55029c0611a1a9caf911`.
  Cross-host report: `release/verification/f1e3cd4fb312-v100-cross-host.json`. M0/R4 mechanics are complete;
  next freeze real SPX provenance/preprocessing and the stationary-fidelity protocol before a 600-step run.
- Both machines used the hostname `ubuntu22`, so the pilot's hostname-only hash collided. The distinct GPU UUIDs
  establish independent hardware for these reports; future reports hash hostname plus `/etc/machine-id`.
- Pre-M1 data audit exposed a real loader bug: `pandas.read_parquet` on physical files below Hive-style paths
  inferred partition fields and collided with the same stored `symbol` field. Training and baseline loaders now
  read each physical file through `pyarrow.parquet.ParquetFile`; a path-conflict/adjusted-close regression test
  is included. The 2015--2024 Yahoo files pass schema/coverage/null/duplicate audits, but lack acquisition time,
  request and library-version provenance. Reacquire the free SPX input with a complete manifest before M1.
- M1 is frozen before new outputs in `configs/ecomd_v1/m1_stationarity_screen.yaml` and its companion proposal.
  It uses a fresh audited Yahoo acquisition, seed-0 300+resume-to-600 training, 16 new calibration seeds
  (811000--811015), a committed gate fit before 16 held-out seeds (811100--811115), T=8000/L=4000 and full
  early/post/late reporting. No W-star or failed held-out transfer fails. Either post or late <=2/11 stops the
  positive-paper route; 3--4 is diagnostic-only; both >=5 plus <=10% late distance degradation merely authorizes
  multiseed/baseline/cross-market production. No checkpoint/rollout or new outcome was seen before this freeze.
- The formal free `^GSPC` acquisition ran from clean `4a2332d62616` and produced ten audited 2015--2024 shards.
  All annual byte hashes, row counts and timestamp ranges exactly match the historical cache, ruling out detected
  revision/normalization drift. The committed no-value manifest SHA is `0836ddd279a16db5010907120e65da87db58a2f2634c25f0e732334a98ffff7c`;
  train has 1,005 returns. Vendor bytes remain internal/untracked. Training must fail closed on manifest, physical
  shard and derived train-return hashes before V100 allocation.
- M1 production entry is fail-closed: the protocol now pins manifest file SHA `0836ddd2...`; preflight runs
  before CUDA and rehashes the manifest, all ten physical shards and all reconstructed split-return vectors.
  Checkpoints bind Git/config/protocol/manifest/dataset/train-return metadata and reject mismatched resumes.
  The only legal phases are a clean no-checkpoint `stop_after_iter=300` first segment and explicit resume from
  expected iter 300 to the unchanged final iter 600. Full regression is 110 tests and strict mypy covers 71
  modules. Deploy the exact clean commit next; no M1 checkpoint or rollout exists yet.
- The seed-0 SPX reference training completed on V100-A at exact `7b2cd40fe0f3`: 300+exact-resume+300 took
  294.85+294.61 seconds, peak reserved HBM 11.951 GiB. Final checkpoint SHA is
  `7822c030b44aa8e18110d807d7a4bfc15dea5ebd0175c5bd0fa2d2a10f96f34a`; it is format-2/state-complete/
  iter-600 with history 0--599, all checked values finite and 600 positive gradient rows. Services exited 0,
  checkout remained clean and GPU returned idle. Verification: `release/verification/7b2cd40fe0f3-m1-spx-training.json`.
- Operational disclosure: one accidental full checkout was terminated before CUDA, one missing-blob checkout
  was rejected, and one prelaunch shell substitution warning was bounded by independent idle checks immediately
  before/after. Neither rejected tree ran the experiment. Calibration is now separately bound to the final
  checkpoint and fresh node seed files; held-out is still locked and no stationarity/fidelity result exists.
- The 16 frozen calibration trajectories completed from clean evaluation commit `a18d70c1c78e` on the two
  V100s (eight interleaved seeds each). Both services exited successfully and returned their GPUs idle. A/B
  no-value shard-manifest hashes are `959c4047...51d9` and `44c2e944...6e8`. The result-blind gate fitter is
  implemented and requires global seed ordering plus exact file/manifest/source bindings. Calibration values
  have not yet been fitted at this point; held-out remains absent and locked until the gate artifact is committed.
- Calibration was first opened only after the fitter commit `179da420a`. The exact 16-by-8000 matrix hash is
  `18149f87...a90c`. The frozen energy tolerance is `0.019507027186009607`; W=0 fails narrowly and W=500/1000/
  1500 pass, selecting W-star 500. ADF/KPSS selects W-star 0. Gate artifact SHA is `17ad4f26...ae55`, with zero
  held-out trajectories at fit time. This only authorizes held-out transfer; no fidelity/physics claim follows.
- The pre-heldout binding, launcher and complete fixed-window analysis are implemented result-blind after gate
  commit `3f1303b04`. They pin W-star 500, the exact gate/checkpoint/source/seed hashes, require the binding blob
  to equal its sole first-add commit and encode every frozen decision tier. Full regression is 132 tests and
  strict mypy covers 75 modules. Commit/deploy/preflight this freeze next; no held-out output exists yet.
