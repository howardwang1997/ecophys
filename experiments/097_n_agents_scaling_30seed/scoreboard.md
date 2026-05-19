# Score — 097_n_agents_scaling_30seed

Discovered 90 runs, 90 with eval, 24 rejected for numerical instability (66 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `scale_n1000_pair_zumdn_b3_seed10` | aggregational_gaussianity=1430.7 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed11` | aggregational_gaussianity=1141.7 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed12` | aggregational_gaussianity=2135.1 (>|1000.0|) | 5/11 |
| `scale_n1000_pair_zumdn_b3_seed13` | aggregational_gaussianity=1518.7 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed15` | aggregational_gaussianity=2045.8 (>|1000.0|) | 4/11 |
| `scale_n1000_pair_zumdn_b3_seed16` | aggregational_gaussianity=1401.6 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed18` | aggregational_gaussianity=1142.5 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed19` | aggregational_gaussianity=1348.4 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed20` | aggregational_gaussianity=1338.5 (>|1000.0|) | 5/11 |
| `scale_n1000_pair_zumdn_b3_seed23` | aggregational_gaussianity=1065.5 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed24` | aggregational_gaussianity=1167.2 (>|1000.0|) | 5/11 |
| `scale_n1000_pair_zumdn_b3_seed25` | aggregational_gaussianity=1292.8 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed28` | aggregational_gaussianity=1207.8 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed3` | aggregational_gaussianity=1323.3 (>|1000.0|) | 3/11 |
| `scale_n1000_pair_zumdn_b3_seed9` | aggregational_gaussianity=1411.5 (>|1000.0|) | 3/11 |
| `scale_n5000_pair_zumdn_b3_seed1` | conditional_kurtosis=148.5 (>|100.0|) | 6/11 |
| `scale_n5000_pair_zumdn_b3_seed19` | aggregational_gaussianity=1442.2 (>|1000.0|) | 4/11 |
| `scale_n5000_pair_zumdn_b3_seed22` | aggregational_gaussianity=1000.6 (>|1000.0|) | 2/11 |
| `scale_n5000_pair_zumdn_b3_seed23` | aggregational_gaussianity=1052.5 (>|1000.0|) | 4/11 |
| `scale_n500_pair_zumdn_b3_seed12` | aggregational_gaussianity=1113.7 (>|1000.0|) | 5/11 |
| `scale_n500_pair_zumdn_b3_seed15` | aggregational_gaussianity=1015.6 (>|1000.0|) | 4/11 |
| `scale_n500_pair_zumdn_b3_seed20` | aggregational_gaussianity=1068.4 (>|1000.0|) | 4/11 |
| `scale_n500_pair_zumdn_b3_seed23` | aggregational_gaussianity=1020.7 (>|1000.0|) | 5/11 |
| `scale_n500_pair_zumdn_b3_seed27` | aggregational_gaussianity=1242.3 (>|1000.0|) | 4/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `scale_n5000_pair_zumdn_b3` | 26 | **4.65** | [4.19, 5.12] | 1.20 | 7 | 0 | 4 |
| `scale_n500_pair_zumdn_b3` | 25 | **4.08** | [3.68, 4.48] | 1.04 | 6 | 0 | 5 |
| `scale_n1000_pair_zumdn_b3` | 15 | **3.87** | [3.20, 4.73] | 1.60 | 8 | 1 | 15 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `scale_n1000_pair_zumdn_b3_seed27` | **8/11** |
| `scale_n1000_pair_zumdn_b3_seed29` | **7/11** |
| `scale_n5000_pair_zumdn_b3_seed17` | **7/11** |
| `scale_n5000_pair_zumdn_b3_seed5` | **7/11** |
| `scale_n5000_pair_zumdn_b3_seed21` | **6/11** |
| `scale_n5000_pair_zumdn_b3_seed3` | **6/11** |
| `scale_n5000_pair_zumdn_b3_seed4` | **6/11** |
| `scale_n5000_pair_zumdn_b3_seed7` | **6/11** |
| `scale_n500_pair_zumdn_b3_seed2` | **6/11** |
| `scale_n500_pair_zumdn_b3_seed28` | **6/11** |

