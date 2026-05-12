# Score — 083_asym_drag_finegrid_30seed

Discovered 90 runs, 90 with eval, 12 rejected for numerical instability (78 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `asymdrag_a04_seed12` | conditional_kurtosis=111.7 (>|100.0|) | 3/11 |
| `asymdrag_a04_seed18` | aggregational_gaussianity=1292.2 (>|1000.0|) | 6/11 |
| `asymdrag_a04_seed9` | aggregational_gaussianity=1064.0 (>|1000.0|) | 5/11 |
| `asymdrag_a05_seed0` | aggregational_gaussianity=1401.7 (>|1000.0|) | 4/11 |
| `asymdrag_a05_seed15` | aggregational_gaussianity=1358.8 (>|1000.0|) | 4/11 |
| `asymdrag_a07_seed0` | aggregational_gaussianity=1352.3 (>|1000.0|) | 3/11 |
| `asymdrag_a07_seed1` | aggregational_gaussianity=1288.0 (>|1000.0|) | 5/11 |
| `asymdrag_a07_seed10` | aggregational_gaussianity=1004.2 (>|1000.0|) | 5/11 |
| `asymdrag_a07_seed27` | aggregational_gaussianity=1188.0 (>|1000.0|) | 3/11 |
| `asymdrag_a07_seed4` | conditional_kurtosis=999.0 (>|100.0|) | 5/11 |
| `asymdrag_a07_seed7` | aggregational_gaussianity=1148.7 (>|1000.0|) | 5/11 |
| `asymdrag_a07_seed9` | conditional_kurtosis=117.3 (>|100.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `asymdrag_a07` | 23 | **4.74** | [4.13, 5.30] | 1.45 | 7 | 0 | 7 |
| `asymdrag_a04` | 27 | **4.33** | [3.59, 5.15] | 2.13 | 9 | 3 | 3 |
| `asymdrag_a05` | 28 | **4.14** | [3.50, 4.79] | 1.76 | 7 | 0 | 2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `asymdrag_a04_seed3` | **9/11** |
| `asymdrag_a04_seed2` | **8/11** |
| `asymdrag_a04_seed20` | **8/11** |
| `asymdrag_a04_seed16` | **7/11** |
| `asymdrag_a05_seed10` | **7/11** |
| `asymdrag_a05_seed4` | **7/11** |
| `asymdrag_a07_seed24` | **7/11** |
| `asymdrag_a07_seed29` | **7/11** |
| `asymdrag_a04_seed10` | **6/11** |
| `asymdrag_a04_seed7` | **6/11** |

