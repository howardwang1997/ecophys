# EcoMD re-entry trigger scan, round 3

**Date:** 2026-09-04

**Mode:** outcome-blind theorem, primary-work and schema audit; this is not Cycle 17 and does not
authorize candidate harvesting

**Decision:** **NO QUALIFIED TRIGGER. No second EcoMD/market-MD ICLR paper is scientifically
defensible from the audited directions. No data outcome was accessed and no implementation,
simulator execution, SSH session or GPU job is authorized.**

## 1. Why this incremental audit was opened

Round 2 left one narrow method watch item: a representation-invariant gradient or abstention
certificate for exact hard-event simulation. The present audit tested three possible ways around that
closure and four newly visible market-data/model routes:

1. sparse-mismatch safe sim-to-real transfer;
2. sound smooth surrogates for discrete abstractions;
3. unbiased gradients for hybrid discrete--continuous controls;
4. kernel-level diagnostics for new LOB world models;
5. a public Hyperliquid level-4 lifecycle and wallet-identity archive; and
6. native Hyperliquid TWAP randomization as a possible field instrument; and
7. axiomatic recovery of market-maker inventory costs.

This was a re-entry-trigger audit under the saturation rule, not a harvest of seven new titles. Each
item was asked one question: does it remove a named blocker in an already closed route? The answer is
no in all seven cases. Three items are genuine partial capabilities, but none supplies an EcoMD paper
claim.

## 2. Safe sim-to-real transfer: a real theorem with the wrong truth contract

