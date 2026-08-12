# Experiment 147

This directory freezes the generated-data identification preflight for V5 annual endogenous market-rule feedback.

- `PREREGISTRATION.md` fixes the estimand, generated cases, estimators, gates and chronology.
- `config.yaml` contains generated constants only.
- The estimator module, focused tests, runner, implementation freeze and result do not exist at the
  preregistration commit.
- After the freeze, the formal output will be `artifacts/raw/preflight.json` and will be immutable.

The experiment can validate an RD analysis path or stop it. It cannot establish a market feedback effect, method
novelty, simulator validity, NMI/NCS readiness or any claim about a real instrument. It uses Mac CPU only; FITRS
records, price data, V100 workers, RTX2060 and all GPUs remain outside scope.

Chronology is part of the experiment: this directory must first be committed and pushed by itself. Development
tests may then use deterministic micro-fixtures, but the 300-replicate formal suite cannot run until a later
implementation commit and `FREEZE.yaml` have both been pushed.

The implementation uses the `research` optional dependency group in `pyproject.toml`, which pins
`rdrobust==2.0.0`. From the `ecophys` Conda environment, the focused pre-freeze checks are:

```bash
conda run -n ecophys pytest tests/test_market_rule_feedback_preflight.py -q
conda run -n ecophys ruff check ecomd/research/market_rule_feedback_preflight.py \
  experiments/147_generated_market_rule_feedback_rd/run_preflight.py \
  tests/test_market_rule_feedback_preflight.py
conda run -n ecophys mypy --strict ecomd/research/market_rule_feedback_preflight.py \
  experiments/147_generated_market_rule_feedback_rd/run_preflight.py
```

After the implementation and `FREEZE.yaml` commits are both pushed, the one permitted formal command is:

```bash
CUDA_VISIBLE_DEVICES=-1 conda run -n ecophys python \
  experiments/147_generated_market_rule_feedback_rd/run_preflight.py \
  --config experiments/147_generated_market_rule_feedback_rd/config.yaml \
  --freeze experiments/147_generated_market_rule_feedback_rd/FREEZE.yaml \
  --output experiments/147_generated_market_rule_feedback_rd/artifacts/raw/preflight.json
```

The runner refuses a dirty checkout, an existing output, a hash/version mismatch, an exposed accelerator or an
unfrozen resource contract. A Python audit hook rejects socket DNS, bind, connect and send-to events in the main
and worker processes. One controller plus three workers each receive one numerical thread; wall time, a
conservative four-process CPU-hour upper bound and resident memory are audited against the frozen limits.
