# Experiment 133 results — atomic distributed exact resume

**Run date:** 2026-08-10  
**Implementation commit:** `a54b4406f738f929197f179a6b3f0a223050f3be`  
**CPU artifact:** `CPU_GLOO_RESULTS.json`  
**Single-V100 artifact:** `V100_RESULTS_455ed73a6f41.json`
**Decision:** two-rank CPU/Gloo and single-V100 CUDA gates PASS

## CPU process-boundary result

The formal test compared an uninterrupted six-iteration run with a three-iteration run resumed in new
processes to the same planned six-iteration learning-rate schedule. All preregistered CPU checks passed:

- final model tensors were bit-exact;
- final optimizer state was bit-exact;
- every rank's complete `SimulatorState`, rollout and auxiliary generator, PyTorch CPU RNG, NumPy RNG, Python
  RNG and history were bit-exact;
- exactly two rank runtime records were present and both ranks ended with the same model digest;
- loading with a mismatched world size hard failed;
- losses and gradients were finite, and no atomic-save temporary file remained.

All model, optimizer and rank-runtime difference counts were zero. The formal run used PyTorch 2.11.0 on
macOS CPU/Gloo and took about 18.2 seconds.

## Implementation finding

The audit exposed a separate distributed initialization defect: the manual gradient-all-reduce path could
construct different initial model parameters on different ranks and did not perform DDP's initial broadcast.
Rank-zero parameters and buffers are now broadcast before optimizer creation. Checkpoint format v2 stores one
complete runtime record per rank and promotes a temporary file with `os.replace`.

`SimulatorState.to(device)` was added so CPU-normalized checkpoint tensors can be restored to a local CUDA
device while RNG payloads remain in their required CPU representation.

## Single-V100 CUDA result

The supervised queue waited behind the unrelated graphene workload and launched only after the blocker was
inactive, no compute process was present and ten consecutive low-utilization polls passed. The clean formal run
used PyTorch 2.3.1+cu121 at queued repository commit `455ed73a6f41f6096b05d581385082a9e7fdc3f6` and finished
in 16.81 seconds.

All 12 recorded CUDA checks passed. The uninterrupted and `3 + new process + 3` executions had identical final
model, optimizer, complete rank runtime and RNG state; all three difference counts were zero. The rank/model
digest was synchronized, iterations and resume history were exact, a world-size mismatch hard failed, all
losses and gradients were finite, and no temporary checkpoint remained. The artifact SHA-256 is
`3b3ab8be3bc77e0a88bd619a527c3b8d85093d96b3ae4d68f4703421e4bdf943`.

## Remaining scope

This PASS establishes exact continuation for the tiny, stateful two-rank Gloo fixture. It does not yet establish:

- multi-node NCCL behavior or production `N=10,000` scale;
- an actual asynchronous kill during a write or durability under power loss;
- a real distributed sampler/data cursor, scheduler, AMP scaler or W&B resume contract.

At the time of the formal CPU run, both V100s were executing unrelated graphene production jobs and were left
untouched. The guarded queue later completed the CUDA gate without sharing or stopping that workload. WP1 still
requires the production-only cursor/scheduler/scaler, logging and interruption contracts relevant to the chosen
training configuration; the mechanics probe alone is not a production checkpoint guarantee.
