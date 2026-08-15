# Compound III exposure and control design

**Date:** 2026-08-16

**Stage:** zero-row protocol design; no governance payload, account, action, trace, liquidation, price or response
row is authorized by this document.

**Machine contract:** `data/manifests/compound_v3_exposure_control_design_v1.yaml`

## 1. Decision

Compound remains viable as a historical M3/M4 development domain, but it has not passed G1. The chain audit solved
deployment provenance and bounded archive access. The next scientific bottleneck is no longer “can we read the
contracts?” It is whether we can construct an exact pre-event account denominator, a complete successful-action
panel and a control frame that survives shared authority.

The key new mechanism is an exact position-completeness certificate. Candidate account addresses are enumerated
from state-owner event roles, then their signed base principal and collateral balances are read at one frozen
block. The candidate set is complete only if its nonnegative component sums reproduce the contract's stored base
supply, base borrow and every collateral total with zero tolerance. This turns log coverage into a falsifiable
conservation test rather than an assumption.

That identity does not solve action completeness. Current Comet source allows a successful base transfer to move
debt between accounts without necessarily emitting an owner-identifying balance event. Full M3 therefore requires
successful call traces plus state reconciliation; an event-only panel cannot support the complete-action claim.

## 2. Evidence boundary and reconnaissance disclosure

Inputs already consumed before this design are:

- official Comet source commit `f766f51583c23acc33b2a7824654ef2029a96804`;
- the passing source summary, SHA-256
  `643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11`;
- the passing chain summary, SHA-256
  `14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944`;
- source-pinned interfaces/storage, the current extended Comet implementation, Configurator, CometProxyAdmin and
  exact deployment metadata; and
- migration filenames plus incidental `ProposalCreated` marker lines exposed by a broad source search.

No migration action list, proposal calldata, governance log, transaction receipt, account value, action log,
trace, liquidation, oracle value or response was decoded. The incidental marker-line visibility must be retained
as reconnaissance disclosure; it conveyed no parameter value, target or execution result.

## 3. The denominator certificate

At a single block, let `U` be the deduplicated candidate-address set and let the stored signed principal for
account `i` be `p_i`. Let `c_ia >= 0` be its stored balance of collateral asset `a`. Comet stores aggregate base
principal totals `S` and `B` and collateral totals `C_a`. Define:

\[
R_S=S-\sum_{i\in U}\max(p_i,0),\qquad
R_B=B-\sum_{i\in U}\max(-p_i,0),
\]

\[
R_a=C_a-\sum_{i\in U}c_{ia}.
\]

Under a source-conforming implementation, atomic same-block reads and the aggregate accounting invariant, each
residual equals the sum of the corresponding nonnegative balance outside `U`. Therefore

\[
R_S=R_B=R_a=0\ \forall a
\]

implies that every address outside `U` has zero stored principal and zero collateral. Conversely, any positive
residual proves that the candidate enumeration missed state or that reconstruction/provider conformance failed.
A negative residual proves duplication, decoding, block-consistency or aggregate-conformance failure. Both are
hard failures; there is no numerical tolerance.

This is a completeness lemma for this storage/accounting design, not a claimed new theorem. It must be re-audited
for the exact historical implementation active at each event. It certifies a position set, not beneficial owners,
intent, action timing or causal independence.

### Candidate-address construction

From proxy deployment through the snapshot, enumerate only state-owner roles:

| Comet event | candidate owner fields | fields deliberately not treated as owner |
|---|---|---|
| `Supply` | `dst` | token `from` |
| `Withdraw` | `src` | token recipient `to` |
| `SupplyCollateral` | `dst` | token `from` |
| `WithdrawCollateral` | `src` | token recipient `to` |
| `Transfer` | nonzero `from`, nonzero `to` | zero mint/burn address |
| `TransferCollateral` | `from`, `to` | none |
| `AbsorbDebt` | `borrower` | `absorber` |
| `AbsorbCollateral` | `borrower` | `absorber` |

The at-risk population at block `T-1` is exactly the certified set with nonzero signed principal or any positive
collateral balance. Tracking rewards alone do not create exposure to the selected collateral-rule change.

