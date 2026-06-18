# Paper A — Finding: the ζ_ED≈1.5 "verification" is a burn-in transient artifact (steady-state refutation)

**Status:** critical, **threatens the empirical support for `theory_tail_transfer.md`** (the
δ*=ζ_ED/3 derivation). Companion to that doc; updates its §"in-silico validation" and closes its
§"What remains to make the derivation end-to-end" (the owed direct-ζ_ED experiment) — but the
result is the **opposite** of the predicted ζ_ED≈1.50.

**TL;DR.** The owed experiment (directly measure ζ_ED from a logged ED series, predicted ≈1.50)
was run on the H20 box on 2026-06-18. It does **not** confirm ζ_ED≈1.5 in steady state. The 1.5
that appears in measurements is a **~20-step burn-in (equilibration) transient** that is present
in every rollout; `run_large.py` does not discard warmup, so the transient contaminates every
Hill estimate. Once the burn-in is dropped, the model's stationary excess-demand **and** return
tails are **light** (Hill α ≈ 4–12) at every δ. The δ-grid "Hill·δ≈1.5, CV 1–9%" table in
`theory_tail_transfer.md` is therefore very likely an artifact of this transient (same
`run_large`, no warmup). Separately, the heavy-tail *source* mechanism (`het_mass`, the
Gabaix–GGPS Zipf trader sizes) was **deliberately dropped** on 2026-06-01, so the model currently
has no stationary mechanism that can produce ζ_ED≈1.5 — the cube law is not in the configured
model's steady-state reachable set.

---

## The owed experiment, run — and its result

`theory_tail_transfer.md` §"What remains" predicted: directly-measured ζ_ED≈1.50 (ndx≈1.60).
Procedure: `run_large.py --save-trajectory` on the 113 concave_d050 seed0 checkpoint (2×H20,
n_steps=8000, 4 rollouts), then Hill on the logged `excess_demand`. Measured ζ_ED = **5.23**
(k_frac=0.05) — the headline mismatch that triggered this investigation.

Diagnosis found **three** root causes; none is the transfer law itself being wrong.

### Cause 1 — the logged `excess_demand` is post-concave-impact (wrong quantity)

`ecomd/models/price_formation.py:340-357`:
```
excess_demand = kappa * dpos.sum()                       # 340: raw aggregate ED
excess_demand = excess_demand + heavy_flow (if het_mass) # 354: Gabaix heavy-tail source
excess_demand = self._concave_impact(excess_demand)      # 357: OVERWRITES — post-impact
...
"excess_demand": excess_demand.detach()                  # 454: saves POST-impact value
```
The trajectory field is the **post-impact** quantity, whose tail equals the return tail *by
construction* (`Δp = β·sign(ED)·|ED|^δ`). The theory's ζ_ED is the **pre-impact (raw)** tail.
`impact_scale=0.5`, `impact_delta_init=0.5`, `impact_delta_learnable=False` (config) → δ=0.5
fixed and invertible: `|raw_ED| = s·(|post|/s)^(1/δ)` with s=δ=0.5. **The transfer identity
`α_post = α_raw/δ` holds exactly at every burn-in level** (e.g. drop=0: α_raw=1.61, α_post=3.22
= 1.61/0.5). The math in `theory_tail_transfer.md` is correct; the measurement was of the wrong
quantity.

### Cause 2 — the heavy tail is a burn-in transient (the serious finding)

Full δ-grid re-run, spx seed0, baseline + concave_d{040,050,060,070}, with `--save-trajectory`
(`experiments/122_zeta_ed_d1/`, 5 cells × 4 rollouts). Hill α at k_frac=0.02 vs burn-in dropped:

| cell | δ | drop=0 \|rawED\|α | drop=0 \|ret\|α | **drop=50 \|rawED\|α** | **drop=50 \|ret\|α** |
|---|---|---|---|---|---|
| baseline | 1.0 | 2.77 | 2.77 | **8.4** | **8.4** |
| concave_d040 | 0.4 | 2.17 | 5.42 | **9.4** | **11.7** |
| concave_d050 | 0.5 | **1.61** | 3.42 | **7.3** | **11.5** |
| concave_d060 | 0.6 | 0.65 | 1.31 | **3.9** | **6.8** |
| concave_d070 | 0.7 | 1.41 | 2.71 | **5.4** | **10.5** |

- The "ζ_ED≈1.5" appears **only at drop=0** (burn-in-inclusive), and even there only incidentally
  (d050: 1.61, d070: 1.41) — across δ the drop=0 raw-ED Hill is 2.77/2.17/1.61/0.65/1.41, **not
  constant**. The cube-law-3 return Hill is likewise burn-in-only.
- The first ~20 steps are a deterministic equilibration transient (post-impact \|ED\| decays
  26.6→9.4→…→2.5); only 36/32000 = 0.11% of steps exceed \|ED\|>3, almost all in those steps.
- **Stationary (drop≥50) tails are light everywhere**: \|rawED\|α ≈ 3.9–9.4, \|ret\|α ≈ 6.8–11.7.
  The model does not reproduce the cube law at any δ in steady state.
