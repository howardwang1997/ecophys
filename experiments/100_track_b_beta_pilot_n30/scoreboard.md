# Score — 100_track_b_beta_pilot_n30

Discovered 930 runs, 930 with eval, 19 rejected for numerical instability (911 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `baseline_v3_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `baseline_v3_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `bb_p010_s150_seed0` | aggregational_gaussianity=1113.5 (>|1000.0|) | 5/11 |
| `bb_p010_s200_seed27` | aggregational_gaussianity=1154.5 (>|1000.0|) | 4/11 |
| `bb_p015_s200_seed16` | aggregational_gaussianity=1020.2 (>|1000.0|) | 6/11 |
| `bb_p015_s250_seed21` | aggregational_gaussianity=2048.7 (>|1000.0|) | 3/11 |
| `bb_p015_s250_seed7` | aggregational_gaussianity=1025.2 (>|1000.0|) | 3/11 |
| `bb_p020_s125_seed19` | aggregational_gaussianity=1044.8 (>|1000.0|) | 2/11 |
| `bb_p020_s125_seed22` | aggregational_gaussianity=1416.3 (>|1000.0|) | 3/11 |
| `bb_p025_s150_seed0` | aggregational_gaussianity=1424.6 (>|1000.0|) | 4/11 |
| `bb_p025_s200_seed0` | aggregational_gaussianity=1817.4 (>|1000.0|) | 4/11 |
| `bb_p025_s200_seed22` | aggregational_gaussianity=1176.7 (>|1000.0|) | 4/11 |
| `bb_p030_s125_seed0` | aggregational_gaussianity=2374.9 (>|1000.0|) | 3/11 |
| `bb_p030_s125_seed21` | aggregational_gaussianity=1030.0 (>|1000.0|) | 2/11 |
| `bb_p040_s125_seed0` | aggregational_gaussianity=1697.8 (>|1000.0|) | 4/11 |
| `bb_p040_s175_seed7` | aggregational_gaussianity=1098.2 (>|1000.0|) | 3/11 |
| `bb_p040_s200_seed0` | aggregational_gaussianity=1256.1 (>|1000.0|) | 4/11 |
| `bb_p040_s200_seed22` | aggregational_gaussianity=1005.4 (>|1000.0|) | 4/11 |
| `bb_p040_s250_seed22` | aggregational_gaussianity=1201.0 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `bb_p010_s250` | 30 | **5.10** | [4.57, 5.63] | 1.52 | 8 | 1 | 0 |
| `bb_p015_s125` | 30 | **4.83** | [4.27, 5.40] | 1.64 | 8 | 1 | 0 |
| `bb_p020_s250` | 30 | **4.83** | [4.43, 5.23] | 1.15 | 7 | 0 | 0 |
| `bb_p030_s200` | 30 | **4.83** | [4.37, 5.30] | 1.34 | 7 | 0 | 0 |
| `bb_p010_s175` | 30 | **4.80** | [4.40, 5.23] | 1.19 | 7 | 0 | 0 |
| `bb_p030_s250` | 30 | **4.80** | [4.20, 5.37] | 1.63 | 7 | 0 | 0 |
| `bb_p015_s175` | 30 | **4.77** | [4.27, 5.27] | 1.45 | 8 | 1 | 0 |
| `bb_p030_s150` | 30 | **4.77** | [4.23, 5.30] | 1.52 | 8 | 1 | 0 |
| `bb_p040_s250` | 29 | **4.76** | [4.28, 5.28] | 1.41 | 8 | 1 | 1 |
| `bb_p030_s125` | 28 | **4.75** | [4.18, 5.29] | 1.51 | 7 | 0 | 2 |
| `bb_p030_s175` | 30 | **4.70** | [4.20, 5.20] | 1.42 | 8 | 1 | 0 |
| `bb_p025_s250` | 30 | **4.67** | [4.10, 5.20] | 1.56 | 7 | 0 | 0 |
| `baseline_v3` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `bb_p025_s200` | 28 | **4.64** | [4.21, 5.07] | 1.22 | 7 | 0 | 2 |
| `bb_p040_s150` | 30 | **4.63** | [4.27, 5.03] | 1.13 | 8 | 1 | 0 |
| `bb_p020_s175` | 30 | **4.57** | [4.07, 5.07] | 1.43 | 8 | 1 | 0 |
| `bb_p015_s200` | 29 | **4.55** | [4.07, 5.00] | 1.33 | 7 | 0 | 1 |
| `bb_p010_s125` | 30 | **4.53** | [4.10, 5.00] | 1.25 | 8 | 1 | 0 |
| `bb_p015_s150` | 30 | **4.53** | [4.07, 5.00] | 1.31 | 7 | 0 | 0 |
| `bb_p020_s200` | 30 | **4.53** | [4.00, 5.03] | 1.46 | 7 | 0 | 0 |
| `bb_p015_s250` | 28 | **4.50** | [4.07, 4.93] | 1.20 | 7 | 0 | 2 |
| `bb_p025_s125` | 30 | **4.50** | [4.00, 5.00] | 1.43 | 7 | 0 | 0 |
| `bb_p020_s150` | 30 | **4.47** | [3.97, 4.97] | 1.41 | 7 | 0 | 0 |
| `bb_p020_s125` | 28 | **4.46** | [4.04, 4.89] | 1.20 | 7 | 0 | 2 |
| `bb_p025_s175` | 30 | **4.43** | [3.97, 4.93] | 1.36 | 8 | 1 | 0 |
| `bb_p010_s200` | 29 | **4.41** | [3.90, 4.97] | 1.55 | 8 | 1 | 1 |
| `bb_p040_s175` | 29 | **4.38** | [3.79, 4.93] | 1.57 | 7 | 0 | 1 |
| `bb_p040_s125` | 29 | **4.31** | [3.69, 4.93] | 1.75 | 7 | 0 | 1 |
| `bb_p040_s200` | 28 | **4.29** | [3.79, 4.82] | 1.41 | 7 | 0 | 2 |
| `bb_p010_s150` | 29 | **4.24** | [3.83, 4.66] | 1.18 | 7 | 0 | 1 |
| `bb_p025_s150` | 29 | **3.93** | [3.55, 4.34] | 1.13 | 6 | 0 | 1 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `bb_p010_s125_seed29` | **8/11** |
| `bb_p010_s200_seed26` | **8/11** |
| `bb_p010_s250_seed2` | **8/11** |
| `bb_p015_s125_seed8` | **8/11** |
| `bb_p015_s175_seed9` | **8/11** |
| `bb_p020_s175_seed1` | **8/11** |
| `bb_p025_s175_seed20` | **8/11** |
| `bb_p030_s150_seed3` | **8/11** |
| `bb_p030_s175_seed2` | **8/11** |
| `bb_p040_s150_seed25` | **8/11** |

