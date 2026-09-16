# Paper G: same-information overlap reconstruction baselines

PRIVATE / INTERNAL — 2026-09-15. Analytic research decision record; excluded from public evidence.

The preceding rotating-subspace stress case does not establish an ML contribution. It admits an exact nonlearned reconstruction from its existing nearest-link label. More generally, nearest links leave a bounded residual ambiguity; a learner cannot remove that ambiguity uniformly without added information or assumptions. The concrete remaining target is transferable prediction of complementary-subspace correlations, compared against a diagonal-preserving landmark completion with a kinetic error certificate. No such transferable prediction advantage is established here. g41 remains parked.

This is a zero-new-source analytic follow-up to the [previous construction](ecomd_paper_g_overlap_metric_construction_2026-09-15.md) and the [earlier factor/landmark review](ecomd_paper_g_overlap_reduction_review_2026-09-14.md). Their source comparisons remain in force. No new literature or publication-novelty assertion is made.

## B1: exact repair on the declared rotating family

For u_n=(cos(anh),sin(anh)), q=cos(ah), the exact scalar overlap at grid separation k is a_k=cos(kah). Define

\[
a_0=1,\qquad a_1=q,\qquad a_{k+1}=2q a_k-a_{k-1}.
\]

The cosine addition identity proves this recurrence gives every exact overlap. It is the ordinary Chebyshev recurrence, not a new algorithm. It uses the same exact q as linked products q^k. For N equally spaced points, the N distinct separations cost O(N) recurrence operations; materializing a dense matrix still costs O(N²). The previously recorded rank-two factorization provides the corresponding compressed action, and the orthogonal second retained channel adds one rank. No quantum-chemistry query or training set beyond the existing q is required for this restricted family.

This immediately removes the previous phase error for any fixed kinetic discretization, because the reconstructed overlap itself is exact. A model that only beats linked products on this family would not demonstrate that learning is useful.

The hypothesis is essential: a common planar rotation with constant angle increment is declared in advance. Arbitrary molecular subspaces need not satisfy it. With noisy q, the sensitivity can grow as k² because |T_k'(q)|≤k² on [-1,1]. Thus this is an exact-label algebraic comparator, not a claim of uniform long-range stability. The identity a²≈2(1−q)/h² also shows why fixed absolute label noise is amplified when estimating curvature at smaller h. No empirical noise law or universal sample-complexity conclusion is inferred.

## B2: the exact three-node information boundary

Consider three real normalized retained states. Fix a gauge in which the two observed nearest overlaps are q, with 0<q<1. Their Gram matrix has the form

\[
A(r)=\begin{pmatrix}1&q&r\\q&1&q\\r&q&1\end{pmatrix}.
\]

Its determinant is (1−r)(1+r−2q²). Together with its principal minors, positive semidefiniteness is equivalent to

\[
2q^2-1\le r\le1.
\]

Both endpoints are attained by physical vectors in a real two-dimensional ambient space. Set q=cos(theta), u_0=e_1 and u_1=(cos(theta),sin(theta)). The continuation u_2=(cos(2theta),sin(2theta)) gives r=2q²−1; the return u_2=e_1 gives r=1. Both nearest links and all Gram diagonals agree. Their gauge-invariant triangular products q²r differ. At these three fixed geometries each construction can be smoothly interpolated and embedded into an electronic Hamiltonian with the same constant eigenvalues. This finite-grid statement does not assert identical derivative labels, identical known ambient Hamiltonians, or a uniformly smooth continuum pair at arbitrarily small h.

For any deterministic reconstruction rhat using only the declared shared labels,

\[
\sup_{r\in[2q^2-1,1]}|\widehat r-r|\ge1-q^2.
\]

The midpoint rhat=q² attains the bound. This is exactly the two-link product. For a fixed three-node Hermitian kinetic matrix with T_02 nonzero, the only unobserved pair contributes operator error |T_02| |rhat−r|, so the same midpoint is minimax for that specific operator-norm criterion. This does not establish minimax optimality for arbitrary graphs, observables, stochastic losses or molecular priors.

