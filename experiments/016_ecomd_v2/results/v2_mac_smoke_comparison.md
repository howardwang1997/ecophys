# EcoMD v2 eval — v2_mac_smoke

| metric | rule | sim | pass? |
|---|---|---|---|
| #1 ACF(r) | <lambda> | +0.018±0.002 | ✓ |
| #2 α Hill | <lambda> | +7.005±0.298 | ✗ |
| #3 skew | <lambda> | +0.019±0.012 | ✗ |
| #4 Δκ agg | <lambda> | -0.513±0.408 | ✗ |
| #5 Fano | <lambda> | +0.923±0.100 | ✗ |
| #6 ⟨ACF(r²)⟩ | <lambda> | +0.009±0.005 | ✗ |
| #7 κ GARCH-std | <lambda> | -0.624±0.039 | ✓ |
| #8 H DFA|r| | <lambda> | +0.568±0.030 | ✓ |
| #9 ΣLev | <lambda> | -0.071±0.020 | ✓ |
| #10 corr(V,|r|) | <lambda> | +0.042±0.028 | ✗ |
| #11 Zumbach D | <lambda> | -0.015±0.019 | ✗ |
| **Total** | | | **4/11** |

## v2 diagnostics (Goodhart protection)

- **ACF shape loss** (peak/tail ratio penalty): 1.243  (0 = passed; >0 = flat curve)
- **Ljung-Box p-value** (r² at lag 10): 2.50e-01  (<0.05 = rejects white noise)
- **Reject white noise** fraction over realizations: 0%