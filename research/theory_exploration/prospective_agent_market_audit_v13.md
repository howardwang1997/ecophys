# V13 audit — prospective mechanism changes in algorithmic-agent markets

**Closed:** 2026-08-13

**Decision:** `V13_NO_COMMON_OBSERVABLE`

**Outcome access:** none; documentation examples and paper-reported results only

## 1. Gate table

| Gate | Result | Decisive evidence |
|---|---|---|
| G0 protocol finality | `WAIT` | EIP-7732 is still `Review`; the official consensus specifications list Gloas as unstable with fork epoch `TBD`. Ethereum.org schedules ePBS for Glamsterdam but supplies no final epoch. |
| G1 common observables | `FAIL` | Pre-period received bids are relay-selected and relay-clocked; an Ultra Sound aggregate is not all relays. Losing execution payloads are undisclosed. Post-ePBS bids would use a global P2P topic, changing the observation operator. |
| G2 identity/selection | `FAIL_FOR_ADAPTATION` | Public keys are operational identities; builders can submit through multiple keys and relay/location selection changes measured timing. No frozen alias graph or selection bounds make the within-builder policy estimand robust. |
| G3 novelty | `FAIL_FROZEN_CLAIM` | Direct work already studies latency advantage, private order flow, strategic bidding, auction efficiency and builder concentration; 2026 ePBS studies already predict free-option and centralization effects. |
| G4 prospective seal | `NOT_REACHED` | There is no final fork epoch and G1--G3 fail. |
| G5 independent replication | `FAIL` | CoW changes occurred before our freeze and concern solver rewards rather than relay removal; Jito BAM is already partially deployed and has no demonstrated public all-action contract for the same channel. |

The sequential rule stops V13 before data collection, generated power calculations or worker contact.

## 2. Protocol and observation audit

EIP-7732 would replace relay-mediated fair exchange with protocol-native builder commitments, staked builders,
in-protocol payments and payload-timeliness attestations. The EIP also introduces a global P2P topic for signed
builder bids. These are material mechanism changes, but they do not provide an immediate natural experiment:

- the EIP remains under review and the reference Gloas specification is unstable;
- off-protocol middleware may persist for features outside the core protocol;
- pre-ePBS bid timestamps are measurements at particular relays/regions, whereas post-ePBS propagation is a
  network observation; and
- the eligible builder population, key semantics, deadlines, block capacity and propagation window all change at
  the same fork.

The estimand cannot be “effect of removing relays” without a model separating these simultaneous changes. More
importantly, the bid panels do not have a common measurement scale. Ultra Sound documents `received_at`, optional
builder sequence numbers, regional auction endpoints and bid forwarding. Its aggregated analytics view joins its
own locations with delay; it is not global MEV-Boost coverage.

## 3. Direct prior-art result

The frozen hypotheses are scientifically plausible but not an unoccupied contribution:

- Wu et al. model MEV-Boost builder strategy and directly vary latency, private order-flow access and relay
  timeliness enforcement, connecting them to collusion and efficiency.
- Öz et al. measure builder bidding latency and order-flow advantages, and explicitly report the missing losing
  payload, mempool-label and single-relay limitations.
- Wang et al. model asymmetric private order flow and its feedback into builder concentration.
- Mazorra et al. identify the ePBS free option, derive signed effects of volatility, liquidity and external-signal
  value, and estimate historical counterfactual exercise rates.
- Wang et al. directly model ePBS latency and long-run builder concentration using calibrated agent-based
  simulation.
- Algorithmic competition, adaptation and collusion already have a direct NMI precedent; an identity-conditioned
  neural policy is not method novelty.

A real post-fork study could test these predictions, but “first real data after deployment” would be a measurement
contribution, not a new mechanism theory. It becomes flagship-grade only with an identified, surprising residual
and independent replication.

## 4. Second-system audit

### CoW Protocol

CoW is a strong development system: repeated solver competitions, an exact service implementation and a public
`/api/v2/solver_competition/{auction_id}` endpoint expose submitted solutions and rankings. However:

- CIP-85 changed performance/consistency rewards in 2026, and Consistency Metric v2 began on 2026-06-30, before
  this plan was frozen;
- a July 2026 preprint already studies the earlier CIP-74 solver-reward reform;
- the reward change does not remove an intermediary or reproduce the ePBS latency/private-order-flow channel; and
- using it after reading governance retrospectives would be development replay, not untouched replication.

### Jito BAM

Jito BAM is another important algorithmic block-assembly system, but it is already live for part of Solana stake;
FireBAM was announced live on mainnet in May 2026. Public material establishes implementation and adoption state,
not a complete public panel of all scheduler/searcher actions with a future sealed activation. It therefore fails
the present replication contract.

## 5. Narrow retained scientific lead

The ePBS free option suggests a sharper object than the frozen three-channel claim. A strategic builder can make a
committed payload noncanonical precisely when late information makes inclusion unfavorable. The action suppresses
the payoff-revealing outcome. Yet an empty slot is also produced by propagation or implementation failure.

`formal_cards_v13.md` proves an elementary observation equivalence: any conditional empty-slot law can be
generated entirely by strategic withholding or entirely by correlated nonstrategic failure. The real problem is
therefore not detecting a volatility correlation but finding an instrument, randomized deadline/penalty, or
independent propagation witness that separates the two hazards.

This **self-concealing mechanism action** is recorded only as a possible V14 scout. The free-option primitive and
its signed economic predictions are already published. A new paper would need a non-equivalent identification
theorem/method and a prospectively observable system; a standard competing-risk model is insufficient.

## 6. Data and compute disposition

- No relay, CoW, Jito, beacon, execution, bid, block, price, market-share or solver-competition endpoint was
  queried for values.
- Temporary PDFs were used only for primary-paper review and remain untracked under `tmp/`.
- Experiment 155 was not created or run.
- Both V100 32 GB nodes and the RTX2060 were not contacted or queued. H20 remains excluded.
- No data purchase or compute expansion is warranted.

## 7. Re-entry conditions

The real ePBS program may reopen only after all of the following are frozen before outcomes:

1. a final fork epoch and versioned executable specification;
2. a pre/post common-observable map or informative bounds under relay selection;
3. multi-vantage payload/blob propagation evidence capable of separating withholding from failure;
4. an identity ambiguity graph and key-rotation sensitivity protocol;
5. an independently governed, prospectively sealed second system; and
6. a claim that is not merely confirmation of existing latency/private-flow/concentration predictions.

Until then the correct state is closure, not a queued experiment.
