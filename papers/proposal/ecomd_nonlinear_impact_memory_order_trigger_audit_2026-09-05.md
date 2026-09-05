# EcoMD nonlinear-impact memory-order trigger audit

**Date:** 2026-09-05 NZST  
**Archetype:** `simulator_method`  
**Decision:** `partial_capability`  
**Candidate harvesting:** not authorized  
**Experiment, SSH, and GPU status:** not authorized

## 1. Decision

Lee's post-closure paper, *Price manipulation in nonlinear transient impact models: rigidity before
memory and complete positivity after memory* (arXiv:2609.02447v1, 2026-09-02), is a genuine new
theorem source. It establishes a sharp architecture boundary that is directly relevant to EcoMD's
concave-impact module:

- applying a nonlinear instantaneous law to the trading rate **before** any nonzero Volterra memory
  is universally round-trip safe only when that law is affine, and it is linear for a convolution
  kernel;
- applying a monotone nonlinear readout **after** a scalar memory state is safe for every input and
  every monotone readout exactly when the memory kernel is completely positive;
- failure of complete positivity has a finite piecewise-constant negative-cost witness.

This is scientifically useful and rules out a broad family of naive EcoMD extensions. It does not,
however, activate an ICLR topic. The theorem and its constructive witnesses belong to the source;
the current EcoMD price head is not one of the paper's execution-cost architectures; and the
obvious learnable repair is a direct composition of an old complementary-kernel characterization,
existing nonuniform-grid complete-positivity criteria, established monotone neural networks and
passive-system identification.

The source is therefore recorded as `partial_capability`, with zero recorded blockers removed.
There is no topic card, implementation plan, simulator run, outcome access, SSH session or GPU job.

## 2. Frozen market question

**Market-native object.** The cash cost of a zero-inventory execution schedule when signed executed
volume drives a transient impact state and transaction prices are a monotone nonlinear function of
that state.

**Rival explanations.** Under the same execution-rate input and cost convention:

- **H1 -- nonlinear source law:** concavity belongs to instantaneous signed trading rate and is then
  propagated by market memory;
- **H2 -- nonlinear state readout:** signed trading rate first enters a linear memory state, and
  concavity is applied only to the accumulated state.

**Discriminating result.** A legal zero-volume round trip with negative expected mechanical cost
separates the architectures. A positive separator invalidates universal no-manipulation; a null is
valuable only with a universal theorem or a statistically calibrated finite-sample certificate.
Ordinary price prediction, stylized-fact matching or a profitable policy in a self-generated market
does not adjudicate this question.

For an ICLR simulator method, the contribution would additionally need a learnable class that is
strictly broader or more statistically useful than existing passive and Volterra models, a
resolution-stable discrete certificate, and same-semantics truth in two independent non-EcoMD
systems before any market confirmation.

## 3. What the new theorem proves

For a rate-inside architecture,

\[
  D(t)=\int_0^t H(t,s)f(v(s))\,ds,
  \qquad C[v]=\int_0^T v(t)D(t)\,dt,
\]

Lee proves that every finite round trip is safe for every horizon only if `f` is affine for any
nonzero integrable Volterra kernel. For a nonzero convolution kernel, the intercept also vanishes.
Thus the signed power law

\[
  f(v)=\operatorname{sign}(v)|v|^\delta
\]

is manipulable for every `delta != 1`, including the square-root case, for both regular and weakly
singular memory and under every fixed positive rate cap. The construction uses a zero-volume
high-frequency source pump and thin later readout trades. Near `delta=1`, the required switching
count can diverge, so failure on a small fixed policy grid is not evidence of safety.

For the state-outside architecture,

\[
  D=G*v,
  \qquad C_h[v]=\int_0^T v(t)h(D(t))\,dt,
\]

where `h(0)=0` is continuous and nondecreasing, all-input safety for every such `h` is equivalent to
complete positivity of `G`. With `r_a+aG*r_a=aG` and `s_a+aG*s_a=1`, complete positivity means
`r_a,s_a >= 0` for every `a>0`. For nonzero `G`, the classical Clément--Nohel representation is

\[
  L=\beta\delta_0+\ell(t)\,dt,
  \qquad \beta\geq0,\quad \ell\geq0,\quad \ell\ \text{nonincreasing},
  \qquad L*G=1.
\]

