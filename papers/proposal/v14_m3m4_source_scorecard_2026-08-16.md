# V14 M3/M4 replacement-source scorecard

**Date:** 2026-08-16

**Decision:** `AUTHORIZE_COMPOUND_V3_ZERO_ROW_METADATA_PREFLIGHT_ONLY`

**Admission state:** no candidate has passed G1; no participant action, account state, realized response or chain
RPC row was opened for this decision.

## 1. Bottom line

Compound III is the best next *feasibility* route for participant adaptation, not yet the selected empirical event.
Its advantage is structural: a pre-event set of nonzero Comet account positions can potentially define the exposed
population before a rule change, and every member can then be classified as having a successful state adjustment
or no successful state adjustment. That supplies the denominator and explicit null that the current Uniswap and
CoW frames lack.

The scoped unit is an on-chain account address, not a person. “No action” means no successful state-changing
transaction in the frozen channel and window; it does not mean no intent, no reverted attempt or no off-chain
plan. Managers, Bulker operators, transaction senders and account addresses must remain distinct identity layers.

Compound presently has five `pass`, five `partial` and two `unresolved` criteria. Three mandatory kill switches
remain non-pass: exposure-denominator conformance, outcome-blind controls, and licence/retention. The only
authorized work is an official-source metadata audit. Aave is the second route; GC0166 remains conditional on
official identity/provenance clarification. Uniswap Proposal 94 stays the exact-M2 case and cannot be rehabilitated
as M3/M4 by changing its failed concentration gate.

Machine-readable decision:
`data/manifests/v14_m3m4_source_selection_v1.yaml`.

## 2. Common source gate

Every candidate is assessed on twelve properties before response access:

1. exact executable mechanism and operative authority;
2. complete pre-event economic-exposure denominator;
3. observable and scientifically scoped null action;
4. stable action unit with delegation/entry/exit rules;
5. actions, state and outcomes at the same unit and clock;
6. outcome-blind control construction and positivity;
7. exact local treatment execution clock;
8. one development plus two independently selected confirmation interventions;
9. revision, reorg, failure and retention completeness;
10. licence and reproducible retention;
11. authoritative state reconstruction and conformance; and
12. sufficient pre-event support, effective sample size and bounded concentration.

Exposure denominator, controls, treatment clock, licence/retention and state reconstruction are kill switches.
A candidate with a partial or unresolved kill switch may receive a bounded metadata audit but cannot enter G1.

## 3. Comparative decision

| Rank | Candidate | Strongest property | Binding issue | Disposition |
|---:|---|---|---|---|
| 1 | Compound III Comet | executable single-base-market state plus address-level positions and actions | denominator/archive conformance, controls and licence/retention not passed | zero-row metadata preflight only |
| 2 | Aave V3 | rich public payload, address-book and state-diff ecosystem | larger multi-reserve/eMode/delegation/version surface | audit only if Compound fails or proves too sparse |
| 3 | GB GC0166 | future official clock, public BMU schemas and BMRS licence | submission versus default/reject/missing provenance and identity history | wait for official clarification; do not send without approval |
| 4 | Uniswap V3 Proposal 94 | exact 1,000-pool treatment ledger | U1R concentration failure and no outcome-blind controls | fixed M2 only |
| 5 | CoW Protocol | versioned scoring/service mechanism | no admissible complete historical competition enumerator | blocked unless an official list/snapshot appears |
| 6 | AEMO FTA | exact reform clock | affected participant panel is not public | partner conditional |

This is an outcome-blind route reset after a failed data contract, not selection among observed treatment effects.
No Compound or Aave participant response has been inspected.

## 4. Why Compound is genuinely different from the failed pool frame

Compound's official documentation describes signed base balances, global supply/borrow indices and per-account
collateral state, together with supply, withdrawal, borrow/repay-through-balance, transfer and liquidation
operations. Its helper views expose account balances and collateral membership. Governance calls Configurator
setters and deploys/upgrades a Comet implementation; for non-mainnet instances, the economically operative clock
must include bridge delivery and the local timelock rather than the mainnet proposal time.

Those properties suggest a candidate end-to-end unit:

\[
  i=(\text{chain},\text{Comet market},\text{account address}),
\]

