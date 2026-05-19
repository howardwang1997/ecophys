# Score — 096_all_pairs_30seed

Discovered 690 runs, 690 with eval, 26 rejected for numerical instability (664 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `pair_ar1c_memk_seed1` | conditional_kurtosis=137.9 (>|100.0|) | 4/11 |
| `pair_ar1c_pl_seed15` | conditional_kurtosis=117.2 (>|100.0|) | 4/11 |
| `pair_asym_ar1c_seed0` | conditional_kurtosis=684.4 (>|100.0|) | 4/11 |
| `pair_asym_ar1c_seed1` | conditional_kurtosis=1000.0 (>|100.0|) | 4/11 |
| `pair_asym_levy_seed12` | aggregational_gaussianity=2222.3 (>|1000.0|) | 5/11 |
| `pair_asym_levy_seed17` | conditional_kurtosis=665.3 (>|100.0|) | 5/11 |
| `pair_asym_levy_seed4` | aggregational_gaussianity=1338.8 (>|1000.0|) | 5/11 |
| `pair_asym_levy_seed6` | conditional_kurtosis=105.7 (>|100.0|) | 5/11 |
| `pair_asym_memk_seed16` | aggregational_gaussianity=1027.4 (>|1000.0|) | 2/11 |
| `pair_asym_memk_seed8` | aggregational_gaussianity=2650.5 (>|1000.0|) | 3/11 |
| `pair_asym_ms_seed1` | conditional_kurtosis=227.8 (>|100.0|) | 4/11 |
| `pair_asym_ms_seed12` | conditional_kurtosis=238.4 (>|100.0|) | 5/11 |
| `pair_asym_ms_seed17` | aggregational_gaussianity=1016.4 (>|1000.0|) | 5/11 |
| `pair_b3_memk_seed27` | aggregational_gaussianity=1435.0 (>|1000.0|) | 3/11 |
| `pair_b3_pl_seed0` | aggregational_gaussianity=1157.8 (>|1000.0|) | 5/11 |
| `pair_b3_pl_seed27` | aggregational_gaussianity=1073.5 (>|1000.0|) | 4/11 |
| `pair_levy_memk_seed18` | aggregational_gaussianity=1061.8 (>|1000.0|) | 3/11 |
| `pair_levy_ms_seed0` | aggregational_gaussianity=1090.3 (>|1000.0|) | 3/11 |
| `pair_levy_ms_seed16` | aggregational_gaussianity=2490.2 (>|1000.0|) | 3/11 |
| `pair_levy_ms_seed7` | aggregational_gaussianity=1182.3 (>|1000.0|) | 3/11 |
| `pair_levy_pl_seed5` | aggregational_gaussianity=1018.5 (>|1000.0|) | 3/11 |
| `pair_zumdn_levy_seed16` | aggregational_gaussianity=1359.2 (>|1000.0|) | 4/11 |
| `pair_zumdn_memk_seed18` | aggregational_gaussianity=1025.5 (>|1000.0|) | 6/11 |
| `pair_zumdn_ms_seed1` | conditional_kurtosis=191.2 (>|100.0|) | 8/11 |
| `pair_zumdn_ms_seed3` | conditional_kurtosis=129.3 (>|100.0|) | 4/11 |
| `pair_zumdn_pl_seed16` | aggregational_gaussianity=1400.6 (>|1000.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `pair_asym_ms` | 27 | **5.33** | [4.78, 5.89] | 1.49 | 8 | 1 | 3 |
| `pair_zumdn_ms` | 28 | **5.29** | [4.75, 5.79] | 1.41 | 8 | 1 | 2 |
| `pair_ar1c_levy` | 30 | **4.97** | [4.50, 5.43] | 1.35 | 7 | 0 | 0 |
| `pair_b3_ms` | 30 | **4.97** | [4.50, 5.43] | 1.35 | 7 | 0 | 0 |
| `pair_b3_levy` | 30 | **4.90** | [4.37, 5.43] | 1.52 | 8 | 1 | 0 |
| `pair_zumdn_pl` | 29 | **4.86** | [4.48, 5.28] | 1.13 | 7 | 0 | 1 |
| `pair_zumdn_levy` | 29 | **4.83** | [4.24, 5.41] | 1.65 | 9 | 2 | 1 |
| `pair_zumdn_memk` | 29 | **4.83** | [4.14, 5.48] | 1.85 | 8 | 1 | 1 |
| `pair_asym_levy` | 26 | **4.81** | [4.23, 5.35] | 1.50 | 7 | 0 | 4 |
| `pair_levy_ms` | 27 | **4.78** | [4.22, 5.37] | 1.53 | 9 | 2 | 3 |
| `pair_pl_ms` | 30 | **4.77** | [4.37, 5.20] | 1.19 | 7 | 0 | 0 |
| `pair_memk_ms` | 30 | **4.67** | [4.20, 5.13] | 1.35 | 8 | 1 | 0 |
| `pair_ar1c_memk` | 29 | **4.66** | [4.10, 5.14] | 1.45 | 7 | 0 | 1 |
| `pair_levy_memk` | 29 | **4.59** | [4.10, 5.07] | 1.40 | 7 | 0 | 1 |
| `pair_asym_memk` | 28 | **4.57** | [3.89, 5.25] | 1.85 | 9 | 1 | 2 |
| `pair_levy_pl` | 29 | **4.45** | [3.79, 5.10] | 1.80 | 8 | 1 | 1 |
| `pair_b3_memk` | 29 | **4.38** | [3.90, 4.90] | 1.40 | 7 | 0 | 1 |
| `pair_memk_pl` | 30 | **4.33** | [3.87, 4.83] | 1.37 | 7 | 0 | 0 |
| `pair_ar1c_ms` | 30 | **4.30** | [3.83, 4.77] | 1.34 | 7 | 0 | 0 |
| `pair_asym_ar1c` | 28 | **4.25** | [3.68, 4.82] | 1.60 | 7 | 0 | 2 |
| `pair_b3_pl` | 28 | **4.21** | [3.82, 4.61] | 1.13 | 7 | 0 | 2 |
| `pair_ar1c_pl` | 29 | **3.90** | [3.48, 4.31] | 1.14 | 6 | 0 | 1 |
| `pair_asym_pl` | 30 | **3.77** | [3.20, 4.43] | 1.76 | 9 | 1 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `pair_asym_memk_seed2` | **9/11** |
| `pair_asym_pl_seed28` | **9/11** |
| `pair_levy_ms_seed15` | **9/11** |
| `pair_zumdn_levy_seed11` | **9/11** |
| `pair_asym_ms_seed14` | **8/11** |
| `pair_b3_levy_seed9` | **8/11** |
| `pair_levy_ms_seed10` | **8/11** |
| `pair_levy_pl_seed26` | **8/11** |
| `pair_memk_ms_seed24` | **8/11** |
| `pair_zumdn_levy_seed9` | **8/11** |