- `run_large.py` does **not** discard warmup (line 104's "drop" is an OOM tensor drop, not burn-in).
- The transfer identity itself breaks down stationary (drop=50 ratios raw/ret = 0.52–0.81 vs δ
  0.4–0.7): when ED is light-tailed the additive Gaussian return-noise (`price_formation.py:381`
  `ση`) is no longer negligible, so α_ret ≉ α_raw/δ except in the burn-in-dominated regime.

### Cause 3 — the heavy-tail source mechanism is OFF by design (D2)

`het_mass_enabled` (the GGPS Zipf trader-size heavy-tail injection, `price_formation.py:347-354`,
the code comment calls it *"the real Gabaix tail"*) is **set in zero configs repo-wide**
(`grep experiments/**/*.yaml`: 0 hits). git: introduced in `566780fac` "exp 113: Gabaix
mechanism-level solve", then **deliberately dropped**. `.claude/memory/project_neural_sde_tournament.md:148-154`:
heterogeneous masses **misfired twice** (v1 weighted-Gaussian thinning; v2 fixed-Pareto-weights →
one whale per step → tail tracks the t-innovation, not the size distribution). Decision
(user, 2026-06-01, option A): *"baseline already over-produces tail (hill 1.4), so adding
size-heaviness is the wrong direction — DROP masses, refocus exp 113 on a clean concave-impact
solve."* The exp-113 design memo itself predicts *"concave alone → hill↑"* — i.e. a lighter tail,
exactly what is measured here stationary. With het_mass off, raw ED = κ·ΣΔpos ≈ Gaussian by CLT;
**there is no stationary mechanism that can yield ζ_ED≈1.5 in the current configuration.**

---

## What this means for `theory_tail_transfer.md`

- **The lemma is unchanged** (α_Y = ζ/δ is a correct change-of-variables identity).
- **The §"in-silico validation" table is contaminated.** Its Hill·δ≈1.48–1.60 (CV 1–9%) was
  computed by `score_transfer_law.py` fit mode over `inference_merged.json` files produced by the
  same warmup-less `run_large`. The same burn-in transient that inflates the direct ζ_ED will
  inflate the per-cell Hill·δ, and because the transient is structural (every rollout) it will do
  so with low cross-seed variance — producing a *consistent, low-CV* "1.5" that looks like a
  universal law but is an equilibration artifact.
- **The "dynamics generate ζ_ED≈3/2" unification (§ with exp 109) is unsupported in steady state.**
  The baseline "over-produced tail (hill 1.4)" cited there is itself burn-in-inclusive (this doc,
  baseline drop=0: 2.77; drop≥50: 8.4).
- **The headline claim "δ≈0.5 is derived, not fitted" currently rests on a transient**, not on a
  stationary stylized fact.

## Honest limits

- **seed0 only** (δ-grid used n=30). Quantitative means may differ; the structural burn-in
  artifact is seed-robust (deterministic equilibration). A full n=30 re-run with warmup discard
  settles it definitively (option R1).
- **spx only** of the 5 assets; mechanism is shared, so the other 4 are very likely the same.
- **n_steps=8000.** drop=50/200/1000 all agree the tail is light, so 8000 is enough to refute
  "stationary ≈ 1.5"; a 50000-step run is cheap insurance against a slowly-developing heavy tail.

## Options (decision pending)

| | action | cost | resolves |
|---|---|---|---|
| **R1** | re-run full δ-grid n=30 (≥1 asset) with `--save-trajectory` + warmup discard | few-h GPU | whether the 30-seed "1.5" survives burn-in (expect: no) |
| **R2** | revive a **working** stationary heavy-tail source — `het_mass` v3 (per-step heavy flow with learnable tail index, per the memory's own prescription) or another mechanism — so the model actually produces the cube law in steady state, then re-validate | code + train | the constructive path to restoring the claim |
| **R3** | reframe Paper A off stationary stylized facts onto **crash / transient dynamics** (where the heavy tail genuinely lives) | writing | if the heavy tail is legitimately transient-only |
| **R4** | one n_steps=50000 spx d050 rollout, warmup-free, to rule out a slow-developing heavy tail | ~1 h | cheap insurance before R1/R2 |

**Reviewer-2 recommendation:** R4 (1 h insurance) → R2 (the only path that keeps the
tail-transfer headline). R1 only makes the refutation bullet-proof at n=30; it does not change
the direction. R3 is the fallback if a working heavy-tail mechanism proves out of reach.

## Reproducibility

- Code: `scripts/score_transfer_law.py` `measure_zeta_mode` upgraded (Hill α-vs-k curve +
  200-bootstrap CI + \|ret\| sanity + transfer ratio); `ecomd/models/price_formation.py`
  `_concave_impact` (inverse used here).
- Data: `experiments/122_zeta_ed/` (probe, spx d050) and `experiments/122_zeta_ed_d1/`
  (δ-grid seed0 re-run, 5 cells); trajectory npz are gitignored, regenerated by
  `scripts/gpu_zeta_ed_2card.sh` + the D1 driver in `logs/2026-06-18.md`.
- Session record: `logs/2026-06-18.md` (full chronological detail, both sessions).
