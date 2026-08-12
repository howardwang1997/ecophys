# PLAN — feature/arch-extensions overnight H20 batch (2026-04-28)

**Branch**: `feature/arch-extensions` (off `feature/custom-autograd-step`,
HEAD `9a41983`).

**Status (Mac)**: implementation complete; all 6 tier modules + 100
configs + 8 generators + master launcher + 22 tier tests landed and
green. Existing 220+ tests still pass.

## Why this batch

Across 094 runs (031–036) under varied hyperparameters, no single
config exceeded ~5/11 stylized-fact coverage reproducibly.

- Best singletons (each enters a different fact basin):
  - `pcfix_chunk24_seed1` 7/11 — covers hill, gain_loss, aggreg_normality
  - `ph_init_s01_h96_seed1` 6/11 — covers autocorr_returns, dfa, zumbach
  - `ph_n_seeds_default_seed5/8` 5/11 — wider but shallower
- 035 stacked-winner (chunk=128 + h=96 + init=0.1 + Sprint 2): mean **2.40**
  — WORSE than any single lever. Hyperparameter effects don't compose.
- 036 ablation: removing chunk=128 from the stack recovers to mean
  **3.20** (the new "best basin" = `abl_no_chunk128`); no cell exceeds 4/11 mean.

→ Hyperparameter knobs are exhausted. The next axis is **architectural**.

## What's in the batch

Six tiers, all default-OFF (baseline equivalence). Each tier flips one
set of `EcoMDConfig` flags; combinations test composition.

| Tier | What | Hypothesis |
|---|---|---|
| 1.1 | Per-agent GRU memory `(N, d_memory)` aggregated into external context | DFA, zumbach, autocorr need agent-level temporal memory |
| 1.2 | K² type-aware pair-kernel heads (shared backbone) | volume_corr, gain_loss need fund/MM/HFT/retail to use different rules |
| 1.3 | Pair features: `+distance`, `+inner_prod`, signed Δs | Cheap test for "is `(s_i, s_j, |Δs|)` enough info" |
| 2.1 | Compound-Poisson jumps via `tanh(s)` drift correction | hill, gain_loss, autocorr need discrete jumps, not just SDE |
| 2.2 | Multi-timescale: 80% fast agents, 20% slow (every 4 steps) | DFA, zumbach need multi-scale temporal structure |
| 3.1 | ISAB attention pairwise (M=64, n_heads=4) — O(N·M) memory | Long-range structure needs global info flow per step |

**Memory-safety note (3.1)**: ISAB uses manual `einsum + softmax`
attention rather than `torch.nn.functional.scaled_dot_product_attention`,
because PyTorch's fused SDPA backends (Flash, mem-efficient) currently
break `create_graph=True` double-backward. At N=10K, M=64, d=32 the
attention scores matrix is 2.5 MB — negligible.

## Experiments (100 configs, ~3-4h on 8-card)

| Dir | Cells × seeds | Total | Description |
|---|---:|---:|---|
| 037_arch_tier_1_1_memory | 1 × 10 | 10 | Tier 1.1 only |
| 038_arch_tier_1_2_kernels | 1 × 10 | 10 | Tier 1.2 only |
| 039_arch_tier_1_3_features | 1 × 10 | 10 | Tier 1.3 (`pair_features_extra=all`) |
| 040_arch_tier_2_1_jumps | 1 × 10 | 10 | Tier 2.1 (lambda=0.5, scale=0.01) |
| 041_arch_tier_2_2_multitimescale | 1 × 10 | 10 | Tier 2.2 (fast_frac=0.8, slow_freq=4) |
| 042_arch_tier_3_1_isab | 1 × 10 | 10 | Tier 3.1 (M=64, n_heads=4) |
| 043_arch_pairs | 6 × 5 | 30 | hand-picked pairwise tier combos |
| 044_arch_all_stacked | 2 × 5 | 10 | all-tiers-on (with/without ISAB) |
| **Total** | | **100** | |

