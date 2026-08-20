# Liquity V2 Agentic Priority Queue: Outcome-Blind D0 Freeze

**Frozen:** 2026-08-20, before querying the frozen event-support counts

**Target:** conditional *Nature Machine Intelligence* field study; *Nature Computational Science* only with a new general method and cross-system validation

**Status:** D0 support audit authorized; outcomes, queue reconstruction, EcoMD, and GPU work forbidden until D0 passes

## Decision in one sentence

Test whether Liquity V2 provides a sufficiently large, auditable field setting in which autonomous rate managers and self-managing borrowers compete for position in the same redemption-priority queue; stop the route if the frozen support and transport gates fail.

## Scientific question

Liquity V2 orders redemption exposure by borrower-selected interest rates. Borrowers may manage their own rate or delegate a batch to an autonomous rate manager (ARM). The official ARM monitors its debt-in-front buffer and changes the rate of its whole batch. This creates a rare public field system in which human and autonomous controllers act on the same ranked resource-allocation mechanism.

The candidate question is:

> Does autonomous queue management reduce the managed borrowers' redemption exposure by exporting rank risk to unmanaged borrowers, and does shared automation create synchronized rate-adjustment waves or crowding?

This is a real-protocol question, not a simulator-error paper. EcoMD is downstream and is used only if a validated field mechanism later requires a generative counterfactual.

## Claim boundary

### Known mechanism

- Lower-rate Troves are redeemed first within a collateral branch.
- A batch manager changes the rate of an entire contiguous batch and reinserts that batch in the sorted queue.
- Liquity's official ARM monitors debt in front, redemption fees, and time since adjustment.
- Strategic priority queues, scheduling identities, and algorithmic crowding are established areas. We cannot claim that rank competition or queue externalities are new in general.

### Exact accounting lens, not a novelty claim

For Troves with debts \(d_i\) and debt ahead \(Q_i\), a fixed debt multiset satisfies

\[
\sum_i d_i Q_i
=
\frac{1}{2}\left[\left(\sum_i d_i\right)^2-\sum_i d_i^2\right].
\]

If managed debt \(D\) moves ahead of crossed debt \(C\), the managed exposure reduction is exactly \(DC\), transferred pairwise to the crossed positions. Reordering changes who bears priority exposure, not its aggregate debt-weighted amount. This is a protocol-specific decomposition based on standard pairwise accounting, not a new theorem.

The empirical analysis must keep three channels separate:

1. **Rank channel:** redistribution of redemption exposure across borrowers.
2. **Price channel:** higher rates may support BOLD demand and reduce aggregate redemption pressure.
3. **Fee/timing channel:** frequent or premature adjustments create fees and timing costs.

### Earliest defensible NMI claim

After a preregistered D1 and a held-out prospective test, a defensible claim would be that autonomous controllers measurably redistribute exposure between machine-managed and self-managed borrowers, with quantified benefits, externalities, heterogeneity, and policy counterfactuals. D0 alone supports no such claim.

### Additional burden for NCS

NCS requires more than this field result:

- a new stochastic-priority-system identification or calibration method;
- formal identifiability or error guarantees beyond the accounting identity;
- validation outside Liquity, preferably in a second queueing or allocation system;
- a frozen, method-dependent prospective prediction;
- EcoMD only if it is validated as a counterfactual engine against those real observations.

Without those additions, the appropriate ambition is NMI or a strong computational social-science/financial-systems venue, not NCS.

## D0: support-only audit

The original scientific contract is `configs/empirical_physics/liquity_agentic_queue_d0_v1.yaml`. Formal
execution now uses the resumable transport child
`configs/empirical_physics/liquity_agentic_queue_d0_v3.yaml`; it recursively proves every scientific section
equal through v2 to v1. Version 2 replaced the incomplete dRPC log witness with OnFinality while retaining dRPC
for historical state. Version 3 only groups OnFinality's address filter and adds a sanitized per-chunk
checkpoint after the public endpoint exhausted its rate limit. See
`liquity_agentic_queue_d0_transport_amendment_2026-08-20.md` and
`liquity_agentic_queue_d0_recovery_amendment_2026-08-20.md`. The contract pins:

- official Liquity core and ARM repositories by commit and file hash;
- all three mainnet branches and official ARM addresses;
- one immutable end block and block hash;
- four event signatures and the only fields that may be decoded;
- two independent public RPC transports and three source-blind qualification shards;
- sample-size gates chosen before any event counts.

D0 may decode only:

- event type;
- Trove operation or batch operation code;
- Trove ID and batch-manager address;
- canonical log identity, branch, block number, transaction hash, and block timestamp.

D0 must not decode or retain rates, debt, collateral, redemption amount, redemption price, queue rank, adjustment direction, or any market outcome. Raw RPC responses are not retained.

### Frozen pass gates

All gates must pass:

- exact full log-identity replication across Blockscout and OnFinality, with dRPC as the independent historical
  bytecode witness;
