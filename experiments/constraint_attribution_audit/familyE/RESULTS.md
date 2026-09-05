# Family E results: contraction dose-response (mechanism test, exploratory review branch)

Date: 2026-08-29

Status: **exploratory branch authorized by the D0 freeze-and-review clause after family C's
inversion; full frozen grid (hidden {64,128} × epochs {400,800}, 5 seeds); diffusion family
with single-factor ν manipulation; baseline ν=0.02 is family A's confirmatory cell.**

## Dose-response on ood_flat (best free_res cell; mean ± sd over 5 seeds)

| ν | rich-band one-step decay | free | free_res | hard | winner |
|---:|---:|---:|---:|---:|---|
| 0.02 | ~1.00 (near-identity) | 0.443 | **0.004** | 0.004 | free_res (100×) |
| 2.0 | e^{−0.5} | 0.222±0.016 | **0.153±0.011** | 0.152±0.010 | free_res (1.5×) |
| 10.0 | e^{−4.9} | **0.140±0.010** | 0.262±0.014 | 0.259±0.012 | **free (1.9×, inverted)** |

Seed bands are non-overlapping at each ν. The parameterization winner flips monotonically in
the map's contraction strength, exactly as the mechanism (residual heads must learn large
cancelling updates whose off-support extrapolation is fragile under contraction) predicts.
The constraint verdict is unaffected: `hard` ≡ `free_res` at every dose.

## Standing

Exploratory (review branch), supportive of the confirmatory four-family conclusion; entering
the paper as the mechanism section, not the confirmatory tables.
