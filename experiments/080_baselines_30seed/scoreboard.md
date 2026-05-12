# Score — 080_baselines_30seed

Discovered 120 runs, 120 with eval, 24 rejected for numerical instability (96 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `ar1_sv_seed0` | conditional_kurtosis=134.5 (>|100.0|) | 1/11 |
| `ar1_sv_seed10` | conditional_kurtosis=104.6 (>|100.0|) | 2/11 |
| `ar1_sv_seed11` | conditional_kurtosis=458.5 (>|100.0|) | 2/11 |
| `ar1_sv_seed12` | conditional_kurtosis=215.7 (>|100.0|) | 3/11 |
| `ar1_sv_seed13` | conditional_kurtosis=302.2 (>|100.0|) | 2/11 |
| `ar1_sv_seed14` | conditional_kurtosis=235.7 (>|100.0|) | 1/11 |
| `ar1_sv_seed15` | conditional_kurtosis=129.2 (>|100.0|) | 1/11 |
| `ar1_sv_seed16` | conditional_kurtosis=133.0 (>|100.0|) | 3/11 |
| `ar1_sv_seed17` | conditional_kurtosis=126.3 (>|100.0|) | 3/11 |
| `ar1_sv_seed18` | conditional_kurtosis=256.8 (>|100.0|) | 1/11 |
| `ar1_sv_seed19` | conditional_kurtosis=134.5 (>|100.0|) | 2/11 |
| `ar1_sv_seed2` | conditional_kurtosis=270.6 (>|100.0|) | 3/11 |
| `ar1_sv_seed20` | conditional_kurtosis=151.2 (>|100.0|) | 4/11 |
| `ar1_sv_seed21` | conditional_kurtosis=140.7 (>|100.0|) | 2/11 |
| `ar1_sv_seed23` | conditional_kurtosis=101.7 (>|100.0|) | 2/11 |
| `ar1_sv_seed25` | conditional_kurtosis=159.0 (>|100.0|) | 4/11 |
| `ar1_sv_seed26` | conditional_kurtosis=310.0 (>|100.0|) | 2/11 |
| `ar1_sv_seed27` | conditional_kurtosis=110.7 (>|100.0|) | 3/11 |
| `ar1_sv_seed28` | conditional_kurtosis=230.2 (>|100.0|) | 2/11 |
| `ar1_sv_seed29` | conditional_kurtosis=102.5 (>|100.0|) | 2/11 |
| `ar1_sv_seed6` | conditional_kurtosis=582.2 (>|100.0|) | 2/11 |
| `ar1_sv_seed7` | conditional_kurtosis=125.1 (>|100.0|) | 1/11 |
| `ar1_sv_seed8` | conditional_kurtosis=107.7 (>|100.0|) | 3/11 |
| `ar1_sv_seed9` | conditional_kurtosis=133.7 (>|100.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `garch` | 30 | **4.73** | [4.40, 5.07] | 0.98 | 6 | 0 | 0 |
| `gbm` | 30 | **2.50** | [2.33, 2.67] | 0.51 | 3 | 0 | 0 |
| `ar1_sv` | 6 | **2.33** | [2.00, 2.67] | 0.52 | 3 | 0 | 24 |
| `lux_marchesi` | 30 | **2.17** | [2.03, 2.30] | 0.38 | 3 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `garch_seed12` | **6/11** |
| `garch_seed14` | **6/11** |
| `garch_seed17` | **6/11** |
| `garch_seed21` | **6/11** |
| `garch_seed24` | **6/11** |
| `garch_seed25` | **6/11** |
| `garch_seed27` | **6/11** |
| `garch_seed1` | **5/11** |
| `garch_seed11` | **5/11** |
| `garch_seed15` | **5/11** |

