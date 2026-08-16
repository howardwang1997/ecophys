# Aave V3 liquidation-threshold source/effect preflight v1

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document, the v1 manifest,
`ecomd/research/aave_liquidation_threshold_source.py`, its tests and the runbook.

## Question and deliberately narrow scope

Can pinned official Aave V3.7 source define an exact nonlearned intervention operator for a strict decrease in one
base reserve's liquidation threshold (LT)? This A0 audit asks only whether the source supports that operator and
exposes the views needed to design a later chain-event inventory. It does **not** inspect any deployment, chain
event, governance payload, account, action, liquidation or response row.

The source is `https://github.com/aave-dao/aave-v3-origin.git` at commit
`cff15de6d1271b0c800fc001f4aea4c263e8a597`. The manifest fixes fourteen allowed files, paths and normalized
semantic markers. It also records Business Source License 1.1 provenance; this is not legal advice.

All fourteen allowed official blobs were inspected through the official GitHub API while specifying and
calibrating markers (197,858 response bytes); therefore A0 is a reproducible source-integrity certification, not a
blind scientific discovery test. Search reconnaissance also exposed Aave governance proposal 204, an AAVE V3
Ethereum LT increase executed in 2023. It is development-only and can never be untouched confirmation. No
participant response was inspected.

## Exact event-layer operator

At the last pre-event state, let

\[
W^- = \sum_i C_i^- L_i^-, \qquad D^- > 0,
\]

where `C_i` is source-computed collateral value in base currency and `L_i` is its effective LT in basis points.
For changed reserve `j`, the strict effect holds balances, prices, indexes and all other account-relevant
configuration fixed and requires

\[
0 < L_j^+ < L_j^-, \quad \mathrm{LTV}_j^+=\mathrm{LTV}_j^-, \quad B_j^+=B_j^-.
\]

If reserve `j` is active collateral with `C_j^- > 0`, the account has debt, and eMode does not override its base
LT, then

\[
W^+ = W^- - C_j^- (L_j^- - L_j^+).
\]

The exact integer health factor is

\[
H(W,D)=\left\lfloor
\frac{\operatorname{round\_half\_up}(W\,10^{18}/D)}{10{,}000}
\right\rfloor,
\]

using pinned `wadDiv` overflow and rounding. If eMode supplies the effective LT or the reserve is not account
collateral, the direct base-LT effect is exactly zero. Self-checks require the weighted identity, HF monotonicity,
one deterministic HF=1 crossing and both zero routes.

A crossing from `H^- >= 1e18` to `H^+ < 1e18` is a **health-factor boundary crossing**, not proof of executable
liquidation. Liquidation additionally depends on active/unpaused reserves, grace periods, debt/collateral
eligibility and execution. A later event protocol must version-match deployed code, exclude frozen reserves, and
reject same-transaction changes to eMode, oracle, indexes or other account-relevant configuration.

## Strict response-estimand boundary

LTV affects borrowing capacity but not this HF identity; liquidation bonus affects liquidation payoffs but not the
identity. Both must be unchanged so a later response has one declared mechanical treatment. An eligible response
event must also be unbundled at payload/transaction level. Holding state fixed defines a counterfactual operator;
it does not claim realized block-end state changed only through that operator.

For ConfigEngine executions, the strict route additionally requires LTV and `liqBonus` inputs to use the pinned
`EngineFlags.KEEP_CURRENT = type(uint256).max - 42`. ConfigEngine represents `liqBonus` as the increment above
100%, then adds `100_00` before calling the pool configurator; later inventories must compare normalized pool
configuration values, not confuse these two encodings.

The mechanism is not learned at the event layer. If admitted later, learning begins at account adaptation:
repayment, collateral changes, borrowing, eMode change, liquidation and exit after the exact shock.

## Twelve conjunctive gates

The audit passes only if all gates pass:

1. exact official source commit and remote;
2. clean source checkout;
3. all fourteen required files;
4. all frozen normalized markers;
5. `configureReserveAsCollateral` has no user-configuration reference or account iteration (its pending-LTV path
   is explicitly present and is not mislabelled as reserve-only);
6. exact weighted accumulator and `wadDiv` arithmetic;
7. explicit eMode-versus-base-LT routing;
8. account/reserve views needed for later design;
9. the HF boundary and necessary liquidation checks;
10. config-engine `CollateralUpdate` routing to the pool configurator;
11. all deterministic identity self-checks; and
12. pinned licence provenance.

Markers do not prove deployment. The exact commit and file hashes make the source object reproducible; a later
protocol must independently identify historical proxy implementations.

## Decisions

- All gates pass: `PASS_SOURCE_EFFECT_IDENTITY_AUTHORIZE_AAVE_CHAIN_EVENT_INVENTORY_DESIGN_ONLY`.
- Any source/scientific gate fails: `FAIL_SOURCE_EFFECT_IDENTITY_KEEP_AAVE_UNADMITTED`.
- An exception writes `INFRASTRUCTURE_FAILURE_NO_AAVE_SOURCE_EFFECT_RESULT`, not a scientific result.

A pass authorizes only a separately frozen Ethereum deployment/version and LT-event inventory **design**. It does
not authorize running that inventory, opening accounts, claiming a denominator, passing G1, fitting a causal model
or starting GPUs. A fail triggers source reselection, not relaxed markers.

## Access and resources

The run reads one clean partial checkout containing fourteen official text files. It retains paths, byte counts,
SHA-256 hashes, marker/gate booleans and toy effects, but no raw source bodies. There is no RPC, API, paid data,
account row, worker or GPU access.

Expected cost after checkout is under one minute, one local CPU core and well below 100 MiB. Both V100 workers and
the RTX 2060 remain idle. Source is staged only after the protocol commit is pushed; the audit runs once from a
clean detached worktree. The first success or failure outcome is immutable under v1.
