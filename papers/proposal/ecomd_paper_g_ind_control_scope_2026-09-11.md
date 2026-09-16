# Paper G: informative decomposition and executed control scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. Previous goal turn: progress through the response
frontier review. This audit answers a named source question: does the original
IND work already implement control, and does it require future targets at
deployment? Repository connection: neural-PDE physical-response validation.

## Verified primary scope

[Arranz and Lozano-Duran, JFM 1000, A95 (2024)](https://doi.org/10.1017/jfm.2024.1007),
published 5 December 2024, Sections 3.2-3.3, describes an approximate
current-measurement controller and executed DNS opposition-control comparisons.
Wall-normal velocity measured near the wall drives wall blowing/suction.
Three controllers use the total, estimated informative, or estimated residual
velocity, at friction Reynolds numbers 180 and 395. Training starts from a
baseline controlled simulation. The paper explicitly discusses how actuation
changes the information decomposition. Its control decomposition uses zero
target lag; the forecasting example uses a different lag and observation
history. A residual-amplitude rescaling comparison is also reported.

The real-time approximation takes present velocity, not the future wall stress.
The forecasting section separately approximates decomposed inputs from available
history and matches baseline history information. Thus the target-conditioned
analysis is not the entire deployment pipeline. The source provides an aIND
code/example link, but no repository, checkpoint or DNS implementation was
inspected here. Published controller performance is prior evidence, not a new
Paper G result or independently repeated experiment.

## What changes in the research decision

The general assertion that informative-flow decomposition has never been tested
in closed-loop flow control is ruled out by this source. The 2026 vortex-gust
paper's proposed future intervention remains a statement about its own
configuration; the two papers are compatible. Channel wall actuation is not
localized removal of a vortex-gust structure.

Keep three distinct tests: a decomposition's observational information content,
an approximate sensor-to-actuator controller's realized effect, and a statement
about all possible actions. The reported comparisons establish a particular
control application. They do not, by themselves, identify the best controller
over an unrestricted action class, or equate zero predictive information under
one policy with zero influence under every intervention.

Any future comparison must freeze the sensing plane, available history, target
lag, baseline policy, actuator law, flow-driving condition and evaluation
quantity. The source's actuation-induced distribution change is already explicit;
it is not a newly discovered failure. Its drag-reduction metric must not be
silently replaced by a net-energy metric. A velocity-amplitude control is useful
without proving equality of every physical actuation cost.

## Stop rule

Retain the concrete opposition-control parent and the online-approximation
boundary. Stop generic first-control-validation, future-target-leakage and
policy-shift narratives from this source. This does not imply that every new
method or result is occupied; it means no specific contribution beyond the
parent has been supplied here. No recorded contribution blocker is removed.
Require a named same-action unresolved prediction or a substantive residual
after the existing controller and information-matched baselines before re-entry.
No code, data, model, experiment, forecast, candidate cycle or machine card.
The full ICML/NMI/NCS Paper G objective remains unachieved.