## 4. Treatment and clocks

The preferred historical intervention is a change to an existing asset's borrow collateral factor. Liquidation-
threshold and supply-cap changes are ordered fallbacks. Collateral additions, price-feed replacements, emergency
pauses, rewards/reserves actions, implementation-only upgrades and bundled multi-market changes are excluded from
the first design because they either lack a pre-existing directly exposed population or mix mechanisms.

Configurator setters update configuration used to deploy a new immutable Comet implementation; they do not by
themselves make the proxy use it. A clean candidate must link, in one successful transaction:

1. exactly one eligible Configurator change for one existing collateral in one market;
2. `CometDeployed(cometProxy, newComet)`; and
3. the target proxy's ERC-1967 `Upgraded(newComet)` event.

The operative treatment clock is the proxy `Upgraded` log, not proposal creation, queue time, Configurator setter
or `CometDeployed`. Pre/post getters at blocks `T-1` and `T` must reproduce the event's old/new parameter and new
implementation. Any other market upgrade in the transaction, eligible change in the same payload, or target/control
mechanism event within 24 hours is a disclosed exclusion under the frozen metadata rule—not an outcome-based
choice.

Historical candidates are development only. A prospective Compound event can enter the confirmation registry only
under the existing first-event/no-replacement rule and lead-time requirement; ordinary short-timelock execution
does not automatically qualify.

## 5. Action and identity contract

The statistical unit is `(chain, Comet market, account address)`. It is not a person or firm. The following layers
must be retained separately:

- account whose Comet state changes;
- top-level transaction sender;
- immediate caller of Comet;
- authorized manager or Bulker;
- external token funder/recipient;
- liquidation absorber; and
- collateral-sale recipient.

The primary voluntary channels are supply, repay, withdraw, borrow, base transfer, collateral supply, collateral
withdrawal and collateral transfer. Liquidation is a separate competing risk. A “no action” observation means no
successful state-changing account adjustment in the frozen window. It does not mean no intent, no reverted call,
no off-chain decision or no manager activity.

Event logs alone are insufficient. In the current source, a base transfer can increase one debt and repay another
without a corresponding nonzero `Transfer` mint/burn event. A complete action panel therefore requires:

1. successful call traces for direct Comet and Bulker-mediated calls;
2. decoded account-owner/operator/sender roles;
3. matching receipt status and canonical block;
4. pre/post account-state reconciliation at transaction or bounded checkpoint resolution; and
5. exact aggregate residuals at frozen checkpoints.

If a reproducible trace source is unavailable, the route may report logged channels and net state changes only,
but C3 and the complete M3 adaptation claim fail. It must not silently relabel logged activity as all activity.

## 6. Response and population accounting

Frozen horizons are one hour, one day, seven days and 28 days. For the certified `T-1` population, report:

- time to first successful voluntary adjustment by channel;
- liquidation incidence as a competing risk;
- signed principal and collateral-state changes;
- persistence, complete exit and cross-market migration; and
- contribution-share reallocation with cluster-robust uncertainty by address.

Entrants are account-market units first reaching nonzero certified state after `T`; there is no fictitious hazard
denominator of all Ethereum addresses. M4 forecasts entrant counts and state/contribution distributions. Persistent,
entrant and exit accounting must close at every horizon before any Price/Oaxaca/Shapley-style attribution.

## 7. Controls are a kill switch, not a convenience

All six markets share a Configurator and proxy admin. A payload can update several markets, common collateral prices
transmit shocks and one address can span markets. “Another Comet market” is not independent by default.

Four candidate families are frozen:

1. same-market accounts with zero direct affected-asset balance;
2. the same collateral asset in another unchanged Comet market;
3. matched account-market units in an unchanged Comet market; and
4. pre-event pseudo-interventions.

No one family is sufficient. Before response access, the payload/receipt must show no direct control-market action;
pre-event support must achieve weighted SMD at most 0.10, effective sample size at least 100 per arm, top-one weight
share at most 0.20 and top-ten at most 0.60. Inference clusters repeated addresses across markets. Anticipation,
oracle/common-price shocks, liquidations and contemporaneous governance remain explicit sensitivity analyses.

