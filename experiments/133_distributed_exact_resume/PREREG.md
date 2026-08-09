# Experiment 133 — atomic distributed exact-resume

**Frozen:** 2026-08-10, before implementation results  
**Status:** WP1 production-semantics feasibility test  
**Cost boundary:** local CPU/Gloo plus one already-available V100 when idle; no expansion, no paid data, no H20

## Question

Can a process-boundary restart reproduce uninterrupted state-complete training when every distributed rank owns
an independent simulator trajectory and random stream?

The historical checkpoint stores rank-0 model and optimizer weights only. It does not store per-rank simulator
state, explicit generator state, global CPU/CUDA/NumPy/Python RNG, or a data cursor. Incrementing the seed by the
iteration number is not an exact resume mechanism.

## Required checkpoint payload

Format v2 must atomically contain:

- next optimizer iteration;
- model and optimizer state;
- normalized simulator/training configuration and world size;
- one runtime record per rank;
- complete `SimulatorState` payload for each rank;
- explicit rollout-generator state for each rank;
- PyTorch CPU RNG and local CUDA RNG where present;
- NumPy and Python RNG state;
- state-complete/legacy-path label and checkpoint format version.

Tensor runtime state is serialized on CPU and restored to the local device. A temporary file must be flushed by
`torch.save` and promoted with `os.replace`; a partially written target must never be treated as valid.

World-size mismatch, missing rank runtime, format mismatch, state-complete flag mismatch and incompatible
pairwise-cache kind must hard fail. Legacy format-v1 checkpoints may load model/optimizer for reproduction but
must be labelled non-exact and cannot pass this experiment.

## Frozen comparison

Use a tiny but stateful simulator with stochastic non-resampling edges, regime/agent/global recurrent state,
integrator feedback buffers, multi-timescale clock and compound-Poisson jumps. Use fixed synthetic moment
targets; no market data are needed.

Compare two independent executions initialized from the same seed:

1. uninterrupted six optimizer iterations;
2. three iterations, final atomic checkpoint, new process, resume to iteration six.

The CPU test uses two Gloo ranks. The CUDA test uses one V100 rank because the available V100 machines are
independent single-card nodes; it tests device round-trip but does not pretend to be a multi-node NCCL test.

## Frozen hard gates

- CPU two-rank final model tensors are bit-exact between uninterrupted and resumed runs.
- CPU optimizer state and iterations 3--5 losses are bit-exact.
- Every rank's final complete simulator state, explicit generator state and captured global RNG states are
  bit-exact.
- Checkpoint contains exactly two distinct rank records and no temporary checkpoint remains.
- Attempting to load the two-rank checkpoint with world size one hard fails.
- Single-V100 uninterrupted/resumed final model, optimizer, complete simulator state and RNG are bit-exact; if a
  CUDA library prevents bit equality, the run fails rather than relaxing the threshold post hoc.
- All gradients and losses are finite.

Passing establishes restart semantics at this scale only. It does not validate production `N=10,000`, multi-node
NCCL, filesystem failure under power loss, W&B continuity or the scientific quality of the training objective.

