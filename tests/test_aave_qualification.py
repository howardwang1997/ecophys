from __future__ import annotations

import json

from ecomd.data.aave_qualification import (
    address_topic,
    assess_clean_panel,
    audit_asset_rate_change,
    canonical_sha256,
    classify_clean_policy_windows,
    extract_implementation_reference,
    extract_rate_strategy_updates,
    extract_solidity_event_definitions,
    reduce_policy_logs,
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


def test_solidity_event_extraction_canonicalizes_multiline_abi() -> None:
    source = """
    // event Fake(address indexed ignored);
    event ReserveInitialized(
      address indexed asset,
      address indexed aToken,
      address variableDebtToken
    );
    event EModeCategoryAdded(uint8 indexed categoryId, uint ltv, string label);
    /* event Hidden(bytes32 value); */
    """
    definitions = extract_solidity_event_definitions(source)
    assert set(definitions) == {
        "ReserveInitialized(address,address,address)",
        "EModeCategoryAdded(uint8,uint256,string)",
    }
    assert definitions["ReserveInitialized(address,address,address)"][
        "indexed_positions"
    ] == [0, 1]


def test_rate_strategy_parser_supports_legacy_and_origin_forms() -> None:
    source = """
    rateStrategies[0] = IAaveV3ConfigEngine.RateStrategyUpdate({
      asset: AaveV3ArbitrumAssets.USDCn_UNDERLYING,
      params: IV3RateStrategyFactory.RateStrategyParams({
        optimalUsageRatio: EngineFlags.KEEP_CURRENT,
        variableRateSlope1: _bpsToRay(9_00),
        variableRateSlope2: EngineFlags.KEEP_CURRENT
      })
    });
    rateStrategies[1] = IAaveV3ConfigEngine.RateStrategyUpdate({
      asset: AaveV3ArbitrumAssets.DAI_UNDERLYING,
      params: IAaveV3ConfigEngine.InterestRateInputData({
        optimalUsageRatio: EngineFlags.KEEP_CURRENT,
        baseVariableBorrowRate: EngineFlags.KEEP_CURRENT,
        variableRateSlope1: 6_50,
        variableRateSlope2: EngineFlags.KEEP_CURRENT
      })
    });
    """
    assert extract_rate_strategy_updates(source) == [
        {
            "asset_alias": "USDCn",
            "configured_change_fields": ["variableRateSlope1"],
            "variable_rate_slope1_bps": 900,
            "slope1_only": True,
        },
        {
            "asset_alias": "DAI",
            "configured_change_fields": ["variableRateSlope1"],
            "variable_rate_slope1_bps": 650,
            "slope1_only": True,
        },
    ]


def test_rate_strategy_parser_marks_bundled_change_noncomparable() -> None:
    source = """
    IAaveV3ConfigEngine.RateStrategyUpdate({
      asset: AaveV3BaseAssets.USDC_UNDERLYING,
      params: IAaveV3ConfigEngine.InterestRateInputData({
        optimalUsageRatio: 90_00,
        variableRateSlope1: 6_50
      })
    });
    """
    update = extract_rate_strategy_updates(source)[0]
    assert update["configured_change_fields"] == [
        "optimalUsageRatio",
        "variableRateSlope1",
    ]
    assert update["slope1_only"] is False


def _policy_log(
    *,
    address: str,
    topic0: str,
    topic1: str | None,
    data: str,
    block_number: int,
    transaction_byte: int,
    log_index: int,
) -> dict[str, object]:
    topics = [topic0]
    if topic1 is not None:
        topics.append(topic1)
    return {
        "address": address,
        "topics": topics,
        "data": data,
        "blockNumber": hex(block_number),
        "blockHash": "0x" + f"{block_number:064x}",
        "transactionHash": "0x" + f"{transaction_byte:064x}",
        "logIndex": hex(log_index),
        "removed": False,
    }


def test_policy_reducer_decodes_scopes_but_drops_raw_values() -> None:
    configurator = "0x64b761D848206f447Fe2dd461b0c635Ec39EbB27"
    rewards = "0x8164Cc65827dcFe994AB23944CBC90e0aa80bFcb"
    dai = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    dai_a_token = "0x018008bfb33d285247A21d44E50697654f754e63"
    rate_topic = "0x" + "11" * 32
    isolation_topic = "0x" + "22" * 32
    reward_topic = "0x" + "33" * 32
    secret_word = "5345435245545f504f4c494359"
    logs = [
        _policy_log(
            address=configurator,
            topic0=rate_topic,
            topic1=address_topic(dai),
            data="0x" + secret_word.ljust(64, "0"),
            block_number=100,
            transaction_byte=1,
            log_index=0,
        ),
        _policy_log(
            address=configurator,
            topic0=isolation_topic,
            topic1=None,
            data="0x" + address_topic(dai)[2:] + "0" * 64,
            block_number=101,
            transaction_byte=2,
            log_index=0,
        ),
        _policy_log(
            address=rewards,
            topic0=reward_topic,
            topic1=address_topic(dai_a_token),
            data="0x" + secret_word.ljust(64, "f"),
            block_number=102,
            transaction_byte=3,
            log_index=0,
        ),
    ]
    reduced = reduce_policy_logs(
        logs,
        contract_addresses={
            "pool_configurator": configurator,
            "rewards": rewards,
        },
        topic_definitions={
            rate_topic: {
                "signature": "ReserveInterestRateStrategyChanged(address,address,address)",
                "name": "ReserveInterestRateStrategyChanged",
                "contract_group": "pool_configurator",
                "scope_rule": "asset_topic",
            },
            isolation_topic: {
                "signature": "BorrowableInIsolationChanged(address,bool)",
                "name": "BorrowableInIsolationChanged",
                "contract_group": "pool_configurator",
                "scope_rule": "asset_data_word_zero",
            },
            reward_topic: {
                "signature": "AssetConfigUpdated(address,address,uint256,uint256,uint256,uint256,uint256)",
                "name": "AssetConfigUpdated",
                "contract_group": "rewards",
                "scope_rule": "reward_asset_topic",
            },
        },
        selected_assets={"DAI": dai},
        selected_tokens={"DAI": [dai_a_token]},
        start_block=100,
        end_block_inclusive=102,
        block_timestamps={100: 1_000, 101: 1_001, 102: 1_002},
    )
    assert [row["symbol"] for row in reduced] == ["DAI", "DAI", "DAI"]
    assert all(row["scope"] == "selected_asset" for row in reduced)
    encoded = json.dumps(reduced)
    assert secret_word not in encoded
    assert dai.lower() not in encoded.lower()
    assert dai_a_token.lower() not in encoded.lower()


def test_clean_window_classifier_applies_failure_and_late_censoring() -> None:
    transaction = "0x" + "aa" * 32
    base_event = {
        "event_signature": "ReserveInterestRateStrategyChanged(address,address,address)",
        "event_name": "ReserveInterestRateStrategyChanged",
        "contract_group": "pool_configurator",
        "scope": "selected_asset",
        "symbol": "DAI",
        "block_number": 100,
        "block_timestamp": 1_000_000,
        "transaction_hash": transaction,
        "policy_data_sha256": "a" * 64,
    }
    late_event = {
        **base_event,
        "event_name": "BorrowCapChanged",
        "event_signature": "BorrowCapChanged(address,uint256,uint256)",
        "block_number": 200,
        "block_timestamp": 1_000_000 + 15 * 86_400,
        "transaction_hash": "0x" + "bb" * 32,
    }
    global_contaminant = {
        **base_event,
        "event_name": "PriceOracleUpdated",
        "event_signature": "PriceOracleUpdated(address,address)",
        "contract_group": "addresses_provider",
        "scope": "global",
        "symbol": None,
        "block_number": 90,
        "block_timestamp": 1_000_000 - 86_400,
        "transaction_hash": "0x" + "cc" * 32,
    }
    units = [
        {
            "proposal_id": 1,
            "symbol": "DAI",
            "cohort": "primary_rate_decrease",
            "execution_block": 100,
            "execution_timestamp": 1_000_000,
            "execution_transaction_hash": transaction,
        }
    ]
    censored = classify_clean_policy_windows(
        [base_event, late_event],
        units,
        exclusion_pre_seconds=14 * 86_400,
        minimum_clean_post_seconds=14 * 86_400,
        target_post_seconds=28 * 86_400,
    )[0]
    assert censored["clean_window_eligible"] is True
    assert censored["administrative_censor_event"]["event_name"] == "BorrowCapChanged"
    assert censored["clean_followup_seconds"] == 15 * 86_400

    failed = classify_clean_policy_windows(
        [base_event, global_contaminant],
        units,
        exclusion_pre_seconds=14 * 86_400,
        minimum_clean_post_seconds=14 * 86_400,
        target_post_seconds=28 * 86_400,
    )[0]
    assert failed["clean_window_eligible"] is False
    assert failed["contaminating_event_count"] == 1


def test_clean_panel_has_no_amber_fallback() -> None:
    units = [
        {
            "proposal_id": 3,
            "cohort": "reverse_sign",
            "clean_window_eligible": symbol != "USDT",
        }
        for symbol in ("DAI", "USDC", "USDT")
    ]
    panel = assess_clean_panel(
        units,
        minimum_total=3,
        minimum_primary=0,
        minimum_reverse=2,
        minimum_assets_per_proposal=2,
    )
    assert panel["eligible_unit_count"] == 2
    assert panel["decision_checks"]["minimum_reverse_sign_clean_units"] is True
    assert panel["passed"] is False
