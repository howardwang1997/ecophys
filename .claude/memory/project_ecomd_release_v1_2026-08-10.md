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
- Twenty-seven focused release/state/training tests pass. Ruff passes on all changed Python files.
- Wheel `ecomd-0.0.1` built successfully, installed to an isolated target directory, imported from that target
  and passed the same CPU smoke. A pre-commit build hash was
  `131e8250c052a2c2198a2b635aed017e02b9b154d2cd7303eab4abe16e22f099`; it is diagnostic, not a release hash.
- Full strict mypy is not clean: 83 errors in 17 imported files. This is an honest R2 blocker, not waived by the
  focused runtime tests.

## Compute and next gate

- Keep both V100s idle until R0--R3 and one canonical M0 configuration are frozen. Then use one V100 32 GB for
  an fp32 reference pilot/checkpoint-resume/long-rollout run and the second for an independent host/seed repeat.
  Future expansion may use more non-H20 hardware; H20 remains excluded.
- Next: commit the contract/repair, run the clean-commit source artifact and isolated-wheel experiment, close
  strict typing or narrow the genuinely public core, then freeze one M0 model configuration. Only after that
  may an M1 V100 pilot be queued.
