# Paper G kinetic-selectivity contribution review

PRIVATE / INTERNAL — 2026-09-14. Current disposition: parked, nonterminal. The original Cycle45 candidate record remains historical.

The kinetic-selectivity question remains scientifically meaningful, but the present plan has not identified a contribution beyond comparing representations and stratifying existing mutation-rate predictions. That is the primary reason to stop escalation. Independent measurement support also remains incomplete; this is not a claim that the entire final truth contract must be complete at F1.

Two existing primary works were deepened, and two repository interfaces were inspected. No new primary-work lineage, topic or cycle was added.

| Source | New clarification |
| --- | --- |
| [Agius et al., 2013](https://doi.org/10.1371/journal.pcbi.1003216) | The main text relates affinity to off-rate changes, evaluates mutant subgroups and describes more stringent related-complex validation in Text S3. Nested feature-selection validation is already present. The supplement was not opened; no first subgroup-analysis claim is available. |
| [AIntibody, 2026](https://doi.org/10.1038/s41587-026-03238-6) | Selected SPR/KinExA methods establish that orthogonal measurements target equilibrium affinity and selected designs. They do not independently measure both kinetic rates for every submission. Construct, buffer, fitting, censoring and selection differences must remain explicit. |
| [AbAgKer README](https://github.com/CSUBioGroup/AbAgKer) | Declares complex/sequence identifiers and supervised affinity/auxiliary kinetic fields. It does not establish a complete replicate-resolved joint kinetic uncertainty schema. Loader implementation was not verified. |
| [Xencor source interface](https://github.com/XenInc/Xencor-AIntibody-Challenges/blob/main/code/challenge_3_winning_model_for_publication.py) | Selected source reads characterized heavy/light sequences and applies a scalar regressor. This is a usable baseline interface locator; no CSV, model weights or execution were accessed. |

Repository branches were inspected without immutable revision qualification. These are source-interface findings, not a complete reproducible asset contract or evidence of absent files elsewhere.

R1: accessible prediction is different from information retention

Let eta have zero mean and variance one. A representation z=epsilon*eta is invertible for every epsilon>0. Yet population ridge regression with a fixed positive penalty lambda minimizes

    E[(eta-w*z)^2] + lambda*w^2

at w=epsilon/(epsilon^2+lambda). Its prediction is epsilon^2/(epsilon^2+lambda)*eta, approaching zero as epsilon shrinks despite no loss of information. Standardizing the feature repairs this particular example. The lesson is limited: a probe failure alone cannot prove that affinity pretraining erased kinetic information. A legitimate empirical claim concerns accessible prediction under a declared readout, supervision and compute budget. This is a standard analytic control, not a diagnosis of a published encoder.

R2: equilibrium validation leaves the common rate direction unchecked

Write mutation log-rate changes as a and b, affinity contrast d=b-a and common rate coordinate eta=(a+b)/2. Consider true a=b=0 but fitted mutant-specific errors ahat=bhat=u. Then dhat=0 while etahat=u. A covariance sigma^2*11^T has no variance along the affinity contrast and nonzero variance along the common direction.

An independent equilibrium measurement agreeing with d=0 therefore still cannot validate the apparent kinetic shift. Independent kinetic replicates or a defensible joint fit-error model are needed; shared systematic effects need additional controls. This constructed common-error example does not claim such errors occurred in SPR or in either retained dataset. Parent normalization does not automatically eliminate mutant-specific errors.

What would change the decision

A specific biological mechanism contrast, a concrete method advantage, or a matched kinetic-control asset could make a substantive follow-up possible. The next proposal would need a conclusion that existing mutation-rate prediction and ordinary stratified evaluation do not already supply. It must match information and training budgets across raw and affinity-trained representations, normalize/readout-tune fairly, and distinguish deployment predictors from oracle-affinity diagnostics.

For measurement support, freeze parent/mutant and replicate joins, rate uncertainty/covariance, fitting windows and censoring, construct and assay conditions, selection and confirmation partitions. Do not infer independent kinetic truth from a second equilibrium assay, or prospective confirmation from a historically prospective but now published challenge. No claim is made that suitable data cannot exist.

Decision: park g45 nonterminally. Empirical kinetic benefits remain possible, and a negative result from a carefully designed study might be useful; neither has been established here. No field-wide closure, new family saturation, calibration-transfer re-entry or permission request is created. Continue with another unsaturated native question unless a concrete contribution-changing result arrives.

Counts remain Paper G89/29/0, detailed36/173 and inclusive45/229. Graph333/279 now has1980 locators; evidence1247; candidate0/parked14. Four new source-reading records preserve all prior histories. No F2 qualification, F3 audit, forecast, machine card, outcome payload, scientific implementation, training, simulation, hardware, outreach, delegation or publication. Administrative validation is recorded separately.