with pre-event exposure defined only from state at a frozen block. The M3 outcome can be a multichannel adjustment
process—supply, withdraw, borrow, repay, collateral movement or liquidation—conditional on that exposure. M4 can
model entry, exit and movement across markets. The distinction is important: Uniswap U0 enumerated configured
contracts, whereas a Comet snapshot may enumerate economically live positions directly.

This remains a hypothesis. Interest accrual means event sums are not account state; principal and global indices
must be reconstructed and checked against authoritative views. Contract configuration files are not proof of
executed or current on-chain state. A manager can act for an account, so transaction sender is not the response
unit. Liquidations are partly third-party actions and cannot be pooled with voluntary adjustment without a
separate channel.

## 5. Candidate multiscale design

The smallest coherent architecture is:

1. **M2 mechanism:** an exact, nonlearned local governance/configuration transition with code, proxy, storage,
   authority and execution history pinned;
2. **exposure router:** a shared pre-event account state followed by channel-specific support gates and conditional
   intensities;
3. **M3 adaptation:** competing risks for successful voluntary account adjustments, liquidation and no successful
   adjustment, with manager delegation observed rather than conflated with identity;
4. **M4 population:** entry, exit and migration across Comet markets or collateral regimes; and
5. **frozen prediction:** probabilistic response vectors sealed before the chosen intervention executes and never
   refit to its post-event outcomes.

The router baselines must include uniform account weights, static exposure value, trailing action counts, a static
hurdle model and a channel-independent router. A learned router is scientifically useful only if it improves
pre-event calibration and frozen post-change prediction over those baselines on independent interventions.

## 6. Event and control requirements

A usable parameter change should be selected from governance calldata without looking at responses and should:

- affect one declared market or asset through an interest curve, collateral factor, liquidation factor or supply
  cap;
- have an exact successful local execution block;
- avoid a payload that simultaneously changes every plausible comparison market;
- leave at least one mechanism-credible unaffected or not-yet-treated market with pre-event overlap;
- have enough lead time to freeze the population, response, baselines and precision calculation; and
- be retained even if the effect is null, operationally failed or inconvenient.

Shared asset prices, common risk sentiment, cross-market borrowers and bundled governance can invalidate a naive
control. “Another Comet market” is only a candidate control until pre-event balance and support diagnostics pass.
Historical proposals may be used for development, but confirmation needs a new first-event/no-replacement rule.

## 7. Data and compute ladder

### Authorized now

- exact official Git commit, licence and named source-file hashes;
- six Ethereum-mainnet configuration/root pairs;
- action, storage and Configurator source markers;
- migration filenames as repository metadata only;
- passing deployed proxy/implementation/configuration and fixed archive metadata; and
- one sealed D0 scan of Configurator logs and six proxy `Upgraded` logs in the fixed block window.

The D0 scan uses bounded public RPC plus local CPU, no paid data, no remote worker and zero GPU-hours. It retains
normalized governance/configuration rows only and cannot be expanded in place.

### Still locked

- governance transaction/receipt rows, payloads and call traces;
- account-state snapshots, action events, reverts, liquidations, oracle prices and market outcomes;
- historical bulk indexing, model fitting and GPU work; and
- any prospective response collection.

Even if D0 finds a provisional atomic candidate, the next protocol may inspect only that candidate's receipt,
calldata, governance call path and finality evidence. Account rows require a later frozen exposure/state-
conformance protocol. GPUs become relevant only after the data contract, controls and independent intervention
clock pass; neither the two V100s nor the RTX 2060 is currently queued.

## 8. Evidence and licence caution

The official Comet repository is pinned at commit
`f766f51583c23acc33b2a7824654ef2029a96804`. Its LICENSE text names Business Source License 1.1, a
2025-12-31 change-date clause and GPL v2-or-later as the change licence. The audit records that text and hash but
does not turn it into a legal opinion about every repository version or about independent RPC data. Code licence,
on-chain facts and an RPC provider's retention/redistribution terms are separate provenance objects.

Primary sources:

