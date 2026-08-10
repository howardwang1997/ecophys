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
