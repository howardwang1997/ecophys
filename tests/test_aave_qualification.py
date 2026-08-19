from __future__ import annotations

from ecomd.data.aave_qualification import (
    address_topic,
    audit_asset_rate_change,
    extract_implementation_reference,
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
