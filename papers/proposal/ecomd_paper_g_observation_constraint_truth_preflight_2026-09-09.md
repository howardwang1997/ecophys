# Paper G: observation geometry and experimental constraint truth

PRIVATE / INTERNAL. Bounded truth-asset preflight, started 2026-09-09
11:44:02 UTC. Decision: `partial_capability`, zero removed contribution
blockers. No candidate harvest, new cycle, experiment or public claim.

## Decision and repository connection

Two inspected experimental releases provide actual velocity observations,
including one joint volumetric velocity-temperature release with verified
version and reuse terms. This improves the source map for the repository's
conservative neural-PDE work. It does not yet provide calibrated independent
truth for all derivatives, missing boundary fluxes or intervention responses.

The relevant scientific distinction is whether a constraint belongs to the
full physical state or to the observed representation. A planar restriction
of a three-dimensional incompressible velocity field need not be divergence
free in the plane. Enforcing the latter condition can remove real signal.
This is established physics and projection geometry, with a direct method
parent below; it does not itself supply a new Paper G contribution. Paper D's
affine mass-constraint results do not imply any planar divergence assertion.

## Source capabilities and limits

[Renn, Palmer and Gharib, Scientific Data 13,1123](https://www.nature.com/articles/s41597-026-07368-z),
published 16 May 2026, describes six cylinder-wake regimes and in-plane
velocity sequences. The valid temporal unit is a 100-frame sequence; adjacency
between separate sequences is not guaranteed. Section on three-dimensional
effects explicitly recognizes out-of-plane transport, and the paper does not
assert that the measured plane is a closed two-dimensional flow. Matching
formation time also does not guarantee matching shedding period.

[CaltechDATA record g2z1f-nex65](https://data.caltech.edu/records/g2z1f-nex65)
is version 2, created 6 November 2025. The official API confirms public files
and CC-BY-4.0 data rights, separately from the article's CC-BY-NC-ND-4.0 terms.
Its seven-file manifest lists six HDF5 files and a notebook. Only metadata was
read: none of these files was downloaded or previewed. This is a measured
planar-velocity source, not volumetric derivative or actuator-response truth.

[Toscano et al., arXiv2407.15727v2](https://arxiv.org/html/2407.15727v2),
23 July 2024, sections 2-3.2 and selected 4.1-4.4, describes simultaneous
particle positions, three velocity components and temperature in a finite
Rayleigh-Benard volume. Temperature uses color-to-temperature calibration;
it is not directly supplied by the subsequently fitted flow model. Field
gradients and dissipation are model-inferred, with statistical comparisons
to other regimes. Those comparisons are distinct from simultaneous derivative
reference measurements. This reading is explicitly the preprint version,
not an assumption of identity with its later journal article.

[Dryad dataset 10.5061/dryad.jm63xsjnj](https://datadryad.org/dataset/doi:10.5061/dryad.jm63xsjnj)
supplies a documented `txyz` / `uvwT` schema. The official API identifies
dataset154294, version4, version resource359200, publication and modification
on 16 April 2025, with CC0-1.0 rights. The landing page lists a 53.81 MB MAT
file and a README. Coordinates and fields are nondimensional. These are
useful joint observations, but no independent derivative-error certificate,
new randomized forcing protocol or untouched whole-run partition has been
qualified here. The MAT file was not accessed.

[Shimano, Shiratori and Nagano, Meccanica59,1191-1227](https://link.springer.com/article/10.1007/s11012-024-01771-9),
17 July 2024, introduction and section2.1, is a direct parent for reconstructing
planar velocity while accounting for out-of-plane transport. It explicitly
distinguishes planar divergence from full incompressibility. Its target is
recovery of a missing velocity component using a divergence/vorticity
objective; it is not the identical two-component denoising experiment below.
The broad observation mismatch and generic relaxation remedy are already
occupied. No performance or uniqueness guarantee beyond the inspected scope
is endorsed.

The 2026 TU Delft volumetric-PIV thesis release was inspected only at
institutional description level. A statement that images, 3D velocities and
code exist does not establish a synchronized same-target reference contract.
It remains intake, not a qualified source. These release dates also must not
be presented as new post-closure experimental acquisitions.

## Exact physical control: restriction does not preserve planar divergence

On the periodic cube [0,2*pi]^3, let viscosity nu>0, a(t)=A exp(-2 nu t), and

\[
U(x,y,z,t)=(a\sin x\cos z,\;0,\;-a\cos x\sin z),
\qquad
p=\frac{a^2}{4}(\cos 2x+\cos 2z).
\]

This is a smooth unforced incompressible Navier-Stokes solution with unit
density. Direct substitution gives div U=0, Delta U=-2U,
partial_t U=nu Delta U, and

\[
(U\cdot\nabla)U=(a^2\sin x\cos x,0,a^2\sin z\cos z)=-\nabla p.
\]

Let O retain the first two components on z=0. Then

\[
v=OU=(a\sin x,0),\qquad
\nabla_{xy}\cdot v=a\cos x=-\partial_z U_z\big|_{z=0}.
\]

The missing term is a physical normal derivative. Even a three-component
stereo measurement on this single plane observes U_z=0; it does not measure
partial_z U_z. More components on one plane and a spatial volume provide
different information.

For the periodic L2 orthogonal Helmholtz projectors P3 and P2,

\[
P_3U=U,\qquad P_2OU=0,\qquad OP_3U=OU.
\]

The second equality holds because v is the planar gradient of -a cos x.
The two operations therefore do not commute. With normalized area measure
on the plane, projecting a noiseless observation introduces squared error
a(t)^2/2. The null is a genuinely planar shear
U=(B exp(-nu t) sin y,0,0), which is preserved by P2 after restriction.

These are analytic controls, not fitted networks or a model of either
experimental apparatus. Other spatial boundaries and projection weights
need their own calculation. No claim that a studied model erases an actual
experimental field follows from this periodic example.

## Error tradeoff and required truth

For any orthogonal projector P, Q=I-P, true observed field v and estimate
v_hat=v+e, orthogonality gives the exact identity

\[
\|P\widehat v-v\|^2-\|\widehat v-v\|^2
=\|Qv\|^2-\|Qe\|^2.
\]

It needs neither independent errors nor zero mean. Projection removes the
error component outside the subspace but also removes any true observed
signal there. Improvement and harm are both possible. Estimating these two
terms is a reference problem; the residual norm of a noisy measured field
alone does not separate them.

At a fixed time, one plane can also be observationally identical under two
stipulated explanations: the exact three-dimensional field above measured
without error, or a zero field with measurement error (a sin x,0). Projection
is harmful in the first and helpful in the second. This is the ordinary
unknown-noise decomposition, not a claim that the actual camera has that error
law. A calibrated error model or independent additional measurement can
distinguish the explanations. A generic uncertainty penalty is not automatically
a new method.

For this control, nearby-plane normal-velocity measurements expose the missing
gradient. With planes z=+h and -h,

\[
\frac{U_z(h)-U_z(-h)}{2h}
=-a\cos x\,\frac{\sin h}{h}.
\]

The limit recovers -a cos x. At finite separation the sinc factor is a known
family-specific correction, not an exact derivative for arbitrary flows.
For independent endpoint measurement errors with variance sigma^2, the
central-difference noise variance is sigma^2/(2h^2). Bringing the planes closer
reduces smooth truncation error but can amplify measurement noise. This is
standard differentiation error propagation, not a new cost theorem.

## Bounded preflight contract and next condition

The supported estimands currently stop at measured point/plane values and
within-release reconstruction comparisons under explicit measurement models.
Distinguish those from derivatives, complete-state rollout, total heat balance
and counterfactual actuator responses. Fix coordinate calibration, observation
volume, particle/sequence identity, clock, finite-difference or interpolation
operator, spatial boundary conditions, and physical weights before comparison.

A derivative or projected-risk reference needs an independent measurement
channel or validated calibration/regularity contract with covariance and
resolution accounting. A reconstructed field constrained by the method under
test cannot serve as independent truth for that same constraint. Genuine
three-dimensional measurements are valuable, but this alone does not certify
all derivatives or erase their finite-resolution uncertainty.

No independent same-target replication, complete-state replay, calibration
release or untouched whole-source confirmation partition is qualified. These
are remaining asset questions, not newly discovered empirical failures. The
current five-source audit and the exact controls remove no recorded method
or variance-cost contribution blocker. Existing closed formulations remain
closed; this does not close the entire experimental-fluid domain.

Stop this preflight at partial capability. Re-entry needs an actual blocker-
removing source or theorem and a distinct contribution surviving the known
observation and projection parents. No outcomes, scientific implementation,
simulation or compute were accessed or authorized.

Contract: `research/paper_g/observation_constraint_truth_preflight_20260909.yaml`.
Metadata provenance: `research/paper_g/piv_observation_source_manifest_20260909.json`.
