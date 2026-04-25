# H20 run #2 analysis — 2026-04-25 15:15 CST

## What ran (via `scripts/h20_run_all_today.sh`)

1. **N-scaling** (4 configs: N=500/2K/5K/10K) — all completed, world_size=1, ~110s/each
2. **v2.1 retryA** (κ=1.0, ws=0, clip=10, lr=5e-4, warmup=30) — completed, world_size=4
3. **Eval existing** — inference on the 3 successful + 1 diverged ckpt from run #1

## CORRECTION: my run #1 analysis was wrong

I claimed "all H20 N=10K runs produce wrong-sign ACF". This was based on the
training-time `acf_sim` field, which is computed as `acf_sq_mean(r,
max_lag=8)` — **the mean ACF over lags 1..8**, not lag-1. The eval-side
`acf_squared_returns` reports **only lag 1**.

A simulator with strong lag-1 clustering but oscillation/decay collapse at
longer lags can show:
- training `acf_sim` ≈ −0.3 (average over 8 lags)
- inference `acf_squared_returns` ≈ +0.4 (lag 1 alone)

Both are "true". The right reading: **lag-1 may be fine, but the ACF decay
shape is what fails** — not a sign flip but a Goodhart-style "peak hit,
shape collapsed". This is the same failure mode that the Mac sweep's
`w_acf_shape` regulariser was designed to catch.

## Correct scoreboard from inference_merged.json (10 facts, no
   conditional_kurtosis since H20 inference module doesn't compute it)

| Run | n/10 | acf(r²) lag1 | hill | leverage | zumbach | comment |
|---|---|---|---|---|---|---|
| **v1.0 Hawkes SPX H20** | **7/10** ★ | **+0.297** ✓ | 3.79 ✓ | −4.58 ✓ | −0.009 ✗ | best — Hawkes-on-v0.6 alone |
| v2.1 SPX H20 (diverged) | 5/10 | +0.473 ✓ | 19873 ✗ | +6.60 ✗ | −0.089 ✗ | even broken, basic shape OK |
| v0.9 SPS SPX H20 | 4/10 | +0.089 ✗ (target +0.34) | 51 ✗ | −2.57 ✓ | −0.046 ✗ | weak vol clustering |
| v0.9 SPS BTC H20 | 1/10 | +0.926 ✗ (over) | 23.7 ✗ | +9.65 ✗ | −0.004 ✗ | broken — cross-asset transfer fails |

## Implications for Paper A scoreboard

1. **v1.0 Hawkes (= v0.6 + Hawkes self-excitation) is the H20 winner.**
   7/10 matches Mac's 7/11, with no v2 architecture novelty added.
2. **v2.1's Mac 9/11 was a Mac-only win.** At H20 scale even the
   conservative retryA (next section) didn't beat v1.0.
3. **v0.9 SPS doesn't transfer to BTC under default config.** That's a
   real cross-asset finding.

## v2.1 retryA training (no inference run yet)

Config: κ=1.0, ws=0, clip=10, lr=5e-4, warmup=30. world_size=4.

- loss: 2.69 → min 1.09 → 1.23 (final, settled)
- grad max: 34K (much better than first run's 39M; clip working)
- training-side `acf_sim`: −0.566 (mean over lags 1..8 = bad shape)
- training-side `hill_sim`: 9.20 (real 2.68)

**Did NOT diverge** (the conservative knobs worked). But also didn't reach
v1.0 Hawkes's 7/10 numbers based on the training log — and we don't have
inference yet to confirm.

**Next step for retryA**: run inference to get the actual 10-fact score.

## N-scaling diagnostic: incomplete without inference

I built `experiments/020_n_scaling/` to test the "ACF sign-flip with N"
hypothesis. Now that I know the metric was misleading, the diagnostic
question shifts: **does the ACF shape (lag-1 to lag-8 decay) get worse
with N?** Need inference rollouts on the four N-scaling ckpts to answer
properly.

The N-scaling ckpts probably weren't saved (the n_scaling script doesn't
explicitly write checkpoint.pt). Have to re-run with checkpoint saving
enabled, or do the eval inline.

## Recommended next H20 step

Cheapest first:
```bash
# Inference on retryA to get its real scoreboard
bash scripts/h20_inference.sh experiments/016_ecomd_v2/config_h20_spx_N10k_retryA.yaml
```

Then if v1.0 Hawkes is the winner, **promote it to a flagship config** for
Paper A and table the v2.1 typed-coupling story as Mac-only ablation.
