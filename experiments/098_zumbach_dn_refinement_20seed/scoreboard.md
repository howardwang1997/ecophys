# Score — 098_zumbach_dn_refinement_20seed

Discovered 100 runs, 100 with eval, 9 rejected for numerical instability (91 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `zumdn_s050_lam085_seed3` | conditional_kurtosis=279.7 (>|100.0|) | 5/11 |
| `zumdn_s050_lam090_seed3` | conditional_kurtosis=199.2 (>|100.0|) | 7/11 |
| `zumdn_s075_lam085_seed4` | conditional_kurtosis=247.1 (>|100.0|) | 5/11 |
| `zumdn_s075_lam095_seed1` | conditional_kurtosis=114.8 (>|100.0|) | 5/11 |
| `zumdn_s075_lam095_seed2` | conditional_kurtosis=118.1 (>|100.0|) | 7/11 |
| `zumdn_s100_lam085_seed0` | conditional_kurtosis=124.0 (>|100.0|) | 5/11 |
| `zumdn_s100_lam095_seed3` | conditional_kurtosis=193.7 (>|100.0|) | 6/11 |
| `zumdn_s150_lam090_seed0` | conditional_kurtosis=180.4 (>|100.0|) | 7/11 |
| `zumdn_s200_lam090_seed0` | conditional_kurtosis=101.9 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `zumdn_s075_lam095` | 3 | **6.67** | [5.00, 8.00] | 1.53 | 8 | 1 | 2 |
| `zumdn_s100_lam095` | 4 | **5.50** | [3.75, 6.75] | 1.73 | 7 | 0 | 1 |
| `zumdn_s050_lam090` | 4 | **5.25** | [3.00, 6.75] | 2.22 | 7 | 0 | 1 |
| `zumdn_s050_lam099` | 5 | **5.20** | [4.40, 6.20] | 1.10 | 7 | 0 | 0 |
| `zumdn_s100_lam090` | 5 | **5.20** | [3.80, 6.40] | 1.64 | 7 | 0 | 0 |
| `zumdn_s200_lam085` | 5 | **5.20** | [4.00, 6.40] | 1.48 | 7 | 0 | 0 |
| `zumdn_s075_lam099` | 5 | **5.00** | [4.00, 5.80] | 1.22 | 6 | 0 | 0 |
| `zumdn_s100_lam099` | 5 | **5.00** | [4.00, 5.80] | 1.22 | 6 | 0 | 0 |
| `zumdn_s150_lam095` | 5 | **5.00** | [2.80, 7.20] | 2.83 | 8 | 2 | 0 |
| `zumdn_s150_lam099` | 5 | **5.00** | [3.40, 6.20] | 1.87 | 7 | 0 | 0 |
| `zumdn_s200_lam099` | 5 | **5.00** | [3.80, 6.20] | 1.58 | 7 | 0 | 0 |
| `zumdn_s200_lam095` | 5 | **4.80** | [3.20, 6.40] | 2.17 | 7 | 0 | 0 |
| `zumdn_s050_lam095` | 5 | **4.60** | [4.00, 5.40] | 0.89 | 6 | 0 | 0 |
| `zumdn_s150_lam085` | 5 | **4.40** | [2.80, 6.00] | 2.07 | 7 | 0 | 0 |
| `zumdn_s100_lam085` | 4 | **4.25** | [3.50, 5.00] | 0.96 | 5 | 0 | 1 |
| `zumdn_s075_lam090` | 5 | **4.20** | [3.00, 5.20] | 1.48 | 6 | 0 | 0 |
| `zumdn_s075_lam085` | 4 | **4.00** | [3.25, 4.75] | 0.82 | 5 | 0 | 1 |
| `zumdn_s050_lam085` | 4 | **3.75** | [2.50, 5.25] | 1.71 | 6 | 0 | 1 |
| `zumdn_s150_lam090` | 4 | **3.75** | [2.00, 5.50] | 2.06 | 6 | 0 | 1 |
| `zumdn_s200_lam090` | 4 | **3.00** | [2.00, 4.25] | 1.41 | 5 | 0 | 1 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `zumdn_s075_lam095_seed3` | **8/11** |
| `zumdn_s150_lam095_seed2` | **8/11** |
| `zumdn_s150_lam095_seed4` | **8/11** |
| `zumdn_s050_lam090_seed0` | **7/11** |
| `zumdn_s050_lam099_seed0` | **7/11** |
| `zumdn_s075_lam095_seed4` | **7/11** |
| `zumdn_s100_lam090_seed4` | **7/11** |
| `zumdn_s100_lam095_seed4` | **7/11** |
| `zumdn_s150_lam085_seed2` | **7/11** |
| `zumdn_s150_lam099_seed2` | **7/11** |

