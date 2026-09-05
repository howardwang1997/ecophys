# EcoMD Hyperliquid TWAP assignment-reconstruction audit

**Date:** 2026-09-04

**Stage:** outcome-blind truth-asset/re-entry audit; not a topic cycle or machine card

**Decision:** **PARTIAL CAPABILITY / NOT QUALIFIED**

**Authorization:** no data or outcome access, parser implementation, node deployment, EcoMD work,
SSH, simulation or GPU use

## 1. Question and first-failure decision

Can the missing pre-match assignment tape for Hyperliquid's randomized native TWAPs be reconstructed
uniquely by joining `node_twap_statuses`, `node_order_statuses`, fills and `replica_cmds`, at least on
a collision-free subset?

The answer is conditional rather than affirmative. A frozen compatibility graph can certify a
subset only after an authoritative scheduler, exhaustive order-source taxonomy and complete attempt
stream have already been established. The public schemas do not establish those premises. They keep
the parent TWAP identifier and randomize flag in one stream, omit the parent identifier and source
tag from order-status rows, and attach `twapId` to executions rather than every intended attempt.
Replica commands expose actions but no documented internal-child provenance map. The unofficial
reverse-engineered source sharpens the apparent schedule but supplies neither an authoritative child
emission rule nor the randomizer, draw, rounding rule or child-order identifier.

Therefore the attempted reconstruction removes **zero** hard blockers. It cannot support a
design-identified field benchmark, a new ICLR method claim or any experiment. The previous truth-
asset preflight is sharpened, not rescued.

## 2. Observed objects and the missing join key

| Object | Relevant fields | What remains absent |
|---|---|---|
| TWAP status | parent `twapId`; user, asset, side, total and executed size, duration, start, reduce-only, `randomize` | intended child size/draw, child OID, propensity and rounding |
| Order status | user, asset, side, original/remaining size, OID, timestamp, status, order type, TIF, optional client ID | parent `twapId`, TWAP/source tag and random draw |
| Fill/trade | execution, OID and nullable `twapId` | rejected and zero-fill attempts; intended rather than executed dose |
| Replica command | block/action index, acting user and action payload | a documented bijection from internal scheduled children to order-status OIDs |

