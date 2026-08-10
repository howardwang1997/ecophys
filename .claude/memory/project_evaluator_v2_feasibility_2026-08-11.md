# Evaluator v2 free-data feasibility freeze — 2026-08-11

## Durable decision

EcoMD v1 is stopped as a positive model paper. Do not repair its formal 2/11 result by tuning bands on the
already-seen held-out trajectories. The next zero-cost step is to qualify a replacement evaluator on real data
before it is allowed to score any simulator.

## Frozen design

- Contract: `configs/evaluator_v2/feasibility_v1.yaml`.
- Human-readable freeze: `papers/proposal/evaluator_v2_feasibility_freeze_2026-08-11.md`.
- Free daily markets: Yahoo SPX (`^GSPC`), NDX (`^NDX`), GLD and EURUSD (`EURUSD=X`), 2005--2024.
- Disjoint periods: reference 2005--2009; conformal calibration 2010--2014; confirmation 2015--2018;
  report-only 2019; sealed 2020; temporal validation 2021--2024.
- Primary matched non-overlapping block lengths are 120 and 240 observations; 500 is diagnostic.
- Split-conformal intervals use only reference/calibration blocks. Required confirmation and temporal self-coverage
  is at least 0.75 under the frozen finite-sample rule.
- Each eligible metric must also respond in its expected direction to a predeclared targeted surrogate. Surrogates
  include joint temporal permutation, sign randomization, circular volume shift and Gaussian iid replacement.
- Metric scopes are explicit: gain/loss means the current sample-skewness implementation and is equity-index-only;
  leverage is equity-index-only; volume coupling requires finite non-constant volume; daily Zumbach is diagnostic.
- Calendar 2020 stays sealed. The EcoMD-v1 held-out trajectories/results are forbidden for threshold selection.

## Compute and data policy

This feasibility phase is CPU-only and uses free data only. GPU use, paid-data purchase and H20 use are forbidden.
The two V100s remain idle. Formal acquisition must run from the exact clean/pushed freeze commit into a fresh
directory. It fails closed if the expected annual shards or schema are missing, and its no-values manifest must
be committed and bound before metric computation.

Formal acquisition completed result-blind from clean/pushed commit `0de183067568d9201377e91bfb41992990e43bfd`.
All 80 expected annual shards passed schema/provenance audit with no duplicate timestamps. The committed no-values
manifest is `data/manifests/evaluator_v2_free_daily_2005_2024.json`; canonical payload SHA is
`28560c599e9c63418732d34cee0ade29665e24eb75b5b5fc123435d0bc005666` and file SHA is
`a6d46c595041cb37d587296dac841b20b8257edd36c0c5ae65bec112bf243eba`. Raw data are internal-only under
`/private/tmp/ecophys-evaluator-v2-data-viDtFu`; no prices, returns or metric outputs were inspected before binding.

## Decision gate

Do not design a new EcoMD score from this study unless real-data self-coverage and surrogate falsification both
pass under the frozen rules. Failure is an evaluator result, not permission to retune after inspection.

## Implementation freeze

`ecomd/eval/evaluator_v2.py` and `scripts/run_evaluator_v2_feasibility.py` implement the bound study. Before any
real metric output, the remaining machine-level semantics were fixed: real-minus-within-block-control-median is
the paired effect; pooled IQR contains all real and all eight-replicate control estimates; direction ties and
nonpositive IQR fail; selection-finiteness excludes report-only 2019; volume eligibility requires three markets.
The runner requires clean HEAD equal to upstream, verifies all 80 raw file hashes and each non-sealed return hash,
and never parses sealed-2020 values. Synthetic tests deliberately confirm that unchanged L=120 aggregational
Gaussianity and DFA can fail finite-sample requirements rather than being silently adapted. Pre-output validation:
140 tests pass, Ruff passes, and strict mypy passes all 76 package modules.

The first formal invocation from `71ed5a9b6` produced no artifact: diagnostic-only Zumbach's
`report_no_eligibility_decision` string reached the eligibility relation parser. No values were printed or
inspected. The execution-only fix keeps diagnostic real/control estimates, sets `passed: null`, and excludes them
from eligibility as the original protocol requires; it has a direct regression test. No scientific rule changed.
