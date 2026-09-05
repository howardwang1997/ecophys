from __future__ import annotations

import csv
import zipfile
from pathlib import Path

import pytest

from scripts.fcc_clock1_support_audit import (
    SCHEMAS,
    load_instructions,
    load_result_keys,
    summarize_support,
)


def write_csv_zip(path: Path, member: str, rows: list[list[str]]) -> None:
    csv_path = path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerows(rows)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(csv_path, arcname=member)


def test_clock1_support_requires_constraint_hit_on_coupled_instruction(
    tmp_path: Path,
) -> None:
    bids = tmp_path / "bids.zip"
    results = tmp_path / "results.zip"
    write_csv_zip(
        bids,
        "bids.csv",
        [
            [
                "auction_id",
                "round",
                "frn",
                "market",
                "channel_block",
                "price_point",
                "selection_number",
            ],
            ["113", "1", "A", "M1", "P1", "0.5", "10"],
            ["113", "1", "B", "M1", "P1", "0.5", "20"],
            ["113", "1", "C", "M2", "P2", "0.5", "30"],
            ["113", "2", "D", "M3", "P3", "0.6", "40"],
            ["113", "2", "D", "M4", "P4", "0.6", "50"],
            ["113", "3", "E", "M5", "P5", "0.7", "60"],
        ],
    )
    write_csv_zip(
        results,
        "results.csv",
        [
            [
                "auction_id",
                "round",
                "frn",
                "market",
                "channel_block",
                "fully_applied_flag",
            ],
            ["113", "1", "A", "M1", "P1", "Y"],
            ["113", "1", "B", "M1", "P1", "N"],
            ["113", "1", "C", "M2", "P2", "N"],
            ["113", "2", "D", "M3", "P3", "N"],
            ["113", "2", "D", "M4", "P4", "Y"],
            ["113", "3", "E", "M5", "P5", "N"],
        ],
    )
    result_keys, negative_keys, result_rows = load_result_keys(
        results,
        auction_id="113",
        schema=SCHEMAS["113"],
    )
    instructions, bid_rows, discarded_switch_to_rows = load_instructions(
        bids,
        auction_id="113",
        schema=SCHEMAS["113"],
    )
    summary = summarize_support(
        auction_id="113",
        instructions=instructions,
        result_keys=result_keys,
        negative_result_keys=negative_keys,
        bid_rows=bid_rows,
        result_rows=result_rows,
        discarded_switch_to_rows=discarded_switch_to_rows,
        minimum_tie_blocks=3,
    )
    assert summary["instructions"] == 6
    assert summary["tie_blocks"] == 3
    assert summary["multi_instruction_tie_blocks"] == 2
    assert summary["structurally_coupled_tie_blocks"] == 2
    assert summary["instructions_with_any_n_flag"] == 4
    assert summary["order_sensitive_support_upper_bound"] == 2
    assert summary["upper_bound_prefilter_pass"] is False


def test_switch_rows_collapse_to_one_instruction_at_from_leg_price(
    tmp_path: Path,
) -> None:
    bids = tmp_path / "bids.zip"
    results = tmp_path / "results.zip"
    bid_header = [
        "auction_id",
        "round",
        "frn",
        "market",
        "category",
        "price_point",
        "selection_number",
        "bid_type",
        "switch_from_category",
        "switch_to_category",
    ]
    write_csv_zip(
        bids,
        "bids.csv",
        [
            bid_header,
            ["108", "1", "A", "M1", "C1", "0.4", "10", "Switch", "", "C2"],
            ["108", "1", "A", "M1", "C2", "1.0", "10", "Switch", "C1", ""],
            ["108", "1", "B", "M1", "C1", "0.4", "20", "Simple", "", ""],
        ],
    )
    write_csv_zip(
        results,
        "results.csv",
        [
            [
                "auction_id",
                "round",
                "frn",
                "market",
                "category",
                "fully_processed_flag",
            ],
            ["108", "1", "A", "M1", "C1", "N"],
            ["108", "1", "A", "M1", "C2", "N"],
            ["108", "1", "B", "M1", "C1", "Y"],
        ],
    )
    result_keys, negative_keys, result_rows = load_result_keys(
        results,
        auction_id="108",
        schema=SCHEMAS["108"],
    )
    instructions, bid_rows, discarded_switch_to_rows = load_instructions(
        bids,
        auction_id="108",
        schema=SCHEMAS["108"],
    )
    summary = summarize_support(
        auction_id="108",
        instructions=instructions,
        result_keys=result_keys,
        negative_result_keys=negative_keys,
        bid_rows=bid_rows,
        result_rows=result_rows,
        discarded_switch_to_rows=discarded_switch_to_rows,
        minimum_tie_blocks=1,
    )
    assert summary["instructions"] == 2
    assert summary["discarded_switch_to_rows"] == 1
    assert summary["tie_blocks"] == 1
    assert summary["multi_instruction_tie_blocks"] == 1
    assert summary["order_sensitive_support_upper_bound"] == 1
    assert summary["upper_bound_prefilter_pass"] is True


def test_malformed_switch_fails_closed(tmp_path: Path) -> None:
    bids = tmp_path / "bids.zip"
    write_csv_zip(
        bids,
        "bids.csv",
        [
            [
                "auction_id",
                "round",
                "frn",
                "market",
                "category",
                "price_point",
                "selection_number",
                "bid_type",
                "switch_from_category",
                "switch_to_category",
            ],
            ["108", "1", "A", "M1", "C2", "1.0", "10", "Switch", "", ""],
        ],
    )
    with pytest.raises(ValueError, match="invalid_rows=1"):
        load_instructions(bids, auction_id="108", schema=SCHEMAS["108"])
