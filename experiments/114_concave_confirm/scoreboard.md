# Score — 114_concave_confirm

Discovered 390 runs, 390 with eval, 2 rejected for numerical instability (388 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `btcusdt_baseline_seed5` | aggregational_gaussianity=1318.3 (>|1000.0|) | 3/11 |
| `eurusd_baseline_seed11` | aggregational_gaussianity=1257.0 (>|1000.0|) | 4/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `eurusd_concave_d045` | 30 | **5.33** | [4.87, 5.80] | 1.32 | 9 | 1 | 0 |
| `btcusdt_concave_d045` | 30 | **5.30** | [4.77, 5.80] | 1.44 | 9 | 1 | 0 |
| `gold_concave_d045` | 30 | **5.20** | [4.57, 5.83] | 1.81 | 9 | 3 | 0 |
| `ndx_concave_d050` | 30 | **5.13** | [4.57, 5.67] | 1.55 | 8 | 2 | 0 |
| `ndx_concave_d045` | 30 | **5.03** | [4.50, 5.57] | 1.50 | 8 | 2 | 0 |
| `btcusdt_concave_d050` | 30 | **5.00** | [4.43, 5.57] | 1.62 | 9 | 1 | 0 |
| `gold_concave_d050` | 30 | **5.00** | [4.33, 5.73] | 1.98 | 10 | 2 | 0 |
| `spx_concave_d045` | 30 | **4.83** | [4.40, 5.27] | 1.23 | 8 | 1 | 0 |
| `eurusd_concave_d050` | 30 | **4.73** | [4.13, 5.37] | 1.78 | 9 | 1 | 0 |
| `btcusdt_baseline` | 29 | **4.31** | [3.76, 4.86] | 1.49 | 7 | 0 | 1 |
| `eurusd_baseline` | 29 | **4.24** | [3.86, 4.62] | 1.09 | 6 | 0 | 1 |
| `gold_baseline` | 30 | **4.20** | [3.70, 4.70] | 1.40 | 7 | 0 | 0 |
| `ndx_baseline` | 30 | **4.17** | [3.63, 4.70] | 1.53 | 7 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `gold_concave_d050_seed23` | **10/11** |
| `btcusdt_concave_d045_seed11` | **9/11** |
| `btcusdt_concave_d050_seed14` | **9/11** |
| `eurusd_concave_d045_seed4` | **9/11** |
| `eurusd_concave_d050_seed14` | **9/11** |
| `gold_concave_d045_seed18` | **9/11** |
| `gold_concave_d050_seed18` | **9/11** |
| `gold_concave_d045_seed13` | **8/11** |
| `gold_concave_d045_seed24` | **8/11** |
| `ndx_concave_d045_seed28` | **8/11** |

