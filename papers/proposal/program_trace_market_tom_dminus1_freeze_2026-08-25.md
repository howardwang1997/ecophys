# Program-and-trace market-agent prediction: D-1 freeze

**Frozen:** 2026-08-25
**Status:** parked conditional reserve; not an active experiment
**Allowed work:** outcome-free benchmark-contract and licensing audit only

## Target

Predict a calibrated joint path law for an externally authored market agent and the market under an unseen mechanism, conditional on the frozen program, a small seen-mechanism trace set, the unseen mechanism specification, initial state, opponents, and execution environment. A version-upgrade claim must include the true program diff.

## Activation gates

1. At least 20 independently authored programs belong to the exact intersection of three genuine mechanisms with a shared agent interface. The target is 50.
2. The same unedited strategy program runs in each mechanism. Compatibility wrappers may adapt transport only and must be frozen and audited.
3. Every program has immutable source, reuse rights, container, dependency lock, model/prompt snapshot where applicable, RNG implementation and seed policy.
4. Mechanism specifications, opponent populations, initial-state generators, scoring, logs, and all intervention-relevant state are versioned and redistributable.
5. A second independently maintained market system can implement a smaller replication contract.
6. The organizer agrees to a chronological held-out upgrade or an equivalent prospectively sealed program diff.
7. An outcome-free precision/power calculation sets the required number of authors and paths; 20 is only a feasibility floor, not automatic statistical sufficiency.
8. A training-data contamination audit is possible, or the evaluation uses prospectively sealed unpublished programs that could not have entered model pretraining.

These gates are deliberately not met by the current public artifacts; that is why the route is parked. D-1 permits one bounded organizer/registry contract audit, after separately authorized external outreach, to determine whether they can be supplied prospectively. A definitive negative organizer response or a complete census showing no credible supply path closes the route. Counts may not be pooled across incompatible contests, APIs, authors, or mechanisms.

## Required baselines

- trajectory-only theory-of-mind model;
- source-only predictive executor;
- real simulator rollouts under a frozen budget that accounts for trace generation, model training and amortized inference as well as marginal test-time cost;
- edit-distance and simple static-analysis predictors;
- generic language model with the same source and trace budget;
- mechanism-specific empirical Bayes and population-average predictors.

## Frozen post-qualification kill-suite specification

D-1 freezes, but does not implement, specifications for unseen triggers, semantic refactors, one-line threshold cascades, hidden dependencies, rare hazards requiring abstention, and opponent-population shifts. Executable fixtures may be created only after every activation gate passes. Passing average reward while failing any relevant post-qualification fixture is a failure.

## Paper-level success criteria

- author-held-out and mechanism-family-held-out joint path-law improvement over every required baseline;
- preregistered calibration and selective-risk coverage, with non-vacuous acceptance;
- refactor invariance and behavioral-diff sensitivity;
- prospective chronological upgrade prediction;
- replication in the second market system;
- a theorem or impossibility boundary that is specific to cross-mechanism semantic transfer and not merely surrogate execution.

Thresholds and exact risk functionals remain unset until a qualifying benchmark contract exists. Setting them after observing outcomes is forbidden.

## Forbidden actions before qualification

- no outcome inspection, agent scoring, model implementation, training, EcoMD integration, data purchase, or GPU use;
- no claim of predicting an unspecified future version;
- no use of generated clones as independent authors;
- no relabeling of submarkets within one integrated game as three mechanism families;
- no replacement of a calibrated path law by mean score or next-action accuracy.
- no repeated organizer search after a definitive negative contract finding; no external inquiry without separate authorization.

## Probability ledger

Current public-contract estimate: T0 8--12%, complete NMI 2--4%. With the full organizer contract, prospective three-mechanism execution, and independent replication: T0 18--25%, complete NMI 6--10%. These probabilities must be revised downward if any qualification item is weakened.
