# EcoMD selective-participant-identity truth-asset trigger audit

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Market-outcome access, implementation, simulation, SSH, and GPU work:** not authorized

## 1. Executive decision

Two apparently participant-resolved data sources were screened as possible external truth for an
EcoMD participant-ecology or response-learning paper.

The Mendeley release *Anomaly bias Stock Trades and Order Dataset* fails at the source contract. Its
official record does not name the exchange, market, instrument universe, date interval, acquisition
channel, identifier construction, matching rules, or an associated paper. The archive contains only
two CSV files and no README or data dictionary. Calling `MEMBER_CODE`, `CLIENT_ID`, and `TRADER_ID`
distinct entities is a convention stated by the depositors, not an audited identity guarantee.

Nasdaq TotalView-ITCH is authoritative and materially stronger. Its public specification exposes a
day-unique displayed-order reference, nanosecond timestamps, add, execute, cancel, delete, and replace
messages, and an MPID on attributed add messages. Nasdaq also hosts several public full-day sample
logs. This is genuine lifecycle and partial participant information.

It is nevertheless not complete participant truth. Attribution is an order attribute selected by
the participant; the same feed has unattributed add messages. One member may request supplemental
MPIDs, while one member or broker can aggregate multiple customers. Non-displayed orders have no add
message, and the current non-cross trade message nulls its order reference. The public tape therefore
cannot assign all actions, inventory, information, or cross-venue activity to stable economic actors.

This failure is exact rather than merely practical. For anonymous orders, any conditional allocation
of actions among hidden actors produces the same observed ITCH law. Without a restriction or an
external validation sample for the participant-chosen attribution mechanism, the full participant
distribution and its intervention response are unidentified. This is the standard
missing-not-at-random problem. Clustering observable orders does not repair it: a cluster label
`C=g(X)` adds no information conditional on the features used to construct it.

The broad scientific claims are also occupied. Prior work already clusters MBO events into behavioral
roles, studies persistent market-member trading networks, measures the predictive value of public
wallet identity, and models signaling and collusion through identity-revealing order features.
Generic informative-label and MNAR methods cover the obvious statistical repair. Neither source
therefore reopens an ICLR-grade EcoMD route. No data rows were accessed and all three GPU workers stay
outside this route.

## 2. Exact question and rival explanations

**Market-native object.** Let `A_t` be an accepted order action, `M_t` its economically relevant
actor, `R_t` the indicator that the public message carries an attributed identifier, and `X_t` the
public order-book state and message fields. The candidate question was whether the newly located
archives identify stable participant-conditioned transition or response laws

\[
K_m(x, a, dx') = P(X_{t+1}\in dx'\mid X_t=x,A_t=a,M_t=m)
\]

well enough to ground EcoMD particle types or interactions.

- **H1 — participant truth:** stable identifiers and complete order lifecycles turn the aggregate
  tape into an observed interacting population; participant-conditioned responses can anchor EcoMD
  types and distinguish strategic mechanisms.
- **H0 — selected identity projection:** identifiers are opaque or selectively disclosed service
  labels. Multiple economic actors can share one label and one actor can split across labels, while
  anonymous, hidden, rejected, inventory, and off-venue state remain unobserved. Participant ecology
  and intervention response are therefore not identified.

**Cheapest discriminator.** Before reading an outcome row, require the official source contract to
name the venue, period, event lifecycle, ID hierarchy, split/merge rules, anonymous and hidden-order
semantics, and a validation path for the attribution mechanism. Then ask whether two complete actor
worlds can induce the same public message law but different participant response. A single such twin
closes H1.

A positive result would provide a real participant-level observation bridge that current EcoMD lacks.
A null result is still useful because it prevents an order ID, broker MPID, wallet, or feature cluster
from being silently promoted to a physical particle or persistent strategy type.

## 3. Mendeley source-contract audit

The official Mendeley record was inspected without opening either CSV.

