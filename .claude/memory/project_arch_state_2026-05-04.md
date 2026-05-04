---
name: EcoMD architectural state 2026-05-04 (post 85-seed retest)
description: After 064 added 50 NEW seeds, p_4_2__2_1 mean settles at 5.14/11 (85 seeds pooled); but the autocorr_returns metric is essentially AR(0.9) drift, inflating other facts. True post-AR(1) pass count likely ~3/11.
type: project
originSessionId: 6929e7db-e7e9-4079-9f5e-564e7b32f7b4
---
**Current best EcoMD architecture (as of 2026-05-04):**

`p_4_2__2_1` = full Tier 4.2 dyngraph + Tier 2.1 jumps. Same config as 2026-04-30 memo.

**Real performance** (85-seed pooled CI, 048 seeds 0-4 + 052 seeds 5-34 + 064 seeds 35-84):
- 35-seed (April 30): mean 5.40/11
- 50-seed retest (May 4): mean **4.96/11** — 35-seed value was partial lottery
- **85-seed pooled**: mean ≈ **5.14/11**, max 10/11 (3 seeds: 21, 51, 70), ≥7 hit rate ~24%, ≥9 hit rate ~5%

**The "5.14/11" is itself contaminated** — see `project_ar1_drift_artifact.md`:
- ρ̂ on returns = 0.904. The simulator outputs are AR(0.9), not random walk.
- `acf_squared_returns` and `dfa_hurst_abs_r` "pass" partly because of AR(1) baseline.
- Theoretical post-AR(1)-whitening pass rate: ~3/11 (one fewer fact directly via
  acf_sq² collapsing, one fewer via Hurst dropping below 0.6 lower bound).
- Empirical confirmation pending E3b H20 run.

**What 053-066 long-weekend did NOT find:**
- bf16 chunk=48/64 doesn't lift mean (5.0-5.5 across all)
- bigN N=10K bf16 = 4.75 mean (worse, not better); N≥15K eval OOM
- long_training (n_iters=400/800) = 5.0 (no convergence improvement)
- jump_grid_wide overall mean 4.48 (worse than baseline)
- 057 rollout_reg `rr_s120_w10_e5` mean 6.83 (n=6) — only positive signal but lottery zone

**One real signal worth chasing**: 057 `rr_s120_w10_e5` (rollout reg horizon=120, weight=10, every-5-iters). Mean 6.83 / max 10 / ≥9 hit 33% on n=6. Needs 30-seed retest to confirm.

**Why this matters for papers:**
- NeurIPS 2026 main (deadline ~May 22) is essentially gone unless rr_s120 confirms AND AR(1) artifact is fixed within 18 days. Both conditions unlikely.
- Workshop / arXiv / ICML 2027 / NeurIPS 2027 remain on the table per plan v3.
- ANY paper draft must include AR(1)-whitened companion column.

**How to apply:**
- When user asks "what's our best", quote 5.14 (85-seed) NOT 5.40, AND flag the AR(1) contamination
- Don't repeat 7.20 from 048 alone (5-seed lottery) or 6.83 from 057 alone (6-seed lottery)
- For paper claims, default to mean+CI from n≥30 AND post-AR(1) residual column
- Architecture exploration is in diminishing returns — focus shifted to dynamics fixes (overdamped regime, force noise injection, w_autocorr_r boost)