Failure of every control does not prevent a descriptive forecast score, but it kills causal language about a rule-
induced behavioral response and weakens the flagship Lucas-test interpretation.

## 8. Staged data plan

| Stage | Data opened | Pass licenses | Hard stop |
|---|---|---|---|
| D0 governance metadata | Configurator/proxy/governor logs, receipts, calldata and block headers; no participant rows | freeze historical candidate inventory and exact clocks | no atomic clean event, finality or terms |
| D1 exposure census | pre-event state-owner logs, account views and aggregate totals only | certified at-risk denominator | any nonzero residual, unconformed historical implementation or cap breach |
| D2 support/control | pre-event account actions/state, manager layers, prices needed for matching; no post-event response | freeze controls, precision and response manifest | trace incompleteness, support/concentration failure or spillover |
| D3 historical response | one-time post-event actions/state at frozen horizons | development model/effect diagnostics | reconciliation or placebo failure |
| D4 model ladder | historical development splits only | prospective forecast code freeze | M3/M4 lacks compute-matched value |
| D5 confirmation | first qualifying future events under existing registry | NCS/NMI evidence if replicated | replacement, refit or insufficient independent events |

The next authorized stage after this design passes is D0 only. It must have a separate manifest and be committed
before any governance payload/log query.

## 9. Data sources, retention and finality

Blockscout documents a no-key per-instance JSON-RPC endpoint and a 1,000-log maximum per `eth_getLogs` response.
Its current documentation also warns that per-instance API access is being deprecated in favor of its PRO API.
That makes it suitable for bounded feasibility, not the sole archival dependency of a paper.

Production extraction requires:

- one canonical execution/archive source with logs, historical calls, transactions, receipts and successful call
  traces;
- a second execution provider reproducing block hashes and frozen aggregates;
- a consensus/Beacon source linking the execution payload to a finalized checkpoint; and
- written review of access, retention and derived-data release terms for every provider.

The 64-block snapshot used in the metadata audit is not consensus finality. Public artifacts contain no raw account
addresses. Internal longitudinal IDs use keyed HMAC-SHA256; the address crosswalk is encrypted and access-limited.
Raw provider payloads are not published. Code licence, public chain facts, provider terms and privacy/ethics review
are separate provenance objects. The current bounded source search found relevant Blockscout terms, but no legal
conclusion authorizing bulk redistribution; that gate remains unresolved.

Primary references:

