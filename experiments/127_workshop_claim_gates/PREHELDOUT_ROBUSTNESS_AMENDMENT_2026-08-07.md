# Experiment 127 — pre-held-out robustness amendment

**Frozen:** 2026-08-07 06:57 NZST, while both V100 training services were active. A read-only audit at
freeze time found zero calibration or held-out trajectory files on either node.

## Motivation

The seven E1 checkpoints use the same 16 held-out rollout seeds. The binding primary hierarchical
bootstrap remains exactly as specified in `PREREG.md`: it resamples checkpoints and then trajectories
within checkpoints. That calculation does not preserve cross-checkpoint dependence induced by common
random numbers. This amendment adds a secondary robustness calculation before any learned calibration
or held-out output exists.

## Frozen secondary calculations

1. **Crossed checkpoint/common-seed bootstrap.** Use only the E1 checkpoints with a calibration
   W-star, exactly as in the primary estimand. For each of 2,000 replicates, resample the scorable
   checkpoints with replacement and draw one common 16-index trajectory resample that is applied to
   every selected checkpoint. Compute each selected checkpoint's median paired Hill difference and
   then their equal-weight mean. Use seed `127902` and the percentile 95% interval.
2. **Market-balanced leave-one-out diagnostic.** Freeze the groups SPX (baseline, concave), NDX,
   gold, EUR/USD, and BTC (baseline, concave). Average checkpoint medians within each represented
   market, average markets equally, and report every leave-one-market-out value and their range.

The original primary effect, interval, and E-A/E-B/E-C rules are unchanged. These secondary results
cannot upgrade the registered tier. If the common-seed interval includes zero while the primary
interval excludes zero, or a leave-one-market-out estimate changes sign, the disagreement must be
reported and any broad checkpoint-independence wording removed.
