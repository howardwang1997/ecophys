# Plan v12 — Solenoidal excitation gap between drift identification and stable recovery

**Frozen:** 2026-08-13

**Branch:** `global-drift-identifiability-gap-audit-v12`

**Base:** `main@1106a339944e5598838c6b0192e8513b90445fd7`

**Initial state:** `EQUATION_AUDIT`; no generated sample, real-system outcome, market file, remote host or GPU is
authorized before the theorem and prior-art gates below

## 1. Why V12 exists

V11 found a real distinction that its pointwise formula could not resolve. On a closed state manifold, a
density-ratio map with `d` outputs must have critical points, so a pointwise inverse is singular somewhere. Yet an
exact circle example is globally drift-identifying because the stationary continuity equation couples those
singular points to the rest of the state space.

V12 asks whether this gap has a sharp operator-theoretic form:

> When do multiple stationary densities identify the common drift exactly, and when do they identify it with a
> uniform stability margin against divergence-free ambiguity currents?

The target is a general inverse-problem theorem, not a new name for V11's Fokker--Planck subtraction and not a
claim about EcoMD or market physics.

## 2. Frozen mathematical object

Let `M` be a connected closed oriented smooth `d`-manifold, `d>=2`, with a declared smooth volume form `mu`. Let
`rho_0,...,rho_K` be positive smooth stationary densities induced by known perturbations of a common-drift
diffusion. Define

\[
r_m=\rho_m/\rho_0,
\qquad
R=(\log r_1,\ldots,\log r_K):M\to\mathbb R^K.
\]

V11 proved that a common-drift ambiguity can be represented by a current `j` satisfying

\[
\operatorname{div}_{\mu}j=0,
\qquad
dR(j)=0.
\]

Let `H_div` be the `L^2(mu)` closure of smooth divergence-free vector fields and define the solenoidal excitation
operator and its lower modulus

\[
T_R:H_{\rm div}\to L^2(M;\mathbb R^K),
\qquad
T_Rj=dR(j),
\]

\[
\gamma(R)=\inf_{0\ne j\in C^\infty,\,\operatorname{div}_{\mu}j=0}
\frac{\lVert T_Rj\rVert_{L^2}}{\lVert j\rVert_{L^2}}.
\]

Exact population identification is `ker T_R={0}`. Uniform `L^2` stability is `gamma(R)>0`. These are deliberately
different gates.

## 3. Candidate theorem family

### V12-T1 — stability equals immersion

Candidate statement: for `d>=2`,

\[
\gamma(R)>0
\quad\Longleftrightarrow\quad
R\text{ is an immersion}.
\]

The forward direction is nontrivial only at a critical point. The intended attack constructs normalized smooth
divergence-free currents concentrated anisotropically near a kernel direction of `dR`, with
`||T_R j_epsilon||_2 -> 0`. The reverse direction follows from compactness and the positive minimum singular value
of `dR` in a declared metric.

### V12-T2 — sharp environment regimes on closed state spaces

Conditional on T1 and standard transversality:

1. if `K<d`, a nonzero smooth divergence-free current tangent to all ratio levels should exist, so the drift is
   not identified;
2. if `K=d`, a generic smooth density-ratio map has full rank on a dense open set, hence `ker T_R={0}`, but no map
   from closed `M^d` to `R^d` is an immersion, hence `gamma(R)=0`;
3. stable recovery is abstractly possible first at `K=imm(M)`, the Euclidean immersion dimension of `M`, though
   achievability by feasible drift perturbations is a separate control problem.

This would give a one-regime gap between generic exact identification and stable inversion, with a
topology-dependent stable-environment count.

### V12-T3 — conditional statistical consequence

A viable NMI theorem must go beyond the unrestricted `L^2` lower modulus. It must quantify how the near-kernel
construction interacts with a declared Sobolev/Hölder drift class and observation error. An acceptable endpoint is
one of:

- a minimax lower bound showing the rate loss caused by a generic fold singularity;
- a regularized global estimator with a matching rate and a topology/criticality-dependent condition number; or
- a perturbation-design guarantee that increases a coordinate-invariant global margin without presupposing the
  unknown drift or desired stationary densities.

Without T3, T1/T2 may remain a short inverse-problem note rather than an NMI contribution.

## 4. Non-claims fixed at freeze

- V12 does not claim the ambiguity-current identity, density ratios as first integrals, Hodge/Nambu currents,
  transversality, immersion theory or stationary Fokker--Planck inversion as new primitives.
- `gamma(R)=0` is not finite-sample impossibility under every smoothness class. The localized currents may have
  growing derivatives, which must be accounted for explicitly.
- Genericity over arbitrary positive density families is not genericity over densities achievable by a fixed
  physical actuator.
- Exact drift identification does not validate the assumed state, common diffusion, intervention semantics or
  stationarity.
- EcoMD, current market regimes and synthetic SDE fixtures cannot serve as NCS evidence.

## 5. Mandatory prior-art attack

The audit must place T1--T3 beside:

- inverse invariant-measure and stationary Fokker--Planck identification, especially Liu--Liu and DyNoSeD;
- KDS/Stein/Galerkin formulations of stationary generators;
- Jacobi last multipliers, inverse Jacobi multipliers, Hodge decomposition and generalized Nambu currents;
- closed-range/coercivity results for multiplication or first-order constrained operators;
- localized solenoidal quasimodes, compensated compactness and degenerate elliptic inverse problems;
- Thom jet transversality, generic maps between equal-dimensional manifolds and immersion dimension; and
- statistical inverse-problem rates near fold or vanishing-design singularities.