- DOI `10.17632/fsn6fn7ht8.1`, version 1, was published on 25 April 2025 under CC BY 4.0.
- The description says the data are “representative” of logs from an exchange electronic trading
  system and were obtained through unspecified “open channels.” It does not identify the exchange,
  country, asset class, symbols, trading dates, timezone, source URL, vendor, or collection method.
- The description instructs users to *treat* `MEMBER_CODE`, `CLIENT_ID`, and `TRADER_ID` as unique
  entities inside the dataset ecosystem. It supplies no mapping hierarchy, persistence interval,
  collision policy, beneficial-owner semantics, anonymization method, or evidence that IDs are
  stable across sessions.
- The API exposes one 24,062,365-byte archive with SHA-256
  `406f34f004a68328a6048c38ae0cab37e2283cc6f6943fa98658aab9dd3775da`. Reading only the ZIP central
  directory showed `Trades .csv` and `Orders .csv`, with no README, codebook, licence file, or
  provenance manifest. No CSV header or data row was read.
- An official 2026 conference schedule links the same contributor group to *Temporal-Weighted Cycle
  Anomaly Detection for Circular Trading*. The available author description reports validation by
  injecting fraudulent cycles and lists validation on larger real regulatory data as future work.
  This contextual clue is not needed for the decision: the repository record already fails the
  immutable source and identity contract.

The dataset may be useful for classroom anomaly-detection exercises. It cannot support a claim about
real exchange participants, market manipulation prevalence, or EcoMD particle semantics.

## 4. Nasdaq capability and boundary

### 4.1 What is genuinely observed

The TotalView-ITCH 5.0 specification supplies a strong displayed-book event contract.

- An accepted displayable order receives a day-unique order reference.
- Message `A` adds an unattributed displayed order; message `F` adds an attributed displayed order
  with a four-character MPID.
- Executions, partial cancellations, deletes, and replacements reference the displayed order, so its
  displayed lifecycle can be reconstructed.
- Message `L` reports registration state, market-maker mode, and primary-market-maker status for
  registered MPIDs in each issue.
- Nasdaq's official sample directory exposes several full-day ITCH 5.0 logs, including large 2025
  and 2026 files. Availability is public, but a publication-grade reuse and redistribution licence
  was not located in the sample directory.

This is a valuable conformance and partial-identity fixture. It is strictly stronger than anonymous
L2 data and stronger than the unverified Mendeley release.

### 4.2 What is not observed

The official rules make the missingness mechanism explicit.

1. Attribution is a participant-designated order attribute. Displayed orders may be non-attributable,
   so `R_t` is a strategic choice rather than randomized label availability.
2. Market makers and ECNs may request supplemental MPIDs. An MPID is therefore not invariant under
   one economic member being represented by multiple identifiers.
3. A member can trade for its own account or serve as broker/dealer for customers. A firm MPID does
   not identify the beneficial owner, strategy, information set, or controller of an order.
4. A non-displayed order has no add message. The current non-cross trade message sets its order
   reference to zero and, since 2014, does not retain an informative resting-side indicator.
5. ITCH reports accepted exchange events, not rejected attempts, private parent orders, inventories,
   positions across venues, latency, or the policies that selected attribution.

Consequently, “every order has a participant” is false for the public feed even though every
displayed order has a lifecycle. “Every attributed order has an MPID” is true but too narrow to
identify the full participant ecology.

## 5. Selective-attribution nonidentification theorem

Let the observable record be

\[
O=(X,R,R M),
\]

where `M` is observed only when `R=1`. Fix any observed law `P(O)` with positive anonymous mass
`P(R=0)>0`. For every probability kernel `q(m\mid X,R=0)`, define a complete-data law by

\[
P_q(M=m\mid X,R=0)=q(m\mid X,R=0)
\]

and retain the observed conditional law when `R=1`. All `P_q` induce exactly the same law of `O`.
They can nevertheless assign every anonymous action to one visible member, to an entirely disjoint
population, or to state-dependent mixtures with opposite response functions.