- [official Comet source](https://github.com/compound-finance/comet)
- [Compound account management](https://docs.compound.finance/account-management/)
- [Compound collateral and borrowing](https://docs.compound.finance/collateral-and-borrowing/)
- [Ethereum JSON-RPC block parameters](https://ethereum.org/developers/docs/apis/json-rpc/)
- [Ethereum proof-of-stake finality](https://ethereum.org/developers/docs/consensus-mechanisms/pos/gasper/)
- [Blockscout ETH RPC and log cap](https://docs.blockscout.com/devs/apis/rpc/eth-rpc)
- [Blockscout requests and limits](https://docs.blockscout.com/devs/apis/requests-and-limits)
- [Blockscout terms and conditions](https://eaas.blockscout.com/terms-and-conditions)

## 10. Compute and storage

This design and its validation use local CPU only, negligible storage and zero GPU. D0 should remain below hundreds
of metadata calls and tens of MiB. D1 scales with historical log volume and the number of candidate addresses times
active assets. It is CPU/network-bound; exact call and byte budgets must be measured in a count-only preflight
before launch. Batched historical calls may be used only after same-block equivalence tests.

Call traces are the likely resource bottleneck. A free provider may not supply complete historical internal calls;
the alternatives are a provider with written terms or a self-managed execution/archive index, requiring substantial
SSD capacity and CPU/RAM but still no GPU. No V100 or RTX 2060 work is queued through D2. GPUs become relevant only
after a response contract, historical splits and G1/G2-style support gates pass.

## 11. Gate topology

```text
official source + chain metadata PASS
                |
                v
      D0 atomic upgrade inventory ---- no clean event ----> Compound remains metadata/M2 only
                |
                v
      D1 event-enumerated U + exact aggregate residuals
                | nonzero residual
                +-------------------------------> denominator FAIL
                |
                v
      D2 traces + identity layers + controls + terms/finality
          |             |                 |
          |             |                 +----> retention/finality FAIL
          |             +----------------------> causal language FAIL
          +------------------------------------> complete M3 claim FAIL
                |
                v
      D3 historical development response -> D4 compute-matched model ladder
                |
                v
      existing prospective first-event registry -> two independent confirmations
```

## 12. Current conclusion

The denominator problem now has a rigorous and cheap falsification test. The two binding risks are more serious:
complete call traces and credible controls under shared authority. This is progress because it localizes failure.
It is not a reason to start training. The first D0 governance-log substage is now complete; the scientifically
correct next experiment is its separately frozen receipt/payload/getter/finality substage with zero participant
rows.

## 13. D0 log-inventory update

The first D0 substage deliberately split governance logs from receipts/payloads and passed all ten gates at commit
`db26bbe91111b6a71f6a4083231927574dd2b188`. It found 14 provisional atomic rows among 184 eligible updates. This
is enough to proceed, but it also quantifies the shared-authority risk: 170 eligible rows have another Configurator
log and 126 have another frozen-market upgrade in the same transaction.

The two highest-priority log candidates are borrow-factor changes, but neither is selected. To avoid post-hoc
convenience selection, the next D0 substage must freeze and audit all 14 receipts, calldata/call paths, pre/post
getters, 24-hour governance neighborhoods and finality evidence before applying a deterministic filter. The D1
exposure census, all participant actions/responses and all GPU work remain locked. Result:
`experiments/v14_compound_v3_governance_log_inventory/RESULTS.md`.

That all-candidate substage is now frozen as 187 JSON-RPC calls plus one Beacon request. It audits complete
receipts, stateful call cones, exact T-1/T getter/slot transitions, D0-derived contamination neighbors and
provider-reported finality for every row before filtering. Protocol:
`experiments/v14_compound_v3_candidate_mechanics_preflight/PREREGISTRATION.md`.

V1 produced no mechanics result: PublicNode returned JSON-RPC `-32601` for all three allowed
`debug_traceTransaction` attempts at the first candidate. No trace result or later state/getter query was opened,
and D1 remains locked. Immutable result:
`experiments/v14_compound_v3_candidate_mechanics_preflight/RESULTS_V1.md`.

V2 now freezes the only permitted repair before any further candidate query. It hash-pins the v1 protocol/result,
keeps every candidate and scientific check unchanged, and replaces only the unavailable debug RPC with the
documented Blockscout unpaginated raw-trace endpoint. Flat paths must have a unique root, all parents and exact
`subtraces`; `SELFDESTRUCT` is conservatively stateful. The exact plan is 173 RPC, 14 raw-trace REST and one Beacon
request. A bounded failure artifact retains every attempted-response hash/outcome without raw payloads, so another
transport failure cannot erase provenance. Protocol:
`experiments/v14_compound_v3_candidate_mechanics_preflight/PREREGISTRATION_V2.md`. D1 remains locked until one
complete v2 execution passes all unchanged gates.

V2 subsequently passed all 12 gates at protocol commit `c7f770a938abe9f0e8452c9bda84bb8ed69f2e5e` and retained
four mechanics-conforming candidates. All four are supply-cap increases; no borrow-factor row survives the
call-cone rule. This invalidates direct reuse of the generic nonzero-position denominator for the next stage: a
cap expansion does not alter an existing account's collateral factor, liquidation threshold or current balance,
and would-be constrained suppliers are not a pre-event enumerable cohort.

Accordingly, the authorized D1 design must start with a zero-account-row activation/estimand subgate. It must
preregister how `totalsCollateral(asset).totalSupplyAsset` at T-1 relates to the old supply cap, what constitutes a
binding constraint, which market-level entrant/flow estimand remains identifiable, and what result stops M3. No
account census may begin merely because D0b passed. If the cap was slack or the estimand/control is not defensible,
Compound remains mechanics evidence only. Immutable result:
`experiments/v14_compound_v3_candidate_mechanics_preflight/RESULTS_V2.md`.

The D1a protocol now makes that gate executable without opening participant data. It hash-pins every D0b v2
artifact and derives all four survivors plus seven unique implementation bytecode hashes before network access.
Each historical implementation must match a fully verified, unchanged Blockscout Solidity source bundle with the
exact aggregate getter ABI and source-level cap-enforcement markers. PublicNode then reproduces D0b's bytecode and
T−1/T configuration state.

For each event, D1a fixes six pre-event block offsets—1, 300, 1,800, 7,200, 21,600 and 50,400—and obtains the
contemporaneous cap and `totalsCollateral(asset)` from both providers. Exact T−1 equality is the only strong-
activation pass; 90%, 95% and 99% utilization and earlier snapshots are diagnostics, not movable thresholds. No
post-event total is queried. A pass permits only a separately frozen market-level collateral-flow design; the
account-level route is retired for every outcome because thwarted potential suppliers are unobservable. A clean
no-retry run is exactly 134 RPC plus seven verified-source REST operations and requires no paid data, worker or
GPU. Protocol:
`experiments/v14_compound_v3_supply_cap_activation_preflight/PREREGISTRATION.md`.

D1a v1 produced no activation result. After two chain IDs and seven source-metadata HTTP 200 responses, the first
historical PublicNode `eth_getCode` operation returned HTTP 403 on all three frozen attempts. The run stopped
before any code result, configuration, aggregate total or participant/response row. The bounded failure ledger was
independently verified; v1 is immutable and must not be rerun. A v2 may repair only documented historical-state
transport and partial normalized-source evidence while preserving every scientific and access rule. Result:
`experiments/v14_compound_v3_supply_cap_activation_preflight/RESULTS_V1.md`.

V2 is a narrow documented repair. PublicNode's public page exposes archive data through a separate access action,
so its unauthenticated endpoint is retained only for historical headers. Blockscout's documented per-instance RPC
becomes the sole historical configuration/aggregate-state source; both providers must return identical number,
hash and timestamp for every lookback block. This is canonical-block triangulation, not independent state
replication, and the limitation is an explicit result field.

The four candidates, seven source matches, six lookbacks, exact saturation and all access/decision rules inherit
unchanged. Redundant PublicNode code/post-configuration requests are removed because D0b and verified-source
bytecode hashes are immutable parents. The v2 plan is 98 RPC plus seven source REST = 105 operations. A later
failure now retains completed normalized source/candidate evidence without turning it into a scientific result.
Protocol:
`experiments/v14_compound_v3_supply_cap_activation_preflight/PREREGISTRATION_V2.md`.

## D1a v2 complete result and route disposition

V2 was executed exactly once at pushed protocol commit
`a9af33e9c1e519a1b670f5700bf627655ff053fa`. All 105 operations succeeded on their first attempt, all ten
integrity gates passed, and all seven implementation-source plus four candidate-state records conformed. No
infrastructure fallback or threshold change was used.

No candidate met exact T−1 integer saturation. T−1 utilization was approximately 99.860059%, 73.530680%,
99.999622% and 99.999949%; none of the other 20 fixed lookbacks was exactly saturated either. The preregistered
decision is therefore `FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE`, with no authorized
next stage. D1b, account/action/response collection, G1 and GPU work are not queued.

The near-boundary cbETH states do not overturn the decision. Because the contract rejects a deposit whose
post-deposit total exceeds the cap, residual headroom can still be economically binding for a larger attempted
order. But attempted/reverted orders and would-be suppliers were outside the frozen zero-account audit, and a
post-hoc near-cap threshold would not identify them. A future constraint-boundary study must be separately
preregistered across new protocols/events and must treat these four observed rows as development data. Full
result: `experiments/v14_compound_v3_supply_cap_activation_preflight/RESULTS_V2.md`.
