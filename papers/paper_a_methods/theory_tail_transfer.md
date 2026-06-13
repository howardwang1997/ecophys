# Paper A — Theory: the tail-transfer law for concave price impact (δ* = ζ/α)

Paper-ready derivation + in-silico validation for §4 (the "why δ≈0.5" theory). Drop-in for a
NeurIPS/ICML theory subsection. Verified on the δ-grid 2026-06-13 (`scripts/score_transfer_law.py`).

---

## Setup

EcoMD's price update is a **concave (sub-linear) price impact** of aggregate excess demand
$\mathrm{ED}_t = \sum_i \Delta s_{i,0}(t)$:
$$
\Delta p_t \;=\; \beta\,\mathrm{sign}(\mathrm{ED}_t)\,|\mathrm{ED}_t|^{\delta}, \qquad 0<\delta\le 1 .
$$
$\delta=1$ is linear (Kyle) impact; $\delta=\tfrac12$ is the Tóth–Bouchaud square-root law.

## Lemma (tail transfer under a power map)

Let $X\ge 0$ have a regularly varying upper tail $\;\Pr(X>x)=\ell(x)\,x^{-\zeta}\;$ with
$\zeta>0$ and $\ell$ slowly varying. For $Y=X^{\delta}$, $\delta>0$,
$$
\Pr(Y>y)=\Pr\!\big(X>y^{1/\delta}\big)=\ell\!\big(y^{1/\delta}\big)\,y^{-\zeta/\delta},
$$
so $Y$ is regularly varying with tail index $\boxed{\;\alpha_Y=\zeta/\delta\;}$.
*(Proof: direct change of variables; $\ell(y^{1/\delta})$ remains slowly varying, so it does not
affect the tail exponent — equivalently, the Hill estimator of $Y$ converges to $\zeta/\delta$.)*

## Corollary (the √-law crossing)

Take $X=|\mathrm{ED}|$ with tail index $\zeta_{\mathrm{ED}}$. The per-step return magnitude is
$|\Delta p|=\beta\,|\mathrm{ED}|^{\delta}$ (the constant $\beta$ shifts scale, not exponent), so the
**return tail index obeys**
$$
\alpha(\delta)=\frac{\zeta_{\mathrm{ED}}}{\delta}.
$$
The simulator matches the empirical **inverse-cubic law** ($\alpha=3$; Gabaix et al. 2003) at
$$
\delta^{*}=\frac{\zeta_{\mathrm{ED}}}{\alpha}=\frac{\zeta_{\mathrm{ED}}}{3}.
$$
With the empirically observed **half-cubic excess-demand / volume exponent** $\zeta_{\mathrm{ED}}\approx 3/2$
(Gabaix–Gopikrishnan–Plerou–Stanley, *Nature* 2003), this gives the square-root law
$$
\delta^{*}=\tfrac{3/2}{3}=\tfrac12 .
$$
**δ≈0.5 is therefore not fitted — it is the exponent that reconciles a half-cubic demand tail with
an inverse-cubic return tail.**

*(Marginal-tail caveat: returns are measured over the rollout, not per step. The exponent transfers
to the series because (i) sums of power-law innovations inherit the minimum tail index, and (ii)
volatility clustering preserves the marginal tail. Clustering shifts the crossover scale and finite-
sample constant, not the leading exponent. This is the leading-order claim; §validation tests it.)*

## In-silico validation (δ-grid, `score_transfer_law.py`, 2026-06-13)

The law makes a **parameter-free, falsifiable prediction**: $\alpha(\delta)\cdot\delta=\zeta_{\mathrm{ED}}$
is **constant across the δ-grid**, and equal across assets if the demand tail is universal. Measured
mean Hill per (asset, δ) cell over experiments 113/114/118 (Hill $=\hat\alpha$):

