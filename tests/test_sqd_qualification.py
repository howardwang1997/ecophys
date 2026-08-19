from __future__ import annotations

import json

import pytest

from ecomd.data.sqd_qualification import (
    BlockWindow,
    canonical_sha256,
    parse_stream_payload,
    select_block_windows,
    validate_block_window,
)


def _block(number: int) -> dict[str, object]:
    block_hash = "0x" + f"{number:064x}"
    parent_hash = "0x" + f"{number - 1:064x}"
    return {
        "header": {
            "number": number,
            "hash": block_hash,
            "parentHash": parent_hash,
            "timestamp": 1_700_000_000 + number,
        }
    }


def test_parse_stream_payload_accepts_array_and_json_lines() -> None:
    records = [_block(10), _block(11)]
    assert parse_stream_payload(json.dumps(records)) == records
    assert parse_stream_payload("\n".join(json.dumps(item) for item in records)) == records
    assert parse_stream_payload("") == []


def test_select_block_windows_is_deterministic_and_in_bounds() -> None:
    windows = select_block_windows(0, 10_000, fractions=[0.1, 0.5, 0.9], width=6, near_head_lag=100)
    assert [item.label for item in windows] == [
        "fraction_0.100",
        "fraction_0.500",
        "fraction_0.900",
        "near_finalized",
    ]
    assert all(0 <= item.first < item.last <= 10_000 for item in windows)
    assert windows == select_block_windows(
        0, 10_000, fractions=[0.1, 0.5, 0.9], width=6, near_head_lag=100
    )


def test_validate_block_window_accepts_exact_header_chain() -> None:
    window = BlockWindow("test", 10, 15)
    result = validate_block_window([_block(number) for number in range(10, 16)], window)
    assert result["all_checks_pass"] is True
    assert result["canonical_sha256"] == canonical_sha256([_block(number) for number in range(10, 16)])


def test_validate_block_window_rejects_gap_and_event_rows() -> None:
    window = BlockWindow("test", 10, 15)
    records = [_block(number) for number in range(10, 16) if number != 12]
    records[0]["logs"] = [{"address": "forbidden"}]
    result = validate_block_window(records, window)
    assert result["all_checks_pass"] is False
    assert result["checks"]["numbers_exact"] is False
    assert result["checks"]["no_event_rows"] is False


def test_window_validation_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        select_block_windows(10, 9, fractions=[0.5], width=6, near_head_lag=0)
    with pytest.raises(ValueError):
        select_block_windows(0, 100, fractions=[1.1], width=6, near_head_lag=0)
