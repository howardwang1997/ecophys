# C4 precision floor: outcome-blind session-count calculation for the two-arm priority contrast

Date: 2026-08-27 (Session 19)

Precondition C4 of the frozen treatment selection
(`ecomd_truth_asset_treatment_selection_audit_2026-08-26.md`). Paper-only; uses published
laboratory session variability for **noise calibration only, never effect directions**, per the
capability-build plan. No outcome of any planned session was accessed (none exist).

## 1. Frozen method

Primary contrast: session-level difference in time-weighted minimum spread (in minimum price
increments, "ticks") between the FIFO arm and the randomized-priority arm; secondary contrast:
mean touch depth (orders). Assignment unit = session = one independent market (the frozen
asset plan uses one market per session, unlike Aldrich–López Vargas's two six-trader markets
per session).

Two-sided two-sample t-test at α = 0.05, power 0.8. Sessions per arm:

```
n = 2 · (z_{0.975} + z_{0.8})² · σ² / MDE² = 15.70 · (σ / MDE)²
```

where σ is the between-session SD of the session-level statistic and MDE the minimal
detectable effect. For the invariance null (H0), the equivalence test (TOST) at the same band
Δ and α = 0.05 requires approximately the same n as the difference test at MDE = Δ, so one
table serves both readings. Within-session averaging over the frozen 8 trading periods reduces
σ if period-level noise dominates; per the plan's conservatism the calculation ignores this
reduction (persistent group effects plausibly dominate; Aldrich–López Vargas cluster all
inference at the group level).

## 2. Noise anchors (verbatim-cited, published sources only)

From [Aldrich & López Vargas, Experimental Economics 23(2):322–352 (2019)](https://doi.org/10.1007/s10683-019-09605-2),
design and text-quoted statistics:

- Design: between-subjects; 6 sessions per institution; each session = 12 traders in two
  independent 6-trader markets; 8 periods × 4 min; partner matching; units ECU with 2 ECU = $1
  and minimum increment 0.1 ECU; equilibrium spreads s* = 0.324/0.566/0.475 ECU (C1/C2/C3).
- "the standard deviation of minimum spread is nonzero but very low under FBA, and between
  three and five times greater under CDA" (time-series SD, 1-s sampling).
- Observed CDA price-difference volatility is "between five and 7.5 times" its theoretical
  counterpart; theoretical Std(P_t − P_{t−1}) ∈ [0.241, 0.276] ECU ⇒ observed CDA ≈
  1.2–2.1 ECU per 3-s change at the widest anchor.
- Institutional contrasts (FBA − CDA minimum-spread coefficients): −0.123, −0.502, −0.560 ECU.

Anchors imply: session-mean spread dispersion plausibly lies in 0.1–0.5 ECU (1–5 ticks);
time-series volatility is 1.2–2.1 ECU but is an upper bound (within-market, 1–3 s scale).
The exact Table 2 dispersion cells are image-only in the accessible renderings; retrieving
them (published PDF or replication package) is a recorded re-adjudication condition that may
lower σ.

## 3. Sensitivity table (sessions per arm)

| σ (ticks) | MDE 1 tick | MDE 2 ticks | MDE 3 ticks |
|---|---|---|---|
| 1 | 16 | 4 | 2 |
| 2 | 63 | **16** | 7 |
| 3 | 141 | 35 | 16 |
| 5 | 393 | 98 | 44 |

## 4. Frozen defaults and verdict

- **σ default: 2 ticks** (conservative midpoint of the anchor range 1–5).
- **MDE: 2 ticks** for the primary spread contrast (the anchor institutional contrasts,
  0.12–0.56 ECU = 1.2–5.6 ticks, show that a 2-tick MDE is of the order laboratory
  institution changes produce; a within-grammar tie-allocation change is plausibly smaller —
  this is honestly acknowledged, and the depth contrast carries the Lemma-2 directional
  prediction as secondary).
- **Requirement: 16 sessions per arm = 32 sessions at the discovery site**, with the
  confirmation site independently powered at the same count (the frozen two-site replication
  contract). At 8–12 paid participants per session this is 256–384 participant-sessions per
  site — inside the range of published multi-session laboratory market studies but at the
  expensive end.
- **Verdict: conditionally passed.** The calculation method, anchors, σ default and MDE are
  frozen; the gate closes terminally only when the user freezes the cost ceiling (stop
  condition 3 of the capability-build plan). If the ceiling accommodates ≥ 32 sessions per
  site, C4 passes; if only fewer sessions are affordable, the design must either raise MDE to
  3 ticks (16 sessions per arm at σ = 3) or stop.

## 5. Recorded conditions

1. Retrieving the published Table 2 dispersion cells or a replication package may revise σ
   downward (reducing n); the frozen default stays until then.
2. If a pilot-free variance floor from the confirmation site differs from the frozen σ by more
   than a factor of 1.5 in either direction, the session count is recomputed once, before any
   outcome is inspected, under the same formula.
3. No multiplicity adjustment is applied to this floor calculation; the frozen analysis plan
   (one primary contrast, prespecified secondaries with disclosed exploratory status) controls
   multiplicity at the analysis stage.

No topic status, card, or execution authorization is created. A-1 (ethics, outreach,
recruitment) and A0 (sessions, outcomes) remain unauthorized; C3 (explicit user authorization
for A-2 platform qualification) is the remaining gate before any implementation work.
