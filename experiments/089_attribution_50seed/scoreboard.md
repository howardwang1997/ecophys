# Score — 089_attribution_50seed

Discovered 800 runs, 796 with eval, 79 rejected for numerical instability (717 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `attr_ar1_s03_seed10` | conditional_kurtosis=830.6 (>|100.0|) | 4/11 |
| `attr_ar1_s03_seed12` | conditional_kurtosis=498.1 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed13` | aggregational_gaussianity=1062.9 (>|1000.0|) | 4/11 |
| `attr_ar1_s03_seed15` | aggregational_gaussianity=1023.2 (>|1000.0|) | 5/11 |
| `attr_ar1_s03_seed16` | aggregational_gaussianity=1036.2 (>|1000.0|) | 3/11 |
| `attr_ar1_s03_seed17` | conditional_kurtosis=537.9 (>|100.0|) | 3/11 |
| `attr_ar1_s03_seed18` | aggregational_gaussianity=1175.8 (>|1000.0|) | 3/11 |
| `attr_ar1_s03_seed2` | conditional_kurtosis=379.3 (>|100.0|) | 5/11 |
| `attr_ar1_s03_seed20` | conditional_kurtosis=684.1 (>|100.0|) | 5/11 |
| `attr_ar1_s03_seed21` | aggregational_gaussianity=1051.0 (>|1000.0|) | 5/11 |
| `attr_ar1_s03_seed23` | aggregational_gaussianity=1087.1 (>|1000.0|) | 5/11 |
| `attr_ar1_s03_seed24` | conditional_kurtosis=501.9 (>|100.0|) | 3/11 |
| `attr_ar1_s03_seed25` | conditional_kurtosis=371.4 (>|100.0|) | 4/11 |
| `attr_ar1_s03_seed27` | conditional_kurtosis=328.1 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed28` | aggregational_gaussianity=1011.7 (>|1000.0|) | 2/11 |
| `attr_ar1_s03_seed30` | conditional_kurtosis=407.3 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed31` | conditional_kurtosis=591.3 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed32` | aggregational_gaussianity=1048.7 (>|1000.0|) | 3/11 |
| `attr_ar1_s03_seed33` | conditional_kurtosis=458.4 (>|100.0|) | 4/11 |
| `attr_ar1_s03_seed34` | aggregational_gaussianity=1010.9 (>|1000.0|) | 4/11 |
| `attr_ar1_s03_seed36` | aggregational_gaussianity=1005.7 (>|1000.0|) | 3/11 |
| `attr_ar1_s03_seed38` | conditional_kurtosis=439.3 (>|100.0|) | 4/11 |
| `attr_ar1_s03_seed39` | conditional_kurtosis=495.0 (>|100.0|) | 3/11 |
| `attr_ar1_s03_seed4` | conditional_kurtosis=505.5 (>|100.0|) | 1/11 |
| `attr_ar1_s03_seed40` | aggregational_gaussianity=1025.9 (>|1000.0|) | 3/11 |
| `attr_ar1_s03_seed41` | conditional_kurtosis=538.8 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed43` | conditional_kurtosis=741.2 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed44` | conditional_kurtosis=423.0 (>|100.0|) | 5/11 |
| `attr_ar1_s03_seed45` | conditional_kurtosis=601.0 (>|100.0|) | 4/11 |
| `attr_ar1_s03_seed47` | conditional_kurtosis=289.2 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed48` | aggregational_gaussianity=1017.6 (>|1000.0|) | 3/11 |
| `attr_ar1_s03_seed49` | conditional_kurtosis=621.4 (>|100.0|) | 4/11 |
| `attr_ar1_s03_seed6` | conditional_kurtosis=731.5 (>|100.0|) | 3/11 |
| `attr_ar1_s03_seed8` | conditional_kurtosis=539.1 (>|100.0|) | 2/11 |
| `attr_ar1_s03_seed9` | aggregational_gaussianity=1127.4 (>|1000.0|) | 4/11 |
| `attr_ar1_s05_seed29` | aggregational_gaussianity=1255.4 (>|1000.0|) | 3/11 |
| `attr_ar1_s08_seed13` | aggregational_gaussianity=1093.1 (>|1000.0|) | 2/11 |
| `attr_ar1_s08_seed14` | aggregational_gaussianity=1432.9 (>|1000.0|) | 3/11 |
| `attr_ar1_s08_seed23` | aggregational_gaussianity=1854.3 (>|1000.0|) | 3/11 |
| `attr_ar1_s08_seed38` | aggregational_gaussianity=1172.2 (>|1000.0|) | 4/11 |
| `attr_ar1_s08_seed41` | aggregational_gaussianity=2055.2 (>|1000.0|) | 3/11 |
| `attr_ar1_s08_seed44` | aggregational_gaussianity=1002.7 (>|1000.0|) | 3/11 |
| `attr_ar1_s08_seed5` | aggregational_gaussianity=2470.8 (>|1000.0|) | 2/11 |
| `attr_ar1_s08_seed7` | aggregational_gaussianity=1443.3 (>|1000.0|) | 4/11 |
| `attr_asymdrag_a06_seed35` | conditional_kurtosis=288.0 (>|100.0|) | 6/11 |
| `attr_asymdrag_a06_seed9` | conditional_kurtosis=107.4 (>|100.0|) | 6/11 |
| `attr_baseline_v3_seed47` | aggregational_gaussianity=1217.2 (>|1000.0|) | 3/11 |
| `attr_inner_3_seed11` | aggregational_gaussianity=2111.8 (>|1000.0|) | 3/11 |
| `attr_inner_3_seed18` | aggregational_gaussianity=1033.9 (>|1000.0|) | 3/11 |
| `attr_inner_3_seed20` | aggregational_gaussianity=2046.7 (>|1000.0|) | 4/11 |
| `attr_inner_3_seed22` | aggregational_gaussianity=2054.4 (>|1000.0|) | 5/11 |
| `attr_inner_3_seed27` | aggregational_gaussianity=2120.7 (>|1000.0|) | 3/11 |
| `attr_inner_3_seed30` | aggregational_gaussianity=1560.3 (>|1000.0|) | 4/11 |
| `attr_inner_3_seed39` | aggregational_gaussianity=1468.8 (>|1000.0|) | 4/11 |
| `attr_inner_3_seed7` | aggregational_gaussianity=3595.8 (>|1000.0|) | 4/11 |
| `attr_inner_3_seed9` | aggregational_gaussianity=1056.8 (>|1000.0|) | 7/11 |
| `attr_jump_l01_seed32` | aggregational_gaussianity=1025.6 (>|1000.0|) | 3/11 |
| `attr_levy_a17_seed19` | aggregational_gaussianity=1015.3 (>|1000.0|) | 3/11 |
| `attr_zumbach_dn_s10_seed3` | conditional_kurtosis=193.7 (>|100.0|) | 6/11 |
| `attr_zumbach_dn_s10_seed39` | conditional_kurtosis=125.2 (>|100.0|) | 5/11 |
| `attr_zumbach_s05_seed1` | conditional_kurtosis=145.7 (>|100.0|) | 6/11 |
| `attr_zumbach_s05_seed12` | conditional_kurtosis=156.7 (>|100.0|) | 7/11 |
| `attr_zumbach_s05_seed16` | conditional_kurtosis=137.0 (>|100.0|) | 5/11 |
| `attr_zumbach_s05_seed2` | conditional_kurtosis=102.0 (>|100.0|) | 5/11 |
| `attr_zumbach_s05_seed28` | conditional_kurtosis=111.1 (>|100.0|) | 4/11 |
| `attr_zumbach_s05_seed37` | conditional_kurtosis=153.9 (>|100.0|) | 7/11 |
| `attr_zumbach_s05_seed40` | conditional_kurtosis=106.9 (>|100.0|) | 8/11 |
| `attr_zumbach_s05_seed47` | conditional_kurtosis=123.2 (>|100.0|) | 5/11 |
| `attr_zumbach_s05_seed5` | conditional_kurtosis=117.3 (>|100.0|) | 5/11 |
| `attr_zumbach_s05_seed6` | conditional_kurtosis=195.3 (>|100.0|) | 7/11 |
| `attr_zumbach_s10_seed29` | conditional_kurtosis=116.5 (>|100.0|) | 5/11 |
| `attr_zumbach_s10_seed36` | conditional_kurtosis=105.3 (>|100.0|) | 4/11 |
| `attr_zumbach_s10_seed4` | conditional_kurtosis=106.5 (>|100.0|) | 5/11 |
| `attr_zumbach_s10_seed40` | conditional_kurtosis=114.0 (>|100.0|) | 5/11 |
| `attr_zumbach_s10_seed44` | conditional_kurtosis=106.1 (>|100.0|) | 5/11 |
| `attr_zumbach_s10_seed47` | conditional_kurtosis=105.9 (>|100.0|) | 5/11 |
| `attr_zumbach_s10_seed9` | conditional_kurtosis=119.1 (>|100.0|) | 5/11 |
| `attr_zumbach_s20_seed24` | conditional_kurtosis=100.3 (>|100.0|) | 4/11 |
| `attr_zumbach_s20_seed26` | conditional_kurtosis=117.5 (>|100.0|) | 4/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `attr_zumbach_dn_s10` | 48 | **5.12** | [4.73, 5.52] | 1.41 | 8 | 1 | 2 |
| `attr_b3_k3` | 50 | **4.96** | [4.62, 5.30] | 1.24 | 8 | 1 | 0 |
| `attr_asymdrag_a06` | 48 | **4.92** | [4.31, 5.50] | 2.16 | 9 | 5 | 2 |
| `attr_powerlaw_a15` | 50 | **4.88** | [4.56, 5.20] | 1.19 | 8 | 2 | 0 |
| `attr_ar1_s05` | 49 | **4.88** | [4.51, 5.27] | 1.35 | 8 | 2 | 1 |
| `attr_baseline_v3` | 49 | **4.82** | [4.45, 5.18] | 1.32 | 8 | 1 | 1 |
| `attr_zumbach_s05` | 40 | **4.75** | [4.33, 5.20] | 1.41 | 8 | 2 | 10 |
| `attr_inner_3` | 41 | **4.71** | [4.17, 5.24] | 1.78 | 8 | 1 | 9 |
| `attr_levy_a17` | 49 | **4.65** | [4.29, 5.00] | 1.27 | 7 | 0 | 1 |
| `attr_memk_l095_s10` | 50 | **4.56** | [4.20, 4.92] | 1.33 | 8 | 1 | 0 |
| `attr_microstructure_r03` | 50 | **4.54** | [4.16, 4.92] | 1.42 | 7 | 0 | 0 |
| `attr_ar1_s03` | 15 | **4.47** | [3.80, 5.20] | 1.46 | 8 | 1 | 35 |
| `attr_jump_l01` | 45 | **4.38** | [3.96, 4.80] | 1.47 | 7 | 0 | 1 |
| `attr_zumbach_s10` | 43 | **4.23** | [3.84, 4.63] | 1.34 | 7 | 0 | 7 |
| `attr_ar1_s08` | 42 | **3.93** | [3.52, 4.33] | 1.37 | 7 | 0 | 8 |
| `attr_zumbach_s20` | 48 | **3.77** | [3.27, 4.31] | 1.90 | 8 | 2 | 2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `attr_asymdrag_a06_seed14` | **9/11** |
| `attr_asymdrag_a06_seed2` | **9/11** |
| `attr_ar1_s03_seed35` | **8/11** |
| `attr_ar1_s05_seed19` | **8/11** |
| `attr_ar1_s05_seed35` | **8/11** |
| `attr_asymdrag_a06_seed10` | **8/11** |
| `attr_asymdrag_a06_seed19` | **8/11** |
| `attr_asymdrag_a06_seed33` | **8/11** |
| `attr_b3_k3_seed4` | **8/11** |
| `attr_baseline_v3_seed22` | **8/11** |

