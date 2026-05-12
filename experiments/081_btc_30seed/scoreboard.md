# Score — 081_btc_30seed

Discovered 60 runs, 60 with eval, 7 rejected for numerical instability (53 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `btc_v4combo_seed0` | conditional_kurtosis=413.6 (>|100.0|) | 5/11 |
| `btc_v4combo_seed10` | aggregational_gaussianity=1706.1 (>|1000.0|) | 4/11 |
| `btc_v4combo_seed13` | aggregational_gaussianity=1742.2 (>|1000.0|) | 4/11 |
| `btc_v4combo_seed15` | aggregational_gaussianity=1063.4 (>|1000.0|) | 7/11 |
| `btc_v4combo_seed17` | conditional_kurtosis=3333.4 (>|100.0|) | 5/11 |
| `btc_v4combo_seed27` | conditional_kurtosis=363.2 (>|100.0|) | 4/11 |
| `btc_v4combo_seed9` | aggregational_gaussianity=1200.0 (>|1000.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `btc_v4combo` | 23 | **5.39** | [4.87, 5.96] | 1.34 | 8 | 2 | 7 |
| `btc_baseline` | 30 | **4.80** | [4.27, 5.33] | 1.49 | 8 | 1 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `btc_baseline_seed22` | **8/11** |
| `btc_v4combo_seed24` | **8/11** |
| `btc_v4combo_seed26` | **8/11** |
| `btc_baseline_seed26` | **7/11** |
| `btc_v4combo_seed1` | **7/11** |
| `btc_v4combo_seed16` | **7/11** |
| `btc_v4combo_seed5` | **7/11** |
| `btc_baseline_seed1` | **6/11** |
| `btc_baseline_seed13` | **6/11** |
| `btc_baseline_seed14` | **6/11** |

