# Score — 099_memk_refinement_5seed

Discovered 100 runs, 100 with eval, 3 rejected for numerical instability (97 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `memk_s025_lam099_seed0` | aggregational_gaussianity=1596.0 (>|1000.0|) | 4/11 |
| `memk_s050_lam095_seed0` | aggregational_gaussianity=1005.9 (>|1000.0|) | 5/11 |
| `memk_s150_lam095_seed0` | aggregational_gaussianity=1031.3 (>|1000.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `memk_s025_lam095` | 5 | **5.80** | [4.40, 7.20] | 1.92 | 8 | 1 | 0 |
| `memk_s050_lam090` | 5 | **5.80** | [4.80, 7.00] | 1.48 | 8 | 1 | 0 |
| `memk_s075_lam095` | 5 | **5.80** | [4.60, 7.20] | 1.64 | 8 | 1 | 0 |
| `memk_s100_lam085` | 5 | **5.80** | [4.80, 6.80] | 1.30 | 7 | 0 | 0 |
| `memk_s050_lam099` | 5 | **5.60** | [5.20, 6.00] | 0.55 | 6 | 0 | 0 |
| `memk_s100_lam099` | 5 | **5.40** | [5.00, 5.80] | 0.55 | 6 | 0 | 0 |
| `memk_s075_lam090` | 5 | **5.20** | [4.20, 6.20] | 1.30 | 7 | 0 | 0 |
| `memk_s075_lam099` | 5 | **5.20** | [4.60, 5.80] | 0.84 | 6 | 0 | 0 |
| `memk_s150_lam099` | 5 | **5.20** | [4.60, 5.80] | 0.84 | 6 | 0 | 0 |
| `memk_s025_lam090` | 5 | **5.00** | [3.40, 6.20] | 1.87 | 7 | 0 | 0 |
| `memk_s100_lam090` | 5 | **5.00** | [4.40, 5.60] | 0.71 | 6 | 0 | 0 |
| `memk_s100_lam095` | 5 | **5.00** | [4.40, 5.60] | 0.71 | 6 | 0 | 0 |
| `memk_s050_lam085` | 5 | **4.80** | [3.40, 5.80] | 1.64 | 6 | 0 | 0 |
| `memk_s050_lam095` | 4 | **4.50** | [3.25, 6.25] | 1.73 | 7 | 0 | 1 |
| `memk_s150_lam090` | 5 | **4.40** | [3.60, 5.40] | 1.14 | 6 | 0 | 0 |
| `memk_s025_lam099` | 4 | **4.25** | [2.75, 5.00] | 1.50 | 5 | 0 | 1 |
| `memk_s150_lam095` | 4 | **4.25** | [2.50, 6.25] | 2.06 | 7 | 0 | 1 |
| `memk_s075_lam085` | 5 | **4.20** | [3.20, 5.20] | 1.30 | 6 | 0 | 0 |
| `memk_s025_lam085` | 5 | **4.00** | [2.80, 5.20] | 1.58 | 6 | 0 | 0 |
| `memk_s150_lam085` | 5 | **3.60** | [2.60, 4.60] | 1.34 | 5 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `memk_s025_lam095_seed4` | **8/11** |
| `memk_s050_lam090_seed4` | **8/11** |
| `memk_s075_lam095_seed4` | **8/11** |
| `memk_s025_lam090_seed1` | **7/11** |
| `memk_s025_lam095_seed2` | **7/11** |
| `memk_s050_lam095_seed3` | **7/11** |
| `memk_s075_lam090_seed4` | **7/11** |
| `memk_s075_lam095_seed3` | **7/11** |
| `memk_s100_lam085_seed0` | **7/11** |
| `memk_s100_lam085_seed4` | **7/11** |

