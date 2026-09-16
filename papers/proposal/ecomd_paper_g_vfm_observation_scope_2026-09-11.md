# Paper G: vortex-force observation and averaging scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. This bounded source comparison follows the pitching
asset preflight; it is not force-from-PIV candidate harvesting. The repository
connection is neural-PDE response validation. The previous goal turn made
progress by qualifying a prescribed-motion average-response asset.

## Primary evidence

[Otomo et al., Experiments in Fluids66:64,2025](https://link.springer.com/article/10.1007/s00348-025-03962-w):
selected Sections2.1,3.2,4.2 and5. The snapshot method combines a velocity-vorticity
integral with an added-mass force requiring body geometry and acceleration.
Its experimental approximation omits viscous pressure and skin friction;
an ellipse formula supplies added mass. The geometry-dependent force weight
comes from auxiliary Laplace potentials. Thus "snapshot" does not mean a
velocity image is the entire input. Cases2/3 reuse the earlier NACA0018
pitching experiments and cite DOI10.7488/ds/7677; they are not new independent
replication of that archive. The paper already discusses finite windows and
near-surface optical coverage. No source performance is adopted as a new
Paper G result. The2024 preprint is not a second lineage; the2025 version of
record governs this reading.

[Liguori et al., arXiv:2603.13078v1](https://arxiv.org/html/2603.13078v1):
selected Sections2.1-2.2 and conclusion. This work derives a mean-force form
from incompressible RANS with a Reynolds-stress contribution and uses a
Boussinesq eddy-viscosity model. Its assessment uses URANS mean fields for a
gliding bird and GOE803 section, including external comparisons of CFD with
experimental reference data. Reconstructing forces from those mean fields
against CFD force curves is not an independently measured stress-component
truth. Gliding has zero added-mass term in the stated application. That
stationary-geometry mean target is not automatically the phase-conditioned
moving-wing target. No matched contradiction with the2025 snapshot method
or new physical confirmation is established.

## Elementary averaging check

For a fixed motion phase, suppose every realization is mapped to the same
coordinates and domain, and the geometry weight Lambda is deterministic.
Assume sufficient integrability to interchange the spatial integral and
conditional expectation. For the vortex integral alone, write

    V(u,omega) = rho * integral Lambda dot (u * omega).

Decompose u=mean(u)+u' and omega=mean(omega)+omega', with means conditional
on that phase. Expansion gives

    mean(V) - V(mean(u),mean(omega))
        = rho * integral Lambda dot mean(u' * omega').

The two mixed terms vanish by the definition of the conditional means.
The correction vanishes when its weighted integral is zero; the fluctuations
need not vanish pointwise. This is standard conditional bilinear averaging,
not a new theorem, closure model or measured effect. It does not establish
the sign or size of a correction in the archive. If geometry, phase alignment
or the domain varies across realizations, the fixed-weight identity is
insufficient and those variables must remain inside the averaging operation.

## What the physical asset can decide

The existing average lift waveform can compare total-force predictions under
its prescribed motion. It cannot, by itself, independently validate each
spatial vortex contribution or separate modelled stress, added mass and
unobserved-region effects. A conventionally defined force decomposition may
be mathematically useful without being individually measured. No claim that
such decomposition is always nonunique, or that total-force validation is
worthless, follows from this scope distinction.

The new source relationship makes the next step narrower: qualify the exact
averaging/kinematics contract and an independently discriminating observable
before any component-attribution claim. A new method paper reusing the same
pitch archive does not fill the independent-confirmation gap. The mean-force
capability retained in the previous preflight remains intact.

## Stop rule

Stop generic snapshot-force, Reynolds-correction and force-map-attribution
variants from these sources. These methods and the covariance identity have
direct parents. No contribution blocker is removed. Further re-entry needs
opposed predictions for the same body motion, observed state, averaging
operator and target, or a genuinely new truth asset removing a named blocker.
No new archive, code, model, PDF, outcomes, simulation or hardware was accessed.
No candidate, forecast, machine card or execution authority follows. The
full Paper G publication objective remains unachieved.
