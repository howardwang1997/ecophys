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
