# Score — 093_5asset_traditional_baselines

Discovered 100 runs, 45 with eval, 11 rejected for numerical instability (34 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `trad_ar1sv_btcusdt_seed0` | conditional_kurtosis=147.0 (>|100.0|) | 3/11 |
| `trad_ar1sv_btcusdt_seed1` | conditional_kurtosis=146.8 (>|100.0|) | 2/11 |
| `trad_ar1sv_btcusdt_seed2` | conditional_kurtosis=222.8 (>|100.0|) | 2/11 |
| `trad_ar1sv_btcusdt_seed3` | conditional_kurtosis=104.2 (>|100.0|) | 3/11 |
| `trad_ar1sv_btcusdt_seed4` | conditional_kurtosis=102.6 (>|100.0|) | 3/11 |
| `trad_ar1sv_gold_seed0` | conditional_kurtosis=140.1 (>|100.0|) | 4/11 |
| `trad_ar1sv_gold_seed2` | conditional_kurtosis=111.5 (>|100.0|) | 3/11 |
| `trad_ar1sv_spx_seed0` | conditional_kurtosis=140.1 (>|100.0|) | 4/11 |
| `trad_ar1sv_spx_seed1` | conditional_kurtosis=103.4 (>|100.0|) | 2/11 |
| `trad_ar1sv_spx_seed2` | conditional_kurtosis=153.7 (>|100.0|) | 3/11 |
| `trad_ar1sv_spx_seed3` | conditional_kurtosis=104.5 (>|100.0|) | 3/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `trad_garch_spx` | 5 | **4.60** | [3.40, 5.80] | 1.52 | 6 | 0 | 0 |
| `trad_garch_btcusdt` | 5 | **4.20** | [3.20, 5.20] | 1.30 | 6 | 0 | 0 |
| `trad_ar1sv_spx` | 1 | **4.00** | [4.00, 4.00] | 0.00 | 4 | 0 | 4 |
| `trad_garch_gold` | 5 | **3.40** | [3.00, 3.80] | 0.55 | 4 | 0 | 0 |
| `trad_ar1sv_gold` | 3 | **3.00** | [2.00, 4.00] | 1.00 | 4 | 0 | 2 |
| `trad_gbm_btcusdt` | 5 | **2.80** | [2.40, 3.00] | 0.45 | 3 | 0 | 0 |
| `trad_gbm_gold` | 5 | **2.80** | [2.40, 3.00] | 0.45 | 3 | 0 | 0 |
| `trad_gbm_spx` | 5 | **2.80** | [2.40, 3.00] | 0.45 | 3 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `trad_garch_btcusdt_seed4` | **6/11** |
| `trad_garch_spx_seed0` | **6/11** |
| `trad_garch_spx_seed4` | **6/11** |
| `trad_garch_btcusdt_seed0` | **5/11** |
| `trad_garch_spx_seed2` | **5/11** |
| `trad_ar1sv_gold_seed4` | **4/11** |
| `trad_ar1sv_spx_seed4` | **4/11** |
| `trad_garch_btcusdt_seed2` | **4/11** |
| `trad_garch_gold_seed0` | **4/11** |
| `trad_garch_gold_seed4` | **4/11** |