Lee's storage identity turns these signs into nonnegative endpoint, potential and Bregman terms,
and the converse produces a finite negative-cost input whenever a resolvent sign fails. Completely
monotone kernels are sufficient but not necessary: the paper gives completely positive kernels
with damped oscillatory modes.

These results establish a real placement rule -- *memory before nonlinearity* -- rather than a
thermodynamic analogy. They are also already the source paper's central contribution.

## 4. The theorem does not currently apply to EcoMD

In `ecomd/models/price_formation.py`, EcoMD computes an aggregate excess-demand displacement and
applies the signed-power map directly to that aggregate before forming the log-return core. Its
Hawkes-like state is subsequently updated from the magnitude of the log return and adds a signed
excitation term. This is neither the paper's declared `G*f(v)` propagator nor its `h(G*v)` model:

1. the input is an aggregate latent-agent displacement, not an identified trader's executed rate;
2. the simulator has no matching cash account and execution-price functional for this channel;
3. the later state is nonlinear feedback from realized return magnitude, not a fixed linear
   transient-impact convolution;
4. no admissible strategic round-trip control is defined.

The earlier price-clock audit also proved that EcoMD's `+1e-8` signed-power offset is discontinuous
at zero and that a memoryless concave map cannot commute exactly with arbitrary temporal
aggregation. Lee's theorem reinforces the need for state and a declared execution clock, but it
does not retroactively turn the current module into a safe or unsafe execution model. Doing so
would require changing the simulator's scientific semantics, not merely replacing one line.

## 5. Why the obvious neural parameterization is not yet an ICLR residual

The most attractive construction is

\[
  \ell_\theta(t)\geq0,\qquad \ell_\theta'(t)\leq0,
  \qquad (\beta_\theta\delta_0+\ell_\theta dt)*G_\theta=1,
  \qquad h_\phi\ \text{monotone}.
\]

One would learn the complementary density rather than the impact kernel, solve a triangular
Volterra equation for `G_theta`, and use `h_phi(G_theta*v)` as the price response. This gives a
valid safety certificate, but each ingredient is already available:

1. the equivalence between complete positivity and a nonnegative nonincreasing complementary
   measure is classical and is explicitly reused by Lee;
2. monotone neural networks already parameterize arbitrary scalar monotone functions by integrating
   a positive neural derivative;
3. learning long-memory and integro-differential response operators is occupied by Neural Laplace
   and nonparametric Volterra-kernel methods;
4. passive and nonnegative input-output system identification already has constrained linear,
   RKHS, port-Hamiltonian and Poisson--Dirac formulations;
5. Abi Jaber et al. already optimize the same nonlinear state-outside propagator family, including
   power-law memory, through a convergent nonlinear Fredholm iteration.

Even a bounded-kernel density theorem is nearly automatic. If `beta >= beta_min > 0`, then

\[
  \beta G+\ell*G=1
\]

is a Volterra equation of the second kind. Approximation of a nonnegative nonincreasing `ell` in
`L1(0,T)` by a monotone network, followed by the standard Volterra-resolvent/Gronwall bound,
implies continuous dependence of `G` on `ell`. This combines a standard monotone universal
approximator with a standard stable linear solve. The genuinely difficult singular branch
`beta=0`, which contains weakly singular memories, is a first-kind inverse problem and is not
covered by that easy argument.

Calling this composition a "complete-positive neural operator" would therefore overstate novelty
unless it adds a result that is false for generic passive networks and not a direct corollary of the
complementary representation.

## 6. The adaptive-grid escape is also mostly occupied

At a finite grid, write the causal state map as `D=A v` and its inverse as `v=B D`. Lee's discrete
complete-accretivity theorem states that

\[
  \sum_i (BD)_i h(D_i)\geq0
\]

for every vector `D` and continuous nondecreasing `h` exactly when

\[
  B_{ij}\leq0\ (i\ne j),\qquad B\mathbf 1\geq0,
  \qquad B^\top\mathbf 1\geq0.
\]

For a lower-triangular Toeplitz inverse this reduces to nonpositive lag coefficients and
nonnegative partial sums. Feng and Li independently characterize complete positivity on uniform
and arbitrary nonuniform meshes through the convolution or pseudo-convolution inverse. Their
R-CMM work adds variable-step monotonicity preservation and, for the fractional averaged-integral
scheme, needs no step-ratio restriction.

