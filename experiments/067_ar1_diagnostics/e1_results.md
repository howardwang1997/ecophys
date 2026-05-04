# E1 results — frozen (T, γ) at 4 cells, 6 seeds each

## Cell-level summary

| cell | (T, γ) | γ·dt | n | mean pass | ac_r | acf_sq | Hurst | leverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `freezeTG_T05_g1` (sanity) | (0.05, 1) | 0.01 | 6 | 3.50 | +0.668 | +0.522 | +1.345 | +0.065 |
| `freezeTG_T05_g10` | (0.05, 10) | 0.10 | 6 | 4.00 | **+0.338** | +0.216 | **+0.728** ✓ | **-0.226** ✓ sign |
| `freezeTG_T05_g100` | (0.05, 100) | 1.00 | 6 | 2.83 | +0.476 | +0.198 | +0.859 | +0.255 |
| `freezeTG_T20_g1` (hot) | (0.20, 1) | 0.01 | 6 | **5.50** | +0.645 | +0.369 | +1.211 | +0.829 |

Reference: 064 unconstrained (learnable T,γ): n=50, mean 4.96, ac_r +0.58, Hurst 1.12.

## Per-fact pass rate

| fact | T05_g1 | T05_g10 | T05_g100 | T20_g1 |
|---|---:|---:|---:|---:|
| autocorr_returns | 0/6 | 0/6 | **1/6** | 0/6 |
| hill_tail_index | 0/6 | 0/6 | 1/6 | 0/6 |
| gain_loss_asymmetry | 2/6 | 3/6 | 1/6 | 2/6 |
| aggregational_gaussianity | 3/6 | 2/6 | 1/6 | 5/6 |
| intermittency_fano | 6/6 | 6/6 | 6/6 | 6/6 |
| acf_squared_returns | 3/6 | 3/6 | 1/6 | **6/6** |
| conditional_kurtosis | 4/6 | 2/6 | 3/6 | **6/6** |
| dfa_hurst_abs_r | 1/6 | **3/6** | 0/6 | 0/6 |
| leverage_effect | 0/6 | **3/6** | 1/6 | 2/6 |
| volume_volatility_corr | 1/6 | 2/6 | 1/6 | 2/6 |
| zumbach_asymmetry | 1/6 | 0/6 | 1/6 | 4/6 |

## What this tells us

**(1) `T05_g10` (γ·dt = 0.1) is the only cell that genuinely fixes the dynamics.**
- ac_r drops from 0.58 (unconstrained) → 0.67 (frozen at init) → **0.34** (10× damping).
- Hurst moves from non-physical 1.12 → 0.73 (in band [0.6, 0.9]) for first time.
- leverage flips sign from spurious + to correct − (3/6 pass leverage band).
- BUT mean pass count is only 4.0/11 — the model loses some volatility-clustering inflation.

**(2) `T20_g1` (4× T) wins on raw score (5.5) but does NOT fix dynamics.**
- ac_r unchanged at 0.65; Hurst still 1.21 (non-physical).
- The score gain is from acf_sq² 6/6 and cond_kurt 6/6 — both AR(1)-baseline-inflated facts.
- This is exactly the AR(1) artifact pattern: more T noise → bigger r² variance → "more vol clustering" but it's drift baseline.

**(3) `T05_g100` (γ·dt = 1.0, fully overdamped) breaks the model.**
- Per-step relaxation kills drift; model becomes near-static. agg_gaussianity blows up to 1500 (target 10–200).
- 1 seed (seed3) hit ac_r = 0.037 (a true white noise) — but the rest of the dynamics broke.
- Suggests: full overdamped at γ=100 is too aggressive; intermediate γ ~ 3–20 is the sweet spot.

**(4) Sanity check: just freezing (T05_g1) drops score from 4.96 → 3.50.**
- The unconstrained model used the small ~3% wiggle in T/γ to get an extra ~1.5 facts.
- Confirms the T/γ DID matter even though the absolute movement was tiny.

## Implications

- **The 4.96/11 baseline is inflated by ~1 fact of AR(1)-driven artifact** (acf_sq² and Hurst riding on drift).
- **The honest "physically valid" pass rate is closer to 3-4/11** (T05_g10 cell 4.0, plus losing 1 to lottery on n=6).
- **Hurst > 1 in all 064 seeds was a red flag.** Only T05_g10 produces physical Hurst.
- **The right architectural fix is intermediate damping** (γ ≈ 3–20), not the maximum-noise hack of T20_g1.

## Next experiments

1. **T05_g{3,5,20} sweep × 30 seeds each** to find the sweet spot of damping.
2. **T20_g10** (combine 4× T with 10× damping) — could regain the volatility-clustering passes while keeping dynamics honest.
3. **Run E3b** (saved trajectories on all 50 064 seeds) to get the post-AR(1)-residual baseline empirically. With that, we can write the paper as "AR(1)-residual pass count = X/11" honestly.
