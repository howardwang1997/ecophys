# Paper G: isotope-response contribution and identification audit

PRIVATE / INTERNAL. 2026-09-13 NZ. Follow-up to Cycle34; no new question or cycle.

**Park the candidate nonterminally for portfolio allocation.** The earlier periodic nonredundancy example remains valid. This review adds an exact blind family for all allowed element-wise mass interventions and identifies direct, efficient force-constant supervision as an existing competitor. Practical incremental value remains an empirical question; the current evidence does not qualify a distinct ICLR/ICML contribution. Neither absence of benefit nor impossibility of a useful restricted metric has been established.

The prospective [allocation](../../research/paper_g/isotope_contribution_allocation_20260913.yaml) allowed at most three new retained primary works. Two were expanded and retained. The original Cycle34 ten-work screen remains unchanged. This is a targeted contribution review, not a fifteen-work F3 audit; no retrospective forecast is created.

## Direct competitors and fair information accounting

[PFT, Koker et al., arXiv v4](https://arxiv.org/html/2601.07742v4), Sections 3–4, directly trains periodic MLIPs against reference force constants using sampled Hessian columns and one Hessian-vector product per training batch. It evaluates curvature and downstream property performance, with upstream co-training to address forgetting. Its source describes the PBE MDR phonon dataset and a test split containing both materials absent from MPtrj and materials already present there. Thus generic efficient curvature supervision, associated phonon improvements, and reuse of this reference resource are established competitors. Its reported A100 cost is not a benchmark for our available machines. The isotope measurement is not itself evaluated in the inspected sections; this is not an exhaustive absence claim.

[HINT, Yin et al., arXiv v1](https://arxiv.org/html/2603.25373v1), Sections II and IV, combines Hessian pre-training, configuration selection, curriculum weighting and random-projection Hessian losses. Its loss uses Rademacher probes and Hessian-vector products, and it discusses molecular and anharmonic-material applications. Therefore stochastic curvature sketches and label-efficient Hessian learning are also direct methodological neighbors. The reported application results do not establish performance for our frozen isotope target.

These are two additional distinct works, making eight in the exact candidate's retained neighborhood. Other search hits were intake only and were not expanded or used as evidence. No literature search silence supports novelty.

When reference force constants have already been acquired, all proposed harmonic isotope labels are deterministic transformations of them. A comparison that supplies these matrices only to the isotope method while giving competitors merely scalar frequencies confounds objective design with privileged information. Direct force-constant error is a legitimate validation comparator on the same labelled materials; it is not a free input on unlabelled deployment materials.

The meaningful residual, if one exists, must concern task weighting, robustness, sample efficiency or decision value at matched labels and compute. It cannot be an assertion that mass relabelling creates new quantum-chemistry information. Conversely, deterministic reuse of labels does not prove a task-oriented loss useless: different losses can prioritize different errors under finite capacity and finite optimization budgets.

## Exact blind family under every group-wise mass intervention

Work in the internal coordinates of the previous six-site scalar periodic construction. Let

\[
M(\boldsymbol\mu)=\sum_g\mu_g\Pi_g,\qquad \mu_g>0,
\]

where the orthogonal projectors select the supported labelled groups. Choose an orthogonal matrix Q satisfying Q Pi_g = Pi_g Q for every g. Define K'=Q K Q^T, with labelled displacement coordinates and probes held fixed. Since Q commutes with every allowed M and M^(-1/2),

\[
M^{-1/2}K'M^{-1/2}
 =Q\bigl(M^{-1/2}KM^{-1/2}\bigr)Q^T.
\]

Every allowed mass assignment therefore produces identical spectra. Group-projected spectral measures are also equal because their projectors commute with Q. This equality includes finite endpoints, differences, all response derivatives, and any deterministic score computed solely from these spectra.

This need not be a relabelling of the physical experiment. Use K_A from the previous construction and rotate only its two internal A coordinates by theta=pi/4, leaving B internal coordinates and both group centroids unchanged. The stiffness along the same fixed displacement r_A1 changes from 3/2 to

\[
(3/2)\cos^2\theta+(7/2)\sin^2\theta=5/2.
\]

Thus a local displacement-force measurement distinguishes the systems although the entire supported isotope-spectral experiment does not. Apply the same transformation cell by cell. It preserves finite interaction range, positivity and the common centroid coupling. Because centroids are fixed, the translational zero mode and acoustic sum rule remain intact.

This is an exact scalar periodic counterexample to complete force-error identification. It is not a proof that realistic chemical MLIPs commonly make these errors, nor a three-dimensional chemical realization. More refined site labels or direction-sensitive observations change the intervention/measurement family and require a separate analysis. The conclusion applies to the declared group/element-wise spectra, not to all possible isotope experiments or scattering intensities.

Consequently an isotope-only score cannot certify a universal bound on full force-constant error or reliably localize every coupling error. The earlier example showed that the score is stronger than some ordinary spectral summaries; this example shows that it is still incomplete. Both statements can hold simultaneously. This is elementary linear algebra used as a control, without a new-theorem claim.

## The proposed training loss is locally a weighted Hessian error

For a fixed mass choice a, set S_a=M_a^(-1/2). Let u_ai be a normalized eigenvector of S_a K S_a at a simple eigenvalue. Perturb K by E. With gaps bounded away from zero, ordinary first-order Hermitian perturbation gives

\[
\delta\lambda_{ai}=\operatorname{tr}(A_{ai}E)+O(\|E\|^2),
\qquad A_{ai}=S_a u_{ai}u_{ai}^T S_a.
\]

For a response defined as an endpoint eigenvalue change relative to a fixed baseline b, the linearized error is tr[(A_ai-A_bi)E], with consistent isolated mode association. Squaring and summing these residuals gives a positive-semidefinite quadratic form in E to leading order. Frequency-based losses introduce the corresponding inverse-frequency weights and require exclusion or separate treatment of zero modes. Degeneracy/crossings require spectral-projector or aggregate formulations, not this simple-mode formula.

Mass-response supervision therefore induces a task-dependent weighting of the already supplied Hessian error. It may help finite-sample learning, but the algebra alone gives no improvement over direct or suitably weighted Hessian supervision. The blind family above supplies null directions for spectral supervision. Full matrix norms also do not totally order target errors; a smaller global matrix error can have a worse error in a particular response-sensitive direction. Neither objective universally dominates the other in task performance.

As a separate standard control, for any zero-mean random probe with covariance I,

\[
\mathbb E\|Ez\|_2^2=\operatorname{tr}(E^TE)=\|E\|_F^2.
\]

This identity explains why random HVP probes are a mandatory complete-matrix competitor in expectation. It is not a guarantee that a finite number of probes detects every error, nor a claim that our isotope loss is computationally equivalent to one HVP. Dense isotope eigensolves and model Hessian construction must be charged to the budget.

## A decision claim that would be testable, but is not established

Freeze a model pool, reference protocol, labelled mass actions, spectral resolution and loss before outcomes. On validation materials, use either baseline phonon summaries, projected-spectrum metrics, direct/weighted Hessian error, or isotope-response error to select one model or calibration. Then evaluate the selected model on a disjoint confirmation set and compare selection regret relative to the best member of the same pool under the declared target risk. A model selected by its isotope error and evaluated on those same material/action outcomes provides no independent selection evidence.

If the intended target is isotope prediction, held-out isotope risk is a legitimate target but says nothing by itself about transport, reaction kinetics or general force accuracy. Broader utility needs its own target and truth. Where training is proposed, compare against direct Hessian supervision, stochastic HVP supervision, ordinary spectral supervision and simple rescaling, with identical labels, upstream data, tuning effort and measured compute.

Multiple isotope assignments from one force matrix are dependent derived labels. Split by material/prototype as appropriate, preserving release-time and overlap information; never put isotope variants of one structure into opposite development and confirmation partitions. Any new-chemistry claim additionally requires verified pretraining/material provenance. For time-evolving collections use chronological separation, as required by project data discipline. More mass assignments do not automatically increase the number of independent confirmation units.

Analytic failure regimes now include uniform scaling and rank-one redundancy, the group-commuting blind orbit, acoustic zeros, near degeneracies, geometry/functional mismatch and use of a harmonic target to claim anharmonic transfer. Calibration on a restricted model/material distribution remains possible, but its coverage and false-acceptance rates are currently unmeasured. The reference/model joins and untouched confirmation partition are also not yet qualified at file level.

## Allocation decision

The discriminating fork remains: finite group-wise isotope responses may be a useful task-oriented selector beyond inexpensive spectral summaries, or their benefit may be explained by direct curvature information and existing calibration. The periodic example does not choose between those practical explanations. The two new works establish strong feasible competitors, and the new blind family rules out a broader force-error certification narrative.

After this bounded review, no concrete advantage at matched information and cost is supported. Park g34_isotope_spectral_response for allocation; do not declare the empirical hypothesis false or close all isotope-informed learning. Resume only on a contribution-changing primary result or a qualified, economical comparison asset with a genuinely untouched confirmation partition and an explicit budget. Merely proposing another mass grid, relabelled material, generic spectral loss or additional review is insufficient to resume this source chain.

Next effort goes to an unsaturated cross-domain question cycle under the existing PI scope, with balanced measurement/intervention sampling. The broad ICLR/ICML objective is active and incomplete. This review itself authorizes no data/model payload access, implementation, training, simulation, GPU work, participant work, outreach or publication.
