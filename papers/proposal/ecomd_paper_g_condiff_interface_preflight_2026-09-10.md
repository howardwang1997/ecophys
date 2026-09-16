# Paper G: ConDiff interface and continuum-truth preflight

PRIVATE / INTERNAL — source capability and development reasoning only.
`public_evidence_eligible: false`. Started 2026-09-09T16:37:09Z
(2026-09-10 04:37 Pacific/Auckland). Previous goal turn: progress.

**Decision: partial capability, no qualified re-entry trigger.** ConDiff provides
a specified discrete elliptic input/output interface. It does not, from this
audit, provide a paired continuum-reference intervention or a contribution
beyond existing interface methods and elliptic error estimation. The overall
Paper G objective remains unachieved. No candidate, cycle, forecast, machine
card, experiment or route activation is added.

This follows the source lead in the force-spectrum comparison and attaches to
`paper_g_numerical_teacher_continuum_ranking`, which remains `failed_closed`.
The named blockers are
`supplied_reference_certificate_is_elementary_error_propagation` and
`exact_and_stochastic_physical_supervision_have_direct_parents`. Cycles 29–30
already exhausted ordinary harvesting in this parent. This preflight is
infrastructure work, not a third renamed cycle.

## Verified source scope

[ConDiff v2](https://arxiv.org/html/2406.04709v2), dated 3 February 2025,
studies a two-dimensional stationary scalar elliptic equation with homogeneous
Dirichlet boundary conditions. Coefficients are exponentiated Gaussian fields;
covariance family, variance and contrast acceptance ranges define the sampling
regime. Its 64 and 128 grids use independently generated fields, explicitly
not paired realizations. References use a second-order finite-volume method.
These statements define a discrete benchmark; they do not establish a
sample-specific continuum-error enclosure. Selected reading: Section 2 and
limitations, with public numerical tables visible but no raw outcomes accessed.
The v1 introduction was preliminary intake; v2 governs this record.

Four small text files were read at repository commit
`e3111fc734f39f7c7d53999f650e111f18217883`:
[generator](https://github.com/condiff-dataset/ConDiff/blob/e3111fc734f39f7c7d53999f650e111f18217883/condiff.py),
[loader](https://github.com/condiff-dataset/ConDiff/blob/e3111fc734f39f7c7d53999f650e111f18217883/load_ConDiff.py),
[README](https://github.com/condiff-dataset/ConDiff/blob/e3111fc734f39f7c7d53999f650e111f18217883/README.md),
and [license](https://github.com/condiff-dataset/ConDiff/blob/e3111fc734f39f7c7d53999f650e111f18217883/LICENSE).

The source calls a sparse direct solve on its assembled matrix. Its stencil
uses arithmetic combinations of adjacent coefficient entries, Fortran-order
flattening and an `(n+1)^2` scale. The loader exposes coefficient arrays of
shape `(samples,n+1,n+1)` and RHS/solution arrays `(samples,n^2)`, under HDF5
keys `k`, `rhs`, `x`. This is a source-text contract, not a reproduced solve or
verification that hosted arrays match that commit. Root software terms are
MIT; linked dataset terms, immutable dataset revision and dependency versions
remain unqualified. No loader, generator or notebook was executed.

## What this resolves and what it does not

| Capability | Assessment |
| --- | --- |
| Named discrete coefficient-to-solution task | Specified by the selected source |
| Same underlying realization across grid levels | Not supplied by the published split |
| Continuous coefficient/RHS lift and interface geometry | Must be frozen separately before a continuum claim |
| Certified continuum observable or model-risk difference | Not established by solver order or array shape |
| Pure conservation intervention at matched approximation/optimization budget | Not established by the source |
| Untouched Paper G confirmation and independent truth lineage | Not qualified |

The lognormal-field terminology does not by itself fix a cellwise or continuous
lifting. This is a target-definition requirement, not an allegation about the
paper or its code. Cross-grid comparison also needs common latent coefficient
and forcing realizations, a fixed physical domain and a fixed observation
functional. Equal parameter labels do not supply those couplings. Stationary
elliptic data cannot automatically validate the repository's dynamical
advection or shallow-water results.

## Paper-only transmission control

The following is an elementary control, not a new theorem, an observed neural
failure, or a claim about a ConDiff sample. No numerical or symbolic experiment
was run. Let the domain be `(0,1)`, with `k=a>0` left of `1/2` and `k=b>0`
right of it, forcing one, and zero endpoint values. For any real `V`, set

\[
w_V(x)=\begin{cases}
\dfrac{x(1/2-x)}{2a}+2Vx,&0\le x\le1/2,\\
\dfrac{(x-1/2)(1-x)}{2b}+2V(1-x),&1/2\le x\le1.
\end{cases}
\]

Every member belongs to `H^1_0`, is continuous at the interface, and satisfies
`-k w_V''=1` away from it. The one-sided values of `k w_V'` are
`-1/4+2aV` and `1/4-2bV`. Hence the unique weak solution has

\[
V_*={1\over4(a+b)},\qquad
-(k w_V')'-1=\left[2(a+b)V-\frac12\right]\delta_{1/2}.
\]

Writing `d=V-V_*`, the error is the triangular function `2dx` on the left
and `2d(1-x)` on the right. Direct integration gives

\[
\|w_V-u\|_{L^2}^2={d^2\over3},\qquad
\int_0^1k|(w_V-u)'|^2\,dx=2(a+b)d^2.
\]

Thus an almost-everywhere interior strong residual and correct outer boundary
values leave an interface degree of freedom. A complete weak formulation or
the transmission flux condition removes this freedom. This does not show
that exact conservation harms generalization; the incomplete and complete
constraints are different mathematical interventions.

A second elementary control separates teacher consistency from continuum
truth. For an invertible discrete operator `A_h` and exact discrete solution
`u_h=A_h^{-1}b`, imposing **all** equations `A_h v=b` leaves only `v=u_h`.
For an approximate solution, `v-u_h=A_h^{-1}(A_h v-b)`. After a fixed lift
`I_h`, continuum error additionally contains `I_h u_h-u`. A scalar global
balance or a subset of equations generally leaves a larger nullspace.
Invertibility and the lift are explicit hypotheses; no matrix was assembled
or tested here. This is standard linear algebra, not a new correction method.

## Minimal collision check

[Tseng, Lin, Hu and Lai, v2](https://arxiv.org/html/2210.08424v2), published in
JCP in 2023, already formulate solution/flux transmission conditions in
Section 2, introduce a cusp feature in Section 3.1, and include separate
interior, interface and boundary losses in Section 3.2, Eq. 15. Generic
interface penalties or cusp features therefore have a direct neural-method
parent. Their representation intervention is not a matched causal comparison
of hard versus soft conservation at equal capacity and optimization cost.
No claims from their numerical tables are reproduced here.

The existing goal-error audit already pins neural DWR, functional majorants
and FOSLS. A flux/adjoint certificate must still satisfy their conformity,
constant and integration requirements. Substituting high-contrast data does
not remove the recorded contribution blockers. HANO, contrast-robust
upscaling and other search results were routing leads only; they were not a
full neighborhood review or evidence of a literature-wide absence.

The deeper repository question—whether a correct constraint improves
out-of-distribution prediction or reallocates error into admissible channels—
is not answered by this method collision. A useful discriminating observation
would need the same continuous problem, target functional, valid intervention,
representation and resource budget. Existing source comparisons do not yet
qualify that observation. Positive and null empirical results would both be
ambiguous without these controls.

## Frozen truth contract and stopping decision

1. **Estimands:** fixed continuum cell-average or bounded linear observable;
   L2 model-risk differences are separate from energy error and grid-label fit.
2. **Assignment/interference:** pair the same coefficient/forcing realization
   across legal interventions; freeze interface geometry, input information,
   architecture class and optimization/reference-query budgets.
3. **Lifecycle/replay:** domain, continuous lift, covariance/dependency version,
   all random streams and rejection rules, grid/ordering, boundary treatment,
   solver arithmetic, independent certificate and observation operator.
4. **Rights/ethics/release:** public article reading and pinned MIT software
   text only. Dataset/dependency use and release remain separately unqualified.
5. **Untouched confirmation:** absent; published splits are not automatically
   an untouched Paper G confirmation partition.
6. **Independent replication:** one generator/source lineage; neither the
   1D hand control nor another grid supplies independent 2D truth.
7. **Cost:** include coefficient generation/rejection, reference solves,
   certification, training and target estimation; no cost forecast qualified.
8. **Stop rules:** no further ConDiff metadata collection, added benchmark
   rows, interface-loss variants or generic elliptic certificates as re-entry.

Re-entry requires a named same-condition primary disagreement or a control/
theorem that removes a recorded blocker, validated in the trigger ledger
before harvesting. Continue the overall Paper G search through that gate;
the next substantive task is a primary-comparison audit of the original
conservation/generalization fork with representation and truth held fixed.
Do not substitute another dataset for that scientific disagreement. No full
15-work audit, implementation, outcomes, GPU, outreach or publication is
authorized by this record.

The formal result, source manifest, contract, trigger ledger, graph, memory
and daily log jointly preserve this update. Their validation checks record
consistency, not novelty, physical truth, or journal readiness.
