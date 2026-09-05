---
name: Pareto-bounded floors — autocorr_returns + zumbach_asymmetry
description: 089 attribution batch found single mechanisms CAN lift both floors, but every floor-lifter breaks ≥1 other fact ≥20pp; ceiling is Pareto, not architectural
type: project
---

> **Superseded for Zumbach claims on 2026-09-05.** The canonical evaluator and differentiable
> loss compare one past coarse-volatility window with fine volatility at unequal lag distances.
> A reversible process with decaying volatility autocovariance therefore has a strictly negative
> population score. All Zumbach pass rates, "floor lifter" rankings and Zumbach-attributed
> collateral costs below are quarantined until a role-swapped, null-calibrated rescore is separately
> authorized. The autocorrelation result is unaffected. See
> [[project_ecomd_zumbach_orientation_audit_2026-09-05]].

**Updated 2026-05-20**: Reframed from "9/11 architectural ceiling" → "11-fact Pareto frontier".

The 089 attribution batch (16 cells × 50 seeds) found that both putative floors
**can be lifted by single mechanisms**, but each lift comes with a corresponding
collateral break elsewhere:

| floor fact | best lifter | pass% | collateral cost |
|---|---|---:|---|
| `autocorr_returns` | `ar1_s03` | 87% (vs baseline 24%, +62pp) | breaks `acf_squared_returns` −65pp |
| `zumbach_asymmetry` | `ar1_s05` | 43% (vs baseline 6%, +37pp) | breaks `conditional_kurtosis` −47pp |
| `zumbach_asymmetry` | `zumbach_dn_s10` | 29% (+23pp) | **NO breakage ≥−13pp** — safest patch |

`zumbach_dn_s10` is the only cell in 089 with no individual fact-breakage ≥−13pp,
making it the safest single-mechanism patch. It also has the best overall mean (5.12)
and replicates at n=29 (5.31) on SPX and n=26 on Gold (**5.96 — new SOTA single-mech cell**).

**Cross-asset confirmation (2026-05-20 089b/092 5-asset rescore)**:
The Pareto ceiling holds across all 5 assets. No cell at n≥26 reaches mean ≥ 5.5:
- Gold zumdn 5.96 (best), EURUSD zumdn 5.36, SPX zumdn 5.24, BTC b3 5.10, NDX pair 5.18.
- 096 all-pairs (23 pairs × 30 seeds): best `pair_asym_ms` 5.33. Pair compositions do
  not break the ceiling either.

**Why:** The old "architectural floor" framing was too strong — it claimed v3 cannot
produce these facts at all. The 089 evidence is weaker but stronger as a paper claim:
**no single mechanism in our 10-mechanism family simultaneously satisfies all 11
Cont 2001 facts.** Specialist mechanisms exist for every fact (per-fact biggest-mover
table in 089 attribution_matrix), but they trade against each other. This Pareto
structure is the central Paper A §4 finding.

**How to apply:**
- Stop saying "9/11 ceiling" — say "Pareto frontier, max observed mean 5.96/11 (Gold zumdn)".
- The falsification claim in Paper A §4 is: "no Markovian latent-state agent dynamics in
  our 10-mechanism family simultaneously matches all 11 Cont 2001 facts on any of 5 assets,
  even after explicit floor-targeting patches and 23 pair compositions." Stronger than the
  original "two facts impossible" formulation.
- AR(1) drift-clip variant (090b `ar1_s05_clip` mean 5.11 at ~5% rej) fixed the original
  AR(1) instability (70% rej) without changing the Pareto picture.
- Memory kernel (memk) mechanism remains ambiguous — 099 at n=5 had 4 cells tied at 5.80,
  noisy. 099b at n=30 (overnight 2026-05-20) settles whether memk has a hidden operating
  point or is correctly disqualified.

**Related**: [[project_pareto_ceiling]] (this is the central paper claim),
[[feedback_seed_count_lottery]] (098/099 n=5 numbers are not citable),
[[project_ar1_drift_artifact]] (AR(1) integrator diagnosis).
