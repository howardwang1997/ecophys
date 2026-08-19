# dYdX fixed-funding-carry T0 result — 2026-08-20

## Decision

**T0 PASS, authorizing metadata-only D0.** This is not evidence that the signed boundary response exists. No
trade, candle, price, open-interest, basis or realized-funding outcome was opened during T0.

The frozen minimums are met: ten paired `0 -> 100 -> 0` markets and 28 clean `100 -> 0` reversals have a
complete passed-governance parameter lineage. Every eligible transition changes only `default_funding_ppm` in
the full message payload. The development set alone contains 21 markets, so proposal 317 remains an untouched
six-market confirmation wave and proposal 220 remains locked as the opposite-direction test.

## Exact execution blocks

The first block strictly after each nanosecond voting deadline was located from public historical block headers.
Its `active_proposal` event records `proposal_passed` in `EndBlock`; the immediately preceding block has a time
before the deadline. Block IDs below are the CometBFT block hashes.

| Proposal | Last pre-deadline block | Time (UTC) | Executing block | Time (UTC) | Executing block hash |
|---|---:|---|---:|---|---|
| 220 | 38694463 | 2025-03-03 02:28:29.271191997 | 38694464 | 02:28:30.245352527 | `71A9A07B9B253FCE4E6F8892F4EADDD79A4689BC0C881EF54DE8E56E03552CE5` |
| 314 | 63326126 | 2025-11-14 12:07:36.127193005 | 63326127 | 12:07:36.732286866 | `193474E53A213B7ACAE72C2620B2326A70B5B93696B4930F7859C83116D143E2` |
| 315 | 63626788 | 2025-11-16 16:31:53.229178773 | 63626789 | 16:31:53.817651095 | `0C59111D63675F2DF15896A570B244B050BD3B45F5B4A3D552CFAF99306C5AED` |
| 316 | 63626887 | 2025-11-16 16:32:57.431679872 | 63626888 | 16:32:58.083063704 | `0A428F4AB98104D608411A37E9BA2271879EB7A9F7C11CA66D16666581F4880B` |
| 317 | 63981004 | 2025-11-19 06:19:54.448580956 | 63981005 | 06:19:55.023295249 | `98E44E17A6949CF754303A1CEBEF6803D7E64B9AE5094B79D23E45AD4B151D72` |
| 318 | 63981518 | 2025-11-19 06:25:18.043396332 | 63981519 | 06:25:18.598999959 | `A2585DD5C0DF286CBECDCC66F9750CAEF952063C21CF65F742A000E27C3691BC` |

The update executes at the end of the listed block. Accordingly, committed post-state is available after that
block and the outcome design drops the partial execution hour. It never treats the rounded web timestamp as an
activation instant.

## State-proof chain

This proof is a reproducible transition ledger, not a historical RPC snapshot:

1. a current public Cosmos REST node returned all 391 governance proposals in one counted page;
2. only passed `MsgUpdatePerpetualParams` messages were retained, ordered by nanosecond voting end;
3. for each frozen ticker, the immediately previous full payload and event payload were compared field by field;
4. all 28 reversal payloads are `100 -> 0` with `changed_payload_fields = [default_funding_ppm]`, and all ten
   paired forward payloads are `0 -> 100` with the same singleton change;
5. official protobuf states that every field must be set; the message server checks module authority and writes
   the funding and liquidity fields; and the ante handler rejects this internal message from external
   transactions; and
6. the historical `EndBlock` event independently confirms that each named proposal passed and executed at the
   located height.

This establishes the relevant state difference at `h-1` and committed state after `h` without pretending that
pruned public RPC nodes served a point-in-time query. A future archive snapshot may be added as redundant
validation, but is not required to reconstruct the governed transition.

## Remaining claim boundary

Nearest work covers funding-time periodicity, perpetual pricing, funding-formula design and separation of fixed
carry from convergence intensity. It does not, in the sources audited at the freeze, estimate a governance dose
change at an unchanged clock with a signed exit/re-entry dipole and switching-friction interpretation. This
novelty conclusion is provisional and must be rerun before submission.

T0 therefore unlocks only the frozen D0 protocol in
`configs/empirical_physics/dydx_funding_carry_d0_v1.yaml`. D0 may retain endpoint schemas, counts, timestamps,
heights and content hashes. It must discard all price, size, side, funding-rate, OHLC, OI and midpoint values,
must not query the proposal-317 outcome window, and must not query the proposal-220 outcome window.

No GPU, paid data or EcoMD work is authorized.
