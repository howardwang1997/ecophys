# Formal cards v12 — exact identification versus solenoidal stability

These cards distinguish exact population identification, unrestricted `L^2` coercivity and conditional
smoothness-aware stability. A proof does not imply novelty. The local ingredients overlap classical
`A`-free wave-cone, redundant inverse-PDE and Grushin/subelliptic theory.

## T1 — coordinate-free ambiguity operator

Let `M` be a connected closed oriented smooth `d`-manifold, `d>=2`, with smooth volume form `mu`. Let
`R=(R_1,...,R_K):M -> R^K` be the log-density-ratio map from V11. For a vector field `j`, define

\[
 T_Rj=dR(j).
\]

The common-drift ambiguity equations are

\[
 \mathop{\rm div}_{\mu}j=0,
 \qquad T_Rj=0.
\]

Equivalently, with the `(d-1)`-form `beta=i_j mu`,

\[
 d\beta=0,
 \qquad dR_m\wedge\beta=0\quad(m=1,\ldots,K).
\]

The second equivalence follows from

\[
 dR_m\wedge i_j\mu=dR_m(j)\mu.
\]

This is an exact stationary-PDE statement. It does not assert that every modified drift remains inside a smaller
parametric model, is nonexplosive, or induces a unique ergodic diffusion.

## T2 — uniform solenoidal stability is exactly immersion

Fix Riemannian metrics on `M` and `R^K` and set

\[
 \gamma(R)=
 \inf_{\substack{0\ne j\in C^\infty(TM)\\ \mathop{\rm div}_{\mu}j=0}}
 \frac{\lVert dR(j)\rVert_{L^2}}{\lVert j\rVert_{L^2}}.
\]

Then

\[
 \gamma(R)>0
 \quad\Longleftrightarrow\quad
 R\text{ is an immersion}.
\]

**Immersion implies stability.** The smallest singular value of `dR_x` is a positive continuous function on
compact `M`, so it has a positive minimum. Integrating the resulting pointwise inequality proves coercivity.

**A critical point destroys stability.** Suppose `dR_p v=0` for a unit vector `v`. Choose volume coordinates
`x=(x_1,...,x_d)` centered at `p` with `mu=dx` and `v=e_1`. For fixed nonzero smooth compactly supported bumps,
set

\[
 \psi_\varepsilon(x)=A_\varepsilon
 \phi(x_1/\varepsilon)\chi(x_2/\varepsilon^2)
 \prod_{q=3}^d\eta_q(x_q/\varepsilon),
\]

\[
 j_\varepsilon=(\partial_2\psi_\varepsilon,-\partial_1\psi_\varepsilon,0,\ldots,0).
\]

After extension by zero, this is a smooth exactly divergence-free field on `M`. Direct rescaling gives

\[
 \lVert (j_\varepsilon)_2\rVert_2
 \le C\varepsilon\lVert (j_\varepsilon)_1\rVert_2.
\]

The support lies within `O(epsilon)` of `p`; hence smoothness and `dR_p(e_1)=0` give

\[
 \lVert dR_x(e_1)\rVert\le C\varepsilon
 \quad\text{on the support}.
\]

Consequently, after normalizing `||j_epsilon||_2=1`,

\[
 \lVert T_Rj_\varepsilon\rVert_2\le C\varepsilon\longrightarrow0.
\]

For every nonnegative integer `s`, the same construction satisfies

\[
 \lVert j_\varepsilon\rVert_{H^s}\le C_s\varepsilon^{-2s}.
\]

The anisotropic scale `x_2=O(epsilon^2)` is essential: it makes the transverse correction required by exact
incompressibility the same order as the loss of sensitivity in the kernel direction.

**Prior-art status.** For the divergence operator in dimension at least two, every vector amplitude belongs to
the `A`-free wave cone because one can choose a nonzero frequency perpendicular to it. Localized solenoidal waves
and rigidity away from a wave cone are established machinery. T2 is therefore retained as a tailored lemma, not
as an independent novelty claim.

## T3 — exact nonidentification below dimension

If `K<d`, then there exists a nonzero smooth field `j` satisfying

\[
 \mathop{\rm div}_{\mu}j=0,
 \qquad dR(j)=0.
\]

Thus an unrestricted smooth common drift is not identified at the stationary-PDE level.

Let `r=max_x rank(dR_x)`.

**Case `r=d-1`.** Select `d-1` components `f_1,...,f_{d-1}` of `R` whose differentials are independent somewhere
and define

\[
 \beta=df_1\wedge\cdots\wedge df_{d-1}.
\]

This form is closed and nonzero. Since the rank of all component differentials is never larger than `d-1`,
`dR_m wedge beta=0` everywhere. The field defined by `i_j mu=beta` is the required ambiguity.

**Case `r<=d-2`.** On a relatively compact constant-rank chart `U`, choose independent component functions
`f_1,...,f_r` and coordinates `(f,y)` supplied by the constant-rank theorem. Every component of `R` is locally a
function of `f`. With `n=d-r>=2`, choose a nonzero compactly supported closed `(n-1)`-form `gamma` in the `y`
coordinates, for example `gamma=d eta` for a compactly supported `(n-2)`-form `eta`. Choose a compactly supported
smooth `h(f)` and set

\[
 \beta=h(f)\,df_1\wedge\cdots\wedge df_r\wedge\gamma.
\]

It is closed, compactly supported in `U`, nonzero and wedges to zero with every `dR_m`. Extending it by zero and
using `i_j mu=beta` completes the proof. The construction also covers `r=0`.

This result is an exact global threshold for unrestricted smooth ambiguity fields. It is stronger than a
pointwise equation count, but its differential-form ingredients are elementary Hodge/Nambu geometry.

