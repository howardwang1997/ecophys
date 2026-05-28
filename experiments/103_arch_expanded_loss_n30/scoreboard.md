# Score — 103_arch_expanded_loss_n30

Discovered 390 runs, 320 with eval, 44 rejected for numerical instability (276 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `agentmem_inner4_seed10` | aggregational_gaussianity=1404.6 (>|1000.0|) | 3/11 |
| `agentmem_inner4_seed13` | aggregational_gaussianity=2549.4 (>|1000.0|) | 4/11 |
| `agentmem_inner4_seed14` | aggregational_gaussianity=1827.6 (>|1000.0|) | 3/11 |
| `agentmem_inner4_seed15` | aggregational_gaussianity=1763.6 (>|1000.0|) | 3/11 |
| `agentmem_inner4_seed16` | aggregational_gaussianity=2169.3 (>|1000.0|) | 4/11 |
| `agentmem_inner4_seed18` | aggregational_gaussianity=2168.8 (>|1000.0|) | 3/11 |
| `agentmem_inner4_seed2` | aggregational_gaussianity=1472.2 (>|1000.0|) | 4/11 |
| `agentmem_inner4_seed22` | aggregational_gaussianity=1695.1 (>|1000.0|) | 3/11 |
| `agentmem_inner4_seed24` | aggregational_gaussianity=1033.3 (>|1000.0|) | 3/11 |
| `agentmem_inner4_seed26` | aggregational_gaussianity=1851.4 (>|1000.0|) | 4/11 |
| `agentmem_inner4_seed4` | aggregational_gaussianity=1096.8 (>|1000.0|) | 5/11 |
| `agentmem_inner4_seed6` | aggregational_gaussianity=1252.3 (>|1000.0|) | 5/11 |
| `agentmem_inner4_seed9` | aggregational_gaussianity=1035.2 (>|1000.0|) | 4/11 |
| `agentmem_seed4` | aggregational_gaussianity=1285.6 (>|1000.0|) | 3/11 |
| `baseline_v3_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `baseline_v3_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `inner2_seed12` | aggregational_gaussianity=1133.8 (>|1000.0|) | 3/11 |
| `inner2_seed15` | aggregational_gaussianity=1599.8 (>|1000.0|) | 3/11 |
| `inner2_seed18` | aggregational_gaussianity=2296.4 (>|1000.0|) | 3/11 |
| `inner2_seed19` | aggregational_gaussianity=1387.8 (>|1000.0|) | 6/11 |
| `inner2_seed24` | aggregational_gaussianity=1430.5 (>|1000.0|) | 4/11 |
| `inner2_seed4` | aggregational_gaussianity=2277.9 (>|1000.0|) | 3/11 |
| `inner2_seed5` | aggregational_gaussianity=1287.2 (>|1000.0|) | 3/11 |
| `inner2_seed7` | aggregational_gaussianity=1378.3 (>|1000.0|) | 3/11 |
| `inner4_seed11` | aggregational_gaussianity=1298.6 (>|1000.0|) | 3/11 |
| `inner4_seed12` | aggregational_gaussianity=1291.9 (>|1000.0|) | 7/11 |
| `inner4_seed14` | aggregational_gaussianity=1098.0 (>|1000.0|) | 5/11 |
| `inner4_seed16` | aggregational_gaussianity=1223.5 (>|1000.0|) | 5/11 |
| `inner4_seed18` | aggregational_gaussianity=1074.1 (>|1000.0|) | 4/11 |
| `inner4_seed19` | aggregational_gaussianity=1062.6 (>|1000.0|) | 3/11 |
| `inner4_seed2` | aggregational_gaussianity=1222.6 (>|1000.0|) | 4/11 |
| `inner4_seed25` | aggregational_gaussianity=1059.1 (>|1000.0|) | 4/11 |
| `inner4_seed26` | aggregational_gaussianity=2391.5 (>|1000.0|) | 3/11 |
| `inner4_seed27` | aggregational_gaussianity=2195.2 (>|1000.0|) | 4/11 |
| `inner4_seed29` | aggregational_gaussianity=3150.0 (>|1000.0|) | 5/11 |
| `inner4_seed5` | aggregational_gaussianity=1454.0 (>|1000.0|) | 3/11 |
| `inner4_seed6` | aggregational_gaussianity=2993.5 (>|1000.0|) | 3/11 |
| `inner4_seed7` | aggregational_gaussianity=1814.8 (>|1000.0|) | 3/11 |
| `inner8_seed12` | aggregational_gaussianity=1205.3 (>|1000.0|) | 5/11 |
| `inner8_seed18` | aggregational_gaussianity=1110.6 (>|1000.0|) | 3/11 |
| `inner8_seed23` | aggregational_gaussianity=1194.0 (>|1000.0|) | 2/11 |
| `inner8_seed25` | aggregational_gaussianity=2069.9 (>|1000.0|) | 6/11 |
| `inner8_seed29` | aggregational_gaussianity=1295.4 (>|1000.0|) | 3/11 |
| `inner8_seed3` | aggregational_gaussianity=1127.6 (>|1000.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `agentmem_inner4` | 17 | **5.41** | [4.71, 6.06] | 1.46 | 8 | 1 | 13 |
| `gstate_off` | 30 | **4.97** | [4.40, 5.50] | 1.59 | 8 | 1 | 0 |
| `inner8` | 20 | **4.95** | [4.50, 5.40] | 1.10 | 7 | 0 | 6 |
| `agentmem` | 19 | **4.95** | [4.26, 5.58] | 1.51 | 8 | 1 | 1 |
| `inner2` | 22 | **4.73** | [4.14, 5.32] | 1.45 | 7 | 0 | 8 |
| `baseline_v3` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `exploss_base` | 30 | **4.63** | [4.13, 5.10] | 1.35 | 7 | 0 | 0 |
| `inner4` | 16 | **4.62** | [4.00, 5.19] | 1.26 | 7 | 0 | 14 |
| `isab_inner4` | 14 | **3.07** | [2.86, 3.29] | 0.47 | 4 | 0 | 0 |
| `isab_m128` | 16 | **2.38** | [2.12, 2.62] | 0.50 | 3 | 0 | 0 |
| `isab_m32` | 22 | **2.36** | [2.18, 2.59] | 0.49 | 3 | 0 | 0 |
| `isab` | 30 | **2.27** | [2.10, 2.43] | 0.45 | 3 | 0 | 0 |
| `isab_agentmem` | 12 | **2.17** | [2.00, 2.42] | 0.39 | 3 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `agentmem_inner4_seed8` | **8/11** |
| `agentmem_seed17` | **8/11** |
| `gstate_off_seed15` | **8/11** |
| `agentmem_inner4_seed11` | **7/11** |
| `agentmem_inner4_seed23` | **7/11** |
| `agentmem_inner4_seed27` | **7/11** |
| `agentmem_seed3` | **7/11** |
| `exploss_base_seed15` | **7/11** |
| `exploss_base_seed23` | **7/11** |
| `gstate_off_seed12` | **7/11** |

