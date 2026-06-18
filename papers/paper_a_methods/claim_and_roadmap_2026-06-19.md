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

**Evidence in hand (exp 123, 2026-06-19, spx n=32 + ndx n=30, windowed Hill α_ED(t)):**
control steady-state α_ED = **4.75** (light, never dips); a state_kick at t=3000 drives α_ED → **0.5**
(heavier than the cube law), which **relaxes back to ≈4.7 within ~1k steps**, with the **same depth as
the t=0 equilibration template** (0.66). ndx replicates. This **rules out** the "fat tail is a t=0
startup artifact" reading — the heavy tail genuinely **recurs under driving**. (verdict: spx = P\*,
ndx = P; `experiments/123_driven_transient/verdict_*.json`.)

**Supporting claim (C-method, the honest correction).** Rollout stylized-fact scoring **without warmup
discard** misreads this transient as a *stationary* fat tail. The project's earlier "Hill ≈ 1.3
overshoot" and the concave-impact "in-band solve" are **burn-in artifacts**: R1 shows the standard Hill
moves UP under warmup discard (baseline 3.87→6.55, concave 5.05→9.26 at n=8000) and the concave cell is
**too-thin in steady state** — the 4000-step "in-band solve" was burn-in inflation. This is a measurement
caveat + correction for the ABM / market-sim literature.

## What the claim does NOT yet support (honest limits → the roadmap)

1. **Dose-response is saturated** above mag=3 (the dip floors at ~0.5 for mag 3/6/12). → **Stage 1.5**.
2. **state_kick perturbs agent latent states** — a skeptic calls it "mechanical, not market physics."
   Need an **exogenous / market-realistic** shock channel. → **Stage 2 (channels)**.
3. **Two assets only** (spx, ndx). → **Stage 2 (multi-asset)**.
4. **Relaxation timescale τ uncharacterized** — is it universal? scale with dose / N / asset? → **Stage 2**.
5. **No real-data check.** Whether *real* market fat tails are a non-equilibrium transient (vs stationary)
   is the make-or-break for a **market**-physics claim. → **Stage 3 (the decisive one)**.

## Venue calibration

- As a **methods + simulator-physics** paper (mechanism + the burn-in measurement caveat + the
  tail-transfer decomposition): **NeurIPS / ICML** is realistic *now*, after Stage 1.5 + Stage 2.
- The **Nature-Physics-flagship** ambition is gated on **Stage 3**: real crash episodes must show the
  same transient α-dip-and-recover. If real fat tails are stationary, the claim retreats to "MD market
  sims produce fat tails only transiently" — still a genuine methods result, lower venue.

## Roadmap (priority order)

| stage | experiment | answers | cost (inference, reuse ckpt) | code? |
|---|---|---|---|---|
| **1.5** | spx **sub-threshold dose sweep** state_kick mag {0.3,0.5,1,2} (+ existing 3/6/12, control) | the dose-response below saturation; find threshold mag* | ~128 rollouts | none (run_large --shock-mag) |
| **2a** | **multi-asset** revival: gold/eurusd/btc × {control, kick3} | generalization | ~180 rollouts | none |
| **2b** | **2nd shock channel** — exogenous **price-jump** and/or **liquidity (γ-drop)** | rebut "state_kick is mechanical" | ~128 rollouts | ~15–30 LoC in `_apply_shock` (+ validate) |
| **2c** | **news channel** (`_fundamental`, info_asym ON) | a third, information-shock channel | retrain 1 seed (~1h) + inference | config + retrain |
| **2d** | **relaxation-timescale τ** = exp-fit of α_ED recovery vs dose / N / asset | is τ universal? | analysis of 1.5/2a data | none |
| **3** | **REAL-DATA crash validation** — windowed Hill α on 2010 flash crash / 2020 COVID / Luna / FTX / SVB return series | do real markets show the transient α-dip-and-recover? **decides market-physics vs sim-only** | data + analysis (no sim) | estimator already exists |
| C2 (opt) | entropy production / effective-temperature during the transient | non-equilibrium-thermo tie-in (Paper B bridge) | analysis | some |

**Immediate (overnight, no new code):** Stage 1.5 + Stage 2a (`scripts/gpu_exp123_overnight.sh`).
**Next deliberate session:** Stage 2b (price-jump/liquidity channel, validated like the state_kick smoke),
then Stage 3 (real-data) — Stage 3 is the one that decides the venue.
