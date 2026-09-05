# EcoMD known-gain oscillator truth-asset composability audit

**Date:** 2026-09-05  
**Work type:** truth/control-asset trigger audit; not candidate harvesting  
**Parent:** known-gain weak-design singularity follow-up  
**Decision:** `partial_capability`  
**Dataset outcomes, implementation, outreach, SSH, and GPU status:** not authorized

## 1. Exact question

The Causal Chamber preflight found a programmable real feedback plant but no released relative-gain
experiment or signed numerical coupling truth. A second source scan found three physical oscillator
families that appear complementary:

- a 28-node electronic Rössler network with known structures and 101 global coupling levels;
- a three-node electronic simplicial complex with a two-dimensional grid of linear and nonlinear
  coupling strengths; and
- a programmable electrical Ising network with positive and negative pair couplings.

The hostile question is whether one of them, or their combination, supplies the missing truth asset
for the frozen known-column-gain estimand. The answer is no. Each system has a useful controlled
quantity, but the quantities live in different parameter spaces. Missing dimensions of one truth
contract cannot be borrowed from a different system with a different intervention and target.

No data archive or observation table was downloaded. This audit used only primary-paper and public
repository metadata.

## 2. Frozen discriminator

At zero feedback, write (G=KU) for a perturbation direction. Under a common gain
(D_\gamma=sI+E), the first-order precision signal for a (K)-circulatory direction is

\[
 [E,G]_{ij}=(E_{ii}-E_{jj})G_{ij}.
\]

Therefore a physical validation of the orientation result needs all three properties in the same
apparatus and same response law:

1. a nonzero (K)-circulatory or otherwise signed directed component to recover;
2. independently varied node/channel gains so that (E_{ii}-E_{jj}) changes; and
3. a quantitative, externally known target plus complete observations under a justified bridge to
   the output-only equilibrium precision model.

A global scalar coupling gives (E=0). A symmetric reciprocal coupling has no circulatory target.
Two gains multiplying different physical interaction bases are not diagonal gains multiplying
different columns. These are algebraic mismatches, not matters of dataset size or estimator choice.

## 3. Asset-by-asset audit

### 3.1 Twenty 28-node Rössler networks

