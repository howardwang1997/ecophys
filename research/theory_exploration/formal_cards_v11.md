# Formal cards v11 — multi-stationary drift tomography

These cards separate exact mathematics from novelty and venue admission. Cards T1--T4 have complete elementary
proofs under their stated regularity assumptions. A complete proof is not a novelty pass: the main ingredients are
stationary Fokker--Planck subtraction, weighted divergence-free currents, Jacobi last multipliers, Nambu currents
and elementary differential topology.

## T1 — pointwise stationary-density subtraction

On an open subset of `R^d`, consider

\[
 dX_t=\{b(X_t)+u_m(X_t)\}\,dt+\sqrt{2\kappa}\,dW_t,
 \qquad m=0,\ldots,K,
\]

with common known `kappa>0`, known `u_m`, common unknown `b` and positive `C^2` stationary densities `rho_m`.
Let

\[
 s_m=\nabla\log\rho_m,
 \qquad
 g_m=\kappa\{\Delta\log\rho_m+\lVert s_m\rVert^2\}
      -\nabla\!\cdot u_m-u_m^\top s_m.
\]

The stationary Fokker--Planck equation divided by `rho_m` is

\[
 \nabla\!\cdot b+b^\top s_m=g_m.
\]

Subtracting environment zero gives

\[
 \alpha_m(b)=q_m,
 \qquad
 \alpha_m=d\log(\rho_m/\rho_0),
 \qquad
 q_m=g_m-g_0.
\]

If `S` has rows `alpha_m` and `rank S(x)=d`, then `b(x)=S(x)^\dagger q(x)`.

**Proof.** Expand `Delta rho_m/rho_m` as
`Delta log rho_m + ||grad log rho_m||^2`, then subtract the two scalar equations. Full column rank gives the unique
linear-algebraic solution.

**Scope.** This is a strong, population-level formula. It differentiates each density twice, assumes a common
known diffusion and says nothing about finite-sample stability. It is an elementary Fokker--Planck rearrangement,
not a headline theorem.

## T2 — exact ambiguity-current characterization

Let `b` and `b_tilde` be two admissible common drifts that, under the same diffusion and the same known additive
fields `u_m`, have the same positive stationary densities `rho_m`. Put

\[
 \delta b=\widetilde b-b,
 \qquad
 j=\rho_0\delta b,
 \qquad
 r_m=\rho_m/\rho_0.
\]

At the stationary-PDE level, the two drifts are observationally equivalent if and only if

\[
 \nabla\!\cdot j=0,
 \qquad
 j\!\cdot\!\nabla r_m=0
 \quad(m=1,\ldots,K),
\]

together with the declared boundary and admissibility conditions. Equivalently, every density ratio is a first
integral of the baseline-weighted ambiguity current.

**Proof.** Subtracting the two stationary equations in environment `m` gives
`div(rho_m delta b)=0`. The baseline equation is `div j=0`. Since `rho_m delta b=r_m j`,

\[
 \nabla\!\cdot(r_mj)=r_m\nabla\!\cdot j+j\!\cdot\!\nabla r_m
 =j\!\cdot\!\nabla r_m.
\]

This proves necessity. The same calculation in reverse proves sufficiency for preservation of every stationary
PDE. Existence or unique ergodicity of the modified process must still be checked inside the admissible model
class.

For a closed oriented `d`-manifold with volume form `mu`, if `K=d-1` and the density ratios are independent
somewhere, the Nambu current defined by

\[
 \iota_j\mu=dr_1\wedge\cdots\wedge dr_{d-1}
\]

is divergence free, tangent to every ratio level set and nonzero somewhere. Thus
`delta b=j/rho_0` is an explicit nontrivial ambiguity whenever it remains admissible.

**Prior-art status.** Liu and Liu characterize the single-density ambiguity as a density-weighted
divergence-free current. The fact that ratios of two multipliers are first integrals is classical Jacobi-last-
multiplier theory, and divergence-free flows represented by integral invariants are standard Nambu mechanics.
Their conjunction is a useful exact diagnostic but V11-C1 is `RETIRED_PRIOR_ART`.

## T3 — coordinate-invariant excitation operator

Raw Euclidean singular values of `S` depend on the coordinate chart. Let `A_x:T_x^*M -> T_xM` be a declared
positive-definite diffusion co-metric and let `w_m>0` be fixed environment weights. Define

\[
 \mathcal F_x v
 =\sum_{m=1}^K w_m\,\alpha_m(v)\,A_x\alpha_m,
 \qquad
 \alpha_m=d\log(\rho_m/\rho_0).
\]