- [Compound governance and Configurator semantics](https://docs.compound.finance/governance/)
- [Compound collateral, borrowing and indexed account state](https://docs.compound.finance/collateral-and-borrowing/)
- [Compound state helper functions](https://docs.compound.finance/helper-functions/)
- [Compound manager permissions](https://docs.compound.finance/account-management/)
- [Compound liquidation semantics](https://docs.compound.finance/liquidation/)
- [official Compound Comet repository](https://github.com/compound-finance/comet)
- [official Aave DAO repository index](https://github.com/aave-dao)
- [official Aave address book](https://github.com/aave-dao/aave-address-book)
- [official Aave proposal repository](https://github.com/aave-dao/aave-proposals-v3)

## 9. Immediate sequence

1. Commit and push the D0 governance-log manifest, collector, tests and preregistration before network access.
2. Run D0 once from its exact pushed commit and preserve failure or pass without changing window, event or market.
3. On pass, freeze a separate candidate receipt/payload/call-path/finality audit; do not open account rows.
4. On failure, keep Compound outside G1 and audit Aave only under a new source protocol.
5. Keep the GC0166 request unsent unless the user authorizes contact.

## 10. Source-preflight result

The v2 run at pushed protocol commit `0245e6ebcd11e263e13bdeb98ff2d66cb1498b6c` passed all nine source-
conformance gates. Six of six mainnet market manifests were structurally complete, with six unique Comet roots,
22 collateral configurations and 56 migration filenames. All frozen action, state, Configurator and licence
markers were present; 16 file hashes were independently verified. Artifact SHA-256:
`643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11`.

This does not change the scorecard to G1. All six markets share one Configurator address in the source roots, which
makes bundled treatment and shared-authority spillover an explicit control risk. Repository configurations remain
non-authoritative until code/storage/execution metadata conform on chain. The next admissible protocol is chain
deployment/archive *metadata only*; accounts, actions, prices, responses and GPUs stay locked. Result:
`experiments/v14_compound_v3_metadata_preflight/RESULTS.md`.

## 11. Chain-metadata result

The v2 chain run at protocol commit `d1019df44df4acbc944e6aae408595de69478e09` passed 12/12 metadata gates:
62 one-attempt calls, an explicit 64-block confirmation-depth snapshot, six source-conforming market getters and
bounded historical state at block 17,000,000. Artifact SHA-256:
`14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944`.

All six markets and the Configurator share one proxy-admin address. This removes deployment ambiguity but makes
shared-authority spillover more concrete. The pass authorizes exposure/control protocol design only; it does not
change the candidate to G1-admitted. Result:
`experiments/v14_compound_v3_chain_metadata_preflight/RESULTS_V2.md`.

## 12. Zero-row exposure/control design result

The design now has an exact exposure-denominator test. At one block, enumerated positive/negative principal and
each collateral balance must reproduce the corresponding aggregate total with zero residual. Conditional on the
active implementation's accounting invariant, zero residual certifies no omitted nonzero position.

This advances the exposure kill switch from “unresolved in principle” to “empirically testable but not yet run.”
Controls and retention remain unresolved, and complete action data becomes a new explicit trace-source kill switch:
event logs do not cover every debt-changing base transfer. The next stage is a sealed governance metadata inventory
only. No account, trace or response access follows from the design. Full protocol:
`papers/proposal/v14_compound_exposure_control_design_2026-08-16.md`.

## 13. Frozen D0 governance-log inventory

D0 fixes blocks 14,000,000--25,760,572, one Configurator and six deployed Comet proxies. It makes 336 root
`eth_getLogs` requests in 250,000-block inclusive partitions, plus chain ID and two cross-provider headers. An
exactly 1,000-row response is discarded and recursively bisected; single-block saturation fails. The expected
unsaturated path is 339 calls at two requests per second.

Only three existing-asset parameter events are eligible. A provisional event requires exactly one eligible
Configurator log, exactly one same-proxy `CometDeployed`, exactly one matching proxy `Upgraded`, no other
Configurator log, no other frozen-market upgrade and `old != new` in the same transaction. The `Upgraded` log is
the operative clock. This is log-level screening, not payload isolation or treatment validity.

Every account/action/response row remains forbidden. A pass authorizes only a separately frozen receipt, calldata,
governance-call-path and consensus-finality preflight. Protocol:
`experiments/v14_compound_v3_governance_log_inventory/PREREGISTRATION.md`.

## 14. D0 governance-log result

D0 passed all ten gates at protocol commit `db26bbe91111b6a71f6a4083231927574dd2b188`. The exact unsaturated path
used 339 one-attempt requests and 605,863 response bytes, normalizing 886 logs with zero duplicate or conflict.
Among 184 eligible parameter updates, 14 satisfy the provisional atomic log rule: twelve supply-cap and two borrow-
collateral-factor changes across 14 distinct blocks.

Bundling is the rule rather than the exception. Of the 184 eligible rows, 170 share a transaction with another
Configurator log, 167 with another eligible parameter update and 126 with another frozen-market upgrade; counts
overlap. This confirms that shared authority is a material spillover problem, not merely a design caveat.

The already frozen event priority leaves two borrow-factor candidates at the top. The older is a mainnet-USDS
wstETH change from 0.82 to 0.80 at block 22,273,296; the later mainnet-WETH rsETH change is 0 to 0.80 and therefore
needs especially strict pre-existing-collateral/exposure checks. Neither is selected or valid yet. The next
preflight should audit all 14 candidates before applying deterministic filters, and may open only receipts,
calldata/call paths, getters, block/finality evidence and governance-neighborhood metadata. `G1`, participant rows
and GPUs remain locked. Result:
`experiments/v14_compound_v3_governance_log_inventory/RESULTS.md`.

## 15. Frozen all-candidate mechanics preflight

D0b audits all 14 provisional rows before filtering, in the pre-existing event priority and deterministic block/
transaction order. The exact no-retry plan is 187 JSON-RPC calls plus one Beacon finality request. It requires
complete transactions/receipts, two-provider headers, callTracer trees, T-1/T implementation/admin/code and exact
eight-word asset getters.

Payload isolation is a call-cone test: one exact Configurator setter, deploy, proxy-admin deploy/upgrade and target-
proxy upgrade `CALL` must exist; deploy and upgrade must descend from and be sent by that proxy admin. Successful
stateful calls outside their ancestor/descendant cone fail that candidate. Receipt logs are also re-decoded against
all D0-retained indexed/value fields rather than matched on topic0 alone.
Every candidate is retained with its check vector; at least one must survive. The 24-hour neighbor plan is derived
from D0 rather than inspected ad hoc.

The finality evidence combines the execution `finalized` tag, Beacon light-client finality update, an explicit
execution-header hash match and candidate header replication. It remains provider-reported because no local BLS/
Merkle verification is performed. A pass licenses D1 exposure-count/cost protocol *design only*. Protocol:
`experiments/v14_compound_v3_candidate_mechanics_preflight/PREREGISTRATION.md`.

V1 did not reach a scientific decision. At the first candidate, PublicNode returned JSON-RPC `-32601` on all three
frozen `debug_traceTransaction` attempts. No trace result, slot/getter evidence or later candidate was opened, so
none of the 14 rows can be called conforming or nonconforming. D1 remains locked. Result:
`experiments/v14_compound_v3_candidate_mechanics_preflight/RESULTS_V1.md`.

V2 is frozen as a transport-only repair: the v1 scientific base and its result are hash-pinned, while the 14 trace
operations use Blockscout's documented raw-trace REST response. Completeness requires unique paths, an explicit
root, every parent and exact child/subtrace counts; successful out-of-cone `SELFDESTRUCT` is stateful. The total
plan remains 188 operations (173 RPC, 14 raw trace, one Beacon), and both success and bounded failure paths retain
every HTTP-attempt hash/outcome. No candidate trace may be probed before the v2 protocol is pushed and no endpoint
may be substituted afterward. Protocol:
`experiments/v14_compound_v3_candidate_mechanics_preflight/PREREGISTRATION_V2.md`.

V2 passed 12/12 at commit `c7f770a938abe9f0e8452c9bda84bb8ed69f2e5e`: 188 logical operations, 191 HTTP
attempts and four fully conforming rows. Eight rows fail call-cone isolation and three fail the 24-hour rule, with
one overlap. The four survivors are all supply-cap increases in December 2022--February 2023; two repeat the same
WETH-market asset. This is enough to design the next gate but not to call Compound's participant-response route
viable.

A supply-cap increase relaxes a market constraint; it does not directly perturb existing accounts' collateral
factors or liquidation thresholds. The generic nonzero-position population is not a treated cohort, and would-be
suppliers blocked by the old cap have no pre-event on-chain denominator. Before any account row, freeze an
aggregate T-1 cap-utilization/estimand gate and a market-level entrant/flow estimand. Slack caps or an indefensible
control retire the causal M3 route. Result:
`experiments/v14_compound_v3_candidate_mechanics_preflight/RESULTS_V2.md`.
