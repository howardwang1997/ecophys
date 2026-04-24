# Three-way comparison: Real data / Lux-Marchesi 1999 / GARCH(1,1)-t

GARCH: fitted per-dataset, 10 × 20000 step synthetic realizations, t-innovations.
Lux-Marchesi: single parameter set (paper defaults), 10 × 20k realisations (from experiment 001).

## Fitted GARCH(1,1)-t parameters

| dataset | ω | α | β | α+β | ν |
|---|---|---|---|---|---|
| spx | 2.13e-02 | 0.167 | 0.828 | 0.995 | 5.42 |
| spy | 2.22e-02 | 0.171 | 0.824 | 0.995 | 5.44 |
| btcusdt | 1.54e-04 | 0.200 | 0.780 | 0.980 | 4.67 |
| ethusdt | 1.65e-04 | 0.100 | 0.880 | 0.980 | 5.23 |


## spx (2015-2026_daily)

| metric | expected | real | GARCH(1,1)-t | LM99 (asset-agnostic) |
|---|---|---|---|---|
| #1 ACF(r) | <0.05 | +0.060 | +0.019 ± 0.007 | +0.055 ± 0.051 |
| #2 α Hill | [3, 5] | +2.673 | +2.132 ± 0.213 | +5.837 ± 0.281 |
| #3 skew | <0 daily equity | -0.645 | -0.375 ± 1.015 | -0.001 ± 0.032 |
| #4 Δκ agg | >0 | +15.475 | +46.599 ± 24.412 | -4.763 ± 3.649 |
| #5 Fano | >1 | +7.544 | +20.229 ± 8.725 | +3.092 ± 4.043 |
| #6 ⟨ACF(r²)⟩ | >0.05 | +0.221 | +0.209 ± 0.026 | +0.024 ± 0.040 |
| #7 κ GARCH-std | >0, <uncond | +2.475 | +3.433 ± 0.826 | +0.022 ± 0.058 |
| #8 H DFA|r| | [0.55, 0.80] | +0.982 | +0.967 ± 0.032 | +0.576 ± 0.094 |
| #9 ΣLev | <0 daily | -0.863 | -0.082 ± 0.256 | -0.046 ± 0.196 |
| #10 corr(V,|r|) | [0.2, 0.6] | — | — | +0.043 ± 0.040 |
| #11 Zumbach D | >0 indices | -0.050 | -0.073 ± 0.015 | -0.006 ± 0.008 |

## spy (2015-2026_daily)

| metric | expected | real | GARCH(1,1)-t | LM99 (asset-agnostic) |
|---|---|---|---|---|
| #1 ACF(r) | <0.05 | +0.054 | +0.019 ± 0.007 | +0.055 ± 0.051 |
| #2 α Hill | [3, 5] | +2.766 | +2.149 ± 0.219 | +5.837 ± 0.281 |
| #3 skew | <0 daily equity | -0.574 | -0.388 ± 1.010 | -0.001 ± 0.032 |
| #4 Δκ agg | >0 | +14.106 | +46.055 ± 24.849 | -4.763 ± 3.649 |
| #5 Fano | >1 | +7.683 | +19.559 ± 8.468 | +3.092 ± 4.043 |
| #6 ⟨ACF(r²)⟩ | >0.05 | +0.217 | +0.208 ± 0.025 | +0.024 ± 0.040 |
| #7 κ GARCH-std | >0, <uncond | +2.443 | +3.394 ± 0.819 | +0.022 ± 0.058 |
| #8 H DFA|r| | [0.55, 0.80] | +0.976 | +0.959 ± 0.033 | +0.576 ± 0.094 |
| #9 ΣLev | <0 daily | -0.894 | -0.087 ± 0.258 | -0.046 ± 0.196 |
| #10 corr(V,|r|) | [0.2, 0.6] | +0.571 | — | +0.043 ± 0.040 |
| #11 Zumbach D | >0 indices | -0.052 | -0.073 ± 0.015 | -0.006 ± 0.008 |

## btcusdt (2024Q1_1m)

