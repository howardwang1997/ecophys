# Paper G Cycle29: physical impulse response of history-based PDE surrogates

**Subsequent status:** the supplied formulation was closed by the [bounded F2 resolution](ecomd_paper_g_history_response_resolution_2026-09-09.md). The original deferral below is historical.

**PRIVATE / INTERNAL — exploratory selection record, not public evidence.**

Session began2026-09-09T05:50:12Z. Reading and derivations were interleaved;
no prospective forecast, experiment or full hostile audit is claimed.
Companion: `research/paper_g/cycle29_question_screen_20260909.yaml`.

**Decision: one bounded F2-deferred question; no machine card or execution.**
The strongest residual is whether accurate, conservative history-based PDE
surrogates develop incorrect responses to physically specified current-time
impulses, and whether a remedy adds value beyond existing sensitivity training
and causal-confusion methods. Novelty and prevalence remain unresolved. The
two analytic checks below establish a discriminating test and a required negative
control; they do not establish a new learning algorithm or a publishable result.

## Scope and connection to completed work

The PI's current objective names ICML main, Nature Machine Intelligence and Nature
Computational Science, and requires a connection to this repository's experiments.
Paper D's current manuscript, `papers/paper_d_constraints/main.tex`, supplies the
connection: conservative autoregressive PDE surrogates, multiframe inputs and
separate physical-history response diagnostics. Its original registered study and
subsequent post-hoc analyses keep their existing evidence roles. No checkpoint,
trajectory or result array was inspected in this session. Their outcomes are not
independent evidence for this new question.

The discovery protocol now explicitly includes this repository-related neural-PDE
scope and ICML main. This changes the eligible domain, not the scientific standard
or execution authority. No market route is reopened: a declared deterministic
PDE state reset with analytic truth is not an identified intervention on latent
financial agents. Prior generic nonidentification and derivative-method results
remain mandatory intellectual comparators. There is no verified opposite-sign
pair of papers with a common estimand.

## One question, with a decisive fork

**G29-01 — Can conserving history-based surrogates forecast correctly while
misrepresenting a legal instantaneous perturbation, and can that response be
recovered without erasing physically necessary memory?**

- Native object: a periodic physical field, observed input history, known evolution
  law and a specified zero-mean instantaneous source at the current observation.
- H0: among competent full-state predictors, prior frames provide useful numerical
  context without a material loss of correctly timed impulse response; ordinary
  current-state or sensitivity-supervised baselines suffice.
- H1: training only on unforced histories permits a systematic dependence on past
  frames that reproduces forecasts but attenuates or delays the legal impulse
  response; an intervention-aware method has an additional, reproducible benefit.
- Discriminator: compare each model's current-time impulse response to the same
  analytic/solver response, alongside unforced forecast skill and physically
  consistent whole-history perturbations. A true-memory control must reject a
  universal remove-history remedy.
- Positive value: a validated response failure and a repair with a defensible
  cost/accuracy advantage could change learned-simulator use in control.
- Null value: demonstrate that existing baselines suffice or that the proposed
  failure is not material in competent models; stop the new-method claim.

This is a measurement/method question, not a claim that the generic distinction
between prediction and intervention is new. No numerical publication probability
is assigned before a complete subject-specific audit.

## Analytic check A: perfect forecasting and conservation do not fix pulse response

Let A be a unitary periodic translation on a finite Fourier space. Let P project
onto the spatial constant and Q=I-P, with AP=PA=P. The physical dynamics are
x_(t+1)=A x_t. For α∈[0,1], define a two-frame predictor

\[
 F_\alpha(y,x)=Px+A Q\big[(1-\alpha)x+\alpha Ay\big].
\]

Here y is the preceding field and x is the current field. Additional input frames
may be ignored, so the construction also embeds in a longer-history model class.

