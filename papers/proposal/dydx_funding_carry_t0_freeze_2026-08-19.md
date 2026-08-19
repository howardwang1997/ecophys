# dYdX fixed-funding-carry T0 freeze — 2026-08-19

## Purpose and lock point

This protocol is frozen after reading governance payloads, rules, API schemas and prior work, but before reading
any trade, candle, open-interest, price, basis or realized-funding outcome around an intervention. T0 asks
whether an on-chain change in fixed funding carry can identify a non-trivial scheduled-cost response. It does
not test whether the response is empirically present.

The causal contrast is a change in `default_funding_ppm` while the hourly funding clock is unchanged. The target
is the signed pre-boundary exit/post-boundary re-entry response, not generic funding-time periodicity.

## Frozen causal model

For market `i`, funding hour `h` and trader `j`:

```text
governance state Z_ih -> expected/realized funding R_ih -> boundary action X_ijh -> trade flow Y_ih
         |                         ^                         ^
         |                         |                         |
         +------ market rules -----+        U_ih -----------+
```

`U_ih` contains news, inventory, liquidity demand and latent trader state. The clean governance payload and
same-clock comparison identify the total effect of the parameter change `Z`; they do not by themselves identify
the effect of endogenous realized funding `R`. Any IV interpretation of `R` additionally requires relevance,
exclusion through funding exposure and monotonicity and must be reported separately from the reduced-form result.

Treatment time is the first block that executes a passed proposal, not its announcement, submission or rounded
voting-end time. D0 must locate that block and verify the full state immediately before and after it.

## Frozen cohorts

### Development reversal waves

- proposal 314: `2Z`, `ASTER`, `ATH`, `BEAM`, `BERA`, `DRIFT`;
- proposal 315: `EIGEN`, `ENA`, `HYPE`, `KAITO`, `MNT`, `MORPHO`, `MOVE`, `ONDO`;
- proposal 316: `PAXG`, `PENGU`, `POL`, `POPCAT`, `SPX`, `S`, `SYRUP`.

### Untouched confirmation

- proposal 317: `TAO`, `TRUMP`, `USUAL`, `XMR`, `ZEC`, `ZEN`.

Proposal 318's `ZORA` is secondary only. It cannot replace proposal 317 or rescue failure.

### Locked forward-direction test

Proposal 220 is evaluated only on `ONDO`, `ENA`, `TAO`, `XMR`, `MNT`, `POPCAT`, `BEAM`, `ZEN`, `PAXG` and
`DRIFT`. These are the markets with an explicit earlier zero state and a later eligible reversal. Its post
window is seven full days because a bundled cross-margin/liquidity upgrade passed eight days later.

### Exclusions

- `AVNT`, `CRO`, `PUMP`, `WLFI` and `XPL`: no independently reconstructed immediately preceding full state;
- FARTCOIN: proposal 318 bundled default funding with market-type and liquidity-tier changes;
- any market with another rule, listing, tick-size, step-size, margin, liquidity-tier, oracle or trading-status
  change inside the frozen event window;
- any event whose executing block or `h-1` state cannot be recovered; and
- any market failing the data-completeness and pre-period activity floors below.

Exclusions may only increase through these rules. No excluded market may be restored after outcomes are read.

## Frozen response construction

At each UTC hourly boundary, form taker buy and sell notional in five-minute windows. With `S` and `B` denoting
sell and buy notional, define

```text
I_pre  = (S - B) / (S + B) over minutes [-5, -1]
I_post = (B - S) / (B + S) over minutes [ 0,  4]
D_00   = (I_pre + I_post) / 2
A      = D_00 - mean(D_15, D_30, D_45),
```

where each pseudo-boundary uses the identical pre/post construction. Zero-denominator windows are missing, not
zero. Trade notional is `price * size`; the API taker-side convention must be verified against official source
and one deterministic fixture before analysis.

The primary reduced-form coefficient is the stacked pre/post change in `A` for treated markets relative to
eligible same-platform controls and event-specific time effects. Raising fixed positive carry (`0 -> 100`) must
increase `A`; removing it (`100 -> 0`) must decrease `A`. Exact equality of forward and reverse magnitudes is not
predicted because margin regimes and market states differ.

Secondary, hierarchically ordered outcomes are:

1. realized total funding and midpoint/oracle basis as first-stage and economic-state checks;
2. pre/post open-interest change;
3. unsigned trade-count and notional pulses; and
4. return and absolute-return responses.

Historical spread and depth are unavailable and therefore forbidden outcomes. Unsigned outcomes cannot support
the primary mechanism claim.

## Event windows, controls and estimators