## T4 — the equal-count identification/stability gap

Let `K=d`. A residual set of maps `R` in the Whitney `C^infty` topology is transverse to the rank strata of the
one-jet bundle. Its critical set is consequently a positive-codimension stratified set and has zero volume, while
`dR` is invertible almost everywhere. Therefore

\[
 T_Rj=0\text{ in }L^2
 \quad\Longrightarrow\quad j=0\text{ almost everywhere}.
\]

The common drift is generically exactly identified in the unrestricted `L^2` ambiguity space. On the other hand,
no map from a nonempty closed `M^d` to `R^d` is an immersion, so T2 gives

\[
 \gamma(R)=0.
\]

Every smooth map to `R^d`, up to irrelevant componentwise constants, can be realized as a log-density-ratio map:
for any positive baseline `rho_0`, take `rho_m proportional to exp(R_m)rho_0`. Thus the genericity statement is
valid for abstract positive density families. It is not a claim about density families reachable through a fixed
physical actuator.

Combining T3, T4 and V11's immersion construction yields three abstract regimes:

| Nonbaseline densities | Population result for unrestricted smooth drifts |
|---|---|
| `K<d` | nonidentified |
| `K=d` | generically identified, never uniformly `L^2` stable on closed `M` |
| `K>=imm(M)` | some abstract density family is uniformly stable |

For `d<K<imm(M)`, exact identification can occur but abstract uniform stability cannot. The table is not an
actuator-achievability theorem.

## T5 — sharp conditional stability in the two-dimensional fold chart

Consider the standard fold

\[
 R(x,y)=(x^2/2,y)
\]

on `R^2`, and a compactly supported smooth divergence-free field `j=(j_1,j_2)`. Define

\[
 E(j)^2=\lVert xj_1\rVert_2^2+\lVert j_2\rVert_2^2
 =\lVert dR(j)\rVert_2^2.
\]

For `s>0`, an anisotropic Grushin estimate and interpolation give

\[
 \lVert j\rVert_2
 \le C_s\left\{E(j)+E(j)^{\frac{2s}{2s+1}}
 \lVert j\rVert_{H^s}^{\frac{1}{2s+1}}\right}.
\]

To see the subelliptic step directly, Fourier transform in `y`. The zero-frequency component of `j_1` vanishes by
compact support. For frequency `xi != 0`, divergence freedom gives
`partial_x hat(j_1)+i xi hat(j_2)=0`. The one-dimensional harmonic-oscillator inequality implies

\[
 \int\left(x^2|\widehat j_1|^2+|\widehat j_2|^2\right)dx
 \ge |\xi|^{-1}\int|\widehat j_1|^2dx.
\]

Hence the observation controls a negative half derivative of `j_1`; interpolation between that norm and `H^s`
gives the displayed exponent. The directly observed `j_2` contributes the first term.

The exponent is sharp in scaling. The normalized stream-function family from T2 obeys

\[
 E(j_\varepsilon)\asymp\varepsilon,
 \qquad
 \lVert j_\varepsilon\rVert_{H^s}\asymp\varepsilon^{-2s}.
\]

Thus no stronger homogeneous interpolation exponent can hold for the standard fold. With an `H^s` radius `L`
and deterministic observation error `delta`, the corresponding modulus scales as

\[
 L^{1/(2s+1)}\delta^{2s/(2s+1)}.
\]

This is a conditional deterministic inverse bound, not yet a minimax theorem for stationary samples. Density and
score estimation error, dependence, unknown diffusion and admissibility of both SDEs remain outside the card.

**Prior-art status.** The fold energy is the classical Grushin sum-of-squares geometry. Subelliptic estimates and
sharp concentrating quasimodes are established. The inverse-SDE interpretation and the three-regime synthesis
were not located verbatim, but the mathematical rate mechanism by itself is not a novelty pass.

## T6 — higher singularities remain conjectural

For a corank-one normal form whose invisible derivative vanishes to order `q`, the same scaling argument predicts

\[
 x_2=O(\varepsilon^{q+1}),
 \qquad
 \lVert dR(j_\varepsilon)\rVert_2=O(\varepsilon^q),
 \qquad
 \lVert j_\varepsilon\rVert_{H^s}=O(\varepsilon^{-(q+1)s}),
\]

and the conditional exponent

\[
 \frac{(q+1)s}{(q+1)s+q}.
\]

This is `CONJECTURE`, not a theorem. Generic equal-dimensional maps may contain folds, cusps and higher
Thom--Boardman strata depending on dimension and stability notion; a global rate also depends on how these strata
interact. No claim may replace that stratified analysis by the statement “generic means fold everywhere.”

## T7 — venue disposition after the equation proof

T2--T5 give a clean exact/conditional theorem package, but the current contribution is mostly a synthesis of
known primitives:

- stationary Fokker--Planck ambiguity and ratio first integrals;
- localized divergence-free `A`-free waves;
- generic rank-stratum transversality and immersion theory; and
- Grushin subellipticity plus interpolation.

V12 therefore closes as `V12_THEOREM_ONLY`. The theorem package remains `CONJECTURE` at the research-candidate
level pending an independent human novelty/value audit; this label does not mean its displayed lemmas are unproved.
It is not an admitted NMI or NCS project.
An NMI route would require a nonstandard finite-sample theorem or feasible intervention-design algorithm that is
not ordinary Tikhonov regularization of a Grushin inverse problem. An NCS route additionally requires controlled
real-system interventions and a prospectively replicated mechanism. No worker, GPU, generated sample or market
dataset is justified by these cards.
