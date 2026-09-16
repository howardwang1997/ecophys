# Paper G: force-error, thermostat and observable attribution preflight

PRIVATE / INTERNAL — 2026-09-10, session started 03:07 Pacific/Auckland.
Public evidence eligible: false. Paper-only source and control-asset audit;
no new topic cycle, candidate harvesting, experiment or activation.

## Decision and repository connection

The apparent primary-paper disagreement does **not** qualify as a matched
contradiction. The useful advance is a concrete attribution contract and
analytic controls: changing the thermostat can change sampling, and correct
separate position and velocity marginals do not imply correct phase-space
correlations or physical dynamics. These are standard consequences, not a new
ML theorem or empirical discovery.

The repository's conservation/learned-dynamics question supplies the scientific
connection. Its original D-3 contract already asks for mechanisms under matched
fidelity; keyword overlap alone must not terminate that deeper question.
See [the original question contract](ecomd_question_contract_constraint_inductive_bias_2026-08-27.md).
Existing Paper D runs/results are not Paper G evidence or authority.

For bookkeeping, this control asset is attached to
`slow_memory_random_batch_invariant_correction`, whose recorded blockers include
`force_variance_artificial_heating_correction_direct_prior` and
`uniform_slow_memory_correction_or_bound_absent`. The attachment tests the
boundary of its thermostat analogy. Deterministic positional force error is
not automatically the zero-mean random-batch noise considered there. Nothing
here removes either blocker, reopens that market route, extends implementation
scope, or changes the neural-PDE protocol. Disposition: `partial_capability`;
candidate harvest false; original Paper G goal remains unachieved.

## Selected primary evidence and exact reading scope

