# Score — 110_moe_tournament

Discovered 300 runs, 300 with eval, 3 rejected for numerical instability (297 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `baseline_tamed_seed1` | aggregational_gaussianity=1102.7 (>|1000.0|) | 3/11 |
| `baseline_tamed_seed11` | aggregational_gaussianity=1013.3 (>|1000.0|) | 4/11 |
| `moe_k4_t10j01_seed27` | aggregational_gaussianity=2727.1 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `moe_k4_tamed_lbw001` | 30 | **4.83** | [4.27, 5.40] | 1.62 | 8 | 2 | 0 |
| `moe_k4_t10j00` | 30 | **4.77** | [4.17, 5.40] | 1.76 | 9 | 2 | 0 |
| `moe_k8_tamed` | 30 | **4.77** | [4.20, 5.33] | 1.65 | 8 | 1 | 0 |
| `moe_k4_tamed_info` | 30 | **4.60** | [4.13, 5.03] | 1.28 | 7 | 0 | 0 |
| `moe_k4_tamed` | 30 | **4.57** | [3.93, 5.23] | 1.83 | 9 | 1 | 0 |
| `moe_k4_tamed_sv` | 30 | **4.57** | [3.97, 5.17] | 1.70 | 9 | 1 | 0 |
| `moe_k4_t5` | 30 | **4.53** | [3.97, 5.10] | 1.63 | 8 | 1 | 0 |
| `baseline_tamed` | 28 | **4.43** | [3.93, 4.93] | 1.40 | 7 | 0 | 2 |
| `moe_k4_t10j01` | 29 | **4.34** | [3.86, 4.86] | 1.40 | 7 | 0 | 1 |
| `moe_k8_t10j01` | 30 | **3.90** | [3.30, 4.50] | 1.71 | 7 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `moe_k4_t10j00_seed14` | **9/11** |
| `moe_k4_tamed_seed21` | **9/11** |
| `moe_k4_tamed_sv_seed29` | **9/11** |
| `moe_k4_t10j00_seed8` | **8/11** |
| `moe_k4_t5_seed13` | **8/11** |
| `moe_k4_tamed_lbw001_seed17` | **8/11** |
| `moe_k4_tamed_lbw001_seed25` | **8/11** |
| `moe_k8_tamed_seed20` | **8/11** |
| `baseline_tamed_seed13` | **7/11** |
| `baseline_tamed_seed8` | **7/11** |