- nonempty contract code at the frozen height for every branch's TroveManager and BorrowerOperations;
- at least 500 unique opened Troves and 100 ever-batched Troves;
- at least 50 official-ARM Troves, with at least 15 in each of two branches;
- at least five registered batch managers and three managers with at least two rate updates;
- at least 30 official ARM rate updates, with at least eight in each of two branches;
- at least 200 manual rate adjustments from at least 75 unique Troves;
- at least 50 redemption transactions on 25 UTC dates and two branches;
- at least 20 official ARM rate updates within 24 hours of a same-branch redemption, spanning ten UTC dates and two branches;
- complete event classification.

The thresholds are minimum support for a credible human-versus-agent event study and matching design. They are not estimates of the expected counts.

### Stop rule

Any failed source, deployment, transport, or sample-support gate closes this Liquity NMI route before outcome analysis. No threshold relaxation, post-hoc window expansion, synthetic support, queue reconstruction, D1, EcoMD, or GPU rescue is allowed.

## Work after a D0 pass

### D1: separately frozen observational design

Before decoding any numerical event fields:

- define treatment at the Trove and batch levels;
- reconstruct time-consistent queue states with no future information;
- predefine human comparators, exact exclusions, censoring, and attrition handling;
- separate manager-selection effects from within-Trove switching effects;
- predefine negative controls and placebo timestamps;
- freeze primary outcomes for rank exposure, redemption incidence, costs, and spillovers;
- freeze clustered uncertainty at manager, Trove, transaction, and time levels;
- reserve the final chronological period for a prospective test.

### D2: mechanism and policy tests

- event study around autonomous rate changes;
- matched self-managed comparator and within-Trove switch design;
- debt-weighted exposure-transfer accounting;
- tests for synchronized rate changes and strategy crowding;
- heterogeneous effects by branch, debt size, queue density, and redemption regime;
- policy counterfactuals such as update-frequency limits, randomized tie-breaking, and externality charges.

### D3: general method and NCS escalation

- formulate the observed system as a stochastic priority queue with endogenous control;
- establish what is identifiable from event logs and snapshots;
- develop a long-horizon calibration or invariant-measure method if existing tools fail;
- validate on at least one non-Liquity allocation system;
- make and score a frozen prospective prediction.

## Data requirements

### D0 — free, public, sufficient now

- official Liquity source repositories;
- Ethereum block headers, contract bytecode, and four event families;
- official documentation binding three addresses to the ARM label.

No paid data, wallet deanonymization, off-chain prices, or proprietary labels are needed.

### D1/D2 — still mostly free

- full decoded Liquity events and canonical queue snapshots or deterministic reconstruction;
- transaction senders/receipts for controller provenance and gas costs;
- BOLD and collateral prices from auditable on-chain pools and oracle feeds;
- Stability Pool and redemption-split state;
- contract creation traces or verified bytecode for manager classification;
- optional public frontend/delegate registries.

The last chronological interval remains untouched until the prospective test. Crash or stress periods cannot be used for tuning.

### Stronger publication tier

Potentially useful later, but not required for feasibility:

- archived mempool/order-flow data to study anticipation or front-running;
- verified off-chain ARM execution traces or canister logs from Liquity/DFINITY;
- borrower/delegate interviews or consented strategy labels;
- a second field system with comparable priority allocation.

These would require collaboration or data purchase only after the public-data design demonstrates value.

## Compute requirements

### D0

- CPU only, at most 12 core-hours;
- under 0.25 GB of derived metadata;
- zero GPU-hours and zero paid-data cost.

### D1/D2

- CPU/RAM for event decoding and queue reconstruction: approximately 100–500 core-hours and 64–256 GB RAM peak, depending on snapshot frequency;
- modest storage: approximately 0.1–1 TB including verified raw and derived data;
- the current two V100 32 GB nodes may run CPU jobs, but their GPUs should remain idle unless a learned model is preregistered.

### NCS-scale method work

- initial method feasibility: current two V100 32 GB GPUs are adequate;
- cross-system models, hyperparameter robustness, and large seed arrays may require additional heterogeneous non-H20 GPU/CPU workers;
- workers must remain separated by GPU type and benchmarked against canonical V100 jobs;
- no plan assumes H20 access.

## Decision tree

```text
D0 source + transport + support
├── fail -> close Liquity route; record why; no outcomes/GPU
└── pass -> freeze D1 before numerical decoding
    ├── no credible human-agent contrast -> descriptive systems paper at most
    ├── robust field externality + prospective result -> NMI candidate
    └── plus new general method + cross-system validation -> conditional NCS candidate
```

## Immediate execution order

1. Commit and push this freeze plus the audited D0 implementation and tests.
2. Run or resume the v3 multi-provider D0 from a clean worktree and an external sanitized checkpoint.
3. Publish the immutable manifest and a concise pass/fail decision.
4. If and only if D0 passes, draft and commit a separate D1 preregistration before decoding numerical outcomes.
