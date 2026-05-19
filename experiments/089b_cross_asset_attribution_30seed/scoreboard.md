# Score — 089b_cross_asset_attribution_30seed

Discovered 480 runs, 240 with eval, 7 rejected for numerical instability (233 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `attr_btcusdt_ar1_s05_seed27` | aggregational_gaussianity=1527.2 (>|1000.0|) | 4/11 |
| `attr_btcusdt_ar1_s05_seed29` | aggregational_gaussianity=1433.7 (>|1000.0|) | 5/11 |
| `attr_btcusdt_b3_k3_seed18` | aggregational_gaussianity=1056.2 (>|1000.0|) | 3/11 |
| `attr_btcusdt_levy_a17_seed16` | aggregational_gaussianity=1221.6 (>|1000.0|) | 4/11 |
| `attr_btcusdt_zumbach_dn_s10_seed22` | conditional_kurtosis=131.7 (>|100.0|) | 5/11 |
| `attr_btcusdt_zumbach_dn_s10_seed3` | conditional_kurtosis=144.0 (>|100.0|) | 7/11 |
| `attr_btcusdt_zumbach_dn_s10_seed9` | conditional_kurtosis=115.5 (>|100.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `attr_btcusdt_b3_k3` | 29 | **5.10** | [4.62, 5.55] | 1.29 | 7 | 0 | 1 |
| `attr_btcusdt_asymdrag_a06` | 30 | **4.93** | [4.40, 5.43] | 1.46 | 7 | 0 | 0 |
| `attr_btcusdt_zumbach_dn_s10` | 27 | **4.81** | [4.26, 5.37] | 1.52 | 8 | 1 | 3 |
| `attr_btcusdt_powerlaw_a15` | 30 | **4.73** | [4.13, 5.33] | 1.70 | 8 | 1 | 0 |
| `attr_btcusdt_baseline_v3` | 30 | **4.70** | [4.10, 5.27] | 1.64 | 8 | 1 | 0 |
| `attr_btcusdt_levy_a17` | 29 | **4.66** | [4.14, 5.17] | 1.45 | 7 | 0 | 1 |
| `attr_btcusdt_memk_l095_s10` | 30 | **4.63** | [4.23, 5.07] | 1.19 | 7 | 0 | 0 |
| `attr_btcusdt_ar1_s05` | 28 | **4.43** | [3.96, 4.89] | 1.23 | 7 | 0 | 2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `attr_btcusdt_baseline_v3_seed22` | **8/11** |
| `attr_btcusdt_powerlaw_a15_seed14` | **8/11** |
| `attr_btcusdt_zumbach_dn_s10_seed27` | **8/11** |
| `attr_btcusdt_ar1_s05_seed13` | **7/11** |
| `attr_btcusdt_ar1_s05_seed21` | **7/11** |
| `attr_btcusdt_asymdrag_a06_seed13` | **7/11** |
| `attr_btcusdt_asymdrag_a06_seed15` | **7/11** |
| `attr_btcusdt_asymdrag_a06_seed6` | **7/11** |
| `attr_btcusdt_b3_k3_seed0` | **7/11** |
| `attr_btcusdt_b3_k3_seed14` | **7/11** |

