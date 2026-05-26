# EcoMD vs surrogate baselines — common-10-fact head-to-head

**Generated:** 2026-05-26 (analysis of the 2026-05-26 weekend batch).
**Reproduce:**
```
conda run -n ecophys python scripts/score_summary.py \
  experiments/095b_baselines_n30 \
  experiments/098c_zumdn_fine_grid_n30 experiments/098d_asset_mode_n30 \
  experiments/099b_memk_refinement_n30 experiments/100_track_b_beta_pilot_n30 \
  experiments/101_track_b_alpha_pilot_n30 \
  --exclude volume_volatility_corr
```

## Why this exists / methodology

The default scorer uses 11 stylized facts. The surrogate baselines (`WGANLPSimulator`,
`TrajCastLiteSimulator` in `scripts/run_baseline_fit_eval.py`) are **returns-only** generators —
they emit no trading-volume series, so `volume_volatility_corr` (fact #10) cannot be computed for
them. Under the 11-fact default, `score_summary.py`'s instability filter treated that absent fact
as NaN and silently dropped **all 250 baseline seeds** ("no eval results found"), making the
baseline invisible while EcoMD was still scored. That is not a fair comparison.

The `--exclude volume_volatility_corr` mode (added 2026-05-26 to `score_summary.py` /
`score_phase.py`) scores **every** model on the **shared 10 facts**, putting EcoMD and the
returns-only baselines on the same footing. EcoMD's extra `volume_volatility_corr` capability is
reported separately (below), not folded into the head-to-head score.

## Result — common 10 facts (mean pass-count across ~25–30 seeds)

| rank | model | mean (10-fact) | std | n |
|---|---|---|---|---|
| 1 | **095b `baseline_trajcast_spx`** | **5.24** | 0.78 | 25 |
| 2 | **095b `baseline_wgan_ndx`** | **5.12** | 0.78 | 25 |
| 3 | 098d `x5_zum_downside` (best EcoMD) | 4.89 | 1.50 | 27 |
| 4 | 095b `baseline_trajcast_btcusdt` / `_ndx` | 4.84 | 0.6–0.8 | 25 |
| 5 | 099b `memk_s025_lam090` | 4.64 | 1.39 | 28 |
| 6 | 101 `ha_K06_b016_u08` / `ha_K08_b016_u08` | 4.60 | 1.4–1.6 | 30 |
| 7 | 100 `bb_p010_s250` | 4.57 | 1.43 | 30 |
| — | EcoMD `baseline_v3` (reference) | 4.14 | 1.33 | 28 |

**Two surrogate baselines (`trajcast_spx`, `wgan_ndx`) beat every EcoMD configuration across all
four mechanism families** (098c zumdn, 098d asset×mode, 099b memk, 100 B-β, 101 B-α). The best
EcoMD cell anywhere is `x5_zum_downside` = 4.89; EcoMD's own `baseline_v3` (4.14) sits mid-pack.
TrajCast/WGAN are also ~2× more stable across seeds (std ≈ 0.6–0.9 vs EcoMD ≈ 1.3–1.7).

## Caveats (how to read this honestly)

- The win is **asset-specific**: `trajcast_gold` = 4.16 and `trajcast_eurusd` = 3.00 do **not**
  beat EcoMD. TrajCast/WGAN are strongest on the indices they were fit to (SPX, NDX).
- The baselines are **learned return generators fit on the target asset's real returns**, then
  sampled — matching return stylized facts is close to what they directly optimize. EcoMD is a
  mechanistic Langevin simulator; its intended value is the physics/interpretability (C2) and the
  volume channel, not out-generating a return-fitter on return facts alone.
- **For Paper A this is still a reviewer kill-shot if presented as "EcoMD reproduces stylized
  facts well."** A NeurIPS referee will run exactly this head-to-head. The defensible claims are
  (a) the mechanism-independent ceiling result and (b) capabilities the baselines lack
  (volume/volatility coupling, mechanistic knobs) — not raw fact-count superiority.

## EcoMD's extra capability (reported separately, not in the head-to-head)

On the 11th fact, EcoMD configs produce `volume_volatility_corr` in-band (e.g. seed-13 of
`ha_K04_b016_u08` = 0.63, band [0.3, 0.8]); the returns-only baselines have no volume channel and
cannot be scored on it at all. This is a genuine EcoMD capability but must be argued as such, not
counted as a fact "win."
