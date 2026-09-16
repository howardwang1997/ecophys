# Paper G: periodic realization and isotope-response boundaries

PRIVATE / INTERNAL. 2026-09-13 NZ. Source and analytic follow-up to Cycle34.

**Retain the existing candidate, with a stronger but narrower foundation.** The finite-mass nonredundancy example has an exact stable, translation-invariant one-dimensional periodic realization. A source-level path to common-geometry force matrices is documented. These results remove two preliminary uncertainties; neither establishes a new physical phenomenon, practical ML benefit, or readiness for ICLR/ICML.

This is not a new question or cycle. Two additional retained primary works consume Cycle34's ten-work allocation. A six-work targeted collision review is complete; the full F2 contribution/measurement contract remains unqualified. No fifteen-work audit, forecast, machine card, dataset/model payload, scientific implementation or simulation was opened.

## Exact periodic harmonic construction

In each cell n, take six scalar displacement coordinates, three in labelled group A and three in B. All baseline masses are one in the chosen units. This is an abstract scalar lattice, not a specified chemical compound.

For each group g define orthonormal coordinates

\[
r_{g1}=(u_{g1}-u_{g2})/\sqrt2,\quad
r_{g2}=(u_{g1}+u_{g2}-2u_{g3})/\sqrt6,\quad
c_g=(u_{g1}+u_{g2}+u_{g3})/\sqrt3.
\]

Set r=(r_A1,r_A2,r_B1,r_B2), c=(c_A+c_B)/sqrt2 and d=(c_A-c_B)/sqrt2. The two models differ only in the internal stiffness matrix:

\[
K_A=\begin{pmatrix}
3/2&0&-1/2&0\\0&7/2&0&-1/2\\
-1/2&0&3/2&0\\0&-1/2&0&7/2
\end{pmatrix},\qquad
K_B=\begin{pmatrix}
2&0&-1&0\\0&3&0&-1\\
-1&0&2&0\\0&-1&0&3
\end{pmatrix}.
\]

For either K, define the finite-range energy

\[
U_K=\frac12\sum_n
\left[r_n^\mathsf{T}Kr_n+\kappa d_n^2+
\gamma(c_{n+1}-c_n)^2\right],\qquad \kappa,\gamma>0.
\]

Both internal matrices have eigenvalues 1,2,3,4 and are positive definite. The centroid sector has stiffnesses kappa and 2 gamma(1-cos q). Consequently the lattice is stable with exactly one translational zero mode at q=0, and all other modes positive for q nonzero. Uniform translation changes neither r nor d nor the intercell difference: the acoustic sum rule holds. Forces are conservative, with a smooth quadratic potential. Non-pairwise harmonic interactions are allowed here.

Now multiply the masses of **all three labelled A sites** by 1+epsilon, leaving B unchanged. The orthonormal transformation stays block diagonal with respect to A and B, so the internal mass matrix is diag(1+epsilon,1+epsilon,1,1). The centroid sector changes identically in both models and does not couple to the internal coordinates.

The four internal baseline modes each have total A-group weight 1/2 in both models. Therefore both lattices share their baseline frequencies, A/B group-projected spectral measures, and first-order optical log-frequency slopes. At epsilon=1, their internal characteristic polynomials are exactly the pair from Cycle34:

\[
p_A=(2\lambda^2-\tfrac92\lambda+2)
     (2\lambda^2-\tfrac{21}2\lambda+12),\quad
p_B=(2\lambda^2-6\lambda+3)(2\lambda^2-9\lambda+8),
\]
\[
p_B-p_A=\tfrac34\lambda^2.
\]

Multiplication by the common centroid characteristic polynomial preserves their difference. The distinct endpoint optical spectra occur at every wavevector, so Brillouin-zone averaging does not erase the example.

This resolves periodicity, scalar translational invariance, positivity and a fixed labelled mass action. It does **not** establish a three-dimensional rotationally invariant chemical realization, realistic interactions, equality of every atom-resolved spectrum, or occurrence among trained MLIPs. The flat internal branches are part of the construction; generic persistence under realistic couplings has not been proved. There is no new-theorem claim.

## What remains redundant or bounded

The selected-subspace projected spectrum records diagonal participation, not all mixing matrix elements. Nevertheless, full force constants already determine every harmonic isotope endpoint. In a baseline mass-weighted frame, write the reference and predicted matrices as D and D+E and the relative mass update as I+epsilon Pi. Set S=(I+epsilon Pi)^(-1/2). The target error is exactly S E S.

For epsilon >= 0, norm(S) <= 1, giving

\[
\|SES\|_2\leq\|E\|_2,\qquad
\max_i|\widehat\lambda_i(\epsilon)-\lambda_i(\epsilon)|
\leq\|E\|_2.
\]

The second inequality is the standard Hermitian eigenvalue bound, with eigenvalues sorted at each endpoint. Subtracting the baseline errors gives at most 2 norm(E) for the error in a sorted squared-frequency change. This is not branch tracking through a crossing. Frequency rather than squared-frequency relative errors need a lower frequency bound; acoustic zero modes require separate treatment.