[Vera-Ávila et al.](https://doi.org/10.1016/j.dib.2019.105012) release measurements from 28
electronic Rössler circuits under 20 network configurations. For every configuration, the experiment
records 30,000 time points at 101 values of one coupling strength (kappa\in[0,1]), with three
repetitions; the topology files are supplied. Digital potentiometers change the coupling for all
circuits in common steps.

This is a strong public physical benchmark, but under the closest map to the known-gain model it has

\[
 D_\gamma=\kappa I,
 \qquad [D_\gamma,G]=0
\]

for every circulatory direction. One hundred and one values on that scalar ray do not create relative
gain information. Its target is network link structure under nonlinear chaotic diffusive dynamics,
not a signed directed matrix in an output-only Gaussian equilibrium law. Moreover, generic topology
reconstruction on this exact experimental dataset is already demonstrated by
[Singhal et al.](https://doi.org/10.1016/j.ifacol.2023.10.879), so applying another neural or
physics-informed estimator to it is not an unoccupied contribution.

**Verdict:** useful future co-trending/abstention negative control; failed as positive orientation
truth.

### 3.2 Three-node physical simplicial complex

[Vera-Ávila et al.](https://doi.org/10.1016/j.dib.2024.111145) release four experimental scenarios
for three Rössler-like circuits. In every scenario, pairwise linear strength and nonlinear
higher-order strength are each varied over 100 values, giving 10,000 time series of 30,000 points.
The archives are publicly referenced on Zenodo.

This source has a genuine two-dimensional control grid, but its dynamics have the schematic form

\[
 \dot x=f(x)+\kappa_{\mathrm{lin}}B_{\mathrm{lin}}(x)
              +\kappa_{\mathrm{high}}B_{\mathrm{high}}(x).
\]

The two coordinates multiply different interaction orders and, across scenarios, different measured
state variables. They do not independently scale node columns of one invariant (\Phi). Recasting
((\kappa_{\mathrm{lin}},\kappa_{\mathrm{high}})) as two entries of (gamma) would silently replace
the estimand after asset discovery. A general known-operator-modulation theorem could encompass this
system, but that theorem has not been stated, distinguished from LPV/bilinear identification, or
proved.

**Verdict:** useful future off-estimand/specification negative control; failed as a same-action gain
system.

### 3.3 Programmable subharmonic-resonator Ising network

[English et al.](https://www.nature.com/articles/s42005-022-01111-x) build a physical network of
driven nonlinear RLC oscillators. A switch matrix can independently choose whether a pair is
uncoupled, positively coupled, or negatively coupled, and the voltage traces are synchronized. This
is unusually strong signed edge truth.

The same paper states that individual connected pairs cannot have different coupling strengths.
The resistor construction is reciprocal and represents a symmetric Ising matrix, whereas the
known-gain singularity concerns orientation of a (K)-circulatory component. Its driven nonlinear
transient is not the frozen equilibrium law, experimental mismatches are only qualitatively captured
by the model, and both datasets and simulation code are available only by author request.

**Verdict:** useful future reciprocity negative control; failed as a relative-gain circulation truth
asset, and not a public reusable dataset without outreach.

## 4. Why the three partial assets do not compose

| Required property | Rössler network | Simplicial complex | Ising resonators |
|---|---:|---:|---:|
| Public physical observations | yes | yes | no; author request |
| More than one numerical control direction | no; global (kappa) | yes; mechanism-type strengths | topology/sign choices, not strength directions |
| Diagonal node/channel gain action | no | no | no |
| Signed directed/circulatory truth | no | no | no; signed but reciprocal |
| Same output-only equilibrium precision law | no | no | no |

Validation evidence is not a checklist whose cells may be filled by unrelated systems. To establish
the (n^{-1/4}) transition, the same target must experience the design transition while all other
mechanisms stay within the declared model. Pooling global-gain data from one apparatus, a
two-mechanism grid from another, and symmetric sign truth from a third would never observe the
commutator that drives the theorem.

The combination does suggest three valuable falsifiers if the route is activated later:

1. a method should abstain from orienting circulation on the global-(kappa) Rössler data;
2. it should report zero circulatory component on reciprocal Ising couplings; and
3. it should reject or flag the simplicial data when a mechanism-type intervention is falsely encoded
   as a node gain.

Those are null controls, not evidence that the estimator recovers a nonzero signed component.

## 5. Novelty consequence

The scan also kills an easy pivot. “Infer physical interaction networks from coupling sweeps” is
already an established problem, and the Rössler benchmark has already been used for data-efficient
network inference. A broader model

\[
 R_e=(I-\Phi M_e)^{-1}\varepsilon_e
\]

with known general modulation operators (M_e) could be mathematically interesting, but it is a new
subject rather than a free generalization. Before re-entry it would need:

- an exact observation model covering dynamic nonlinear systems without relabelling their controls;
- necessary and sufficient identification conditions for the operator family ({M_e});
- a singular-information theorem not reduced to standard LPV, bilinear, network-inference, or weak-ID
  machinery; and
- at least one physical system where the same operator family varies and the signed target is known.

The current oscillator assets do not supply that package.

## 6. Decision

**Decision:** `partial_capability`, with zero removed blockers. The public Rössler and simplicial
datasets are valuable physical controls, and the Ising device supplies signed reciprocal topology,
but none implements the frozen gain action or target. Their complementary strengths cannot be
combined into same-estimand evidence.

Do not download their observations, implement an estimator, request Ising data, or allocate the A800
or V100 workers. Re-audit only if a source releases independently varied per-node or per-channel gains
on a system with externally known nonreciprocal signed coupling, complete state/lifecycle metadata,
and a defensible reduction to the frozen output law. A larger global coupling sweep, another
synchronization metric, a two-mechanism grid, or programmable symmetric signs is not a trigger.