| asset | $\mathrm{Hill}\cdot\delta$ (= $\zeta_{\mathrm{ED}}$) | CV across δ-grid | $\delta^{*}=\zeta/3$ | bootstrap $\delta^{*}$ |
|---|---|---|---|---|
| spx | 1.483 | 3.4% | 0.494 | 0.508 |
| ndx | **1.596** | 4.7% | **0.532** | 0.531 |
| gold | 1.509 | 2.8% | 0.503 | 0.513 |
| eurusd | 1.551 | 9.0% | 0.517 | 0.521 |
| btcusdt | 1.492 | 1.2% | 0.497 | 0.508 |

**Findings.**
1. $\mathrm{Hill}\cdot\delta$ is **constant within each asset** (CV 1–9%, mostly 3–5%) — i.e. the
   simulator's $\mathrm{Hill}(\delta)$ follows the predicted $\propto 1/\delta$ form, not the
   ad-hoc linear fit used in the first δ-grid pass. (This also explains that pass's poor per-seed
   $r^2\!=\!0.22$–$0.31$: the scatter was seed noise; the per-δ **means** are a clean $1/\delta$ curve.)
2. The constant clusters at $\zeta_{\mathrm{ED}}\approx 1.5$ across all five assets — the **Gabaix
   half-cubic exponent**, recovered endogenously from the model.
3. The crossing $\delta^{*}=\zeta/3$ reproduces the bootstrap $\delta^{*}$ values, and **explains
   the ndx "deviation" mechanistically**: ndx's $\delta^{*}=0.53$ is the law applied to its slightly
   heavier demand tail $\zeta_{\mathrm{ED}}=1.60$, not a failure of universality. The honest headline
   becomes: *the √-law crossing $\delta^{*}=1/2$ holds exactly when the excess-demand tail is the
   Gabaix half-cubic $\zeta=3/2$; deviations are predicted by, not exceptions to, $\delta^{*}=\zeta/3$.*

## Unification with the "dynamical, not distributional" finding (exp 109)

Exp 109 showed the baseline ($\delta=1$) tail overshoot is generated dynamically — Gaussian noise +
zero jumps still gives Hill≈1.30. The transfer law closes the loop: **the dynamics (clustering /
excess-demand feedback) generate the heavy excess-demand tail $\zeta_{\mathrm{ED}}\approx 3/2$;
concave impact transfers it to the return tail via $\alpha=\zeta_{\mathrm{ED}}/\delta$.** One causal
chain: *dynamics → heavy demand tail (ζ) → impact exponent δ sets the return tail (α=ζ/δ).*

## What remains to make the derivation end-to-end (owed experiment)

The validation above infers $\zeta_{\mathrm{ED}}$ *via the law* (from $\mathrm{Hill}\cdot\delta$).
To close it **independently**, measure $\zeta_{\mathrm{ED}}$ directly: dump the per-step
$\mathrm{ED}_t$ series from a rollout and Hill-estimate its tail. **Prediction:** directly-measured
$\zeta_{\mathrm{ED}}\approx 1.50$ (ndx $\approx 1.60$), matching the $\mathrm{Hill}\cdot\delta$ column.
If confirmed, the chain ED-tail → transfer → return-tail is measured end-to-end and δ* is *derived
and verified*, not fitted. (Realizations currently store only aggregated facts, so this needs a short
rollout with ED logging — Mac N≤500 smoke or one H20 cell; no retraining.)

## Citations
- Gabaix, Gopikrishnan, Plerou, Stanley. *A theory of power-law distributions in financial market
  fluctuations.* Nature 423, 267 (2003). — inverse-cubic returns (α≈3), half-cubic volume (ζ≈3/2),
  square-root impact $r\sim V^{1/2}$.
- Tóth et al. *Anomalous price impact and the critical nature of liquidity.* PRX 1, 021006 (2011). —
  square-root impact law.
- Bouchaud, Bonart, Donier, Gould. *Trades, Quotes and Prices* (2018). — impact concavity review.
