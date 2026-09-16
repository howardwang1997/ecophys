# Paper G: Koopman response and physical actuation

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

This bounded source comparison follows the closed physical-history-response
route. Its repository connection is learned PDE evolution under specified
forcing, with stochastic response also relevant to EcoMD. It creates no raw
question, candidate, re-entry audit or experiment authority.

The decisive source question was whether a newly published optimal-response
construction supplies a realizable physical input, or a response prediction
under a specified input, that changes the existing contribution/truth decision.

## Two distinct source contracts

[Froyland, Giannakis and Peters, arXiv2606.06728v1](https://arxiv.org/html/2606.06728v1),
June 4, 2026: selected Sections 2, 3.2–3.5 and 7.
The method constructs a kernel-smoothed transition matrix from observations.
It optimizes a simple eigenvalue's magnitude or phase over row-sum-zero
perturbations with a Frobenius-norm budget and disallowed entries. Section 3
distinguishes this matrix derivative from a state-space derivative. Section 3.5
maps a perturbation to coordinate-observation responses by multiplying it by
the observation matrix. This supplies an interpretation of the optimized
Markov response; the inspected construction supplies no map from a specified
PDE actuator family to its feasible transition perturbations. This last scope
judgment is our inference, not an independently observed failure.

[Zagli et al., arXiv2410.01622v2](https://arxiv.org/html/2410.01622v2),
June 18, 2025: selected Sections 2 and 3.2, especially Method 3, plus the
observation-scope statement opening Section 4. A specified drift perturbation
defines the response target. Method 3 projects the response observable using
unperturbed trajectory averages of the forcing field dotted with dictionary
gradients, then uses the EDMD Gram pseudoinverse. It avoids explicitly
estimating the invariant density. The examples use full phase-space
observations. The equations require regularity, ergodic sampling and the
integration-by-parts boundary conditions; the method does not infer an unknown
actuator from passive observations. No finite-sample certification or independent
empirical reproduction is established by this selected reading.

## Consequences for the existing route

| Selection issue | Retained conclusion |
|---|---|
| New computational instrument | A concrete known-forcing, passive-trajectory response baseline is available in the literature. |
| Matched disagreement | None: optimizing an observation-space Markov perturbation differs from predicting the response to a specified physical forcing. |
| Physical execution | A probabilistic transition constraint must not be substituted for the actual actuator and its admissible inputs. |
| Novelty | Generic passive-data response recovery is already occupied. A useful new result must specify its additional accuracy, cost or identifiable physical consequence. |
| Confirmation | An estimated response remains a prediction requiring appropriate independent validation; it is not truth by construction. |

For a future admissible comparison, freeze the physical state, executed input
family, response observable and observation clock first. If the input's action
in the observed state is known and the required dictionary derivatives and
sampling assumptions are justified, include the known-forcing method among
the baselines. Do not impose a universal requirement for intervention training
data: that would discard the useful capability above. Conversely, a coordinate
response visualization alone is not a complete actuator contract. These are
comparison requirements, not a proposed new theorem or learning method.

The parent failure codes
`generic_sensitivity_and_history_nuisance_remedies_have_direct_prior` and
`generic_statistical_accuracy_and_forced_response_have_direct_prior` remain.
No substantive blocker is removed. Stop generic Koopman-response collection
from this comparison. Further work requires a named native-response result or
new truth/control asset that passes the existing trigger gate. Merely restricting
an optimizer to a known linear input subspace does not by itself establish
publication-level novelty.

This preserves the objective of a scientifically novel, repository-related
Paper G for ICML main, NMI or NCS. Selection is still incomplete.

Related decisions:
[history-response closure](ecomd_paper_g_history_response_resolution_2026-09-09.md),
[response-source frontier](ecomd_paper_g_response_frontier_2026-09-11.md).

