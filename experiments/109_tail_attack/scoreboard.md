# Score — 109_tail_attack

Discovered 135 runs, 135 with eval, 2 rejected for numerical instability (133 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `t10_j01_seed0` | aggregational_gaussianity=1241.5 (>|1000.0|) | 4/11 |
| `t30_j05_seed0` | aggregational_gaussianity=1230.9 (>|1000.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `normal_j00` | 15 | **5.20** | [4.47, 5.93] | 1.47 | 8 | 1 | 0 |
| `t10_j01` | 14 | **4.86** | [3.86, 5.86] | 1.96 | 8 | 2 | 1 |
| `anchor_t5_j05` | 15 | **4.80** | [4.13, 5.47] | 1.37 | 6 | 0 | 0 |
| `normal_j05` | 15 | **4.80** | [4.00, 5.67] | 1.74 | 7 | 0 | 0 |
| `t10_j01_sv` | 15 | **4.67** | [3.87, 5.40] | 1.54 | 7 | 0 | 0 |
| `normal_j00_sv` | 15 | **4.60** | [4.00, 5.27] | 1.30 | 7 | 0 | 0 |
| `t10_j05` | 15 | **4.47** | [3.80, 5.07] | 1.25 | 6 | 0 | 0 |
| `t30_j05` | 14 | **4.21** | [3.50, 4.86] | 1.31 | 6 | 0 | 1 |
| `t10_j00` | 15 | **4.07** | [3.33, 4.73] | 1.49 | 6 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `normal_j00_seed0` | **8/11** |
| `t10_j01_seed1` | **8/11** |
| `t10_j01_seed2` | **8/11** |
| `normal_j00_seed11` | **7/11** |
| `normal_j00_seed4` | **7/11** |
| `normal_j00_seed8` | **7/11** |
| `normal_j00_sv_seed13` | **7/11** |
| `normal_j00_sv_seed9` | **7/11** |
| `normal_j05_seed11` | **7/11** |
| `normal_j05_seed13` | **7/11** |

