# Non-auction randomized-priority search — G−1 result

> **Status amendment (2026-09-05).** The contemporaneous references below to FCC clock-1 as a
> candidate are historical. Its subsequent D−1 audit failed on identification, standard-parent,
> cross-mechanism and simulator-validation gates; see
> `fcc_clock1_random_rank_cascade_dminus1_result_2026-09-05.md`.

**Frozen:** 2026-08-24

**Verdict:** one new candidate, one parked prospective probe, no active Nature route

**Resource use:** rules, schemas, source code and literature only; no candidate outcome data, implementation, model call, EcoMD run or GPU

## Decision

The scientific question does **not** require an auction. The broader object is a stateful constrained market in
which an auditable random priority or processing order changes the state seen by later requests. A hostile search
found three serious non-auction or non-uniform-auction anchors, but only one crosses the frozen 15% T0 screening
floor:

1. **OASIS simultaneous-submission-window transmission allocation** is retained as the primary D−1 candidate.
   MISO and SPP, with BPA as a backup, use a random customer order for same-priority requests received in one
   five-minute window. Requests then consume available transfer capability sequentially. Its T0 survival prior is
   18%, but its current unconditional NCS/NMI probabilities are only about 1.5%/0.7%.
2. **DCRDEX verifiable epoch sequencing** is parked as a prospective measurement probe. Its commit–reveal proof
   makes the realized permutation replayable in principle, but there is no official permanent full-event archive,
   competitive-epoch support is unknown, the random seed can be threatened by selective non-reveal, and no
   scientifically equivalent second system exists. Its single-system T0 data-contract prior is 15–20%, but its
   unconditional NCS probability is below 2%.
3. **Nasdaq PSX 2010–2013 weighted-random residual allocation** is failed-closed under the public field contract.
   The historical feed identifies passive executions but does not document an aggressor parent/batch key or a
   random seed, so residual-lottery contests cannot be proved from standard ITCH fields.

FCC clock-1 remains a separate auction candidate. This search removes the earlier impression that random
micro-ordering must be studied in an auction; it does not activate OASIS, DCRDEX or FCC as a Nature paper.

## Common scientific object and its limit

For event (e), let

\[
C_e=(S_e^-,A_e,Q_e)
\]

contain the pre-randomization state, admissible actions and official randomization law. Let (R_e\sim Q_e) be the
realized ordering and (M(C_e,R_e)) the one-step official matching or allocation result. For frozen microscopic and
macroscopic representations \(\Psi\) and \(\Phi\), define

\[
X_e=\Psi[M(C_e,R_e)]-
\mathbb E_{r\sim Q_e}\Psi[M(C_e,r)],
\qquad
Y_e(h)=\Phi(S_{e+h})-\Phi(S_e^-).
\]

A shared descriptive target is the randomization-centered response projection

\[
K_h=\mathbb E[Y_e(h)X_e^\top]
     \left(\mathbb E[X_eX_e^\top]\right)^+ .
\]

This is not yet a new theorem. Ordinary randomization inference, local projections and linear response already
cover broad versions. It also identifies an average response projection, not an event-specific unobserved long-run
counterfactual. The only potentially irreducible result is a state-dependent, multi-constraint response operator
whose frozen spectrum or relaxation law predicts a second independent system better than sequence-only,
scalar-capacity and standard queue-order baselines.

Four counterexamples constrain all future claims:

- If the relevant actions commute in \(\Psi\), then \(X_e=0\) and there is no order susceptibility.
- In PSX, a residual winner can change labelled order inventory while leaving aggregate price-level depth exactly
  unchanged at impact time.
- With anonymous order IDs, two trader-response models can generate the same public feed and different long-run
  effects; EcoMD cannot recover the missing identity channel.
- Replaying the realized future order stream after a counterfactual ordering measures mechanical sensitivity, not
  an adaptive-market causal path.

## Candidate A: OASIS random-priority network response

### Mechanism contract

MISO, SPP and BPA rules specify a Simultaneous Submission Window. Within the same reservation priority and the
same posted-tariff/no-discount price tier, customer order is randomized and requests are processed sequentially.
The first accepted request changes available transfer capability and therefore the state faced by later requests.
This is a non-auction allocation when unequal bid-price windows are excluded.

Official anchors:

