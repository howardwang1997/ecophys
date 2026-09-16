# Paper G: Keller–Segel critical aggregation truth preflight

**PRIVATE / INTERNAL — paper-only development analysis, not public evidence or a new topic activation.**
Session started 2026-09-09T13:14:36Z (2026-09-10 01:14 NZST).
Literature cutoff: 2026-09-09. This record follows source inspection and algebra;
it is not a prospective forecast, independent confirmation, or an empirical result.

The new source lane supplies a concrete physical object related to the repository's
neural PDE and physical-constraint work: aggregation in the two-dimensional,
parabolic–elliptic Keller–Segel equation. Exact controls distinguish density fidelity,
symmetry-orbit fidelity, and finite-time persistence. **Partial capability** is the
decision. No recorded contribution blocker is removed and no candidate harvesting
is authorized. The previous noise/history lane is not being reopened.

## 1. Source scope and closest parents

| Source and inspected scope | What it establishes here | Boundary |
|---|---|---|
| [Blanchet–Dolbeault–Perthame 2006](https://ejde.math.txstate.edu/Volumes/2006/44/blanchet.pdf), Theorem 1.1 and Section 2.1 | Classical critical mass and virial blow-up bound on the whole plane | Finite second moment is essential to this virial use; an upper bound is not the exact singularity time |
| [Feng–Ng–Zhang, DeepLagrangian v1](https://arxiv.org/pdf/2510.14297v1), formulation, loss, Section 4, selected experiment definitions | Direct neural density-flow parent; the written attractive-kernel energy and Theorem 4.4 can be checked | Freeze whole-space interpretation separately from the initial bounded-domain wording; the numerical loss and particle reference use a smoothed kernel |
| [Shen–Wang, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/b9a17133e3943509243b5e197c1c23b2-Paper-Conference.pdf), Equations 3–8, Section 3 and [Appendix G](https://papers.neurips.cc/paper_files/paper/2023/file/b9a17133e3943509243b5e197c1c23b2-Supplemental-Conference.pdf) selected passages | Direct loss-to-KL and modulated-energy parent | Its Coulomb force is repulsive; main analysis is periodic, with additional boundary/regularity discussion for the whole space |
| [Carlen, arXiv2312.00614v2](https://arxiv.org/html/2312.00614v2), Theorems 1.2–1.3 and Section 1.1 | Critical log-HLS deficit controls squared L1 distance to the translation/dilation optimizer manifold, with coefficient 1/32 | This is a distance to a manifold, not to a specified optimizer; the full proof was not audited |
| [Yu–Yang, ASYS v1](https://arxiv.org/html/2606.20467v1), Section 3.2 and Tables A.6–A.7 | Direct symbolic collapse-profile parent | Its KS fit uses a supplied singularity time and a finite pre-asymptotic window; it does not infer an unknown event time or contradict a different asymptotic rate |
| [Giesselmann–Kwon v2](https://arxiv.org/html/2309.09036v2), formulation, Theorem 3.2 and Remark 3.3 | Conditional reconstruction/residual stability is an existing, method-independent parent | Bounded Neumann domain and c−Δc=ρ differ from the unscreened whole-plane model below; not an exact collision with the bound derived here |
| [Jüngel–Leingang 2017](https://arxiv.org/abs/1709.03931), abstract and metadata only | Discrete virial blow-up bounds already exist for several time discretizations | Detailed assumptions and proofs not inspected |

No opposite-headline fork is inferred from these different domains, kernels or
targets. Other search hits and article reference lists are intake, not audited evidence.
There was no fifteen-work audit, code inspection or raw-result access.

## 2. Exact physical contract and classical virial control

Fix the whole plane, no advection or chemical degradation, μ,χ>0, mass M, and
the unsmoothed kernel K(x)=log|x|/(2π). For the normalized density p=ρ/M,

    ∂t p + div(p A[p]) = 0,
    A[p] = −μ ∇log p − χ M ∇K*p.

Assume the regularity, decay and integrability needed for the following moment
identities. With center m=∫x p dx and J=∫|x−m|²p dx finite, the exact equation gives

    m' = 0,
    J' = 4μ − χM/(2π).

Thus Mcrit=8πμ/χ. For supercritical mass define κ=χM/(2π)−4μ>0 and
τv=J(0)/κ. A classical smooth solution cannot continue past τv with this contract.
The identity gives an upper bound on its maximal regular existence time, not its
exact value. Critical mass alone and J'=0 do not classify all critical solutions.

For the mathematical unit-disk density ρ0=16, μ=χ=1, M=16π and J(0)=1/2,
the bound is τv=1/8. This is a standard control, not a newly measured event time.
Smooth initial densities can be used instead; no claim requires training on the
discontinuous disk. Bounded-domain, advected and smoothed-kernel cases need their
own moment identities.

## 3. Attractive interaction and critical translation control

For a smooth, sufficiently decaying zero-mass difference f, set h=K*f. Since
Δh=f, integration by parts with vanishing boundary term gives

    ∬ K(x−y) f(x)f(y) dxdy = −∫|∇h|² dx ≤ 0.

The zero-mass and boundary conditions matter: this is not an identity for an
arbitrary nonzero-mass charge distribution. It reverses the sign for the repulsive
Green function g=−K. In particular, the attractive modulated interaction cannot
be used as a nonnegative addition to KL for arbitrary pairs of densities.

The signs in DeepLagrangian's kernel, Section 4 energy definition, and Theorem 4.4
were visually checked on PDF pages 2,9,13. This is a mathematical scope objection
to the displayed energy domination, not an implementation finding or a claim
about the article's numerical results. A correction to one source is not a Paper G
contribution. The source PDF and selected-render hashes are privately recorded.

A stronger independent control uses μ=χ=1 and M=8π. Set

    q(x) = 1 / [π(1+|x|²)²].

This is a normalized smooth critical equilibrium:

    ∇log q = −4x/(1+|x|²),
    ∇K*q = x/[2π(1+|x|²)],
    A[q] = 0.

Let the reference be p(t)=q, and the hypothesis be p̂(t,x)=q(x−a(t)), a(0)=0.
The invertible translation flow has velocity a'(t); by translation invariance,
A[p̂]=0. Consequently its population Lagrangian residual is

    L = ∫₀ᵀ∫ p̂ |a'−A[p̂]|² dxdt = ∫₀ᵀ|a'|²dt.

Choose a(t)=(t/T)e1. The terminal displacement is fixed and L=1/T. To bound
terminal KL without numerical integration, the first-coordinate marginal of q is
1/[2(1+s²)^(3/2)]. The event {x1>0} has probabilities 1/2 and
1/2+1/(2√2) under q and q(·−e1). Pinsker's inequality therefore gives

    KL(q(·−e1) || q) ≥ 1/4.

The reference velocity gradient vanishes, C1=0. At T=2, the displayed
DeepLagrangian bound under its unrestricted whole-space smooth-flow reading would
give KL≤L/4=1/8. Moreover, the critical modulated free energy is zero between
these translated equilibria, while KL is positive: their free energies coincide
and the first variation at q is constant.

This control has finite entropy, logarithmic moment, first moment, translation
action and relative entropy, but **infinite second moment**. It is explicitly
outside Section 2's finite-J virial contract. The theorem's displayed assumptions
do not state a finite-second-moment restriction; nevertheless its initial domain
wording and the precise network/prior class must remain separate qualifications.
No exact representation by the finite Gaussian-prior experimental KRnet has been
proved here. No failure of that trained architecture is inferred.

Removing translations/dilations from the metric invokes the existing optimizer
manifold in log-HLS stability. Adding a center penalty or the elementary bound
|a(T)|²≤T∫|a'|² is also insufficient novelty. The source objection does not remove
any of the previous generic measurement or off-support-repair blockers.

## 4. Finite-moment persistence requires residual action

The following paper-only derivation is independent of the source objection.
It is a development truth control with **unqualified novelty**.

Keep Section 2's exact unscreened equation and supercritical mass. Consider any
smooth positive normalized hypothesis on [0,T] with finite centered moment,
continuous moment evolution and sufficient decay, satisfying

    ∂t p̂ + div[p̂(A[p̂]+ε)] = 0.

Write m(t)=∫x p̂ dx, J(t)=∫|x−m(t)|²p̂ dx, J0=J(0)>0, and ε̄=∫p̂ ε dx.
The mass, center and virial calculations now yield

    m' = ε̄,
    J' = −κ + 2∫p̂(x−m)·(ε−ε̄) dx,
    Lshape = ∫₀ᵀ∫p̂|ε−ε̄|² dxdt = L − ∫₀ᵀ|m'|²dt.

For a≥0 choose b(t)=a/(1+at), so b'+b²=0. Completing a square gives

    ∫p̂|ε−ε̄|² dx ≥ b(J'+κ) − b²J.

Integrate, use J(T)≥0, and obtain

    Lshape ≥ −a J0 + κ log(1+aT).

Optimizing over a≥0 gives the explicit necessary condition

    Lshape ≥ 0,                                           T≤τv,
    Lshape ≥ κ[log(T/τv)−1+τv/T],                         T>τv.

This lower bound is invariant to a common translation of coordinates and removes
the center-drift component of the residual. It says that a finite-moment smooth
hypothesis surviving beyond the classical virial limit cannot have arbitrarily
small *population residual against the exact equation*. The threshold grows
quadratically for T/τv just above one. It does not identify the actual blow-up
time, prove that every small-loss model has accurate density, or apply to q above.

The scalar moment relaxation has equality path

    J*(t)=(1−t/T)[J0+(κT−J0)t/T],
    b(t)=(κ/J0−1/T)/[1+(κ/J0−1/T)t],

with J*' = −κ+2bJ* and J*(T)=0. This checks the algebra and the optimized
moment bound. It does **not** show attainability by a regular full Keller–Segel
density up to T, nor establish optimality over neural approximations. No solver,
symbolic computation package, optimization run or numerical fixture was executed.

For a softened learner, ε must be defined against the exact kernel. A sampled
loss using Kδ cannot simply be substituted for L. The bias vector
χM(∇K−∇Kδ)*p̂, its weighted norm, and time/space sampling errors must be controlled.
The exact Kδ used in the cited numerical parent has not been reconstructed here.
No claim about its error magnitude is authorized by the symbolic identity.

## 5. Truth-asset preflight and disposition

- Supported estimands: the classical finite-moment virial identity, population
  residual action for finite-time persistence, and the separate infinite-moment
  critical translation control. Density KL, orbit distance, peak height, mass
  concentration and exact event time remain distinct.
- Assignment/interference: deterministic complete initial density and equation;
  common physical units, mass, diffusivity, attraction and initial family.
  Particle sampling is part of the numerical approximation, not a new physical
  intervention. No experimental assignment or participant protocol exists.
- Lifecycle/replay: dimension, domain and boundary; chemical screening/advection;
  exact versus softened kernel and δ; initial density and tails; normalization;
  complete flow/particle state; time representation; quadrature and sampling;
  optimizer and RNG state; singularity stopping rule. Only the analytic subset
  is qualified. No released implementation or replay state was inspected.
- Rights/ethics/release: public primary-paper reading only. One PDF is cached
  privately; no article figures redistributed, no code/data rights inferred.
  No participants, outreach or field data; any future release needs its own rights
  review and public-evidence separation.
- Confirmation: all controls and source interpretations here are development.
  No untouched partition or independently executed replication has been created.
  Freeze initial-profile families, tail classes, mass regimes and kernel limits
  before any future selection or outcomes. Existing Paper D roles are unchanged.
- Replication/cost: independent classical PDE, neural residual and particle
  reference comparisons are not qualified merely by their names. Current
  scientific compute is zero. A finite-cost rigorous upper bound on population
  residual, including tail/singularity effects, is still missing.
- Stop rules: no escalation for a source correction, symmetry alignment, mass
  threshold reproduction, generic residual control, or mistaking a virial bound
  for exact event time. Stop any proposed certificate whose premise substitutes
  a softened/sampled loss without accounting for bias and integration error.

The next decisive **paper-only** update is narrow: determine whether the necessary
persistence bound admits a practically informative, finite-sampling and kernel-bias
certificate under a named density/tail class, beyond classical reconstruction and
moment controls. An exact PDE-level sharpness or obstruction result could also
matter. If this reduces to standard concentration plus an unusable density bound,
retain the analytic control and stop this formulation. This condition is not
candidate authorization and has no implied publication probability.

Record this infrastructure session in the re-entry ledger, evidence registry,
route graph, daily log and long-term memory. Search cycles and forecasts remain
unchanged; no machine card, scientific implementation, outcome access or compute.
