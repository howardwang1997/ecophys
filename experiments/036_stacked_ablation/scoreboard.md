# Score — 036_stacked_ablation

Discovered 40 runs, 28 with eval.

## Stacked-winner ablation — which knob breaks the stack?
Reference: stacked-full (035) mean 2.40/11. Look for cells
where mean RECOVERS to ≥ 4-5/11 — that knob is the saboteur.

| cell | n_seeds | mean n/11 | 95% CI | std |
|---|---:|---:|---|---:|
| `no_chunk128` | 10 | **3.20** | [2.10, 4.30] | 1.93 |
| `no_h96` | 8 | **3.00** | [2.25, 3.62] | 1.07 |
| `no_init01` | 10 | **2.20** | [1.50, 2.90] | 1.23 |

## Top 10 individual runs
| run | n/11 |
|---|---:|
| `abl_no_chunk128_seed1` | **6/11** |
| `abl_no_chunk128_seed3` | **5/11** |
| `abl_no_chunk128_seed7` | **5/11** |
| `abl_no_chunk128_seed0` | **4/11** |
| `abl_no_chunk128_seed6` | **4/11** |
| `abl_no_h96_seed0` | **4/11** |
| `abl_no_h96_seed2` | **4/11** |
| `abl_no_h96_seed5` | **4/11** |
| `abl_no_init01_seed4` | **4/11** |
| `abl_no_chunk128_seed2` | **3/11** |

