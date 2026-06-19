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

- 2 episodes, crypto only. A broader test (more episodes; equity minute via the planned FirstRate
  buy) would firm it up — but 2/2 clean crypto crashes contradict the prediction, robust to
  vol-standardization and to raw-vs-regime estimation.
- The transient could in principle live in a non-return observable (order-flow imbalance / L2 depth)
  we don't have yet (Tardis L2). That is a *future* direction, not a pilot result, and would be a
  different claim.