The pinned [Bitquery schemas](https://github.com/bitquery/streaming_protobuf/tree/08e6e0648db9a350b7620106eaabe2e9fd777afa/hyperliquid)
make the parent/order separation explicit. The independently written
[Sorella order-status parser](https://github.com/SorellaLabs/hyperliquid-db-rs/blob/8f9d4828e4aad8ed9c336225db4802a622f1887e/hyperliquid-db-core/src/hl_fs/schemas/node_order_statuses.rs)
corroborates the order fields and likewise has no TWAP-parent field. Both repositories had no
detected repository license at the audited revisions and neither is protocol authority; they are
corroboration, not a rights or semantics contract. The official L1-schema evidence from the parent
preflight remains controlling.

The [SQD replica-command schema](https://docs.sqd.dev/en/data/hyperliquid/hyperliquid-replica-cmds)
provides action metadata and payloads. It does not state that subtracting signed user actions leaves
exactly the native-TWAP children, nor does it enumerate every alternative exchange-generated source.
Consequently an unmatched order is not a documented TWAP child merely because it lies near an
expected slice time.

## 3. Exact reconstruction criterion

Assume hypothetically that a versioned scheduler and complete source contract produce a finite set
of intended TWAP attempt slots $S$, and that $C$ is the complete set of candidate pre-match order
records. Freeze a compatibility graph $G=(S,C,E)$ using only pre-outcome fields: user, asset, side,
reduce-only state, legal time window, size support, source class and any exact scheduler constraints.
Represent allowed missing or non-TWAP records by explicit dummy vertices rather than deleting them
after seeing outcomes.

**Proposition 1 (linkage identification).** Let $\mathcal L(O)$ be all matchings compatible with the
frozen observed record $O$ and all declared conservation constraints. A linkage-dependent estimand
$\theta$ is point identified exactly when

$$
  \theta(L)=\theta(L') \quad \text{for every }L,L'\in\mathcal L(O).
$$

The full linkage is identified exactly when $|\mathcal L(O)|=1$. In the ordinary one-to-one graph
case, given one perfect matching $M$, it is unique exactly when $G$ has no $M$-alternating cycle.

**Proof.** The first two statements are the definition of identification as constancy over all latent
completions compatible with the observations. For the graph statement, the symmetric difference of
two distinct perfect matchings decomposes into alternating cycles. Conversely, flipping the edges of
an alternating cycle in $M$ produces a second perfect matching. Capacity or cross-row constraints
can be expanded into slot vertices; in the general case the operative test remains whether the full
feasible-assignment set is a singleton. ∎

This is an audit criterion, not a novel machine-learning result. A degree-one row is a certificate
only relative to the declared candidate set. It says nothing if a legal order source was omitted or
the scheduler that generated $S$ is only guessed.

## 4. Two-parent non-identification witness

Consider two simultaneously active randomized parents for the same user, asset, side and reduce-only
state. Their legal due windows overlap. Two zero-fill order-status rows have sizes lying in both
parents' allowed support and share the same admissible time window. Because neither row has a parent
identifier, the compatibility graph contains the four edges of $K_{2,2}$. It has two matchings,
obtained by swapping the rows between parents.

Both latent linkages preserve every public order row. Because the attempts do not fill, both also
preserve each parent's aggregate executed-size path and every fill record. Yet they pair each size
with a different parent history, adaptive base size and conditional randomization law. A parent-
conditioned excursion effect, normalized dose response or propensity-weighted world-model loss is
therefore not a function of the observations.

Time ordering does not resolve the witness when the due windows overlap, and aggregate size
conservation does not resolve it for zero fills. Restricting to one apparent parent per time window
removes this alternating cycle only under two unverified assertions: the exact scheduler generated
all true slots, and every non-TWAP/internal order source has been exhaustively labeled. The public
records do not certify either assertion.

## 5. What the reverse-engineered source does and does not establish

The pinned [unofficial recovered source](https://github.com/can1357/hl/tree/999556f6e0a474b8312db96ec3149e1c44e97c23)
reports a per-user schedule keyed by a parent/order identifier, an initial fire approximately one
second after placement, thirty-second advancement, progress fields, retry buckets and adaptive
termination. This is useful hypothesis generation for a future official audit.

It is not admissible ground truth:

- its README states that it was reverse engineered from a stripped binary, is unofficial, omits
  `Cargo.toml` files and is not compilable as supplied;
- no repository license was detected at the pinned revision;
- the inspected TWAP handler and time module do not recover the child-size randomization formula,
  RNG state/draw, rounding/cap order, emitted child OID or a parent-to-child log key; and
- several fields remain explicitly unknown.

Accordingly, it cannot freeze the scheduler, justify copying code, certify exchange randomness or
turn timestamp proximity into a unique link.

## 6. Why probabilistic linkage is not the missing scientific contribution

Existing work already combines uncertain linkage with causal inference. Shan, Thomas and Gutman
use Bayesian linkage plus multiple imputation and require a strongly non-informative linkage
assumption. Guha and Reiter jointly model linkage, outcome, propensity and covariates. Zhu et al.
address treatment measurement error through a nonparametric instrumental-variable estimator.

These methods can propagate uncertainty **conditional on their models and identification
assumptions**. They cannot certify that an omitted internal source is absent, recover a protocol RNG
that was not logged, or make a latent treatment sequentially randomized. A posterior over parent
links is not a randomization distribution.

There is one logically valid weaker object: the identified set

$$
  \Theta(O)=\{\theta(L):L\in\mathcal L(O)\},
$$

or a world-model ranking that is invariant over all $L$. But its coverage is valid only if
$\mathcal L(O)$ contains every lawful data-generating completion. Without scheduler and source
completeness, even the set is falsely narrow. With those premises supplied, matching-polytope bounds
and robust ranking would still need a theorem or empirical target beyond established record-linkage,
measurement-error and robust-assignment machinery before becoming ICLR-scale. No such irreducible
residual is evidenced here.

## 7. Randomization-law qualification

An exact propensity is not logically necessary for every model-based conditional-mean analysis if
one assumes sequential ignorability and estimates the treatment law. That weaker route, however,
would be observational with respect to the unlogged mechanism and incomplete hidden scheduler state.
The proposed field-truth benchmark specifically needs design credibility: the intended child dose,
complete conditioning history, positivity and either known probabilities or an auditable mechanism
that makes as-if-randomness defensible.

The official documentation gives a parent flag and an up-to-±20% support statement. The audited
public and recovered sources give no exact distribution, versioned rounding/cap order, RNG
commitment or logged draw. Unique parent linkage, even if later obtained for a subset, would not by
itself clear this independent blocker.

## 8. Hostile decision table

| Claim | Verdict | Reason |
|---|---|---|
| All intended children can be reconstructed uniquely now | **FAIL** | parent key/source tag absent; collision and source-completeness witnesses remain |
| A frozen unique-matching test could certify a restricted subset | **CONDITIONAL** | true only after authoritative scheduler, complete attempt stream and exhaustive source taxonomy |
| Reverse engineering supplies the randomization design | **FAIL** | unofficial, incomplete, unlicensed and no recovered draw/law/link |
| Bayesian linkage restores field-randomized identification | **FAIL** | propagates model-based linkage uncertainty under assumptions; does not recover design assignment |
| “Causal inference under TWAP linkage error” is unoccupied | **FAIL** | causal record linkage and treatment-measurement-error methods are direct generic parents |
| The residual ICLR benchmark is executable | **FAIL** | assignment, rights, confirmation, replication and same-action simulator contracts remain absent |

This audit is not a new F3 screen, so no retrospective T0 probability is written. The family has now
received its bounded truth-asset and reconstruction checks; further relabeling is forbidden until a
new qualified trigger is recorded.

## 9. Exact re-entry object

Re-audit only if an official or lawfully releasable, version-pinned source provides all of:

1. a source tag and parent `twapId` on **every** intended child order-status event before matching,
   including rejection and zero fill, or a cryptographically/verifiably equivalent bijection;
2. the versioned conditional size law, adaptive base computation, rounding/caps and RNG draw or
   commitment needed to defend sequential randomization;
3. complete block-ordered prestate and lifecycle coverage with a written completeness SLA;
4. lawful derived-data/benchmark release and the prior preflight's identity-ethics controls; and
5. an untouched future partition, independently governed replication and at least two independent
   world-model lineages implementing the identical action/state/clock/outcome grammar.

A release satisfying only item 1 removes the linkage blocker, not the randomization or real-bridge
blockers. Even all five items authorize only a bounded question screen; a machine card and new
machine decision are still required before data access, implementation, EcoMD integration or GPU
work.

## 10. Primary and schema sources added by this audit

1. Bitquery, pinned Hyperliquid TWAP/order-status protobuf schemas:
   https://github.com/bitquery/streaming_protobuf/tree/08e6e0648db9a350b7620106eaabe2e9fd777afa/hyperliquid
2. Sorella Labs, pinned Hyperliquid order-status schema:
   https://github.com/SorellaLabs/hyperliquid-db-rs/blob/8f9d4828e4aad8ed9c336225db4802a622f1887e/hyperliquid-db-core/src/hl_fs/schemas/node_order_statuses.rs
3. Unofficial recovered `hl-node` source, pinned revision:
   https://github.com/can1357/hl/tree/999556f6e0a474b8312db96ec3149e1c44e97c23
4. SQD, Hyperliquid replica-command schema:
   https://docs.sqd.dev/en/data/hyperliquid/hyperliquid-replica-cmds
5. Shan, Thomas and Gutman, *A multiple imputation procedure for record linkage and causal
   inference*: https://doi.org/10.1214/20-AOAS1397
6. Guha and Reiter, *Regression-assisted Bayesian record linkage for causal inference*:
   https://doi.org/10.1016/j.jspi.2023.07.004
7. Zhu et al., *Causal inference with treatment measurement error*:
   https://proceedings.mlr.press/v180/zhu22a.html
