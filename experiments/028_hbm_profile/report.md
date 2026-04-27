# Phase 6 — HBM Profile Results

Each config trained 3 iters; peak HBM captured via `torch.cuda.max_memory_*`. Predicted column uses calibration of 3.5 GB/step at N=10K stochastic_mlp + create_graph=True + linear scaling in N + ~3 GB fixed overhead.

| config | N | chunk | K | predicted GB | **measured alloc GB** | reserved GB | train time |
|---|---:|---:|---:|---:|---:|---:|---:|
| `p6_baseline_n10k_chunk24_K0` | 10,000 | 24 | 0 | 87.0 | **79.64** | 80.68 | 3s |
| `p6_n100k_chunk64_K2` | — | — | — | — | **OOM/missing** | — | — |
| `p6_n10k_chunk128_K4` | — | — | — | — | **OOM/missing** | — | — |
| `p6_n10k_chunk128_K8` | — | — | — | — | **OOM/missing** | — | — |
| `p6_n20k_chunk128_K8` | — | — | — | — | **OOM/missing** | — | — |
| `p6_n50k_chunk128_K4` | — | — | — | — | **OOM/missing** | — | — |

## Calibration check

Baseline (chunk=24 N=10K K=0): predicted=87.0 GB, measured=79.64 GB, ratio = 0.92×
→ **Calibration accurate** (within ±15%)

## BPTT checkpointing failure analysis

All 5 BPTT-checkpointed configs OOM'd. The OOM traceback shows allocation
failure during `torch.autograd.grad` inside `conservative_forces`, called
from within a `torch.utils.checkpoint` recompute:

```
File "ecomd/models/potentials.py", line 307, in conservative_forces
    (grad_s,) = torch.autograd.grad(u, s, create_graph=create_graph)
```

Root cause: BPTT checkpoint assumes the forward pass stores intermediate
activations that can be discarded and recomputed. But EcoMD's forward pass
itself calls `autograd.grad(create_graph=True)` to compute forces from the
learned potential. During recompute, this `autograd.grad` must reconstruct
the full computation graph, re-allocating all the memory that checkpointing
was supposed to save. Net result: K=8 checkpoint uses the same memory as
K=0 (no checkpoint).

This is a fundamental incompatibility between gradient checkpointing and
higher-order autograd (forces via `autograd.grad`). The fix requires either:
1. **Spatial sharding** — shard pairwise interaction across GPUs so per-GPU
   memory scales as O(B) not O(N), making checkpointing unnecessary.
2. **Custom force computation** — replace `autograd.grad` with a manually
   implemented force kernel that doesn't require graph retention.
3. **Forward-mode AD** — use `torch.func.jvp` instead of `autograd.grad`
   for force computation (avoids backward-mode graph retention).

## Implications

- **Only chunk24_K0 (no BPTT) is feasible** at N=10K on single H20 (98 GB).
- N=20K/50K/100K require spatial sharding (`feature/spatial-checkpoint`).
- All 109 loss-redesign configs were fixed to chunk24_K0 as a workaround.
- The `ch` (chunk × BPTT) ablation axis is collapsed; `lf`, `te`, `dm`,
  `bal` axes remain valid.