Thus the proposed score can expose information omitted by **summary spectral metrics**, but cannot be advertised as amplification beyond full force-matrix control under a heavier-mass update. Generic closeness in energy/force samples is a different assumption from a full operator-norm Hessian bound.

Single-coordinate rank-one updates have a scalar resolvent reconstruction: det(D-lambda[I+epsilon vv^T]) equals det(D-lambda I) times [1-lambda epsilon v^T(D-lambda I)^(-1)v], extended through poles as a polynomial identity. Its input is already determined by frequencies and the v-projected spectral measure. Uniform mass scaling is also exactly determined. Both are mandatory easy controls. Finite higher-rank substitution is the supported nonredundancy regime.

## Six-work collision review

| Work | What is already known | Remaining distinction |
|---|---|---|
| [Loew et al.](https://arxiv.org/html/2412.16551v1) | Large-scale phonon and thermodynamic MLIP benchmarking | A new score must improve a decision beyond those comparisons |
| [Han and Cheng](https://arxiv.org/html/2506.01860v1) | DFT and experimental neutron-spectrum evaluation | Isotope-sensitive coupling evaluation is not generic spectral benchmarking |
| [Armstrong et al.](https://arxiv.org/html/2602.20907v1) | Isotope-induced mode mixing and continuation | Mixing, eigenvector transport and isotope perturbation formulas are not new |
| [Deng et al.](https://www.nature.com/articles/s41524-024-01500-6) | Systematic softening and inexpensive local correction | Include simple rescaling/calibration controls |
| [Fu et al., eSEN](https://arxiv.org/html/2502.12147v1), 6.4 and Appendix B | Relationships between test error and physical-property errors among smooth, energy-conserving models | Compare within valid conservative model families; the lattice example does not refute their statistical correlations |
| [Bongalonta, Dinner and Tokmakoff](https://pubmed.ncbi.nlm.nih.gov/41190617/), [author manuscript indexed text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12768576/) | Isotope-labelled IR constraints, structural information and sensitivity to coupling/forward-model error | Isotope labels adding useful information is prior art; their peptide ensemble problem is not the fixed-crystal harmonic MLIP estimand |

The last two are the new retained works. The peptide review uses verified bibliographic metadata and indexed author-manuscript introduction/conclusion passages, not a full methods audit. A LiH isotope/transport abstract was encountered during intake but not expanded, retained or used to support the candidate. No assertion of absent prior art follows from keyword-search silence.

## Source-level truth path

The [Alexandria directory index](https://alexandria.icams.rub.de/data/phonon_benchmark/) lists separate PBE/PBEsol directories, CSV summaries and a displacement archive. The [benchmark README](https://github.com/hyllios/utils/tree/main/benchmark_ph) names the reference and model phonon workflows. The previously verified provider CC BY 4.0 declaration remains the data-licence starting point.

Two author sources were read without execution:

- [calc_ref.py](https://raw.githubusercontent.com/hyllios/utils/main/benchmark_ph/calc_ref.py) loads reference phonopy YAML, constructs and symmetrizes force constants, and saves them explicitly. It disables the nonanalytic electric-field correction. This is the declared reference convention to reproduce, not a failure narrative.
- [calc_phonopy.py](https://raw.githubusercontent.com/hyllios/utils/main/benchmark_ph/calc_phonopy.py) builds the model calculation from reference cell coordinates and supercell/primitive matrices; relaxation is optional. It generates displaced forces and saves symmetrized force constants. This supports a common-geometry comparison path, but does not prove a precomputed matched set of model matrices is already released.

CSV thermodynamic summaries alone do not qualify the finite-response target. Required joins remain: material identity, labelled sites, mass convention, geometry, primitive/supercell mapping, force constants, nonanalytic convention, reference functional and displacement/symmetrization settings. Source hashes and directory metadata are recorded in YAML. No compressed YAML, CSV outcomes, displacement archive or weights were opened.

## Candidate decision and next allocation

The five-part contract is now narrower: X is a fixed-geometry labelled harmonic reference; A is a finite, higher-rank mass substitution; Y is the endpoint spectral change under a frozen resolution; H1 versus H0 asks whether this adds a useful model-selection/calibration signal after ordinary spectra, projected weights, gaps and smoothness controls; T comprises the exact periodic scalar construction and a documented source interface, with file-level real-material qualification still pending.

Keep the measurement candidate for a bounded contribution assessment. No experimental isotope campaign or new DFT calculation is required merely to establish the harmonic truth target. Conversely, nonredundancy alone does not warrant a paper: a useful positive result must change an evaluation or training/calibration decision at matched information and cost; a useful null must delimit when existing diagnostics suffice. The complete reference Hessian is an oracle, not a free deployment feature.

Cycle34's ten-primary-work screen allocation is consumed. Any further literature expansion needs a separately recorded, outcome-blind review allocation within the existing paper-research scope; a full F3 audit additionally needs the exact subject and prospective forecast before opening its neighborhood. This record authorizes no execution. Current status remains candidate, with no full F2 qualification or F3 advancement.

Counts remain Paper G69 formulations/18 cycles/0 cards. The broad ICLR/ICML objective remains active and incomplete; this turn made progress through an exact construction, sharper reduction boundaries and source-contract evidence.
