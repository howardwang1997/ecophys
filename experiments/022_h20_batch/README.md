# 022 — H20 batch (multi-asset × architecture sweep)

Six configs that systematically test the v3 features. Each is a
self-contained training run; H20 user runs them sequentially via
`scripts/h20_batch_v3.sh`.

## Matrix

| ID | Config | Multi-asset | Multi-scale Hawkes | Regime GRU | Two-pop γ/T | Notes |
|---|---|---|---|---|---|---|
| A0 | `config_a0_baseline.yaml`           | SPX only | ✗ | ✗ | ✗ | v1.0 Hawkes recipe — H20 7/10 baseline |
| A1 | `config_a1_multi_asset.yaml`        | ✓ SPX+BTC+ETH | ✗ | ✗ | ✗ | universality datum |
| A2 | `config_a2_multi_asset_mshawkes.yaml`| ✓ | ✓ | ✗ | ✗ | + zumbach / acf-shape fix |
| A3 | `config_a3_multi_asset_regime.yaml` | ✓ | ✗ | ✓ | ✗ | + non-stationary regime |
| A4 | `config_a4_multi_asset_twopop.yaml` | ✓ | ✗ | ✗ | ✓ | + heterogeneous Langevin |
| A5 | `config_a5_all_features.yaml`       | ✓ | ✓ | ✓ | ✓ | the kitchen sink |

Each ablation isolates one feature against A1 (multi-asset baseline) so
we can attribute n/10 deltas to specific architectural choices.

## Run order on H20

```bash
git pull
bash scripts/h20_batch_v3.sh           # all 6 sequentially
# or single:
bash scripts/h20_batch_v3.sh A5
```

Each config: N=10K, 200 iter, chunk=24, 4-card DDP gloo. Wall ~120s
training × 6 + 2 min eval × 6 ≈ ~15 minutes total.

After all done, eval:
```bash
bash scripts/h20_batch_v3_eval.sh
```

## Output layout

```
experiments/022_h20_batch/
├── config_a0_baseline.yaml … config_a5_all_features.yaml
├── results_a0/
│   ├── training_log.json
│   ├── checkpoint.pt
│   ├── inference_merged.json   ← from eval
│   └── inference_rank_0.json
├── results_a1/, results_a2/, … results_a5/
└── scoreboard.md               ← Mac post-run summary table
```
