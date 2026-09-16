# Paper G Cycle34: materials and molecular response

PRIVATE / INTERNAL research-selection record. 2026-09-13 NZ.

Four source-informed F1 questions were screened: two measurement methods and two empirical interventions. Three generic formulations close at the primary-collision gate. One narrower measurement question survives provisionally: **do finite, element-selective isotope spectral responses reveal errors in learned force constants beyond baseline frequencies and element-projected spectral weights?**

Eight primary works and three documentation sources were retained. No F2/full hostile audit, forecast, machine card, model/data payload access, scientific implementation or experiment was performed. The cycle start precedes the searches; individual questions were composed during reading and are not prospective experimental freezes. The previous LRU review made progress by resolving its allocation; both that question and the chemical stress question remain parked.

## Screening decisions

| ID / archetype | Native question and rivals | Discriminating result and both-answer value | F1 disposition |
|---|---|---|---|
| g34_isotope_spectral_response / measurement_method | At fixed structure and electronic reference, does finite isotope-response error contain coupling information beyond ordinary frequency and element-projected spectral errors, or are the extra scores redundant? | A controlled response error surviving those baselines would justify an intervention-sensitive MLIP diagnostic; a tight null would support cheaper baseline evaluation. | Retain F1 only. Analytic nonredundancy exists for harmonic matrices; realized crystal/model relevance and exact novelty are unresolved. |
| g34_phonon_misspecification_uq / measurement_method | Do energy/force-based uncertainty ensembles cover phonon errors, or do shared approximation errors invalidate their apparent confidence? | Matched-reference phonon coverage could support property-level reliability; lack of coverage would identify a need for curvature-sensitive calibration. | Close this generic formulation: direct misspecification-UQ work already studies phonons; no distinct calibration guarantee or new material mechanism specified. |
| g34_sto_isotope_phase / empirical_intervention | At fixed lattice state, does oxygen mass substitution change SrTiO3's phase through quantum/anharmonic fluctuations, or can classical harmonic mass scaling explain it? | A fixed-structure mass/temperature comparison separates the mechanisms; a positive effect would support nuclear-quantum modelling, while a null would bound that claim in the specified region. | Close the generic proposal: the named MLIP/SSCHA study already investigates this physical intervention and structural dependence. |
| g34_co_dimerization_charge_response / empirical_intervention | At a Cu/water interface, does solvent reorganization screen the charge dependence of CO dimerization, or does field stabilization dominate? | Matched charge, cell area, solvent and reaction-coordinate free energies could discriminate; a positive result would motivate explicit solvent, a null would delimit simpler models. | Close this generic formulation: the current OC25-linked work already studies this mechanism and its high-charge boundary. |

No exact duplicate of these native formulations was found in the route graph by domain/target search. The earlier closed local-charge-input route is not the isotope measurement question. No opposite headlines are treated as a matched contradiction. Generic closures do not close materials ML, phonon UQ, quantum phase transitions or electrochemical modelling.

## Primary neighborhood and collision boundaries

