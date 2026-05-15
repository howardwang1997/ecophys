# Attribution matrix — 089_attribution_50seed

Discovered 16 cells, 11 facts. Pass-rate = % of seeds whose aggregated fact value falls in band. Stability filter applied (same as `score_phase.py`).

## Per-cell × per-fact pass rate (%)
| cell | n | rej | ac_r | hill | g/l | agg | fano | ac² | ckur | hurs | lev | v·v | zum | mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `attr_zumbach_dn_s10` | 48 | 2 |  35 |   4 |  40 |  38 |  98 |  75 |  58 |  42 |  38 |  56 |  29 | **5.12** |
| `attr_b3_k3` | 50 | 0 |  30 |   6 |  42 |  36 | 100 |  72 |  64 |  62 |  38 |  38 |   8 | **4.96** |
| `attr_asymdrag_a06` | 48 | 2 |  12 |  21 |  62 |  29 |  92 |  62 |  44 |  35 |  77 |  54 |   2 | **4.92** |
| `attr_powerlaw_a15` | 50 | 0 |  42 |  12 |  38 |  22 | 100 |  62 |  62 |  62 |  36 |  48 |   4 | **4.88** |
| `attr_ar1_s05` | 49 | 1 |   2 |  63 |  63 |   6 | 100 |  96 |  20 |  27 |  63 |   4 |  43 | **4.88** |
| **attr_baseline_v3** | 49 | 1 |  24 |   6 |  53 |  22 | 100 |  65 |  67 |  55 |  49 |  33 |   6 | **4.82** |
| `attr_zumbach_s05` | 40 | 10 |  45 |  10 |  32 |  45 |  98 |  80 |  38 |  22 |  50 |  45 |  10 | **4.75** |
| `attr_inner_3` | 41 | 9 |  32 |  10 |  44 |  10 |  95 |  46 |  71 |  56 |  41 |  61 |   5 | **4.71** |
| `attr_levy_a17` | 49 | 1 |  18 |  10 |  47 |  33 | 100 |  69 |  69 |  41 |  37 |  37 |   4 | **4.65** |
| `attr_memk_l095_s10` | 50 | 0 |  28 |  20 |  34 |  26 | 100 |  64 |  54 |  52 |  30 |  32 |  16 | **4.56** |
| `attr_microstructure_r03` | 50 | 0 |  32 |   8 |  40 |  32 |  98 |  62 |  52 |  40 |  36 |  48 |   6 | **4.54** |
| `attr_ar1_s03` | 15 | 35 |  87 |  13 |  40 |  13 |  93 |   0 |  60 |  47 |  53 |  33 |   7 | **4.47** |
| `attr_zumbach_s10` | 41 | 9 |  46 |  22 |  15 |  49 |  98 |  83 |  37 |  17 |  34 |  29 |  10 | **4.39** |
| `attr_jump_l01` | 45 | 1 |  31 |   2 |  42 |  29 | 100 |  62 |  49 |  42 |  33 |  38 |   9 | **4.38** |
| `attr_zumbach_s20` | 43 | 7 |  42 |   7 |  16 |  40 |  93 |  65 |  47 |  21 |  35 |  35 |  12 | **4.12** |
| `attr_ar1_s08` | 42 | 8 |  29 |  17 |  26 |  19 |  90 |  40 |  69 |  36 |  14 |  33 |  19 | **3.93** |

## Δ vs baseline (percentage-point change in pass-rate)
Positive = mechanism PASSES this fact more than v3 baseline. Negative = mechanism BREAKS this fact relative to baseline.

| cell | n | rej | ac_r | hill | g/l | agg | fano | ac² | ckur | hurs | lev | v·v | zum | mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `attr_zumbach_dn_s10` | 48 | 2 | +11 |  -2 | -13 | +15 |  -2 | +10 |  -9 | -13 | -11 | +24 | +23 | **+0.31** |
| `attr_b3_k3` | 50 | 0 |  +6 |  -0 | -11 | +14 |  +0 |  +7 |  -3 |  +7 | -11 |  +5 |  +2 | **+0.14** |
| `attr_asymdrag_a06` | 48 | 2 | -12 | +15 |  +9 |  +7 |  -8 |  -3 | -24 | -20 | +28 | +22 |  -4 | **+0.10** |
| `attr_powerlaw_a15` | 50 | 0 | +18 |  +6 | -15 |  -0 |  +0 |  -3 |  -5 |  +7 | -13 | +15 |  -2 | **+0.06** |
| `attr_ar1_s05` | 49 | 1 | -22 | +57 | +10 | -16 |  +0 | +31 | -47 | -29 | +14 | -29 | +37 | **+0.06** |
| `attr_zumbach_s05` | 40 | 10 | +21 |  +4 | -21 | +23 |  -2 | +15 | -30 | -33 |  +1 | +12 |  +4 | **-0.07** |
| `attr_inner_3` | 41 | 9 |  +7 |  +4 |  -9 | -13 |  -5 | -19 |  +3 |  +1 |  -8 | +28 |  -1 | **-0.11** |
| `attr_levy_a17` | 49 | 1 |  -6 |  +4 |  -6 | +10 |  +0 |  +4 |  +2 | -14 | -12 |  +4 |  -2 | **-0.16** |
| `attr_memk_l095_s10` | 50 | 0 |  +4 | +14 | -19 |  +4 |  +0 |  -1 | -13 |  -3 | -19 |  -1 | +10 | **-0.26** |
| `attr_microstructure_r03` | 50 | 0 |  +8 |  +2 | -13 | +10 |  -2 |  -3 | -15 | -15 | -13 | +15 |  -0 | **-0.28** |
| `attr_ar1_s03` | 15 | 35 | +62 |  +7 | -13 |  -9 |  -7 | -65 |  -7 |  -8 |  +4 |  +1 |  +1 | **-0.35** |
| `attr_zumbach_s10` | 41 | 9 | +22 | +16 | -38 | +26 |  -2 | +18 | -31 | -38 | -15 |  -3 |  +4 | **-0.43** |
| `attr_jump_l01` | 45 | 1 |  +7 |  -4 | -11 |  +6 |  +0 |  -3 | -18 | -13 | -16 |  +5 |  +3 | **-0.44** |
| `attr_zumbach_s20` | 43 | 7 | +17 |  +1 | -37 | +17 |  -7 |  -0 | -21 | -34 | -14 |  +2 |  +6 | **-0.70** |
| `attr_ar1_s08` | 42 | 8 |  +4 | +11 | -27 |  -3 | -10 | -25 |  +2 | -19 | -35 |  +1 | +13 | **-0.89** |

## Per-fact biggest mover (most positive Δ from baseline)
| fact | best mechanism | Δ pass-rate |
|---|---|---:|
| `autocorr_returns` | `attr_ar1_s03` | +62 |
| `hill_tail_index` | `attr_ar1_s05` | +57 |
| `gain_loss_asymmetry` | `attr_ar1_s05` | +10 |
| `aggregational_gaussianity` | `attr_zumbach_s10` | +26 |
| `intermittency_fano` | `attr_b3_k3` | +0 |
| `acf_squared_returns` | `attr_ar1_s05` | +31 |
| `conditional_kurtosis` | `attr_inner_3` | +3 |
| `dfa_hurst_abs_r` | `attr_b3_k3` | +7 |
| `leverage_effect` | `attr_asymdrag_a06` | +28 |
| `volume_volatility_corr` | `attr_inner_3` | +28 |
| `zumbach_asymmetry` | `attr_ar1_s05` | +37 |

## ⚠️ Cells with >30% rejection rate (numerical instability)
- `attr_ar1_s03`: 35/50 (70%)

