# Continuous-distance score — 076_collective_price_30seed

## Per-cell mean |z| across 11 facts

| cell | n_seeds | mean_|z| | facts_in_band | best fact (lowest |z|) |
|---|---:|---:|---:|---|
| `collective_g1` | 30 | 0.61 | 2/11 | gain_loss_asymmetry |
| `collective_g10_inner5` | 30 | 3.37 | 2/11 | autocorr_returns |
| `collective_g10` | 30 | 14.25 | 2/11 | autocorr_returns |

## Per-fact best cell

| fact | best cell | model | empirical | |z| | in_band |
|---|---|---:|---:|---:|---:|
| autocorr_returns | `collective_g10_inner5` | +0.114 | +0.060 | 0.22 | ✅ |
| hill_tail_index | `collective_g1` | +89.312 | +2.673 | 0.49 | ❌ |
| gain_loss_asymmetry | `collective_g1` | -0.229 | -0.645 | 0.15 | ❌ |
| aggregational_gaussianity | `collective_g1` | +0.085 | +15.475 | 1.17 | ❌ |
| intermittency_fano | `collective_g1` | +17.116 | +7.544 | 0.67 | ✅ |
| acf_squared_returns | `collective_g10_inner5` | +0.073 | +0.221 | 0.81 | ❌ |
| conditional_kurtosis | `collective_g1` | +12.823 | +2.475 | 0.29 | ❌ |
| dfa_hurst_abs_r | `collective_g1` | +1.256 | +0.982 | 0.49 | ❌ |
| leverage_effect | `collective_g1` | +0.836 | -0.863 | 0.25 | ❌ |
| volume_volatility_corr | `collective_g1` | +0.618 | +1.000 | 0.93 | ✅ |
| zumbach_asymmetry | `collective_g1` | -0.033 | -0.050 | 0.21 | ❌ |