Consequently, a learner that makes the off-diagonal entries of `B` negative, adds row/column
slacks, and differentiates through `A=B^{-1}` is an immediate constrained-matrix construction.
Sampling a continuous nonnegative decreasing complement and integrating it over nonuniform cells
also yields the required signs by telescoping. This can be useful software, but the sign theorem,
inverse representation and variable-grid structure are not new.

A genuine remaining numerical theorem would have to cover the singular `beta=0` branch or a
nonstationary/operator-valued memory with a mesh-uniform approximation and conditioning bound,
while preserving the continuous and discrete safety notions under one fixed physical clock. No
such result was established in this audit.

## 7. Other apparent exits collide directly

| Proposed exit | Direct collision or reduction | Decision |
|---|---|---|
| Train an RL agent to find negative-cost loops | Tsaknaki--Macrì--Lillo already compare DDPG with a full-information optimizer for manipulation discovery | Occupied; Lee also gives constructive finite witnesses |
| Claim learning agents create square-root-impact manipulation cycles | Zhou--Chen--Wei already report evolutionary learned cycles and a mean-field bifurcation story | Direct 2026 preprint collision; its quality does not restore novelty |
| Learn a positive exponential mixture and monotone readout | Bernstein mixtures, complete monotonicity, UMNN and passive neural dynamics | Safe but strictly narrower and compositional |
| Project an unconstrained fit to the nearest safe model | Passive-system identification and RKHS constrained-operator learning | Generic parent; market data still lack causal input-output truth |
| Use a port-Hamiltonian latent state | PoDiNN, stable/stochastic PHNN and kernel PH identification | Existing physics-informed ML family |
| Fit nonlinear power-law execution paths | Nonlinear Fredholm propagator optimization | Existing market-specific model and solver |

The empirical contract is an independent failure. Anonymous market order flow does not reveal the
counterfactual price path or cash cost of an assigned round trip, and fitting `G` and `h` to the
same passive tape cannot validate universal safety. EcoMD-generated trajectories would be
self-validation unless the input, execution price, cost and comparator systems are fixed first.

## 8. Narrow research boundaries before the matrix follow-up

Lee explicitly leaves general nonlinear matrix convolution, marginal stability and singular
actuation open. Of these, the only boundary plausibly broad enough for ICLR is:

> Can a differentiable learner represent noncommuting matrix-valued long-memory operators and
> nonlinear cross-impact readouts while providing a necessary-or-sharp safety certificate that is
> invariant across temporal discretizations?

Simple scalar memory times a fixed positive-semidefinite cross-impact matrix, simultaneous
diagonalization, an ICNN readout, or a port-Hamiltonian realization is not enough; those are direct
sufficient constructions. A survivor would need at least one of:

- a characterization or strict expressivity theorem for noncommuting matrix memory that exceeds
  ordinary passivity and the scalar complementary-kernel result;
- a minimax or finite-sample separation showing why the constrained estimator learns a larger
  truth class or needs fewer interventions than passive state-space and unconstrained Volterra
  baselines;
- a singular-memory, arbitrary-mesh **conditional** recovery theorem in frozen physical norms,
  with a matching lower bound and a truth class strictly larger than completely monotone mixtures.

That is a theorem target, not an authorized candidate or experiment. It should be killed if it
reduces to a common metric transform, a simultaneously diagonalizable family, an M-matrix inverse,
an ICNN, or a port-Hamiltonian network.

The follow-up in Section 11 closes the universal-convex-readout version of this boundary. It does
not characterize every fixed nonlinear readout and every matrix Volterra kernel, but it proves that
quantifying over all convex-gradient readouts collapses the kernel to one common scalar memory.

## 9. Gate table and machine decision

