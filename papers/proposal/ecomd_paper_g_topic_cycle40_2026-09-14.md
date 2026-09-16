# Paper G Cycle40 — Learning coupled distortions for crystal repair

PRIVATE / INTERNAL — exploratory decision record, not public research evidence.
2026-09-14 NZ. Authority: `research/discovery/decisions/pi_cross_domain_ml_scope_20260912.yaml`.

## Decision

Retain **g40_learned_mode_coupling_repair** as one provisional F1 candidate in the
simulator-method archetype. No F2 qualification, full hostile audit, forecast, machine
card or scientific execution. The possible contribution is a transferable prior for
anharmonic mode coupling that reduces total crystal-repair cost. Its novelty and benefit
are unresolved; automated repair, coupled soft-mode search and learned atomic optimization
already have direct parents. This is not yet an ICLR/ICML-ready proposal.

## Native question and rivals

Start with a periodic crystal at fixed composition, a declared energy reference and
an initial dynamically unstable structure. Allow mode distortions, full-coordinate
relaxation and declared cell changes within a common commensurate-supercell and atom
budget. The response is cost to reach a lower-energy structure satisfying a declared
0 K dynamical-stability check, plus the success–cost curve over held-out structures.
Energy comparisons across cell sizes use the same per-formula-unit normalization.

- H1: chemistry- and geometry-conditioned anharmonic coupling has transferable structure;
  a learned prior selects useful combined distortions using fewer total evaluations.
- H0: on-demand probing/local fitting, genetic search or generic learned optimization
  removes the benefit, or the initial unstable subspace loses relevance along repair.

A positive answer would identify when a physically structured learned search prior pays
for itself across chemical/prototype families. A null answer would delimit when online
probing or established search is more economical. Neither outcome establishes a new
physical effect or a universal lower bound on crystal search.

The original intake concerned stability versus synthesizability. The screened question
is narrower: 0 K optimization. It makes no claim about actual synthesis, finite-temperature
free energies, equilibrium sampling, transition rates or finding a global minimum.

## Three primary anchors, bounded reading

| Work | What it establishes for this screen | Consequence |
|---|---|---|
| [PhononBench, v1](https://arxiv.org/html/2512.21227v1) | Evaluates generated crystals using MatterSim-based phonon calculations. Selected overview/evaluation/property-conditioned sections read. | Supplies task context, not independent DFT truth for every structure or experimental synthesis labels. |
| [VibroML, v1](https://arxiv.org/html/2604.27685v1) | Already provides single-mode and coupled-mode following, genetic search, random displacements, relaxation and phonon rechecking. Selected introduction and core remediation methods read. | Automatic repair and adding coupled distortions are occupied contributions; GA is a required comparator. |
| [Learn2Hop, ICML 2021](https://proceedings.mlr.press/v139/merchant21a.html) | Learns atomic optimizers that hop across rough energy landscapes. Selected methods/feature table include geometric neighborhood information as well as optimizer state. | Learning atomic search or adding chemical/geometry features alone is insufficient. Its exact task differs from periodic phonon-stable repair. |

These are three retained works, not three complete reviews. No outcome payload or model
was accessed. Search-intake mentions of crystal RL/MCTS remain follow-up priorities,
not reviewed evidence. No absence-of-prior-art conclusion follows from this bounded set.

## Two exact controls

These are hand-derived standard polynomial controls, not new theorems or crystal observations.
For gamma > -1, consider

\[
V_\gamma(x,y)=-\tfrac12(x^2+y^2)+\tfrac14(x^4+y^4)
                 +\tfrac\gamma2 x^2y^2.
\]

**C1 — identical harmonic instability, different stable directions.** At the origin,
the Hessian is -I for every gamma. Axis stationary points (±1,0) and (0,±1) have
energy -1/4 and Hessian eigenvalues 2 and gamma-1. Mixed stationary points satisfy
x²=y²=1/(1+gamma), have energy -1/[2(1+gamma)], and Hessian eigenvalues
2 and 2(1-gamma)/(1+gamma). Thus gamma=0 has stable mixed points and saddle axes;
gamma=2 has stable axes and saddle mixed points. Harmonic information alone does not
determine which combination reaches a stable point. This is an information statement
about this family, not a limitation on models also given geometry or force probes.

**C2 — one cheap probe defeats the toy ML story.** In this normalized family,
V_gamma(1,1)=(gamma-1)/2, so one off-axis energy query identifies gamma exactly.
Consequently C1 supplies no evidence that learning is economical. A serious method must
beat an on-demand low-order fit using the same available observations. Learning cannot
win by depriving its comparator of probes, chemistry, geometry or history.

## Tentative method and decisive comparison

One unimplemented hypothesis is a learned low-order or low-rank anharmonic energy model
on the unstable subspace, conditioned on local structure and a limited set of force probes.
It would choose a distortion, permit full relaxation and recompute the subspace. Mode
sign, order and rotations within degenerate eigenspaces must leave real-space proposals
consistent: basis covariance is a correctness requirement, not the claimed contribution.
Cubic terms, changing stable modes, cell strain and nonlocal pathways may defeat a local
quartic restriction. Combining wavevectors requires a common admissible supercell; the
learner receives no larger structural search space than its comparators.

The decisive result would be held-out chemical/prototype-family repair curves at equal
total cost against single-mode following, coupled-mode enumeration, GA, random search,
on-demand polynomial fitting and a capable learned atomic optimizer. Count energy/force
queries, relaxations, phonon/Hessian construction, setup, training and tuning; report both
query counts and wall time, separately for first use and a declared amortization horizon.
Existing MLIPs already make energy queries cheap, so replacing queries with another model
must justify its own cost. Compare at matched success and energy/stability targets.

Final validation needs a declared independent reference and q-point/supercell support.
A sampled phonon path alone is not a theorem of stability throughout the Brillouin zone.
Surrogate screening and independent confirmation must retain separate labels. Future
splits must prevent structure/prototype leakage and preserve untouched confirmation;
data rights, joins, replication and execution costs remain unqualified at F1.

## Scope, accounting and next decisive step

This differs from g34 isotope spectral inference and phonon uncertainty questions in
target and action: choosing structural distortions, not calibrating a response estimator.
It differs from g38 KA sampling because the target is optimization, not an equilibrium
measure. No saturated calibration-transfer family is reopened.

One raw question, one quick screen, one F1-deferred survivor; zero F2/F3/cards/forecasts.
Three primary works and two analytic controls. This bounded source-led allocation is not
a twelve-program cycle; measurement/intervention sampling targets are unmet. No broad
source-scarcity claim or filler questions are used.

Next: a bounded exact-method comparison of crystal RL/MCTS and the existing remediation
parents, focused on whether learned mode coupling supplies a specific contribution beyond
local fitting and generic learned optimization. Stop or park if it remains only a feature
substitution with no defensible cost mechanism. Do not expand into a full review before
that distinction is concrete. No implementation, outcomes, simulations, training, GPU,
laboratory work, outreach, delegation or publication is authorized by this record.

Cumulative after recording: Paper G 84 formulations / 24 cycles / 0 cards; detailed ledger
31 cycles / 168 raw questions; historical-inclusive ledger 40 / 224. Graph 328 nodes,
279 edges, 1912 locators; evidence registry 1193. One candidate and nine parked routes
across the graph; existing active verification-liquidity protocol remains separate.