1. **Hinz, Karasiev, Hu and Mihaylov, PR Materials 7, 083801 (2023)**,
   [DOI](https://doi.org/10.1103/PhysRevMaterials.7.083801).
   Selected accepted main text and OSTI manuscript/supplement read. The object
   is warm dense hydrogen with an orbital-free to Kohn–Sham force correction.
   The stated OFMD setup uses an Andersen thermostat. Main-text discussion
   suggests a thermostat can make non-conservation inconsequential, then
   expressly reserves the energy-distribution/specific-heat question.
   Supplement IV assesses local force derivatives and a thermostat-off work
   diagnostic. Equation 23 accumulates force–velocity work; for a
   non-conservative field this alone is not an independent state-energy oracle.
   This is an observable distinction, not an implementation allegation.
   The named kernel and observables differ from the water comparisons below.

2. **Bigi, Langer and Ceriotti, ICML 2025**,
   [proceedings metadata](https://proceedings.mlr.press/v267/bigi25a.html),
   [arXiv v6 selected Sections 3.1, 4.5–4.6, G.5–G.6](https://arxiv.org/html/2412.11569v6).
   The proceedings establish venue; detailed claims here use the later v6,
   without asserting byte identity to the proceedings PDF. They distinguish
   thermostat-dependent temperature, structural correlations and dynamics.
   G.5 explicitly leaves forcefield differences and non-conservative sampling
   effects incompletely separated. Jacobian asymmetry, mode-dependent errors,
   thermostat tradeoffs and conservative/direct-force combinations are already
   substantive parents. That attribution limit is useful, but is not proof
   that no later work has resolved it.

3. **Chmiela et al., Science Advances 3, e1603015 (2017)**,
   [primary indexed Methods excerpt](https://pmc.ncbi.nlm.nih.gov/articles/PMC5419702/).
   Only indexed Methods/metadata passages read, not a complete article audit.
   GDML's harmonic-oscillator comparison fixes samples, descriptor and kernel,
   and uses a Helmholtz/Poisson decomposition with Neumann boundary conditions.
   Thus neither force decomposition nor a matched toy is a new method by
   itself. This excerpt does not establish a full thermostat/transport study.

4. **Duncan, Lelièvre and Pavliotis, J Stat Phys 163, 457–491 (2016)**,
   [DOI](https://doi.org/10.1007/s10955-016-1491-2),
   [author-hosted final article, selected Sections 1.2–1.3](https://www.ma.imperial.ac.uk/~pavl/nonreversible.pdf).
   Their overdamped nonreversible sampler preserves a chosen density through
   a weighted divergence-free drift. This is a direct parent for invariant
   density with changed dynamics and sampling efficiency. It is not an
   assertion that arbitrary position forces in inertial MD preserve canonical
   phase space. Full proof and numerical results were not independently checked.

5. **Zhang, Hou, Ge and Dral (2023)**,
   [arXiv abstract](https://arxiv.org/abs/2308.11305).
   Abstract/metadata only. Simulation-energy versus true-energy conservation
   is already an explicit primary distinction. No particular criterion or
   infrared result is imported from unread full text.

The Hinz/Bigi pair changes material, learned force, thermostat kernel and
observable; it does not meet the project's same-state/intervention/response
rule. The Hinz reservation also prevents treating its sentence as a universal
guarantee. A primary attribution limitation survives, not a qualified clash.

## Paper-only control 1: what a thermostat can preserve

Use unit mass and Boltzmann constant. Fix the physical position/velocity state,
a smooth confining reference potential U, positive temperature T, and a smooth
deterministic position-only force error r. For Langevin dynamics

    dq = v dt,
    dv = [-grad U(q) + r(q) - gamma v] dt + sqrt(2 gamma T) dW,

with gamma > 0, the desired density is
rho0 = Z^-1 exp[-(U(q)+|v|^2/2)/T]. The reference transport and thermostat
generators annihilate rho0. The additional forward-generator term is

    -div_v(r(q) rho0) = (r(q) dot v) rho0 / T.

Since rho0 has full velocity support, rho0 is stationary exactly when r = 0
almost everywhere (under the regularity and no-boundary-flux assumptions).
Changing gamma alone cannot fix a nonzero r. The same stationary-residual
argument applies to a standard Andersen velocity-refresh operator at T,
because that collision operator separately annihilates rho0.

This is **not** a theorem against all thermostats, velocity-dependent forces,
augmented samplers or altered target potentials. A conservative force error
also changes the specified target U; it can preserve a different canonical
density. A truly white, conditionally unbiased force-noise term changes the
diffusion operator and may admit an FDT correction. It is a different error
contract from the deterministic r above.

In the separate overdamped model

    dq = [-grad U(q) + r(q)] dt + sqrt(2 T) dW,

pi0 proportional to exp(-U/T) is stationary when div(r pi0) = 0. Nonzero r
can satisfy this condition, producing stationary current r pi0. For constant
antisymmetric J, r = J grad U is one construction. Dropping velocity is a
change of stochastic model, not evidence for an inertial MD correction.

## Paper-only control 2: exact marginal agreement with a hidden current

Let q,v be two-dimensional and J = [[0,-1],[1,0]]. Consider the linear model

    dq = v dt,
    dv = [(-k I + a J)q - gamma v] dt + sqrt(2 gamma Tb) dW,

where k,gamma,Tb > 0 and a^2 < gamma^2 k. This is a synthetic control, not a
claim about a trained molecular model. The characteristic polynomial is
(z^2+gamma z+k)^2+a^2. The quartic stability criterion reduces to the stated
inequality, so a unique centered stationary Gaussian exists.

Write Q = E[qq^T], V = E[vv^T], C = E[qv^T]. The stationary moment equations
give, with s = Tb/(k-a^2/gamma^2),

    Q = s I,     V = k s I,     C = -(a s/gamma) J.

Verification on paper: C+C^T=0;
V+Q(-kI+aJ)^T-gamma C=0; and
(-kI+aJ)C+C^T(-kI+aJ)^T-2gamma V+2gamma Tb I=0.
These identities determine the covariance of the stable linear process.

For any desired marginal temperature T*, select the bath parameter

    Tb = T* [1-a^2/(gamma^2 k)].

Then q ~ N(0,(T*/k)I) and v ~ N(0,T*I), exactly the separate marginals of
the harmonic reference at T*. Nevertheless

    E[qx vy - qy vx] = 2 a T*/(gamma k),

which is nonzero for a != 0. The phase-space law is not the product canonical
law. The retuned bath is an explicit intervention using analytic truth, not
the same-bath comparison of control 1 and not a proposed blind calibration
algorithm. In particular, matching the full energy distribution was not proved:
q and v are correlated. Its variance differs from the reference by
2 a^2 T*^2/(gamma^2 k).

The sign pair +a/-a at the **same** k,gamma,Tb has identical separate marginals,
force-error norm and Jacobian-asymmetry norm, but opposite oriented currents.
Orientation is a physical sign convention for this planar control; changing
coordinates changes the reported sign consistently. No new handedness effect
or representation-independent scalar universality is claimed.

## Paper-only control 3: matching force RMSE does not match the response

In the overdamped harmonic reference U=k|q|^2/2 at temperature T, compare
r_rot=aJq with r_grad=a diag(1,-1)q, for 0<|a|<k. Under the same reference
configuration measure,

    E_pi0 |r_rot|^2 = E_pi0 |r_grad|^2 = 2 a^2 T/k.

The rotational error preserves pi0 and adds current. The gradient error is
conservative but changes the stationary covariance to
diag(T/(k-a), T/(k+a)). Consequently a matched force RMSE is a useful control
but cannot assign a sign to structural or dynamical error. This calculation
is a standard linear diffusion example, not a trained-model comparison, an
OOD result, or evidence that non-conservative models are preferable.

## Attribution interface and next decisive update

The missing asset is a **matched learned-force intervention**, not another
thermostat benchmark. Before any re-entry, source/schema work must establish
one fixed conservative reference, one fixed learned force, and a specified
configuration domain, measure and boundary condition for its decomposition.
If a weighted projection is used, freeze it explicitly: r=grad phi+s with
div(mu s)=0 and the appropriate zero-normal residual boundary condition.
The choice of mu matters; a fitted model's own stationary measure cannot
silently replace independent physical truth. A Helmholtz decomposition and
an orthogonal force-error identity do not by themselves attribute transport.

A prospective comparison would hold the conservative component fixed and
vary the residual under a fixed thermostat, reporting a declared physical
current or correlation alongside static marginals; a separate thermostat
intervention would quantify sampling changes. Decomposition fitting error,
integration error, reference-force mismatch and effective independent-sample
cost would all need explicit control. Selecting a synthetic perturbation
with a guaranteed effect is a diagnostic, not evidence about learned errors.

Positive value: an independently qualified intervention could locate a
learned error component responsible for a specified physical response.
Null value: absence of that effect would rule out non-conservation as the
explanation for that response in the fixed comparison, without claiming that
all dynamics are correct. Neither result would presently be novel without
distinguishing the GDML and nonreversible-diffusion parents.

Next bounded action: audit whether an existing primary learned-force asset
actually supports this frozen component intervention and independent response
truth, or whether a source supplies a nonclassical response theorem. Do not
repeat generic temperature-control, curl-penalty, Helmholtz or OU examples.
If only a fixed-target linear/Poisson calculation remains, stop this
formulation. No 15-paper neighborhood, probability forecast or machine card
has been opened.

## Truth-asset and release boundary

- Estimands: specified invariant law, position/velocity joint moments and
  physically timed correlation/current, never temperature alone.
- Assignment/interference: full force field, thermostat kernel and bath
  parameter are separate interventions; comparisons share a fixed reference.
- Lifecycle/replay: domain, potential, masses, force error, diffusion or
  collision generator, boundary, initial/stationary law and physical clock.
- Rights/ethics/release: public primary reading; one OSTI article bundle
  privately cached, without data/software reuse or redistribution authority.
- Untouched confirmation: none; every toy and source in this note is
  development-visible. No reference array/model checkpoint was opened.
- Independent replication: no solver run; the linear controls share one
  analytic lineage and do not supply two learned physical truth systems.
- Cost: paper algebra only; decomposition, reference force and decorrelated
  sampling costs remain unqualified. No compute allocation.
- Stop: no mismatched headline clash, marginal-as-joint certificate,
  deterministic-error-as-white-noise substitution, learned-physics claim
  from a constructed toy, or Paper D result transfer.

Canonical contract and source manifest accompany this note in
`research/paper_g/force_thermostat_attribution_20260910.yaml` and
`research/paper_g/force_thermostat_source_manifest_20260910.json`.
