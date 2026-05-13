# Score — 088_pairs_and_confirmation

Discovered 460 runs, 460 with eval, 19 rejected for numerical instability (441 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `b3_k3_tau05_pure_seed27` | aggregational_gaussianity=3105.5 (>|1000.0|) | 3/11 |
| `btc_pair_AB_seed13` | conditional_kurtosis=136.4 (>|100.0|) | 4/11 |
| `btc_pair_AB_seed19` | conditional_kurtosis=258.3 (>|100.0|) | 5/11 |
| `btc_pair_AB_seed23` | conditional_kurtosis=440.0 (>|100.0|) | 6/11 |
| `btc_pair_AB_seed7` | conditional_kurtosis=116.1 (>|100.0|) | 5/11 |
| `btc_pair_LA_seed27` | aggregational_gaussianity=1296.3 (>|1000.0|) | 6/11 |
| `btc_pair_LA_seed29` | aggregational_gaussianity=1091.8 (>|1000.0|) | 5/11 |
| `conf_asymdrag_a06_seed35` | conditional_kurtosis=215.6 (>|100.0|) | 6/11 |
| `pair_AB_seed18` | conditional_kurtosis=149.6 (>|100.0|) | 4/11 |
| `pair_AB_seed19` | conditional_kurtosis=1387.6 (>|100.0|) | 4/11 |
| `pair_AM_seed16` | aggregational_gaussianity=1012.7 (>|1000.0|) | 2/11 |
| `pair_AM_seed8` | aggregational_gaussianity=2634.5 (>|1000.0|) | 3/11 |
| `pair_LA_seed1` | conditional_kurtosis=680.4 (>|100.0|) | 4/11 |
| `pair_LA_seed22` | aggregational_gaussianity=1650.3 (>|1000.0|) | 6/11 |
| `pair_LA_seed29` | aggregational_gaussianity=1129.4 (>|1000.0|) | 5/11 |
| `pair_LA_seed5` | conditional_kurtosis=598.5 (>|100.0|) | 6/11 |
| `pair_MB_seed27` | aggregational_gaussianity=1436.6 (>|1000.0|) | 3/11 |
| `triple_LAM_seed10` | aggregational_gaussianity=1374.0 (>|1000.0|) | 3/11 |
| `triple_LAM_seed12` | aggregational_gaussianity=1022.7 (>|1000.0|) | 7/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `pair_AB` | 28 | **5.18** | [4.54, 5.79] | 1.68 | 8 | 2 | 2 |
| `btc_pair_LA` | 28 | **5.00** | [4.50, 5.54] | 1.39 | 8 | 1 | 2 |
| `pair_LA` | 26 | **4.96** | [4.27, 5.65] | 1.87 | 9 | 2 | 4 |
| `conf_b3_k3_pure` | 50 | **4.94** | [4.60, 5.28] | 1.24 | 8 | 1 | 0 |
| `conf_asymdrag_a06` | 49 | **4.94** | [4.37, 5.49] | 2.08 | 9 | 4 | 1 |
| `b3_k3_tau05_pure` | 29 | **4.93** | [4.38, 5.48] | 1.51 | 8 | 2 | 1 |
| `triple_LAM` | 28 | **4.79** | [4.21, 5.32] | 1.55 | 7 | 0 | 2 |
| `b3_k3_tau15_pure` | 30 | **4.63** | [4.13, 5.13] | 1.40 | 8 | 1 | 0 |
| `pair_LM` | 30 | **4.60** | [4.13, 5.07] | 1.38 | 7 | 0 | 0 |
| `btc_pair_AB` | 26 | **4.58** | [4.08, 5.04] | 1.27 | 6 | 0 | 4 |
| `pair_AM` | 28 | **4.57** | [3.93, 5.21] | 1.83 | 9 | 1 | 2 |
| `b3_k4_pure` | 30 | **4.43** | [4.00, 4.87] | 1.22 | 7 | 0 | 0 |
| `pair_MB` | 29 | **4.38** | [3.93, 4.86] | 1.29 | 7 | 0 | 1 |
| `pair_LB` | 30 | **4.30** | [3.87, 4.73] | 1.24 | 6 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `conf_asymdrag_a06_seed14` | **9/11** |
| `conf_asymdrag_a06_seed2` | **9/11** |
| `pair_AM_seed2` | **9/11** |
| `pair_LA_seed21` | **9/11** |
| `b3_k3_tau05_pure_seed19` | **8/11** |
| `b3_k3_tau05_pure_seed2` | **8/11** |
| `b3_k3_tau15_pure_seed0` | **8/11** |
| `btc_pair_LA_seed22` | **8/11** |
| `conf_asymdrag_a06_seed10` | **8/11** |
| `conf_asymdrag_a06_seed19` | **8/11** |

