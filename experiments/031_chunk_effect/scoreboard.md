# Score — 031_chunk_effect

Discovered 15 runs, 15 with eval.

## Group by chunk
| chunk | n_seeds | mean n/11 | 95% CI | std |
|---:|---:|---:|---|---:|
| 24 | 5 | **2.60** | [1.60, 3.60] | 1.34 |
| 64 | 5 | **2.60** | [1.80, 3.00] | 0.89 |
| 128 | 5 | **2.80** | [1.60, 4.40] | 1.92 |

## Per-seed across chunks (looking for seed dominance)
| seed | chunk=24 | chunk=64 | chunk=128 |
|---:|---:|---:|---:|
| 0 | 2/11 | 3/11 | 1/11 |
| 1 | 2/11 | 1/11 | 6/11 |
| 2 | 1/11 | 3/11 | 3/11 |
| 3 | 4/11 | 3/11 | 2/11 |
| 4 | 4/11 | 3/11 | 2/11 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `pc_chunk128_seed1` | **6/11** |
| `pc_chunk24_seed3` | **4/11** |
| `pc_chunk24_seed4` | **4/11** |
| `pc_chunk128_seed2` | **3/11** |
| `pc_chunk64_seed0` | **3/11** |
| `pc_chunk64_seed2` | **3/11** |
| `pc_chunk64_seed3` | **3/11** |
| `pc_chunk64_seed4` | **3/11** |
| `pc_chunk128_seed3` | **2/11** |
| `pc_chunk128_seed4` | **2/11** |

