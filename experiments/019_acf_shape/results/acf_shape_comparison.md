# ACF(r²) decay shape — architecture comparison

Real SPX daily ACF(r²) shows peak-decay: ~0.45 at lag 1, decays to ~0.11 at lag 16.
Architectures that produce vol clustering correctly should show similar peak-decay.
Flat curves indicate 'constant variance regime' — Goodhart-failure mode (single
summary number passes but actual physics is wrong).

| architecture | lag 1 | lag 5 | lag 10 | lag 16 | shape |
|---|---|---|---|---|---|
| Real SPX daily | +0.451 | +0.290 | +0.217 | +0.111 | **peak-decay** |
| v0.6 trained (Mac) | +0.383 | +0.345 | +0.308 | +0.234 | flat |
| v0.8 trained (Mac) | +0.083 | +0.077 | +0.068 | +0.060 | flat |
| v0.7 trained (Mac, σ↓) | +0.481 | +0.402 | +0.334 | +0.244 | flat |
| v1 MACE H hybrid | +0.182 | +0.201 | +0.187 | +0.187 | flat |
| v1 MACE A_matched | -0.010 | +0.006 | -0.007 | -0.014 | flat |

## Interpretation

- **peak-decay** (lag1/lag10 > 1.5): real vol clustering — variance shocks decay over time.
- **flat** (curve ~ constant): constant-variance regime, NOT vol clustering.
- v1 MACE H hybrid is the canonical Goodhart case: passes #6 mean test but flat shape.