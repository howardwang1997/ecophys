# Paper G: adjudicating the force-spectrum mechanism comparison

PRIVATE / INTERNAL — public_evidence_eligible=false.
Session started 2026-09-10 04:17 Pacific/Auckland. Previous turn: progress.
Bounded primary-source comparison, not a new candidate or search cycle.

## Outcome and research relevance

No matched primary mechanism disagreement was qualified by this search.
The strongest apparently positive counterpoint to the Bigi force study uses
periodic conservative-force correction and altered atomic masses. It therefore
does not establish that the same uncorrected nonconservative force leaves
the same physical velocity spectrum or diffusion coefficient accurate.

Stop extending this cross-paper force-spectrum comparison without a new
specific trigger. This is a bounded-search conclusion, not proof that no
useful force-model question exists anywhere. It also does not close the
repository's deeper conservation/generalization question: whether an imposed
constraint removes dynamical error or redirects it into another channel.
The [original D-3 question](ecomd_question_contract_constraint_inductive_bias_2026-08-27.md)
supplies that connection; its historical forecasts and experiment plan are
not current authority or evidence.

Decision: `not_trigger`; removed blockers: none. The closed
`slow_memory_random_batch_invariant_correction` route retains only comparison
and measurement controls. No market or atomistic implementation is authorized.

## What the primary comparisons actually hold fixed

