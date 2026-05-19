# Score — 094_var_holdout_12seed

Discovered 96 runs, 96 with eval, 5 rejected for numerical instability (91 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `var_asymdrag_a06_seed1` | aggregational_gaussianity=1018.2 (>|1000.0|) | 6/11 |
| `var_asymdrag_a06_seed5` | conditional_kurtosis=144.1 (>|100.0|) | 3/11 |
| `var_baseline_v3_seed1` | aggregational_gaussianity=1068.9 (>|1000.0|) | 3/11 |
| `var_pair_zumdn_b3_seed11` | conditional_kurtosis=148.7 (>|100.0|) | 7/11 |
| `var_powerlaw_a15_seed5` | aggregational_gaussianity=1018.0 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `var_powerlaw_a15` | 11 | **5.55** | [4.55, 6.64] | 1.81 | 9 | 2 | 1 |
| `var_asymdrag_a06` | 10 | **5.30** | [4.30, 6.40] | 1.77 | 9 | 1 | 2 |
| `var_zumdn_s10` | 12 | **5.08** | [4.17, 6.08] | 1.78 | 8 | 2 | 0 |
| `var_b3_k3` | 12 | **4.67** | [4.00, 5.33] | 1.30 | 7 | 0 | 0 |
| `var_pair_zumdn_b3` | 11 | **4.45** | [3.64, 5.27] | 1.51 | 7 | 0 | 1 |
| `var_ar1_s05` | 12 | **4.33** | [3.67, 5.08] | 1.30 | 7 | 0 | 0 |
| `var_pair_zumdn_asym` | 12 | **4.17** | [3.33, 5.00] | 1.47 | 6 | 0 | 0 |
| `var_baseline_v3` | 11 | **4.00** | [3.27, 4.73] | 1.26 | 6 | 0 | 1 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `var_asymdrag_a06_seed3` | **9/11** |
| `var_powerlaw_a15_seed11` | **9/11** |
| `var_powerlaw_a15_seed1` | **8/11** |
| `var_zumdn_s10_seed0` | **8/11** |
| `var_zumdn_s10_seed11` | **8/11** |
| `var_ar1_s05_seed8` | **7/11** |
| `var_asymdrag_a06_seed6` | **7/11** |
| `var_b3_k3_seed7` | **7/11** |
| `var_pair_zumdn_b3_seed6` | **7/11** |
| `var_zumdn_s10_seed4` | **7/11** |