1. **Conservation:** P F_α(y,x)=Px for every history, including inconsistent ones.
2. **Perfect unforced forecasting:** if x=Ay, then F_α(y,x)=Ax. Starting from any
   consistent unforced history, every autoregressive forecast is exact by induction.
3. **Correct consistent-history response:** for Pb=0, change the history to
   (y+A^(-1)b,x+b). The next response is Ab for every α, exactly the physical
   response to changing the initial condition consistently through the history.
4. **Different current-time pulse response:** at time0 apply the source b to the
   current field after recording the preceding field. The new history is(y,x+b),
   and the physical next state changes by Ab. The learned change is(1-α)Ab.
   Its normalized error is α. At α=1 it ignores the pulse at the first step.

This last operation is a legitimate state reset in the declared forced problem,
not an unforced-history symmetry. In continuum notation it is the jump induced by
u_t+c u_x=b(x)δ(t), with the post-jump state supplied as the current observation.
No future force remains after this jump; a missing future-force input is therefore
not the cause of the discrepancy in this fixture.

The construction is not rescued by requiring bounded rollouts. In the Q channel,
unitarity gives

\[
 \|q_{t+1}\|\le(1-\alpha)\|q_t\|+\alpha\|q_{t-1}\|.
\]

Thus the maximum of the two most recent Q norms cannot increase for α∈[0,1].
More explicitly, after the pulse and with subsequent autonomous prediction,

\[
 \delta\widehat x_t
 =A^t b\,\frac{1+\alpha(-\alpha)^t}{1+\alpha},\qquad t\ge0.
\]

To verify, transform to z_t=A^(-t)δx_t; then
z_(t+1)=(1-α)z_t+αz_(t-1), z_(-1)=0 and z_0=b. The characteristic roots are1
and-α. For α<1 the physical response is asymptotically attenuated by1/(1+α);
for α=1 it alternates between the correct response and zero. This is an elementary
linear recurrence, not a new rephasing or memory law.

All these predictors have the same restriction to the manifold of unforced
histories. The example is therefore a specialization of off-support
nonidentification. We claim no novel impossibility theorem and no finding about
the trained models in the repository. Its value is the exact physical action,
stable conserving controls and a closed-form response for a future test.

## Analytic check B: deleting history is wrong under partial observation

Take one nonzero Fourier mode of the periodic wave equation. Its sampled amplitude
satisfies a_(t+1)=2cos(θ)a_t-a_(t-1), for a declared nondegenerate sampling phase
θ∈(0,π). The complete physical state includes displacement and velocity. If only
displacement is observed, two legal histories with a_0=0 and a_(-1)=±δ have next
amplitudes∓δ. Any predictor using a_0 alone gives the same output to both and has
worst-case absolute error at least δ, by the triangle inequality. Both fields have
zero spatial mean; mass/mean projection does not remove this ambiguity.

Consequently, a remedy must distinguish redundant history in a fully observed
first-order state from memory needed to reconstruct an omitted state variable.
This is standard state sufficiency, not a theorem contradicting history-space
operators. A no-history baseline may use only the same supplied observations;
silently providing velocity would change its information budget.

## Primary-work collision map

The seven retained works below supply six distinct method/problem lineages because
the two SC-NO papers belong to the same framework. F1 anchors were the spectral
audit, SC-FNO2025 and causal confusion; the bounded F2 map adds history-specific
and prescribed-forcing comparators. The audit is incomplete, not a novelty clearance.

