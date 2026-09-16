# Paper G Cycle41 — learning electronic overlap transport

PRIVATE / INTERNAL. 2026-09-14 NZ. Exploratory decision record, not public scientific evidence.

## Decision and native question

Retain **g41_electronic_overlap_transport** as one provisional F1 simulator-method
candidate. No F2 qualification, full hostile audit, forecast, machine card or execution.
Its potential contribution is economical learning of cross-geometry electronic overlaps
for coherent electron–nuclear propagation, beyond existing phase-free fitting and
diabatic Hamiltonian models. Neither novelty nor a practical cost advantage is established.

Fix a molecule/electronic reference, retained electronic subspace, nuclear domain and
initial wavepacket. Allowed comparisons change the surrogate and its training acquisition
within the same budget, then evaluate held-out initial packets and loops in the declared
domain. Responses are gauge-invariant nuclear density/interference observables and
electronic populations, with geometric loop phase as a diagnostic. Raw coefficients
in different electronic gauges are not directly comparable physical observables.

- H1: learning overlap structure from a limited connected set of reference calculations
  improves coherent predictions per total cost over fitted surfaces/couplings and direct
  interpolation when loop information matters.
- H0: a capable diabatic fit or same-budget overlap interpolation already captures the
  relevant information; any gain is explained by added labels, numerical resolution,
  state-space choice or the propagation method.

Positive value: identify when a learned cross-geometry representation is economical for
coherent molecular prediction. Null value: determine when direct representations suffice
and avoid using pointwise accuracy as a surrogate for coherent accuracy. Neither answer
requires claiming a new geometric-phase effect.

## Three primary anchors

