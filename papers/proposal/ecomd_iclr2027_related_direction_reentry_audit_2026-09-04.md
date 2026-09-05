# EcoMD-related ICLR 2027 re-entry audit

**Date:** 2026-09-04

**Mode:** outcome-blind repository and primary-literature audit under the search-family saturation rule

**Decision:** **NO-GO / KILL. No new topic cycle, machine card, experiment plan, simulator run, or GPU job is authorized.**

## 1. Decision in one paragraph

There is no scientifically defensible second ICLR 2027 paper to start from the molecular-dynamics-style
market-simulation program on the evidence available today. The closest method questions are real, but none
currently has an irreducible contribution: long-horizon differentiation reduces to established truncated or
unrolled-gradient work; stochastic pair subsampling reduces to Random Batch Method theory that already shows
long-time and phase-transition bias; exact gradients through market ties and event-order changes meet an
established discontinuity boundary; and market-simulator validity still lacks an assigned, replay-complete
external counterfactual. The decision is based on those hard gates, not on a probability threshold. The joint
chance of discovering, validating, and writing a genuinely new method by the current deadline is only low
single digits as a diagnostic judgment, not a registered forecast.

## 2. Why this is a re-entry audit rather than Cycle 17

The repository has already completed Cycles 10--16 with 84 raw question programs and no machine card. The
same simulator-method, standard-parent, and field-truth families are saturated. The governing
[runbook](../../docs/research_topic_exploration_runbook.md) therefore forbids another venue-first or
relabelled cycle until an append-only trigger removes a recorded blocker. This audit tests plausible triggers;
it does not harvest new candidates and it does not backfill an F3 forecast.

