# Score — 092_5asset_replication_30seed

Discovered 600 runs, 600 with eval, 31 rejected for numerical instability (569 counted in stats below).

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
| `xa_eurusd_asym_seed18` | aggregational_gaussianity=1011.6 (>|1000.0|) | 5/11 |
| `xa_eurusd_b3_seed18` | aggregational_gaussianity=1080.9 (>|1000.0|) | 3/11 |
| `xa_eurusd_pair_zumdn_b3_seed16` | conditional_kurtosis=111.2 (>|100.0|) | 5/11 |
| `xa_eurusd_zumdn_seed25` | conditional_kurtosis=137.5 (>|100.0|) | 5/11 |
| `xa_eurusd_zumdn_seed3` | conditional_kurtosis=137.7 (>|100.0|) | 8/11 |
| `xa_gold_asym_seed9` | aggregational_gaussianity=1046.7 (>|1000.0|) | 5/11 |
| `xa_gold_pair_zumdn_b3_seed11` | conditional_kurtosis=121.3 (>|100.0|) | 5/11 |
| `xa_gold_pair_zumdn_b3_seed14` | conditional_kurtosis=134.5 (>|100.0|) | 6/11 |
| `xa_gold_pair_zumdn_b3_seed2` | conditional_kurtosis=131.3 (>|100.0|) | 6/11 |
| `xa_gold_pair_zumdn_b3_seed22` | conditional_kurtosis=167.1 (>|100.0|) | 7/11 |
| `xa_gold_zumdn_seed14` | conditional_kurtosis=104.9 (>|100.0|) | 5/11 |
| `xa_gold_zumdn_seed22` | conditional_kurtosis=128.6 (>|100.0|) | 5/11 |
| `xa_gold_zumdn_seed4` | conditional_kurtosis=122.5 (>|100.0|) | 5/11 |
| `xa_gold_zumdn_seed9` | conditional_kurtosis=102.7 (>|100.0|) | 5/11 |
| `xa_ndx_asym_seed15` | aggregational_gaussianity=2045.8 (>|1000.0|) | 4/11 |
| `xa_ndx_asym_seed29` | aggregational_gaussianity=1077.1 (>|1000.0|) | 6/11 |
| `xa_ndx_asym_seed9` | aggregational_gaussianity=1031.2 (>|1000.0|) | 8/11 |
| `xa_ndx_b3_seed27` | aggregational_gaussianity=1023.8 (>|1000.0|) | 3/11 |
| `xa_ndx_pair_zumdn_b3_seed11` | conditional_kurtosis=115.0 (>|100.0|) | 5/11 |
| `xa_ndx_pair_zumdn_b3_seed22` | conditional_kurtosis=146.9 (>|100.0|) | 8/11 |
| `xa_spx_pair_zumdn_b3_seed2` | conditional_kurtosis=121.4 (>|100.0|) | 5/11 |
| `xa_spx_pair_zumdn_b3_seed22` | conditional_kurtosis=158.3 (>|100.0|) | 6/11 |
| `xa_spx_zumdn_seed3` | conditional_kurtosis=193.7 (>|100.0|) | 6/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `xa_gold_zumdn` | 26 | **5.96** | [5.38, 6.54] | 1.54 | 8 | 5 | 4 |
| `xa_eurusd_zumdn` | 28 | **5.36** | [4.86, 5.89] | 1.45 | 8 | 4 | 2 |
| `xa_spx_zumdn` | 29 | **5.24** | [4.69, 5.79] | 1.57 | 8 | 1 | 1 |
| `xa_spx_asym` | 30 | **5.20** | [4.47, 5.90] | 2.11 | 9 | 4 | 0 |
| `xa_ndx_pair_zumdn_b3` | 28 | **5.18** | [4.57, 5.82] | 1.72 | 8 | 4 | 2 |
| `xa_spx_b3` | 30 | **5.17** | [4.70, 5.63] | 1.32 | 8 | 1 | 0 |
| `xa_eurusd_asym` | 29 | **5.14** | [4.55, 5.72] | 1.64 | 8 | 2 | 1 |
| `xa_eurusd_pair_zumdn_b3` | 29 | **5.14** | [4.55, 5.72] | 1.62 | 8 | 4 | 1 |
| `xa_gold_asym` | 29 | **5.14** | [4.69, 5.59] | 1.25 | 8 | 1 | 1 |
| `xa_gold_pair_zumdn_b3` | 26 | **5.12** | [4.42, 5.77] | 1.77 | 9 | 1 | 4 |
| `xa_btcusdt_pair_zumdn_b3` | 26 | **5.08** | [4.35, 5.81] | 1.96 | 9 | 2 | 4 |
| `xa_btcusdt_b3` | 29 | **5.07** | [4.62, 5.48] | 1.22 | 7 | 0 | 1 |
| `xa_ndx_b3` | 29 | **4.93** | [4.41, 5.45] | 1.41 | 8 | 1 | 1 |
| `xa_ndx_zumdn` | 30 | **4.83** | [4.20, 5.47] | 1.80 | 8 | 4 | 0 |
| `xa_spx_pair_zumdn_b3` | 28 | **4.75** | [4.18, 5.36] | 1.67 | 8 | 2 | 2 |
| `xa_btcusdt_zumdn` | 27 | **4.70** | [4.11, 5.33] | 1.68 | 8 | 2 | 3 |
| `xa_btcusdt_asym` | 30 | **4.70** | [4.10, 5.23] | 1.62 | 7 | 0 | 0 |
| `xa_gold_b3` | 30 | **4.67** | [4.23, 5.10] | 1.27 | 7 | 0 | 0 |
| `xa_ndx_asym` | 27 | **4.63** | [3.93, 5.30] | 1.82 | 8 | 1 | 3 |
| `xa_eurusd_b3` | 29 | **4.45** | [3.97, 4.97] | 1.40 | 8 | 1 | 1 |

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
| `xa_eurusd_asym_seed25` | **8/11** |
| `xa_eurusd_asym_seed28` | **8/11** |
| `xa_eurusd_b3_seed14` | **8/11** |

