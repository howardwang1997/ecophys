# Score — 090b_ar1_stability_grid

Discovered 120 runs, 120 with eval, 27 rejected for numerical instability (93 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `ar1_s025_l90_seed12` | conditional_kurtosis=553.0 (>|100.0|) | 3/11 |
| `ar1_s025_l90_seed13` | conditional_kurtosis=303.0 (>|100.0|) | 4/11 |
| `ar1_s025_l90_seed18` | aggregational_gaussianity=1045.2 (>|1000.0|) | 3/11 |
| `ar1_s025_l90_seed2` | conditional_kurtosis=294.9 (>|100.0|) | 5/11 |
| `ar1_s025_l90_seed5` | aggregational_gaussianity=1029.6 (>|1000.0|) | 4/11 |
| `ar1_s025_l95_seed10` | conditional_kurtosis=319.1 (>|100.0|) | 7/11 |
| `ar1_s025_l95_seed4` | conditional_kurtosis=237.8 (>|100.0|) | 6/11 |
| `ar1_s025_l95_seed7` | aggregational_gaussianity=1052.2 (>|1000.0|) | 3/11 |
| `ar1_s02_l85_seed11` | conditional_kurtosis=396.3 (>|100.0|) | 4/11 |
| `ar1_s02_l85_seed12` | conditional_kurtosis=454.6 (>|100.0|) | 4/11 |
| `ar1_s02_l85_seed13` | conditional_kurtosis=367.8 (>|100.0|) | 3/11 |
| `ar1_s02_l85_seed14` | conditional_kurtosis=460.2 (>|100.0|) | 4/11 |
| `ar1_s02_l85_seed17` | conditional_kurtosis=434.5 (>|100.0|) | 3/11 |
| `ar1_s02_l85_seed3` | conditional_kurtosis=364.7 (>|100.0|) | 4/11 |
| `ar1_s02_l85_seed5` | aggregational_gaussianity=1117.7 (>|1000.0|) | 3/11 |
| `ar1_s02_l85_seed6` | conditional_kurtosis=481.1 (>|100.0|) | 4/11 |
| `ar1_s02_l85_seed7` | aggregational_gaussianity=1180.5 (>|1000.0|) | 3/11 |
| `ar1_s02_l85_seed8` | conditional_kurtosis=458.0 (>|100.0|) | 3/11 |
| `ar1_s02_l85_seed9` | conditional_kurtosis=497.9 (>|100.0|) | 3/11 |
| `ar1_s02_l95_seed11` | conditional_kurtosis=216.5 (>|100.0|) | 4/11 |
| `ar1_s02_l95_seed15` | conditional_kurtosis=173.8 (>|100.0|) | 7/11 |
| `ar1_s02_l95_seed16` | aggregational_gaussianity=1180.6 (>|1000.0|) | 5/11 |
| `ar1_s02_l95_seed18` | conditional_kurtosis=283.2 (>|100.0|) | 6/11 |
| `ar1_s02_l95_seed5` | aggregational_gaussianity=1150.5 (>|1000.0|) | 3/11 |
| `ar1_s03_clip_seed16` | conditional_kurtosis=141.5 (>|100.0|) | 7/11 |
| `ar1_s03_clip_seed8` | conditional_kurtosis=227.5 (>|100.0|) | 7/11 |
| `ar1_s05_clip_seed8` | conditional_kurtosis=195.0 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `ar1_s05_clip` | 19 | **5.11** | [4.63, 5.58] | 1.10 | 7 | 0 | 1 |
| `ar1_s03_clip` | 18 | **4.83** | [4.28, 5.39] | 1.25 | 7 | 0 | 2 |
| `ar1_s025_l95` | 17 | **4.71** | [4.12, 5.29] | 1.31 | 7 | 0 | 3 |
| `ar1_s025_l90` | 15 | **4.53** | [4.00, 5.07] | 1.13 | 6 | 0 | 5 |
| `ar1_s02_l95` | 15 | **4.53** | [3.87, 5.27] | 1.46 | 8 | 1 | 5 |
| `ar1_s02_l85` | 9 | **4.11** | [3.11, 5.00] | 1.54 | 6 | 0 | 11 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `ar1_s02_l95_seed10` | **8/11** |
| `ar1_s025_l95_seed12` | **7/11** |
| `ar1_s02_l95_seed8` | **7/11** |
| `ar1_s03_clip_seed12` | **7/11** |
| `ar1_s05_clip_seed13` | **7/11** |
| `ar1_s05_clip_seed18` | **7/11** |
| `ar1_s025_l90_seed15` | **6/11** |
| `ar1_s025_l90_seed19` | **6/11** |
| `ar1_s025_l90_seed4` | **6/11** |
| `ar1_s025_l90_seed6` | **6/11** |

