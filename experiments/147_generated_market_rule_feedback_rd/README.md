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
