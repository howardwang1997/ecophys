# Continuous-distance score — 069_gamma_damping_30seed

## Per-cell mean |z| across 11 facts

| cell | n_seeds | mean_|z| | facts_in_band | best fact (lowest |z|) |
|---|---:|---:|---:|---|
| `T05_g20` | 30 | 1.29 | 6/11 | leverage_effect |
| `T05_g10` | 30 | 1.29 | 6/11 | gain_loss_asymmetry |
| `T05_g15` | 30 | 1.44 | 5/11 | acf_squared_returns |
| `T05_g5` | 30 | 1.54 | 4/11 | leverage_effect |
| `T05_g3` | 30 | 2.09 | 4/11 | gain_loss_asymmetry |

## Per-fact best cell

| fact | best cell | model | empirical | |z| | in_band |
|---|---|---:|---:|---:|---:|
| autocorr_returns | `T05_g20` | +0.370 | +0.060 | 1.15 | ❌ |
| hill_tail_index | `T05_g10` | +1.776 | +2.673 | 0.36 | ❌ |
| gain_loss_asymmetry | `T05_g10` | -2.199 | -0.645 | 0.10 | ❌ |
| aggregational_gaussianity | `T05_g20` | +527.689 | +15.475 | 1.10 | ❌ |
| intermittency_fano | `T05_g10` | +33.649 | +7.544 | 4.27 | ✅ |
| acf_squared_returns | `T05_g15` | +0.221 | +0.221 | 0.01 | ✅ |
| conditional_kurtosis | `T05_g5` | +3.704 | +2.475 | 0.08 | ❌ |
| dfa_hurst_abs_r | `T05_g5` | +0.944 | +0.982 | 0.13 | ❌ |
| leverage_effect | `T05_g5` | -0.812 | -0.863 | 0.01 | ✅ |
| volume_volatility_corr | `T05_g3` | +0.528 | +1.000 | 1.02 | ✅ |
| zumbach_asymmetry | `T05_g20` | -0.073 | -0.050 | 0.26 | ❌ |
