# Paper G: IND–SHAP controller comparison

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. The proposed opposing-event interpretation is not
established by the selected sources. This is a bounded comparison of a named
pair, not a new discovery cycle or a scientific result.

## Source comparison

| Dimension | IND | SHAP–DRL |
|---|---|---|
| Information role | Approximate decomposition of opposition-control input | Learned importance field supplies a training reward |
| Runtime observation | Present wall-normal velocity | Local streamwise and wall-normal fluctuations |
| Flow | Two-wall channel; reported Re_tau 180 and 395 | Open channel; Re_tau 180 |
| Intervention | Full, informative or residual opposition signal | Learned blowing/suction policy with action constraints |
| Comparison scope | Specified decomposed controllers | Policies trained with different rewards |

IND already implements closed-loop DNS and discusses policy-dependent
decomposition. Its control example conditions on a zero-lag wall-shear target;
its delayed prediction example is a separate task. See [Arranz and
Lozano-Duran, JFM 1000:A95](https://doi.org/10.1017/jfm.2024.1007), Sections 3.2–3.3,
and the preceding IND scope record.

The second source reports drag and modeled actuation-energy comparisons. Its
SHAP controller reaches extreme action values less often than direct-drag DRL.
Reduced action extremes do not establish an opposite prescription for IND's
sensor events. Actor observations and volumetric reward construction are
different information roles. See [Beneitez et al., arXiv:2504.02354v2](https://arxiv.org/html/2504.02354v2),
Figures 1–4, equations 5–6, and Methods. Selected HTML only; supplementary
material, implementation and outcome arrays were not inspected.

## Inference and stopping boundary

The comparison does not match native state, conditioning, policy class or
boundary conditions. Similar Reynolds numbers and wall actuation alone cannot
establish a contradictory physical prediction. Neither a performance ranking
nor attribution-guided control proves an unrestricted intervention theorem.
These are scope judgments, not newly demonstrated failures of either method.

Generic first-control, first-energy-accounting and blanket future-target-leakage
claims are unavailable here. No contribution blocker was removed. Stop expanding
this pair by citation or code crawling. Reconsider only with a specified
same-state, same-information, same-action response for which named explanations
make distinct predictions after established baselines. A prospective experiment
must separately specify estimand, action cost and confirmation; this record
does not authorize one. Paper G remains without a qualified topic.
