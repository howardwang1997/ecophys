# Experiment 148

This experiment is the serial execution repair for Experiment 147. It changes no scientific setting and cannot
create market evidence.

- `PREREGISTRATION.md` fixes the repair boundary and chronology.
- `execution_config.yaml` references the immutable Experiment 147 scientific files by path and SHA256 and tightens
  execution to one controller process with one numerical thread.
- At this preregistration commit, no Experiment 148 runner, test, `FREEZE.yaml` or result exists.
- The eventual formal output path is `artifacts/raw/preflight.json`; partial results and overwrite are forbidden.

Experiment 147 remains closed and must not be rerun. FITRS values, price data, V100 workers, RTX2060 and all GPUs
remain outside scope.

After the preregistration commit, the focused implementation checks are:

```bash
conda run -n ecophys pytest tests/test_market_rule_feedback_serial.py -q
conda run -n ecophys ruff check \
  experiments/148_generated_market_rule_feedback_rd_serial/run_preflight.py \
  tests/test_market_rule_feedback_serial.py
conda run -n ecophys mypy --strict \
  experiments/148_generated_market_rule_feedback_rd_serial/run_preflight.py
```

These checks validate parent hashes, exact `6600` fit/`1800` oracle task counts, task ordering, controller-PID
execution and network/GPU/thread guards. They do not call the formal suite. One development probe executed one
parent `smooth_null` task to verify the serial adapter, inspected only success/failure flags and was then removed
from the repeatable test suite; it is logged and cannot enter any result.

Only after the implementation and `FREEZE.yaml` commits are pushed, the single formal command is:

```bash
CUDA_VISIBLE_DEVICES=-1 ROCR_VISIBLE_DEVICES=-1 conda run -n ecophys python \
  experiments/148_generated_market_rule_feedback_rd_serial/run_preflight.py \
  --execution-config experiments/148_generated_market_rule_feedback_rd_serial/execution_config.yaml \
  --freeze experiments/148_generated_market_rule_feedback_rd_serial/FREEZE.yaml \
  --output experiments/148_generated_market_rule_feedback_rd_serial/artifacts/raw/preflight.json
```

The runner verifies a clean checkout, absent output, parent and repair hashes, commits, Python and package versions
before installing its network guard. It writes no checkpoint and atomically renames a complete temporary JSON only
after all tasks and diagnostics finish.

## Formal result

The sole formal run completed from clean checkout `b396d40fc` and returned
`GENERATED_RD_PREFLIGHT_FAIL`. The immutable raw artifact is
`artifacts/raw/preflight.json` (SHA256
`6b5f0ba9fd594c241a4e4977299d2e90a8c45371418b30acaaf6a27ba401532b`); the complete interpretation is in
`RESULTS.md`.

All 6,600 primary fits and 1,800 declared oracle constructions succeeded, and all five diagnostic guards passed.
Only 9/16 gated cells passed: one rounded null failed false-positive control, and all six 5% effect cells failed
the 80% power gate. The result retires the current V5 identification design before any real outcome is opened.
Experiment 148 is immutable and must not be rerun.
