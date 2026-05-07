# Continuous-distance score — 074_clean_physics_ablation

## Per-cell mean |z| across 11 facts

| cell | n_seeds | mean_|z| | facts_in_band | best fact (lowest |z|) |
|---|---:|---:|---:|---|
| `clean_g10_no_LN` | 26 | 0.84 | 2/11 | leverage_effect |
| `clean_g10_minimal` | 30 | 1.24 | 2/11 | zumbach_asymmetry |
| `clean_g10_no_gpair` | 28 | 1.45 | 5/11 | leverage_effect |
| `clean_g10_baseline` | 30 | 1.51 | 6/11 | gain_loss_asymmetry |
| `clean_g10_no_twopop` | 30 | 10.46 | 5/11 | acf_squared_returns |

## Per-fact best cell

| fact | best cell | model | empirical | |z| | in_band |
|---|---|---:|---:|---:|---:|
| autocorr_returns | `clean_g10_no_twopop` | +0.287 | +0.060 | 1.50 | ❌ |
| hill_tail_index | `clean_g10_minimal` | +144.929 | +2.673 | 0.41 | ❌ |
| gain_loss_asymmetry | `clean_g10_minimal` | -0.236 | -0.645 | 0.07 | ❌ |
| aggregational_gaussianity | `clean_g10_minimal` | +30.095 | +15.475 | 0.34 | ✅ |
| intermittency_fano | `clean_g10_no_LN` | +14.840 | +7.544 | 0.62 | ✅ |
| acf_squared_returns | `clean_g10_no_twopop` | +0.200 | +0.221 | 0.17 | ✅ |
| conditional_kurtosis | `clean_g10_no_LN` | +122.691 | +2.475 | 0.22 | ❌ |
| dfa_hurst_abs_r | `clean_g10_no_gpair` | +0.957 | +0.982 | 0.10 | ❌ |
| leverage_effect | `clean_g10_no_gpair` | -0.936 | -0.863 | 0.02 | ✅ |
| volume_volatility_corr | `clean_g10_minimal` | +0.883 | +1.000 | 0.35 | ❌ |
| zumbach_asymmetry | `clean_g10_minimal` | -0.045 | -0.050 | 0.04 | ❌ |
