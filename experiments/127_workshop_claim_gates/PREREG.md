# Experiment 127 — Binding pre-registration

**Frozen:** 2026-08-07 NZST, before new implementation outputs, retraining, or held-out rollouts.

This document binds the Paper E confirmatory analysis and the conditional Paper S diagnostic. Existing
exp123--126 summaries are prior evidence and are not confirmatory observations for exp127.

## E0 constants

- usable return length: `T=8000` (`run_large --n-steps=8001`, followed by its existing one-return drop);
- fixed scoring length: `L=4000`;
- learned-model calibration/held-out counts: 16/16 per checkpoint;
- W sensitivity grid: `{0,50,100,200,500,1000,1500,2000,3000}`;
- energy-distance block length: 500;
- gate block starts: `{0,500,1000,1500,2000,2500,3000,3500,4000}`;
- late block starts: `{6000,6500,7000,7500}`;
- checkpoint-level statistic: median trajectory distance;
- late-null tolerance: one-sided 95th percentile of 2000 trajectory-level bootstrap replicates;
- persistence rule: three consecutive 500-step blocks within tolerance;
- maximum valid W-star: 3000;
- Hill estimator: the repository canonical return estimator with `k_frac=0.05`; estimator implementation hash
  is frozen in the execution manifest;
- target pass count uses the repository's frozen canonical 11 bands. Continuous target distance is the
  mean across facts of zero inside the band and distance to the nearest bound divided by band width
  outside it; estimates are first aggregated by held-out trajectory median at each W;
- confidence intervals: 95%, 2000 hierarchical bootstrap replicates;
- all random bootstrap operations use explicit seeds in the generated analysis manifest.

The robust scale is calibration-late median/MAD. A dimension with MAD below `1e-12` uses scale 1.0 and
is flagged. No empirical target band enters scale, threshold, or W-star selection.

## E1 primary hypothesis and decision

For the pre-specified learned checkpoints, initialization relaxation changes fixed-length tail scoring:
the checkpoint-level aggregate of
`Hill([W-star,W-star+4000)) - Hill([0,4000))` is nonzero with a 95% interval excluding zero, and the
direction is consistent with the known warm-up artifact (post-gate Hill is larger/lighter).

The primary test is one aggregate learned-model effect; per-asset effects are secondary and fully
reported. A ranking flip is neither required nor promoted to primary. A checkpoint with no W-star is a
reported failure to verify stationarity, not excluded from the no-W-star rate and not assigned an
invented score.

The point estimator is the equal-weight mean of checkpoint-level median paired Hill differences. The
hierarchical bootstrap resamples checkpoints, then held-out trajectories within each sampled
checkpoint, and recomputes that statistic. A checkpoint is *scorable* when calibration produced a
W-star; held-out gate transfer is reported separately and is *confirmed* only when the frozen
three-block rule passes held-out data. E-A requires all seven E1 asset/family checkpoints to be both
scorable and confirmed. Five or six scorable checkpoints can support only E-B case-study wording;
fewer than five is E-C. The aggregate interval is calculated on scorable checkpoints, regardless of
held-out gate outcome, and is never described as covering missing or unconfirmed checkpoints.

## E2 specificity and sensitivity

At the pseudo-checkpoint level:

- long-burn GARCH-t and stationary-start AR(1)-SV are specificity controls;
- cold-low and cold-high groups are sensitivity controls;
- the energy gate is acceptable only if the upper 95% Wilson bound of its pooled analytic stationary
  false-positive rate is at most 0.15;
- sensitivity is characterized by detection rate and delay with Wilson intervals; no minimum positive
  rate is imposed post hoc;
- a methods-level E-A claim additionally requires the energy gate to improve at least one pre-specified
  tradeoff over both fixed W baselines without worsening stationary false positives beyond the bound:
  cold-start detection, median detection delay, or absolute fixed-length score error to long-burn.

The 0.15 bound is a finite-sample safety bound, not the nominal per-distance 0.05 quantile. If it fails,
the gate is not recalibrated on held-out results; Paper E becomes E-C or a clearly limited audit after a
new future pre-registration.

## E3 scope

`sv_d3_both` seeds `{0,1,2}` are a within-EcoMD architectural robustness test. They are not an
independent neural-SDE family. At least 2/3 must show the same sign of the held-out Hill difference for
the within-family transfer statement; otherwise report the null/heterogeneity and use E-B wording.

## E4 baseline rules

- Fixed W baselines are exactly 500 and 1000.
- The ADF/KPSS gate tests both returns and absolute returns in each 500-step block. A block passes only
  if ADF rejects its unit-root null at `p<0.05` and KPSS fails to reject its stationarity null at
  `p>0.05` for both series. Tests use a constant, ADF maximum lag 10 with AIC autolag, and KPSS
  automatic lag selection. This four-test rule is evaluated per calibration trajectory; a
  checkpoint-level block passes when at least 8/16 trajectories pass. W is the first of three
  consecutive checkpoint-level passing blocks, capped at 3000.
- Test direction, p thresholds, block sizes, and persistence rule are not altered after any result.
- W=0/500/1000 never receive model-specific tuning.

## Paper E tiers

- **E-A:** E1 held-out effect passes; analytic stationary false positives pass; cold-start response is
  detectable; E3 has same-sign replication on at least 2/3 checkpoints; and E4 gives a nontrivial
  advantage under the frozen rule.
- **E-B:** E1 and analytic specificity pass, but E3 or E4 does not support broad wording. Submit only an
  EcoMD case study/protocol audit and show the limitation.
- **E-C:** E1 vanishes, stationary false positives fail, fixed-length scoring cannot be maintained, or
  any main result needs target leakage/post-hoc threshold changes. Do not submit the method claim.

## Conditional Paper S rule

This rule is evaluated only after Paper E work is complete. Arms, doses, shock time, and recovery
settings must be copied from the exp126 representative configuration into the execution manifest before
any conditional rollout is inspected.

Primary S contrast: paired coherent-minus-balanced post-shock Hill deficit. Paper S survives only if:

1. all three recovery estimators give the same recovery direction at windows 200, 500, and 1000;
2. at least 3/4 pre-specified checkpoints show the same coherent-minus-balanced direction;
3. the checkpoint-level aggregate 95% interval excludes zero;
4. raw/post-impact provenance and numerical-integrity checks pass.

Failure kills the standalone coherence diagnostic. No trained-Levy, extra asset, dose search, or
alternative estimator may be promoted to replace it in this workshop cycle.

## Deviations and missingness

All missing checkpoints, training divergence, OOM, corrupted shards, no-W-star outcomes, nulls, and
implementation deviations are written to `RESULTS.md`. A failed shard may be rerun only with the same
manifest row and seed. Scientific hyperparameter changes require a new labeled exploratory run and
cannot enter the confirmatory result.
