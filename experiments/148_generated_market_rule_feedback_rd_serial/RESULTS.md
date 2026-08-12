# Experiment 148 results — generated annual market-rule-feedback RD preflight

**Decision:** `GENERATED_RD_PREFLIGHT_FAIL`

**Formal checkout:** `b396d40fcc29cdf25daddd457b7d908b6d4f1d97`

**Raw artifact:** `artifacts/raw/preflight.json`

**Raw SHA256:** `6b5f0ba9fd594c241a4e4977299d2e90a8c45371418b30acaaf6a27ba401532b`

## Result in one paragraph

The frozen analysis is not adequate for the proposed real-data study at the blind official-register sample scale.
Only 9 of 16 gated cells passed. The cutoff-10 rounded null rejected 25/300 times (`8.33%`, Wilson 95% upper bound
`12.01%`), exceeding both the `8%` point threshold and `11%` upper-bound threshold. More decisively, every
`|tau|=0.05`, `sigma=0.10` effect cell missed the 80% power gate: non-clustered power was `48.67%--56.33%`, and
clustered power was `33.67%`. These failures are not driven by optimizer/API instability or large point-estimate
bias: all 6,600 `rdrobust` fits succeeded, all gated absolute median biases were below `0.004`, all 1,800 oracle
intervals were constructed, and every diagnostic guard passed. The current V5 identification design therefore
retires before any instrument-level market outcome is opened.

This result does not show that the real annual tick--ADNT feedback is zero. It shows that the frozen design cannot
reliably control error and detect the preregistered Nature-scale 5% effect under its own plausible generated cases
and available sample envelope. Re-running, changing seeds, relaxing thresholds or inspecting real signs to choose
a new design is prohibited.

## Gated cells

`Sig.` is null rejection for null cases and power for effect cases. `Wilson` is its 95% Wilson interval. `Coverage`
uses the robust bias-corrected interval. `Bias` is `|median(tau_hat)-tau|`. Oracle coverage applies only to the six
declared independent Gaussian null/cutoff cells.

| Scenario | Cutoff | Decision | Successful fits | Sig. | Wilson 95% | Coverage | Sign | Bias | Oracle coverage | Failed gates |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| smooth null | 10 | PASS | 300/300 | 7.33% | [4.89%, 10.85%] | 92.67% | — | 0.00004 | 98.00% | — |
| smooth null | 600 | PASS | 300/300 | 3.67% | [2.06%, 6.45%] | 96.33% | — | 0.00116 | 99.00% | — |
| rounded null | 10 | **FAIL** | 300/300 | 8.33% | [5.71%, 12.01%] | 91.67% | — | 0.00168 | 98.67% | rejection, Wilson upper |
| rounded null | 600 | PASS | 300/300 | 6.33% | [4.09%, 9.68%] | 93.67% | — | 0.00395 | 99.67% | — |
| curved null | 10 | PASS | 300/300 | 7.33% | [4.89%, 10.85%] | 92.67% | — | 0.00167 | 100.00% | — |
| curved null | 600 | PASS | 300/300 | 4.67% | [2.80%, 7.68%] | 95.33% | — | 0.00147 | 100.00% | — |
| regression-to-mean null | 10 | PASS | 300/300 | 6.33% | [4.09%, 9.68%] | 93.67% | — | 0.00149 | — | — |
| regression-to-mean null | 600 | PASS | 300/300 | 7.33% | [4.89%, 10.85%] | 92.67% | — | 0.00038 | — | — |
| MCAR attrition null | 10 | PASS | 300/300 | 6.67% | [4.36%, 10.07%] | 93.33% | — | 0.00302 | — | — |
| clustered null | 10 | PASS | 300/300 | 4.67% | [2.80%, 7.68%] | 95.33% | — | 0.00061 | — | — |
| reinforcing +5% | 10 | **FAIL** | 300/300 | 52.33% | [46.69%, 57.92%] | 96.00% | 97.33% | 0.00027 | — | power, Wilson lower |
| reinforcing +5% | 600 | **FAIL** | 300/300 | 54.33% | [48.68%, 59.88%] | 92.33% | 95.67% | 0.00137 | — | power, Wilson lower |
| corrective -5% | 10 | **FAIL** | 300/300 | 48.67% | [43.06%, 54.30%] | 94.33% | 96.67% | 0.00144 | — | power, Wilson lower |
| corrective -5% | 600 | **FAIL** | 300/300 | 50.67% | [45.04%, 56.28%] | 94.00% | 98.00% | 0.00187 | — | power, Wilson lower |
| mixed-exposure +5% | 10 | **FAIL** | 300/300 | 56.33% | [50.68%, 61.83%] | 94.00% | 96.67% | 0.00270 | — | power, Wilson lower |
| clustered reinforcing +5% | 10 | **FAIL** | 300/300 | 33.67% | [28.56%, 39.19%] | 93.33% | 93.00% | 0.00186 | — | power, Wilson lower, sign |