| Gate | Result |
|---|---|
| Genuine post-closure theorem | Pass |
| Concave rate-before-memory is universally safe | Fail: affine rigidity |
| Current EcoMD instantiates either execution architecture | Fail: action and cost semantics differ |
| Complementary-kernel neural parameterization is irreducible | Fail: direct theorem + monotone-network + Volterra-solve composition |
| Arbitrary-grid sign certificate is unoccupied | Fail: complete accretivity and nonuniform CP/R-CMM parents |
| Adversarial/RL manipulation discovery is unoccupied | Fail: direct 2026 work and source witnesses |
| Passive-system learning is unoccupied | Fail: RKHS, PoDiNN and PHNN parents |
| Universal convex-gradient matrix memory is an irreducible class | Fail: rank-one quadratic readouts force one scalar temporal kernel; the positive direction is MIMO Zames--Falb/Lee |
| Multi-asset safe-kernel learning is unoccupied | Fail: direct nonlinear factor, dynamically coupled and nonparametric cross-impact work |
| Singular zero-feedthrough inversion has mesh-uniform same-norm conditioning | Fail: fractional complements already force `kappa_2 >= N^gamma/sqrt(2 gamma+1)`; the continuum inverse is unbounded |
| Shape constraints or positive mixtures make singular recovery a new method | Fail as stated: stability then comes from an explicit source class/regularizer, with direct inverse-problem and constrained-system-identification parents |
| Two-system and market truth contract | Fail |
| Existing recorded blocker removed | Fail |

**Machine decision:** `partial_capability`, `removed_blockers: []`,
`candidate_harvest_authorized: false`, `exact_reentry_scope: none`.

No code, data, simulator, outcome, SSH endpoint or GPU was used. The A800 at `100.113.230.38` and
the V100 workers at `100.80.236.112` and `100.123.220.57` remain idle for this route.

## 10. Exact re-entry condition

Re-audit only after a written theorem supplies either (i) a singular-memory learner with a
cone-specific conditional/minimax recovery rate in frozen observation and kernel norms, a matching
lower bound, and a truth class strictly larger than completely monotone positive mixtures, or (ii) a fixed,
market-native nonlinear readout and genuinely noncommuting matrix-memory class whose sharp
certificate exceeds Lee's conic complements and state-space storage, MIMO Zames--Falb/IQC,
factor-direction concave cross-impact, matrix positive type, simultaneous diagonalization,
M-matrix/complete-accretive discretization, ICNN/UMNN, Neural Laplace, passive RKHS
identification, PoDiNN and port-Hamiltonian networks. Universal quantification over all convex
gradients is closed by Section 11. Before implementation, freeze one execution-rate/cash-cost
estimand, two independently maintained non-EcoMD systems with the same action and clock semantics,
and a lawful untouched market confirmation source. A new machine decision is then required.

## 11. Follow-up: universal nonlinear matrix memory collapses to scalar memory

### 11.1 Frozen question and rival explanations

Let `d >= 2`, let `G` be an integrable causal `d x d` convolution kernel, and define

\[
 D_v=G*v,\qquad
 C_{G,F,T}[v]=\int_0^T v(t)^\top \nabla F(D_v(t))\,dt,
\]

where `F` ranges over differentiable convex potentials with `\nabla F(0)=0`.

- **Matrix hypothesis:** noncommuting or asset-specific temporal kernels can remain safe for every
  convex-gradient readout.
- **Rigidity hypothesis:** universal readout safety forces every asset direction to share the same
  scalar temporal kernel; matrix structure survives only after restricting the readout class.

A matrix survivor would reopen the only broad theorem branch from Section 8. Scalar collapse is
also useful because it prevents an invalid learner from hiding heterogeneous decay behind an ICNN.

### 11.2 Exact bounded theorem

Under the global `L1` assumptions needed for the Fourier argument, all-input safety on every finite
horizon for every such `F` holds if and only if

\[
              G(t)=g(t)I_d\quad\text{a.e.},
\]

where `g=0` or `g` is a globally completely positive scalar kernel. Thus the universal nonlinear
matrix class is not a noncommuting class at all.

This statement is invariant under a simultaneous change of state and flow coordinates. If
`D'=SD`, `v'=Sv`, and `h'(D')=S^{-T}h(S^{-1}D')`, then the power pairing is unchanged, the class of
convex potentials is unchanged, and `G'=SGS^{-1}`. The conclusion `G=gI` is therefore preserved;
it is not an artifact of asset units or an analyst-selected Euclidean basis.

### 11.3 Necessity proof

It is enough first to use the convex quadratics

