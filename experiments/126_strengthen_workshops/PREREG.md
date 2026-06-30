# exp 126 — PRE-REGISTRATION (BINDING)

**Status:** BINDING. Frozen **before the H20 runs**. Per the project pre-registration clause
(`feedback_preregistration.md`) + no-downgrade rule (`feedback_no_downgrade.md`): **all arms reported
regardless of outcome; no arm/observable/threshold may change after the runs**; deviations go in a
Deviations section and are reported both ways. **Date frozen:** 2026-06-30. **Design:** `DESIGN.md`.

G-D1b and G-E are **carried over verbatim** from the exp 125 PREREG (H-D1, H-E) — they were designed and
frozen there but not run. H-D2′ is a **new** pre-registration (the elevation of a secondary exp-125
observable to a tested claim, with an artifact control), required because α_ret(N) was NOT the
pre-registered primary in exp 125 (which was α_ED, and which stays the primary record for "ED tail").

---

## H-D1b (trained heavy noise — the Route-A Pareto point).
*Prediction:* a **trained** Lévy model (α=1.7, and heavier α=1.5) reaches a heavier *stationary* return
tail than the t(df5) baseline (hill_tail_index DECREASES toward ~3), **at a measurable cost** —
ACF²(r²) and/or leverage degrade as the tail fattens.
- **Decision / pre-committed framing (positive either way):**
  - If trained Lévy installs a heavier stationary tail with a clustering/leverage cost → **"we identify
    the exact missing ingredient (a stationary heavy source) and quantify the tails-XOR-dynamics Pareto
    cost inside one architecture"** (the central Route-A positive result; ML4PS headline-grade).
  - If trained Lévy does NOT heavy the stationary tail (self-averages like G-D1a) → **"even an
    end-to-end-trained infinite-variance bath self-averages away; the light tail is a structural
    property of the learned dissipative dynamics, not the noise source"** (still positive; the strongest
    form of the fundamental claim). Report the (hill, ACF², leverage) triple for every trained model.
  - **Stability note (not an outcome gate):** if Lévy α=1.5 training diverges (NaN/grad blowup), that is
    reported as a finding ("heavy-tailed BPTT is unstable at α≤1.5"), and α=1.7 carries the claim.

## H-B′ (atlas completion). *Prediction (carried from exp 125 H-B, now on 5 assets × dur∈{1,20}):*
`liquidity_drop` revives the heavy-tail-and-relax transient (post-shock α_ED dip ≥2 below control) on
≥3/5 assets at DUR=20; `temperature_spike` does not (dip < 2). DUR=1 is weaker than DUR=20 for both.
*Framing:* either way report the full 5-asset × 3-driver × 2-dur control surface; the coherent (kick) vs
incoherent (temperature) vs liquidity contrast is the GenAI mechanism statement, not a pass/fail gate.

## H-C′ (dose law completion). *Prediction:* dip(dose) on gold + eurusd is monotone increasing and
well-fit (R² ≥ 0.9) by ≥1 pre-specified form (saturating / power-law / logarithmic), with onset
0.1–0.3σ (eurusd onset may be higher per its known vol-threshold, `project_eurusd_weak_ofi`).
*Framing:* report best-fit form + params + R² per asset; the law (and any per-asset onset shift) is the
result.

## H-D2′ (return-tail self-averaging — re-pre-registered, WITH artifact control). The **primary
observable is the EWMA-vol-standardized return-tail index α_ret_std(N)**; α_ret(N) and α_ED(N) are
reported alongside. *Prediction:* α_ret(N) rises (lighter) with N (confirming exp 125); the **decisive**
test is α_ret_std(N).
- **Decision / pre-committed framing (positive either way):**
  - If α_ret_std(N) ALSO rises monotonically (positive log-N slope, R² ≥ 0.8) → **genuine CLT
    Gaussianization of returns**: the return fat-tail is (partly) an aggregation effect, localized to the
    price-formation stage — the re-pre-registered headline mechanism (two-stage: ED tail dynamics-set,
    return tail self-averages).
  - If α_ret_std(N) is flat while raw α_ret(N) rises → the raw rise was a **return-scaling artifact**;
    the pre-registered exp-125 primary (**α_ED flat ⇒ ED tail is dynamics-set, not aggregation**) stands
    unchallenged as the mechanism. (Either outcome is reported as the result; no headline-swap without
    the standardized control passing.)

## H-E (transferable pitfall — carried from exp 125 H-E). *Prediction:* the neural-SDE baseline shows the
same warm-up Hill inflation (no-discard heavier than discard-50). *Framing:* positive → "the warm-up
audit is a transferable protocol, validated on 2 generator families"; if not → "the pitfall is specific
to off-equilibrium-initialized rollouts" (a precise scope). Optional; reported only if run.

---

## Estimators (frozen, = exp 125)
- Steady-state α_ED: windowed Hill (k_frac=0.1) on excess demand, warm-up [0,500) discarded, averaged
  over the steady window (pre-shock for shocked arms). Post-shock min α_ED / τ as exp 123/124.
- 11 facts: `compute_all` (warm-up-discarded returns). hill_tail_index is the full-rollout fact (lower
  = heavier), reported as-is for the Pareto comparison.
- α_ret_std: EWMA(λ=0.05)-vol-standardized log-returns, warm-up [0,500) dropped, Hill k_frac=0.1 on |·|.
- CIs: normal-approx 95% from windowed mean/std (≥20 rollouts/arm); bootstrap where per-seed available.

## Multiple comparisons / no gate-shopping
**G-D1b is the single primary Route-A test; H-D2′'s primary observable is α_ret_std (pre-committed).**
All atlas/dose/noise cells are characterization, tabulated in full regardless of significance. No
observable is promoted post-hoc; the α_ret headline is licensed ONLY by the standardized control passing.
