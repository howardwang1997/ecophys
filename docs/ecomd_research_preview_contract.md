# EcoMD research-preview contract

**Contract version:** 1

**Status:** source preview; no validated checkpoint

**Date:** 2026-08-10

## Intended use

The preview supports code inspection, deterministic synthetic smoke tests, gradient-path
checks, and reproducibility work on a differentiable stochastic multi-agent simulator. It
does not warrant empirical market fidelity, causal interpretation of latent variables,
order-level execution semantics, or production use.

## Simulator semantics

A continuation is exact only when it carries the complete `SimulatorState`. The state
contains agent positions and lagged positions, price state, regime/agent/global recurrent
states, the absolute clock, fundamental and pending exogenous values, shock state,
path-dependent integrator buffers, neighbour-cache state, and the explicit generator state.

Release-eligible training must satisfy all of the following:

- `training.release_contract_version: 1`;
- `training.state_complete: true`;
- `training.persistent_state: true`;
- `simulator.jump_legacy_train_proxy: false`;
- `simulator.bptt_checkpoint_every: 0`;
- `simulator.bptt_custom_function: false`.

`validate_release_training_contract` enforces these conditions. Historical configurations
without a contract version remain runnable for provenance, but they are explicitly
ineligible for a model release. Old checkpoints cannot be upgraded by metadata editing;
they require retraining because their optimization trajectories used different state
semantics.

The main training rollout and optional long-horizon regularizer both use `rollout_state`
under the release contract. Truncated BPTT may detach the graph at a chunk boundary, but it
must preserve every forward state value and the RNG stream.

## Observation semantics

The implemented aggregate-bin path may expose bin-level returns, signed aggregate demand,
volume-like aggregates, and deterministic derived summaries under its tested contract. It
does not create empirical order IDs, queue priority, cancellations, fills, or event-time L2
semantics. Those require a separate generative mechanism and validation target.

## Claim ledger

| Statement | Preview status |
|---|---|
| Differentiable stochastic simulator source is available | Supported by tests |
| Arbitrary chunking and checkpoint continuation are bitwise exact under the complete state contract | Supported on CPU test configurations |
| Current candidate checkpoint has the same contract | False; no checkpoint is endorsed |
| EcoMD reproduces stationary real-market stylized facts out of sample | Not established |
| Latent heavy-tail transients are real market physics | Not claimed |
| Current canonical model is MACE/equivariant | Not claimed |
| Aggregate bins are equivalent to an order book | False |

## Artifact boundary

The source preview is built from an explicit allow-list. It excludes all checkpoints,
experiment outputs, raw/derived market data, vendor archives, secrets, and the bulk research
history. A tag or archive of the current research monorepo is not a valid release artifact.

## Hardware boundary

CPU is sufficient for release packaging and smoke verification. A future checkpoint release
requires one frozen fp32 reference run on a V100 32 GB followed by an independent run on the
second V100. More GPUs may be added for seed coverage or scale tests. H20 is excluded from
the forward plan.
