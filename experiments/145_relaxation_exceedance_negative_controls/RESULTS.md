# Experiment 145 result — relaxation exceedance does not identify adaptation

**Formal decision:** `ATTRIBUTION_NOT_IDENTIFIED`  
**Candidate admission:** false  
**Novelty pass:** false  
**Adaptation identified:** false  
**Raw SHA-256:** `9b752b4ad428ceb56d82483f94cf7e3c92d26ed3869cbe8a7ddbfbe75c5c5d4f`

## Chronology

- V2 plan frozen at `dca7ce36d`.
- Experiment preregistered at `f7ce84bff`.
- Implementation committed at `6fe7a8f06`.
- Hash freeze and formal-run checkout at `0ca8fe1a3`.
- The clean-checkout runner executed once and wrote the raw artifact without overwrite.

## W1 — omitted fixed slow mode

The declared baseline envelope was `0.6^L`; the fixed hidden mode was `0.9^L`. At every preregistered lag
`L=1,...,8`, the latter exceeded the former. At `L=8`, the two values were approximately `0.01680` and `0.43047`,
with positive margin `0.41367`.

No transition parameter changes with time or history. The witness therefore confirms
`CONFIRMED_HIDDEN_SLOW_MODE_EXCEEDANCE`: the rejection may be caused by an omitted but non-adaptive state with a
longer timescale than the audited baseline class.

## W2 — fixed clock representation

A single fixed six-state row-stochastic operator reproduced the entire preregistered path
`[0.25, -0.10, 0.60, 0.20, -0.35, 0.05]` with maximum absolute error `0.0`. Its one-step Dobrushin coefficient was
`1.0`, and neither the transition matrix nor observable was updated.

Decision: `CONFIRMED_FIXED_CLOCK_REPRESENTATION`.

This is an impossibility witness, not a proposed market model. Any bounded finite path can be encoded in the same
way by augmenting a time-homogeneous state with a deterministic clock. Consequently, a finite response curve alone
cannot exclude non-adaptive hidden-state explanations. The chain lies outside a strictly contractive baseline
class; that is exactly why observed exceedance diagnoses class incompleteness rather than adaptation.

## Scientific consequence

The admissible logical conclusion of

\[
|R_{obs}(L)|>B_L
\]

is `the true response is outside the declared baseline class B`, subject to causal-control validity. It is not
`agents learned`, `beliefs changed` or `the residual is behavioral`. Even a well-controlled event study can
identify a dynamic treatment response while leaving the mechanism label unidentifiable.

Experiment 145 therefore supports the v2 NCS decision `NCS_C0_FAIL_IDENTIFICATION`. Reopening would require an
independently measured state-completeness restriction or an intervention that separates adaptive updates from all
fixed hidden-state alternatives. Adding more flexible baselines after seeing the response is not a repair because
it destroys the prospective test.

## Resource audit

- Inputs were committed constants only.
- Market files read: 0; sealed periods opened: 0; data purchased: none.
- Device: Mac CPU; runner wall time `0.02294` s; GPU use `0.0` hours.
- Neither V100 worker nor the RTX2060 was contacted.