| Work and inspected scope | What it already covers | Remaining distinction to verify |
|---|---|---|
| [Gao, Yang, Karniadakis2026, Spectral Audit](https://arxiv.org/abs/2606.02427), PDF§1–3 | Directional/Fourier Jacobian assessment against PDE tangent truth, including phase and mode coupling. | Its defined query is an initial field with fixed in-context examples. A history-time assignment test must add more than another Jacobian plot. |
| [Behroozi, Shen, Kifer2025, SC-FNO](https://arxiv.org/abs/2505.08740), v3 PDF§1–2 | Sensitivity-supervised operator learning using physical derivatives; broad forward/inverse improvements are occupied. | Correctly timed state-reset response and an equal-oracle-budget comparator require explicit matching. |
| [Behroozi et al.2026, SC-NO](https://arxiv.org/abs/2608.29888), abstract/metadata | Sampled solver-derived sensitivities, autoregression and higher-dimensional inverse problems. | A cheaper-Jacobian or rollout extension cannot be assumed new; detailed method comparison remains necessary. |
| [de Haan et al., NeurIPS2019](https://papers.neurips.cc/paper_files/paper/2019/hash/947018640bf36a2bb609d3557a285329-Abstract.html), PDF§1–3 | Extra correlates can hurt causal generalization; targeted interventions distinguish explanations. | PDE prediction is not imitation policy learning, but this is a close conceptual parent, not supporting novelty. |
| [Wen et al., NeurIPS2020, Copycat Agents](https://arxiv.org/abs/2010.14876), selected PDF introduction/method | Observation histories can expose nuisance past-action information; adversarial representation is a remedy. | Need to show any proposed temporal intervention/repair contributes beyond this parent. |
| [HS-FNO2026](https://arxiv.org/abs/2605.09523), v2 abstract/metadata | History is a true state for delay/memory PDEs; exact shift-append structure is already a proposed method. | It is a necessary-memory comparator, not an opposite-sign experiment on the same Markov PDE. |
| [STCO2026](https://arxiv.org/abs/2608.20477), abstract/metadata | Future prescribed forcing/motion conditions belong in the operator input. | Our impulse is already encoded in the current post-jump state; do not conflate the two interventions or refute STCO's full interface from its abstract. |

No dataset, software package or target results were obtained from these sources.
No source's implementation problems or development history supports the question.

## Bounded test contract and the next decisive audit

The physical target is
R_b(h,k)=S_k(x_0+b)-S_k(x_0), with a predeclared current-time reset, zero-mean b,
fixed future forcing and an unchanged earlier history. Compare the learned
response to R_b, not merely its norm. Record unforced forecast skill separately.
For the whole-history control, use its own corresponding physical reference;
do not infer a causal difference by comparing interventions of unequal total
input energy as if they were the same action.

Minimum prospective design, still unqualified:

- Separate fully observed Advection/nonlinear conservation-law targets from a
  genuinely partial-observation wave or delay target. The present two analytic
  fixtures are not two independent executed simulator lineages.
- Freeze meaningful forecast-competence criteria, state channels, forcing timing,
  response bandwidth and amplitudes before accessing a new outcome partition.
- Compare equal-data, equal-compute current-state and history models, ordinary
  impulse augmentation with correct labels, SC-NO-style sensitivity training and
  relevant temporal-dropout/causal-confusion baselines. Count solver and derivative
  labels in the cost. Keep training versus inference conservation distinct.
- For any claimed repair, require maintained forecast competence, lower physical
  response error and retention of necessary memory. A response plot or standard
  regularizer under a new name is insufficient.
- Existing Paper D weights/data are development material if later authorized;
  they cannot provide independent confirmation of the newly selected hypothesis.
  No untouched partition, power target, implementation or execution budget is
  qualified by this document.

**Next action:** complete the specific history/current-state/derivative-label
comparison in SC-NO2026, Copycat Agents and PDE-Refiner's history controls, and
inspect a suitable physical source schema without outcomes. Either identify a
distinct calibrated measurement or method contribution with an executable
falsifier, or close this formulation. Do not add another generic response-audit
variant if this bounded check fails. No F3 fifteen-work review is opened yet.

An ICML-main case remains conditional on a distinct contribution and strong
controlled evidence. NMI/NCS would additionally need a substantially broader
scientific advance and transfer evidence. Current records prove neither. The
persistent Paper G objective remains active.
