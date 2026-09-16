# Paper G — finite local sampling and restricted flow states

PRIVATE / INTERNAL. Paper-only scope resolution; not public scientific evidence.
Session 21 started 2026-09-10T18:53:42Z (06:53 NZST September 11).
Previous goal turn: progress. Decision: **not_trigger**; retain the route closure.

## Decision-relevant question

The flux/locality audit left finite-grid observability unproved. Can two distinct
members of the cited initialization family agree on the declared local input
samples, so that an exterior-response twin would be valid within that family?
For exact initialization samples, **no**: a 5-by-5 tensor subgrid suffices to
identify both global velocity fields. This strengthens the earlier warning
against treating an unrestricted remote-bump control as a matched-distribution
counterexample. It does not establish why any trained network performs well.

Repository connection: Paper D studies the attribution of neural-PDE constraints;
the existing Paper G flux/locality audit examines the distinct claim that a
conserving/local architecture represents a local physical response. No Paper D
outcomes are used. This is a follow-up to an explicit unresolved sampling-rank
statement, not another candidate cycle or archive expansion.

## Source contract

[Ye, Li and Yan, arXiv2504.09807v1](https://arxiv.org/html/2504.09807v1),
Sections 2.1–2.3, specifies initial density and temperature equal to one, and
each velocity component as `0.6 b(x)^T Lambda b(y)`, where

\[
b(s)=(\sin\pi s,\sin2\pi s,\cos\pi s,\cos2\pi s)^T.
\]

Each `Lambda` has 16 Gaussian coefficients. The periodic square is `[-1,1]^2`,
grid spacing is `1/64`, and the stated unit input/output widths are 54/6 grid
points. Training also uses randomly selected later times, not initialization
alone. All four physical fields are inputs. These are article-specified
conditions, not independently inspected arrays, architecture code or outputs.

## 1. Exact finite-grid rank

Choose five distinct coordinates modulo period two in each direction from the
declared input rectangle. For example, offsets `0,13,26,39,52` fit within its
54 grid points. Let `B_x[i,:]=b(x_i)^T`, and define `B_y` likewise.

**Lemma.** Each 5-by-4 matrix has column rank four.

Proof: a null coefficient vector would give a real trigonometric polynomial
with frequencies `+/-1,+/-2` vanishing at five distinct points. With
`z=exp(i pi s)`, multiply its Laurent representation by `z^2`. The resulting
polynomial has degree at most four and five distinct roots, hence is zero.
Linear independence of the Fourier coefficients gives the claimed rank.

For either velocity, its 5-by-5 sample matrix is

\[
U=0.6 B_x\Lambda B_y^T,
\qquad
\Lambda=\frac1{0.6}B_x^\dagger U(B_y^\dagger)^T.
\]

The tensor observation map has rank 16; both velocities together identify all
32 real initialization coefficients. Density and temperature are fixed.
Thus any deterministic later target with a well-defined evolution is a
function of this initial patch on the specified family. This is an existence
statement, not an efficient learned decoder or proof that the actual architecture
can express or has learned the decoder. The declared full input rectangle is
the observation here; no per-neuron receptive-field audit was performed.

In particular, no distinct exact members of this initial family can agree on
that patch even before imposing equal global invariants. Adding an energy or
momentum condition cannot create such a pair. Arbitrary smooth exterior bumps
belong to a different family, as the earlier audit correctly stated.

## 2. Linearized later states do not require an observed clock

For the continuum equations linearized at uniform positive rest, constant
coefficients imply Fourier-mode decoupling:

\[
\widehat v_k(t)=\exp(tA_k)\widehat v_k(0).
\]

The initialization uses only `k_x,k_y in {+/-1,+/-2}`. Linear evolution preserves
this spatial mode support in every field. Applying the same tensor interpolation
to all four observed perturbation fields recovers the full current linearized
state. Its next-time target is consequently determined by the current patch,
even when the current time is not supplied. This is an exact observation claim
for the linearized continuum model, not a finite-amplitude compressible-flow
result or a statement about the paper's FEM/RK4 data generator.

For each finite time, `exp(t A_k)` is invertible. Together with patch sampling,
this also makes the derivative from the 32 initial coefficients to the local
four-field observation injective at rest. No spectral stability claim is needed
for this finite-time matrix-exponential fact.

## 3. What transfers conditionally to nonlinear evolution

Fix an observation time `t` and a target time `t+Delta`. Assume the continuum
solution exists on that interval in a regularity class with a continuously
differentiable map from the finite initialization coefficients to the sampled
fields. This is a stated analytical hypothesis; no source-specific uniform
existence or stability constants are certified here.

At zero velocity, the observation derivative has rank 32 by the preceding
linearized argument. Select 32 scalar observation coordinates with a nonsingular
minor. The inverse-function theorem gives a neighborhood of zero coefficients
on which those observations recover the coefficients. The nonlinear future
target therefore factors through the local patch on this neighborhood.

Limits are material: the neighborhood may depend on `t`, horizon and the chosen
minor. The result neither covers all Gaussian initial draws nor supplies a
uniform noise tolerance. Nonlinear evolution generates additional harmonics,
so direct Fourier interpolation no longer reconstructs the full state exactly.
For the paper's mixture of later times without an explicit time input, fixed-time
inverse maps cannot simply be merged: overlapping observation branches must be
checked. That mixed-time nonlinear identification question remains unresolved.
It is not automatically an attractive new topic.

## 4. Injectivity is not numerical robustness

If the initial sample matrix has perturbation `E`, the algebraic reconstruction
satisfies

\[
\|\widehat\Lambda-\Lambda\|_F
\leq\frac{\|E\|_F}{0.6\,\sigma_{\min}(B_x)\sigma_{\min}(B_y)}.
\]

The minimum singular values are positive by the proof. No numerical value,
practical conditioning threshold, roundoff accuracy or measured reconstruction
error is asserted. Contiguous versus spaced points change conditioning; neither
the grid count nor an analytic-continuation analogy settles it. A future-target
error bound additionally needs sensitivity of that target to the coefficients.

## Allocation and nonclaims

The exact finite-grid initialization question is resolved; the unrestricted
remote-bump example still supplies no same-family prediction contradiction.
The linearized result and conditional local inverse sharpen the scope at later
times without proving an empirical performance mechanism. Physical locality,
restricted-distribution predictability, architectural capacity and numerical
robustness remain distinct.

These are elementary interpolation, linearization and inverse-function
consequences. They do not establish a new algorithm, scientific-ML lower bound,
matched primary disagreement, practical model failure, or publication-level
contribution. No recorded blocker is removed. Retain the closed
`paper_g_numerical_teacher_continuum_ranking` route and stop this sampling-rank
follow-up. A further step must supply a nonstandard, decision-changing residual
under a matched state/observation/target contract; merely estimating this matrix's
condition number, adding another sampling pattern, or extending the same lemma
does not by itself qualify a Paper G re-entry.

No numerical linear algebra, scientific code, dataset, solver, training run,
confirmation outcome or new forecast was used. Source performance numbers visible
in the selected article passage are not used as Paper G evidence. Administrative
record checks do not verify mathematical correctness or novelty.
