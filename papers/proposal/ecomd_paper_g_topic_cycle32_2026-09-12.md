# Paper G Cycle 32: cross-domain ML question screening

Date: 2026-09-12. Status: six F1 screens; five closed formulations and one F1
deferral. No F2, F3, machine card or publication-readiness finding.

The PI broadened discovery to scientific ML in finance, physics, biology,
chemistry and materials, targeting ICLR/ICML main. This round samples two
measurement, two empirical-intervention and two theory questions. Its start
record precedes generation; the individual questions and decisions below were
composed during literature reading and are not prospective experimental
preregistrations. Ten primary works are retained, within the twelve-work limit.
The scope decision and administrative details are in the linked internal records.

## Screening result

| Program | Archetype | Decision | Decisive issue |
|---|---|---|---|
| Perturbation-specific transcriptomic prediction | Measurement | F1 closed | Generic metric correction and strong linear comparison already have direct parents. |
| Assigned genetic dose transfer | Empirical intervention | F1 closed | Measured guide abundance and response scores do not establish assigned-dose truth. |
| Reaction uncertainty under specified condition shifts | Measurement | F1 deferred | A distinguishable target exists; stress-data calibration and contribution remain unqualified. |
| Impurity reports as recipe-success supervision | Empirical intervention | F1 closed | Unreported impurity is not verified purity; co-occurrence is not failed synthesis. |
| BO with failed synthesis | Theory | F1 closed | Generic observation failure has prior art; changing the utility alone is elementary. |
| Local potentials under nonlocal charge changes | Theory | F1 closed | Generic locality obstruction and long-range remedy have direct prior art. |

These decisions concern the formulations below, not the viability of entire
fields. A route-graph search found no exact prior formulation for these native
objects. Earlier market/PDE closures do not constitute a cross-domain veto.

## 1. Perturbation-specific transcriptomic prediction

**Object and action.** Gene-specific expression response at a fixed cell
context and batch under a specified genetic perturbation. Compare models with
the same held-out interventions and the same external biological information.

**Rivals.** Apparent predictive skill reflects perturbation-specific response,
or mainly shared response and unequal prior information. The discriminator is
a specificity-aware evaluation against matched linear/additive baselines.
A positive result establishes the biological signal captured; a null result
validates that the tested performance survives shared-response controls.

