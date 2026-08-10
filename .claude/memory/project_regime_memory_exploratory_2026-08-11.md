# Real-market lagged-regime memory exploratory — 2026-08-11

Motivated by evaluator-v2 temporal-coverage failures, the study asked whether prior-half realized volatility
predicts next-half squared-return memory. It is permanently exploratory because all 14 free markets were already
spent for design. Freeze: `configs/empirical_physics/regime_memory_exploratory_v1.yaml`; result interpretation:
`papers/proposal/regime_memory_exploratory_result_2026-08-11.md`.

Coverage-only selection retained 11 symbols with all 38 non-2020 half-years supporting exact N120 blocks; EURUSD,
HSI and N225 were excluded before targets. Fit was 2005H2--2014H2; evaluations were 2015H1--2019H2 and
2021H2--2024H2. Predictor was previous-half log realized volatility with fit-only per-symbol median/IQR. M0 used
symbol fixed effects; M1 added one common slope. Inference used 17 calendar clusters, 999 common-calendar
permutations and 5,000 calendar-cluster bootstraps. 2020 stayed unparsed.

Formal primary FAIL from clean/pushed `6f92a399d`: common slope +0.003196, pooled MSE improvement 4.3769% (below
5% floor), both eras positive at 4.4823%/4.1627%, 12/17 calendar and 10/11 symbol wins. Bootstrap 90% CI was
[1.6824%, 7.2206%], but calendar-preserving permutation p=0.147 (146/999 nulls at or above real). Bootstrap cannot
override the temporal-alignment null. Volume secondary had the wrong negative slope, non-transfer across eras and
p=0.103; autocorr diagnostic degraded, so there is specificity but no nominatable law.

Artifact canonical SHA `c7c70686654b4d0a168cb1e419b6d6396e4821a3e2a0bc1a4a58cb754572659b`, file SHA
`c4c3aab72892818cb4f8057a41b393198ed7679ef9daf87b6c8316ab01e1c2f3`; 2.07 s CPU/no GPU. Binding decision:
do not lower the 5% threshold, change lag/block/model, or reuse this panel for confirmation. Stop the daily-free
lagged-regime claim and EcoMD training. Next real-physics feasibility must use more mechanism-proximal free
high-frequency observables with an event-time protocol; V100s remain idle.