Then `F_x` is positive semidefinite and self-adjoint in the metric induced by `A_x^{-1}`. Its rank is the span
rank of the score-difference covectors. Under a smooth coordinate change with Jacobian `J`,

\[
 A_y=JA_xJ^\top,
 \qquad
 \alpha_{m,y}=J^{-\top}\alpha_{m,x},
 \qquad
 \mathcal F_y=J\mathcal F_xJ^{-1}.
\]

The eigenvalues of `F_x`, unlike raw chart singular values, are therefore coordinate invariant after the physical
diffusion metric and environment weights have been declared.

**Scope.** This is standard tensorial preconditioning/frame geometry. The eigenvalues still depend on the chosen
physical diffusion tensor and environment weights. It corrects the coordinate claim falsified by Experiment 152;
it is not currently treated as a novelty contribution.

## T4 — exact-coframe obstruction and immersion dimension

Let `M` be a nonempty closed smooth `d`-manifold with `d>=1`, and let `rho_0,...,rho_K` be positive smooth
densities. Define the density-ratio map

\[
 R:M\longrightarrow\mathbb R^K,
 \qquad
 R(x)=\bigl(\log(\rho_1/\rho_0),\ldots,
              \log(\rho_K/\rho_0)\bigr).
\]

The pointwise score-difference rank is `d` everywhere if and only if `R` is an immersion. On compact `M`, this is
also equivalent to a strictly positive uniform minimum eigenvalue of the intrinsic frame operator in T3.

Consequently:

1. `K<d` can never give pointwise full rank;
2. `K=d` can never give pointwise full rank on a closed manifold; and
3. the smallest `K` for which *some abstract positive density family* can give pointwise full rank is exactly the
   Euclidean immersion dimension `imm(M)`.

Thus any uniformly stable pointwise strong-tomography design on a closed state manifold needs at least `d+1`
nonbaseline densities, or at least `d+2` total environments. This is one more than the naive local equation count.

**Proof.** The differential `dR` has rows `alpha_m`, proving the first equivalence. If `K=d` and `dR` were full
rank, the inverse-function theorem would make `R` a local diffeomorphism and hence an open map. Its image would be
both nonempty open and compact in connected noncompact `R^d`, a contradiction. For the final statement, any such
density family supplies an immersion and hence `K>=imm(M)`. Conversely, if
`F=(f_1,...,f_K):M -> R^K` is an immersion, choose any positive `rho_0` and set

\[
 \rho_m=\frac{e^{f_m}\rho_0}{\int_M e^{f_m}\rho_0}.
\]

Then `d log(rho_m/rho_0)=df_m`, so the resulting ratio map is an immersion.

**Critical limitation.** The converse constructs an abstract family of densities. It does not show that a fixed
set of feasible additive controls, chosen without knowing `b`, induces those densities. More importantly, failure
of pointwise rank at one or more locations does not by itself prove failure of *global* PDE identifiability: the
exact global criterion is the absence of nonzero admissible currents in T2. T4 therefore obstructs uniformly
conditioned pointwise inversion, not every possible global estimator.

An exact circle witness makes the distinction sharp. On `S^1`, take `rho_0` uniform,
`rho_1 proportional to exp(a cos x)` with `a` nonzero, baseline drift `b=0`, `u_0=0` and known
`u_1=kappa d log rho_1/dx`. Both densities are stationary. The one score difference vanishes at two points, as T4
requires, so the pointwise algebraic inverse is singular there. Yet a one-dimensional divergence-free current is
constant. T2 then gives `j r_1'=0`; because `r_1` is nonconstant, that constant must be zero. The common drift is
therefore globally unique despite unavoidable pointwise rank defects. Any stronger claim that the compactness
obstruction alone forces global non-identifiability is false.

## T5 — venue decision

The exact T4 connection was not located verbatim in the audited interventional-SDE or non-sequential-dynamics
sources, but it is an elementary differential-topology consequence and currently has no statistical lower bound,
feasible intervention-design algorithm or real-system witness. It remains `CONJECTURE` at the research-candidate
level, meaning that its mathematical proof is recorded but its novelty and paper value are not certified.

To advance beyond `V11_CONJECTURE_ONLY`, a human expert audit must first verify a nontrivial literature gap. The
candidate would then need at least one of:

- a global identifiability or minimax lower bound strictly stronger than the pointwise immersion obstruction;
- a feasible perturbation-design theorem that controls the intrinsic margin without knowing the target drift;
- a finite-sample estimator and rate not reducible to DyNoSeD, KDS, Stein/Galerkin or ordinary regularized inverse
  problems; or
- a calibrated real mechanism in which the topology-dependent count makes a frozen, independently replicated
  scientific prediction.

Until then, Experiment 153 and all remote/GPU work remain locked.
