# Stage 3 real-data pilot — does the EcoMD driven-transient appear in real markets? (2026-06-19)

**NCS Gate 2 test.** Windowed + regime-level Hill α on real 1-minute crypto crash windows (free
Binance public API): **Luna** (2022-05, UST depeg, BTC −30% / ETH −36%) and **FTX** (2022-11, BTC
−24% / ETH −31%), plus a matched **calm control** (2023-07, BTC rangebound). Data: `data/real/`,
fetch `scripts/fetch_crash_windows.py`.

## Result — the driven transient does NOT replicate in real returns (robust)

**Sliding-window α(t) (W=720, 1m):** estimator-noise-dominated; all three episodes (incl. calm)
wander α≈1.5–4.2 with no clean crash-timed dip. Inconclusive at this resolution.

**Robust regime-level Hill (single estimate per regime, thousands of pts):**

| episode | pre α | crash α | post α | Δcrash |
|---|---|---|---|---|
| Luna BTC | 2.54 | **3.97** | 3.74 | **+1.43** (tail *lighter*) |
| Luna ETH | 2.64 | **4.40** | 3.64 | **+1.76** |
| FTX BTC | 2.84 | 2.68 | 2.38 | −0.16 |
| FTX ETH | 2.89 | 2.66 | 2.88 | −0.23 |
| calm null | — | — | — | 2.63 ± 0.17 |

**Vol-standardized (r / EWMA|r|, removes the high-vol→lighter-Hill confound):** Luna still
*lightens* (3.42→4.47, Δ+1.05); FTX flat (Δ+0.19/−0.20) inside the calm null (3.36±0.37). The
negative is **not** a vol artifact.

## Interpretation

Real crashes do **not** drive the α-dip-and-recover that EcoMD shows. Real fat tails are
approximately **stationary** (cube-law-ish α≈2.5–3 raw / ≈3.4 standardized, in calm **and** crash) —
the established Gabaix–Plerou–Stanley inverse-cubic universality. The EcoMD driven-transient is a
property **of the simulator**, which (deliberately, het_mass off — see the burn-in finding) has **no
stationary heavy-tail source**, so it can only produce heavy tails transiently (burn-in or shock).
Real markets have such a source, so their tail is always ≈ cube.

## Venue implication (the honest call)

- **NCS Gate 2 (real-market anchor) does NOT pass.** Paper A cannot honestly be sold as "controlled
  experiments reveal driven-transient heavy tails in **financial markets**." The data contradicts it.
- **The defensible Paper A is simulator-physics + a model–reality gap:** *in EcoMD, heavy tails are a
  driven transient and the steady state is light-tailed — unlike real markets, whose cube-law tail is
  stationary; this controlled discrepancy localizes a missing stationary heavy-tail mechanism in this
  class of differentiable market simulators.* That is a genuine **NeurIPS/ICML methods + computational
  -science** result (it includes the burn-in measurement correction + the shock-protocol toolkit), not
  a Nature-CS/Physics market discovery.

## Caveats on this negative (honest)

- (Initial 2 episodes superseded by the broadened test below.)

## Broadened + formally tested (5 episodes + null distribution) — negative CONFIRMED

Per the "broaden before deciding" call: extended to **5 crypto crashes** (COVID-2020 −56%, China-ban
-2021 −47%, Celsius/3AC-2022 −41%, Luna, FTX) + a **formal null-distribution test**
(`scripts/null_test_crash_tails.py`). Statistic Δα = α(crash 2d) − α(pre 5d), vol-standardized; null
= the same window-pair slid across a 3-month calm stretch (n=170, null Δα = +0.02 ± 0.43). The
driven-transient predicts Δα ≪ 0 (heavier at the crash).

| episode | Δα | z | verdict |
|---|---|---|---|
| COVID 2020 | −0.07 | −0.2 | flat |
| China-ban 2021 | −0.91 | −2.2 | heavier (p=0.01) — the only hit |
| Celsius 2022 | +0.83 | +1.9 | **lighter** |
| Luna 2022 | +1.05 | +2.4 | **lighter** |
| FTX 2022 | +0.19 | +0.4 | flat |

**Pooled z = +1.03** (slightly *lighter*, opposite to the prediction). Only 1/5 supports the
transient — within the false-positive rate for 5 tests, offset by 2 significant opposite-direction
results. **The negative is robust and formally established.** Real return tails are stationary
cube-law across calm and crash.

## Remaining caveats (honest, narrow)

- Crypto only (free-intraday limit; historical equity minute needs the unbought FirstRate data). But
  5 episodes incl. the most violent crypto crashes, formally tested → equity is unlikely to overturn.
- The transient could in principle live in a non-return observable (order-flow imbalance / L2 depth)
  we don't have (Tardis L2). A *future*, different claim — not this pilot.
