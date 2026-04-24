# Stylized Facts Reference Values — Paper A Table 1 candidate

Generated: 2026-04-23  |  11 metrics per Cont (2001)  |  hardware: Mac / conda env `ecophys`

| dataset | period | n | #1 ACF(r) | #2 α tail | #3 skew | #4 Δκ agg | #5 Fano | #6 ACF(r²) | #7 κ GARCH-std | #8 H DFA|r| | #9 ΣLev | #10 corr(V,|r|) | #11 Zumbach D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| spx | 2015-2026_daily | 2841 | +0.060 | +2.673 | -0.645 | +15.475 | +7.544 | +0.221 | +2.475 | +0.982 | -0.863 | — | -0.050 |
| spy | 2015-2026_daily | 2841 | +0.054 | +2.766 | -0.574 | +14.106 | +7.683 | +0.217 | +2.443 | +0.976 | -0.894 | +0.571 | -0.052 |
| btcusdt | 2024Q1_1m | 131039 | +0.007 | +2.679 | -1.635 | +58.195 | +36.516 | +0.108 | +11.108 | +0.919 | -0.338 | +0.630 | -0.020 |
| ethusdt | 2024Q1_1m | 131039 | +0.007 | +2.781 | -1.909 | +143.389 | +34.186 | +0.063 | +4.835 | +0.898 | -0.357 | +0.599 | -0.003 |


## Cont 2001 / MITRE 2023 expected ranges

- #1 ACF(r) near 0 (< 0.05 typically); Ljung-Box p > 0.05
- #2 α ∈ [3, 5]
- #3 skew < 0 for daily equity indices; may be ≈0 or positive for crypto / intraday individual stocks (MITRE 2023)
- #4 Δκ = κ(scale=1) − κ(scale=max) > 0 (Gaussianisation with aggregation)
- #5 Fano > 1 (clustering of extremes); MITRE reports 2.6–4.7 at 1-min Dow stocks
- #6 ⟨ACF(r²)⟩ > 0.05 (volatility clustering)
- #7 excess κ of GARCH residuals > 0 but < unconditional κ
- #8 H ∈ [0.55, 0.80] on stationary samples; values near 1 indicate non-stationarity
- #9 ΣLev < 0 for daily equity indices; weak/absent at intraday (MITRE 2023)
- #10 corr(V, |r|) > 0 (≈0.2–0.6) in clock time
- #11 Zumbach D > 0 for indices; weak for individual intraday

## DFA Hurst multi-order investigation (H ≈ 0.98 anomaly)

| dataset | H(order=1) | H(order=2) | H(order=3) | Δ(1-3) |
|---|---|---|---|---|
| spx_daily_2015_2026 | +0.982 | +1.011 | +1.008 | -0.026 |
| spy_daily_2015_2026 | +0.976 | +1.004 | +1.003 | -0.027 |
| btc_1m_2024Q1 | +0.919 | +0.910 | +0.884 | +0.035 |
| eth_1m_2024Q1 | +0.898 | +0.879 | +0.857 | +0.041 |

Large Δ(1-3) → order-1 DFA was picking up across-window trend rather than long memory.
