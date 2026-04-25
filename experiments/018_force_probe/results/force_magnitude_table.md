# Force-magnitude probe — EcoMD architecture comparison

N=200 agents, d=32 state dim, n_repeats=5 (random init seeds).
Untrained: pure init-time forces. Langevin noise per step σ ≈ 0.032.

Forces below noise σ → simulator dynamics dominated by Langevin noise,
training has no signal to learn meaningful dynamics.

| architecture | V_init | |F|_init mean ± std | ratio vs v0.x | vs noise (σ=0.032) |
|---|---|---|---|---|
| v0.x PairwisePotential (baseline) | -46.1±268.3 | 0.8247±0.1373 | 1.000× | 25.8× |
| v0.9 StochasticPairwise (k=50) | -45.3±268.4 | 0.8271±0.1382 | 1.003× | 25.8× |
| v1 MACE-lite (k=32, body=4, default) | +2.5±7.0 | 0.0374±0.0057 | 0.045× | 1.2× |
| v1 MACE H hybrid (k=N-1, mult=10) | -1276.9±7023.3 | 1.1488±0.0917 | 1.393× | 35.9× |
| v2.0 default (gauge on, T=eye) | -1.3±11.0 | 0.0490±0.0044 | 0.059× | 1.5× |
| v2.0 phi=3.0 (gauge on, T=eye) | +15957.4±24060.4 | 44.7568±5.2104 | 54.272× | 1398.6× |
| v2.1 (gauge off, T=ones, phi=1.0) | -726.0±494.2 | 5.8553±0.9979 | 7.100× | 183.0× |

## Interpretation

- **|F| / σ < 1**: Langevin noise dominates → no learnable structure → 4/11 stylized facts (white noise floor).
- **|F| / σ ≈ 30-50**: signal sufficient for clustering dynamics → 6-7/11 achievable.
- **|F| / σ ≫ 100**: gradient explosion regime; clip=1.0 caps effective lr → again poor training.