# Score — 098b_zumdn_dayshift_n30

Discovered 240 runs, 240 with eval, 8 rejected for numerical instability (232 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `zumdn_s075_lam095_seed1` | conditional_kurtosis=114.8 (>|100.0|) | 5/11 |
| `zumdn_s075_lam095_seed2` | conditional_kurtosis=118.4 (>|100.0|) | 7/11 |
| `zumdn_s075_lam095_seed29` | conditional_kurtosis=116.7 (>|100.0|) | 5/11 |
| `zumdn_s100_lam090_seed13` | conditional_kurtosis=165.9 (>|100.0|) | 7/11 |
| `zumdn_s100_lam090_seed14` | conditional_kurtosis=131.6 (>|100.0|) | 6/11 |
| `zumdn_s100_lam090_seed20` | conditional_kurtosis=178.9 (>|100.0|) | 6/11 |
| `zumdn_s100_lam095_seed3` | conditional_kurtosis=193.7 (>|100.0|) | 6/11 |
| `zumdn_s150_lam095_seed19` | aggregational_gaussianity=1627.1 (>|1000.0|) | 4/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `zumdn_s075_lam095` | 27 | **5.59** | [4.96, 6.19] | 1.62 | 8 | 4 | 3 |
| `zumdn_s100_lam095` | 29 | **5.21** | [4.69, 5.72] | 1.47 | 8 | 1 | 1 |
| `zumdn_s050_lam099` | 30 | **5.13** | [4.57, 5.67] | 1.63 | 8 | 2 | 0 |
| `zumdn_s075_lam099` | 30 | **5.07** | [4.67, 5.47] | 1.17 | 8 | 1 | 0 |
| `zumdn_s100_lam099` | 30 | **4.77** | [4.27, 5.23] | 1.36 | 7 | 0 | 0 |
| `zumdn_s150_lam095` | 29 | **4.69** | [4.17, 5.24] | 1.49 | 8 | 2 | 1 |
| `baseline_v3` | 30 | **4.57** | [4.10, 5.07] | 1.36 | 8 | 2 | 0 |
| `zumdn_s100_lam090` | 27 | **4.56** | [4.07, 5.04] | 1.34 | 8 | 1 | 3 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `baseline_v3_seed13` | **8/11** |
| `baseline_v3_seed22` | **8/11** |
| `zumdn_s050_lam099_seed24` | **8/11** |
| `zumdn_s050_lam099_seed26` | **8/11** |
| `zumdn_s075_lam095_seed14` | **8/11** |
| `zumdn_s075_lam095_seed26` | **8/11** |
| `zumdn_s075_lam095_seed3` | **8/11** |
| `zumdn_s075_lam095_seed4` | **8/11** |
| `zumdn_s075_lam099_seed13` | **8/11** |
| `zumdn_s100_lam090_seed4` | **8/11** |

