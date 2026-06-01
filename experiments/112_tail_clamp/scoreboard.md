# Score — 112_tail_clamp

Discovered 100 runs, 100 with eval, 7 rejected for numerical instability (93 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `tclamp_abs_seed0` | conditional_kurtosis=115.9 (>|100.0|) | 2/11 |
| `tclamp_abs_seed1` | conditional_kurtosis=205.4 (>|100.0|) | 2/11 |
| `tclamp_abs_seed13` | conditional_kurtosis=144.3 (>|100.0|) | 4/11 |
| `tclamp_abs_seed5` | conditional_kurtosis=335.1 (>|100.0|) | 0/11 |
| `tclamp_abs_seed6` | conditional_kurtosis=995.3 (>|100.0|) | 1/11 |
| `tclamp_abs_seed8` | conditional_kurtosis=458.9 (>|100.0|) | 4/11 |
| `tclamp_abs_seed9` | conditional_kurtosis=355.9 (>|100.0|) | 2/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `tclamp_rel_c8` | 20 | **5.00** | [4.55, 5.45] | 1.08 | 7 | 0 | 0 |
| `tclamp_rel_c5` | 20 | **4.50** | [4.15, 4.85] | 0.83 | 6 | 0 | 0 |
| `baseline` | 20 | **4.15** | [3.50, 4.80] | 1.50 | 7 | 0 | 0 |
| `tclamp_rel_c3` | 20 | **3.30** | [2.80, 3.80] | 1.17 | 5 | 0 | 0 |
| `tclamp_abs` | 13 | **3.15** | [2.31, 4.00] | 1.72 | 5 | 0 | 7 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `baseline_seed14` | **7/11** |
| `tclamp_rel_c8_seed4` | **7/11** |
| `baseline_seed13` | **6/11** |
| `baseline_seed8` | **6/11** |
| `tclamp_rel_c5_seed14` | **6/11** |
| `tclamp_rel_c5_seed16` | **6/11** |
| `tclamp_rel_c8_seed13` | **6/11** |
| `tclamp_rel_c8_seed14` | **6/11** |
| `tclamp_rel_c8_seed15` | **6/11** |
| `tclamp_rel_c8_seed16` | **6/11** |

