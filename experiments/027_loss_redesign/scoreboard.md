# Loss Redesign Ablation — Scoreboard

## Phase 1 — Single-axis sweeps (45 runs)

### Axis bal — balance_mode

| variant | n_seeds | mean n/11 | 95% CI |
|---|---:|---:|---|
| `fixed` | 3 | **3.33** | [2.00, 5.00] |
| `invvar` | 3 | **3.33** | [2.00, 5.00] |

### Axis ch — chunk × BPTT

| variant | n_seeds | mean n/11 | 95% CI |
|---|---:|---:|---|
| `chunk128_K8` | 3 | **3.33** | [2.00, 5.00] |
| `chunk24_K0` | 3 | **3.33** | [2.00, 5.00] |
| `chunk64_K8` | 3 | **3.33** | [2.00, 5.00] |

### Axis dm — distance_mode

| variant | n_seeds | mean n/11 | 95% CI |
|---|---:|---:|---|
| `huber` | 3 | **3.33** | [2.00, 5.00] |
| `l1` | 3 | **3.33** | [2.00, 5.00] |
| `mse` | 3 | **3.33** | [2.00, 5.00] |

### Axis lf — loss_family

| variant | n_seeds | mean n/11 | 95% CI |
|---|---:|---:|---|
| `huber_moments` | 3 | **2.67** | [1.00, 5.00] |
| `l1_legacy` | 3 | **2.67** | [1.00, 5.00] |
| `mse_moments` | 3 | **2.67** | [1.00, 5.00] |
| `w2_only` | 3 | **3.00** | [3.00, 3.00] |

### Axis te — tail_estimator

| variant | n_seeds | mean n/11 | 95% CI |
|---|---:|---:|---|
| `kurtosis` | 3 | **3.33** | [2.00, 5.00] |
| `quantile` | 3 | **3.33** | [2.00, 5.00] |
| `softhill` | 3 | **3.33** | [2.00, 5.00] |

### Top 5 individual Phase 1 runs

| run | n/11 |
|---|---:|
| `p1_bal_fixed_seed1` | **5/11** |
| `p1_bal_invvar_seed1` | **5/11** |
| `p1_ch_chunk128_K8_seed1` | **5/11** |
| `p1_ch_chunk24_K0_seed1` | **5/11** |
| `p1_ch_chunk64_K8_seed1` | **5/11** |

## Baseline references (for §5 paper table)

- GARCH(1,1)-t fitted (per-asset, deterministic): see `experiments/002_garch_baseline/results/three_way_comparison.md`. Approximately **5-7/11** under strict bands.
- LM99 ABM (asset-agnostic): **5/11** under strict bands.
- Shi 2024 Neural Hawkes: TODO if Phase C implementation lands.

