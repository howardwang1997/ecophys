# Paper G: accelerating-tunnel control scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. Previous goal turn: progress. This one-source check
asks whether an accelerating tunnel removes the finite-width gust-control
gap identified in the preceding mechanism audit. No candidate cycle opens.
Repository connection: native interventions for neural-PDE response validation.

## Source and decisive mismatch

[Viola et al., Experiments in Fluids 66, 205 (2025)](https://link.springer.com/article/10.1007/s00348-025-04135-5),
published 25 October 2025, describes an accelerating wind tunnel for untethered
bodies. The abstract and Sections 2.2-2.3 specify spatially uniform,
irrotational transverse gusts and explicitly distinguish them from vortex
and Kuessner-type gusts. Changing the tunnel's acceleration generates a
uniform pressure gradient; the approach targets a different disturbance from
a finite spatial jet that a wing enters and leaves. A free-falling dandelion
example demonstrates its intended application. The paper links data at
DOI10.7488/ds/8031; that item was not opened because the control mismatch
already resolves this preflight. This is an old paper newly inspected here,
not a new release after route closure.

## Standard frame check

Let x'=x-b(t) be a translating, nonrotating frame and let

    u'(x',t) = u(x'+b(t),t) - b_dot(t).

Spatial differentiation gives

    curl_x' u'(x',t) = curl_x u(x'+b(t),t).

The subtracted velocity is spatially uniform, so its curl vanishes. This
holds for smooth fields, and distributionally for idealized shear sheets.
It is standard kinematics, not a new theorem. A change of reference frame
cannot turn an existing gust shear layer into an irrotational gust. The
additional translational inertial acceleration is likewise curl-free.

This identity compares representations of the same flow. It does not prove
that a real accelerating apparatus never generates wall vorticity, that body
motion cannot change the flow, or that all gust responses are invariant under
physically different actuation. Pressure, buoyancy, body dynamics and boundary
conditions still matter when comparing experiments.

## Consequence for the proposed discriminator

The earlier question concerns changing spatial gust width at fixed relevant
conditions to distinguish exit-induced LEV detachment from formation-limited
detachment. An adjustable temporal acceleration history of an irrotational
gust does not establish that control. Similar nominal duration or relative
speed cannot substitute for the missing shear profile and entry/exit process.

Retain the apparatus as a source for uniform-gust free-body response only.
Do not assert a conflict between the papers or extrapolate a width threshold.
No named contribution blocker is removed. Stop this apparatus-to-width-control
mapping; no dataset/schema expansion is justified by this test. Re-entry
requires a source demonstrating the same native disturbance and independently
adjustable width, plus a distinct unresolved discriminator. No data/code/model
payload, experiment, forecast or machine card. The full ICML/NMI/NCS Paper G
objective remains unachieved.