| Work and reading depth | Established contribution | Implication |
|---|---|---|
| [SchNarc, 2020](https://doi.org/10.1021/acs.jpclett.0c00527), indexed primary loss/method excerpts | Phase-less loss minimizes over joint electronic-state sign assignments at each sample; signs within vectors and between coupled states are constrained. Smoothed couplings use a virtual-property derivative construction. | Do not call this an independent sign choice for every state pair, or claim that arbitrary sign correction is new. The control below is not a zero-loss realizability result for this particular architecture. |
| [Gu, local diabatic representation, 2023 v1](https://arxiv.org/html/2304.04369), section II | Cross-geometry electronic overlaps enter the nuclear kinetic matrix and already encode nonadiabatic transitions and geometric phase. The paper explicitly uses band-projected overlap products around loops. | Overlap propagation, gauge covariance and loop diagnostics are direct parents. The candidate must establish a distinct learning/cost result. |
| [DANN, 2022](https://www.nature.com/articles/s41467-022-30999-w), selected indexed representation/loss excerpts | Learns a smooth diabatic Hamiltonian with coupling-related constraints and chemical transfer in an azobenzene family. | Neural Hamiltonians, coupling-informed learning and chemical transfer already exist. This is not an energy-only baseline; its reported surface-hopping task differs from exact coherent wavepacket propagation. |

Three retained primary works at unequal reading depth, not three complete reviews.
SPaiNN and other nonadiabatic work appeared in search intake only; they are follow-up
collision priorities, not a basis for a novelty claim or additional full readings.
No outcome, overlap matrix, model weights or code was accessed.

## C1 — pointwise sign-insensitive information versus a closed loop

This is a hand-constructed smooth two-level control, not a new theorem or molecular result.
Let phi parameterize a circle. Choose nonnegative C-infinity bumps b_A and b_B with
disjoint supports in the first and second semicircles, flat at support boundaries,
and with each integral equal to pi. Define

\[
\alpha_1(\phi)=\int_0^\phi(b_A+b_B)\,ds,
\qquad \alpha_0(\phi)=\int_0^\phi(b_A-b_B)\,ds,
\]
\[
H_j(\phi)=\cos\alpha_j(\phi)\,\sigma_z+
             \sin\alpha_j(\phi)\,\sigma_x .
\]

Both Hamiltonians are single-valued smooth maps on the circle, extend smoothly to an
annulus, and have constant eigenvalues +1 and -1. Their adiabatic energy derivatives
are identical. In a local real eigenbasis the magnitude of the off-diagonal derivative
coupling is |alpha'_j|/2, identical pointwise because the bumps have disjoint support.
Yet alpha_1 increases by 2pi around the loop, while alpha_0 returns to zero. An upper
eigenvector (cos(alpha/2),sin(alpha/2)) returns with sign -1 or +1 respectively: the
single-band geometric phase differs by pi.

Scope matters. These are different Hamiltonians in the same fixed ambient basis and
with the same declared nuclear kinetic operator, not merely relabeled electronic states.
The domain is an annulus, not a claim of identical spectra on a disk containing a crossing.
The construction is C-infinity, not real analytic; a stronger analytic model class can
remove this particular continuum ambiguity. Additional overlap, dipole, diabatic or other
electronic information can also distinguish them. Architectural integrability constraints
may exclude one model. Thus this control neither refutes SchNarc/DANN nor establishes
observed errors in their published tasks. It tests the information in the specified
pointwise sign-insensitive targets under the stated smooth class.

## C2 — truncated overlap blocks need not be unitary

Let a retained electronic state at one geometry be u=e_1 and at another be
v=cos(theta)e_1+sin(theta)e_2, with 0<theta<pi/2. Their overlap is cos(theta), not 1.
Replacing it with its unitary polar factor gives 1 and changes an off-diagonal nuclear
kinetic matrix element from T_01 cos(theta) to T_01. A gauge change preserves the overlap
magnitude and cannot undo that replacement.

More generally, cross-geometry blocks U†V between orthonormal retained frames are
contractions; they are unitary only when the frames span the same subspace. A learned
transport model must distinguish raw overlaps from a unitary parallel-transport factor.
For compatible electronic states in a common Hilbert space, the full collection of
overlaps is a positive-semidefinite Gram matrix with identity diagonal blocks. These are
standard correctness constraints, not an original method or proof that a proposed learner
can efficiently satisfy them. Single-band projected loop products must also be kept
distinct from products of full complete-basis change-of-frame matrices, which can telescope.

## Tentative method and decisive next comparison

An unimplemented possibility is a shared electronic-feature representation for overlap
blocks, with globally compatible Gram structure and gauge handling across geometries.
Any factorization must allow the needed complex phases or local frame charts; demanding
a globally smooth real eigenvector can itself exclude nontrivial line-bundle structure.
Sparse graph-edge fits alone do not establish the full overlap operator required by a
chosen nuclear kinetic discretization. A finite-rank approximation must control omitted
electronic-state and nuclear-basis errors separately from learning error.

The useful test would compare direct overlap interpolation, a competent diabatic fit,
pointwise coupling fitting, and the learned representation using the same reference
information and the same coherent propagator. Include additional-label acquisition as
a separate baseline: richer supervision is not automatically a method contribution.
Evaluate held-out loops and wavepacket initializations, including cases without geometric
interference. Account for quantum chemistry, overlaps, training, interpolation, memory
and propagation costs, at first use and a declared reuse horizon. Independent convergence
in nuclear resolution and retained electronic states is required. Surface-hopping
population agreement alone does not settle this coherent target.

A usable molecular reference with cross-geometry overlaps, permissions, immutable joins,
untouched confirmation and independent replication is unqualified. The mathematical
controls do not substitute for it. Before full review, the cheapest next step is a
bounded comparison of existing learned-overlap/kernel and local-diabatic approximation
methods: require an explicit construction and cost mechanism beyond direct interpolation.
Park if only generic gauge/Gram constraints remain. No full fifteen-work audit before
subject-specific prospective forecasting as required by the protocol.

## Scope and accounting

No exact graph duplicate found for this native electronic-transport target; prior quantum
decoder, isotope-force and crystal-repair formulations have different objects/actions.
No saturated calibration family is reopened. One raw question / one F1-deferred screen;
three primary works / two analytic controls; no F2/F3/card/forecast. This is a one-question
bounded allocation, not a twelve-program cycle. Measurement/intervention sampling targets
are unmet; no broad source-scarcity assertion or filler is used.

After recording: Paper G85 formulations /25 cycles /0cards; detailed32 cycles /169raw;
inclusive41/225; graph329 nodes /279edges /1926locators; evidence1204; candidate1/parked10.
Initial source intake preceded the allocation, which is not a prospective scientific
forecast. No implementation, outcome payload, simulation, training, GPU, laboratory work,
outreach, delegation or publication. Broad ICLR/ICML objective remains incomplete.
