# Paper G: conservation-comparison and contribution-scope audit

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Started 2026-09-09T16:53:31Z (2026-09-10 04:53 Pacific/Auckland).
Previous goal turn: progress. Overall Paper G objective: active, unachieved.

**Decision: not a qualified primary-disagreement trigger.** Three primary
works materially narrow the interpretation of the original conservation/
generalization question. They do not supply opposite predictions for one
matched intervention. Broad constrained-versus-unconstrained performance,
coordinate-wise error concentration and training-versus-deployment attribution
cannot be claimed as a fresh Paper G contribution on this evidence.

This is a bounded comparison audit following the ConDiff preflight, attached
to the closed `paper_g_numerical_teacher_continuum_ranking` parent. It is not
a new question cycle. The named elementary-reference-certificate and
exact/stochastic-supervision contribution blockers remain. The work neither
reopens the parent nor closes every possible conservation-related question.

## Same words, distinct interventions

| Selected primary | Native prediction and constraint | What the comparison can establish | What cannot be inferred |
| --- | --- | --- | --- |
| [Beucler et al., PRL 2021, v5](https://arxiv.org/html/1909.00912v5), main formulation and SM B.1–B.3 | Convective column tendencies/fluxes; some outputs computed from analytic conservation relations | Residual-coordinate choice and loss weights affect the allocation of error under valid hard constraints | An opposite prediction about the same downscaling or SWE intervention |
| [Harder et al., v9](https://arxiv.org/html/2208.05424v9), Sections 3.1–3.2, 4.1–4.3 and conclusion | High-resolution reconstruction conditional on coarse values; additive, multiplicative and positive constraint layers | Known coarse averages supply output information; their validity differs between synthetic averaging and independently simulated resolutions | A generic guarantee about dynamical invariants or all constrained predictors |
| [Huang and Greenberg, ICML 2025, v1](https://arxiv.org/html/2506.05513v1), Sections 3–5.3 and Appendices F/H/I | Hybrid SWE height prediction and INS velocity evolution; mean-corrected updates or curl increments, with separate symmetry factors | Systematic constraint/symmetry comparisons within stated grids, models, training and initial-condition shifts | A matched-ID-and-compute comparison across all mechanisms, or an opposing same-condition primary prediction |

Beucler already reports error concentration at outputs selected to complete
the constraints, and explores reweighting those outputs. This is published
behavior of the defined model family, not an internal implementation-error
story. Merely observing such concentration elsewhere is insufficient novelty.
Its Section II.3, Eqs. 8–9, also already relates conservation residuals to
squared errors and cross terms, explicitly withholding an a-priori accuracy
prediction. A generic error-cancellation explanation therefore also has a
direct primary parent.

Harder's synthetic coarse inputs are averages of fine targets. The same
paper distinguishes separately simulated low/high-resolution data, discusses
constraint mismatch, and includes a time-split OOD task. Its positive results
therefore cannot be contrasted with another paper's mismatched-constraint
result to manufacture a scientific disagreement.

Huang and Greenberg compare symmetry groups at matched parameter counts,
with validation-based early stopping; equal parameter counts do not imply
equal training cost or ID error. Their SWE model predicts height and uses
a physical velocity update at rollout. Their INS construction adds a curl
increment to the previous velocity (Eq. 80): it is not a claim that all
velocities are represented by a zero-mean curl alone. Constant velocity modes
must not be falsely declared absent. No numerical result was reproduced here.
The [official proceedings record](https://proceedings.mlr.press/v267/huang25j.html)
verifies ICML 2025 publication.

## Reused algebra and one conditional-accounting control

The already-recorded affine projection identity remains the correct null.
Let `P` be the orthogonal tangent projector of an affine constraint in the
**evaluation** inner product. If the target satisfies that constraint,
orthogonal projection of a fixed prediction removes the normal error and
leaves the tangent error unchanged. This is not an empirical discovery.
Changing the metric, constraint value, fitted model or rollout input changes
the question; multiplicative correction is not automatically this projector.

For the additive patch-mean case, let `q` be a fixed vector of `n` predicted
fine values, `y` the target, and `m` the supplied coarse value. Direct
orthogonal decomposition gives

\[
\|q+(m-\bar q)\mathbf1-y\|_2^2-\|q-y\|_2^2
=n\big[(m-\bar y)^2-(\bar q-\bar y)^2\big].
\]

With `m=bar(y)`, the improvement is exactly the removed mean error, on any
test distribution. With an imperfect coarse value it has no universal sign.
This instantiates the existing projection-risk identity; it is not a new
theorem or a claim about errors in the cited datasets.

A useful additional bookkeeping consequence concerns matched ID risk. For
two already chosen predictors `f_H` and `f_U`, define their errors relative
to the same feasible target. Suppose `f_H` satisfies the affine constraint
and their population ID squared errors both equal `r`. Then

\[
R_{P,\mathrm{ID}}(f_H)-R_{P,\mathrm{ID}}(f_U)
=R_{I-P,\mathrm{ID}}(f_U).
\]

This follows immediately by splitting `r` into orthogonal channels. An
increase in the tangent channel **on the matching distribution** is forced
by the conditioning; it does not identify optimizer-mediated error transfer.
The equality supplies no sign for OOD risk. Nor does matching a scalar
post-training risk make architecture, optimizer trajectory or training cost
identical. This is a paper-only control, not a proposed new evaluation method.
No model was trained, selected, reweighted or numerically evaluated.

## Repository overlap and what remains scientifically open

Only the contribution-description portion of current Paper D related work
was inspected (`papers/paper_d_constraints/main.tex`, lines 98–117). It
already targets a same-checkpoint training-by-deployment interaction, crossed
output coordinates and autoregressive feedback, with a parameter-gradient
mechanism question. This is a scope comparison, not a Paper G use of Paper D
results or internal development history. A renamed version of that experiment
does not satisfy the requested new-paper objective.

The historical August 27 D-3 question remains context, not a current forecast
or authority. Its broad novelty and publication expectations are not adopted.
The residual scientific uncertainty is more specific than whether constraints
ever help: which *additional native information or physically valid response
restriction* distinguishes two explanations after the established projection,
representation and training effects are accounted for? The three papers do
not jointly answer that question or supply a qualified opposite-sign fork.

## Stop and next decisive source check

Stop generic hard/soft/projection comparisons, matched-ID error decompositions
and renamed Paper D attribution as candidate generators. No blocker is removed.
No candidate harvest, cycle, full fifteen-work audit, forecast, machine card,
implementation, outcome access, GPU or publication is authorized.

A bounded source-only next lead comes from Huang Appendix F: local flux
representations versus global correction for domain-size transfer, citing
McGreivy and Hakim's *Invariant preservation in machine learned PDE solvers
via error correction* (ICLR workshop, 2023). This is an existing literature
pointer, not a new-publication trigger or an admitted topic. First locate the
primary work and test whether “local flux” actually restricts the response:
freeze the PDE, pressure/elliptic solve, boundary conditions, flux receptive
field and time step. A local divergence stencil alone does not establish a
local domain of dependence. If the supposed distinction is only a standard
projection, finite-volume identity or physical pressure nonlocality, stop at
that reduction. Do not open a new family by relabeling the same question.

The comparison contract freezes target, intervention, replay, rights,
confirmation, independent replication, full cost and stop conditions. Public
article tables were visible during reading; no raw outcome, notebook, source
code, archive or model payload was accessed. Records and cache checks only
verify provenance/consistency, not scientific novelty or venue readiness.
