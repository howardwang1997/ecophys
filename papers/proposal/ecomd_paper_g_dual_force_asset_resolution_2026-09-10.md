# Paper G: dual-force asset and attribution resolution

PRIVATE / INTERNAL — 2026-09-10, session started 03:27 Pacific/Auckland.
Public evidence eligible: false. Source/schema and paper-only resolution;
not a new candidate, cycle, forecast, implementation decision or experiment.

## Outcome

An actual dual-output checkpoint is now pinned through public metadata,
and two published artifact records have explicit rights and file contracts.
This is a useful capability, but it does **not** supply the pure non-conservative
intervention required by the preceding attribution question. Interpolating
between two force heads generally changes their conservative component too.

A cheaper stationary-work diagnostic avoids choosing a force decomposition,
but for a fixed standard Langevin bath its mean equals the kinetic-temperature
excess times the friction. It cannot be promoted into new independent
identification. Local allocation of that residual work also depends on the
chosen reference potential. The narrowed contribution remains unqualified.

Disposition: `partial_capability`, no recorded blocker removed, harvest false.
The existing `slow_memory_random_batch_invariant_correction` graph attachment
is a cross-reference for the force-noise/thermostat control boundary. It changes
neither that closed route nor the project scope. The full Paper G objective
remains active. Paper D results and permissions are not reused.

## Public source contracts

| Asset | What is verified | What is not established |
|---|---|---|
| Bigi ICML supporting record | Zenodo14778891, open CC-BY-4.0; `data-record.zip`, 2,608,121,264 bytes, publisher MD5 `63a3b51451c0ef667ed537e043926c21`; archive-preview listing includes `pet-cons.pt`, `pet-everything.pt`, `pet-nocons.pt` | File names do not establish head semantics, identical learned weights, a decomposition, or version correspondence to every later paper addition; payload not downloaded |
| UPET model and documentation | Public repository revision `c05f6a32658f46c56b23ebae3e8143001693efd1`; `models/pet-mad-s-v1.1.0.ckpt`, displayed size13.1MB, publisher SHA256 `8d5e1588c70f7a4998940e7b535ab84aeb42c0f2253c889d4af23a1a8c6fd553`; repository label BSD-3-Clause; official documentation describes conservative and direct heads | Weights were not downloaded or executed; no global gradient projection or common physical-response truth is certified |
| PET-MAD Materials Cloud record | Record2025.145/v2, API record `h41qv-1n493`, CC-BY-4.0; README checksum verified; documented datasets, split names, units, trained models and inputs | Split names are not untouched Paper G confirmation; the record's surrogate reference is not exact physical truth; no arrays or model payloads opened |

