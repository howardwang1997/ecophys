"""Post-hoc development diagnostics for AEMO direction bundles."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import cast

from ecomd.research.aemo_row_conformance import parse_aemo_timestamp

DIAGNOSTIC_SCHEMA_VERSION = "ecophys-aemo-direction-bundle-diagnostic/v1"
FROZEN_ROW_SUMMARY_SHA256 = "fc422654de5c64a91e71b8dcceb22612f406092cdf6a36900859072041a6668b"


def _timestamp(value: str) -> str | None:
    parsed = parse_aemo_timestamp(value)
    return parsed.isoformat(timespec="microseconds") if parsed is not None else None


def _integer_equals(value: str, expected: int) -> bool:
    try:
        return Decimal(value.strip()) == expected
    except InvalidOperation:
        return False


def _sign(value: str) -> str:
    try:
        number = Decimal(value.strip())
    except InvalidOperation:
        return "UNPARSEABLE"
    if number > 0:
        return "POSITIVE"
    if number < 0:
        return "NEGATIVE"
    return "ZERO"


def _sorted_counts(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _tracker_key(row: Mapping[str, str]) -> tuple[str, str, str, str, str] | None:
    interval = _timestamp(row.get("SETTLEMENTDATE", ""))
    bid_settlement = _timestamp(row.get("BIDSETTLEMENTDATE", ""))
    offer = _timestamp(row.get("BIDOFFERDATE", ""))
    if interval is None or bid_settlement is None or offer is None:
        return None
    return (
        interval,
        row.get("DUID", ""),
        row.get("BIDTYPE", ""),
        bid_settlement,
        offer,
    )


def _period_key(row: Mapping[str, str]) -> tuple[str, str, str, str, str] | None:
    interval = _timestamp(row.get("INTERVAL_DATETIME", ""))
    bid_settlement = _timestamp(row.get("BIDSETTLEMENTDATE", ""))
    offer = _timestamp(row.get("OFFERDATE", ""))
    if interval is None or bid_settlement is None or offer is None:
        return None
    return (
        interval,
        row.get("DUID", ""),
        row.get("BIDTYPE", ""),
        bid_settlement,
        offer,
    )


def summarize_direction_bundles(
    tables: Mapping[str, Sequence[Mapping[str, str]]],
    frozen_summary: Mapping[str, object],
    *,
    analyzer_git_commit: str,
    generated_at: str,
    frozen_summary_sha256: str,
) -> dict[str, object]:
    """Describe multiplicity without resolving an applied bundle from outcomes."""

    period_index: defaultdict[tuple[str, str, str, str, str], list[str]] = defaultdict(list)
    for row in tables["BIDPEROFFER_D"]:
        key = _period_key(row)
        if key is not None:
            period_index[key].append(row.get("DIRECTION", "") or "<EMPTY>")

    physical_dispatch: dict[tuple[str, str], str] = {}
    physical_dispatch_duplicate_count = 0
    for row in tables["DISPATCHLOAD"]:
        if not _integer_equals(row.get("RUNNO", ""), 1) or not _integer_equals(
            row.get("INTERVENTION", ""), 0
        ):
            continue
        interval = _timestamp(row.get("SETTLEMENTDATE", ""))
        if interval is None:
            continue
        physical_key = (interval, row.get("DUID", ""))
        if physical_key in physical_dispatch:
            physical_dispatch_duplicate_count += 1
        physical_dispatch[physical_key] = row.get("TOTALCLEARED", "")

    identity_intervals: defaultdict[str, list[tuple[datetime, datetime, str, str]]] = defaultdict(list)
    for row in tables["DUDETAILSUMMARY"]:
        start = parse_aemo_timestamp(row.get("START_DATE", ""))
        end = parse_aemo_timestamp(row.get("END_DATE", ""))
        if start is None or end is None or start >= end:
            continue
        identity_intervals[row.get("DUID", "")].append(
            (
                start,
                end,
                row.get("DISPATCHTYPE", "") or "<EMPTY>",
                row.get("DISPATCHSUBTYPE", "") or "<EMPTY>",
            )
        )

    candidate_cardinality: Counter[str] = Counter()
    direction_sets: Counter[str] = Counter()
    ambiguous_bid_types: Counter[str] = Counter()
    ambiguous_identity_multiplicity: Counter[str] = Counter()
    ambiguous_identity_types: Counter[str] = Counter()
    ambiguous_identity_subtypes: Counter[str] = Counter()
    totalcleared_sign_by_bid_type: defaultdict[str, Counter[str]] = defaultdict(Counter)
    ambiguous_duids: set[str] = set()
    invalid_tracker_reference_count = 0
    unmatched_tracker_count = 0
    ambiguous_count = 0
    ambiguous_candidate_row_count = 0
    ambiguous_exactly_two_count = 0
    ambiguous_gen_load_pair_count = 0
    ambiguous_duplicate_direction_count = 0
    ambiguous_physical_dispatch_match_count = 0

    for row in tables["DISPATCHOFFERTRK"]:
        tracker_key = _tracker_key(row)
        if tracker_key is None:
            invalid_tracker_reference_count += 1
            continue
        directions = period_index.get(tracker_key, [])
        cardinality = len(directions)
        candidate_cardinality[str(cardinality)] += 1
        direction_set = "|".join(sorted(set(directions))) if directions else "<NONE>"
        direction_sets[direction_set] += 1
        if cardinality == 0:
            unmatched_tracker_count += 1
        if cardinality <= 1:
            continue

        ambiguous_count += 1
        ambiguous_candidate_row_count += cardinality
        bid_type = row.get("BIDTYPE", "") or "<EMPTY>"
        ambiguous_bid_types[bid_type] += 1
        ambiguous_duids.add(row.get("DUID", ""))
        if cardinality == 2:
            ambiguous_exactly_two_count += 1
        if cardinality == 2 and set(directions) == {"GEN", "LOAD"}:
            ambiguous_gen_load_pair_count += 1
        if len(directions) != len(set(directions)):
            ambiguous_duplicate_direction_count += 1

        identity_timestamp = datetime.fromisoformat(tracker_key[0])
        identities = [
            (dispatch_type, dispatch_subtype)
            for start, end, dispatch_type, dispatch_subtype in identity_intervals.get(tracker_key[1], [])
            if start <= identity_timestamp < end
        ]
        ambiguous_identity_multiplicity[str(len(identities))] += 1
        if len(identities) == 1:
            ambiguous_identity_types[identities[0][0]] += 1
            ambiguous_identity_subtypes[identities[0][1]] += 1

        total_cleared = physical_dispatch.get((tracker_key[0], tracker_key[1]))
        if total_cleared is not None:
            ambiguous_physical_dispatch_match_count += 1
            totalcleared_sign_by_bid_type[bid_type][_sign(total_cleared)] += 1

    tracker_count = len(tables["DISPATCHOFFERTRK"])
    frozen_joins = cast(Mapping[str, object], frozen_summary["joins"])
    frozen_tracker_count = cast(int, frozen_joins["tracker_count"])
    frozen_ambiguous_count = cast(int, frozen_joins["tracker_period_ambiguous_count"])
    if tracker_count != frozen_tracker_count or ambiguous_count != frozen_ambiguous_count:
        raise ValueError("diagnostic multiplicity does not reproduce the frozen E1a result")

    return {
        "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "status": "POST_HOC_DEVELOPMENT_DIAGNOSTIC_NO_GATE_DECISION",
        "frozen_e1a_summary_sha256": frozen_summary_sha256,
        "reconciliation": {
            "tracker_count": tracker_count,
            "frozen_tracker_count": frozen_tracker_count,
            "ambiguous_count": ambiguous_count,
            "frozen_ambiguous_count": frozen_ambiguous_count,
            "exact_reproduction": True,
        },
        "candidate_structure": {
            "invalid_tracker_reference_count": invalid_tracker_reference_count,
            "unmatched_tracker_count": unmatched_tracker_count,
            "candidate_cardinality": _sorted_counts(candidate_cardinality),
            "direction_sets": _sorted_counts(direction_sets),
            "ambiguous_candidate_row_count": ambiguous_candidate_row_count,
            "ambiguous_exactly_two_count": ambiguous_exactly_two_count,
            "ambiguous_gen_load_pair_count": ambiguous_gen_load_pair_count,
            "ambiguous_duplicate_direction_count": (ambiguous_duplicate_direction_count),
            "ambiguous_unique_duid_count": len(ambiguous_duids),
            "ambiguous_bid_types": _sorted_counts(ambiguous_bid_types),
        },
        "identity_context": {
            "ambiguous_identity_match_multiplicity": _sorted_counts(ambiguous_identity_multiplicity),
            "ambiguous_dispatch_types": _sorted_counts(ambiguous_identity_types),
            "ambiguous_dispatch_subtypes": _sorted_counts(ambiguous_identity_subtypes),
        },
        "realized_dispatch_context": {
            "physical_dispatch_duplicate_count": physical_dispatch_duplicate_count,
            "ambiguous_physical_dispatch_match_count": (ambiguous_physical_dispatch_match_count),
            "totalcleared_sign_by_bid_type": {
                bid_type: _sorted_counts(counter)
                for bid_type, counter in sorted(totalcleared_sign_by_bid_type.items())
            },
            "sign_is_descriptive_not_an_action_selector": True,
        },
        "diagnostic_flags": {
            "all_ambiguous_exactly_two": (
                ambiguous_count > 0 and ambiguous_exactly_two_count == ambiguous_count
            ),
            "all_ambiguous_are_gen_load_pairs": (
                ambiguous_count > 0 and ambiguous_gen_load_pair_count == ambiguous_count
            ),
            "all_ambiguous_have_one_effective_identity": (
                ambiguous_identity_multiplicity == Counter({"1": ambiguous_count})
            ),
            "all_ambiguous_identities_are_bidirectional": (
                ambiguous_identity_types == Counter({"BIDIRECTIONAL": ambiguous_count})
            ),
        },
        "interpretation_boundary": {
            "tested_post_hoc": True,
            "e1a_failure_overridden": False,
            "fresh_day_confirmation_required": True,
            "realized_dispatch_may_not_select_ex_ante_offer_direction": True,
            "no_causal_or_model_claim": True,
        },
        "gpu_used": False,
        "paid_data_used": False,
        "new_source_request_used": False,
    }
