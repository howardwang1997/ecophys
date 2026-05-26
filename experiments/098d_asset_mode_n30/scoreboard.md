# Score — 098d_asset_mode_n30

Discovered 180 runs, 180 with eval, 23 rejected for numerical instability (157 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `spx_zum_abs_seed11` | conditional_kurtosis=113.2 (>|100.0|) | 3/11 |
| `spx_zum_abs_seed24` | conditional_kurtosis=111.2 (>|100.0|) | 3/11 |
| `spx_zum_abs_seed25` | conditional_kurtosis=164.2 (>|100.0|) | 4/11 |
| `spx_zum_downside_seed2` | conditional_kurtosis=134.9 (>|100.0|) | 4/11 |
| `spx_zum_downside_seed22` | conditional_kurtosis=115.5 (>|100.0|) | 6/11 |
| `spx_zum_downside_seed29` | conditional_kurtosis=109.3 (>|100.0|) | 3/11 |
| `spx_zum_downside_seed5` | conditional_kurtosis=112.3 (>|100.0|) | 5/11 |
| `spx_zum_downside_seed6` | conditional_kurtosis=101.7 (>|100.0|) | 4/11 |
| `spx_zum_none_seed0` | aggregational_gaussianity=1212.3 (>|1000.0|) | 3/11 |
| `spx_zum_none_seed19` | aggregational_gaussianity=1600.0 (>|1000.0|) | 3/11 |
| `x5_zum_abs_seed0` | conditional_kurtosis=125.7 (>|100.0|) | 3/11 |
| `x5_zum_abs_seed12` | conditional_kurtosis=178.4 (>|100.0|) | 4/11 |
| `x5_zum_abs_seed13` | conditional_kurtosis=181.8 (>|100.0|) | 4/11 |
| `x5_zum_abs_seed16` | conditional_kurtosis=125.9 (>|100.0|) | 3/11 |
| `x5_zum_abs_seed18` | conditional_kurtosis=152.5 (>|100.0|) | 4/11 |
| `x5_zum_abs_seed22` | conditional_kurtosis=106.9 (>|100.0|) | 3/11 |
| `x5_zum_abs_seed25` | conditional_kurtosis=141.9 (>|100.0|) | 3/11 |
| `x5_zum_abs_seed26` | conditional_kurtosis=102.0 (>|100.0|) | 3/11 |
| `x5_zum_abs_seed5` | conditional_kurtosis=103.7 (>|100.0|) | 3/11 |
| `x5_zum_downside_seed20` | conditional_kurtosis=112.6 (>|100.0|) | 3/11 |
| `x5_zum_downside_seed25` | conditional_kurtosis=114.7 (>|100.0|) | 4/11 |
| `x5_zum_downside_seed5` | conditional_kurtosis=102.6 (>|100.0|) | 3/11 |
| `x5_zum_none_seed19` | aggregational_gaussianity=1666.0 (>|1000.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `x5_zum_downside` | 27 | **5.22** | [4.63, 5.81] | 1.63 | 9 | 1 | 3 |
| `x5_zum_none` | 29 | **5.03** | [4.52, 5.55] | 1.43 | 8 | 1 | 1 |
| `spx_zum_downside` | 25 | **5.00** | [4.40, 5.64] | 1.58 | 9 | 2 | 5 |
| `spx_zum_none` | 28 | **4.64** | [4.14, 5.11] | 1.34 | 6 | 0 | 2 |
| `x5_zum_abs` | 21 | **4.14** | [3.52, 4.76] | 1.49 | 7 | 0 | 9 |
| `spx_zum_abs` | 27 | **4.04** | [3.41, 4.67] | 1.72 | 7 | 0 | 3 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `spx_zum_downside_seed0` | **9/11** |
| `x5_zum_downside_seed26` | **9/11** |
| `spx_zum_downside_seed4` | **8/11** |
| `x5_zum_none_seed22` | **8/11** |
| `spx_zum_abs_seed0` | **7/11** |
| `spx_zum_abs_seed16` | **7/11** |
| `spx_zum_downside_seed12` | **7/11** |
| `x5_zum_abs_seed8` | **7/11** |
| `x5_zum_downside_seed11` | **7/11** |
| `x5_zum_downside_seed13` | **7/11** |