\[
 F_H(x)=\tfrac12x^\top Hx,\qquad H\succeq0.
\]

The matrix positive-type criterion, equivalently Plancherel, gives for almost every frequency
`omega`

\[
            \operatorname{Herm}\!\left(H\widehat G(i\omega)\right)\succeq0
            \qquad\text{for every }H\succeq0.                 \tag{11.1}
\]

Fix a real vector `u` and put `H=uu^T`, `Z=Ghat(i omega)`. For every complex `x`, (11.1) says

\[
       \operatorname{Re}\{\overline{u^\top x}\,u^\top Zx\}\geq0.       \tag{11.2}
\]

The two complex-linear functionals `a(x)=u^T x` and `b(x)=u^T Zx` must be proportional. Otherwise
there is a `y` with `a(y)=0` and `b(y) != 0`; adding an arbitrary complex multiple of `y` to any
`x_0` with `a(x_0)=1` makes the real part in (11.2) negative. Hence

\[
                         u^\top Z=z_u u^\top,\qquad \Re z_u\geq0.
\]

This holds for every real `u`. Applying it to the basis vectors and their pairwise sums forces all
`z_u` to be the same number, so `Z=z(omega)I_d`. Fourier uniqueness yields `G=gI_d` almost
everywhere. Finally, restricting `v` and `F` to one coordinate reduces universal safety to Lee's
scalar theorem, which forces `g` to be completely positive (apart from the zero kernel).

For sufficiency, take the complementary measure
`L=beta delta_0+ell(t)dt`, with `beta>=0`, `ell>=0` nonincreasing and `L*g=1`. Lee's vector Bregman
storage identity, equivalently Theorem 8.9 with one coefficient `M=I`, makes every term in the cost
nonnegative for every convex `F`. This is also the convex-potential branch of the classical MIMO
Zames--Falb positivity-preserving construction.

### 11.4 Minimal heterogeneous-memory witness

The collapse is substantive rather than merely algebraic. Let

\[
 G(t)=\operatorname{diag}(e^{-t},e^{-2t}),\qquad
 F(x)=\tfrac12(x_1+x_2)^2,
\]

so each diagonal memory is individually completely positive and the readout is a rank-one convex
gradient. For the constant input `v=(1,-3/2)` on `[0,T]`, direct integration gives

\[
 C(T)=-\frac{T}{8}+\frac{5}{16}-\frac12e^{-T}+\frac{3}{16}e^{-2T}.
\]

At `T=3`, `C=-0.086928768151<0`. Thus two safe scalar kernels become unsafe solely because their
decay rates differ and the convex readout couples the coordinates. Since the kernel vanishes at
infinity, Lee's vector remote-compensation theorem converts this all-input separator to a finite
vector round trip.

### 11.5 Collision screen

| Apparent contribution | Primary collision or reduction | Verdict |
|---|---|---|
| Convex-gradient nonlinear readout plus scalar dynamic multiplier | Safonov--Kulkarni prove the MIMO Zames--Falb extension for gradients of convex potentials; Heath--Wills give the same construction and IQC form | Mechanism occupied |
| Sharp universal matrix classification | Two steps from Lee: apply his matrix positive-type boundary to all rank-one quadratic Hessians, then his scalar complete-positivity converse | Useful corollary, not an irreducible paper theorem |
| Learn nonlinear multi-asset decay with uncertainty and real-data tests | Hey--Neuman--Tuschmann already give an offline nonparametric concave multi-asset estimator, confidence bounds, shape projection and proprietary plus public-data experiments; its projection is not a universal nonlinear-safety certificate | Direct learning collision; adding safety must still exceed the separate theory parents |
| Allow factor nonlinearities and coupled decay | The current *Concave Cross Impact* formulation derives no-manipulation factor geometry, calibrates it to metaorders, and its 2026 revision explicitly advertises dynamically coupled impact states | Direct finance collision; the newest PDF was inaccessible during this audit, so no stronger theorem-level claim is made here |
| Linear/noncommuting matrix baseline | Alfonsi--Schied--Kloeck characterize matrix-valued positive-definite kernels and commuting well-behaved subclasses | Mature parent |