Therefore any functional depending on the hidden allocation—participant count, concentration,
interaction network, type mass, inventory response, or counterfactual actor policy—is unidentified
without additional restrictions. For a bounded hidden outcome `Y\in[a,b]`, the assumption-free mean
identified set contains the familiar worst-case interval

\[
E[RY] + P(R=0)[a,b].
\]

Writing this interval down is not an ICLR contribution; it is the standard missing-data bound.
Narrowing it requires a verified selection model, an instrument, randomized attribution, shadow
variables, target labels, or externally audited firm-order links. None is present here.

There is a second representation failure. If one member can use multiple supplemental MPIDs and a
broker can combine many clients, then both splitting and merging preserve permissible public records.
Any law expressed in the raw number of MPIDs, or in pairwise MPID interactions without a declared
quotient, is not invariant to the economic unitization.

## 6. Why behavioral clustering does not create identity

ClusterLOB constructs six time-dependent features for each MBO event, applies K-means++, and calls
three resulting clusters directional, opportunistic, and market-making behavior. The clusters can be
useful predictive summaries. They do not recover participants.

If `C=g(X)` is the cluster label computed from observed order features, then

\[
I(M;C\mid X)=0.
\]

Two worlds with the same feature stream and opposite hidden actor assignment have the same clusters,
cluster imbalances, and any deterministic strategy built from them. A cluster can improve a finite
model through compression or regularization, but it cannot be advertised as independent participant
truth after conditioning on its inputs. This is the same no-increment lemma already recorded for the
HFT proxy.

## 7. Intervention and prior-art audit

The 9 February 2015 addition of MPID attribution messages to BX and PSX initially looks like an
empirical intervention. It does not rescue this route.

- The change made attribution available; it did not randomly assign orders or firms to disclose.
  Adoption and order routing remain endogenous.
- Nasdaq, BX, and PSX share an operator and feed family, so they are not independent implementations.
- The official historical products require agreements and authenticated access. The located public
  sample directory does not supply a 2015 before/after panel for BX and PSX.
- The economic object is already a mature market-transparency question. Studies examine mandatory
  removal of broker identity, voluntary pre-trade anonymity, broker-ID informativeness, and
  experimental anonymous versus identified books.

Nearest direct work closes the obvious claims:

1. Musciotto, Piilo, and Mantegna use special participant-identified LSE and Nasdaq Nordic data to
   measure persistent market-member interaction networks and changing HFT ecology.
2. Zhai uses Hyperliquid wallet-resolved full-message data to show persistent identity-specific
   adverse selection and short-horizon return predictability. This exact public-identity route was
   already audited in the repository.
3. Cartea, Chang, and Graumans show that market makers can reveal identity through order-size signals
   even in an anonymous book and develop competitive and collusive equilibria for the response.
4. ClusterLOB directly occupies unsupervised behavioral roles and cluster-conditioned order-flow
   signals from Nasdaq MBO data.
5. Informative-label, selective-label, PU-learning, and MNAR generative-model work already provides
   tests, weighting estimators, identifiability assumptions, and risk bounds for strategically or
   systematically missing labels.

“Use EcoMD to simulate anonymous versus attributed agents” is therefore a domain illustration of an
occupied transparency mechanism. “Infer anonymous MPIDs with a neural model” has no target labels and
violates the theorem above. “Cluster orders and call clusters particle types” repeats ClusterLOB and
the deterministic-proxy error.

## 8. Gate matrix

| Gate | Mendeley | Nasdaq ITCH | Decision |
|---|---|---|---|
| Named venue, period, and source chain | Fail | Pass | Joint truth contract fails |
| Public immutable file identity | Partial | Pass for samples | Not sufficient |
| Complete displayed-order lifecycle | Unverifiable | Pass | Retain as fixture |
| Rejections and non-displayed intent | Unverifiable | Fail | Full action denominator absent |
| Stable economic actor | Fail | Fail | Opaque IDs; MPID split/merge |
| All actions labelled | Claimed, unaudited | Fail | Attribution is selective |
| Selection mechanism identified | Fail | Fail | Strategic MNAR |
| Inventory/private/cross-venue state | Fail | Fail | Response state incomplete |
| Assigned intervention | Fail | Fail | 2015 availability change is endogenous adoption |
| Open before/after and independent system | Fail | Fail | Historical contract and replication absent |
| Irreducible ICLR method | Fail | Fail | Direct market and MNAR parents |