The existing [Bigi et al. v6](https://arxiv.org/html/2412.11569v6),
Sections4.4–4.6 and4.8, compares direct and conservative PET forces in liquid
water, examines velocity-correlation spectra under specified thermostats,
and separately considers conservative correction by multiple time stepping.
Its favorable hybrid example is already part of the same study. The
preceding attribution audit established that separate force models and
thermostat interventions must not be merged into a pure-component effect.

Two independent primary works were inspected:

- [Gouraud et al., arXiv2602.14975v1](https://arxiv.org/html/2602.14975v1),
  selected Sections2–3.1: DMTS-NC distills a fast direct-force model from
  FeNNix-Bio1(M), corrects it against that conservative target, and uses
  BAOAB-RESPA. Both DMTS variants activate hydrogen mass repartitioning.
  Water tests use 300 K and friction 1/ps. The diffusion comparison includes
  single-step baselines with and without repartitioning; the paper discusses
  diffusion loss relative to computational acceleration. This is a concrete
  hybrid-method result, not a matched direct-force-only contrast to PET.
  No source implementation or reported numerical result was reproduced.
- [Zhang et al., npj Computational Materials10:94 (2024)](https://www.nature.com/articles/s41524-024-01278-7),
  selected Introduction and Results paragraphs on conservation/smoothness:
  DPA-1 discusses NVE drift and dynamical observables while comparing models
  that also differ in smoothness, force fit and energy prediction. It is
  adjacent evidence for the importance of the simulation contract, not an
  opposite prediction about the same PET force and bath. Supplementary
  Notes5–6 were located through the main text but not independently audited.

The comparison matrix is thus:

| Dimension | PET direct-force comparison | DMTS-NC comparison | Consequence |
|---|---|---|---|
| Conservative reference | PET reference | FeNNix-Bio1(M) | Force functions are not matched |
| Use of direct forces | Direct-force dynamics, with hybrid correction separately considered | Fast force plus periodic target correction | Distinct intervention |
| Bath | Includes white-noise Langevin at several couplings | White-noise Langevin, 300 K, 1/ps | One coupling can match; bath mismatch is not a blanket dismissal |
| Mass matrix | Original preparation must be pinned | Repartitioned masses in DMTS/DMTS-NC | Equal molecular mass does not fix the state dynamics |
| Response | Velocity spectrum and low-frequency diffusion interpretation | Finite-trajectory Einstein diffusion estimate, also used as an efficiency diagnostic | Same asymptotic diffusion is possible; finite estimator and claim scope still need matching |
| Accuracy control | Distinct learned force models | Distilled conservative/direct fast models have different force fits | No matched-fidelity pure-conservation intervention |

The first two rows already prevent qualification as the required primary
disagreement. The remaining rows specify controls for future comparisons;
they do not imply that the external studies are invalid.

## Three elementary controls retained

**The target force and the split force are different objects.** If
`F_C=-grad U`, `F_S` is a fast force and `F_L=F_C-F_S`, then their acceleration
generators obey

    B_S + B_L = B_C.

The continuous target generator contains F_C. The finite-step composition
still depends on the split, the step sizes and the ordering; kicks applied at
different positions cannot be replaced by pointwise cancellation along an
actual discrete trajectory. Thus a successful corrected scheme does not
identify the behavior of the uncorrected F_S process. Bigi's own hybrid result
and the independent DMTS-NC result can both hold without contradiction.
This is the method's stated decomposition, not a new conservation theorem.

**Preserved total mass does not preserve every dynamic response.** For a
fixed potential U and constant positive mass matrix M, canonical position
statistics are independent of M after integrating out momenta. The kinetic
generator and vibrational frequencies need not be. As a minimal analytic
control, two harmonic coordinates with k_i>0 and m_1+m_2 fixed have
`omega_i^2=k_i/m_i`; repartitioning the masses changes their spectra while
preserving the canonical position law. Their long-time free diffusion is not
the water observable, so this does not refute the reported diffusion behavior
of HMR. It only rules out using total molecular mass as a complete spectral
matching condition. No numerical oscillator calculation was run.

**Einstein and velocity-correlation diffusion are not automatically different
estimands.** For zero-mean stationary velocity, define
`C(t)=E[v(0) dot v(t)]`. With finite second moments and unwrapped displacement,

    E|q(H)-q(0)|^2 = 2 integral_0^H (H-t) C(t)dt,
    D_H = E|q(H)-q(0)|^2/(2*d*H)
        = (1/d) integral_0^H (1-t/H) C(t)dt.

If C is absolutely integrable, dominated convergence gives
`D=(1/d) integral_0^infinity C(t)dt`. A centered velocity is needed when
there is drift. Periodic wrapping, atom versus molecular-center coordinates,
lag windows and initial preparation must be fixed. A reported finite-window
MSD slope need not be this exact endpoint D_H. These standard identities
prevent inventing a discrepancy merely from estimator names, while preserving
the genuine force/mass/intervention mismatches above.

Physical-response accuracy and samples obtained per unit wall time are
separate objectives. A diffusion decrease compensated by faster simulation
does not itself establish preservation of the physical diffusion coefficient.
Nor does one diffusion coefficient certify effective sample size for every
structural observable. This scope distinction is not a measured failure of
either source.

## Limits, records and next action

This audit reads two additional primary works and reuses the existing Bigi
contract. It supplies no pure learned-component intervention, independent
physical-response truth, untouched confirmation or uniform slow-memory
theorem. No raw outcome, model, notebook, software source or scientific
archive was accessed. Published article algorithms were read but not executed.
No simulation, GPU/SSH, outreach, purchase, publication, commit or push occurred.
All records and article caches remain private/internal.

The current force-spectrum comparison is exhausted at this bounded level.
Do not generate another thermostat, force-head, MTS or HMR variant under a
different label. Re-entry needs a named matched primary prediction or a
specific theorem/control asset removing a recorded blocker.

Continue the overall Paper G search through the repository's neural-PDE
connection. A source-only lead is [ConDiff, arXiv2406.04709](https://arxiv.org/abs/2406.04709), whose primary
abstract describes discontinuous, high-contrast diffusion coefficients. It is
an older 2024 source, not a post-closure publication trigger. Before opening
any topic cycle, check whether its contract supplies a previously unqualified
interface/flux control with a distinct finite-cost scientific residual beyond
the existing elliptic certificate parents. The relevant closed parent is
`paper_g_numerical_teacher_continuum_ranking`, in particular
`supplied_reference_certificate_is_elementary_error_propagation` and
`exact_and_stochastic_physical_supervision_have_direct_parents`. A new dataset
name or another solver benchmark cannot remove them. Only the primary abstract
was used to locate this next source; no candidate has been harvested or
re-entry authorized.