The result changes the interpretation of the preceding stress case. Linked products can be biased on the rotating subclass while remaining the strongest worst-case estimate in this less restricted three-node information class. Selecting the Chebyshev endpoint uses the declared rotation prior. A trained predictor could improve average error if its additional features or training distribution legitimately predict the residual alignment. It cannot claim a distribution-free improvement over the midpoint from identical information alone. One measured skip-edge r distinguishes the displayed pair; its acquisition cost must be included for every comparator.

## B3: a diagonal-preserving landmark baseline and certificate

Let A be a finite scalar electronic Gram matrix, Hermitian PSD with A_nn=1. For independent landmark columns L, suppose the complete columns B=A[:,L] and C=A[L,L] are known, with C positive definite. Define

\[
P=B C^{-1}B^\dagger,\quad R=A-P\succeq0,\quad v_n=R_{nn}=1-P_{nn}\ge0.
\]

These are the standard projection and Schur-complement identities. The residual obeys |R_nm|≤sqrt(v_n v_m). Bare approximate Nyström completion can change Gram diagonals; use instead

\[
\overline A=P+\operatorname{diag}(v).
\]

This baseline is PSD, has the exact unit diagonal and preserves all known landmark columns. It is generally an approximation, not a claimed reconstruction of the original finite-dimensional electronic embedding. Let the finite-grid Hamiltonian use H=E+T⊙A, with the same real diagonal potential E and Hermitian kinetic matrix T for both methods. The resulting error has zero diagonal and satisfies

\[
\|H-\overline H\|_2
\le\max_n\sum_{m\ne n}|T_{nm}|\sqrt{v_n v_m}.
\]

Proof: off-diagonal error entries are T_nm R_nm. Apply the residual Cauchy–Schwarz bound and the maximum absolute-row-sum bound for a Hermitian matrix. Thus complete landmark columns give a computable sufficient kinetic error certificate without learning the remaining entries. With bounded Hermitian finite-grid generators, multiply this bound by |t|/hbar for the standard sufficient propagator-error bound. The certificate can be conservative; it is not a measured acquisition advantage or a sharp stopping theorem.

Each landmark requires a complete column: its acquisition can cost O(N) overlap evaluations. Known columns are not free, rank is not known in advance, and near-singular C needs separate conditioning treatment. The displayed bound assumes exact labels; noisy electronic calculations require their own error allowance. Selecting new landmarks to reduce the weighted residual bound is a concrete nonlearned comparator, not a claimed optimal policy.

## What remains of the learning proposal

The unresolved object is now explicit: off-diagonal complementary-subspace correlations R_nm after projecting onto the observed electronic landmarks. For v_n,v_m>0, a possible target is K_nm=R_nm/sqrt(v_n v_m), with PSD compatibility and unit diagonal on that residual support. A learner could condition on geometry and chemical/electronic features and predict these correlations across a declared family. Zero-residual rows require no prediction. Training K needs measured off-landmark overlaps or equivalent electronic information; assigning zero residual is a prior, not ground truth.

To justify continued investment, show why these normalized correlations have transferable structure that saves reference queries relative to the same-information landmark certificate, overlap-informed KRR and linked products, at matched coherent error and total cost. All baselines can exploit the same features and kinetic-aware objective. The original rotating family is solved without learning, and the unrestricted three-node class has an exact information limit. Neither proves that real-molecule transfer is impossible.

Do not treat this as an activated method, a new topic card, a general quantum-chemistry no-go, or permission for a numerical test. The remaining positive claim is an empirical or approximation-efficiency claim whose molecular support is unqualified. Stop routine expansion of this toy chain; return only with a specified, supported cross-geometry/cross-chemistry correlation structure or a matched acquisition asset. No new raw question, cycle, source, forecast, F2/F3 or execution. The ICLR/ICML objective remains incomplete.