Sources: [Bigi archive](https://zenodo.org/records/14778891),
[UPET revision](https://huggingface.co/lab-cosmo/upet/tree/c05f6a32658f46c56b23ebae3e8143001693efd1),
[official output documentation](https://lab-cosmo.github.io/upet/latest/models.html),
[Materials Cloud record](https://archive.materialscloud.org/record/2025.145).

The Materials Cloud README documents `extxyz` reference energies in eV,
forces in eV/angstrom and periodic stresses in eV/angstrom^3; problem-specific
`train.xyz`, `val.xyz`, `test.xyz`; and two separately labelled MAD/MPtrj
electronic-structure settings for its benchmark. These are useful schema
contracts, not a license to exchange physical targets. The newer PET-MAD1.5
family uses a different declared electronic-structure level from legacy MAD1;
its metadata was recorded as a separate lead, not substituted into this fixture.

[Mazitov et al., Nature Communications16:10653 (2025)](https://www.nature.com/articles/s41467-025-65662-7)
supplies the scientific link: selected architecture, consistency and availability
sections describe direct-force output and material-specific comparisons, with
reference compatibility explicitly separated from experimental accuracy.
No published benchmark values are being reproduced or treated as Paper G results.

The prior [Bigi v6](https://arxiv.org/html/2412.11569v6) was extended here to
selected Sections4.1,4.8 and AppendicesE,H,I,J. Shared-head models and an MTS
correction `F_C-F_D` are explicitly described. AppendixE already measures
closed-loop work. Neither the text nor the output documentation imposes the
gradient-projection identity needed below. Lack of that identity is a
mathematical contract limit, not an allegation of erroneous implementation.

## Control 1: a two-head switch is not a pure component intervention

Freeze a configuration domain, reference measure mu, boundary conditions and
the Hilbert space L2(mu) of vector fields. Let P denote orthogonal projection
onto the closed gradient subspace. Assume the conservative head F_C=-grad U_C
belongs to that subspace, and define the direct head F_D and R=F_D-F_C.

    P R = P F_D - F_C,
    (I-P) R = (I-P) F_D.

Therefore R has no conservative component **if and only if** F_C=P F_D.
Shared parameters or an energy output do not imply this identity. Under the
interpolation F_lambda=F_C+lambda R,

    P F_lambda = (1-lambda) F_C + lambda P F_D.

The conservative component changes with lambda unless the same identity holds.
This is elementary Hilbert-space algebra, not a new theorem.

An explicit countercontrol uses an isotropic Gaussian mu in two dimensions,
J=[[0,-1],[1,0]], F_C=-kq and F_D=-(k+delta)q+aJq. Both heads may report
the same separate energy U_C=k|q|^2/2, yet R=-delta q+aJq. Its gradient part
is -delta q and its weighted-divergence-free part is aJq. The switch changes
both radial stiffness and circulation whenever delta and a are nonzero.
This is a construction allowed by the output contract, not an observed
property of the pinned checkpoint.

A prospective component intervention could use P F_D+lambda(I-P)F_D after
P and its approximation error are independently qualified. The projection
depends on mu, the domain and the boundary. Fitting it on the tested dynamics'
own stationary measure and silently treating it as independent truth is invalid.
The GDML Helmholtz/Poisson parent already prevents calling projection itself
the novel contribution.

## Control 2: total residual work has a cheaper, limited meaning

Keep a single time-independent direct force F_D(q). Under unit masses and
Boltzmann constant, fixed friction gamma>0 and one bath at T>0, consider

    dq=v dt,
    dv=[F_D(q)-gamma v]dt+sqrt(2 gamma T)dW.

For a chosen smooth, single-valued potential U, define

    W_U(t)=integral_0^t [F_D(q_s)+grad U(q_s)] dot v_s ds.

Changing reference to U+phi changes W by phi(q_t)-phi(q_0), by the chain
rule. Its stationary expectation is unchanged if those endpoint variables
are integrable. A long-time sample statement additionally requires the
boundary difference divided by t to vanish; stationarity alone must not be
silently replaced by a finite-window convergence claim. On a periodic domain,
the potential must be single-valued/periodic; a winding force is not a
removable potential gradient.

Ito's formula for E_U=|v|^2/2+U(q), in d unconstrained velocity dimensions,
gives

    dE_U = [R_U dot v-gamma |v|^2+d gamma T]dt
           +sqrt(2 gamma T) v dot dW,
    R_U=F_D+grad U.

With a stationary integrable energy and the usual martingale integrability,

    <R_U dot v> = gamma [<|v|^2>-dT].

Thus mean work bypasses the Hodge projection but is redundant with mean
kinetic-temperature excess **for this thermostat contract**. It can be a
consistency check, not additional causal information about transport. The
identity is not transferred to global velocity rescaling, GLE auxiliary
variables, constrained velocities, multiple baths or numerical trajectories
without their own energy balances. No new entropy-inference algorithm is claimed.

## Control 3: local residual-work attribution depends on the reference

The total reference shift averages to zero, but its coordinate contributions
need not. Reuse the preceding session's stationary rotational linear control,
with Q=sI and E[qv^T]=-(as/gamma)J. Choosing phi=b q1 q2 changes the mean
coordinate1 residual work by -bas/gamma and coordinate2 by +bas/gamma.
Their sum vanishes, while b can vary continuously. The actual process has
not changed at all; only the potential used to assign residual work has.

Consequently a per-atom or per-mode map formed from arbitrary reference-head
residual work cannot automatically locate the source of physical error.
Physical heat delivered to a separately specified bath is another observable.
This does not criticize local entropy-production methods with their own frozen
thermodynamic force, parity and observation contracts.

Two direct inference parents were checked:

- [Frishman and Ronceray, arXiv1809.09650v3](https://arxiv.org/abs/1809.09650v3),
  associated with PRX10,021009 (2020): selected first-section equations
  distinguish irreversible current and the stationary-density gradient for
  overdamped diffusion, and connect force information with entropy production.
  This is not a theorem for inertial q/v data. Final/preprint identity and
  numerical outcomes were not independently verified.
- [Das and Manikandan, Communications Physics9:237 (2026)](https://www.nature.com/articles/s42005-026-02667-8):
  selected Methods specify overdamped diffusion and reconstruct the
  dissipative force/local entropy production with short-time current inference.
  Its background points to underdamped work; that does not extend its own
  displayed estimator to inertial data. Full inference and benchmark claims
  were not audited. Generic learned dissipation maps already have strong parents.

## Remaining scientific fork and stop condition

The meaningful fork remains whether a **specified learned residual component**
causes a **specified physical-response error**, after conservative force and
sampling changes are controlled. This turn qualifies output access at the
documentation level but proves why it is insufficient for that question.
Positive and null effects would both be interpretable only after the component
intervention and independent response reference are valid.

Do not spend another cycle on a generic head-switch, work/temperature score,
curl penalty, Hodge decomposition or local dissipation map. A new advance
must supply a response-specific identification result beyond the existing
projection/current-inference parents, or an actual primary matched mechanism
disagreement. More checkpoint names do not remove the blocker.

The next bounded source task is to audit an existing response-attribution
method on the pinned force contract, asking whether it distinguishes
conservative target bias, irreversible currents and thermostat-induced response
changes with a finite, independently checkable error guarantee. If it only
recovers standard force projection or mean work, stop that formulation.

Truth-asset contract: complete physical state and bath law; independently
fixed projection measure/domain/boundary; separate component and thermostat
interventions; full input/trajectory/event semantics before replay; explicit
rights; untouched confirmation absent; independent replication absent; costs
for projection, reference forces and decorrelated responses unqualified.
All source examples are development-visible. No archive/model/array payload,
notebook output or scientific source file was opened or executed; documentation
usage snippets and public article results are not raw experiment access.
No GPU, outreach, purchase or publication occurred.
