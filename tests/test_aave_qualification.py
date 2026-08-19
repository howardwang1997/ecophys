from __future__ import annotations

import json

from ecomd.data.aave_qualification import (
    address_topic,
    audit_asset_rate_change,
    canonical_sha256,
    extract_implementation_reference,
    summarize_preperiod_activity,
)


def test_asset_rate_audit_allows_only_deployment_and_derived_rows() -> None:
    markdown = """
#### USDC ([0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48](https://example.test))

| description | value before | value after |
| --- | --- | --- |
| interestRateStrategy | old | new |
| baseStableBorrowRate | 12.5 % | 10.5 % |
| maxVariableBorrowRate | 46.5 % | 44.5 % |
| variableRateSlope1 | 11.5 % | 9.5 % |
| interestRate | before-image | after-image |

## Raw diff
"""
    result = audit_asset_rate_change(
        markdown,
        symbol="USDC",
        expected_before_bps=1150,
        expected_after_bps=950,
    )
    assert result["configured_change_fields"] == ["variableRateSlope1"]
    assert result["slope1_delta_bps"] == -200
    assert result["clean_singleton_configured_change"] is True


def test_asset_rate_audit_rejects_a_second_configured_change() -> None:
    markdown = """
#### DAI ([0x6B175474E89094C44Da98b954EedeAC495271d0F](https://example.test))

| description | value before | value after |
| --- | --- | --- |
| variableRateSlope1 | 9 % | 6.5 % |
| optimalUsageRatio | 90 % | 92 % |
"""
    try:
        audit_asset_rate_change(
            markdown,
            symbol="DAI",
            expected_before_bps=900,
            expected_after_bps=650,
        )
    except ValueError as error:
        assert "unexpected configured changes" in str(error)
    else:
        raise AssertionError("a bundled configured change must fail the singleton audit")


def test_implementation_reference_and_address_topic() -> None:
    description = (
        "https://github.com/aave-dao/aave-proposals-v3/blob/"
        "78b4d81bddc1978b7807d39859b806883e087d15/"
        "src/20250312_Multi_StablecoinsInterestRateCurveUpdate/Payload.sol"
    )
    assert extract_implementation_reference(description) == (
        "78b4d81bddc1978b7807d39859b806883e087d15",
        "20250312_Multi_StablecoinsInterestRateCurveUpdate",
    )
    assert address_topic("0x00000000000000000000000000000000000000aA") == (
        "0x00000000000000000000000000000000000000000000000000000000000000aa"
    )


def test_canonical_digest_survives_json_key_normalization() -> None:
    value = {"excluded": {69: "first", 216: "second"}}
    round_tripped = json.loads(json.dumps(value))
    assert canonical_sha256(value) == canonical_sha256(round_tripped)


def _activity_log(
    *,
    pool: str,
    event_topic: str,
    asset: str,
    user_byte: int,
    block_number: int,
    log_index: int,
) -> dict[str, object]:
    byte = f"{user_byte:02x}"
    return {
        "address": pool,
        "topics": [
            event_topic,
            address_topic(asset),
            "0x" + "00" * 31 + byte,
            "0x" + "11" * 32,
        ],
        "data": "0x" + "5345435245545f414d4f554e54".ljust(64, "0"),
        "blockNumber": hex(block_number),
        "blockHash": "0x" + f"{block_number:064x}",
        "transactionHash": "0x" + f"{block_number * 100 + log_index:064x}",
        "transactionIndex": "0x0",
        "logIndex": hex(log_index),
        "removed": False,
    }


def test_preperiod_activity_reducer_retains_only_counts() -> None:
    pool = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    dai = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    borrow_topic = "0x" + "ab" * 32
    repay_topic = "0x" + "cd" * 32
    windows: list[dict[str, object]] = []
    for week_index, start in enumerate((100, 200), start=1):
        logs = [
            _activity_log(
                pool=pool,
                event_topic=borrow_topic,
                asset=dai,
                user_byte=week_index,
                block_number=start,
                log_index=0,
            ),
            _activity_log(
                pool=pool,
                event_topic=repay_topic,
                asset=dai,
                user_byte=week_index + 10,
                block_number=start + 1,
                log_index=1,
            ),
        ]
        windows.append(
            {
                "start_block": start,
                "end_block_exclusive": start + 100,
                "logs": logs,
            }
        )

    summary = summarize_preperiod_activity(
        windows,
        pool_address=pool,
        assets={"DAI": dai},
        borrow_topic=borrow_topic,
        repay_topic=repay_topic,
        minimum_weekly_borrow_events=1,
        minimum_weekly_repay_events=1,
        minimum_weekly_unique_debt_users=2,
        minimum_total_actions=4,
        minimum_total_unique_debt_users=4,
    )
    encoded = json.dumps(summary)
    assert summary["DAI"]["total_combined_actions"] == 4
    assert summary["DAI"]["total_unique_debt_users"] == 4
    assert summary["DAI"]["activity_eligible"] is True
    for forbidden in (
        "SECRET_AMOUNT",
        "5345435245545f414d4f554e54",
        f"{100:064x}",
        f"{100 * 100:064x}",
        "0x" + "00" * 31 + "01",
    ):
        assert forbidden not in encoded


def test_preperiod_activity_reducer_rejects_duplicate_logs() -> None:
    pool = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    dai = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    borrow_topic = "0x" + "ab" * 32
    repay_topic = "0x" + "cd" * 32
    log = _activity_log(
        pool=pool,
        event_topic=borrow_topic,
        asset=dai,
        user_byte=1,
        block_number=100,
        log_index=0,
    )
    try:
        summarize_preperiod_activity(
            [{"start_block": 100, "end_block_exclusive": 200, "logs": [log, log]}],
            pool_address=pool,
            assets={"DAI": dai},
            borrow_topic=borrow_topic,
            repay_topic=repay_topic,
            minimum_weekly_borrow_events=0,
            minimum_weekly_repay_events=0,
            minimum_weekly_unique_debt_users=0,
            minimum_total_actions=0,
            minimum_total_unique_debt_users=0,
        )
    except ValueError as error:
        assert "duplicate log" in str(error)
    else:
        raise AssertionError("duplicate logs must fail the formal reducer")
