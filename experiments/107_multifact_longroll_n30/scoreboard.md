# Score — 107_multifact_longroll_n30

Discovered 90 runs, 90 with eval, 22 rejected for numerical instability (68 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `baseline_v3_seed13` | aggregational_gaussianity=1619.2 (>|1000.0|) | 3/11 |
| `baseline_v3_seed19` | aggregational_gaussianity=1320.9 (>|1000.0|) | 4/11 |
| `baseline_v3_seed20` | aggregational_gaussianity=1165.0 (>|1000.0|) | 6/11 |
| `baseline_v3_seed21` | aggregational_gaussianity=1867.6 (>|1000.0|) | 3/11 |
| `baseline_v3_seed23` | aggregational_gaussianity=1028.3 (>|1000.0|) | 3/11 |
| `baseline_v3_seed28` | aggregational_gaussianity=1052.6 (>|1000.0|) | 3/11 |
| `baseline_v3_seed3` | aggregational_gaussianity=1261.4 (>|1000.0|) | 3/11 |
| `baseline_v3_seed7` | aggregational_gaussianity=1703.9 (>|1000.0|) | 4/11 |
| `longroll_moments_seed11` | aggregational_gaussianity=1238.2 (>|1000.0|) | 4/11 |
| `longroll_moments_seed12` | aggregational_gaussianity=1416.7 (>|1000.0|) | 5/11 |
| `longroll_moments_seed13` | aggregational_gaussianity=1060.0 (>|1000.0|) | 3/11 |
| `longroll_moments_seed14` | aggregational_gaussianity=1446.0 (>|1000.0|) | 4/11 |
| `longroll_moments_seed15` | aggregational_gaussianity=1230.9 (>|1000.0|) | 4/11 |
| `longroll_moments_seed16` | aggregational_gaussianity=1639.6 (>|1000.0|) | 5/11 |
| `longroll_moments_seed23` | aggregational_gaussianity=1322.2 (>|1000.0|) | 5/11 |
| `longroll_moments_seed27` | aggregational_gaussianity=1283.8 (>|1000.0|) | 5/11 |
| `longroll_moments_seed3` | aggregational_gaussianity=1227.7 (>|1000.0|) | 5/11 |
| `longroll_moments_seed7` | aggregational_gaussianity=1461.9 (>|1000.0|) | 4/11 |
| `mf_all_mse_longroll_seed15` | aggregational_gaussianity=2281.2 (>|1000.0|) | 4/11 |
| `mf_all_mse_longroll_seed17` | aggregational_gaussianity=1494.4 (>|1000.0|) | 5/11 |
| `mf_all_mse_longroll_seed20` | aggregational_gaussianity=2507.2 (>|1000.0|) | 3/11 |
| `mf_all_mse_longroll_seed22` | aggregational_gaussianity=1051.8 (>|1000.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `mf_all_mse_longroll` | 26 | **4.27** | [3.46, 5.08] | 2.11 | 8 | 1 | 4 |
| `baseline_v3` | 22 | **4.14** | [3.50, 4.86] | 1.70 | 8 | 1 | 8 |
| `longroll_moments` | 20 | **4.05** | [3.50, 4.65] | 1.36 | 8 | 1 | 10 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `baseline_v3_seed10` | **8/11** |
| `longroll_moments_seed1` | **8/11** |
| `mf_all_mse_longroll_seed24` | **8/11** |
| `baseline_v3_seed24` | **7/11** |
| `mf_all_mse_longroll_seed21` | **7/11** |
| `mf_all_mse_longroll_seed26` | **7/11** |
| `mf_all_mse_longroll_seed28` | **7/11** |
| `mf_all_mse_longroll_seed4` | **7/11** |
| `baseline_v3_seed15` | **6/11** |
| `baseline_v3_seed2` | **6/11** |