The recent empirical papers also do not create the needed same-estimand disagreement. Predictive
cross-impact from passive correlated flow, causal price response to an assigned trade, and
universal no-manipulation are different estimands. Opposite-looking conclusions across them cannot
be promoted to a discovery fork without an assignment and interference contract.

### 11.6 Follow-up decision

The universal-convex-readout matrix branch is **killed**. Its negative theorem is retained as a
reusable safety and expressivity check, but an ICLR paper built from `g_theta I + ICNN` would be a
composition of existing results and would deliberately discard heterogeneous asset memory. A
restricted fixed-readout matrix branch remains mathematically incomplete in full generality, but
Lee's fixed-readout state-space classification and conic certificates, recent factor-direction
cross-impact theory, matrix positive type, MIMO IQC/passivity and the missing causal truth contract
leave no current irreducible ML claim.

The machine decision remains `partial_capability`, with no removed blocker and no authorized
candidate harvesting, implementation, outcome access, SSH or GPU work.

### 11.7 Primary sources for the follow-up

- Safonov and Kulkarni, *Zames--Falb Multipliers for MIMO Nonlinearities*:
  https://doi.org/10.1002/1099-1239(200009/10)10:11/12%3C1025::AID-RNC537%3E3.0.CO;2-L
- Hey, Mastromatteo and Muhle-Karbe, *Concave Cross Impact*:
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5046242
- Hey, Neuman and Tuschmann, *Nonparametric Estimation of Self- and Cross-Impact*:
  https://arxiv.org/abs/2510.06879
- Alfonsi, Schied and Kloeck, *Multivariate Transient Price Impact and Matrix-Valued Positive
  Definite Functions*: https://arxiv.org/abs/1310.4471

## 12. Follow-up: the zero-feedthrough singular complement is an inverse problem, not a free
conditioning theorem

### 12.1 Frozen numerical question

The remaining scalar escape from Section 5 sets `beta=0` in the complementary relation

\[
                         (\ell * G)(t)=1,
\]

with `ell >= 0` nonincreasing and possibly unbounded at the origin. The proposed positive claim was
that a differentiable solver could recover `G` on arbitrary refined grids with a mesh-uniform
condition number while retaining the full singular complete-positive class. The rival explanation
is that this is a first-kind Volterra inverse: any same-norm uniform guarantee is impossible, and
stability can be restored only by declaring a stronger source class, a different norm, or a
regularizer.

The distinction is representation-invariant only after the norms are frozen. Here both the
observed convolution residual and recovered kernel use the ordinary `L2(0,1)` norm, and their
cellwise discretizations use the corresponding equal quadrature weights. A diagonal rescaling or
learned preconditioner is not a stability result unless it and its inverse remain uniformly bounded
in those physical norms.

### 12.2 Continuum obstruction

For `0 < gamma < 1`, take the valid complementary pair

\[
 \ell_\gamma(t)=\frac{t^{\gamma-1}}{\Gamma(\gamma)},\qquad
 G_\gamma(t)=\frac{t^{-\gamma}}{\Gamma(1-\gamma)},\qquad
 \ell_\gamma*G_\gamma=1.
\]

Convolution by `ell_gamma` is the Riemann--Liouville fractional integral `I^gamma`. On a finite
interval it is compact, injective and infinite-rank on `L2`, so its inverse on its range is
unbounded. Consequently there is no constant `C` for

\[
                      \|f\|_2\le C\|I^\gamma f\|_2
\]

over the unrestricted same-norm class. Dostanic gives the corresponding fractional-integral
singular-value decay; Della Valle--Pouchol formulate Abel inversion as an inverse problem of order
`gamma` and recover convergence only in a Hilbert scale with smoothness and boundary conditions.
This already rules out a mesh-uniform raw inverse, independently of neural architecture.

### 12.3 Explicit discrete lower bound

Use the exact product-integration map for cellwise-constant inputs on a uniform grid `h=1/N`:

\[
 (A_N)_{ij}=\frac{h^\gamma}{\Gamma(\gamma+1)}
 \big[(i-j+1)^\gamma-(i-j)^\gamma\big],\qquad j\le i.
\]

Let `w_k=(k+1)^gamma-k^gamma`. For the constant vector, telescoping gives

\[
 \frac{\|A_N\mathbf 1\|_2}{\|\mathbf 1\|_2}
 \ge \frac{1}{\Gamma(\gamma+1)\sqrt{2\gamma+1}}.
\]

