# Score — 090d_depth3_interference_30seed

Discovered 180 runs, 180 with eval, 7 rejected for numerical instability (173 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `triple_pair_AB_ar1clip_seed11` | aggregational_gaussianity=1453.5 (>|1000.0|) | 4/11 |
| `triple_pair_AB_ar1clip_seed29` | conditional_kurtosis=374.2 (>|100.0|) | 4/11 |
| `triple_pair_AB_ar1clip_seed5` | conditional_kurtosis=136.8 (>|100.0|) | 6/11 |
| `triple_pair_AB_zumdn_seed28` | conditional_kurtosis=165.8 (>|100.0|) | 7/11 |
| `triple_pair_AB_zumdn_seed4` | conditional_kurtosis=109.4 (>|100.0|) | 6/11 |
| `triple_zumdn_b3_asym_seed28` | conditional_kurtosis=224.3 (>|100.0|) | 7/11 |
| `triple_zumdn_b3_asym_seed4` | conditional_kurtosis=108.2 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `triple_zumdn_b3_memk` | 30 | **5.00** | [4.27, 5.70] | 2.07 | 9 | 3 | 0 |
| `triple_zumdn_b3_powerlaw` | 30 | **4.77** | [4.20, 5.40] | 1.68 | 9 | 2 | 0 |
| `triple_zumdn_b3_levy` | 30 | **4.70** | [4.27, 5.17] | 1.26 | 7 | 0 | 0 |
| `triple_pair_AB_ar1clip` | 27 | **4.37** | [3.85, 4.89] | 1.45 | 7 | 0 | 3 |
| `triple_pair_AB_zumdn` | 28 | **4.07** | [3.39, 4.75] | 1.84 | 7 | 0 | 2 |
| `triple_zumdn_b3_asym` | 28 | **4.04** | [3.36, 4.71] | 1.90 | 7 | 0 | 2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `triple_zumdn_b3_memk_seed6` | **9/11** |
| `triple_zumdn_b3_powerlaw_seed8` | **9/11** |
| `triple_zumdn_b3_memk_seed0` | **8/11** |
| `triple_zumdn_b3_memk_seed12` | **8/11** |
| `triple_zumdn_b3_powerlaw_seed6` | **8/11** |
| `triple_pair_AB_ar1clip_seed3` | **7/11** |
| `triple_pair_AB_ar1clip_seed4` | **7/11** |
| `triple_pair_AB_ar1clip_seed6` | **7/11** |
| `triple_pair_AB_zumdn_seed21` | **7/11** |
| `triple_pair_AB_zumdn_seed25` | **7/11** |

