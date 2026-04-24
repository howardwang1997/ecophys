# Lux-Marchesi 1999 baseline vs real-market reference values

10 realizations × 20000 steps at dt=0.01. Lux-Marchesi entries show mean ± std across realizations.

| metric | Cont 2001 expected | Lux-Marchesi 1999 | SPX daily | SPY daily | BTC 1m | ETH 1m |
|---|---|---|---|---|---|---|
| #1 ACF(r) | <0.05 | +0.055 ± 0.051 | +0.060 | +0.054 | +0.007 | +0.007 |
| #2 α (Hill) | [3, 5] | +5.837 ± 0.281 | +2.673 | +2.766 | +2.679 | +2.781 |
| #3 skew | <0 (daily equity) | -0.001 ± 0.032 | -0.645 | -0.574 | -1.635 | -1.909 |
| #4 Δκ agg | >0 | -4.763 ± 3.649 | +15.475 | +14.106 | +58.195 | +143.389 |
| #5 Fano | >1 | +3.092 ± 4.043 | +7.544 | +7.683 | +36.516 | +34.186 |
| #6 ⟨ACF(r²)⟩ | >0.05 | +0.024 ± 0.040 | +0.221 | +0.217 | +0.108 | +0.063 |
| #7 κ GARCH-std | >0, < unconditional | +0.022 ± 0.058 | +2.475 | +2.443 | +11.108 | +4.835 |
| #8 H DFA|r| | [0.55, 0.80] | +0.576 ± 0.094 | +0.982 | +0.976 | +0.919 | +0.898 |
| #9 ΣLev | <0 (daily) | -0.046 ± 0.196 | -0.863 | -0.894 | -0.338 | -0.357 |
| #10 corr(V,|r|) | [0.2, 0.6] | +0.043 ± 0.040 | — | +0.571 | +0.630 | +0.599 |
| #11 Zumbach D | >0 (indices) | -0.006 ± 0.008 | -0.050 | -0.052 | -0.020 | -0.003 |


## Did Lux-Marchesi reproduce the target stylized fact?

| metric | target property | LM outcome | OK? |
|---|---|---|---|
| #1 ACF(r) | <0.05 | +0.055 | ✗ |
| #2 α (Hill) | [3, 5] | +5.837 | ✓ |
| #3 skew | <0 (daily equity) | -0.001 | ✓ |
| #4 Δκ agg | >0 | -4.763 | ✗ |
| #5 Fano | >1 | +3.092 | ✓ |
| #6 ⟨ACF(r²)⟩ | >0.05 | +0.024 | ✗ |
| #7 κ GARCH-std | >0, < unconditional | +0.022 | ✓ |
| #8 H DFA|r| | [0.55, 0.80] | +0.576 | ✓ |
| #9 ΣLev | <0 (daily) | -0.046 | ✓ |
| #10 corr(V,|r|) | [0.2, 0.6] | +0.043 | ✗ |
| #11 Zumbach D | >0 (indices) | -0.006 | ≈0 |
