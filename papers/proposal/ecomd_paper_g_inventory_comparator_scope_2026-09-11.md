# Paper G: censored network inventory versus access-limited dynamic control

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. Resolve a previously unaudited primary-parent scope;
retain the sharper known-access learning-rate question as unresolved, without
creating a candidate, new cycle or theorem claim.

## Existing repository question

The [September 8 theorem follow-up](ecomd_paper_g_reentry_theory_result_2026-09-08.md)
proves an O(T^(2/3)) expected regret upper bound when the customer law is unknown
and access restoration is known and exogenous. Its comparator is the known-law
finite-horizon optimal controller with the same initial inventory, access process,
legal customer quotes and feedback restrictions. The bound is uniform in the
restoration probability, including zero. It does not settle the sharper minimax
rate. Large access-value differences do not by themselves imply learning loss.

The separate [unknown-channel search theorem](ecomd_paper_g_recovery_search_result_2026-09-08.md)
does not supply a lower bound for this question: the unknown parameter, coupling
and comparator differ. Its reduced search formulation remains closed.

## Selected primary scope

[Jiang, Jiang and Shen, AISTATS 2026](https://proceedings.mlr.press/v300/jiang26a.html)
studies a continuous, closed inventory network. Section 3.2 evaluates against the
best fixed base-stock target. Section 3 permits repositioning to any simplex
target each period; demand and routing are iid across periods. Appendix A.3
uses the fact that, at a fixed target, initial-inventory dependence is confined
to first-period repositioning cost. Section 4.3.3 stitches policy episodes by
correcting that cost. Theorem 5.1 gives the dimension-dependent upper rate;
Theorem 5.3 states a lower bound against the same base-stock comparator.

Reading: selected Sections 3–5 and Appendix A.3, including lower-bound statement
and sketch, not its full proof. The comparator definition on PDF page 4 was
visually checked. No implementation, notebook or experimental payload inspected.
The source is a strong censored-inventory learning parent, not a proved solution
of all dynamic inventory control or the repository access model.

## Why the rate cannot be transferred by its exponent

The repository has finite funded inventory and unit trading actions. During
suspension it cannot freely reposition to an arbitrary target. It also retains
a dynamic, finite-horizon comparator. A common word such as inventory, or an
exponent of 2/3 at network size two, does not identify the same statistical problem.

For a fixed cost model and horizon, comparison against a restricted policy class
gives no upper bound against all feasible dynamic policies without bounding the
comparator gap. Conversely, a lower bound against the restricted class can imply
one against the larger class only after keeping the learner, instance family and
feedback fixed. None of those model mappings is established here. This is a
standard comparator-scope observation, not a new diagnostic theorem.

## What remains to prove

Keep the known-exogenous-access rate question separate from unknown action-driven
restoration. A meaningful next paper-only step is an actual-feedback learning
argument whose uncertainty terms involve only within-access-mode continuation
differences. It must control adaptive estimation, exploration cost and the exact
dynamic comparator uniformly in restoration rate. Alternatively, give a matching
lower-bound pair with legal customer-only probing retained. No square-root rate,
matching lower bound or removal of the finite-control parent is proved here.

Stop reading this primary after the comparator/control mismatch is established;
do not audit its entire proof or crawl its code merely to enlarge the bibliography.
No blanket novelty follows from mismatch. Existing M0 closure and all experiment
restrictions stand; overall Paper G remains unqualified.