| metric | expected | real | GARCH(1,1)-t | LM99 (asset-agnostic) |
|---|---|---|---|---|
| #1 ACF(r) | <0.05 | +0.007 | +0.018 ± 0.008 | +0.055 ± 0.051 |
| #2 α Hill | [3, 5] | +2.679 | +2.221 ± 0.211 | +5.837 ± 0.281 |
| #3 skew | <0 daily equity | -1.635 | -0.951 ± 2.551 | -0.001 ± 0.032 |
| #4 Δκ agg | >0 | +58.195 | +91.382 ± 115.465 | -4.763 ± 3.649 |
| #5 Fano | >1 | +36.516 | +12.815 ± 4.451 | +3.092 ± 4.043 |
| #6 ⟨ACF(r²)⟩ | >0.05 | +0.108 | +0.162 ± 0.025 | +0.024 ± 0.040 |
| #7 κ GARCH-std | >0, <uncond | +11.108 | +5.219 ± 1.141 | +0.022 ± 0.058 |
| #8 H DFA|r| | [0.55, 0.80] | +0.919 | +0.864 ± 0.031 | +0.576 ± 0.094 |
| #9 ΣLev | <0 daily | -0.338 | -0.125 ± 0.279 | -0.046 ± 0.196 |
| #10 corr(V,|r|) | [0.2, 0.6] | +0.630 | — | +0.043 ± 0.040 |
| #11 Zumbach D | >0 indices | -0.020 | -0.060 ± 0.020 | -0.006 ± 0.008 |

## ethusdt (2024Q1_1m)

| metric | expected | real | GARCH(1,1)-t | LM99 (asset-agnostic) |
|---|---|---|---|---|
| #1 ACF(r) | <0.05 | +0.007 | +0.011 ± 0.002 | +0.055 ± 0.051 |
| #2 α Hill | [3, 5] | +2.781 | +2.779 ± 0.176 | +5.837 ± 0.281 |
| #3 skew | <0 daily equity | -1.909 | -0.106 ± 0.502 | -0.001 ± 0.032 |
| #4 Δκ agg | >0 | +143.389 | +12.696 ± 10.521 | -4.763 ± 3.649 |
| #5 Fano | >1 | +34.186 | +10.460 ± 3.835 | +3.092 ± 4.043 |
| #6 ⟨ACF(r²)⟩ | >0.05 | +0.063 | +0.155 ± 0.030 | +0.024 ± 0.040 |
| #7 κ GARCH-std | >0, <uncond | +4.835 | +3.605 ± 0.540 | +0.022 ± 0.058 |
| #8 H DFA|r| | [0.55, 0.80] | +0.898 | +0.887 ± 0.029 | +0.576 ± 0.094 |
| #9 ΣLev | <0 daily | -0.357 | -0.040 ± 0.109 | -0.046 ± 0.196 |
| #10 corr(V,|r|) | [0.2, 0.6] | +0.599 | — | +0.043 ± 0.040 |
| #11 Zumbach D | >0 indices | -0.003 | -0.059 ± 0.015 | -0.006 ± 0.008 |

## Scoreboard — how many facts each simulator matches (loose tolerance)

Counts metrics where the simulator's mean lands within broad expected range.
Note: LM99 has no per-asset fit — it's an asset-agnostic model run with paper defaults.

| metric check | GARCH scores (per dataset) | LM99 score (once) |
|---|---|---|
| #1 ACF(r) | ✓ ✓ ✓ ✓ (spx/spy/btcusdt/ethusdt) | ✓ |
| #2 α Hill | ✓ ✓ ✓ ✓ (spx/spy/btcusdt/ethusdt) | ✓ |
| #3 skew | ✓ ✓ ✓ ✓ (spx/spy/btcusdt/ethusdt) | ✗ |
| #4 Δκ agg | ✓ ✓ ✓ ✓ (spx/spy/btcusdt/ethusdt) | ✗ |
| #5 Fano | ✓ ✓ ✓ ✓ (spx/spy/btcusdt/ethusdt) | ✓ |
| #6 ⟨ACF(r²)⟩ | ✓ ✓ ✓ ✓ (spx/spy/btcusdt/ethusdt) | ✗ |
| #7 κ GARCH-std | ✗ ✗ ✗ ✗ (spx/spy/btcusdt/ethusdt) | ✓ |
| #8 H DFA|r| | ✗ ✗ ✗ ✗ (spx/spy/btcusdt/ethusdt) | ✓ |
| #9 ΣLev | ✓ ✓ ✓ ✗ (spx/spy/btcusdt/ethusdt) | ✗ |
| #10 corr(V,|r|) | ✗ ✗ ✗ ✗ (spx/spy/btcusdt/ethusdt) | ✗ |
| #11 Zumbach D | ✗ ✗ ✗ ✗ (spx/spy/btcusdt/ethusdt) | ✗ |

### Total matches


| model | spx | spy | btc | eth | LM99 |
|---|---|---|---|---|---|
| GARCH(1,1)-t fitted | 7/11 | 7/11 | 7/11 | 6/11 | — |
| LM99 asset-agnostic | — | — | — | — | 5/11 |