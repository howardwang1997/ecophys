# Score — 102_multifact_loss_n30

Discovered 420 runs, 420 with eval, 7 rejected for numerical instability (413 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `baseline_v3_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `baseline_v3_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `mf_dfa_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `mf_dfa_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `mf_fano_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `mf_fano_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `mf_skew_seed19` | aggregational_gaussianity=1198.3 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `d_mse` | 30 | **4.83** | [4.33, 5.33] | 1.42 | 7 | 0 | 0 |
| `baseline_v3` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `mf_dfa` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `mf_fano` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `mf_all_l1` | 30 | **4.63** | [4.17, 5.13] | 1.35 | 8 | 1 | 0 |
| `mf_all_mse` | 30 | **4.63** | [4.13, 5.10] | 1.35 | 7 | 0 | 0 |
| `mf_skew` | 29 | **4.59** | [4.14, 5.03] | 1.30 | 7 | 0 | 1 |
| `d_huber` | 30 | **4.57** | [4.20, 4.97] | 1.10 | 8 | 1 | 0 |
| `mf_all_mse_hi` | 30 | **4.53** | [4.10, 4.93] | 1.20 | 6 | 0 | 0 |
| `mf_all_mse_lo` | 30 | **4.53** | [3.93, 5.10] | 1.63 | 7 | 0 | 0 |
| `mf_aggdfa` | 30 | **4.50** | [3.97, 5.03] | 1.48 | 7 | 0 | 0 |
| `mf_skewfano` | 30 | **4.47** | [3.97, 4.97] | 1.43 | 8 | 1 | 0 |
| `mf_all_huber` | 30 | **4.43** | [4.00, 4.87] | 1.25 | 7 | 0 | 0 |
| `mf_agg` | 30 | **4.33** | [3.83, 4.83] | 1.45 | 7 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `d_huber_seed16` | **8/11** |
| `mf_all_l1_seed29` | **8/11** |
| `mf_skewfano_seed21` | **8/11** |
| `d_huber_seed22` | **7/11** |
| `d_mse_seed0` | **7/11** |
| `d_mse_seed1` | **7/11** |
| `d_mse_seed16` | **7/11** |
| `d_mse_seed18` | **7/11** |
| `d_mse_seed25` | **7/11** |
| `d_mse_seed29` | **7/11** |

