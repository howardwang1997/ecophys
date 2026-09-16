# Paper G: transverse-gust observation capability

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. Repository connection: neural-PDE physical-response
validation. This is a bounded truth-asset preflight after the VFM audit, not
a new candidate cycle. Previous goal turn: progress, completing registration.

## Primary scope

[Towne et al., AIAA Journal 61, 2867-2892 (2023)](https://doi.org/10.2514/1.J062203),
selected Section VI, describes Maryland towing-tank gust experiments at
Re=20,000, zero incidence and four gust ratios (0.5, 0.75, 1, 1.5).
The released description retains eight individual PIV runs and five
individual filtered force runs, plus their averages. Section VI.B.2 explicitly
states that force realizations are separate from PIV realizations. PIV uses
a glass wing; force acquisition uses an aluminium wing of matching dimensions.
Force acquisition is at 1 kHz with a 5 Hz low-pass filter. Gust strength can
vary independently of Reynolds number. The section already compares measured
lift with classical gust-response models and discusses leading-edge vortices.
These are published capabilities and prior work, not new Paper G results.

[Deep Blue collection metadata](https://deepblue.lib.umich.edu/data/collections/kk91fk98z)
lists the gust dataset with a 2022-06-12 creation date. This is an old asset
newly located in this audit, not a release after the route closure. Only indexed
official metadata was available here; item-specific DOI, current release,
README schema, byte inventory and reuse licence remain unqualified.

[Community challenge, arXiv:2601.06183v1](https://arxiv.org/html/2601.06183v1),
selected introduction, Table 1 and Section 5, already specifies classical/ML
baselines and withheld-target evaluation for compression, forecasting and
sensing. Its listed pitching task uses DNS; it is not a paired physical-gust
confirmation source. This establishes a parent for generic benchmark framing,
not a proof that every possible benchmark contribution is exhausted.

## Supported and unsupported questions

The source supports a potential family of filtered total-force response
distributions under specified gust conditions, and a separate family of
flowfield distributions. A mean-response target does not require simultaneous
acquisition. The individual PIV runs could also support within-flow ensemble
statistics after alignment and coverage are qualified.

However, separate ensembles do not determine the joint distribution of force
and the flow in the same encounter. Matching a run number or normalized time
cannot manufacture this correspondence. Inferring a joint response requires
additional assumptions or joint measurements. This is an identification
boundary, not an observed failure of a trained surrogate or a new theorem.

The native control is gust strength at fixed towing conditions. The inspected
release does not qualify arbitrary gust histories, randomized feedback actions,
full initial-state replay, or independent validation of force-map components.
Separate instrumentation is not automatically independent replication of a
fixed scientific claim. A new observation domain also does not remove the
existing off-support-extension and direct-prior contribution blockers.

## Decision and stop rule

Retain partial marginal-response capability. Do not treat this archive as
paired force/PIV truth, reopen generic history-response modelling, or collect
more analogous archives without a distinct discriminator. Re-entry requires
a same-state/action/response rival or a new asset removing a named blocker.
Freeze rights, calibration, alignment, whole-run confirmation and replication
before any future data action. No HDF5/ZIP, source code, model or outcome payload
was accessed; no scientific execution or outreach. No forecast or machine card.
The full ICML/NMI/NCS Paper G objective remains unachieved.
