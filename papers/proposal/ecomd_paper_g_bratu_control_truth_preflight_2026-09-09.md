# Paper G: nonlinear equilibrium and actuation truth preflight

**PRIVATE / INTERNAL — infrastructure qualification, not a new topic or public evidence.**
Session started 2026-09-09T08:34:37Z; literature cutoff 2026-09-09.
This record follows source reading and algebra. It is not a prospective freeze.

The Bratu family supplies an explicit nonlinear stationary truth control,
including branch stability. The inspected source does not yet supply the full
controlled-dynamics, replay and independent-confirmation contract needed here.
Decision: **partial_capability**, no removed contribution blocker, no re-entry.
This is not a third neural-PDE measurement cycle.

## 1. Source capability and direct parents

[Fabiani et al., arXiv2505.02308v2](https://arxiv.org/html/2505.02308v2)
combine neural timesteppers with Newton–Krylov, Arnoldi and continuation.
The Bratu case uses Chebyshev/BDF training trajectories and a finite-difference
comparison. The paper already discusses eigenvalue sensitivity and compares
learned bifurcations with an analytical critical parameter. Generic neural
bifurcation analysis and the warning that value accuracy need not ensure
spectral accuracy therefore have direct parents. The
[publisher record](https://www.nature.com/articles/s42256-026-01265-1)
confirms a July2026 Nature Machine Intelligence article; the technical reading
here is explicitly tied to the earlier v2, not assumed identical final text.

The [control follow-up, arXiv2509.23975v1](https://arxiv.org/html/2509.23975v1),
sections III–IV, introduces a controlled operator but uses an additive actuation
approximation in its Bratu experiment. It has a finite-difference controlled
comparison. Crucially, the end of IV-A says the NO controllers were tested with
their assumed actuator effect, leaving transfer to the original plant under
model mismatch for later work. Thus the presence of an FD comparison does not
establish that the same NO-designed controller was validated on that plant.
This is a declared protocol boundary, not an allegation about the paper's results.

The release tag v1.0 resolves to commit
`80eb5a0d36b264a882be6ded172f016869eba478`. A filtered, checkout-free source clone
was used to inspect five named text blobs. The manifest records immutable paths,
byte sizes and SHA256. No data arrays, model files, notebook outputs or external
code were executed or opened. Directory listings were metadata only.

## 2. Exact nonlinear stationary control

On x in [0,1], consider u_t=u_xx+lambda exp(u), with homogeneous Dirichlet
conditions. The known stationary family can be parameterized without an
ambiguous branch-selection root solve:

    U_theta(x)=2 log[cosh(theta)/cosh(theta(1-2x))],
    lambda(theta)=8 theta^2 sech(theta)^2,   theta>0.

Direct differentiation verifies the boundary conditions and
U_theta''+lambda(theta) exp(U_theta)=0. Also

    lambda'(theta)=16 theta sech(theta)^2 [1-theta tanh(theta)].

Since theta tanh(theta) increases strictly from zero to infinity, there is one
positive fold parameter theta_* satisfying theta_* tanh(theta_*)=1.
The curve increases before the fold and decreases afterward. This supplies two
stationary profiles for each 0<lambda<lambda(theta_*). The cited decimal value
of the critical lambda is a reported approximation, not a newly computed
certified enclosure here.

An elementary stability derivation makes the control more useful. Define the
self-adjoint Dirichlet linearization

    L_theta w=w_xx+lambda(theta) exp(U_theta) w,
    phi_theta=partial_theta U_theta
             =2[tanh(theta)-(1-2x)tanh(theta(1-2x))].

The function phi_theta is strictly positive in the interior and zero at the
endpoints. Differentiating the stationary equation gives

    L_theta phi_theta=-lambda'(theta) exp(U_theta).

Let psi_theta>0 be a principal Dirichlet eigenfunction, with principal eigenvalue
mu_1. Self-adjointness and integration by parts yield

    mu_1 <psi_theta,phi_theta>
      =-lambda'(theta)<psi_theta,exp(U_theta)>.

Both inner products are positive, so sign(mu_1)=-sign(lambda'). The lower branch
is linearly stable, the upper branch unstable, and the fold has a zero principal
eigenvalue with the explicit positive kernel phi_theta. For an exact time map,
the corresponding multiplier is exp(tau mu_1); it equals one at the fold.

This is classical Bratu/Sturm–Liouville analysis, not a new theorem. It qualifies
stationary profiles, branch labels and the sign of the principal linear mode.
It does not give the entire spectrum, a nonlinear basin of attraction, finite
amplitude control response, a global existence claim, or historical PDEBench
trajectory truth. A fixed point obtained from a learned time map still needs
comparison with this independent stationary target.

## 3. Holding a physical input differs from adding an endpoint kick

For a finite-dimensional linearization x_dot=A x+B_c z with z held constant
during a physical interval tau, variation of constants gives

    x_next=exp(tau A)x+D_tau z,
    D_tau=integral_0^tau exp(s A) B_c ds.

An endpoint update exp(tau A)x+tau B_c z is an approximation to this held-input
protocol. It may instead be an exact definition of a different impulsive action.
Do not compare their gains before fixing force-amplitude versus integrated-kick
units. For bounded A, D_tau=tau B_c+tau^2 A B_c/2+O(tau^3).
For a PDE generator this expansion needs domain/regularity conditions; a
finite-grid bound is not automatically uniform as the mesh is refined.

For one mode a, define r=a tau and chi(r)=(exp(r)-1)/r, with chi(0)=1. The exact
held-input gain is tau b chi(r). A small number written as tau in seconds does
not alone control r across all retained modes and actuator directions.

A scalar control check is explicit. Let a>0,b>0 and choose feedback z=-k x with
k=exp(r)/(tau b). The endpoint approximation predicts a closed-loop multiplier
of zero. The held-input multiplier is exp(r)[1-chi(r)]. At r=1 this is
e(2-e)<-1, so it is unstable. At r->0 the discrepancy vanishes; a=0 is the exact
null. This is standard sampled-data control, not a source-specific instability
finding. In particular, it does not establish that the selected Bratu slow modes
or the reported sampling interval violate the approximation's useful regime.

An autonomous model with perfect value and Jacobian fit cannot, without an
actuation contract, decide which of these two distinct actions is intended.
The source already acknowledges actuation uncertainty. Generic actuator
identification, sampled-data correction or controller transfer is not made novel
by this example.

## 4. Pinned source contract

The full-domain generation script defines continuous initial functions from
random trigonometric, Gaussian and polynomial factors. It samples 39 lambda
values from0 to3.8, outputs51 spatial points at31 times separated by0.001, and
calls Chebfun pde15s with declared tolerances. It retains trajectories only when
the requested number of time outputs is returned. It discards the first two
frames before forming transition pairs, then partitions pairs by random index.
The observed export lists transition arrays, not a complete latent/RNG replay
manifest. These are source-protocol facts, not measured bias or contamination.

Consequences for this project's future use:

- Preserve the complete continuous initial function, trajectory identity and
  generation RNG state. A row-wise split does not certify an untouched
  trajectory or parameter confirmation partition under this project's rules.
- Treat return-length acceptance as an explicit selection rule. Freeze how
  non-completion, physical blow-up and solver statuses would be distinguished
  before outcomes; no frequency or cause was inferred here.
- Solver tolerances specify the numerical procedure, not a certified global
  trajectory-error radius. Keep analytical equilibria separate from dynamic truth.
- The FD routine and Chebfun wrapper provide distinct numerical constructions.
  They remain one public research lineage, not two independently governed
  replications. The wrapper reconstructs a function from equispaced input values;
  that is an observation contract, not recovery of an arbitrary original field.
- The pinned README declares CC BY-NC-SA4.0. No standalone license file is
  present in this tag's tree. Record that declaration without asserting all
  dependency, data or publication rights are resolved. MATLAB/Chebfun and control
  dependencies need separate version and availability qualification before use.

Only source metadata is retained in the repository; source bodies stay in the
private temporary cache. Neither a future compatible reimplementation nor a
claim about the validity of every released result follows from these reads.

## 5. What this asset enables, and what remains open

The supported estimand family is now explicit: nonlinear stationary profile,
fold location and principal stability sign for the declared Bratu problem, plus
held-input linear response conditional on a known generator and actuator map.
This is useful infrastructure beyond the earlier translated-sine truth control.
It changes the available truth menu without removing a recorded contribution
blocker from the history-response or teacher-ranking formulations.

A future protocol must fix initial/branch selection, forcing functions and units,
hold timing, state reconstruction, controller design and deployment plant,
numerical error budget, complete versions/rights, untouched confirmation and an
independent replication. Cost must include truth construction, parameter and
controller selection, numerical certification, training and inference. No
participant or outreach component is proposed.

Stop at a target substitution, missing actuator lifecycle, incomplete replay,
uncertified dynamic reference, adaptive confirmation selection, or a reduction
to existing bifurcation, approximation or control methods. The next topic still
needs a distinct, discriminating scientific contribution. No candidate harvest,
new cycle, F3, forecast, machine card, scientific implementation or outcome
access is authorized by this preflight. The broader Paper G objective remains active.
