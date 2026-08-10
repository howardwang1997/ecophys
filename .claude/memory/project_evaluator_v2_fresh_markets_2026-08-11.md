# Evaluator v2 fresh-market confirmation — 2026-08-11

Freeze before acquisition: `configs/evaluator_v2/fresh_market_confirmation_v1.yaml`; human protocol:
`papers/proposal/evaluator_v2_fresh_market_confirmation_freeze_2026-08-11.md`.

Unseen universe: indices `^DJI,^RUT,^N225,^FTSE,^GDAXI,^HSI`; volume ETFs `SPY,EEM,TLT,EWJ`. Spent
`^GSPC,^NDX,GLD,EURUSD=X` are excluded. Calendar splits remain 2005--2024 with 2020 sealed, so this is an
instrument holdout, not an independent macro-time holdout.

Metric-specific confirmation: autocorr/acf-squared/volume N120/240; aggregation N180/240; conditional/skew N240
secondary; Zumbach N180/240 diagnostic. Hill/DFA/leverage/Fano are excluded. Each applicable split/N needs at
least four non-overlapping blocks before metrics. Minimum eligible counts: six all-symbol, three ETF-volume, four
index-skew. Core suite requires autocorr sanity + acf-squared + aggregation + volume all eligible. A pass only
allows evaluator specification, never model scoring/training. CPU/free only; no GPU. Missing data mark the frozen
symbol ineligible and never trigger replacement.

Formal result-blind acquisition completed from clean/pushed commit `a2fe0101e`: all 200 expected annual shards
passed audit and all ten symbols satisfy the frozen N240 four-block coverage metadata. No market values/metrics were
inspected. Bound manifest `data/manifests/evaluator_v2_fresh_markets_daily_2005_2024.json` has canonical SHA
`e738e53e7ae74205f5d85fe16c070188bfa7d809df8420d2bf95391b8cd0ce0d` and file SHA
`1e0393f8f803c104e0326225ebdee7c9443bcdf38132a2a0ff23ba1d82314cf0`. Internal data root:
`/private/tmp/ecophys-evaluator-v2-fresh-data-RYarjf`.