1. [Loew et al., phonon benchmark](https://arxiv.org/html/2412.16551v1), also [npj Computational Materials 11, 178 (2025)](https://doi.org/10.1038/s41524-025-01650-1), evaluates phonon and thermodynamic properties rather than relying only on energy/force errors. A generic “forces are insufficient for phonons” contribution is already occupied.
2. [Han and Cheng, neutron-spectrum benchmark](https://arxiv.org/html/2506.01860v1), Methods and Results, compares learned potentials with DFT phonons and experimental neutron spectra. It holds cell dimensions fixed but relaxes internal coordinates per model. Its PDOS denotes phonon density of states; do not silently read it as an atom-projected spectrum. A generic spectral benchmark or experimental INS comparison is already occupied.
3. [Armstrong et al., isotope eigenvector transport](https://arxiv.org/html/2602.20907v1), Methods and III, studies H/D ZIF-8 and develops mode continuation and mixing diagnostics. Isotope-induced mode mixing, overlap tracking and eigenvector-sensitive interpretation are existing physics, not our discovery.
4. [Misspecified-potential UQ](https://arxiv.org/html/2502.07104v1), III.3, propagates a POPS ensemble to phonons and reports reference-spectrum bracketing in its example. This is direct prior art, not a universal coverage theorem for other models or materials.
5. [Deng et al., systematic softening](https://www.nature.com/articles/s41524-024-01500-6) reports systematic potential-surface underprediction and data-efficient local correction. Scalar correction is an essential simple comparator for a future diagnostic, not a novel method by itself.
6. [Wong and Yang, fine-tuning bias](https://pubs.acs.org/doi/10.1021/acs.jctc.6c00425) compares one-stage and iterative sampling/fine-tuning in liquid systems. It is adjacent evidence about sampling and shared bias, not a contradictory phonon-UQ result on the same state.
7. [Schmidt and Spaldin, SrTiO3 isotope phase diagram](https://arxiv.org/html/2508.10735v1) combines MLIPs with quantum/anharmonic treatment and varies volume, tetragonality, temperature and isotope mass. The generic isotope phase-transition application is already present.
8. [Sahoo et al., CO dimerization, v2](https://arxiv.org/html/2509.17862v2), 2.3 and Discussion, studies explicit-water screening and a stronger response at very negative charge. Large constant-charge cells approximate, but do not enforce, constant potential. Use this actual v2 title/content; the older OC25 dataset title is not an additional work.

The first three are the retained candidate's F1 anchors. The UQ question has works 4–6, and each empirical question has its direct parent. This is eight distinct works, not eight independent replications. Two primary-work slots remain under the cycle cap of ten.

## Candidate's exact scope

Let Phi be harmonic force constants at one specified geometry and electronic-structure reference, and let M be the labelled nuclear mass matrix. The dynamical matrix is

\[
D(M)=M^{-1/2}\Phi M^{-1/2}.
\]

Change the mass of a specified element/sublattice while keeping Phi and the geometry fixed. This is an evaluation of the harmonic reference, not a prediction of isotope-driven structural relaxation, anharmonic free energy, quantum phase boundaries, or isotope-disorder scattering. Numerical mass interpolation is a mathematical path; only specified isotope endpoints receive a physical interpretation.

For a nondegenerate mode i with normalized eigenvector q_i and eigenvalue lambda_i = omega_i squared, take M(epsilon)=M(0)(I+epsilon Pi), with Pi selecting the changed mass coordinates. Standard perturbation theory gives

\[
\frac{\partial\log\omega_i}{\partial\epsilon}\bigg|_0
=-\frac12 q_i^\dagger\Pi q_i.
\]

Thus a first-order isotope score merely restates the mode's selected-coordinate participation. A new measurement must not claim extra information from this identity. At degeneracy, individual eigenvectors are not unique; compare spectral measures or isolated subspace quantities, not arbitrary branch labels.

The proposed target is a **finite endpoint spectral change**, scored without assigning individual modes across crossings. Fix the frequency window, broadening/resolution and comparison norm before outcomes. The exact choice still requires F2 assessment; broadening must not be tuned to manufacture a gap. Compare at common DFT geometry first, with model-relaxed geometry as a separately labelled analysis.

## Two elementary nonredundancy controls

**A translation-preserving spring example.** Consider three unit masses with force matrices

\[
K_A=\begin{pmatrix}1&-1&0\\-1&2&-1\\0&-1&1\end{pmatrix},\qquad
K_B=\begin{pmatrix}2&-1&-1\\-1&1&0\\-1&0&1\end{pmatrix}.
\]

Both have eigenvalues 0, 1, 3 and obey the acoustic sum rule. Change the mass at the same labelled site 1. At eigenvalue 1 the site weight is 1/2 for A and 0 for B, giving log-frequency slopes -1/4 and 0. The networks are different physical coupling assignments; relabelling both the network and intervention together would not create a difference. This example shows why ordinary frequencies are insufficient, but an element/site-projected baseline already detects its difference.

**A stronger finite-change control.** In a four-dimensional harmonic generalized eigenproblem, let Lambda=diag(1,2,3,4). Choose rank-two projectors in the eigenbasis:

\[
P_A=\frac12\begin{pmatrix}1&1&0&0\\1&1&0&0\\0&0&1&1\\0&0&1&1\end{pmatrix},
\quad
P_B=\frac12\begin{pmatrix}1&0&1&0\\0&1&0&1\\1&0&1&0\\0&1&0&1\end{pmatrix}.
\]

Both are orthogonal conjugates of the same fixed coordinate selector Pi=diag(1,1,0,0). Therefore they describe different positive force matrices under the same labelled mass action, not a change of coordinate convention for one experiment.

Their initial frequencies, selected-subspace projected spectral measures, and all first-order log-frequency slopes (-1/4) agree. For doubling the selected masses, the characteristic polynomials of Lambda - lambda(I+P) are

\[
p_A(\lambda)=(2\lambda^2-\tfrac92\lambda+2)
                 (2\lambda^2-\tfrac{21}2\lambda+12),
\]
\[
p_B(\lambda)=(2\lambda^2-6\lambda+3)
                 (2\lambda^2-9\lambda+8).
\]

Their difference is p_B - p_A = 3 lambda squared / 4, so the finite endpoint spectra differ. Off-diagonal mixing information is not fixed by the initial eigenvalues and diagonal participation alone.

This is a hand-derived matrix control, not a new theorem, measured MLIP error or certified periodic-crystal construction. It does not show insufficiency of the full force matrix, full projected resolvent, or all atom-resolved spectral data. A rank-one mass update has stronger reconstruction identities; replacing all masses uniformly is exact global frequency scaling. Those cases must not be advertised as hard tests.

## Killer controls for the pruned questions

- **UQ:** E_a(x)=a x squared / 2 has E_a(0)=0 and force zero for every a, but curvature a is unrestricted. Agreement at the equilibrium sample cannot certify phonons. The mathematical ambiguity is elementary; the cited UQ work already addresses a substantive version.
- **SrTiO3:** integrating momenta from a classical canonical distribution at fixed geometry/volume leaves the normalized configurational density proportional to exp(-beta U(q)), independent of masses. Classical mass-dependent timescales alone do not provide an equilibrium isotope phase mechanism. This does not exclude nuclear quantum effects or nonequilibrium protocols.
- **Electrochemistry:** for F(Q,xi)=F0(xi)+(Q-q0(xi)) squared /(2C), minimizing F-mu Q gives F0-mu q0-C mu squared /2. Fixed-charge and fixed-potential barriers differ when preferred charge changes along the reaction. Increasing C suppresses the correction only under the stated bounded-charge-change scaling; it is not automatic equivalence for every interfacial state. This is standard ensemble accounting, not a new electrochemical result.

## Truth resource and next decisive step

[Alexandria's dataset page](https://alexandria.icams.rub.de/datasets.html) explicitly links the phonon work, PBE/PBEsol calculations, a full dataset and displacement records. Its [licence page](https://alexandria.icams.rub.de/about.html) declares CC BY 4.0. This gives a plausible reusable reference path, unlike a requirement for new isotope experiments at the F1 measurement stage. File-level force-constant layout, labels, Born-charge/nonanalytic conventions and checksums remain to be pinned. No archive was downloaded.

The [Han/Cheng repository](https://github.com/maplewen4/phonon_uMLIP) supplies model-specific phonon scripts and a dataset pointer. Its scientific paper documents a complementary PBE calculation protocol and fixed-cell comparison. This does not establish interchangeable geometry, functional, displacement convention or model-training independence between the two databases.

The next bounded review should first test the stronger control in a lawful periodic harmonic setting and search the exact finite-isotope-response benchmark neighborhood. Then check whether the release supports paired force matrices at a common geometry without fresh electronic calculations. Strong controls include initial frequencies, selected-element projected weights, spectral gaps, first-order extrapolation and a full-Hessian mass-update reference. Scalar energy rescaling and existing spectral/property fine-tuning must be included if a learning improvement is proposed.

The central uncertainty is **incremental ML value**, not the known isotope perturbation formula. A useful result would explain reproducible model-ranking or error differences after these controls and provide a better calibration/training choice at matched cost. If all differences reduce to known projected-spectrum errors or ordinary force-matrix error without additional practical value, close the standalone pitch. Do not demand new experimental hardware or a new theorem merely to qualify a computational measurement question.

The DFT force matrix is the reference truth, not a free deployment baseline. Any proposed diagnostic or training method must state which reference labels it consumes; full reference matrices trivially determine the harmonic endpoint. Approximation of a chosen DFT reference must also remain separate from experimental accuracy.

Paper G totals: 69 formulations / 18 cycles / 0 machine cards. Detailed ledger: 25 cycles / 153 raw questions; historical-inclusive: 34 cycles / 209 raw questions. The broad ICLR/ICML objective remains active and incomplete.
