# Evaluator v2.1 synthetic sample complexity — 2026-08-11

After evaluator-v2 formal FAIL, calibrate the measurement instruments on known DGPs before any fresh-market
confirmation. Contract: `configs/evaluator_v2/sample_complexity_v1.yaml`; human freeze:
`papers/proposal/evaluator_v2_sample_complexity_freeze_2026-08-11.md`.

The study is synthetic/CPU-only and makes no market/model claim. Grid N=120,180,240,500,1000,2000,4000;
64 independent paths and eight deterministic controls per path. Every metric has a property-bearing signal DGP and
a confound-preserving null DGP. Signal requires complete finiteness, direction fraction >=0.80 and median paired
effect >=0.5 pooled-IQR; null must be equivalent within 0.5 IQR. The minimum admissible N must pass at that N and
all longer grid lengths. Analytic floors: aggregation/Zumbach 180, DFA/conditional/skew 240, Hill 500, Fano 2000,
and 120 otherwise. Zumbach remains diagnostic.

The current SPX/NDX/GLD/EURUSD 2015--2024 results are spent and forbidden for redesigned-estimator confirmation.
A synthetic pass only allows a new, separately frozen free-market holdout protocol. No thresholds/DGP/grid changes
after output. Keep V100s idle.

Implementation is in `ecomd/eval/synthetic_dgps.py` and
`scripts/run_evaluator_v2_sample_complexity.py`. DGP tests verify deterministic finite paths plus the declared skew,
volatility-memory, leverage and volume-coupling structures. A reduced full matrix exercises every metric, length,
signal/null and diagnostic branch. Pre-output validation: 146 tests pass, strict mypy passes 77 package modules,
and Ruff passes. The formal runner requires clean HEAD equal to upstream and verifies the source evaluator result.

Formal result: `results/evaluator_v2/sample_complexity_v1.json`, clean/pushed commit `3fe5a5eed`, canonical SHA
`376eeca24355e0d5ce1eebc0cb4b67ebcf3962019da651aa5de7c8a48881a183`, file SHA
`d1f920f300711bf5118c34de0c4f787f0cd79c2700dd0ab1c2a74e899f9ca73a`, CPU runtime 129.90 s/no GPU.
Frozen-fixture minima: autocorr/acf-squared/volume 120; aggregation 180; conditional/skew 240; Hill/DFA/leverage
500; Fano 2000; Zumbach diagnostic. All minima and longer grid cells pass signal/null with complete 64×8 data.

Reviewer constraint: these are optimistic strong-signal DGP detectability floors, not universal sample complexity or
market evidence. Real feasibility-v1 FAIL remains binding. Four-role non-overlap requires about 16N observations:
N500 needs ~31.7 years and N2000 ~127 years per market. Near-term fresh-market P0 is acf-squared, volume coupling
and aggregation; conditional/skew remain falsification targets, long-N metrics depend on coverage, and Fano exits
the per-market near-term set.