- reversal waves: 28 full UTC days before and after execution, dropping the execution partial hour;
- forward proposal 220: seven full UTC days before and after execution;
- primary pulse windows: five minutes on each side of the real or pseudo-boundary;
- inference unit: market, with randomization inference over eligible market labels and wild-cluster bootstrap;
- nuisance controls: market fixed effects, UTC date-by-hour fixed effects, day-of-week, pre-period log volume,
  volatility, open interest, market age, margin type and liquidity tier;
- event-study leads/lags: daily coefficients, with no bin chosen after results;
- proposal 314--316 models and transformations are frozen before opening proposal-317 outcomes;
- proposal 220 is opened only after the reverse-wave estimator and confirmation result are immutable.

Eligible controls must have been listed at least 60 days before the event, have no governance or trading-status
change within 35 days of execution, have valid data on at least 95% of expected minutes, and record at least 100
trades on at least 21 of the 28 pre-event days. For the seven-day forward window, the analogous activity rule is
100 trades on at least five pre-event days. Activity floors use pre-period data only and are not tunable.

The primary estimator is a stacked difference-in-discontinuities: the change in the real-hour boundary dipole
relative to the three within-hour pseudo-boundaries, compared across treated and eligible markets before and
after execution. A within-treated estimate is reported when no defensible same-type controls exist, but it does
not replace the controlled estimate.

## Falsification battery

All of the following are mandatory:

1. pseudo-execution dates at `-14`, `-7`, `+7` and `+14` days where they do not cross another proposal;
2. pseudo-boundaries at minutes 15, 30 and 45;
3. proposal-announcement and voting-start leads to detect anticipation;
4. never-treated and not-yet-treated same-platform controls;
5. exclusion of the top one and top three absolute-return hours in each event window;
6. leave-one-market-out and leave-one-proposal-out estimates;
7. the permanently contaminated FARTCOIN event as a labelled negative design control, never pooled with clean
   events; and
8. exact schema, pagination, duplicate, missingness and timestamp tests before any model fit.

## PASS, AMBER and stop rules

T0 PASS only authorizes D0 if all are true:

- at least ten paired markets and at least 20 clean reversal markets survive full-state verification;
- the nearest-work audit confirms that causal fixed-dose response at a fixed clock is not equivalent to known
  funding periodicity, perpetual pricing or fixed-carry/intensity separation;
- public history exposes side, price, size, timestamp/height and funding effective height without paid access;
- proposal 317 can remain untouched until model freeze, and proposal 220 can remain untouched until the reverse
  test is immutable; and
- the signed prediction would change how a protocol evaluates fixed carry, rather than merely improve return
  prediction.

T0 is AMBER, not PASS, if exact state is clean but public trade-side history or data rights remain uncertain.
It fails if fewer than five paired or 15 reverse markets survive, if a change in funding clock is discovered, or
if the only distinguishable claim is an unsigned activity/volatility pattern.

After D0, the empirical mechanism is stopped if the fixed parameter has no detectable first stage in realized
funding exposure, proposal-317 direction does not agree with the frozen sign, the proposal-220 direction does
not reverse, or pseudo-boundaries move comparably. A null is publishable as a design result only if precision
excludes the frozen smallest effect of interest; it cannot be relabelled as a different mechanism.

The frozen smallest effect of scientific interest is an absolute `0.02` change in normalized dipole `A` for the
100-ppm-per-eight-hour parameter step. This is a design threshold, not a promised effect.

## Data and compute lock

T0 may access governance payloads, source code, terms, API schemas, endpoint headers and academic papers. It may
not access intervention-window trade, candle, price, open-interest, basis or realized-funding values.

D0, if unlocked, may inspect schemas, pagination, timestamps, block coverage, response counts and missingness
while discarding numeric outcomes. Its caps are 20 CPU core-hours and 2 GB temporary data. GPU, paid data and
EcoMD are forbidden.

The first outcome pilot, if separately frozen after D0, is expected to require 5--20 GB raw JSON, less than
5 GB Parquet and 100 CPU core-hours. No GPU is scientifically required. V100, RTX2060 and all future GPU pools
remain locked until a later learned estimator has a pre-specified role that non-neural event-study methods
cannot perform.

## Sources frozen into T0

- [dYdX governance proposal 220 discussion](https://dydx.forum/t/drc-update-default-funding-rate-for-isolated-markets/3417)
- [dYdX governance reversal discussion](https://dydx.forum/t/fix-set-default-funding-ppm-to-0-for-recently-upgraded-cross-markets/4804)
- [dYdX perpetual schema](https://github.com/dydxprotocol/v4-chain/blob/main/proto/dydxprotocol/perpetuals/perpetual.proto)
- [dYdX Indexer](https://github.com/dydxprotocol/v4-chain/tree/main/indexer)
- [dYdX software terms](https://dydx.exchange/v4-terms)
- [Ahmed and Bhuyan, SSRN 7143718](https://doi.org/10.2139/ssrn.7143718)

