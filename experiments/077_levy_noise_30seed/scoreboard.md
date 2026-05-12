# Score — 077_levy_noise_30seed

Discovered 90 runs, 90 with eval, 5 rejected for numerical instability (85 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `levy_a15_seed16` | aggregational_gaussianity=2241.7 (>|1000.0|) | 4/11 |
| `levy_a15_seed19` | aggregational_gaussianity=1082.7 (>|1000.0|) | 3/11 |
| `levy_a15_seed27` | aggregational_gaussianity=1179.4 (>|1000.0|) | 3/11 |
| `levy_a17_seed19` | aggregational_gaussianity=1015.7 (>|1000.0|) | 3/11 |
| `levy_a19_seed19` | aggregational_gaussianity=1065.0 (>|1000.0|) | 4/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `levy_a19` | 29 | **4.97** | [4.41, 5.52] | 1.52 | 9 | 1 | 1 |
| `levy_a17` | 29 | **4.86** | [4.38, 5.34] | 1.36 | 7 | 0 | 1 |
| `levy_a15` | 27 | **4.85** | [4.37, 5.33] | 1.29 | 7 | 0 | 3 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `levy_a19_seed8` | **9/11** |
| `levy_a15_seed14` | **7/11** |
| `levy_a15_seed4` | **7/11** |
| `levy_a17_seed11` | **7/11** |
| `levy_a17_seed2` | **7/11** |
| `levy_a17_seed27` | **7/11** |
| `levy_a17_seed8` | **7/11** |
| `levy_a19_seed20` | **7/11** |
| `levy_a19_seed22` | **7/11** |
| `levy_a15_seed0` | **6/11** |

