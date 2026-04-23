# Cont (2001) — "Empirical properties of asset returns: stylized facts and statistical issues"

**Full cite**: Cont, R. (2001). *Quantitative Finance*, Vol. 1, No. 2, pp. 223–236. IOP Publishing. PII: S1469-7688(01)21683-2.

**Read date**: 2026-04-23
**Authority status**: the canonical reference for stylized facts of financial returns. Over 10,000 citations. Every market simulator paper cites this.
**Sources used for these notes**: (a) Cont 2001 PDF directly (pages 1 and references), (b) Vyetrenko-Byrd-Petosa-Mahfouz-Dervovic-Veloso-Balch 2020 ICAIF (ABIDES stylized-facts benchmark) + Vyetrenko "Revisiting Cont's Stylized Facts for Modern Stock Markets" (MITRE 2023, [arXiv:2311.07738](https://arxiv.org/html/2311.07738v2)) — this MITRE paper explicitly re-tests all 11 facts on modern Dow-30 data and is the best secondary source for which facts still hold and which don't.

---

## Paper setup

- Log returns: r(t, Δt) = X(t + Δt) − X(t), where X(t) = ln S(t)
- Time scale Δt variable: seconds → months. Cont emphasizes that empirical properties **depend on Δt**.
- Approach: non-parametric / semi-parametric — "let the data speak". Avoids committing to a parametric family prematurely.
- Goal of paper: synthesize empirical regularities across markets/instruments into a **set of constraints that any stochastic model of returns must satisfy**. This is exactly the test suite we need for EcoMD.

## The 11 Stylized Facts — exact enumeration

| # | Fact | Cont's definition (quoted) | Our measurement | Typical value (modern Dow 30, MITRE 2023) |
|---|---|---|---|---|
| **1** | **Absence of autocorrelations** | "Linear autocorrelations of asset returns are often insignificant, except for very small intraday timescales (≃20 min) for which microstructure effects come into play" | Pearson ACF(r_t, r_{t−τ}) at τ ≥ few minutes | First-lag negative (bid-ask bounce), decays to ±0.02 by lag 3; essentially white noise beyond 5–8 lags at 1 min |
| **2** | **Heavy tails** | "Distribution of returns displays a power-law / Pareto-like tail, with finite tail index higher than two and less than five" | Hill estimator → tail index α; excess kurtosis | α ∈ [3, 5] across markets; 1-min kurtosis 10–1000; trade-level up to 10⁶ |
| **3** | **Gain/loss asymmetry** | "Large drawdowns in stock prices (and stock index values) but not equally large upward movements" | Skewness + tail quantile comparison | **Modern update**: does NOT hold cleanly for individual intraday stocks (MITRE 2023). Holds for indices + daily. |
| **4** | **Aggregational Gaussianity** | "As timescale Δt over which returns are calculated increases, distribution looks more and more like a normal distribution" | Kurtosis(Δt) decreasing in Δt; KS distance to normal | 1-min kurtosis > 60-min; normalized returns within Gaussian range at Δt ≥ 20 min |
| **5** | **Intermittency** | "High degree of variability, as quantified by the presence of irregular bursts in time series of a wide variety of volatility estimators" | Fano factor F(Δt) = σ²/⟨N⟩ for extreme returns >99th percentile | 1-min Fano 2.6–4.7; trade-level 27–60. >>1 → strong clustering of extreme events |
| **6** | **Volatility clustering** | "Different measures of volatility display positive autocorrelation over several days, which quantifies the fact that high-volatility events tend to cluster in time" | ACF(\|r_t\|, \|r_{t−τ}\|) or ACF(r_t², r_{t−τ}²) | Positive, slow decay, log-log linear plateau — core empirical motivation for GARCH family |
| **7** | **Conditional heavy tails** | "Even after correcting returns for volatility clustering (e.g. via GARCH-type models), residual time series still exhibit heavy tails. However, the tails are less heavy than in the unconditional distribution of returns" | Kurtosis of GARCH-normalized residuals | Kurtosis reduced but still > 3; sub-Gaussian but not Gaussian |
| **8** | **Slow decay of autocorrelation in absolute returns** | "Autocorrelation function of absolute returns decays slowly as a function of the time lag, roughly as a power law with an exponent β ∈ [0.2, 0.4]. This is sometimes interpreted as a sign of long-range dependence" | ACF(\|r_t\|, \|r_{t−τ}\|) ~ τ^{−β}; DFA Hurst exponent on \|r\| | β ∈ [0.2, 0.4]; Hurst H on \|r\| ≈ 0.6–0.7 → long memory |
| **9** | **Leverage effect** | "Most measures of volatility of an asset are negatively correlated with the returns of that asset" | L(τ) = corr(r_t, \|r_{t+τ}\|²) or corr(r_t, σ_{t+τ}); expect negative at small τ | **Modern update**: does NOT hold cleanly at intraday frequency for individual stocks (MITRE 2023; Blanc et al. 2019 corroborate). Holds for daily returns on indices. |
| **10** | **Volume/volatility correlation** | "Trading volume is correlated with all measures of volatility" | Pearson corr(V_t, \|r_t\|) or cross-correlation | Strong positive in clock-time; weaker and variable in event-time (trade-clock) |
| **11** | **Asymmetry in timescales** | "Coarse-grained measures of volatility predict fine-scale volatility better than the other way around" | A(τ) = corr(coarse-σ_t, fine-σ_{t+τ}); D(τ) = A(τ) − A(−τ); expect D(τ) < 0 | **Modern update**: not consistently observed for individual Dow 30 stocks (MITRE 2023). Known as the **Zumbach effect**; robust for aggregated/index data. |

---

## Statistical pitfalls Cont explicitly warns about

1. **Non-stationarity**: return distributions vary across regimes. Any single-sample estimator needs to account for regime changes. **Our plan response**: hold-out 2019 as "normal period" reference; keep crash windows separate; report per-regime statistics.

2. **Heavy tails + finite-sample bias in moment estimators**: sample kurtosis and variance can be biased/unstable when the true tail index is low (α close to 4, kurtosis not well-defined for α ≤ 4). Must use **tail-index estimation (Hill)** in preference to raw moments. Hill itself has k-choice bias → diagnostic plots needed. **Our plan response**: we've implemented `hill_tail_index` with a full Hill-plot diagnostic (see `ecomd/eval/stylized_facts.py`).

3. **Dependence structure invalidates iid-based tests**: volatility clustering breaks standard IID assumptions under which many tests (KS, Ljung-Box CI, ACF CI) are derived. CIs for ACF of r² need HAC / block-bootstrap. **Our plan response**: use bootstrap for CIs, not parametric.

4. **Time-scale confounds**: clock-time vs. event-time (trade-count) gives different answers. Cont mentions this; MITRE 2023 shows it's even more acute in modern HFT data. **Our plan response**: report both in our evaluation table.

5. **Aggregational Gaussianity doesn't help for risk**: the law of large numbers says r(Δt) becomes approximately Gaussian as Δt grows, but relevant risk horizons (daily → weekly) still show strong non-Gaussianity. Don't use CLT as an excuse to use Gaussian models at daily horizon.

## Critique of models (Cont's targets)

Cont explicitly or implicitly rules out these as insufficient:

- **Gaussian / Brownian motion**: fails #2 (heavy tails), #4 (doesn't explain why non-Gaussian at short Δt), #6 (no clustering)
- **Stable (Lévy α < 2) distributions**: tail exponent α < 2 implies **infinite variance**, inconsistent with aggregational Gaussianity (#4). Short-scale scaling might fit but long-scale fails.
- **Simple GARCH(1,1)**: captures #6 (clustering) by construction, partial #2 (heavy tails via conditional vol), but residuals fail #7 (still heavy-tailed), and does not reproduce #11 (volatility asymmetry in time scales). Cannot produce power-law ACF #8 — GARCH ACF is exponential.
- **Long-memory GARCH (FIGARCH)**: fixes #8 partially but still exponential-like residuals.
- **Stochastic volatility (Heston, Hull-White)**: similar issues as GARCH for #7 and #11.

**Implication for EcoMD**: a market simulator that reproduces only #2 + #6 is not news. The bar is at least #1, #2, #4, #6, #7, #8 cleanly + some of {#3, #5, #9, #10, #11}.

---

## What we must do in EcoPhys Phase 1

### Implement measurement (11 metrics total)

Already implemented in `ecomd/eval/stylized_facts.py` (v0 = first 4):
- ✅ #2 Hill tail index (`hill_tail_index`)
- ✅ #6 Volatility clustering (`acf_squared_returns`)
- ✅ #8 Long memory via DFA Hurst (`dfa_hurst`)
- ✅ #9 Leverage effect (`leverage_effect`) — note modern caveat: may be weak for individual intraday

Still to implement in Phase 1:
- ✅ #1 Absence of autocorrelation — `autocorr_returns` (mean |ACF| + Ljung-Box Q/p)
- ✅ #3 Gain/loss asymmetry — `gain_loss_asymmetry` (skew + left/right tail-quantile ratio)
- ✅ #4 Aggregational Gaussianity — `aggregational_gaussianity` (κ curve + KS-to-normal across scales)
- ✅ #5 Intermittency — `intermittency_fano` (Fano factor for >99th percentile extremes)
- ✅ #7 Conditional heavy tails — `conditional_kurtosis` (GARCH(1,1) residual κ via arch package)
- ✅ #10 Volume/volatility correlation — `volume_volatility_corr` (contemp + cross-lag)
- ✅ #11 Asymmetry in timescales — `zumbach_asymmetry` with gap to remove overlap bias
- ✅ `compute_all(returns, volume=None)` orchestrator runs all 11, catches per-metric errors

**Multi-order DFA investigation (2026-04-23, same day)**:
Implemented `dfa_hurst_multi_order(series, orders=(1,2,3))`. Empirical finding on SPX/SPY 2015-2026 daily + BTC/ETH 2024Q1 1m:
- Full-series DFA-1 gives H ≈ 0.98 (SPX/SPY) and 0.90 (crypto). Multi-order detrending barely changes this (Δ(1→3) ≤ 0.04), **ruling out polynomial trend as the cause**.
- Sub-period DFA on 500-day chunks of SPX daily: H1 median = 0.83, H2 median = 0.69 — right in Cont's expected [0.55, 0.80] range after higher-order detrending.
- The chunk covering the COVID crash (2020-Q1 to 2021-Q2, index 1000-1500) has H1 = 1.22 and dominates the full-series estimate.
- **Conclusion**: full-series H inflation is driven by non-polynomial regime shifts that DFA can't correct. For Paper A, report full H + per-regime H + DFA-2 to give a complete picture. Segmented estimation is the right default for any crisis-containing window.

### Reference-value tables (Phase 1 M1 deliverable)

Run all 11 metrics on:
- SPX daily 1990–2025 (yfinance)
- SPX minute 2008–2025 (T1.a when vendor delivers)
- BTC 1m 2020–2025 (Binance free)
- ETH 1m 2020–2025 (Binance free)
- Per-regime slices: 2003–2007 (calm), 2008–2009 (GFC), 2010 (Flash Crash window), 2017–2019 (calm), 2020 (COVID), 2022 (crypto crises)

Store results at `<data_dir>/reference_values/{dataset}/{period}/stylized_facts.json`. These become Table 1 in Paper A.

### Critical design decisions informed by these notes

1. **Tier the evaluation**: Facts #1/2/4/6/7/8/10 are "must pass" (MITRE 2023 confirms they hold). Facts #3/5/9/11 are "timescale/scope-dependent" — we should report them but not penalize the model for missing them at intraday scale.
2. **Always report per-Δt**: every metric should be a curve over Δt, not a single number. Aggregational Gaussianity (#4) is only visible as a curve.
3. **Handle the clock-time vs event-time confound**: at minute resolution and below, report both. For our agent-based simulator, the natural tick is event-time, so we may need to re-bin to clock-time for direct comparison.
4. **Bootstrap everywhere**: CIs for ACF/Hurst/Hill all need bootstrap because of dependence.

---

## Bibliographic pointers for deeper dives

Cont's own follow-ups on this subject (all worth reading next):
- Cont R, Potters M, Bouchaud J-P (1997) "Scaling in Stock Market Data: Stable Laws and Beyond" — sets up the scaling analysis.
- Cont R (1999) "Statistical properties of financial time series" (lecture notes) — more extended treatment.
- Cont R (2000) "Multiresolution analysis of financial time series" — wavelet-based re-analysis.
- Cont R, Bouchaud J-P (2000) "Herd behavior and aggregate fluctuations in financial markets" — agent-based model that reproduces some of these facts.

Related references in Cont 2001 we should chase:
- Plerou et al. (1999) PRL 83, 1471 — random matrix theory + cross-correlations (ref 103 in the paper)
- Mandelbrot 1963, 1997, 2001 — original heavy-tail papers + multifractal review
- Lux 1997, Lux-Marchesi 1999 — agent-based precursors
- Bouchaud-Matacz-Potters 2001 on leverage effect — note it's a dedicated 2001 follow-up specifically on fact #9

---

## One-paragraph summary for papers

Cont's 2001 synthesis established the 11 stylized facts that any credible model of asset returns must satisfy: absence of linear autocorrelation, heavy tails (α ∈ [3,5]), gain/loss asymmetry, aggregational Gaussianity, intermittency, volatility clustering, conditional heavy tails, slow power-law decay of |r|-autocorrelation (β ∈ [0.2,0.4]), leverage effect, volume/volatility correlation, and Zumbach-style time-scale asymmetry. These facts are robust across markets (equities, FX, commodities) and timescales (intraday to monthly), and rule out Gaussian, stable-Lévy, and plain GARCH models as single-shot explanations. Modern high-frequency reanalyses (Vyetrenko et al. 2023) confirm 8 of 11 facts hold for individual Dow-30 stocks at intraday timescales, while facts #3, #9, and #11 emerge only at coarser timescales or index-level aggregation — an important nuance for microstructure simulators.
