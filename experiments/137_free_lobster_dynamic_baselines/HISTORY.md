# Experiment 137 execution history

- `b9fe0569d`: protocol and initial implementation frozen before fitting.
- `30fd294d9`: fixed shard-count-dependent seeds and moved the 4/5 performance gate to aggregation. GOOG was
  rerun; the old result is retained as `NONCANONICAL_GOOG_PRE_SEED_FIX.json` and is not evidence.
- `5fa745ef4`: added single-archive scheduling while preserving the global archive index/seed. This allowed
  each SHA-verified file to run as it arrived over a constrained link. All five canonical artifacts report
  this execution commit.
- `REPLICATION_GOOG_30FD294D9.json` and canonical `ARCHIVE_2_CUDA.json` have identical audit/model dictionaries,
  confirming that the scheduling-only change did not alter the scientific result.
- All five canonical artifacts are RTX2060 CUDA runs at `5fa745ef4`. `REPLICATION_AAPL_CPU.json`,
  `REPLICATION_MSFT_CPU.json` and `REPLICATION_SPY_CPU.json` are cross-device portability diagnostics, not
  additional independent paths. Their largest held-out combined-NLL difference from CUDA is 0.0164 nats/event.