Pairs in 043: `1_1+1_2`, `1_1+2_1`, `1_2+1_3`, `2_1+2_2`, `1_1+1_3`,
`3_1+1_3`. Stacks in 044: `stack_no_isab` (keeps stochastic_mlp so
1_2/1_3 take effect) and `stack_with_isab` (ISAB pairwise; 1_2/1_3
inactive — flags are silent under `pairwise_kind=isab`).

All cells branch off `abl_no_chunk128` baseline (mean 3.20):
chunk=24, h=96, init_state_scale=0.1, Sprint 2 custom autograd,
twopop+Hawkes, default loss family.

## Run command (H20)

```bash
ssh h20
cd ecophys
git fetch --all
git checkout feature/arch-extensions
git pull
unset NPROC; bash scripts/h20_refresh_deps.sh

# Master driver. SKIP_DONE=1 by default (recoverable on partial completion).
DAEMON=1 bash scripts/h20_arch_overnight.sh

# Tail in another window:
tail -f experiments/_arch_overnight_*.log

# Per-dir tail:
tail -f experiments/0{37,38,39,40,41,42,43,44}_*/_run_*.log

# In the morning (if scoring didn't run automatically):
for d in experiments/0{37,38,39,40,41,42,43,44}_*/; do
    conda run -n ecophys python scripts/score_phase.py "$d"
done
```

Master driver runs the 8 dirs sequentially in priority order:
037 → 040 → 042 → 038 → 039 → 041 → 043 → 044. Single-tier dirs run
first so we keep the most-actionable signals if the batch is cut short.

## Decision rule (next morning)

For each tier with mean 11-fact coverage **n_seeds=10**:

- **mean ≥ 5.0** AND **CI-low ≥ 4.0** → tier breaks the basin ceiling;
  promote to top of the next sprint.
- **3.5 ≤ mean < 5.0** → mild improvement; record but deprioritize unless
  pair combos in 043 multiply the effect.
- **mean < 3.5** → tier null vs. baseline mean 3.20; archive.

Cross-reference with `scripts/perfact_analysis.py` post-batch to see
**which** facts each tier moved (not just total count). This tells us
whether tiers are diversifying basins (good for stacking) or doubling
down on the same facts (bad for stacking).

## Risks tracked

| Risk | Plan |
|---|---|
| ISAB double-backward breaks on H20 fp32 despite Mac smoke pass | Tested with manual einsum (no SDPA dependency). Fallback: switch to a no-attention pairwise. |
| Tier 1.1 BPTT through Sprint 2 Function blows memory at N=10K | h_agent is `(N, d_memory)` saved each step; ~640 KB at d=16, N=10K — cheap. Already smoke-tested. |
| 044 all-stacked NaNs out at iter 5 | SKIP_DONE=1 means the 7 prior dirs still produce data; we'd lose only the all-stacked data point. |
| H20 runs out of overnight time | Priority-ordered dirs; first 6 give the actionable singletons regardless. |

## Verification done before push

- `pytest tests/test_arch_extensions.py` — 22/22 pass (6 tiers ×
  default & Sprint-2 BPTT × pair-feature variants).
- `pytest tests/test_ecomd_smoke.py tests/test_v3_features.py
  tests/test_custom_autograd_step.py tests/test_integrator.py
  tests/test_potentials.py tests/test_paper_a_solidify.py` — all pass.
- `pytest tests/test_bptt_checkpoint.py` (selected, individually) — 4/4 pass.
- 100 configs all parse cleanly via `EcoMDConfig(**cfg) + LossWeights(**lw)`.
- End-to-end Mac mini-train (Tier 1.1, N=80, 3 iters) — finite loss,
  finite gradient, training_log.json written.
- Branch pushed to `origin/feature/arch-extensions` at commit `9a41983`.
