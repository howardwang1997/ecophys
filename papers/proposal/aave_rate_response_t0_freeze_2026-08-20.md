# Aave rate-step response spectroscopy — T0 freeze

**Frozen:** 2026-08-20, before requesting any Aave `Borrow`, `Repay`, `ReserveDataUpdated`,
position-balance, or post-intervention market value.

## Decision question

The dYdX candidate failed because a formally clean intervention did not have enough active units. This T0 asks
whether Aave supplies a larger, real-market intervention panel before any response is inspected:

> Do exact, globally visible borrowing-rate steps reveal a reproducible distribution of adjustment barriers,
> rather than merely an aggregate demand elasticity?

This is a candidate question, not a result. Aave's own Interest Rate Curve Risk Oracle already fits aggregate
isoelastic, exponential, and linear demand models to 10--15 minute supply, borrowing, and rate observations.
Therefore generic elasticity estimation, rate prediction, and welfare optimization are prior art and are not
eligible EcoPhys claims.

## Candidate mechanism

Treat a governance execution as a step in an externally recorded field. For an agent with debt exposure
`D_i`, define the signed integrated incremental carry after execution as

\[
X_i(t)=\int_0^t D_i(s)\,[r_i^+(s)-r_i^-(s)]\,ds.
\]

In the non-interacting threshold limit, an agent adjusts when `|X_i(t)|` first crosses a latent barrier `C_i`.
Conditional survival then satisfies

\[
\Pr(T_i>t\mid D_i)=1-F_C(|X_i(t)|).
\]

Multiple step sizes provide an over-identifying test: response curves should collapse in integrated-carry
coordinates if a common barrier distribution is real. Failure to collapse, execution-time anticipation, or
endogenous utilization feedback are scientifically meaningful falsifiers, not tuning targets. A publishable
larger story would require an inversion method that handles censoring, feedback, heterogeneous risk sets and
staggered cross-chain execution, plus transfer beyond one protocol.

## Frozen primary panel

The official Aave governance cache and proposal source identify six Ethereum Core executions for which DAI,
USDC and USDT each change only the configured `variableRateSlope1`; changes to
`maxVariableBorrowRate` are algebraically derived, and old deployments may replace the strategy address.

| Proposal | Direction | Slope1 (bp) | Role |
|---:|:---:|---:|---|
| 3 | up | 500 → 600 | reverse-sign probe |
| 94 | down | 1200 → 900 | primary |
| 130 | down | 900 → 650 | primary |
| 159 | down | 650 → 550 | primary |
| 247 | down | 1150 → 950 | primary |
| 271 | down | 850 → 650 | primary |

This creates 15 primary rate-decrease market-event units and 18 singleton-change units including the
reverse-sign probe. Proposal 69 is excluded from the singleton panel because it also changes `UOptimal` for the
three core assets. Proposal 216 is excluded because it changes both slope 1 and slope 2. They may later serve as
rate-curve-only stress cases, never as replacements for failed primary units.

## T0 checks and hard boundary

The executable contract is
`configs/empirical_physics/aave_rate_response_t0_v1.yaml`. T0 must verify all of the following from pinned
official repositories:

1. every proposal is executed and maps to exactly one Ethereum payload execution event, block and transaction;
2. the cached AIP points to the frozen implementation commit and directory;
3. the official before/after diff shows only `variableRateSlope1` as a configured change for each selected
   asset;
4. there are at least 15 singleton market-event units;
5. a free Ethereum RPC answers only chain and event-signature metadata probes.

T0 does not authorize an outcome query. If it passes, a separate clean commit must freeze a 28-day pre-period
activity screen. That screen may retain only weekly `Borrow`/`Repay` counts and unique debt-user counts. Only
after it passes may any post-event response, amount, position, utilization, borrow rate, price, or simulation be
opened.

## Data and compute boundary

The preprint *A Cross-Chain Event-Driven Data Infrastructure for Aave Protocol Analytics and Applications*
claims a public Zenodo record at DOI `10.5281/zenodo.17898640`. Availability must be checked rather than
assumed. If the DOI is absent, T0 records that failure and uses direct public chain logs for later gates; it does
not silently describe the claimed 50-million-row dataset as acquired.

T0 is CPU-only and free. No V100, RTX 2060, H20, paid data, EcoMD run, bulk event download or 50-million-row
dataset download is authorized.

## Identification risks that remain after a T0 pass

- governance discussion and queued execution create anticipation;
- rate changes respond to market conditions and are not globally exogenous;
- utilization mechanically feeds user actions back into the realized rate;
- risk-steward changes between governance proposals require a complete policy ledger;
- repeated assets are not independent experimental units;
- entry after a rate decrease needs a defensible at-risk population, not only transaction counts;
- aggregate elasticity is already occupied by the Aave Risk Oracle.

The prospective identification route is exact-execution local discontinuity combined with unaffected assets
and staggered cross-chain payload executions. It remains a proposal until all intervention-ledger, activity,
anticipation and pre-trend gates pass.