The ICLR 2027 [official call for papers](https://www.iclr.cc/Conferences/2027/CallForPapers) sets the abstract
deadline at 2026-09-18 AoE and the paper deadline at 2026-09-25 AoE. Starting on 2026-09-04 leaves fourteen
days to the abstract and twenty-one days to the paper. That interval cannot honestly contain a new theorem or
algorithm, two-system validation, market bridge, strong baselines, ablations, robustness checks, and a
reviewable manuscript.

The repository is also already on `paper-d-iclr-2027-completion`, with the substantially completed ICLR paper
[When Are Exact Conservation Layers Plug-and-Play?](../paper_d_constraints/main.tex). Diverting all three
workers to an unqualified EcoMD idea would directly compete with a much stronger existing submission.

## 3. Repository evidence that the old positive route cannot simply be resumed

1. The broad “first differentiable/Langevin market simulator” claim is closed by prior art. The canonical
   route node `first_differentiable_langevin_market_claim` records Langevin-market, differentiable-ABM, and
   differentiable-financial-simulator collisions.
2. The learned equivariant-potential branch already failed: MACE-lite obtained 0--4/11 across eight variants,
   with force magnitudes 60--190 times too small and a per-node readout that smoothed the dynamics. A larger
   model or another GPU sweep does not supply a new scientific object.
3. The state-complete EcoMD v1 release test failed its frozen positive-model gate. Every one of ten stationary
   held-out windows scored 2/11; robust misses included tail index 6.74 versus 3.52, squared-return ACF 0.011
   versus 0.115, DFA 0.586 versus 0.853, leverage near zero versus -1.066, and volume correlation near zero
   versus 0.409. See the canonical [release record](../../.claude/memory/project_ecomd_release_v1_2026-08-10.md).
4. Earlier apparent 5--8/11 frontiers are not a clean rescue target. The audit found burn-in-contaminated tail
   and impact claims, evaluator semantic defects, Mac-to-large-run non-transfer, and objectives computed from
   chunks containing only about seven returns. The valid explicit long-rollout objective test was
   indistinguishable from baseline (`p = 0.81`), closing loss-weight tuning as a mechanism.
5. Cycle 16 already gave the strongest simulator-validity formulation a frozen full audit. The exact-paper gap
   survived, but the question failed because simulator-native scores do not identify off-support participant
   adaptation, two rule changes are only two independent policy environments, learned and structural engines
   lack a common action language, and the available field assets do not jointly expose assignment, complete
   state, rights, and the same estimand. See the [formal result](ecomd_discovery_loop_topic_cycle_16_prospective_simulator_validity_result_2026-08-26.md).

## 4. Six requested direction families and their decisive tests

These rows map the user's requested directions to existing closures. They are not fresh F0 programs and do
not open a search cycle.

| Direction family | Market-native object and rival explanations | Result that would discriminate | Hard audit result |
|---|---|---|---|
| EcoMD v2 stationary fidelity | Joint stationary law of return, volatility, volume, and order-flow observables. **H1:** learned interactions are the missing mechanism. **H0:** transient/evaluator artifacts or class misspecification explain the old score. | Fresh, untouched stationary windows under a repaired evaluator, with mechanism ablations and equal-budget non-MD baselines. | **Kill.** The existing held-out failure is broad, and no new mechanism class or uncontaminated confirmation partition has been supplied. More seeds or capacity cannot repair that gate. |
| Long-horizon statistic gradients | Gradient of a stationary market statistic with respect to simulator parameters. **H1:** the model failed because training chunks were shorter than the statistic's support. **H0:** the model class cannot generate the target law. | A new estimator or coverage theorem with calibrated bias/variance and lower cost than direct rollout on analytic truth and two independent systems. | **Kill.** ARTBP, unrolled neural-physics training, differentiable-simulator gradient estimators, and the new learnability-window theorem occupy the generic core. No market-specific theorem or new estimator remains. |
| Stochastic-pair/SPS long-run bias | Invariant law and phase boundary under random pair subsampling. **H1:** unbiased instantaneous forces preserve the full interaction law. **H0:** batching noise changes invariant measures or phase transitions. | A uniform long-time coupling or correction that beats known Random Batch Method bounds and survives a hard phase-boundary example. | **Kill.** The parent literature already establishes the method, long-time invariant-measure error, and phase-transition shifts. An EcoMD case study would be a conformance audit, not an ICLR contribution. |
| Exact differentiable hard transactions | Response derivative at queue depletion, price-time ties, and event-order reversals. **H1:** event-aware differentiation gives useful exact gradients. **H0:** the target map is structurally discontinuous. | A guarantee uniform through simultaneous/order-changing events while preserving the exact transaction rule, plus a lower-bound-matching estimator. | **Kill.** The repository's two-bidder tie counterexample proves that rule-exact discrete allocation is not everywhere differentiable; current differentiable-simulator work studies estimator bias/variance around the same nonsmooth boundary. Smoothing changes the rule. |
| Prospective interventional simulator validity | Path-law response to an unseen legal market-rule or trader action from a fixed pre-state. **H1:** a simulator-native intervention score predicts real response error. **H0:** off-support strategic adaptation breaks transport. | Several independently governed assigned interventions, complete replay state, a common action/observation grammar, and sealed outcomes. | **Kill now.** LOB-Bench and interactive generators measure conditional realism and response, not the missing same-state field counterfactual; Cycle 16's truth contract remains open. |
| New symmetry/equivariant market potential | Market response under an explicitly legal relabelling or symmetry. **H1:** the symmetry removes sample complexity without deleting heterogeneity. **H0:** the imposed symmetry identifies behavior that the observable state cannot support. | A market-native invariance, an analytic sample-complexity or generalization result false for generic GNNs, and a misspecification boundary on two systems. | **Kill.** SE(3) is domain-mismatched, trader permutation is broken by private state and role, and a new architecture alone repeats the failed MACE/equivariant branch. |

No row survives its weakest link. Averaging engineering feasibility, available GPUs, or an appealing physics
story against a fatal novelty or identification failure would violate the protocol's Pareto/weakest-link rule.

## 5. Trigger audit

### 5.1 Temporal learnability theorem: not a trigger

Livi's 2026 [Learnability window in gated recurrent neural networks](https://journals.aps.org/pre/abstract/10.1103/843n-yshj)
is a genuine new theorem-level development after the last market-simulator cycle. It strengthens the diagnosis
that temporal credit has a finite, optimizer- and tail-dependent learnability window. It does **not** provide a
new unbiased long-run gradient estimator, invalidate the standard-parent reduction, distinguish missing
market mechanism from optimization failure, or supply two non-EcoMD truth systems. The generic neighborhood
already includes [ARTBP](https://arxiv.org/abs/1705.08209),
[unrolled neural-physics training](https://doi.org/10.1016/j.cma.2024.117441), and
[differentiable-simulator policy-gradient analysis](https://proceedings.mlr.press/v162/suh22b.html).
Decision: `not_trigger`.

### 5.2 Random Batch Method long-time and phase results: not a trigger

EcoMD's stochastic pair sampler is an instance of the method introduced in
[Random Batch Methods for interacting particle systems](https://doi.org/10.1016/j.jcp.2019.108877).
The literature already studies [ergodicity and long-time behavior](https://arxiv.org/abs/2202.04952), while
Guillin, Le Bris, and Monmarché explicitly analyze the
[effect of Random Batch Method on phase transition](https://doi.org/10.1016/j.spa.2024.104498).
These results make the proposed bias question scientifically important but also remove its novelty as a
generic method question. No new correction, sharper market-specific boundary, or theorem escaping the parent
class is present. Decision: `not_trigger`.

### 5.3 Interactive generators and benchmarks: capability without truth

[TRADES](https://doi.org/10.3233/FAIA251249) generates state-conditioned order flow and reacts to an
experimental agent; [LOB-Bench](https://proceedings.mlr.press/v267/nagy25a.html) supplies conditional response,
impact, and discriminator metrics. The 2026 ensemble-imitation simulator is already recorded in the trigger
ledger. These are useful implementations, but none assigns a real legal action in a fixed complete state and
observes both the treated response and a same-state counterfactual. They therefore do not remove Cycle 16's
field-truth, transport, or independent-replication blockers. No new ledger entry is needed for already-audited
capability.

## 6. Compute decision

The current [machine decision](../../research/discovery/current_machine_decision.yaml) authorizes only the
unchanged Paper D held-out continuation on specified V100 work. It does not authorize a new EcoMD selection,
implementation, outcome access, A800 run, or three-worker campaign. Because no trigger or card passed here:

- no SSH session was opened to `100.113.230.38`, `100.80.236.112`, or `100.123.220.57`;
- no code, config, data, checkpoint, process, or remote filesystem was changed;
- GPU allocation for this proposed paper is exactly zero.

This is the required consequence of the user's “kill if novelty or science is inadequate” instruction.

## 7. Exact conditions for a future re-entry

There are only two credible ways to change this decision.

### Method trigger

Supply a new estimator or theorem that is not decomposable into ARTBP/unrolled training, Random Batch Method,
existing differentiable-simulator estimators, invariant-measure gradients, or ordinary nonsmooth smoothing.
Before a market application it must:

1. state analytic bias, variance, and cost guarantees, including an event-order or long-time lower boundary;
2. beat equal-budget direct rollout and mature parent methods on analytic truth;
3. validate on at least two independently maintained non-EcoMD systems with hard negative regimes; and
4. expose a market-native residual that disappears under neither clock, batching, relabelling, nor state
   completion.

### Truth/control trigger

Supply a lawful, versioned asset with assigned legal actions, complete event lifecycle and replay pre-state,
declared interference units, licensed outcomes, an untouched confirmation partition, and independently governed
same-estimand replication. Simulator responsiveness without that external target is not enough.

Only after one trigger is appended as `qualified_trigger` may a new D-1 card and machine decision exist. A
conditional later GPU design would keep hardware pools separate: the two V100s would run independent canonical
system/seed arrays, and the A800 would run scale/OOD cells only after reproducing a canonical V100 job. Every
cell would have a frozen config, seed, git SHA, checkpoint cadence, equal-budget baseline, and stop rule. This is
a re-entry contract, not current authorization or an experiment plan.

## 8. Recommended action

Do not start a second EcoMD-derived ICLR 2027 paper. Preserve the negative results and the two reusable audit
assets—long-horizon objective-support diagnostics and random-batch invariant-law checks—but treat them as QA
and future theorem seeds. Concentrate the remaining ICLR window on Paper D's anonymity/submission blocker.

