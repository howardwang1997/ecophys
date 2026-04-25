# H20 first run analysis — 2026-04-25 14:30 CST

## Inventory

| Job | Variant | N | Hawkes κ | training | grad max | status |
|---|---|---|---|---|---|---|
| 01 | v0.9 SPS SPX daily | 10000 | 0.0 | 200/200 | 21K | ✓ |
| 02 | v0.9 SPS BTC 1m | 10000 | 0.0 | 200/200 | 92K | ✓ |
| 03 | v1.0 Hawkes SPX | 10000 | 0.3 | 200/200 | 75K | ✓ |
| - | v2.1 SPX (κ=2.0, ws=0.3) | 10000 | 2.0 | 200/200 | **39M** | **DIVERGED** |
| - | v2 ablation grid (60-cell) | — | — | — | — | killed (manual) |
| 04 | crash OOS v0.8 | 200 | — | — | — | ✗ `python` not in PATH |

## Inline `acf_sim` (last-10 mean) vs real targets

Real target acf(r²) for SPX = +0.342, for BTC = +0.152.

| Run | acf_sim final | acf_real | sign |
|---|---|---|---|
| v0.9 SPS SPX | **−0.326** | +0.342 | ❌ flipped |
| v0.9 SPS BTC | **−0.579** | +0.152 | ❌ flipped (worst) |
| v1.0 Hawkes SPX | **−0.362** | +0.342 | ❌ flipped |
| v2.1 SPX (diverged) | −0.291 | +0.342 | ❌ flipped (chaotic anyway) |

**All four runs at N=10K produce anti-clustering of squared returns.** Mac
N=200 with the same v0.9 base recipe got acf_lag1 ≈ +0.18 (positive but
weak); v2.1 + κ=2.0 + shape on Mac N=200 hit +0.45. **Going from N=200 to
N=10K flips the sign.**

## v2.1 divergence trajectory

| iter | loss | grad | acf_sim | hill_sim |
|---|---|---|---|---|
| 0 | 3.32 | 124 | −0.539 | 19 |
| 25 | 35.1 | 1543 | −0.65 | 8 |
| 50 | 116 | 10,450 | −0.65 | **182** |
| 100 | 526 | 174K | −0.61 | **2,022** |
| 199 | 3208 | **39M** | −0.10 | **32,081** |

`hill_sim` runaway is the trigger. Strong Hawkes (κ=2.0) at N=10K creates
extreme bursts → top-5% tail estimator unstable → loss term unbounded.
`grad_clip=100` (set loose for v1 MACE-lite "clip caps lr" issue) too loose
for v2 + strong Hawkes. By iter 30 grad_norm 2884 had already broken
threshold; by iter 50 the dynamics chaotic.

## Three findings to lock

### 1. **N=10K ACF(r²) sign-flip**

This is **the** Paper A N-scaling finding. Same recipe / loss / lr that
gives positive (real-direction) vol clustering at N=200 produces
**anti-clustering** at N=10K. Affects all three architectures (v0.9 SPS,
v1.0 Hawkes, v2.1) — not specific to v2.1.

**Hypothesis pool** (need diagnostic to pin):
- *(H1)* Langevin noise √(2γT/m) overwhelms inter-agent coupling at large N
  → returns become approximately IID → r² becomes anti-correlated by
  finite-sample noise.
- *(H2)* `chunk_steps=24` BPTT too short — at N=10K simulator hasn't
  reached steady state when the loss is computed; transient dominates.
- *(H3)* `dt=0.01 + lr=1e-3 + clip=100` interacts badly: lr is calibrated
  for Mac scale, but with 50× more agents the per-agent gradient signal
  is 50× larger after backprop through the pair sum.

**Test**: `experiments/020_n_scaling/` — train v0.9 at N ∈ {500, 2000,
5000, 10000} with identical recipe; observe where acf_sim crosses zero.

### 2. **v2.1 N=10K + κ=2.0 unstable**

Mac winner config diverges. Two parallel rescue paths:
- **Path A** (`config_h20_spx_N10k_retryA.yaml`): drop to κ=1.0, ws=0,
  clip=10, lr=5e-4. Mac sweep showed κ=1.0+ws=0 alone gave 7/11. Less
  ambitious but should be stable.
- **Path B** (not authored yet): keep κ=2.0+ws=0.3 + clip=5, lr=5e-4,
  warmup=30. Run only after Path A confirms scoring infra works.

### 3. **`tomorrow.sh` Job 04** broken on H20

`conda run -n ecophys python ...` errored with `python: command not
found`. Inside `conda run`'s subshell, env's `bin/` may not be on PATH.
Fixed in this commit to use `${CONDA_PREFIX}/bin/python` directly.

## Next H20 commands

```bash
git pull

# 1. Diagnostic — N-scaling sign flip (most important Paper A datum)
bash scripts/h20_n_scaling.sh

# 2. v2.1 retry Path A (κ=1.0, conservative)
CONFIG=experiments/016_ecomd_v2/config_h20_spx_N10k_retryA.yaml \
  bash scripts/h20_launch_v2.sh

# 3. Eval the 3 already-trained ckpts to get full 11-fact scoreboard rows
bash scripts/h20_eval_existing.sh

# 4. Re-run crash OOS (now that python-path bug is fixed)
${CONDA_PREFIX}/bin/python experiments/015_crash_oos/run.py \
  --config experiments/015_crash_oos/config_v08_train_2015_2019.yaml
```

Total wall time estimate: ~25 min for all four sequentially on 4-card
H20.
