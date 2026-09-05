# Family M results: accounting-conservation attribution in a learned CDA simulator

Date: 2026-08-28

Status: **confirmatory outcome under the Family-M child freeze
`ecomd_constraint_attribution_family_m_freeze_2026-08-28.md`; full frozen grid
(hidden {64,128} × epochs {400,800}, 5 seeds, 8 variants) on howard-pc; generated data only;
records in this directory.**

## Frozen-rule outcomes (primary OOD = high-imbalance regime)

### Rule 1 — attribution: **PASS** (ratio 140× at matched cell; rule: ≥2)

| Cell | free | free_res | hard | ratio |
|---|---:|---:|---:|---:|
| 64×400 | 1.703±0.044 | 0.662±0.008 | 0.670±0.011 | 140× |
| 128×800 | 2.604±0.062 | 1.114±0.073 | 1.206±0.117 | 16× |

`hard` and `free_res` seed bands overlap at the matched cell: **the exact accounting constraint
contributes nothing to conserving-channel OOD error; its entire effect is the exact zeroing of
Σ-violations (drift 0.0000 vs 0.0033).** Same verdict as family A — now in a stochastic
financial system.

### Rule 2 — laundering conjunction: **PASS (the only family so far)**

`soft@30`: conserving error **8.00±0.13 vs free 1.70±0.04 (4.7× inflation)** with drift
reduced (0.024 vs 0.067) — the frozen conjunction (inflation ∧ drift reduction) holds at every
cell; `soft@3` already inflates 2×. Even `soft_res@30` mildly inflates (0.85 vs 0.66). The
stochastic next-state targets of the market engine amplify soft-penalty damage far beyond the
deterministic PDE families (A: +18–33%; M: +100–370%). **Domain-dependence finding: penalty
methods degrade worst exactly where targets are irreducibly stochastic.**

### Rule 3 — decoupling control: **PASS exactly** (0.00% deviation, drift 0.0000 everywhere)

### ID-cost finding (non-overlap branch)

Absolute-output ID RMSE 0.17–0.26 vs residual 0.11–0.16 (1.5×), and the absolute arm *degrades*
with capacity (1.70 → 2.60) — absolute next-state prediction overfits stochastic targets.

## Secondary observations (recorded, not frozen claims)

- The residual family's best cell is the *smallest* (64×400): the market transition is noisy;
  capacity does not help.
- `soft_res` drift is noisier across cells than `free_res` — the penalty perturbs optimization
  even in residual form.

## Cross-family state after M

| Family | Attribution | Laundering | Decoupling |
|---|---|---|---|
| A (MLP, 3 PDE systems) | PASS 6/6 (260–5225×) | 2/6 | exact |
| M (CDA, market) | PASS (140×) | **PASS (4.7×)** | exact |
| B (1D U-Net) | running | — | — |
| C (2D U-Net) | running | — | — |