For the alternating vector `x_j=(-1)^j`, the positive weights `w_k` decrease, so every alternating
partial sum has magnitude at most `w_0=1`. Hence

\[
 \frac{\|A_Nx\|_2}{\|x\|_2}\le
 \frac{h^\gamma}{\Gamma(\gamma+1)},
 \qquad
 \boxed{\ \kappa_2(A_N)\ge \frac{N^\gamma}{\sqrt{2\gamma+1}}\ } .
\]

The same result holds with equal cell-quadrature `L2` weights because the common factor cancels.
For `gamma=1/2`, direct SVD gives `kappa_2/N^gamma` equal to `0.9821, 0.9729, 0.9683, 0.9661,
0.9651, 0.9645` for `N=16,32,64,128,256,512`. Thus the lower bound is not merely a continuum
pathology hidden by this standard discretization.

If `P_N A_N Q_N` were uniformly conditioned while `P_N,Q_N` and their inverses were uniformly
bounded in the frozen norms, submultiplicativity would make `A_N` uniformly conditioned, contrary
to the bound. Any successful preconditioner must therefore move the growing factor into a change
of norm, encoder or decoder; it cannot erase physical noise amplification.

### 12.4 What the lower bound does and does not prove

The alternating vector is a worst-case direction in the ambient space. It does **not** prove that
every finite-dimensional fractional family, every monotone complement, or every statistically
regular source class is unrecoverable. Such restrictions can yield conditional stability. They
must, however, be printed as part of the estimand:

- the source class and its smoothness or mixture-order radius;
- the observation and recovery norms;
- the noise model and excitation design;
- the regularization rule and parameter selection; and
- the approximation and statistical lower bound under the same class.

Once these are supplied, the obvious repairs have direct parents. Lamm and Elden prove
noise-optimal sequential Tikhonov convergence for standard first-kind Volterra discretizations;
Della Valle and Pouchol give Abel regularization in Hilbert scales; Aravkin--Burke--Pillonetto
already combine stable-spline regularization with nonnegativity, unimodality and complete-
monotonicity inequalities in system identification. Restricting to positive exponential mixtures
also leaves the full complete-positive class and enters classical relaxation-system and Markovian
approximation territory; Bayer--Breneis obtain superpolynomial finite-factor approximation for the
fractional stochastic-Volterra kernel.

### 12.5 Decision and precise residual

The proposed singular-memory claim is **killed in its mesh-uniform same-norm form**. A neural
triangular solve cannot have a resolution-independent raw conditioning guarantee over the full
class. A regularized solver, Sobolev/Hilbert-scale decoder, fixed-order positive mixture or
shape-constrained stable spline is scientifically legitimate, but it is a specialization or
composition of established inverse-problem and system-identification methods.

The only unclosed mathematical residue is much narrower: a cone-specific minimax/conditional
recovery theorem for the general complete-positive complement class, in fixed physical norms,
with a matching lower bound and a strict separation from completely monotone mixtures and generic
Volterra regularization. No such theorem was established here. Even if obtained, it would still
need assigned execution-rate/cash-cost truth, two independent non-EcoMD systems and a lawful
untouched market confirmation source to support an ICLR market claim.

The route decision therefore remains `partial_capability`, with no removed blocker and no
authorized candidate harvesting, implementation, outcome access, SSH or GPU work.

### 12.6 Primary sources for the singular follow-up

- Dostanic, *Asymptotic Behavior of the Singular Values of Fractional Integral Operators*:
  https://doi.org/10.1006/jmaa.1993.1177
- Lamm and Elden, *Numerical Solution of First-Kind Volterra Equations by Sequential Tikhonov
  Regularization*: https://doi.org/10.1137/S003614299528081X
- Della Valle and Pouchol, *Solving Abel Integral Equations by Regularisation in Hilbert Scales*:
  https://arxiv.org/abs/2107.12062
- Aravkin, Burke and Pillonetto, *Generalized System Identification with Stable Spline Kernels*:
  https://doi.org/10.1137/16M1070517
- Bayer and Breneis, *Markovian Approximations of Stochastic Volterra Equations with the
  Fractional Kernel*: https://arxiv.org/abs/2108.05048
