---
name: chunk_steps > 24 OOMs at full 4.2 arch + N=10K
description: Per-card H20 (96GB) OOMs at chunk_steps>24 with full 4.2 + 2.1 architecture; 8-card NPROC>1 doesn't help (DDP, not tensor-parallel)
type: project
---

**Hard constraint as of 2026-04-30:**

At full Tier 4.2 + Tier 2.1 architecture (gate + u + LN + jumps + N=10K + hidden=96 + Sprint 2 custom autograd path), `chunk_steps > 24` OOMs on a single H20 (96GB).

**Why 8 cards don't help directly:**
- `train_distributed.py` is **data-parallel-over-iterations**: each rank runs full N×chunk simulator with different seed; gradients all-reduced. Per-card memory same as NPROC=1. (See file docstring lines 7-19.)
- True tensor-parallelism on N is documented as "v2 story when N=5×10⁵" — NOT implemented.
- Sprint 1 (`spatial-checkpoint`) and Sprint 2 (`custom-autograd-step`) are intra-card optimizations, not cross-card pooling.

**Available memory-reduction levers (no new code needed):**

| Lever | Cost | Expected chunk gain |
|---|---|---|
| Reduce N from 10K → 5K | SF estimate noise ↑ √2 | chunk → 48 (1.0× memory) |
| Reduce N from 10K → 2.5K | SF estimate noise ↑ 2× | chunk → 96 |
| Reduce hidden from 96 → 64 | model capacity 1/3 down | chunk → 36 |
| Disable `global_state_into_pair` | u becomes only-aggregator | chunk → 48 likely |

**Code-side levers (not yet implemented):**

| Lever | Difficulty | Expected gain |
|---|---|---|
| **bf16 mixed precision** (autocast + custom_fwd/bwd) | 1-2h | 2× chunk for free; H20 SXM5 also 2× speed |
| Stop-grad rollout regularization (no chunk increase, but fixes train/eval mismatch) | 1-2h | orthogonal — keeps chunk=24 |
| Tensor-parallel on N (cross-card sharding) | 1-2 weeks | 8× chunk, NVLink fast |
| Pipeline parallelism on chunk_steps | 2-3 weeks | 8× chunk, complex backprop |

**How to apply:**
- Never attempt chunk > 24 + 4.2 arch + N=10K without one of the above levers
- For 1-day exploration: use N tradeoff (cheapest) + bf16 if implemented
- For paper-grade chunk size: bf16 → 48 OR (N=5K, chunk=48) — both keep memory budget
- **N=10K, chunk=48 requires tensor-parallel — no shortcut for that combination**
- The orthogonal fix (no chunk increase) is rollout regularization — reach for that first when "we need longer horizon" comes up
