# Score — 092_5asset_replication_30seed

Discovered 600 runs, 360 with eval, 20 rejected for numerical instability (340 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `xa_btcusdt_b3_seed18` | aggregational_gaussianity=1055.5 (>|1000.0|) | 3/11 |
| `xa_btcusdt_pair_zumdn_b3_seed18` | conditional_kurtosis=110.3 (>|100.0|) | 6/11 |
| `xa_btcusdt_pair_zumdn_b3_seed19` | aggregational_gaussianity=1055.5 (>|1000.0|) | 5/11 |
| `xa_btcusdt_pair_zumdn_b3_seed22` | conditional_kurtosis=163.7 (>|100.0|) | 7/11 |
| `xa_btcusdt_pair_zumdn_b3_seed28` | conditional_kurtosis=119.4 (>|100.0|) | 5/11 |
| `xa_btcusdt_zumdn_seed22` | conditional_kurtosis=131.7 (>|100.0|) | 5/11 |
| `xa_btcusdt_zumdn_seed3` | conditional_kurtosis=144.1 (>|100.0|) | 7/11 |
| `xa_btcusdt_zumdn_seed9` | conditional_kurtosis=115.5 (>|100.0|) | 5/11 |
| `xa_gold_asym_seed9` | aggregational_gaussianity=1046.7 (>|1000.0|) | 5/11 |
| `xa_gold_pair_zumdn_b3_seed11` | conditional_kurtosis=121.3 (>|100.0|) | 5/11 |
| `xa_gold_pair_zumdn_b3_seed14` | conditional_kurtosis=134.5 (>|100.0|) | 6/11 |
| `xa_gold_pair_zumdn_b3_seed2` | conditional_kurtosis=131.3 (>|100.0|) | 6/11 |
| `xa_gold_pair_zumdn_b3_seed22` | conditional_kurtosis=167.1 (>|100.0|) | 7/11 |
| `xa_gold_zumdn_seed14` | conditional_kurtosis=104.9 (>|100.0|) | 5/11 |
| `xa_gold_zumdn_seed22` | conditional_kurtosis=128.6 (>|100.0|) | 5/11 |
| `xa_gold_zumdn_seed4` | conditional_kurtosis=122.5 (>|100.0|) | 5/11 |
| `xa_gold_zumdn_seed9` | conditional_kurtosis=102.7 (>|100.0|) | 5/11 |
| `xa_spx_pair_zumdn_b3_seed2` | conditional_kurtosis=121.4 (>|100.0|) | 5/11 |
| `xa_spx_pair_zumdn_b3_seed22` | conditional_kurtosis=158.3 (>|100.0|) | 6/11 |
| `xa_spx_zumdn_seed3` | conditional_kurtosis=193.7 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `xa_gold_zumdn` | 26 | **5.96** | [5.38, 6.54] | 1.54 | 8 | 5 | 4 |
| `xa_spx_zumdn` | 29 | **5.24** | [4.69, 5.79] | 1.57 | 8 | 1 | 1 |
| `xa_spx_asym` | 30 | **5.20** | [4.47, 5.90] | 2.11 | 9 | 4 | 0 |
| `xa_spx_b3` | 30 | **5.17** | [4.70, 5.63] | 1.32 | 8 | 1 | 0 |
| `xa_gold_asym` | 29 | **5.14** | [4.69, 5.59] | 1.25 | 8 | 1 | 1 |
| `xa_gold_pair_zumdn_b3` | 26 | **5.12** | [4.42, 5.77] | 1.77 | 9 | 1 | 4 |
| `xa_btcusdt_pair_zumdn_b3` | 26 | **5.08** | [4.35, 5.81] | 1.96 | 9 | 2 | 4 |
| `xa_btcusdt_b3` | 29 | **5.07** | [4.62, 5.48] | 1.22 | 7 | 0 | 1 |
| `xa_spx_pair_zumdn_b3` | 28 | **4.75** | [4.18, 5.36] | 1.67 | 8 | 2 | 2 |
| `xa_btcusdt_zumdn` | 27 | **4.70** | [4.11, 5.33] | 1.68 | 8 | 2 | 3 |
| `xa_btcusdt_asym` | 30 | **4.70** | [4.10, 5.23] | 1.62 | 7 | 0 | 0 |
| `xa_gold_b3` | 30 | **4.67** | [4.23, 5.10] | 1.27 | 7 | 0 | 0 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `xa_btcusdt_pair_zumdn_b3_seed27` | **9/11** |
| `xa_gold_pair_zumdn_b3_seed4` | **9/11** |
| `xa_spx_asym_seed14` | **9/11** |
| `xa_spx_asym_seed2` | **9/11** |
| `xa_btcusdt_pair_zumdn_b3_seed11` | **8/11** |
| `xa_btcusdt_zumdn_seed14` | **8/11** |
| `xa_btcusdt_zumdn_seed27` | **8/11** |
| `xa_gold_asym_seed12` | **8/11** |
| `xa_gold_zumdn_seed10` | **8/11** |
| `xa_gold_zumdn_seed2` | **8/11** |

