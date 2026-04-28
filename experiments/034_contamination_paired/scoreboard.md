# Score — 034_contamination_paired

Discovered 20 runs, 20 with eval.

## Contamination paired — default vs sprint2 (custom autograd)
| variant | n_seeds | mean n/11 | 95% CI | std |
|---|---:|---:|---|---:|
| `default` | 10 | **2.40** | [1.80, 3.10] | 1.17 |
| `sprint2` | 10 | **3.20** | [2.40, 4.00] | 1.40 |

### Per-seed paired comparison
| seed | default | sprint2 | delta |
|---:|---:|---:|---:|
| 0 | 2/11 | 2/11 | 0 |
| 1 | 5/11 | 1/11 | -4 |
| 2 | 1/11 | 1/11 | 0 |
| 3 | 2/11 | 4/11 | +2 |
| 4 | 2/11 | 4/11 | +2 |
| 5 | 3/11 | 4/11 | +1 |
| 6 | 1/11 | 4/11 | +3 |
| 7 | 3/11 | 3/11 | 0 |
| 8 | 3/11 | 5/11 | +2 |
| 9 | 2/11 | 4/11 | +2 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `ct_default_seed1` | **5/11** |
| `ct_sprint2_seed8` | **5/11** |
| `ct_sprint2_seed3` | **4/11** |
| `ct_sprint2_seed4` | **4/11** |
| `ct_sprint2_seed5` | **4/11** |
| `ct_sprint2_seed6` | **4/11** |
| `ct_sprint2_seed9` | **4/11** |
| `ct_default_seed5` | **3/11** |
| `ct_default_seed7` | **3/11** |
| `ct_default_seed8` | **3/11** |

