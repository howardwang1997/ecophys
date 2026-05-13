---
name: Branch F (088) results — depth-2 ceiling + BTC fact-trading
description: Empirical findings from 088 pair sweep (460 cfg, 50-seed confirmation): depth-2 composition is sweet spot, BTC trades facts not lifts, B3 most stable mechanism
type: project
---

460-run sweep landed 2026-05-13 (commit `874557e`). Scoring via `scripts/score_summary.py` (the standardized tool we built to prevent the H20 cherry-pick bug from recurring).

**Best cells** (stability filter applied):
- `pair_AB` (asym + B3 discrete regime): mean=5.18, max=8, n=28/30, rej=2 — best 2-mechanism combo
- `conf_asymdrag_a06`: mean=4.94, max=9, n=49/50 — Branch D's 5.10 was inflated by ~0.16 at n≈30
- `conf_b3_k3_pure`: mean=4.94, max=8, n=50/50, **0 rejections** — most stable mechanism at any seed count
- `pair_LA` (Lévy + asym): mean=4.96, max=9 — high variance, 4/30 rejected
- `triple_LAM`: mean=4.79 — confirms Branch E `combo_no_inner` (4.74) replicates

**Three structural findings**:

1. **Depth-2 compositional sweet spot**. Stacking depth → mean: 1=4.94, 2=5.18, 3=4.79, 4=4.62. Monotonic decline past depth 2. The v3 architecture composes weakly at depth 2 and interferes at depth ≥3.

2. **Cross-asset = fact-trading, NOT lift**. SPX `pair_AB`=5.18 but BTC `pair_AB`=4.58 (worse). BTC fixes `hill_tail` (μ=2.5 in band) but breaks `aggregational_gaussianity` (μ=330) and `dfa_hurst` (μ=1.00). The Branch E `btc_v4combo`=5.39 SOTA was BTC-period luck; doesn't replicate at n=30.

3. **B3 is the stability champion**: 0/50 rejections (every other cell has 1-4/30 rejections). Anchor mechanism for any future composition.

**Why:** This batch was designed to test "do pairs compose where 4-mech combos don't" (Case A/B/C decision tree from `papers/proposal/run_list_2026-05-12.md`). Result: Case B — pairs compose weakly but no breakthrough. Direct input to the NeurIPS 2027 plan reframe (see `project_paper_a_neurips_2027.md`).

**How to apply:** When designing future ECoMD experiments, default to depth ≤ 2; treat depth ≥ 3 as a dead end barring architectural change. When claiming cross-asset generalization, report per-fact pass-rate, not pass-count mean. Use B3 as the safe-mechanism baseline.

**See also**: `logs/2026-05-13.md` for full per-fact decomposition; `experiments/088_pairs_and_confirmation/scoreboard.md` for raw table.