## Descriptive high-noise cells

These `sigma=0.20` results were preregistered as descriptive and did not enter the overall decision. Power ranged
from `14.33%` to `18.67%` across the six effect cells. They reinforce, but are not needed for, the conclusion that
the blind support envelope is inadequate for a 5% effect.

| Scenario | Cutoff | Power | Wilson 95% | Coverage | Bias |
|---|---:|---:|---:|---:|---:|
| reinforcing | 10 | 16.33% | [12.58%, 20.94%] | 95.33% | 0.00509 |
| reinforcing | 600 | 18.67% | [14.66%, 23.46%] | 93.00% | 0.00436 |
| corrective | 10 | 18.00% | [14.07%, 22.74%] | 92.67% | 0.00043 |
| corrective | 600 | 16.67% | [12.88%, 21.30%] | 94.33% | 0.00515 |
| mixed exposure | 10 | 15.67% | [11.99%, 20.21%] | 95.67% | 0.00227 |
| clustered reinforcing | 10 | 14.33% | [10.82%, 18.75%] | 95.33% | 0.00126 |

## Diagnostic and execution audit

- Sorting detection: `300/300`.
- Differential-attrition detection: `300/300`.
- Coarse-mass-point refusal: `300/300`; every replicate had one distinct left and two distinct right values inside
  the frozen bandwidth.
- Shared RTS 28 cutoff labels: `2/2` correct.
- Statutory zero/nonzero tick first-stage labels: `5/5` correct.
- Primary fits: `6,600/6,600`; fit failures: `0`.
- Oracle attempts/successes: `1,800/1,800`; oracle failures: `0`.
- Wall time: `76.8363 s`; one controller, zero workers, one numerical thread.
- Conservative CPU use: `0.02135 core-hours`; maximum RSS: `0.1965 GB`.
- Market/FITRS/price/paid/sealed files, network calls, remote workers and GPU-hours: all zero.

Matplotlib emitted a cache-directory warning during package import and built a temporary font cache. It did not
alter a DGP, fit, gate, artifact path or decision, and the run remained inside the frozen wall/RAM bounds.

## Decision and route

Experiment 148 is immutable and may not be rerun. Its `GENERATED_RD_PREFLIGHT_FAIL` activates Experiment 147
Section 5's stop rule: retire the current V5 identification plan before market outcomes. No FITRS instrument pair,
date-correct price, FCA sealed record, V100 or RTX2060 job is authorized.

The annual policy feedback remains a scientifically meaningful hypothesis that would require a prospectively new
data/design opportunity, such as substantially denser independent cutoff support or an exogenous reclassification
with a stronger first stage. It cannot be reopened by buying ordinary data, increasing GPU compute, changing the
effect floor, adding years post hoc or using EcoMD to manufacture power. A new topic iteration must define its
scientific object and metadata-level feasibility gate before outcome inspection.
