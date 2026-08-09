# Experiment 133 results — atomic distributed exact resume

**Run date:** 2026-08-10  
**Implementation commit:** `a54b4406f738f929197f179a6b3f0a223050f3be`  
**CPU artifact:** `CPU_GLOO_RESULTS.json`  
**Decision:** two-rank CPU/Gloo gate PASS; single-V100 CUDA gate waiting for an idle card

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

## Remaining scope

This PASS establishes exact continuation for the tiny, stateful two-rank Gloo fixture. It does not yet establish:

- single-V100 CPU-to-CUDA round-trip parity;
- multi-node NCCL behavior or production `N=10,000` scale;
- an actual asynchronous kill during a write or durability under power loss;
- a real distributed sampler/data cursor, scheduler, AMP scaler or W&B resume contract.

At the time of the formal CPU run, both available V100s were executing unrelated graphene production jobs, so
the CUDA gate was not launched. Their jobs were left untouched. WP1 remains incomplete until the V100 check and
the production-only cursor/scheduler/scaler contracts relevant to the chosen training configuration are tested.

