# C4 stragglers — root cause analysis (Mac N=1000 + H20 N=10K)

**Caveat first**: Mac N=1000 with `strict=False` ckpt load gives a
DIFFERENT effective architecture than H20 N=10K (twopop_type_idx is a
buffer regenerated at simulator init for the new N). So Mac per-fact
numbers don't reproduce H20. Reliable diagnosis only on facts where
both platforms tell the same story.

## Summary table

| Fact | H20 N=10K (real) | Mac N=1000 (imperfect) | Reliable? | Fix candidate |
|---|---|---|---|---|
| autocorr_returns | +0.27 | ρ(1)=-0.70 | ✗ DIVERGES | retrain after fix |
| volume_vol_corr | -0.38 | +0.20 | ✗ DIVERGES | retrain after fix |
| **zumbach** | **-0.067** | **-0.044** | **✓ AGREES (sign)** | multi-scale Hawkes |

## Reliable: #11 zumbach_asymmetry — single-scale Hawkes

Both Mac (-0.044) and H20 (-0.067) show negative D̄ (anti-Zumbach).
D̄ monotonically decreases with τ (more negative at longer τ).

**Mechanism**: Hawkes single EMA with α=0.1 makes "past fine vol predicts
future fine vol" (10-step memory) the dominant correlation. The "past
coarse → future fine" Zumbach asymmetry requires LONGER memory in the
past channel.

**Fix**: multi-scale Hawkes (P2 already implemented):
- $M^{(s)}_t$ short EMA (α=0.1, 10-step)
- $M^{(l)}_t$ long EMA (α=0.005, 200-step)
- excitation = κ_s M^(s) + κ_l M^(l)

Weekend configs B2/F1/F2/F3/I1 test this. Highest priority for paper.

## Unreliable on Mac — H20 numbers + theory suggest:

### #1 autocorr_returns +0.27

**Likely mechanism**: Hawkes excitation κ·M_t·sign(β·ED_t) amplifies
same-sign streaks — high recent vol → next price step amplified in
same direction. Creates positive ρ(1).

**Fix candidates** (untested):
- Reduce κ from 0.3 to 0.1
- Sign-flipping Hawkes (−sign instead of +sign)
- Higher w_autocorr_r (weekend F0 tests 0.5→1.5)

### #2 volume_volatility_corr -0.38

**Likely mechanism**: twopop γ-heterogeneity (0.7-1.5×) → low-γ agents
move less, dominate calm regimes → low volume during calm. Hawkes burst
in PRICE layer doesn't propagate to agent state directly, so volume
(= Σ|Δs_{i,0}|) doesn't track vol burst. Negative correlation results.

**Fix candidates** (NOT in weekend batch):
- Connect Hawkes back to agent state forcing
- Redefine volume to be price-driven (|Δp|·stake)
- Drop γ-heterogeneity, keep only T-heterogeneity

## Recommended next steps

1. **Add `--save-trajectory` to inference** so Mac analysis can be
   architecture-faithful (use H20-trained ckpt's actual sim, no shrink).
2. **Weekend's expected wins** (zumbach in F1/F2/F3) — confirm fixes #11.
3. **Volume + autocorr fixes** (architectural) — out of weekend scope;
   follow-up work.