Keyword absence is not a novelty result. T1 is retired if it is a direct named theorem or if its proof has no
consequence beyond an ordinary smallest-singular-value observation.

## 6. Proof obligations and kill tests

### P0 — ambiguity-space correctness

- Specify the Hilbert domain, volume form, boundary-free setting and density-to-current conversion.
- Separate the kernel criterion from existence/ergodicity of every modified SDE.
- **Kill:** stop if the proposed operator does not represent all admissible common-drift differences.

### P1 — localized divergence-free quasimode

- Construct `j_epsilon` in a coordinate chart at an arbitrary critical point.
- Prove exact divergence freedom, unit `L^2` normalization and `||dR(j_epsilon)||_2 -> 0`.
- Track anisotropic support and derivative growth rather than relying on a picture.
- **Kill:** retire T1 if incompressibility forces an `O(1)` observed component or the construction needs a
  nongeneric critical normal form.

### P2 — sharp exact-identification regimes

- Prove a nonzero tangent divergence-free current for `K<d`, including variable-rank maps.
- Prove dense full rank suffices for zero smooth kernel.
- State the exact genericity topology and use an appropriate transversality theorem for `K=d`.
- **Kill:** do not call the threshold sharp if one of the nonidentification or generic-identification directions is
  missing.

### P3 — statistical and control meaning

- Bound the Sobolev/Hölder norm of the quasimodes and derive a noise-versus-resolution lower bound.
- Distinguish an abstract density immersion from stationary densities induced by feasible known controls.
- **Kill:** no NMI route if regularization reduces T3 to standard degenerate-design inverse regression with no new
  theorem, estimator or design rule.

### P4 — scientific observability

- Require quantitative perturbation vector fields, independently checked stationary ensembles and a frozen unseen
  intervention.
- **Kill:** no NCS route without a real controlled mechanism and independent replication.

## 7. Authorized zero-cost work

Before a human novelty audit, work is limited to primary-source reading, symbolic proofs and deterministic local
coordinate calculations on the Mac in the `ecophys` Conda environment.

If T1/T2 survive equation-level prior art, Experiment 154 may be separately preregistered as an exact deterministic
scaling audit. It may check analytic fold charts, divergence-free current normalization and predicted residual/
smoothness exponents. It may not use random training samples, neural estimators, real data or favorable-case
sweeps. Experiment 153 remains locked under the V11 decision and is not repurposed.

## 8. Data requirements

| Tier | Data | Admission condition |
|---|---|---|
| T0 current | Primary-source text, exact charts, hand-specified smooth functions and symbolic constants only. | Plan frozen; no outcome computation. |
| T1 theorem stress | Immutable deterministic fixtures, then generated stationary samples only if a statistical T3 survives and a new experiment is preregistered. | T1/T2 human audit and exact proof checks. |
| T2 NMI | At least two structurally distinct controlled non-financial systems, quantitative perturbation fields, repeated stationary ensembles and held-out interventions. | Non-equivalent estimator/rate already established. |
| T3 NCS | A real system with a substantive recovered non-gradient mechanism, independent stationarity checks and frozen cross-system/intervention replication. | Method is publishable without the application. |

No current EcoMD, LOBSTER, Binance, prediction-market or blockchain-controller data satisfy T2/T3.

## 9. Compute requirements

| Tier | CPU | GPU | Worker policy |
|---|---:|---:|---|
| T0 proof/prior art | <=20 core-hours | 0 | Mac only; do not contact workers. |
| conditional Exp154 | <=50 core-hours | 0 | Mac CPU only. |
| conditional finite-sample T1 | <=1,000 core-hours | <=50 V100-equivalent hours | Two V100 32 GB workers only after a new preregistration; RTX2060 for smoke/CPU jobs. |
| NMI validation | 2,000--20,000 core-hours | 200--2,000 V100-equivalent hours | May expand to heterogeneous non-H20 pools after canonical V100 benchmarks. |
| NCS confirmation | 10,000--100,000 core-hours | 2,000--20,000 V100-equivalent hours | Capacity/data may expand behind gates; no H20 assumption. |

More compute cannot establish closed range, novelty, feasible intervention semantics or real stationarity.

## 10. Venue and decision rules

- **NMI:** requires T3, a usable non-equivalent method and cross-domain validation. T1/T2 alone are insufficient.
- **NCS:** requires the NMI-grade computational object plus a new prospectively replicated scientific mechanism.
- **Mathematical/specialist fallback:** may be assessed only after the NMI/NCS audit closes; it cannot be used to
  weaken claims while inspecting outcomes.

Pre-audit flagship probability is low: approximately `3--8%` for NMI and below `1%` for NCS in the current form.
The exact theorem family could still be valuable even if those routes fail, but automation may not issue a
novelty pass.

## 11. Chronology

1. Commit and push this plan before formal proof cards, Experiment 154 preregistration or scaling outcomes.
2. Complete P0--P2 and equation-level prior art before any generated sample or worker contact.
3. Append rather than overwrite V1--V11 graph history and failure lessons.
4. Close as `V12_NO_SURVIVOR_PRIOR_ART`, `V12_NO_SURVIVOR_PROOF`, `V12_THEOREM_ONLY`,
   `V12_CONJECTURE_ONLY` or `V12_READY_FOR_HUMAN_AUDIT`.
5. Synchronize graph, ledgers, lineage, memory and dated logs before integration into `main`.
