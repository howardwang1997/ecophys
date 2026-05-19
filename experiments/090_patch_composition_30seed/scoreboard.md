# Score — 090_patch_composition_30seed

Discovered 240 runs, 240 with eval, 9 rejected for numerical instability (231 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `pair_AB_reref_seed19` | conditional_kurtosis=701.2 (>|100.0|) | 4/11 |
| `pair_ar1_b3_seed22` | aggregational_gaussianity=1089.5 (>|1000.0|) | 5/11 |
| `pair_ar1_b3_seed7` | aggregational_gaussianity=1199.8 (>|1000.0|) | 5/11 |
| `pair_zumdn_ar1_seed0` | aggregational_gaussianity=1142.2 (>|1000.0|) | 3/11 |
| `pair_zumdn_ar1_seed12` | aggregational_gaussianity=1585.0 (>|1000.0|) | 2/11 |
| `pair_zumdn_asym_seed29` | conditional_kurtosis=132.9 (>|100.0|) | 6/11 |
| `pair_zumdn_b3_seed2` | conditional_kurtosis=121.4 (>|100.0|) | 5/11 |
| `pair_zumdn_b3_seed22` | conditional_kurtosis=158.3 (>|100.0|) | 6/11 |
| `zumdn_solo_n30_seed3` | conditional_kurtosis=193.6 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `zumdn_solo_n30` | 29 | **5.31** | [4.76, 5.86] | 1.54 | 8 | 1 | 1 |
| `pair_ar1_b3` | 28 | **5.21** | [4.75, 5.68] | 1.32 | 8 | 1 | 2 |
| `pair_AB_reref` | 29 | **5.21** | [4.55, 5.86] | 1.80 | 8 | 3 | 1 |
| `pair_zumdn_b3` | 28 | **4.68** | [4.14, 5.29] | 1.59 | 8 | 2 | 2 |
| `pair_ar1_asym` | 30 | **4.60** | [4.20, 5.00] | 1.13 | 7 | 0 | 0 |
| `pair_zumdn_asym` | 29 | **4.31** | [3.83, 4.79] | 1.39 | 7 | 0 | 1 |
| `pair_zumdn_ar1` | 28 | **3.96** | [3.18, 4.72] | 2.13 | 8 | 1 | 2 |
| `triple_zumdn_ar1_b3` | 30 | **3.90** | [3.30, 4.50] | 1.69 | 7 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `pair_AB_reref_seed13` | **8/11** |
| `pair_AB_reref_seed3` | **8/11** |
| `pair_AB_reref_seed6` | **8/11** |
| `pair_ar1_b3_seed28` | **8/11** |
| `pair_zumdn_ar1_seed24` | **8/11** |
| `pair_zumdn_b3_seed0` | **8/11** |
| `pair_zumdn_b3_seed4` | **8/11** |
| `zumdn_solo_n30_seed14` | **8/11** |
| `pair_AB_reref_seed16` | **7/11** |
| `pair_AB_reref_seed23` | **7/11** |