[Ni and Kamgarpour](https://arxiv.org/abs/2609.01418) give a finite-sample safe-transfer method for a
finite-horizon tabular constrained MDP. The simulator and target share state and action spaces,
reward and constraint definitions, and differ only in transition probabilities. Their algorithm uses
active target-environment rollouts to certify simulator-equal state--action--next-state triples and
concentrates target learning on a mismatch set. Its guarantee additionally assumes a known strictly
feasible target policy with a known safety margin and a known separation between equal and unequal
transition triples. The demonstration is a small gridworld with manually constructed safety.

[Wu et al.](https://arxiv.org/abs/2607.25207) independently provide upper and lower bounds for hybrid
offline-source and online-target learning under shifted tabular transitions. Their algorithms allow
heterogeneous source bias, but require valid state--action-specific bias information, target
interactions and coverage/concentrability. Unknown bias without sacrificing the no-worse-than-online
guarantee remains an open problem in that work.

These results are important generic progress. They do not certify EcoMD from a passive market tape:

- a public tape does not assign the candidate policy's actions or permit safe active exploration;
- no known target policy comes with a known regulatory or economic safety margin;
- public L2/L4 observations are not a complete common Markov state shared with EcoMD;
- simulator--market shift includes hidden participant objectives, information and strategic response,
  not merely a transition-kernel perturbation with known reward and constraint; and
- neither a total-variation separation nor a valid fine-grained bias bound is known for unseen market
  actions.

### Passive-certification impossibility twin

Let a behavior policy visit only action $a_0$ at state $s$. Construct two target MDPs that agree
with each other and the simulator on every transition and observation reachable under $a_0$, but
after the unvisited action $a_1$ let one enter a high-reward safe state and the other enter a loss or
constraint-violating state. Their passive-data laws are identical, while the value and safety of a
policy using $a_1$ have opposite conclusions. No passive estimator can certify simulator agreement
at $a_1$ without active coverage or an additional structural restriction.

This is exactly why the new theorems pay for target interaction and mismatch assumptions. Public
market observation does not make those assumptions disappear. The result therefore sharpens the
`prospective_counterfactual_market_simulator_validity` kill condition rather than removing it.

## 3. Smooth abstraction and mixed-gradient exits are already occupied

[S3](https://arxiv.org/abs/2608.15920) uses a differentiable reverse-simulation proxy to optimize a
finite abstraction of known deterministic, twice-differentiable dynamics. Soundness is preserved by
a separate Taylor-model reachability construction. This is not a proof that the surrogate gradient
equals a discrete response, nor a certificate that an abstraction predicts an unknown real system.
Importing S3 into EcoMD would require the very known dynamics and observation semantics that the
market problem lacks.

[Alvo, Russo and Kanoria](https://arxiv.org/abs/2605.14297) derive an unbiased mixed-gradient estimator
for hybrid action spaces: continuous pathwise terms, discrete score-function terms and their cross
term are combined under shared exogenous simulator randomness. This directly occupies the obvious
repair of joining an EcoMD continuous gradient to a discrete event likelihood. It also requires a
simulator that is smooth conditional on the discrete decision and exposes the relevant likelihoods
and replayable noise.

Together with PST, exact-forward Gumbel straight-through methods, mixed-order differentiable-simulator
gradients, score-function/control-variate estimators and coupled CTMC sensitivity, these papers leave
no unoccupied contribution in “differentiate the hybrid market simulator.” A new route would need an
actual estimator or lower bound that cannot be algebraically rewritten as those methods, plus a
proved bias--variance--cost advantage on two independent hard-event systems. No such object was found
or derived here.

## 4. LOB world-model diagnostics: good science, direct collision, ambiguous real null

[Chen and Glasserman](https://arxiv.org/abs/2608.23706) provide the strongest new diagnostic result.
On finite synthetic Markov LOBs, transformer models produce almost entirely valid event sequences yet
can learn a biased one-step kernel, fail state compression and introduce history dependence absent
from the true kernel. Kernel-level and history-level total-variation tests therefore distinguish
syntactic realism from recovery of known dynamics.

That already occupies the generic paper “do market world models learn dynamics rather than realistic
sequences?” Applying the same tests to EcoMD and the new [FlowLOB](https://arxiv.org/abs/2608.13096)
and [M3](https://arxiv.org/abs/2608.19227) generators would be a useful benchmark extension, not a new
ICLR mechanism or method. FlowLOB's future-statistic controls and M3's injected TWAPs also remain
inside-model interventions; neither observes the corresponding field counterfactual.

### Real-history diagnostic ambiguity

Let two latent level-4 states $z_0,z_1$ have the same observed L2 projection $x$, but different
next-event kernels because order age, wallet identity or a private policy differs. If history helps
infer whether the current latent state is $z_0$ or $z_1$, then

\[
P(X_{t+1}\mid X_t=x,X_{t-1:t-k})
\neq P(X_{t+1}\mid X_t=x)
\]

even for the correct generator of the observed process. A history test labels dependence “spurious”
only when $x$ is independently known to be a Markov state, as it is in the synthetic construction.
In real L2 data, the same signal can be correct filtering under a non-lumpable observation quotient.
Thus the diagnostic cannot be promoted to a real-market mechanism test without first solving the
closed L2 lumpability/state-completion problem.

## 5. Hyperliquid L4: valuable measurement asset, not intervention truth

The public [Hyperliquid L4 release](https://doi.org/10.5281/zenodo.18184441) is the most useful asset
found in this round. Its outcome-blind schema describes a contiguous December 2025 archive of
accepted and rejected order lifecycles, wallet and order identifiers, order-book changes, trades,
per-side pre-trade positions, trigger and time-in-force fields, and native TWAP identifiers. The associated
[repository](https://github.com/daojingzhai/public-trader-identity/commit/7fd7616b8a3af5193ff9efe9d5b27e4bae7c3135)
pins MIT-licensed December timing-reconstruction code. It is explicitly an early partial release:
the remaining estimation code is absent, public book diffs have no consensus block number, block
timestamp or oracle stream, and their timing and block counters must be reconstructed. No bulk shard
or empirical outcome was downloaded or inspected in this audit.

This materially improves future measurement feasibility. It does not remove the existing truth
contracts:

- the associated [identity paper](https://arxiv.org/abs/2608.04373) explicitly treats wallet identity
  as pseudonymous: one economic actor may split across wallets and one wallet may aggregate multiple
  principals;
- off-venue inventory, private beliefs, algorithms and information are absent;
- a realized order lifecycle contains one path, not randomized assignment and both same-state
  potential paths;
- the public order-status schema has no TWAP parent identifier, while `twap_id` appears only on the
  two sides of executed trades;
- one venue-month is not an independent confirmation lineage; and
- direct work already studies wallet-identity predictability, rejected/in-flight messages and native
  execution programs.

The archive is therefore a reusable truth-asset input only for a future estimand that is explicitly
wallet-level, invariant to economic-actor splitting where required, and identified without a missing
counterfactual. It does not by itself reopen rejected-intent pressure, metaorder-memory origin,
self-trade ownership, L2 lumpability or prospective simulator validity.

### TWAP randomization near-miss

The [official order-type documentation](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types)
shows a genuine randomized mechanism: users may enable a setting that adjusts each native TWAP child
size by up to plus or minus twenty percent. The
[exchange API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
records the parent asset, side, total size, duration and boolean randomize flag and returns a TWAP ID.
If every pre-match randomized child draw and its propensity were publicly linked to that parent, this
could create useful within-parent dose variation and deserves more scrutiny than an ordinary event
study.

The current public contract does not expose that assignment. The Zenodo order-status records contain
no parent TWAP ID or randomize flag; only executed trade sides carry `twap_id`. Neither the official
documentation nor the sample publishes the draw distribution, RNG seed, logged propensity or a tape
of intended children including nonfills. Although official historical
[L1 transaction archives](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data) may reveal
the user-selected parent action, their completeness is not guaranteed and the documented
[order-status schema](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/nodes/l1-data-schemas)
still does not link all child attempts to the parent.

Observed execution size cannot substitute for the missing draw. The scheduler enlarges later children
when earlier children underfill, subject to spread, liquidity, a three-percent slippage cap and a
three-times normal-size catch-up cap. Realized and later intended sizes are therefore functions of
earlier market outcomes. Parent initiation, total size, duration and enabling randomization are also
user-selected, and concurrent market interference remains. The mechanism is a **partial capability,
not an identified instrument**. Re-entry requires a frozen pre-match parent--child assignment log,
the exact or logged randomization probability, all nonfilled attempts and a separate confirmation
source before any outcome access.

## 6. Axiomatic market making does not identify an EcoMD force law

[Axiomatic Market Making](https://arxiv.org/abs/2606.09454) derives a restricted quote rule from eight
axioms and additional cost assumptions, and describes recovery of inventory-cost structure along a
single maker's changing quote and inventory schedule. It is a direct theorem parent, not an open
axiomatic niche.

The apparent EcoMD extension would infer a maker “force” from aggregate book shape or wallet-tagged
quotes. It fails twice. First, the theorem's identification discussion presupposes a maker-level
dynamic panel with inventory and proxies for beliefs and risk state; a simultaneous aggregate depth
curve is not that panel. Second, Hyperliquid wallet identifiers do not reveal the complete economic
actor.

### Aggregate-decomposition impossibility twin

For an aggregate ask-depth curve $D(p)=\sum_i D_i(p)$, choose any admissible perturbation $h(p)$
and form $D'_1=D_1+h$, $D'_2=D_2-h$. The aggregate book is unchanged, but the two makers' marginal
inventory costs, inventories and quote responses can be different. Infinitely many maker panels can
therefore induce the same observed aggregate curve. Relabelling an arbitrary decomposition as
particle forces does not identify it. Identification needs a declared maker-level dynamic panel and
state assumptions, or a partial-identification theorem invariant to that decomposition. Neither is
present.

## 7. Trigger verdicts

| Audited trigger | Decision | Genuine update | Fatal remaining issue |
|---|---|---|---|
| Sparse-mismatch safe sim-to-real | `partial_capability` | Safe transfer can exploit a small transition-mismatch set under explicit assumptions. | Active target exploration, known safe baseline/margin, common complete state and transition-only shift are absent in public markets. |
| S3 sound smooth abstraction | `not_trigger` | Smooth optimization can coexist with reachability soundness for known deterministic dynamics. | Soundness comes from the external reachability proof, not surrogate-gradient or real-market validity. |
| Hybrid mixed gradients | `not_trigger` | An unbiased discrete--continuous estimator is available. | It is the direct parent; EcoMD supplies neither a new estimator nor the full engine derivative contract. |
| LOB kernel/history diagnostics | `not_trigger` | Valid-looking paths can conceal a wrong known synthetic kernel. | The generic diagnostic is published and its real-L2 history null is not identified under omitted L4 state. |
| Hyperliquid L4 lifecycle asset | `partial_capability` | Public licensed order lifecycle, wallet, rejection, pre-trade-position and TWAP fields now exist. | Wallet is not owner, private state and assignment are missing, and direct empirical claims are occupied. |
| Native TWAP randomization | `partial_capability` | Optional exchange-side child-size randomization exists. | The public sample lacks linked parent settings, propensity/seed and intended nonfill-inclusive child draws; catch-up makes realized size endogenous. |
| Axiomatic maker-state recovery | `not_trigger` | A direct quote-representation theorem and maker-panel identification proposal exist. | Aggregate maker decomposition is nonidentified and complete maker state is unobserved. |

All seven entries are append-only in `research/discovery/reentry_trigger_ledger.yaml`. None removes a
recorded route blocker; all set `candidate_harvest_authorized: false`.

## 8. ICLR and compute decision

There is no experiment whose result would adjudicate a novel identified claim under the current
contract. A cross-model diagnostic benchmark would repeat the Chen--Glasserman contribution; training
EcoMD on Hyperliquid would measure in-sample simulation behavior without external counterfactual
truth; and fitting maker forces would estimate one arbitrary latent decomposition. More seeds or
larger GPUs cannot repair any of those failures.

The allocation is therefore deliberately zero:

- `100.113.230.38` (A800 40 GB): no SSH, staging or job;
- `100.80.236.112` (V100 32 GB): no SSH, staging or job; and
- `100.123.220.57` (V100 32 GB): no SSH, staging or job.

No experiment plan is written because an executable plan would falsely imply scientific authority.
The existing Paper D remains the only current ICLR-scale route in the repository.

## 9. Exact conditions for another EcoMD review

Do not open another search cycle in this saturated family. Re-audit only if at least one concrete
object exists before candidate harvesting:

1. **Passive-transfer theorem:** a partial-identification or abstention result for unvisited market
   actions under a declared partial-observation model, with a non-vacuous observable bound that does
   not assume the conclusion through a known fine-grained bias map.
2. **Representation-invariant world-model diagnostic:** a statistic whose interpretation survives
   latent-state refinements and observation quotients, or an L4 truth construction that independently
   establishes the claimed Markov state.
3. **Lawful intervention asset:** assigned or otherwise identified market actions with complete
   pre-state, explicit interference, a reserved confirmation family and an independently governed
   same-estimand source.
4. **Maker partial-identification theorem:** nontrivial bounds on a maker-level response that are
   invariant to wallet splitting and aggregate-book decompositions and use only declared observable
   state.

Only such an object may be entered into the re-entry ledger. A qualified trigger would then authorize
a bounded question screen, not immediate GPU use; a new machine card and machine decision would still
be required.
