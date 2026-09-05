# EcoMD unpaired interaction-energy trigger audit

**Date:** 2026-09-05  
**Stage:** bounded D-3 re-entry-trigger audit; no candidate harvest  
**Archetype:** `measurement_method` / `simulator_method` boundary  
**Decision:** `not_trigger`, zero removed project blockers  
**Outcome, implementation, simulation, SSH and GPU access:** none

## Decision first

The ICLR 2026 paper
[iJKOnet](https://arxiv.org/abs/2506.01502) makes two useful facts unusually explicit. First, a
population-dynamics benchmark that was intended to be unpaired had retained particle trajectories
across snapshots, and correcting that pairing materially changed performance. Second, both iJKOnet
and JKOnet* fail to recover general interaction energies reliably in the corrected unpaired setup.
Neither fact reopens an EcoMD topic.

The apparent repair, replacing a mini-batch pair average by an off-diagonal U-statistic, removes an
ordinary finite-batch diagonal bias but not the inverse problem. Even within conservative
Wasserstein gradient flows, a single non-equilibrium population path need not separate external
potential from pair interaction. Existing work already characterizes the identifiable mean-field
interaction space, learns interaction kernels from density or discrete particle snapshots, jointly
selects interaction, external-potential and diffusion terms, and supplies discretization,
observational-error and Wasserstein-stability results. EntangledSBM occupies the broader neural
multi-particle bridge branch but learns a target-conditioned control bias, not the physical
interaction law.

EcoMD adds a more basic observation mismatch: its particles are latent, mutually coupled and not
exchangeable observed market units. A chronological market tape is neither an independent
population at each elapsed time nor a complete joint molecular configuration. No named blocker is
removed, so candidate harvesting and all compute remain closed.

## 1. Frozen trigger claim

**Proposed capability claim.** The corrected paired-versus-unpaired evidence and interaction-energy
failure in iJKOnet reveal an unoccupied ICLR method: use a debiased inverse-JKO objective to recover
EcoMD-style pairwise forces from identity-free population snapshots.

**Market-native object.** A pair-interaction contribution to the drift of a resolved market
population, separated from external forcing and diffusion, with an intervention response that is
unchanged by relabeling or splitting latent agents.

**Rival explanations.** Under H1, the reported failure is mainly a biased pairwise mini-batch
estimator, so an off-diagonal estimator yields a new and identifiable interaction-learning method.
Under H2, debiasing is elementary and the substantive obstacles are the potential--interaction
gauge, ill-conditioned mean-field inverse operator, and absence of the required market population
observation.

**Discriminating result.** H1 requires a theorem that jointly identifies the interaction, external
potential and diffusion from finite unpaired empirical measures, with a stable rate near loss of
excitation and a market observation matching that operator. An exact observational equivalence or
a direct existing estimator supports H2. Either sign is useful: a positive result could reopen a
method screen, while a null prevents synthetic force recovery from being reported as market
mechanism identification.

## 2. What the ICLR result actually establishes

[Persiianov et al.](https://arxiv.org/abs/2506.01502) assume independent samples from measures
`rho_0,...,rho_K` and that consecutive measures exactly follow a finite-step JKO update for an
unknown energy functional. Their inverse-optimization objective avoids a precomputed optimal
transport plan. The proved recovery-quality result, however, is restricted to the potential-energy
component under convexity and smoothness conditions. The paper explicitly leaves interaction and
internal energies outside that theorem.

The corrected experiments are scientifically useful:

- the earlier synthetic pipeline kept particle identity across times even though the population
  problem was described as unpaired;
- performance changes substantially when every time snapshot is independently regenerated;
- neither iJKOnet nor JKOnet* accurately reconstructs the tested interaction energies;
- adding a learnable interaction term can degrade recovery of a purely external potential.

The official MIT implementation is pinned at
[`873bc0a`](https://github.com/MuXauJl11110/iJKOnet/tree/873bc0a331f79e2ab1b2d539d29ebb9df0ce444a).
The paper's current arXiv version is v3 from 2026-03-02, and the code and ICLR acceptance both
predate the August EcoMD family closures. This is missed collision evidence, not a post-closure
capability change.

## 3. Two exact reductions

### 3.1 Off-diagonal debiasing is not the scientific core

Use the conventional interaction energy

\[
  \mathcal W(\rho)=\frac12\mathbb E\,W(X-X'),
  \qquad X,X'\stackrel{\mathrm{iid}}{\sim}\rho.
\]

For a batch of size `B`, the all-pairs V-statistic has expectation

\[
  \mathbb E\!\left[\frac{1}{2B^2}\sum_{i,j}W(X_i-X_j)\right]
  =\frac{B-1}{B}\mathcal W(\rho)+\frac{W(0)}{2B}.
\]

Deleting the diagonal and dividing by `B(B-1)` gives the unbiased order-two U-statistic. This is a
direct application of classical
[U-statistic theory](https://doi.org/10.1214/aoms/1177730196). It can be a useful implementation
fix, but it is neither a new estimator class nor a proof that `W` is identified. The bias is only
`O(1/B)`; inverse-operator singularity and component aliasing can remain at infinite sample size.

### 3.2 A transient potential--interaction gauge

Consider the Wasserstein gradient-flow drift generated by

\[
  \mathcal J(\rho)=\int V(x)d\rho(x)
  +\frac12\iint W(x-y)d\rho(x)d\rho(y)
  +\beta\int \rho\log\rho\,dx.
\]

Only the sum

\[
  \nabla V(x)+(\nabla W*\rho_t)(x)
\]

enters the drift. Suppose the observed, possibly non-equilibrium path has a fixed mean
`m=integral x d rho_t(x)`. For any scalar `c`, define

\[
  \delta W(z)=\frac c2\lVert z\rVert^2,
  \qquad
  \delta V(x)=-\frac c2\lVert x\rVert^2+c\,m^\top x.
\]

Then for every time and every shape of `rho_t`,

\[
  \nabla\delta V(x)+(\nabla\delta W*\rho_t)(x)
  =[-cx+cm]+c[x-m]=0.
\]

Thus a fully transient, non-radial population path with fixed mean cannot distinguish a quadratic
confinement change from a quadratic interaction change. The ambiguity preserves the entire density
path, not merely one statistic, and survives particle relabeling. It complements the rotational
current counterexample in the prior transient-population audit: the gradient restriction removes
solenoidal ambiguity but does not automatically identify the decomposition of the gradient energy.

Multiple initial populations with different controlled means can break this particular witness,
but then recovery depends on an excitation/coercivity operator. Calling that active population
design does not by itself create a new theorem.

## 4. Nearest-work collision

| Primary work | What is already supplied | Consequence for the proposed residual |
|---|---|---|
| [Lang and Lu](https://arxiv.org/abs/2106.05565) | The identifiable function space for mean-field interaction kernels is the closure of an inverse-operator RKHS; the infinite-dimensional inverse problem is ill-posed | A gauge/null-space characterization or regularization warning is occupied |
| [Lang and Lu](https://arxiv.org/abs/2010.15694) | Nonparametric interaction-kernel recovery from discrete space-time density observations, with regularized least squares and numerical-error rates | Identity-free density-level kernel learning is occupied |
| [Messenger and Bortz](https://arxiv.org/abs/2110.07756) | Weak-form recovery of interaction force, external potential and diffusivity from discrete-time particle histograms, with `O(N^{-1/2})` convergence under a full-rank library | Simultaneous snapshot recovery and a finite-particle rate are occupied |
| [Carrillo et al.](https://arxiv.org/abs/2402.06355) | Sparse partial inversion for nonlinear aggregation--diffusion, with noise/discretization analysis and a stability estimate controlling solution Wasserstein error | Sparse recovery, robustness and downstream density stability are occupied |
| [JKOnet*](https://papers.nips.cc/paper_files/paper/2024/file/0ce1eb87dbb03fdfa872a93d15cfe333-Paper-Conference.pdf) | A first-order JKO loss parameterizes potential, interaction and internal energy from snapshot distributions | General-energy inverse-JKO parameterization is occupied, even though recovery can fail |
| [iJKOnet](https://arxiv.org/abs/2506.01502) | End-to-end inverse JKO, an unpaired benchmark correction, potential-only quality theory and a documented interaction failure | The exact motivating diagnosis and easy algorithmic frame are already published |

A neural, grid-free implementation might improve scalability, but that is not yet an irreducible
result. To survive, it would need matching upper and lower finite-sample bounds in the identifiable
quotient, explicit behavior near small coercivity eigenvalues, and a demonstrated advantage not
obtainable by changing the basis or solver in the existing weak-form/RKHS methods.

## 5. Why a joint multi-particle bridge does not rescue force identification

[EntangledSBM](https://arxiv.org/abs/2511.07406) uses a Transformer to parameterize coupled bias
forces for first- or second-order Langevin systems. Its object is the stochastic-control solution
that steers a known base path measure toward a target distribution. It does not prove that static
endpoints identify the uncontrolled physical interaction or that its learned bias equals that
interaction.

This distinction is decisive. Many path laws can share the same endpoints, and a Schrödinger bridge
selects one by a reference-path and relative-entropy criterion. Changing the reference dynamics can
change the selected bridge while preserving the endpoint data. EntangledSBM therefore occupies the
generic neural multi-particle bridge story but does not remove the interaction-identification
blocker.

## 6. Pairing is a different observation, not a free validation signal

Paired samples expose an empirical coupling between successive states and can approximate
increments or velocities. Unpaired samples expose only marginals. Preserving identities in an
unpaired benchmark therefore changes the observation sigma-field; it does not merely reduce Monte
Carlo noise. Strong-form trajectory estimators and weak-form density estimators already embody
these two regimes.

The iJKOnet correction is important benchmark QA, but a paper whose only contribution is detecting
or removing this leakage would repeat the published diagnosis. A scientific residual would have to
derive a calibrated test that detects hidden cross-time coupling from released data without access
to generator labels, and prove that the test controls a downstream identification error. No such
result or EcoMD-specific need is present here.

## 7. EcoMD and market observation contract

The required samples are observable particles from a common population law at synchronized elapsed
times, or complete joint configurations drawn repeatedly under a fixed initial law. EcoMD's latent
agents are coupled through price and history, have analyst-chosen identity and cardinality, and are
not public market entities. Treating them as independent samples invokes the very propagation-of-
chaos and representation assumptions that need validation.

Public prices, returns or order-book snapshots are one evolving market system. Resting orders also
undergo birth, cancellation, execution, priority and strategic replacement rather than a fixed-mass
diffusive gradient flow. No current legal asset supplies repeated complete initial populations,
controlled excitation, untouched force or response truth, and an independently governed exact
replication. Synthetic EcoMD data could only show that an estimator recovers the generator used to
make those data.

## 8. Gate decision

| Gate | Result |
|---|---|
| Exogenous post-closure capability | Fail: paper v3, acceptance and repository predate the August closures |
| Interaction recovery theorem | Fail: iJKOnet's proof is potential-only and interaction recovery fails empirically |
| Irreducible debiasing | Fail: off-diagonal correction is a standard U-statistic |
| Identifiability beyond known operators | Fail: an exact transient `V/W` gauge remains; RKHS/coercivity theory is direct prior |
| Unoccupied estimator/rate | Fail: density inversion, WSINDy and partial inversion cover the obvious estimators and guarantees |
| Multi-particle bridge equals physical force | Fail: EntangledSBM learns a reference-dependent control bias |
| Market truth contract | Fail: no synchronized observable population, actuator, force truth or independent replication |

**Decision:** `not_trigger`, with `removed_blockers: []` and
`candidate_harvest_authorized: false`. No topic card, experiment plan or machine decision is
created.

## 9. Exact re-entry boundary

Re-audit only if both sides become concrete:

1. a theorem and estimator jointly recover `V`, `W` and diffusion from finite unpaired empirical
   measures modulo an explicitly declared gauge, give matching upper/lower error behavior near
   coercivity loss, and are demonstrably not a neural restatement of inverse JKO, weak-form sparse
   regression, RKHS inversion or partial inversion; and
2. a legal market-native asset supplies repeated synchronized observable populations or assigned
   excitation with complete pre-state, untouched response/force truth and an independently governed
   same-estimand replication.

Until then, do not construct an EcoMD candidate around unpaired interaction recovery, implement a
debiased inverse-JKO variant, generate simulator outcomes, connect by SSH or use the A800/V100
workers for this route.
