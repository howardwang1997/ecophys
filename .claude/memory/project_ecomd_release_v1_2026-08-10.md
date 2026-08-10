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
