# AEMO direction-bundle post-hoc development diagnostic

**Status:** analysis code frozen before the diagnostic run, but the motivating aggregate result is already known.
This is explicitly post-hoc and has no confirmatory pass/fail gate.

## Motivation and non-overridable prior result

Frozen E1a is `FAIL_MODERN_ROW_CONFORMANCE_SMOKE`: 43,200/592,560 tracker rows had more than one period-bid
direction candidate. This diagnostic cannot override that decision or relax its 5% threshold.

AEMO's official [Data Model v5.3 participant impact](https://tech-specs.docs.public.aemo.com.au/Content/TSP_EMMSDM53_April2024/Participant_Impact.htm)
states that bidirectional units have distinct `GEN` and `LOAD` bid rows. Its
[Bidding and Dispatch specification](https://tech-specs.docs.public.aemo.com.au/Content/TSP_EMMS_June2024/Bidding_and_Dispatch.htm)
requires two directions for BDU energy and regulation FCAS bids, while contingency FCAS remains a single
direction-independent offer. The official
[DISPATCHLOAD update](https://tech-specs.docs.public.aemo.com.au/Content/TSP_EMMSDM53_April2024/Electricity_Data_Model_5.3.htm?TocPath=Electricity+Data%C2%A0Model%7CDM+5.3+-+April+2024%7C_____5)
does not add a direction field; it gives negative `TOTALCLEARED` for BDU import and positive values otherwise.

This suggests two rival interpretations: the multiplicity is either a malformed join, or the applied action is a
bundle containing both direction-specific legs. Using realized `TOTALCLEARED` to select an ex-ante bid leg would
leak the outcome into the action representation and is prohibited.

## Frozen descriptive questions

Using only the already-retained 16 June 2026 development objects:

1. Reproduce the exact frozen tracker and ambiguity counts.
2. Tabulate candidate cardinality and direction sets for every tracker row.
3. For ambiguous rows only, tabulate bid type, unique DUID count, candidate count and repeated-direction defects.
4. Join the effective-dated identity and tabulate `DISPATCHTYPE`/`DISPATCHSUBTYPE` without listing DUIDs.
5. Tabulate the sign of physical `TOTALCLEARED` by bid type as descriptive realized context only.

No threshold is fitted and no model is run. The output may support a *proposal* for a set-valued action bridge only
if every ambiguous record is exactly a two-row `{GEN, LOAD}` pair with one effective bidirectional identity. Any
such proposal must be frozen and tested on a fresh mechanically selected day. Otherwise the public applied-action
bridge remains unresolved.

## Resources and claim boundary

The diagnostic reuses exact local bytes already verified against the committed receipt and R2 metadata. It makes
no source request and needs CPU only. It is development evidence about representation, not a causal effect,
mechanism replay, model result or paper-level discovery.
