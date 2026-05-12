# Score — 085_b2_wasserstein_30seed

Discovered 90 runs, 82 with eval, 11 rejected for numerical instability (71 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `b2_hybrid_combo_seed1` | conditional_kurtosis=1072.4 (>|100.0|) | 5/11 |
| `b2_hybrid_combo_seed16` | aggregational_gaussianity=1088.2 (>|1000.0|) | 6/11 |
| `b2_hybrid_combo_seed22` | conditional_kurtosis=197.5 (>|100.0|) | 5/11 |
| `b2_hybrid_combo_seed23` | aggregational_gaussianity=2184.4 (>|1000.0|) | 3/11 |
| `b2_hybrid_combo_seed3` | aggregational_gaussianity=1098.1 (>|1000.0|) | 5/11 |
| `b2_hybrid_combo_seed5` | aggregational_gaussianity=2569.6 (>|1000.0|) | 4/11 |
| `b2_hybrid_combo_seed7` | aggregational_gaussianity=1412.5 (>|1000.0|) | 6/11 |
| `b2_wasserstein_combo_seed1` | aggregational_gaussianity=1085.5 (>|1000.0|) | 7/11 |
| `b2_wasserstein_combo_seed21` | aggregational_gaussianity=2119.3 (>|1000.0|) | 4/11 |
| `b2_wasserstein_combo_seed7` | aggregational_gaussianity=1728.5 (>|1000.0|) | 5/11 |
| `b2_wasserstein_combo_seed9` | aggregational_gaussianity=1322.0 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `b2_wasserstein_combo` | 26 | **4.46** | [3.73, 5.19] | 1.96 | 9 | 2 | 4 |
| `b2_wasserstein_pure` | 22 | **4.41** | [3.95, 4.86] | 1.10 | 6 | 0 | 0 |
| `b2_hybrid_combo` | 23 | **4.04** | [3.48, 4.61] | 1.43 | 7 | 0 | 7 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `b2_wasserstein_combo_seed22` | **9/11** |
| `b2_wasserstein_combo_seed28` | **8/11** |
| `b2_hybrid_combo_seed6` | **7/11** |
| `b2_wasserstein_combo_seed2` | **7/11** |
| `b2_hybrid_combo_seed12` | **6/11** |
| `b2_hybrid_combo_seed17` | **6/11** |
| `b2_wasserstein_combo_seed15` | **6/11** |
| `b2_wasserstein_combo_seed18` | **6/11** |
| `b2_wasserstein_combo_seed23` | **6/11** |
| `b2_wasserstein_combo_seed25` | **6/11** |

