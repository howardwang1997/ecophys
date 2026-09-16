# Paper G rheology kinematic-coverage intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

Stop after two selected primary works, before exhausting the four-work allocation. Generic shear-to-extension learning, its invariant excitation limitation, and adding extensional observations already have direct parents. No distinct raw question formed. This is unrelated to reopening the older constitutive quadrature/integrability formulation.

[Cummings et al. (2026), v1](https://arxiv.org/html/2607.14944v1) explicitly discuss vanishing/dependent invariants in planar training, then use a reduced tensor basis for hybrid constitutive learning. Their synthetic tests include 2D and 3D CFD; additional first normal stress difference improves some predictions. The paper acknowledges limited extrapolation and proposes additional flow protocols. A general counterexample does not refute those reported within-class results. Selected main theory and validation-scope sections were reviewed, without solver reproduction.

[Shanbhag and Erlebacher (2024), v1](https://arxiv.org/html/2408.10762v1) already distinguish shear-only stress observation from observing normal stress differences, formulate sparse constitutive discovery, and test extension. Section V.1 explicitly states that even complete stress observation during shear does not activate all invariant directions; it recommends combining shear and extension measurements. Thus neither the generic impossibility warning nor that experimental remedy is a fresh contribution. Selected main methods, extension results and design discussion were read; full supplement and journal-version parity were not audited.

A standard exact control makes the coverage distinction concrete. Let D be the symmetric rate-of-deformation tensor in 3D incompressible flow. Add a parallel stress channel to a fixed objective base law:

Delta_tau = 2 eta a [det(D)/r_star^3]^2 D,

where eta>0 is a viscosity, a>=0 is dimensionless and r_star>0 has units of inverse time. This channel is symmetric, objective and trace-free. Its mechanical dissipation is

Delta_tau:D = 2 eta a [det(D)/r_star^3]^2 tr(D^2) >= 0.

For every embedded planar incompressible flow, the eigenvalues of D are (d,-d,0). The added stress therefore vanishes throughout any such deformation history, regardless of the number of shear or normal-stress observations. Rotating the experiment preserves the determinant and cannot excite this channel. This does not assume that all stress components of a viscoelastic base are planar.

For a uniaxial extension with D=diag(-e/2,-e/2,e), det(D)=e^3/4. The additional extensional viscosity, defined by (tau_zz-tau_xx)/e, is 3 eta a e^6/(16 r_star^6). A nonzero extension rate distinguishes different a values if the base is known. A single measurement identifies only this one unknown coefficient; it does not identify a general constitutive law.

This is an elementary invariant construction, not a new physical mechanism, full thermodynamic/CFD stability proof, empirical failure of a trained model, or ML contribution. Its role is to prevent incomplete observation and incomplete excitation from being confused. Planar extension and uniaxial extension are not interchangeable in this control.

No final-stage truth contract was imposed at intake. Stop the generic source chain because of direct prior coverage, without closing rheology. A future program needs a material-specific mechanism/control contrast and useful learning gain beyond the sparse/hybrid parents. Do not use the remaining citation budget simply to accumulate more papers.

Two retained primaries, one standard control; no new raw question, cycle, route status, F2/F3, forecast or card. Paper G89/29/0; graph333/279/1986; evidence1315. Published results are development evidence. No scientific implementation, outcomes/model payload, simulation, training, hardware, outreach or delegation. The ICLR/ICML objective remains incomplete.
