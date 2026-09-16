# Paper G: HydroGym controlled-flow truth preflight

PRIVATE / INTERNAL. Development source qualification and elementary paper-only
controls; excluded from public research evidence. Session started
2026-09-09T09:48:33Z. No candidate search cycle or execution protocol is activated.

## Decision and scope

**Partial capability; no qualified re-entry.** HydroGym supplies a concrete public
controlled-flow source relevant to the repository's learned PDE dynamics work.
Seven source/license texts are pinned and hashed. They expose a useful interface
to inspect, but do not establish a validated, independently replicated control
truth service. The source is newly inspected here, not newly created by us.

This preflight starts from the recorded history-response and numerical-teacher
routes. Their contribution blockers remain: generic sensitivity/history remedies
have direct prior, and a supplied-reference certificate is elementary error
propagation. A new accessible platform does not remove either blocker. No claim
that the entire fluid-control domain is closed follows from those route decisions.

## Primary source and version contract

- [Nature version of record](https://www.nature.com/articles/s41586-026-10917-6),
  published 19 August 2026: publisher-indexed selected main/methods and
  availability passages read. It describes multiple CFD backends and
  differentiable control. The declared code archive is Zenodo 21062222; the
  identity between that archive and our Git pin is unqualified. Reported flow
  datasets have a separate release path and were not acquired. The final
  article declares CC BY-NC-ND 4.0. No final-PDF replication is claimed.
- [Expanded preprint v2](https://arxiv.org/html/2512.17534v2), dated 30 June
  2026: selected overview, Sections 3.4 and 5.13 and control-method scope read.
  Its two-dimensional periodic Kolmogorov setup exposes four sinusoidal control
  amplitudes at wavenumbers 4–7. Gradient-enhanced policy optimization is an
  existing method in this work, not an unoccupied generic proposal. This
  version declares CC BY 4.0 and is not silently substituted for the final text.
- [L4DC 2025 parent](https://proceedings.mlr.press/v283/lagemann25a.html):
  official metadata and abstract only, PMLR 283:497–512. This earlier platform
  paper establishes lineage; its full proof, implementation and results were
  not independently audited. It is not an independent truth provider.
- [Selected source snapshot](https://github.com/dynamicslab/hydrogym/tree/4ab9854dea3d84e38a59c25e0f5835a00cf8225f):
  commit `4ab9854dea3d84e38a59c25e0f5835a00cf8225f`; seven text files,
  including root MIT license, recorded in
  `research/paper_g/hydrogym_source_manifest_20260909.json`. This is one source
  bundle, not seven independent sources or a full dependency/archive snapshot.

The publication and preprint are versions of one research work. Platform-level
solver diversity does not by itself supply two implementations of this same
periodic, forced, observed control problem. Numerical deployment to a wing is
not a physical experiment for our confirmation contract.

## Selected interface contract

The inspected class is `KolmogorovFlow`, inheriting `JAXFlowEnvBase`, whose
constructor has no Hugging Face integration. Other environment classes use a
different base. This selected class does not establish the behavior of every
platform entry point or packaged training configuration.

The selected source defines four clipped actions, a spatial sinusoidal control
field, interval rollouts, and a spectral vorticity state. Its default parameters
include `dt=0.001`, `action_time=10`, four actions bounded by ±0.5, and a
64×64 flow grid. These are source defaults, not a claim about the published
benchmark run or an authorized execution configuration. The flow state stores
`omega_hat`, the interval trajectory, episode time and terminal flag. Policy
observations average sampled velocity magnitudes over that trajectory. The
reward combines trajectory-averaged energy with an absolute-action penalty;
its weight is configuration dependent. Source metadata is not continuum
conformance or a certified actuator-energy objective.

The selected integration text describes explicit nonlinear stages and implicit
viscous steps with a fixed control field during each rollout. All physical
units, Fourier conventions, sample endpoints, substep counts and actual duration
must be fixed before comparison. A nominal interval or dataclass alone does
not certify physical elapsed time. No source module was imported or executed.

## Exact development control A: held-force response

Independently specify the continuum momentum equation on the periodic square
\([0,2\pi]^2\), density one:

\[
\partial_t u+(u\cdot\nabla)u=-\nabla p+\nu\Delta u+f,
\qquad\nabla\cdot u=0.
\]

Let \(K=\{4,5,6,7\}\), \(b_4=1\), and \(b_k=0\) otherwise. On a held-control
interval of duration \(\tau\), set

\[
u(x,y,t)=\left(\sum_{k\in K}c_k(t)\sin(ky),0\right),\qquad
f(x,y)=\left(\sum_{k\in K}(b_k+a_k)\sin(ky),0\right).
\]

This is a zero-mean invariant shear family: incompressibility holds, the
advective term is identically zero, and constant pressure suffices. With
\(\lambda_k=\nu k^2\), direct substitution gives

\[
\dot c_k=-\lambda_kc_k+b_k+a_k,\qquad
c_k(\tau)=r_kc_k(0)+g_k(b_k+a_k),
\quad r_k=e^{-\lambda_k\tau},\quad
g_k=\frac{1-r_k}{\lambda_k}.
\]

Thus \(\partial c_j(\tau)/\partial a_k=\delta_{jk}g_k\). The positive control
is \(g_k>0\) for \(\tau>0\); the zero-duration control is \(g_k(0)=0\).
The continuous limit at \(\lambda_k=0\) is \(g_k=\tau\), although the frozen
development family uses positive viscosity. For a finite envelope, take
\(\nu\in[1/200,1/40]\), \(c_k(0)\in[-1,1]\), \(|a_k|\le1/2\), and
\(\tau\in[0,10]\). These are mathematical control ranges, not a benchmark
sampling distribution or a new topic program.

A velocity reset of size \(J\) at the interval start contributes \(r_kJ\).
A constant body force of equal integrated impulse \(J\) contributes
\(g_kJ/\tau\). For positive viscosity and duration these differ; they approach
the same limit only as the duration vanishes. A body force in momentum units
also requires the physical curl when represented in vorticity; its amplitude
is not interchangeable with a vorticity reset. This contract is derived from
the specified PDE and makes no assertion about an executed source discrepancy.

The control is linear inside a nonlinear PDE. It exercises forcing, clock,
normalization and observation semantics; it cannot certify nonlinear mode
coupling, chaotic response, long-horizon gradients or learned-policy transfer.

## Exact development control B: state-dependent power

Write \(\langle\cdot\rangle\) for spatial average over the periodic square.
Orthogonality of the sine modes gives

\[
E=\tfrac12\langle|u|^2\rangle=\tfrac14\sum_k c_k^2,
\quad P=\langle u\cdot f\rangle=\tfrac12\sum_k(b_k+a_k)c_k,
\quad D=\nu\langle|\nabla u|^2\rangle=\tfrac\nu2\sum_k k^2c_k^2,
\quad\dot E=P-D.
\]

The control-only fluid power is \(P_a=\tfrac12\sum_k a_kc_k\).
With one nonzero action, changing the corresponding initial shear coefficient
from \(c\) to \(-c\) reverses this power while preserving the action norm,
instantaneous kinetic energy and pointwise speed. If that coefficient is zero,
instantaneous control power is zero even for a nonzero action. These are exact
positive/negative/null accounting controls. They do not identify electrical
actuator cost, and an action regularizer need not claim to represent fluid power.

For \(d_k=r_kc_k(0)+g_kb_k\), the finite controlled-minus-uncontrolled response is

\[
E(c,a;\tau)-E(c,0;\tau)
=\tfrac12\sum_k d_kg_ka_k+\tfrac14\sum_k g_k^2a_k^2.
\]

Consequently a power comparison must match full initial state, background
forcing, duration and action, rather than only action magnitude. Signed velocity
or equivalent full-state information resolves the instantaneous sign ambiguity.
Equal instantaneous speed is not a proof of identical legal observation
histories: past forcing and trajectory averaging may distinguish the states.
No claim of nonidentifiability for the full HydroGym history or failure of a
published controller is made.

## Truth-asset preflight and stop rules

| Contract item | Present qualification and remaining requirement |
|---|---|
| Supported estimands | Exact shear coefficients, endpoint energy, prescribed held-input derivatives, and integrated fluid power. Broader nonlinear response remains unqualified. |
| Assignment/interference | Development actions are fixed external tapes on separate deterministic trajectories with matched initial state. A learned feedback policy changes the action-assignment law and needs its own state and conditioning contract. |
| Lifecycle/replay | Specify initialization, optional relaxation, intervention start, clipping, hold intervals, solver steps, observation windows, reward, termination and wrapper reset. Retain full spectral state, mean velocity convention, latest observation trajectory, physical/episode clocks, action tape, configuration and any policy/normalizer/RNG/wrapper state. Exact executable replay is unqualified. |
| Version/rights | Seven immutable-address source texts hashed; MIT root license read. Full dependency/container/config/data rights and archive-to-paper identity remain unqualified. No participants, downloaded outcomes or third-party source redistribution. |
| Confirmation | All inspected texts and both chosen analytic controls are development material. No untouched whole-source confirmation partition is qualified. A future partition must be fixed before outcome access and tuning, with separate provenance and no shared trajectory fragments. |
| Replication | Exact algebra supplies a narrow analytic reference. An independently implemented same-PDE/forcing/clock/observable solver with a convergence or error contract is still needed for nonlinear claims. Multiple named backends are insufficient without this alignment. |
| Cost/precision | This session used seven text downloads and paper algebra, zero solver steps. Execution precision, gradient cost, hardware compatibility and training budget are unqualified. No speed, memory or publication-probability estimate is inferred. |

For any later simulator-method screen, freeze an equal-access/equal-budget
baseline: direct solver sensitivities where valid, controlled finite differences
with an error/step contract, and established sensitivity-supervision or policy
optimization as applicable to the exact claim. Count source trajectories,
gradient/adjoint calls, precision, wall time and any privileged state. No new
method has been specified here, so this is a required comparison contract,
not an approved experiment plan.

Stop escalation if the source/version/physical target cannot be matched; if
initial resets are substituted for held forcing; if action norms replace the
claimed physical cost; if interval averages are treated as endpoint state; if
one linear subfamily is promoted to nonlinear truth; or if re-entry depends
only on repeating generic differentiable-control results. Repairing source
implementation or conducting conformance work is not a scientific contribution.

The next useful update must identify a specific remaining capability needed by
a distinct same-target contribution, or a primary-model disagreement that can
be separated by this controlled asset. Access to the platform alone authorizes
neither candidate harvesting nor a third cycle in the saturated parent. No raw
questions, full hostile audit, forecast, machine card, scientific implementation,
simulation, outcome access, GPU work, outreach, purchase or publication resulted.

## Records

Contract: `research/paper_g/hydrogym_control_truth_preflight_20260909.yaml`.
Source manifest: `research/paper_g/hydrogym_source_manifest_20260909.json`.
Re-entry record: `paper_g_hydrogym_control_truth_capability_20260909`.
The route graph, evidence registry, daily log and lasting memory record this as
infrastructure progress. Search-cycle, protocol and forecast records remain
unchanged. Operational verification is retained only in the private receipt.
