# Family B results: attribution audit on 1D U-Net PDE surrogates (PDEBench-style OOD)

Date: 2026-08-28

Status: **confirmatory outcome under the D0 freeze; 6 jobs (advection/diffusion/Burgers ×
σ_f ∈ {1.0, 0.1}), channels {16,32} × epochs {400,800}, 5 seeds, 8 variants, two-level 1D
U-Nets at train resolution 128; three frozen OOD probe classes (flat-mode, amplitude, 2×
band-limited resolution shift); records in this directory; executed on the authorized V100s.**

## Frozen-rule outcomes (best free_res cell per system@σ, matched-pair comparisons)

### Rule 1 — attribution: **PASS 18/18** (ratio 12.7–6710×; rule: ≥2)

Conserving-channel error, ood_flat probe (representative):

| System@σ_f | free | free_res | hard | ratio |
|---|---:|---:|---:|---:|
| advection@1.0 | 1.403±0.139 | 0.359±0.035 | 0.371±0.018 | 84× |
| diffusion@1.0 | 1.374±0.118 | 0.075±0.040 | 0.067±0.015 | 156× |
| burgers@1.0 | 1.462±0.117 | 0.425±0.029 | 0.412±0.006 | 79× |
| (all six settings) | — | — | — | 73–159× |

The pattern holds identically on the amplitude probe (12.7–146×) and the **resolution-shift**
probe (evaluate at 256 after training at 128; 38–6710×): even under architecture stress the
output parameterization, not the constraint, carries the OOD behavior. `hard` and `free_res`
are statistically indistinguishable (hard marginally better in 4/6 settings).

### Rule 2 — laundering conjunction: **fails as in family A**

`soft@30` inflates conserving error over `free` (+22–30%, e.g. 1.800±0.037 vs 1.403±0.139) but
brings **no drift reduction** (0.0146 vs 0.0144) — strong soft penalties are again dominated.
`soft_res` ≈ `free_res` (mild λ30 degradation ≤16%).

### Rule 3 — decoupling control: **PASS exactly 18/18** (0.00% deviation, drift 0.0000)

### ID-cost finding

Same non-overlap branch as families A/M: absolute-output U-Nets pay more in-distribution error
than residual U-Nets at every capacity cell; cross-parameterization claims remain matched-pair
only.

## Cross-family state after B

| Family | Attribution | Laundering | Decoupling |
|---|---|---|---|
| A (MLP, 3 PDE systems) | PASS 6/6 | 2/6 (dominated) | exact |
| B (1D U-Net, PDEBench-style OOD) | **PASS 18/18** | fail conjunction (dominated) | exact 18/18 |
| M (CDA market) | PASS (140×) | **PASS (4.7×)** | exact |
| C (2D U-Net) | running | — | — |
