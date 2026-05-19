# Score — 090c_n50_confirm_and_ar1clip_combo

Discovered 150 runs, 150 with eval, 5 rejected for numerical instability (145 counted in stats below).

## Rejected (numerical instability)
Excluded from mean/max because conditional_kurtosis>100, aggregational_gaussianity>1000, or any fact NaN/inf.

| run | reason | raw_score |
|---|---|---:|
| `pair_AB_reref_seed32` | conditional_kurtosis=284.3 (>|100.0|) | 5/11 |
| `pair_ar1clip05_b3_seed6` | conditional_kurtosis=103.6 (>|100.0|) | 4/11 |
| `pair_ar1clip05_zumdn_seed2` | conditional_kurtosis=119.4 (>|100.0|) | 5/11 |
| `pair_ar1clip05_zumdn_seed29` | conditional_kurtosis=113.0 (>|100.0|) | 2/11 |
| `zumdn_solo_n30_seed39` | conditional_kurtosis=125.2 (>|100.0|) | 5/11 |

## Per-cell summary (stability filter applied)
| cell | n_seeds | mean n/11 | 95% CI | std | max | #(≥8) | rejected |
|---|---:|---:|---|---:|---:|---:|---:|
| `zumdn_solo_n30` | 19 | **5.00** | [4.47, 5.53] | 1.15 | 7 | 0 | 1 |
| `pair_ar1clip03_zumdn` | 30 | **4.67** | [4.13, 5.23] | 1.58 | 8 | 2 | 0 |
| `pair_zumdn_b3` | 20 | **4.50** | [4.05, 5.00] | 1.15 | 7 | 0 | 0 |
| `pair_ar1clip05_b3` | 29 | **4.38** | [3.86, 4.90] | 1.45 | 8 | 1 | 1 |
| `pair_AB_reref` | 19 | **4.05** | [3.21, 4.89] | 1.96 | 8 | 1 | 1 |
| `pair_ar1clip05_zumdn` | 28 | **3.64** | [3.07, 4.21] | 1.54 | 7 | 0 | 2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `pair_AB_reref_seed41` | **8/11** |
| `pair_ar1clip03_zumdn_seed13` | **8/11** |
| `pair_ar1clip03_zumdn_seed21` | **8/11** |
| `pair_ar1clip05_b3_seed13` | **8/11** |
| `pair_AB_reref_seed44` | **7/11** |
| `pair_ar1clip03_zumdn_seed23` | **7/11** |
| `pair_ar1clip03_zumdn_seed6` | **7/11** |
| `pair_ar1clip03_zumdn_seed9` | **7/11** |
| `pair_ar1clip05_b3_seed7` | **7/11** |
| `pair_ar1clip05_b3_seed8` | **7/11** |

