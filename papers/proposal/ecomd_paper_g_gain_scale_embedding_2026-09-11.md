# Paper G — column gains and cyclic scale interventions

PRIVATE / INTERNAL. Source and reduction audit; not an original method claim.
Session 23 started 2026-09-10T19:18:27Z (07:18 NZST September 11).
Previous goal turn: progress. Decision: **not_trigger**.

## Why this comparison matters

The known-gain records distinguished outgoing-column modulation with unchanged
innovations from scaling an entire structural mechanism. Those formulas differ
in the original observed coordinates. This audit establishes that the difference
alone is not an irreducible model-class or information advantage: an invertible
observation transformation works for nonzero gains, and a deterministic relay
representation covers zero gains without deleting observations.

This addresses the existing feedback-identification lineage, not a new candidate
or a variant of the preceding two-channel score calculation. Its purpose is to
settle a parent-model comparison before spending effort on a proposed method.

## Primary-source scope

[Saha, Rathore and Garain, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/file/bc766279695d2333e91963b2997172e6-Paper-Conference.pdf),
Definition 1, permits mechanisms depending on shared primitive exogenous
variables, whose joint law is a product. Definition 8 replaces a selected
mechanism by its scaled value plus a shift. Theorems 1–2 give simplicity and
twin-model solvability under global contraction and scales of absolute value
at most one. PDF pages 2, 4 and 6 were visually inspected; the selected theorem
and definition passages were read. Their solvability conclusion does not assert
identification of unknown mechanisms from equilibrium samples. No estimator,
empirical result or full-paper proof audit is imported here.

## 1. Nonzero gains: equivalent observed experiments

Retain the existing equilibrium model

\[
Y_D=\Phi D Y_D+\varepsilon,
\quad \varepsilon=LE,\quad E\sim N(0,I),\quad LL^T=K^{-1}.
\]

`D` is a known diagonal gain matrix, `K` is common across arms, and solutions
exist uniquely on the specified parameter/gain class. Define `Z_D=D Y_D`.
Then

\[
Z_D=D(\Phi Z_D+LE).
\]

This is exactly a zero-shift scale intervention on the base mechanism
`f(z,E)=Phi z+LE`. Correlated effective innovations do not contradict a product
law for primitive noise: different mechanisms may share components of `E`.
This representation does not make `L` known or remove its estimation nuisance.

When every gain is nonzero, `(D,Y_D)` and `(D,Z_D)` determine each other through
a parameter-independent map. For a fixed observed arm,

\[
p_\vartheta^Z(z\mid D)
=p_\vartheta^Y(D^{-1}z\mid D)|\det D|^{-1}.
\]

Hence likelihood ratios and KL divergences are identical, and Fisher information
is identical wherever the scores exist. Identification or nonidentification of
the same structural parameter therefore transfers between these experiments.
Numerical conditioning and a particular estimator's implementation need not be
identical. Merely comparing the left and right positions of `D` misses this
statistical equivalence.

Outcome targets must also be transformed. For example, a physical-coordinate
contrast is `D1^-1 Z_D1-D0^-1 Z_D0`, not generally `Z_D1-Z_D0`. If a structural
model stipulates shared primitive noise across worlds, the blockwise map
preserves that joint law. It does not identify a cross-world coupling from
observed marginals when the coupling was previously unknown.

## 2. Zero gains: retain the original observation

The preceding inversion fails at a zero gain. In particular `D=0` leaves
`Y_0=epsilon`, while `Z_0=0` loses the noise observation. Ignoring this case would
erase the earlier zero-gain reference experiment.

A deterministic relay avoids that loss. Use endogenous variables `(Y,U)` and
base equations

\[
Y=\Phi U+LE,\qquad U=Y.
\]

Apply the source's scale intervention only to the relay equations:

\[
U=D Y.
\]

Eliminating `U` gives the original model for every diagonal `D`, including zeros.
For any solution `Y`, `(Y,DY)` is the corresponding augmented solution, and
projection onto `Y` is the inverse on this support. Observing the relay supplies
no new information: it is a known deterministic function of the retained data.
The same bijection holds for the solution set even before uniqueness is assumed.

The augmented joint distribution is generally singular in its `2n`-dimensional
ambient space. The cited structural solvability framework permits deterministic
mechanisms; this observation does not license transfer of a separate learning
algorithm that requires full-dimensional densities, faithfulness, or independent
node-specific disturbances.

## 3. A sufficient embedding inside the cited contraction theorem

Algebraic representation alone does not verify the source theorem's hypotheses.
Fix a finite bound `M>0` with `max_i |g_i|<=M` throughout the proposed gain family.
Restrict the parameter class by `M ||Phi||_p<=r_bar<1` in an induced `ell_p`
norm. Choose one fixed `c` with `r_bar<c<1` for the entire class, and base mechanisms

\[
f_Y(Y,W,E)=\frac{M}{c}\Phi W+LE,
\qquad f_W(Y,W,E)=cY.
\]

The base endogenous Lipschitz constant is at most

\[
\max\{M\|\Phi\|_p/c,c\}\leq\max\{r_{\rm bar}/c,c\}<1.
\]

Scaling relay coordinate `W_i` by `g_i/M` has absolute value at most one and
gives `W=(c/M)DY`. Substitution again yields `Y=Phi D Y+LE`.
On full Euclidean coordinate domains this verifies the relevant global
contraction and self-map assumptions. The source's simple/twin-solvability
conclusion thus applies to this explicitly bounded subclass, including zero,
negative and magnitude-greater-than-one original gains after normalization.
Using one fixed `c` avoids a parameter-dependent transformation of the observations.

The two-arm observational-equivalence curve from the preceding session has
`Phi_theta ->0`. With its finite gain bound `M=3`, sufficiently small `theta`
therefore lies inside this subclass. Its nonidentification is fully compatible
with unique structural solutions: the competing mechanisms each have a unique
solution while inducing the same observed law.

This condition is sufficient and stronger than mere invertibility of
`I-Phi D`. No general noncontractive stability theorem, gain-uniform learning
bound or necessity of this norm condition is claimed. The constants here are
analytical; no numerical contraction calculation was performed.

## 4. What is settled, and what is not

The native untransformed action formulas remain different, but the outgoing-
versus-incoming label is not by itself a novelty barrier. Unknown correlated
noise and zero gains do not prevent structural embedding when handled as above.
The direct invertible transformation additionally preserves the exact statistical
experiment for nonzero gains; the relay representation preserves the original
observation at every gain.

This settles **model representation**, not the complete statistical problem.
The source's solvability theorems do not prove the preceding nuisance information
formula, a matching minimax rate, globally identifiable parameters, or uniformly
valid confidence sets. The two-arm ambiguity and the third-arm local positive
control remain valid. No claim is made that the cited paper already contains
those exact calculations.

All equivalences here concern fixed-gain equilibrium arms. Time-dependent
transients, finite settling times, delayed actuation, additional pre-window
moments, physical intervention costs and the interpretation of response targets
must retain their own contracts. Changing them is not a free extension of this
result or an authorized new candidate.

## Allocation

Retain the earlier closed route and the exact statistical controls. Any future
proposal must state an unoccupied statistical or physical result within or beyond
this SCM class, rather than rely on where a diagonal gain appears in a matrix formula.
Model inclusion alone does not dismiss a new efficient-learning or inference result.
Neither the representation nor its contraction rescaling is an independent Paper G.
No source-model disagreement, truth/control asset, route-level blocker removal,
new cycle or execution authority is established. Stop this semantic-comparison
branch absent a qualified substantive trigger. The publication-level objective
remains unmet.
