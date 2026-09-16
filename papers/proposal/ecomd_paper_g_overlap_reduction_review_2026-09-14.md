# Paper G: electronic-overlap reduction review

PRIVATE / INTERNAL — exploratory topic adjudication, not public research evidence. 2026-09-14 NZ.

Decision: park `g41_electronic_overlap_transport` nonterminally. Complete-frame compatibility has an exact ordinary-diabatic reduction; factorized propagation has a direct algebraic baseline. A useful learning advantage remains possible, especially for varying truncated electronic subspaces, but no concrete advantage construction or matched molecular truth contract is qualified. This is neither an empirical refutation nor a closure of nonadiabatic scientific ML.

## Allocation and primary comparison

The [immutable allocation](../../../research/paper_g/overlap_reduction_review_start_20260914.yaml) permits one new primary work and deeper reading of existing Gu2023. No new question, search cycle, F2/F3, forecast, machine card, scientific implementation or outcome payload. Four unique primary works now support the route; the original Cycle41 record remains historical and unchanged.

Richings and Habershon, *A new diabatization scheme for direct quantum dynamics: Procrustes diabatization*, JCP 152, 154108 (2020), DOI [10.1063/5.0003254](https://doi.org/10.1063/5.0003254), is a direct parent. Selected sections II.B–C of the [accepted manuscript](https://wrap.warwick.ac.uk/id/eprint/136119/13/WRAP-new-diabatization-scheme-direct-quantum-dynamics-procrustes-diabatization-Habershon-2020.pdf) describe overlap-based SVD alignment and kernel ridge fitting of diabatic potential-matrix entries within grid-based quantum dynamics. Omitted electronic states leave quasi-diabatization residuals; it is not exact for every finite molecular state selection. This establishes an overlap-informed fitted coherent-dynamics comparator, without settling the candidate's matched-cost question. Selected methods only; no reproduction or payload access.

Gu, *Local diabatic representation of conical intersection quantum dynamics*, [arXiv:2304.04369v1](https://arxiv.org/html/2304.04369), section II, supplies the existing overlap-dependent discrete Hamiltonian and geometric-phase construction. The potential uses a DVR approximation. The algebra below is exact for this specified discrete operator, not a claim of exact continuum molecular dynamics. This is a reading-depth update of `g41_local_diabatic`, not a fifth unique work. Cycle41's SchNarc and DANN comparisons remain in force: joint state signs in SchNarc, coupling-constrained diabatic modeling in DANN; neither is an energy-only straw baseline.

## R1 — complete-frame reduction

Take N nuclear grid points, m retained electronic states, diagonal energy matrices E_n, and a fixed nuclear kinetic matrix T. Let F_n be an r-by-m complex matrix with F_n† F_n = I_m, representing electronic states in a common ambient frame. Define

\[
A_{nm}=F_n^\dagger F_m,\qquad
H_{nm}=\delta_{nm}E_n+T_{nm}F_n^\dagger F_m.
\]

For r=m, F_n is unitary. With W=blockdiag(F_n), block multiplication gives

\[
(WHW^\dagger)_{nm}
=T_{nm}I_m+\delta_{nm}F_nE_nF_n^\dagger.
\]

Thus the model is a standard common-kinetic diabatic Hamiltonian with matrix potential V_n=F_n E_n F_n†. Transform initial coefficients and observables by the same W; all corresponding finite-grid predictions agree. Conversely, pointwise diagonalization of any Hermitian V_n constructs such a frame on the finite grid. This is an operator-level representation equivalence, not equality of particular finite neural-network hypothesis classes, optimization behavior, smoothness constraints or sample efficiency.

Gram positivity, diagonal identity blocks and gauge compatibility alone therefore do not supply a distinct complete-frame prediction class. A learning proposal still needs a concrete generalization, acquisition-cost or approximation advantage over capable diabatic fitting.

Two boundaries are essential. First, full-frame products telescope around a closed loop, but projecting to one energy band between steps can retain a nontrivial band holonomy. The reduction does not remove geometric phase. Second, for r>m the block W is only an isometric embedding. The kinetic term is a compression of T tensor I_r to varying local subspaces; it need not reduce to a common m-state kinetic operator. Extending the square proof to arbitrary molecular truncations would be invalid. Residual subspace and omitted-state errors need a separate contract. Cycle41's C-infinity annular example is still only an information control, not a real-analytic molecular or SchNarc realizability result.

## R2 — direct factorized propagation baseline

Given the factors, for coefficients c define

\[
z_{mk}=\sum_\beta (F_m)_{k\beta}c_{m\beta},\qquad
y_{n\alpha}=\sum_k\overline{(F_n)_{k\alpha}}(Tz_k)_n.
\]

Expanding the sums gives y=(T-block-weighted A)c exactly. If applying T to one length-N vector costs C_T, this action costs O(Nrm+r C_T), with O(Nrm) factor storage plus T's storage/workspace. Dense all-pair overlap multiplication is therefore not a compulsory baseline. This statement assumes factors already available, counts r explicitly, and does not assume FFT structure on every grid. Acquiring/fitting the factors, reference electronic calculations and numerical error all remain part of total cost.

The same control admits a direct landmark construction. For a PSD overlap Gram matrix A of exact rank r, choose r independent columns indexed by L. Set B=A[:,L], C=A[L,L]. Then C is invertible and A=B C^{-1}B†: write A=G†G with G having r rows; the selected square G_L is invertible, and substitute. This is standard linear algebra, not a new theorem or a guarantee of cheap rank discovery. Unknown rank, noisy overlaps, conditioning, landmark acquisition and off-grid prediction require separate treatment.

Consequently, learned factors must beat same-information direct factors/landmarks and interpolation at matched coherent-propagation error. Comparing only against dense storage would not isolate learning value. Exact complete-frame equivalence does not establish that these baselines dominate a trained model; that empirical possibility remains unresolved.

## Disposition and reusable result

The named positive claim was lower total cost for gauge-consistent coherent populations/interference at fixed molecule, electronic reference, nuclear domain, initial packet and error target. The null alternative was that labels, state basis, resolution, ordinary interpolation or the propagation algorithm explain any improvement. This review sharpens that comparison but supplies no distinct learning mechanism or qualified molecular truth. Apply the preallocated stop rule and park at F1.

Return only for a concrete transferable factor/subspace structure with an explicit same-information cost/error case, a directly relevant primary mechanism result, or a truth asset removing a named blocker. Changing architecture or relabeling geometric phase is insufficient. A new theorem is not mandatory: a well-identified empirical efficiency contribution could qualify. Do not treat this single parked formulation as saturation of all electronic dynamics.

Counts remain Paper G 85 formulations / 25 cycles / 0 machine cards; detailed discovery ledger 32 cycles / 169 raw questions; inclusive history 41 / 225. This review adds two source records and six locators, yielding 329 nodes / 279 edges / 1,932 locators and 1,206 source records, with zero candidates and eleven parked routes. These are research bookkeeping counts, not scientific evidence or acceptance probabilities. Next allocation: another unsaturated native scientific obstruction unless a contribution-changing result justifies returning here. The broader ICLR/ICML goal remains incomplete.
