# Score — 099b_memk_refinement_n30

Discovered 270 runs, 270 with eval, 7 rejected for numerical instability (263 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `baseline_v3_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `baseline_v3_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `memk_s025_lam090_seed18` | aggregational_gaussianity=1106.8 (>|1000.0|) | 3/11 |
| `memk_s025_lam090_seed19` | aggregational_gaussianity=1310.9 (>|1000.0|) | 4/11 |
| `memk_s025_lam095_seed18` | aggregational_gaussianity=1122.3 (>|1000.0|) | 4/11 |
| `memk_s050_lam090_seed18` | aggregational_gaussianity=1080.5 (>|1000.0|) | 3/11 |
| `memk_s075_lam090_seed19` | aggregational_gaussianity=1918.3 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `memk_s025_lam090` | 28 | **5.00** | [4.46, 5.50] | 1.44 | 7 | 0 | 2 |
| `memk_s075_lam090` | 29 | **4.76** | [4.21, 5.31] | 1.57 | 8 | 3 | 1 |
| `memk_s075_lam095` | 30 | **4.70** | [4.23, 5.17] | 1.32 | 8 | 1 | 0 |
| `memk_s025_lam095` | 29 | **4.66** | [4.21, 5.10] | 1.23 | 7 | 0 | 1 |
| `baseline_v3` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `memk_s050_lam099` | 30 | **4.63** | [4.13, 5.13] | 1.40 | 7 | 0 | 0 |
| `memk_s100_lam085` | 30 | **4.63** | [4.10, 5.13] | 1.47 | 7 | 0 | 0 |
| `memk_s100_lam099` | 30 | **4.40** | [3.80, 5.00] | 1.73 | 8 | 1 | 0 |
| `memk_s050_lam090` | 29 | **4.38** | [3.90, 4.86] | 1.40 | 8 | 1 | 1 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `memk_s050_lam090_seed8` | **8/11** |
| `memk_s075_lam090_seed11` | **8/11** |
| `memk_s075_lam090_seed24` | **8/11** |
| `memk_s075_lam090_seed9` | **8/11** |
| `memk_s075_lam095_seed26` | **8/11** |
| `memk_s100_lam099_seed25` | **8/11** |
| `memk_s025_lam090_seed20` | **7/11** |
| `memk_s025_lam090_seed23` | **7/11** |
| `memk_s025_lam090_seed7` | **7/11** |
| `memk_s025_lam095_seed0` | **7/11** |

