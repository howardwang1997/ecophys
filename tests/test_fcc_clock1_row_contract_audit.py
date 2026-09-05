from __future__ import annotations

import csv
import zipfile
from pathlib import Path

import pytest

from scripts.fcc_clock1_row_contract_audit import audit_row_contract

BID_HEADER = [
    "auction_id",
    "round",
    "frn",
    "market",
    "category",
    "bid_type",
    "quantity",
    "switch_from_category",
    "switch_to_category",
    "previous_round_processed_demand",
    "price_point",
    "price",
    "start_of_round_price",
]
RESULT_HEADER = [
    "auction_id",
    "round",
    "frn",
    "market",
    "category",
    "processed_demand",
    "fully_processed_flag",
]


def write_zip(path: Path, member: str, header: list[str], rows: list[list[object]]) -> None:
    csv_path = path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    with zipfile.ZipFile(path, "w") as archive:
        archive.write(csv_path, member)


def test_audit_counts_unmatched_action_changing_row(tmp_path: Path) -> None:
    bids = tmp_path / "bids.zip"
    results = tmp_path / "results.zip"
    write_zip(
        bids,
        "bids.csv",
        BID_HEADER,
        [
            ["108", 1, "a", "m", "c1", "Simple", 1, "", "", "", 1, 10, 10],
            ["108", 2, "a", "m", "c1", "Simple", 0, "", "", 1, 0, 10, 10],
        ],
    )
    write_zip(
        results,
        "results.csv",
        RESULT_HEADER,
        [["108", 1, "a", "m", "c1", 1, "Y"]],
    )
    output = audit_row_contract(bids, results)
    assert output["unmatched_rows"] == 1
    assert output["unmatched_action_changing_rows"] == 1
    assert output["bid_accounting_closes"] is True
    assert output["round1_quantity_by_match_status_ge_10"] == {}


def test_audit_accepts_switch_transition_pair(tmp_path: Path) -> None:
    bids = tmp_path / "bids.zip"
    results = tmp_path / "results.zip"
    write_zip(
        bids,
        "bids.csv",
        BID_HEADER,
        [
            ["108", 2, "a", "m", "c1", "Switch", 0, "", "c2", 1, 0.5, 15, 10],
            ["108", 2, "a", "m", "c2", "Switch", 1, "c1", "", 0, 1, 20, 10],
        ],
    )
    write_zip(
        results,
        "results.csv",
        RESULT_HEADER,
        [
            ["108", 2, "a", "m", "c1", 0, "Y"],
            ["108", 2, "a", "m", "c2", 1, "Y"],
        ],
    )
    output = audit_row_contract(bids, results)
    assert output["matched_rows"] == 2
    assert output["impossible_matched_transitions"] == 0


def test_audit_fails_closed_on_invalid_post_round_state(tmp_path: Path) -> None:
    bids = tmp_path / "bids.zip"
    results = tmp_path / "results.zip"
    write_zip(
        bids,
        "bids.csv",
        BID_HEADER,
        [["108", 2, "a", "m", "c1", "Simple", 1, "", "", "", 1, 20, 10]],
    )
    write_zip(results, "results.csv", RESULT_HEADER, [])
    with pytest.raises(ValueError, match="missing prior state"):
        audit_row_contract(bids, results)