- [MISO Tariff, Module B](https://docs.misoenergy.org/miso12-legalcontent/Module_B_-_Transmission_Service.pdf)
- [SPP Business Practice 2450](https://www.spp.org/documents/37896/spp%20oatt%20business%20practices_2020_11.pdf)
- [BPA Simultaneous Submission Window practice](https://www.bpa.gov/-/media/Aep/transmission/business-practices/tbp/simultaneous-submission-window-bp.pdf)
- [18 CFR §37.6 OASIS information requirements](https://www.law.cornell.edu/cfr/text/18/37.6)

The regulation supports public queue/status/capacity disclosure in general, but it does not by itself prove that a
current observer export connects lottery position, exact pre-window flowgate state and final allocation by one
stable key. That linkage is the D−1 question, not an assumption.

### Non-triviality gate

Two requests competing for one scalar capacity are a sequential-knapsack toy, not a paper. A qualifying event must
contain at least three requests and at least two coupled constraints, with a swap in the first requests capable of
changing a third party's allocation or another flowgate's terminal state. A frozen model developed on one operator
must predict a held-out response distribution on another operator. MISO and SPP are independent operators but may
share OATI infrastructure, so they are operator replication rather than automatically software-independent
replication.

### D−1 verdict

The candidate receives a T0 survival prior of 18%, just above the activation screen, and remains **candidate only**.
The separate freeze requires public, legally reusable and linkable realization/pre/post-state fields in MISO and
SPP; enough binding multi-constraint events; an outcome-blind first-stage replay; a shared-vendor audit; and a
20-primary-work novelty audit. Any failure closes the card before effects or simulation.

## Parked probe B: DCRDEX verifiable sequencing

DCRDEX is a deployed epochized limit-order book, not a uniform-price batch auction. Orders commit to preimages;
after reveal, the protocol hashes ordered preimages into a seed and applies MT19937/Fisher–Yates to obtain a
processing permutation. The live subscription sends the epoch orders and a match proof containing preimages,
misses, commitment checksum and seed. A complete recorder can therefore validate the proof and replay the
mechanical epoch.

Official anchors:

- [DCRDEX matching specification](https://github.com/decred/dcrdex/blob/master/spec/fundamentals.mediawiki)
- [DCRDEX order subscription and proof protocol](https://github.com/decred/dcrdex/blob/master/spec/orders.mediawiki)
- [DCRDEX production repository](https://github.com/decred/dcrdex)

The public contract is live rather than archival. A pilot would require two independent recorders starting before
an epoch, exact sequence/checksum/preimage/seed verification, immutable software SHAs and a 90-day blinded support
report. Selective non-reveal and server-controlled inclusion must be audited; a proof of deterministic execution
given inputs is not proof of an unbiased seed. At least 2,000 mechanically order-sensitive epochs across three
markets in 90 days is the provisional support floor. Pairwise inversions are not independent samples: the
randomization unit is the epoch.

The route remains parked because Stellar and XRPL use transaction-set-dependent pseudorandom keys rather than an
equivalent external randomization, and direct sequencing/fairness work already occupies the broad headline.
Reopening requires support plus an independent system and a method beyond ordinary randomization inference.

## Failed historical continuous-book anchor: PSX

From 2010-10-08 through 2013-04-30, PSX first allocated whole round lots pro rata at a price and then assigned an
indivisible residual round lot by a displayed-size-weighted random function. The mechanism is genuinely continuous
and non-auction. Historical TotalView-ITCH exposes displayed order lifecycle and passive execution references, but
the public schema does not promise an incoming aggressor ID or parent/batch key for all passive fills. Match Number
identifies an execution; Tracking Number is not documented as the aggressor-grouping contract. Same-nanosecond or
adjacent-message grouping is therefore an inference, not a Nature-grade audit trail.

Official anchors:

- [SEC order approving the original PSX priority](https://www.sec.gov/files/rules/sro/phlx/2010/34-62877.pdf)
- [Nasdaq notice replacing it with price/display/time priority](https://nasdaqtrader.com/TraderNews.aspx?id=ETA2013-36)
- [PSX TotalView-ITCH specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/PSXTVITCHSpecification.pdf)
- [Historical PSX ITCH archive contract](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/PSXITCHFTP.pdf)

PSX reopens only with written Nasdaq semantics that bind all executions of one aggressor and expose every flag
needed to classify residual eligibility. Buying data or grouping by timestamp before that confirmation is
forbidden.

## Other systems closed in this screen

| System | Why the random rule is insufficient |
|---|---|
| IntelligentCross ASPEN and Lynx Periodic Match | Public feeds do not emit every empty match-event realization and omit hidden pre-state; both are also periodic/batch matching rather than a clean continuous-book alternative. |
| Fidelity/NFS CrossStream | Its continuous weighted-random priority is explicit, but the dark ATS does not publish losing candidates, rank, seed or the full book. |
| Stellar and XRPL | Execution order is reproducible, but the salt/key depends on the accepted transaction set; direct frontrunning and order-independence work occupies the broad claim. |
| Shutter, Penumbra and random-leader/proposal families | Encryption, aggregation, random leader selection or an undeployed proposal does not randomize the executed micro-order in the required sense. |
| BOINC | The server cache, RPC eligibility set and candidate pool are not in a permanent public record; it is also only weakly a market. |
| Kubernetes | Production tie sets, scores, RNG state and scheduler configuration are private, and the object is an internal scheduler rather than a market. |
| FAA slot lotteries | Rules exist, but a recent multi-event public stream with entrant list, draw order and before/after holdings was not found. |
| WEM Facility Tiebreak | Random priority is conditional on price–quantity auction clearing and its realized rank is not established as public. |
| LMArena | A randomized laboratory benchmark is not a field market or an external stateful allocation system. |

The closest broad priors include [Hersch's randomized matching proposal](https://pmc.ncbi.nlm.nih.gov/articles/PMC9803255/),
[Jurich's PSX regime study](https://doi.org/10.1142/S2282717X20500048),
[SPEEDEX](https://www.usenix.org/system/files/nsdi23-ramseyer.pdf), and
[verifiable transaction sequencing](https://arxiv.org/abs/2209.15569). These block any claim that random matching,
priority rules, fair sequencing or order dependence is new by itself.

## Final resource decision

- Create one **OASIS candidate** for a metadata/schema/support D−1; no outcome effect or simulator work.
- Keep **DCRDEX parked** until a support-only prospective recorder contract and a credible second system exist.
- Close PSX and the other subroutes under their exact data, identification or market-status failures.
- Keep FCC as a separate candidate; do not combine FCC, OASIS and DCRDEX merely to inflate novelty.
- No Nature-grade route is active. Passing a D−1 authorizes a separately frozen T0 estimand/theorem audit only.
