# Paper G: pitching-airfoil response asset

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`; partial capability for a prescribed-motion,
phase-averaged lift response. This source preflight addresses the closed
physical-history impulse route's missing physical-action/response contract.
It does not reopen that route or authorize another saturated-family cycle.
The preceding IMNO scope audit made progress; its source pairing stays closed.

## Released observation contract

[Edinburgh DataShare, DOI10.7488/ds/7677](https://datashare.ed.ac.uk/items/53cdad8c-a843-42cf-8c45-a16a233b3599/full)
identifies item53cdad8c-a843-42cf-8c45-a16a233b3599, handle10283/8715,
available2024-01-30T12:55:40Z. It lists four pitching-case PIV archives and
Lift.zip, plus Readme.txt. This is an old release newly located here.
The full metadata declares CC BY4.0, corroborated by the linked
[end-user licence](https://datashare.ed.ac.uk/server/api/core/bitstreams/21a0b6b8-3e33-4606-9526-50af9653bb5e/content).
No dataset payload was downloaded or inspected.

The [README](https://datashare.ed.ac.uk/server/api/core/bitstreams/020c64c2-1335-466d-8356-6b063602502d/content)
describes PIV position/velocity columns x,y,u,v with a0.006s time step.
Lift files contain normalized phase t/T, angle in degrees, lift in newtons
and one standard deviation in newtons. They are explicitly phase-averaged.
Four kinematic cases cover amplitudes32/64degrees and symmetric/asymmetric
pitching; the dataset metadata specifies reduced frequency0.22. These are
schema statements, not verified array contents or calibrated covariance.

## Primary experimental scope

[Otomo et al., Experiments in Fluids62:6](https://link.springer.com/article/10.1007/s00348-020-03095-2)
was published online2020-12-23 for the2021 volume. Selected Sections2.1-2.4
and the concluding/model-comparison scope were inspected. The apparatus uses
stepper-driven pitch monitored by an encoder and an independent six-axis
load cell. Force acquisition is1kHz; quiescent-air measurements are subtracted,
then the signal is filtered and averaged over six periods. PIV is planar.
The paper compares adapted Theodorsen and thin-airfoil models and already
uses measured vortex information with impulse theory to account for force
generation. The model comparison and generic vortex-force correction are
therefore direct prior work. We do not adopt its numerical performance or
mechanistic conclusions as new Paper G findings.

## Capability decision

| Supported by inspected sources | Still unqualified |
|---|---|
| Prescribed moving-boundary protocol | Arbitrary pulse or closed-loop actuation support |
| Phase-resolved average lift and dispersion columns | Individual-cycle force realizations and temporal covariance |
| Planar velocity sequences | Complete three-dimensional physical state or derivative truth |
| Separate force measurement modality | Same-run force/PIV trigger, clock and cycle pairing |
| Public file inventory and declared licence | Array-level provenance, dimensional reconciliation and untouched replication |

The distinction changes the next action: this is a possible reference for
average periodic response, so instantaneous noise-free force is not a necessary
gate for that estimand. However, an average waveform cannot establish a joint
cycle-level response law. A standard-deviation column does not by itself give
cross-time covariance or uncertainty of every derived response statistic.
These are inference limits of the released summary, not evidence of a scientific
measurement failure. No absence of raw measurements elsewhere is asserted.

Before a matched physical comparison, reconcile the item-to-paper experiment
mapping and record the target observation operator. The current reading does
not resolve geometry/normalization lineage. The private manifest preserves the
separate reported values without treating documentation differences as novelty.

## Stop and next update

No recorded contribution blocker is removed. Stop generic high-amplitude lift,
vortex correction and force-from-PIV topic harvesting from this asset. A next
update needs a distinct quantitative rival pair at the released average-response
estimand, or independently documented cycle/clock/measurement lineage for a
specifically justified new estimand. Do not download Lift.zip or PIV archives
merely to search for an effect. No outreach, participant work, scientific
implementation, outcomes, simulation or GPU work is authorized here.

Formal record, source manifest, graph, re-entry ledger and memory preserve this
partial capability. The ICML-main/NMI/NCS Paper G objective remains unachieved.
