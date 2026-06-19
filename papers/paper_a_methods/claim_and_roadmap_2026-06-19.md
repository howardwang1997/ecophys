# Paper A — the claim (post exp-123) + experiment roadmap (2026-06-19)

## The claim

**Title-level.** *Fat tails in a differentiable agent-based market simulator are a non-equilibrium
**driven transient**, not a stationary property.*

**Primary claim (C-main).** In an MD-style differentiable market simulator, the **steady state is
light-tailed** (Hill α ≈ 5). The heavy, cube-law-and-beyond tail (α → 0.5) is a **non-equilibrium
phenomenon**: it emerges *only* when the system is driven out of its steady state — at initialization
(equilibration) or by an exogenous shock — and **relaxes back on a finite timescale** (~10³ steps).
The impact tail-transfer law **α = ζ/δ** (exact change-of-variables) decomposes the impact map's
contribution and is the bridge from the excess-demand tail to the return tail.

**Evidence in hand (exp 123 Stage-1 + 1.5 + 2a, 2026-06-19, windowed Hill α_ED(t), n=32/arm):**
control steady-state α_ED ≈ **4.7** (light, never dips); a state_kick at t=3000 drives α_ED → **~0.5**
(heavier than the cube law), which **relaxes back to ≈4.7 within ~1k steps**, with the **same depth as
the t=0 equilibration template**. This **rules out** the "fat tail is a t=0 startup artifact" reading —
the heavy tail genuinely **recurs under driving**. Three quantitative results:
- **Generalization — 5/5 assets P** (spx, ndx, gold, btcusdt, eurusd). Universal across equity/gold/crypto/FX.
- **spx full dose-response = a clean sigmoid** (mag 0.05→12): α_ED = 4.24/3.01/1.88/1.45/1.08/0.77/0.58/
  0.51/0.49/0.58 — **light below mag≈0.1, onset 0.1–0.2, graded ramp, saturated floor ~0.5 above mag 3**
  (monotone 9/10; the lone wiggle is floor-noise — H2 graded-dose-response satisfied; verdict prints "P\*"
  only for that).
- **Asset-dependent threshold ∝ intrinsic volatility:** equities/gold/crypto onset ~0.1–0.2; low-vol FX
  (eurusd) needs ~mag 6–12 (A at mag3 → P at mag12: 4.16/2.91/1.68; burn-in template also lighter, 1.04).
  Ties the transient fat tail to the asset's stability — a feature, not a bug.

(`experiments/123_driven_transient/verdict_{spx,ndx,gold,eurusd,btcusdt}.json`.)

**Supporting claim (C-method, the honest correction).** Rollout stylized-fact scoring **without warmup
discard** misreads this transient as a *stationary* fat tail. The project's earlier "Hill ≈ 1.3
overshoot" and the concave-impact "in-band solve" are **burn-in artifacts**: R1 shows the standard Hill
moves UP under warmup discard (baseline 3.87→6.55, concave 5.05→9.26 at n=8000) and the concave cell is
**too-thin in steady state** — the 4000-step "in-band solve" was burn-in inflation. This is a measurement
caveat + correction for the ABM / market-sim literature.

## What the claim does NOT yet support (honest limits → the roadmap)

1. ✅ **RESOLVED (Stage 1.5).** Dose-response mapped — a clean sigmoid (onset ~0.1–0.2, floor ~0.5).
3. ✅ **RESOLVED (Stage 2a).** 5/5 assets, with an asset-dependent threshold.
2. **state_kick perturbs agent latent states** — a skeptic calls it "mechanical, not market physics."
   Need an **exogenous / market-realistic** shock channel. → **Stage 2b (channels)** — OPEN.
4. **Relaxation timescale τ uncharacterized** — is it universal? scale with dose / N / asset? → **Stage 2d**.
5. **No real-data check.** Whether *real* market fat tails are a non-equilibrium transient (vs stationary)
   is the make-or-break for a **market**-physics claim. → **Stage 3 (the decisive one)** — OPEN.

## Venue calibration

- As a **methods + simulator-physics** paper (mechanism + the burn-in measurement caveat + the
  tail-transfer decomposition): **NeurIPS / ICML** is realistic *now*, after Stage 1.5 + Stage 2.
- The **Nature-Physics-flagship** ambition is gated on **Stage 3**: real crash episodes must show the
  same transient α-dip-and-recover. If real fat tails are stationary, the claim retreats to "MD market
  sims produce fat tails only transiently" — still a genuine methods result, lower venue.

## Roadmap (priority order)

| stage | experiment | answers | status |
|---|---|---|---|
| ~~1.5~~ | spx sub-threshold dose sweep mag {0.05,0.1,0.2,0.3,0.5,1,2} (+ 3/6/12) | dose-response + onset | ✅ **DONE** — sigmoid, onset ~0.1–0.2 |
| ~~2a~~ | multi-asset revival gold/eurusd/btc + eurusd mag6/12 | generalization | ✅ **DONE** — 5/5 P, asset-dep threshold |
| **2b** | **2nd shock channel** — exogenous **price-jump** and/or **liquidity (γ-drop)** | rebut "state_kick is mechanical" | **OPEN** — ~15–30 LoC in `_apply_shock` + validate, then ~128 rollouts |
| **2c** | news channel (`_fundamental`, info_asym ON) | a third, information-shock channel | OPEN — retrain 1 seed (~1h) + inference |
| **2d** | **relaxation-timescale τ** = exp-fit of α_ED recovery vs dose / asset | is τ universal? does it scale with the threshold? | OPEN — analysis of 1.5/2a data (no new sim) |
| **3** | **REAL-DATA crash validation** — windowed Hill α on 2010 flash crash / 2020 COVID / Luna / FTX / SVB | do real markets show the transient α-dip-and-recover? **decides market-physics vs sim-only** | **OPEN, decisive** — data + the existing estimator |
| C2 (opt) | entropy production / effective-temperature during the transient | non-equilibrium-thermo tie-in (Paper B bridge) | OPEN |

**Done (2026-06-19 overnight):** Stage 1 + 1.5 + 2a — (P) physics, 5/5 assets, sigmoid dose-response.
**Next deliberate session:** Stage 2b (price-jump/liquidity channel, validate like the state_kick smoke)
→ Stage 2d (τ, free from existing data) → **Stage 3 (real-data — decides the venue).**