[Ahlmann-Eltze et al.](https://www.nature.com/articles/s41592-025-02772-6)
provide strong linear/additive comparisons for their tested models.
[Systema](https://www.nature.com/articles/s41587-025-02777-8) directly targets
systematic variation in perturbation evaluation. Thus “correct the metric and
compare with a linear baseline” is insufficient as the new contribution.
Different papers' headline rankings, with different models or information,
are not a matched scientific disagreement. Close this generic formulation;
retain the comparator requirements.

## 2. Transfer from guide abundance to assigned genetic dose

**Object and action.** Response to externally assigned knockdown dosage at
fixed guide, cell context and assay time. The rival explanations are causal
dose transfer versus selection through cell state, guide expression and
measurement. A calibrated, externally assigned dose ladder separates them.
A positive finding supports intervention prediction; a null finding bounds
abundance-conditioned predictions to their observed context.

[X-Atlas/Orion](https://www.biorxiv.org/content/10.1101/2025.06.11.659105v1.full)
uses sgRNA abundance stratification as a knockdown-efficacy proxy.
[Perturbation-score work](https://www.nature.com/articles/s41556-025-01626-9)
studies heterogeneous response using expression-derived scores.
Neither selected source establishes the proposed externally assigned dose
contract. A measured post-treatment proxy can be scientifically useful without
being the assigned intervention. Close the proxy-as-assignment formulation
at the empirical early-truth gate. This is not evidence that abundance-based
prediction fails, nor that a suitable dose resource cannot exist.

## 3. Retained F1 question: uncertainty-to-stress transfer in reactions

**Question.** At matched nominal yield, classification margin and repeatability,
does a nominal aleatoric score predict the loss caused by a declared
temperature or moisture perturbation on held-out reactions? The response is
the difference in expected assay yield between a contemporaneous nominal
control and the specified perturbed condition. It is not nominal classification
accuracy, repeatability alone, or an unspecified notion of robustness.

**Source evidence.**
[Zhong et al.](https://www.nature.com/articles/s41467-025-59812-0) use
posterior-averaged classification entropy as their aleatoric score. They
report three repeats for each of 75 selected reactions and compare
scale-associated literature collections. Their published repeatability
validation must be acknowledged; it is not absent. The selected comparisons
do not establish this question's matched, declared stress intervention.
The paper links an HTE release at
[Zenodo](https://doi.org/10.5281/zenodo.12920294); a calibrated stress-response
schema in that release has not been verified.

**Rivals and value.** A transferable chemical sensitivity signal makes the
nominal score incrementally useful under a new stress law. Alternatively, it
primarily captures nominal class ambiguity or within-protocol variability.
The first answer would justify a low-cost process-selection signal under
specified conditions. The second would establish where stress-specific
calibration is necessary. Neither result is currently observed.

### Elementary truth control, not a novelty claim

Let the local yield surfaces for two hypothetical recipes be
\(Y_A(u)=0.2+0.1u_1\) and \(Y_B(u)=0.2+0.1u_2\).
Under nominal independent Rademacher inputs \(u_1,u_2\), both have identical
yield distributions, means, variances and success probabilities at the
20-percent threshold. Their oracle nominal class entropies are identical.
With a declared shift \(u\mapsto u-0.2e_1\), expected yield loss is 0.02
for A and zero for B, with all yields still in the physical interval.

This construction proves only that a scalar nominal score need not identify
direction-specific loss. It does not prove that learned scores are empirically
uninformative, that actual reaction surfaces are linear, or that a model with
additional structural/stress information cannot distinguish the recipes.
The direction and distribution of a perturbation matter. This is elementary
and cannot serve as a new theorem.

### Minimum distinct measurement result

The possible contribution is a calibrated assessment of **incremental stress
prediction at a fixed information budget**, not simply the above counterexample.
Predeclare one stress family and measure:

1. Baseline nominal prediction, class margin and replicate variability.
2. Incremental out-of-sample stress-loss prediction from the aleatoric score.
3. A condition-aware predictor integrating over the declared perturbation law,
   with all stress labels charged to its calibration budget.
4. Performance across held-out substrate families and subsequently a distinct
   stress family, keeping confirmation labels untouched.

[Oliveira, Ott and Ramos](https://proceedings.mlr.press/v89/oliveira19a.html)
already model uncertain inputs in BO. Input-distribution-aware prediction is
therefore an obligatory comparator family, not an invented algorithmic claim.
Comparisons between a nominal-only method and a stress-calibrated method must
show their different information costs; an equal-budget comparison is separate.

The cheapest next decisive work is a bounded source/schema and collision
screen: locate explicit assigned and executed conditions, reaction identity,
nominal/shifted pairing, batch and replicate records, assay calibration,
release rights, and a partition that can be reserved without viewing outcomes.
Uncalibrated assay proxies must retain their measurement label. Published
group-level repeatability summaries cannot substitute for these fields.
One candidate only is retained; no wet-lab activity, data-payload inspection,
model implementation or training is authorized by this document.

**Stop conditions.** Close if the only contribution is “noise is not shift
robustness,” if the available outcome is solely nominal feasibility, or if a
direct matched prior already supplies the proposed measurement result. An
assay and perturbation contract is required before an empirical test. Main-track
potential additionally requires a useful transferable result or method beyond
criticizing one study; that standard has not yet been met.

## 4. Impurity reports as physical synthesis-success labels

**Object and action.** Phase-pure target production under an assigned
solid-state recipe. The rivals are learnable physical success versus
reporting-dependent labels. Independently assigned recipes with complete phase
assays would discriminate them. Positive value is reliable synthesis selection;
null value is a defensible boundary between predicting reports and predicting
physical outcomes.

The [impurity-recipe dataset](https://www.nature.com/articles/s41597-025-06222-y)
explicitly captures impurity coexisting with the target. An unreported impurity
is not certified absence. [Positive-unlabeled synthesizability
learning](https://pubs.rsc.org/en/content/articlehtml/2025/dd/d5dd00065c)
is also an existing parent. The proposed recipe-specific success label and
assignment are unqualified, so close this empirical formulation. Preserve
the resource's legitimate multilabel/report-extraction use.

## 5. Optimization with failed observations versus failed production

**Object and action.** Select a recipe with success probability \(p(x)\) and
conditional successful utility \(f(x)\). An absent assay of an existing outcome
and an attempt producing zero useful product define different targets.
The rivals are valid optimization of the desired utility versus conditional
selection that silently changes it.

For recipes with \((p,f)=(0.1,0.9)\) and \((1,0.6)\), optimizing conditional
successful yield selects the first; optimizing expected useful production
selects the second (0.09 versus 0.6). This elementary control clarifies the
target and is not a new theorem. Positive value is preventing the wrong
objective; null value is validating the missing-observation abstraction when
appropriate. [Iwazaki et al.](https://proceedings.mlr.press/v258/iwazaki25b.html)
already address stochastic observation failures in BO. Do not claim their
assumptions cover arbitrary informative missingness. Close the generic
proposal: no distinct rate, identification result or chemical intervention
has been specified.

## 6. Local potentials with nonlocal charge-state changes

**Object and action.** Local force/energy response when remote charge or
polarization changes at a fixed local atomic neighborhood and declared
electrostatic boundary conditions. Rival explanations are descriptor
sufficiency versus missing long-range state. A same-neighborhood,
different-global-state comparison with a long-range comparator discriminates
them. A positive result limits a descriptor's physical regime; a null result
supports locality within the tested regime.

[Polarizable long-range foundation potentials](https://www.nature.com/articles/s41467-025-65496-3)
are direct prior art for the generic remedy. Same local input with different
physical response is a standard insufficiency argument. Without a distinct
architecture, physical regime result or nontrivial theorem, close this
formulation. This does not establish adequacy of every existing long-range
model.

## Record and next decision

The six full question contracts are in
[the internal screening record](../../research/paper_g/cycle32_question_screen_20260912.yaml).
The route graph records five terminal formulations and one candidate at F1.
No scientific result has been generated; paper-only controls are explicitly
elementary. No forecasts were added or retroactively assigned.

Paper G now has 61 screened formulations in 16 cycles, with zero machine
cards. The detailed ledger contains 23 cycles and 145 raw questions; including
its historical baseline gives 32 cycles and 201 raw questions. These are
screening counts, not counts of publishable topics.
