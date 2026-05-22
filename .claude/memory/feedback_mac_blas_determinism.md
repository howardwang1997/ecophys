---
name: feedback-mac-blas-determinism
description: "On Mac CPU, bit-exact in-process A/B determinism requires torch.set_num_threads(1); multi-threaded BLAS introduces reduction-order non-determinism"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d8f75917-cbc6-43cc-814b-11508430a13a
---

When writing **in-process A/B smoke scripts** on Mac that need bit-exact
identical results across two sequential calls (e.g. comparing baseline vs
feature-flag-on, or repro-checking determinism), set
`torch.set_num_threads(1)` at the top of the script.

```python
import torch
torch.set_num_threads(1)
# ... rest of imports + smoke logic
```

**Why:** PyTorch's default CPU multi-threading parallelises reduction
operations (matmul, sum, etc.) across cores. Because floating-point
addition isn't associative, the *summation order* — which depends on
thread scheduling — produces slightly different bit-patterns from run to
run. Two sequential `train_distributed(...)` calls with the same seed and
config in the same Python process can produce identical loss for the
first 3-5 iters then drift to ~10% diff by iter 30. Diagnosed
2026-05-22 Session 2 (see `logs/2026-05-22.md`).

**Confirmed**: with `set_num_threads(1)` + the SPS-generator fix in
commit `ce47e4fb`, two `train_distributed('gru')` × 2 calls produce
**max loss diff 0.00e+00** across 30 iters. Without `set_num_threads(1)`,
diff drifts to ~0.7+ by iter 10 despite all per-step RNG being seeded.

**How to apply:**
- **Smoke / repro / regression** scripts (any in-process A/B): add the
  one-liner. Cheap, no downside for short runs.
- **Production training** runs (H20 or Mac): do NOT need this. Each cfg
  runs in its own torchrun process; reproducibility within a single
  process (same seed → same trajectory) is unaffected by thread count.
  Single-thread mode would just slow training without helping anything.
- **Unit tests**: existing tests already pass without this because they
  share the *same* RNG path within a single test (same-seed equality is
  unaffected by BLAS threading — the non-determinism only shows when
  running two independent calls back-to-back).

**Related fix**: `ecomd/models/potentials.py:_sample_edges` was the
*first* non-determinism source (unsedeed `torch.rand` for SPS edge
sampling), fixed in commit `ce47e4fb` (2026-05-22). The BLAS threading
issue is the *second*, independent source. Both need to be addressed
for bit-exact in-process determinism on Mac.

**Edge case**: `ecomd/models/ecomd_v2.py:135 _sample_edges` has the
*same* SPS pattern as the fixed one in potentials.py but module-level
(not method); V2 is non-primary architecture, deferred.

See also: [[feedback-workflow]], [[feedback-smoke-test-autonomous]].
