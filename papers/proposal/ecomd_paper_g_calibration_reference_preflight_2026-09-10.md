# Paper G: calibration references for experimental field evaluation

PRIVATE / INTERNAL — discovery infrastructure, not a manuscript or public evidence.
Session began 2026-09-10 00:08 NZST (2026-09-09 12:08 UTC).
Decision: **partial capability; no re-entry or qualified topic**.

This continues the observation-truth preflight. The named contribution blockers
remain `exact_and_stochastic_physical_supervision_have_direct_parents` and
`no_new_variance_cost_result`. The bounded task was to establish what independent
reference the experimental assets actually provide. It is not another neural-PDE
question-generation cycle. Two selected full texts, one publisher abstract, one
dataset metadata record and one dataset schema were assessed.

## What the references establish

| Asset | Established capability | Unqualified extension |
| --- | --- | --- |
| Thermochromic particle measurements | Temperature calibration against plate thermistors; stable-stratification validation | Joint velocity–temperature error covariance, independently measured gradients, transfer of a calibration bound to every convection state |
| Transitional-jet PIV database | Nominal and higher-dynamic-range measurements; separate reference-precision assessment | An error-free reference or automatic calibration of another apparatus |
| RealPDEBench | Experimental observation sequences, matched operating parameters in simulation, documented control and calibration procedures | Identical hidden initial states, complete physical fields, spatially resolved reference-error certification |

Käufer and Cierpka calibrate particle colours against PT-100 references at 16
temperatures spanning 19.7–22.7 °C. The reported sub-0.2 K quantity is the
temperature standard deviation at calibration steps, not a universal coverage
bound. Their stable-stratification comparison assumes a conductive reference
profile; the actual sidewall boundary conditions matter. Velocity uncertainty is
left for dedicated assessment. At publication, supporting data were available
on request. That dated statement does not determine the contents of the later
public AIVT release. Read scope: §§4.1–4.2, the stable-validation part of §5,
§6 and availability statement. [Original calibration paper](https://doi.org/10.1088/1361-6501/ad16d1).

The Neal et al. publisher abstract describes simultaneous nominal PIV,
higher-dynamic-range PIV and hot-wire measurements. Comparing the latter two
assesses reference precision. This explicitly distinguishes a reference from
an error-free field. Full numerical uncertainty budgets were not audited.
[Publisher abstract, p. 2](https://cms.iopscience.iop.org/alfresco/d/d/workspace/SpacesStore/314579af-15d6-11e6-a415-496188f8a415/J%20MST%200516%20Highlights-A4-2.pdf).

The associated jet dataset has DOI 10.4121/13649885, version 1, an issued date
of 2021-01-29 and CC0 rights in its DataCite record. Its description lists
nominal TIFF images and HDR displacement fields. Metadata bytes are pinned;
individual files, reference budgets and confirmation partitions remain
uninspected. Its use of “exact” is not adopted as a zero-error certificate.
[Depositor-supplied metadata](https://api.datacite.org/dois/10.4121/13649885).

RealPDEBench already covers prediction from experimental and simulated data.
The inspected v2 describes free-stream PIV checks against calibrated bulk flow
and reports a release of selected raw images and calibration files. These
support a concrete next metadata audit, not a certified local wake-error model.
Read scope: introduction, §3.1–3.2, Appendix B and F; no benchmark reproduced.
[Primary preprint](https://arxiv.org/html/2601.01829v2).
Its Controlled Cylinder schema records operating condition, coordinates, time
and velocity fields; pressure is simulation-only. A documented sinusoidal
motion law does not itself establish a released, synchronized actuator trace
and identical hidden state across runs. [Official schema](https://realpdebench.github.io/datasets/controlled-cylinder/).

## Consequence for topic selection

There are usable experimental references and an established real-data benchmark
parent. A generic claim that physical models should be evaluated beyond their
numerical teachers cannot supply Paper G's novelty. Nor does finding a familiar
calibration identity remove the variance–cost contribution blocker.

The retained infrastructure must distinguish measured-value risk, reference
precision, derivative truth and intervention truth. An informative next update
would identify the actual calibration manifest and a target-matched reference
budget, with the observation operator, temporal filtering, spatial support,
run identity and untouched confirmation partition fixed. Both a qualified
reference and a documented capability limit would change permissible evaluation;
neither is automatically a scientific result.

This audit removes zero recorded blockers. It adds no raw question, search
cycle, forecast, machine card, theorem, simulation or experimental result.
Independent same-target replication and a substantive contribution remain open.
The broader experimental-fluid domain remains available to a qualified trigger.

Contract: `research/paper_g/calibration_reference_preflight_20260910.yaml`.
Provenance: `research/paper_g/calibration_reference_source_manifest_20260910.json`.
