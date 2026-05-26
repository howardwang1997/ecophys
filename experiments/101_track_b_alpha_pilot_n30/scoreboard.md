# Score — 101_track_b_alpha_pilot_n30

Discovered 750 runs, 750 with eval, 24 rejected for numerical instability (726 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `baseline_v3_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `baseline_v3_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `ha_K04_b004_u04_seed18` | aggregational_gaussianity=1065.0 (>|1000.0|) | 3/11 |
| `ha_K04_b004_u04_seed7` | aggregational_gaussianity=1853.8 (>|1000.0|) | 3/11 |
| `ha_K04_b008_u04_seed19` | aggregational_gaussianity=1062.1 (>|1000.0|) | 2/11 |
| `ha_K04_b008_u04_seed27` | aggregational_gaussianity=1534.0 (>|1000.0|) | 3/11 |
| `ha_K04_b008_u08_seed7` | aggregational_gaussianity=1025.6 (>|1000.0|) | 3/11 |
| `ha_K04_b016_u04_seed27` | aggregational_gaussianity=1137.3 (>|1000.0|) | 2/11 |
| `ha_K04_b032_u04_seed18` | aggregational_gaussianity=1140.3 (>|1000.0|) | 3/11 |
| `ha_K04_b032_u04_seed19` | aggregational_gaussianity=1429.6 (>|1000.0|) | 3/11 |
| `ha_K04_b032_u08_seed0` | aggregational_gaussianity=1366.2 (>|1000.0|) | 3/11 |
| `ha_K06_b004_u08_seed18` | aggregational_gaussianity=1246.4 (>|1000.0|) | 4/11 |
| `ha_K06_b004_u08_seed19` | aggregational_gaussianity=1272.7 (>|1000.0|) | 4/11 |
| `ha_K06_b008_u04_seed27` | aggregational_gaussianity=1094.9 (>|1000.0|) | 3/11 |
| `ha_K06_b008_u08_seed19` | aggregational_gaussianity=1930.8 (>|1000.0|) | 3/11 |
| `ha_K06_b008_u08_seed27` | aggregational_gaussianity=1019.1 (>|1000.0|) | 3/11 |
| `ha_K06_b016_u04_seed0` | aggregational_gaussianity=1301.6 (>|1000.0|) | 3/11 |
| `ha_K06_b016_u04_seed22` | aggregational_gaussianity=1185.8 (>|1000.0|) | 3/11 |
| `ha_K06_b016_u04_seed27` | aggregational_gaussianity=1248.3 (>|1000.0|) | 3/11 |
| `ha_K08_b004_u04_seed7` | aggregational_gaussianity=1499.7 (>|1000.0|) | 3/11 |
| `ha_K08_b008_u04_seed27` | aggregational_gaussianity=1102.1 (>|1000.0|) | 3/11 |
| `ha_K08_b008_u08_seed19` | aggregational_gaussianity=1041.5 (>|1000.0|) | 4/11 |
| `ha_K08_b016_u04_seed24` | aggregational_gaussianity=1455.5 (>|1000.0|) | 3/11 |
| `ha_K08_b032_u08_seed0` | aggregational_gaussianity=1046.2 (>|1000.0|) | 2/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `ha_K06_b016_u08` | 30 | **5.10** | [4.63, 5.57] | 1.35 | 7 | 0 | 0 |
| `ha_K04_b008_u04` | 28 | **5.07** | [4.54, 5.64] | 1.56 | 9 | 2 | 2 |
| `ha_K08_b008_u04` | 29 | **5.07** | [4.59, 5.52] | 1.28 | 7 | 0 | 1 |
| `ha_K08_b016_u08` | 30 | **5.07** | [4.47, 5.73] | 1.84 | 10 | 3 | 0 |
| `ha_K06_b004_u08` | 28 | **5.00** | [4.46, 5.54] | 1.49 | 8 | 1 | 2 |
| `ha_K04_b016_u08` | 30 | **4.97** | [4.40, 5.60] | 1.71 | 11 | 1 | 0 |
| `ha_K04_b004_u04` | 28 | **4.93** | [4.39, 5.43] | 1.41 | 8 | 1 | 2 |
| `ha_K06_b032_u08` | 30 | **4.90** | [4.43, 5.33] | 1.24 | 7 | 0 | 0 |
| `ha_K04_b008_u08` | 29 | **4.90** | [4.38, 5.41] | 1.42 | 8 | 1 | 1 |
| `ha_K04_b004_u08` | 30 | **4.87** | [4.30, 5.40] | 1.57 | 8 | 1 | 0 |
| `ha_K06_b004_u04` | 30 | **4.80** | [4.37, 5.23] | 1.27 | 7 | 0 | 0 |
| `ha_K06_b008_u04` | 29 | **4.79** | [4.24, 5.34] | 1.57 | 8 | 1 | 1 |
| `ha_K06_b016_u04` | 27 | **4.78** | [4.41, 5.15] | 1.01 | 7 | 0 | 3 |
| `ha_K04_b016_u04` | 29 | **4.76** | [4.34, 5.21] | 1.21 | 8 | 1 | 1 |
| `ha_K06_b008_u08` | 28 | **4.71** | [4.21, 5.21] | 1.36 | 7 | 0 | 2 |
| `baseline_v3` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `ha_K04_b032_u04` | 28 | **4.64** | [4.11, 5.21] | 1.54 | 7 | 0 | 2 |
| `ha_K08_b008_u08` | 29 | **4.48** | [4.03, 4.97] | 1.33 | 8 | 1 | 1 |
| `ha_K04_b032_u08` | 29 | **4.45** | [3.86, 5.03] | 1.68 | 7 | 0 | 1 |
| `ha_K08_b016_u04` | 29 | **4.45** | [3.97, 4.93] | 1.33 | 7 | 0 | 1 |
| `ha_K08_b004_u08` | 30 | **4.33** | [3.87, 4.80] | 1.35 | 7 | 0 | 0 |
| `ha_K08_b004_u04` | 29 | **4.31** | [3.93, 4.69] | 1.07 | 7 | 0 | 1 |
| `ha_K08_b032_u04` | 30 | **4.30** | [3.87, 4.73] | 1.24 | 7 | 0 | 0 |
| `ha_K08_b032_u08` | 29 | **4.28** | [3.79, 4.76] | 1.36 | 7 | 0 | 1 |
| `ha_K06_b032_u04` | 30 | **4.23** | [3.77, 4.70] | 1.33 | 7 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `ha_K04_b016_u08_seed13` | **11/11** |
| `ha_K08_b016_u08_seed21` | **10/11** |
| `ha_K04_b008_u04_seed6` | **9/11** |
| `ha_K04_b004_u04_seed2` | **8/11** |
| `ha_K04_b004_u08_seed8` | **8/11** |
| `ha_K04_b008_u04_seed10` | **8/11** |
| `ha_K04_b008_u08_seed17` | **8/11** |
| `ha_K04_b016_u04_seed6` | **8/11** |
| `ha_K06_b004_u08_seed3` | **8/11** |
| `ha_K06_b008_u04_seed6` | **8/11** |

