# Score — 098c_zumdn_fine_grid_n30

Discovered 180 runs, 180 with eval, 6 rejected for numerical instability (174 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `zumdn_s060_lam095_seed11` | conditional_kurtosis=153.2 (>|100.0|) | 6/11 |
| `zumdn_s060_lam095_seed22` | conditional_kurtosis=119.9 (>|100.0|) | 3/11 |
| `zumdn_s060_lam095_seed24` | conditional_kurtosis=132.8 (>|100.0|) | 6/11 |
| `zumdn_s100_lam085_seed27` | conditional_kurtosis=141.5 (>|100.0|) | 3/11 |
| `zumdn_s100_lam092_seed6` | conditional_kurtosis=112.2 (>|100.0|) | 4/11 |
| `zumdn_s120_lam095_seed4` | conditional_kurtosis=138.0 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `zumdn_s085_lam095` | 30 | **5.07** | [4.50, 5.63] | 1.62 | 9 | 1 | 0 |
| `zumdn_s100_lam097` | 30 | **4.97** | [4.37, 5.60] | 1.77 | 9 | 2 | 0 |
| `zumdn_s100_lam092` | 29 | **4.79** | [4.31, 5.28] | 1.35 | 8 | 1 | 1 |
| `zumdn_s100_lam085` | 29 | **4.69** | [4.24, 5.14] | 1.26 | 7 | 0 | 1 |
| `zumdn_s060_lam095` | 27 | **4.63** | [4.11, 5.11] | 1.33 | 7 | 0 | 3 |
| `zumdn_s120_lam095` | 29 | **4.62** | [4.07, 5.17] | 1.54 | 7 | 0 | 1 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `zumdn_s085_lam095_seed0` | **9/11** |
| `zumdn_s100_lam097_seed26` | **9/11** |
| `zumdn_s100_lam092_seed9` | **8/11** |
| `zumdn_s100_lam097_seed29` | **8/11** |
| `zumdn_s060_lam095_seed20` | **7/11** |
| `zumdn_s085_lam095_seed10` | **7/11** |
| `zumdn_s085_lam095_seed21` | **7/11** |
| `zumdn_s085_lam095_seed28` | **7/11** |
| `zumdn_s085_lam095_seed29` | **7/11** |
| `zumdn_s085_lam095_seed4` | **7/11** |

