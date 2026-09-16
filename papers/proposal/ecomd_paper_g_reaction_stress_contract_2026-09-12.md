# Reaction uncertainty and stress transfer: source-contract follow-up

2026-09-12. Subject: g32_reaction_uq_stress_transfer.

**Decision: retain the F1 question, with lower priority and a narrower attribution
claim; do not advance to F2 completion, F3 or experimental execution.** This
bounded follow-up resolves two comparison requirements and pins the available
release. It does not establish a new method, a model failure or publication
readiness. No new question or search cycle is counted.

## The nominal-score comparison has an exact redundancy

For the Bayesian binary classifier, let \(p_w(x)\) be its probability of
feasibility at weights \(w\), \(\bar p(x)=E_w p_w(x)\), and \(h\) binary entropy.
The decomposition used in [Zhong et al.,
equations 5–6](https://www.nature.com/articles/s41467-025-59812-0) is

\[
U_a(x)=E_w h(p_w(x)),\qquad
U_e(x)=h(\bar p(x))-U_a(x).
\]

Consequently, at fixed predictive probability, \(U_a\) and \(U_e\) are invertible
transforms of each other. In particular,

\[
\sigma(\bar p,U_a)=\sigma(\bar p,U_e).
\]

Any prediction using one pair can be represented using the other pair. Once
both \(\bar p\) and \(U_e\) are supplied, \(U_a\) adds no information. At fixed
absolute probability margin the entropy is also fixed, so merely matching
that margin does not separate the two components.

This is an elementary consequence of the definition, not a new theorem.
It applies to consistently computed components of the same predictive
distribution. It does not equate different trained models or imply that a
finite restricted regressor will learn the transformation equally efficiently.
Matching a hard class label alone is insufficient.

**Implication for the retained question.** A stress-prediction improvement
from adding aleatoric uncertainty to a probability-only baseline may be
useful, but it cannot uniquely support an intrinsic-chemical-sensitivity
interpretation. The comparison must include the equivalent
probability-plus-epistemic representation. Better finite-model performance
would need to be described as a representation or estimation effect.
The original empirical question remains open; the redundant feature cannot
be sold as an independent source of information.

The previous equal-nominal-distribution/different-directional-loss control
still applies. Neither control proves actual stress-transfer failure.

## The published uncertainty score uses repeat information during training

The [supplement, sections 2.1.7–2.1.8 and
2.2.15](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-59812-0/MediaObjects/41467_2025_59812_MOESM1_ESM.pdf)
states that 486 reactions were repeated two or three times and added to the
training set before uncertainty ranking of a separate test set. Its subsequent
75-reaction validation is therefore not the sole use of repeats. The general
reaction procedure specifies 30 minutes at 30 degrees; the analytical endpoint
is a chromatographic conversion proxy rather than isolated yield. The inspected
sections do not establish an assigned temperature/moisture stress ladder.

The resulting comparison requirement is ours: charge all training repeats to
the nominal model's information budget. A replicate-based comparator must
receive the same available labels, identities and assay information. This
does not allege leakage in the published study.

## Release and truth contract

The article's original
[Zenodo v1](https://zenodo.org/records/12920294) now links to
[v3, record 17596563](https://zenodo.org/records/17596563), dated November 2025.
Both list an Excel workbook; the v3 listing gives MD5
a6812ee4be7157bbc1163a5585c65c73. These are release metadata, not a newly
available 2026 stress dataset. No workbook contents were accessed.
File-specific reuse rights were not established by the rendered metadata.

The [author README](https://github.com/Chemlex-AI/bayesian-reactivity-prediction)
documents reaction splits and output columns for conversion, feasibility and
uncertainty. It does not supply the paired stress-assignment schema required
here. Absence from this documentation is not proof that the workbook or
authors' records lack the fields.

| Required element | What is established | Remaining qualification |
|---|---|---|
| Nominal reaction/assay protocol | Published methods and repeat-augmented training | Joinable reaction, replicate and batch identifiers |
| Temperature/moisture intervention | Apparatus has controllable settings | Assigned and executed stress values, timing, nominal pairing |
| Physical response | Published chromatographic conversion proxy | Stress-dependent assay calibration; isolated yield cannot be inferred |
| Uncertainty representation | Explicit entropy decomposition | Information-matched probability/epistemic comparator |
| Reuse and provenance | Versioned workbook listing | File-specific rights and field dictionary |
| Confirmation | No payload inspected in this work | Reserve eligible reactions/stresses before outcomes are accessed |

Paper-level apparatus capability, a general procedure and a workbook listing
do not jointly establish an intervention dataset.

## Two adjacent primary works delimit novelty and transfer

[Collins and Glorius (2013)](https://www.nature.com/articles/nchem.1669)
already propose a robustness screen beyond idealized reaction conditions.
The inspected primary abstract establishes the screening parent; it does not
qualify the exact temperature/moisture dataset or answer the present ML
uncertainty question. Generic reaction robustness testing is not new.

[Neves et al. (2026)](https://www.nature.com/articles/s43588-026-01017-6)
address Buchwald–Hartwig prediction across chemical space. Their methods report
384 reactions compared between 96- and 384-well formats, across six substrate
pairs and 64 conditions, and describe CAD calibration. This supplies a concrete
adjacent comparison. Plate format, reaction class and analytical measurement
differ from the frozen acid–amine temperature/moisture target. A format effect
cannot be reinterpreted as isolated thermal or moisture sensitivity. The
paper's OOD result is also not a contradictory prediction for that target.

## What would justify further investment

The viable result, if obtainable, is an empirically calibrated statement about
when a **nominal-information model** predicts declared stress loss and when
stress-labelled calibration provides additional decision value at a stated
cost. Such a result must survive reaction-family transfer, assay controls,
the entropy redundancy above and comparison with
[input-aware BO](https://proceedings.mlr.press/v89/oliveira19a.html).
It would need a contribution beyond a single-study critique to justify
ICLR/ICML main.

The immediate resource task is now specific: obtain a public field dictionary
or methods-linked manifest establishing temperature/moisture assignments and
paired nominal outcomes, with a reusable assay endpoint. Do not inspect the
workbook simply to discover whether it contains suitable outcomes. If the
resource supports only repeats or plate-format comparison, keep it as an
adjacent asset and defer this target; do not silently change the intervention.

This follow-up retains two new primary works, bringing Cycle32 and its
continuation to twelve. The supplement is an expanded reading of an existing
work; release metadata and the README are not additional research works.
Only four primary works are in this candidate's retained neighborhood, so this
is explicitly a pre-F2 contract review, not the runbook's completed six-work
F2 review. Broader literature collection and scientific execution have not
been performed. The F1 screen and its original counts remain historical.
