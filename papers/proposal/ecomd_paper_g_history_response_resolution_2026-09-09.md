# Paper G: bounded resolution of the physical-history impulse question

**PRIVATE / INTERNAL — topic-selection analysis, not public research evidence.**

Session began 2026-09-09T06:11:21Z. This resolves the F2 deferral in
[Cycle29](ecomd_paper_g_topic_cycle29_2026-09-09.md); it is not a new search cycle,
prospective forecast, full fifteen-work review or experiment.
Structured record: `research/paper_g/history_response_resolution_20260909.yaml`.

**Decision: close the current standalone diagnostic-plus-generic-repair
formulation at its bounded F2 contribution gate.** The counterexample is valid,
but ordinary correctly labelled impulse augmentation eliminates its entire
response defect. Existing sensitivity training supplies the corresponding
derivative baseline. Neither a distinct repair nor a calibrated measurement
advantage survives this bounded comparison. This is a selection decision about
the contribution currently supplied, not a proof that trained PDE models never
have response errors, that all history is harmful, or that the broader problem
cannot support a future paper. Those empirical questions remain unresolved.

## What the nearest methods actually constrain

| Primary source and selected reading | Established scope | Consequence for this proposal |
|---|---|---|
| [SC-NO 2026](https://arxiv.org/pdf/2608.29888), sections 2–4.3 and Appendix D | Separates context from a supervised parameter field and matches sampled solver Jacobian rows. Its rollout experiment uses a current-state one-step model; the short-history trajectory predictor is a separate setup. | Correctly timed sensitivity supervision is an obligatory baseline. We cannot attribute a multiframe failure to the reported rollout experiment. |
| [Copycat Agents](https://arxiv.org/pdf/2010.14876), section 5 | The adversary observes the current target as well as the embedding while predicting the previous action; the bottleneck additionally penalizes excess information. Target-shared information is deliberately preserved. | Selective nuisance removal has direct prior. Transplanting the objective to deterministic physical fields requires an explicit nuisance/target contract. |
| [PDE-Refiner](https://arxiv.org/pdf/2308.05732), sections 2–3 and Appendix E.4 | Tests history lengths 1, 2 and 4 on KS. Reports that more history can improve the first prediction while degrading rollout, and relates this to temporal differences and error propagation. | A broad claim that history shortcuts harm PDE prediction is occupied. The paper's rollout phenomenon does not establish our stable, same-action impulse defect. |

SC-NO defines a derivative with respect to its named supervised input. To compare
a multiframe adaptation, freeze whether earlier frames are independent constants
or differentiable descendants of that input, which time is reset, and which
output time is labelled. The selected text does not qualify every such adaptation.
The algebra below therefore evaluates explicit mathematical interfaces, not an
uninspected implementation of SC-NO. Its own cost accounting includes data,
Jacobian production and training; those costs cannot be omitted here.

PDE-Refiner's refinement objective corrupts the candidate next field while
conditioning on the preceding field, then predicts the added noise; its initial
step predicts the clean next field. This is not evidence that it relabels a
physical current-state impulse. Measurement corruption with a clean target,
candidate-field refinement, and physical actuation with a changed target are
different supervised tasks. None may be substituted for another in the response
test. [Method and pseudocode](https://arxiv.org/pdf/2308.05732).

## Exact check C: derivative directions must cover the physical action

Use Cycle29's unitary translation A, mean projector P, Q=I-P and predictor

\[
F_\alpha(y,x)=Px+AQ[(1-\alpha)x+\alpha Ay],\qquad 0\le\alpha\le1.
\]

The consistent-history embedding is H(z)=(A^{-1}z,z). For every z,
F_alpha(H(z))=Az, for every alpha. Consequently all first derivatives of this
composition equal A, and all higher derivatives vanish. Arbitrarily many exact
derivative labels along this embedding do not select alpha. In contrast, for
Pb=0 the current-reset direction Vb=(0,b) gives

\[
DF_\alpha\,Vb=(1-\alpha)Ab,
\qquad D(F_\alpha\circ H)b=Ab.
\]

In finite-dimensional linear algebra, if the derivative-observation directions
span T and the target direction v lies outside T, there is a linear functional
ell that vanishes on T but not on v. Adding w*ell to a Jacobian preserves all
observed directional derivatives and changes its action on v. If v belongs to
T, those exact directional labels determine its image by linearity. This is a
standard span/identification fact, not a new theorem or a criticism of correctly
specified ambient Jacobian supervision. A current-state derivative label Ab in
this fixture directly penalizes alpha.

## Exact check D: a target-conditioned adversary need not select the extension

Work in the zero-mean subspace. On unforced paths let Y=Ax be the target and N=y
the proposed past-field nuisance. Since A is invertible, N=A^{-2}Y. The optimal
squared-error nuisance predictor receiving Y has zero risk regardless of the
embedding. It cannot impose an additional distinction between the alpha models.

More explicitly, E_alpha(y,x)=(1-alpha)x+alpha Ay equals x on every unforced
history. Using the same decoder, covariance function and bottleneck settings
therefore gives the same on-support distribution of every argument to the
Copycat-style objective for all alpha. For a stochastic bottleneck this does not
claim a zero supervised loss: it establishes equality of that loss and the other
objective terms across these extensions. Off-support pulse derivatives differ.

This is an objective-level nonidentification example, not a statement that the
published optimizer selects a harmful extension or that its imitation-learning
results are invalid. Use Bayes squared prediction risk here; differential
entropy of a deterministic continuous conditional distribution is inappropriate.

## Exact check E: an ordinary baseline removes the supplied defect

For a consistent history x=Ay and a legal zero-mean physical pulse b, the correctly
labelled next state is A(x+b). The augmented squared loss of the same family is

\[
L_{\mathrm{pulse}}(\alpha)
=\mathbb E\|F_\alpha(y,x+b)-A(x+b)\|^2
=\alpha^2\mathbb E\|b\|^2.
\]

If the pulse distribution has finite, positive second moment, its unique minimum
over this family is alpha=0. All consistent unforced forecasts remain exact and
conservation is preserved. No special causal adversary or new physical loss is
needed. This result concerns the explicit family and population objective; it
does not prove finite-sample neural optimization, nonlinear transfer, or a fair
empirical cost advantage for any method. Full-rank excitation would be needed to
identify a general matrix-valued defect; one pulse identifies this scalar family.

For complete deterministic Markov state, the current state is already sufficient
for the declared exact next-state target. The displacement-only wave control in
Cycle29 changes the observation regime: velocity is omitted. It establishes the
need to preserve information under partial observation, but does not itself
produce a tradeoff on the full-state task or require a new universal method.
Numerical discretization, observation noise and finite model capacity can create
additional issues; none has been demonstrated by these analytic fixtures.

## Source preflight: what PDEBench supplies and what is still missing

The official [advection generator](https://raw.githubusercontent.com/pdebench/PDEBench/main/pdebench/data_gen/data_gen_NLE/AdvectionEq/advection_multi_solution_Hydra.py)
exposes grid/time settings, transport speed, initial-condition generation and
trajectory/coordinate array output. Its evolution routine accepts a field and
uses numerical flux updates. This is useful source structure, not the exact
unitary translation oracle used in the proof. The inspected generator does not
itself qualify our pulse/sham lifecycle, replay manifest or confirmation split.
No generated arrays or released dataset files were accessed. This was a mutable
main-branch source inspection, without an immutable commit qualification.

The repository [license](https://github.com/pdebench/PDEBench/blob/main/LICENSE.txt)
states an MIT default with exceptions. The selected file carries separate NEC
terms describing noncommercial internal research and restrictions on distribution
and sublicensing. Therefore the default license does not qualify redistribution
of this generator or a derived public benchmark. These are source-contract
observations, not scientific evidence or a legal opinion. Dataset rights are
separate and were not inferred. The analytically specified translation fixture
does not require adopting this implementation.

No source is qualified here for execution: immutable version, complete boundary
and initialization dependencies, perturbation/restart interface, numerical truth
accuracy, release scope, independent confirmation and replication remain to be
frozen. The source limitations are not the reason for the novelty decision.

## Decision boundary and retained assets

The current proposal consists of a standard off-support counterexample, a
physically precise response check and established repair families. Checks C–E
sharpen the baseline comparison; they do not supply the missing new method,
calibration theorem or scientific measurement result. Accordingly the graph node
`paper_g_physical_history_impulse_response` becomes `failed_closed`, with the
closure restricted to this supplied formulation. The original Cycle29 deferral
is retained as historical accounting and linked to this subsequent resolution.
There is no new cycle, card, F3 audit, probability forecast or re-entry audit.

Retain the action-direction span check, the target-conditioned-adversary fixture,
the correctly labelled augmentation null and the distinction between complete
state and partial observation. Existing Paper D results retain their original
registered/post-hoc roles and provide no independent confirmation here.

A re-entry must name a substantive new result or truth/control asset that exposes
a residual after the ordinary baselines, with the same state, action, information
and cost budgets. A new PDE name, another Jacobian plot, or swapping initial-field
and current-state labels is insufficient. Any new source intake about true memory
must first specify the omitted physical state or unresolved scale; memory caused
by coarse observation cannot be treated as a redundant past correlate. Such
source/observability checking is infrastructure, not candidate-harvest authority.

The persistent ICML-main/NMI/NCS objective remains active and unfulfilled. No
outcomes, scientific implementation, solver, simulation or GPU work was used or
authorized by this resolution. Validation receipts are kept separately as
private process records and do not support scientific claims.
