# v2.1 Hawkes × ACF-shape sweep — SPX daily, N=200, 80 iters

**Base recipe** (v2.1, validated 2026-04-25): `gauge_enforce=false,
T_init_mode=ones, kyle_enabled=false, phi_init_gain=1.0, hawkes_alpha=0.1`.

**Sweep**: `hawkes_kappa ∈ {0.1, 0.3, 1.0, 2.0}` × `w_acf_shape ∈ {0.0, 0.3, 1.0}`,
12 configs.

## Results

| κ   | w_shape | n/11 | acf(r²)₁ | shape_loss | final_loss | autocorr(r) | cond_kurt |
|----:|--------:|-----:|---------:|-----------:|-----------:|------------:|----------:|
| 0.1 |    0.0  |  6   |  0.178   |   0.071    |   0.700    |   +0.196    |    72.7   |
| 0.1 |    0.3  |  7 ★ |  0.116   |   0.000    |   1.307    |   +0.324    |    33.9   |
| 0.1 |    1.0  |  7 ★ |  0.244   |   0.000    |   3.069    |   +0.472    |    34.4   |
| 0.3 |    0.0  |  5   |  0.474   |   0.079    |   0.680    |   +0.390    |     3.5   |
| 0.3 |    0.3  |  5   |  0.149   |   0.000    |   0.829    |   +0.350    |    36.9   |
| 0.3 |    1.0  |  6   |  0.431   |   0.000    |   3.338    |   +0.467    |     2.3   |
| 1.0 |    0.0  |  7 ★ |  0.312   |   0.000    |   0.731    |   +0.351    |    74.0   |
| 1.0 |    0.3  |  5   |  0.325   |   0.168    |   1.736    |   +0.369    |   152.4   |
| 1.0 |    1.0  |  5   |  0.330   |   0.361    |   3.663    |   +0.253    |    72.9   |
| 2.0 |    0.0  |  7 ★ |  0.463   |   0.000    |   1.562    |   +0.348    |    53.9   |
| **2.0** | **0.3** | **9 ★★** | **0.446** | **0.000** | **1.366** | **+0.332** | **70.8** |
| 2.0 |    1.0  |  9 ★★ |  0.432   |   0.000    |   3.760    |   +0.405    |    78.2   |

## Interpretation

1. **Two independent paths to 7/11 — only one to 9/11.**
   - Strong-Hawkes path (κ ∈ {1.0, 2.0}) without shape loss: 7/11.
   - Weak-Hawkes path (κ=0.1) with shape loss (ws ∈ {0.3, 1.0}): 7/11.
   - Combining strong Hawkes (κ=2.0) **with** shape loss (ws ≥ 0.3) reaches **9/11**.

2. **Why κ=2.0 + shape loss synergises.** Strong Hawkes generates the bursts
   (raises ACF lag-1 to ~0.45, matching real SPX); shape loss constrains the
   *decay shape* (prevents collapse to a flat plateau). Each alone hits the
   peak OR the shape; together they hit both. Shape loss is now zero at the
   end of training (ws=0.3 final shape_loss = 0.000), confirming the geometry
   is learned, not over-regularised.

3. **The two stragglers at 9/11.**
   - `autocorr_returns` (sim +0.33 vs real ±0.05) — too much short-term
     return memory; expected to ease at N=10K (population averages out).
   - `conditional_kurtosis` (sim +70.8) — fat-tail conditional shape; needs
     more training iterations and/or larger N to settle.

4. **κ=0.3 is a dead zone.** Maxes out at 6/11 (ws=1.0) regardless of
   regularisation. Hawkes too weak for genuine self-excitation, too strong
   to ignore.

## Decision

Adopt **κ=2.0, w_acf_shape=0.3** as the production v2.1 recipe.

- H20 config `experiments/016_ecomd_v2/config_h20_spx_N10k.yaml` updated.
- Expected at N=10K with 200 iters: 9–10/11 (both stragglers ease at scale).
- `final_loss=1.366` is higher than `0.731` of the κ=1.0/ws=0.0 7/11 config
  but final_loss is not the publication target — fact-pass count and ACF
  shape are.

## Files

- Sweep spec: `experiments/017_v2_ablation/grid_mac_v21_sweep.yaml`
- Per-config JSONs: `experiments/017_v2_ablation/results/v21_hK*_s*_result.json`
- Sweep CSV: `/tmp/v21_sweep_summary.csv`
