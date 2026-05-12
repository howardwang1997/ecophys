# Score — 084_b1_microstructure_30seed

Discovered 90 runs, 84 with eval, 3 rejected for numerical instability (81 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `b1_rho03_combo_seed11` | aggregational_gaussianity=2071.2 (>|1000.0|) | 3/11 |
| `b1_rho03_combo_seed15` | aggregational_gaussianity=1621.6 (>|1000.0|) | 4/11 |
| `b1_rho05_pure_seed11` | aggregational_gaussianity=1061.9 (>|1000.0|) | 2/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `b1_rho03_pure` | 24 | **4.58** | [3.92, 5.21] | 1.64 | 8 | 1 | 0 |
| `b1_rho05_pure` | 29 | **4.52** | [4.07, 4.97] | 1.24 | 7 | 0 | 1 |
| `b1_rho03_combo` | 28 | **3.57** | [2.93, 4.29] | 1.85 | 8 | 1 | 2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `b1_rho03_combo_seed23` | **8/11** |
| `b1_rho03_pure_seed24` | **8/11** |
| `b1_rho03_combo_seed4` | **7/11** |
| `b1_rho03_pure_seed26` | **7/11** |
| `b1_rho05_pure_seed4` | **7/11** |
| `b1_rho05_pure_seed8` | **7/11** |
| `b1_rho03_combo_seed9` | **6/11** |
| `b1_rho03_pure_seed20` | **6/11** |
| `b1_rho03_pure_seed3` | **6/11** |
| `b1_rho03_pure_seed4` | **6/11** |

