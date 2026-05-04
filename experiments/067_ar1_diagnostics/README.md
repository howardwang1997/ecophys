# 067 — AR(1) drift diagnostics for `p_4_2__2_1` winner

Branch: `diagnostics/autocorr-ar1`. Started 2026-05-04.

## Why

Across 064/057/058/060/065/066 (309 evals), `autocorr_returns` (mean |ACF[1..20]|)
sits at +0.48–0.72, target band [-0.1, +0.20]. Real SPX daily ≈ 0.00.
This contradicts the "near random walk" assumption underpinning EcoMD as a
Langevin simulator and inflates `acf_squared_returns` and `dfa_hurst_abs_r`
through a drift artifact. Reviewer-2 attack: "your 5/11 is contaminated;
after AR(1) whitening real pass count drops".

## Three diagnostics

- **E2 (`thermo_params.{csv,md}`)**: extract post-training T_eff, γ_eff from
  all 50 064 checkpoints. Test "model cheated by suppressing T".
- **E3a (`ar1_residual_analysis.md`)**: analytical AR(1)-residual ACF,
  using existing inference_rank_0.json diagnostics. 200 realizations,
  no re-rollout needed.
- **E3b (`ar1_full_summary.md` + `full_eval/*.json`)**: re-run inference on
  selected seeds with raw returns saved, recompute all 11 facts on
  AR(1)-whitened residuals.

## Findings (so far)

### E2 — cheat hypothesis FALSIFIED

All 50 seeds kept thermodynamic parameters at their init values:

| param | init | mean post-train | range |
|---|---:|---:|---|
| T_eff | 0.05 | **0.0515** | [0.050, 0.054] |
| γ_eff | 1.00 | **0.980** | [0.96, 1.01] |
| noise_per_step σ | 0.0316 | **0.0324** | [0.032, 0.033] |

**0/50 seeds** suppressed noise to <50% of init. The autocorr=0.6 problem is
NOT due to T-cheating — it's structural. Per-step relaxation `γ·dt = 0.01`
puts the system in deeply underdamped regime (velocity memory time ~ 100 steps).

### E3a — autocorr structure is ~85% pure AR(1)

Across 200 realizations:
- mean ρ̂ (AR(1) coefficient) = **0.904**, median 0.935, max 0.991
- pre-whitening pass rate: 4.5%
- post-whitening pass rate: **94%**

ACF is approximately exponential ρ^k:
| lag | observed | rho^lag | excess (slow component) |
|---:|---:|---:|---:|
| 1 | +0.904 | +0.904 | 0.000 |
| 5 | +0.696 | +0.680 | +0.016 |
| 10 | +0.559 | +0.513 | +0.046 |
| 20 | +0.390 | +0.319 | +0.071 |

So returns are essentially AR(0.9) with a small additional slow-memory
component that grows at long lag (consistent with v3 regime GRU leftover).

### E3b — pending

If acf_squared_returns and dfa_hurst_abs_r drop below their pass bands after
AR(1) whitening, the pass count is fictively inflated. Estimate from theory
(pure AR(1) Gaussian innovations):
- acf_sq² post-whitening ≈ 0 (ε² is iid) → FAILS lower bound 0.15
- hurst_abs_r post-whitening ≈ 0.5 → FAILS lower bound 0.6

So predicted drop: from current ~5/11 to ~3/11 honest pass count.
E3b empirically tests this.

## Implications

1. **Paper A**: cannot honestly report "5/11 stylized facts pass" without
   companion AR(1)-residual column. Probably 3/11 honest.
2. **Architecture fix targets**:
   - Move from γ·dt = 0.01 (underdamped) to γ·dt ≥ 1 (overdamped). Either
     scale γ up 100× or dt down 100× (with force rescaling).
   - Add force-noise term ξ_force into the conservative force computation
     to break inter-step force correlation.
   - Increase w_autocorr_r from 0.5 to ~5–10 in loss; use Bartlett-corrected
     ACF estimator on a longer rollout horizon (per 057 rollout_reg, weight
     × horizon both matter).
3. **Quick experiment**: freeze (T, γ) and see if the structural problem
   persists. If yes, must restructure step function.
