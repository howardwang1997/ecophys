# Reaction-stress candidate: resource decision

2026-09-12. Subject: g32_reaction_uq_stress_transfer.

**Decision: park the candidate at F1.** The specified temperature/moisture
comparison remains scientifically unresolved, but a reusable paired
intervention resource has not been qualified. The bounded source review is
finished. This is an allocation decision, not a falsification of the hypothesis,
a completed F2 review, or a finding about the published model's performance.

## What the public interface establishes

The [training entry point](https://raw.githubusercontent.com/Chemlex-AI/bayesian-reactivity-prediction/main/train.py)
loads a workbook and a separate fingerprint array. It derives a binary target
from the workbook's conversion column and uses the selected split column.
The inspected path does not separately load assigned or measured temperature,
moisture, or paired-intervention identifiers into the predictor.

The [data-processing and fingerprint interface](https://raw.githubusercontent.com/Chemlex-AI/bayesian-reactivity-prediction/main/utils.py)
uses the fingerprint array for model inputs and documents reaction SMILES as
the input to the DRFP encoder.
The [inference entry point](https://github.com/Chemlex-AI/bayesian-reactivity-prediction/blob/main/inference.py)
accepts reaction SMILES, constructs fingerprints and obtains feasibility and
uncertainty outputs. It does not expose a separate temperature/moisture argument.
These are interfaces inspected on the moving default branch, not immutable
execution provenance.

This is an interface contract for planning our study, not a scientific failure.
A structure-only score could still correlate with sensitivity across reactions.
Conversely, a predictor with an explicit condition input would not itself
establish the required experimental truth.

The training entry point is not a complete workbook schema: unused columns can
exist. It therefore cannot establish that stress fields are absent from the
underlying workbook. No workbook, fingerprint array, model weights or
prediction payload was inspected or executed.

## Resource qualification after the bounded review

The [wetlab directory listing](https://github.com/Chemlex-AI/bayesian-reactivity-prediction/tree/main/data/wetlab)
lists the Excel workbook. The inspected directory and previously reviewed
README do not provide a stress-assignment field dictionary. Together with
the nominal procedure and release metadata already reviewed, they still do
not establish reaction-level pairing between a declared temperature/moisture
intervention and its nominal control.

The repository has a
[BSD 3-Clause licence](https://raw.githubusercontent.com/Chemlex-AI/bayesian-reactivity-prediction/main/LICENSE).
This resolves the previously unverified repository software licence; it does
not by itself qualify the separately versioned Zenodo dataset's scope of
rights, provenance or stress fields.

The outstanding requirements are:

- Assigned and executed stress values, with units and timing.
- Reaction, recipe, batch and replicate identity linking nominal and perturbed
  measurements.
- A supported analytical endpoint and calibration under the stress protocol.
- A usable release and a confirmation partition designated before outcomes
  are inspected.
- A distinct measurement contribution after the equal-information and
  entropy-component controls recorded in the prior follow-up.

These requirements are specific to our proposed intervention-loss estimand.
They are not criticisms of a release designed for nominal feasibility.

## Why park rather than keep expanding this source chain

Cycle32 and its preceding continuation already retained twelve primary works.
This final check adds only author source-code, licence and directory
documentation, with zero new primary research works. The named public
interfaces do not remove the remaining truth-resource blocker. Further
repetition of the same documentation review has little expected value.

Keep the candidate's scientific question and elementary controls. Resume its
adjudication only when a concrete methods-linked schema or manifest establishes
the named intervention resource, or when a substantive result changes the
contribution assessment. “A larger reaction dataset,” ordinary repeats,
plate-format contrasts, and a new uncertainty method are insufficient without
the matched target.

The broader cross-domain search remains authorized and unfinished. The next
ordinary discovery cycle should sample other unsaturated scientific questions,
prioritizing accessible truth and interventions alongside novelty. No further
approval is needed for that literature-screening scope. This parked question
does not imply that all chemistry, robustness or scientific-ML routes are closed.

## Record

Route status changes from candidate to parked; no terminal date or failure
code is assigned. There is no new cycle, question, forecast, machine card or
experimental run. Paper G counts remain 61 formulations in 16 cycles, with
zero qualified machine cards. The original F1 and pre-F2 records remain
historical.