No recorded hard blocker is removed.

## 9. Retained scientific value

The screen retains three legitimate assets.

- Nasdaq public samples are useful for parser, lifecycle, MBO-to-L2 projection, and matching-engine
  conformance tests after a future machine decision authorizes their use.
- Attributed MPIDs can support explicitly selected-subpopulation descriptions if every claim is
  conditioned on `R=1` and avoids beneficial-owner, full-population, or causal interpretations.
- The selective-attribution twin is a reusable early kill test for any proposal that maps order IDs,
  MPIDs, wallets, or clusters directly to EcoMD particles.

None authorizes outcome access or a paper experiment now.

## 10. Exact re-entry conditions

Re-audit only if a new asset or theorem provides all relevant pieces:

1. a named, licensed, immutable participant-resolved event release with complete accepted, rejected,
   hidden, cancel, replace, and fill lifecycle semantics;
2. an audited hierarchy from order and service identifiers to stable economic units, including
   identifier rotation, supplemental IDs, brokers, shared control, and actor splitting;
3. an identified attribution/selection mechanism or randomized disclosure with overlap, together
   with participant state and response labels under the proposed intervention;
4. an independently governed second system sharing the same identity, action, timing, and response
   grammar, plus an untouched confirmation partition; and
5. a theorem or algorithm with a guarantee not reducible to standard MNAR identification, partial
   labels, entity resolution, deterministic feature clustering, or market-transparency analysis.

A larger anonymous archive, more public sample days, a neural imputer, an MPID lookup table, or an
EcoMD fit to attributed orders is not a trigger.

## 11. Sources

1. Mendeley Data, *Anomaly bias Stock Trades and Order Dataset*,
   https://data.mendeley.com/datasets/fsn6fn7ht8/1
2. Nasdaq, *Nasdaq TotalView-ITCH 5.0 Specification*,
   https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf
3. Nasdaq Equity Rule 4703(i), *Attribution*,
   https://listingcenter.nasdaq.com/rulebook/Nasdaq/rules/Nasdaq%20Equity%204/block/EQUALS/
4. Nasdaq Equity 2, primary and supplemental MPIDs,
   https://listingcenter.nasdaq.com/rulebook/nasdaq/rules/Nasdaq%20Equity%202
5. Nasdaq official ITCH sample directory,
   https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/
6. Nasdaq Data Technical News 2014-34, BX/PSX attribution rollout,
   https://www.nasdaqtrader.com/TraderNews.aspx?id=dtn2014-34
7. Zhang et al., *ClusterLOB*, https://arxiv.org/abs/2504.20349
8. Musciotto, Piilo, and Mantegna, *High-frequency trading and networked markets*,
   https://doi.org/10.1073/pnas.2015573118
9. Cartea, Chang, and Graumans, *Anonymity, Signaling, and Collusion in Limit Order Books*,
   https://doi.org/10.2139/ssrn.5080700
10. Sportisse et al., *Are labels informative in semi-supervised learning?*,
    https://proceedings.mlr.press/v202/sportisse23a.html
11. Zhai, *Public Trader Identity: Adverse Selection and Return Predictability*,
    https://arxiv.org/abs/2608.04373

## 12. Compute decision

This audit is `not_trigger`; `candidate_harvest_authorized=false`. Do not download the two Mendeley
CSV files, the multi-gigabyte ITCH sample logs, or historical BX/PSX outcomes. Do not change EcoMD,
train an identity model, SSH to a worker, or schedule an A800/V100 job under this route.
