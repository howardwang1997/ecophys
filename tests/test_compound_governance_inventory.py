from copy import deepcopy
from itertools import pairwise
from pathlib import Path

import pytest

from ecomd.research.compound_governance_inventory import (
    CONFIGURATOR,
    EVENT_CONTRACT,
    _collect_address_logs,
    load_governance_inventory,
    normalize_governance_log,
    provisional_candidates,
    root_intervals,
    split_inclusive_interval,
    validate_governance_inventory,
    validate_parent_artifacts,
)

MANIFEST_PATH = Path("data/manifests/compound_v3_governance_log_inventory_v1.yaml")
PROXY = "0xc3d688b66703497daa19211eedff47f25384cdc3"
OTHER_PROXY = "0x5d409e56d886231adaf00c8775665ad0f9897b56"
ASSET = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
IMPLEMENTATION = "0x1111111111111111111111111111111111111111"
TX_HASH = "0x" + "bb" * 32


def _topic_address(address: str) -> str:
    return "0x" + "00" * 12 + address[2:]


def _words(*values: int) -> str:
    return "0x" + "".join(value.to_bytes(32, "big").hex() for value in values)


def _raw_log(
    *,
    address: str,
    topics: list[str],
    data: str = "0x",
    transaction_hash: str = TX_HASH,
    log_index: int,
    block_number: int = 14_000_000,
) -> dict[str, object]:
    return {
        "address": address,
        "topics": topics,
        "data": data,
        "blockNumber": hex(block_number),
        "blockHash": "0x" + "aa" * 32,
        "transactionHash": transaction_hash,
        "transactionIndex": "0x0",
        "logIndex": hex(log_index),
        "removed": False,
    }


def _normalize(
    raw: dict[str, object],
    *,
    expected_address: str,
    market_id: str | None,
) -> dict[str, object]:
    return normalize_governance_log(
        raw,
        expected_address=expected_address,
        market_id=market_id,
        from_block=14_000_000,
        to_block=14_249_999,
    )


def _candidate_triplet() -> list[dict[str, object]]:
    eligible = _normalize(
        _raw_log(
            address=CONFIGURATOR,
            topics=[
                str(EVENT_CONTRACT["update_asset_borrow_collateral_factor"]["topic0"]),
                _topic_address(PROXY),
                _topic_address(ASSET),
            ],
            data=_words(800_000_000_000_000_000, 750_000_000_000_000_000),
            log_index=4,
        ),
        expected_address=CONFIGURATOR,
        market_id=None,
    )
    deployed = _normalize(
        _raw_log(
            address=CONFIGURATOR,
            topics=[
                str(EVENT_CONTRACT["comet_deployed"]["topic0"]),
                _topic_address(PROXY),
                _topic_address(IMPLEMENTATION),
            ],
            log_index=8,
        ),
        expected_address=CONFIGURATOR,
        market_id=None,
    )
    upgraded = _normalize(
        _raw_log(
            address=PROXY,
            topics=[
                str(EVENT_CONTRACT["upgraded"]["topic0"]),
                _topic_address(IMPLEMENTATION),
            ],
            log_index=9,
        ),
        expected_address=PROXY,
        market_id="mainnet_usdc",
    )
    return [eligible, deployed, upgraded]


def test_canonical_inventory_and_parent_hashes_are_valid() -> None:
    manifest = load_governance_inventory(MANIFEST_PATH)

    assert validate_governance_inventory(manifest) == []
    assert validate_parent_artifacts(manifest, Path.cwd()) == []


def test_root_partition_and_recursive_split_are_exact() -> None:
    intervals = root_intervals(14_000_000, 25_760_572, 250_000)

    assert len(intervals) == 48
    assert intervals[0] == (14_000_000, 14_249_999)
    assert intervals[-1] == (25_750_000, 25_760_572)
    assert all(right[0] == left[1] + 1 for left, right in pairwise(intervals))
    assert split_inclusive_interval(10, 11) == ((10, 10), (11, 11))
    assert split_inclusive_interval(10, 14) == ((10, 12), (13, 14))


def test_saturated_parent_is_discarded_and_bisected() -> None:
    class FakeRpc:
        def __init__(self) -> None:
            self.intervals: list[tuple[int, int]] = []

        def call(self, **kwargs: object) -> object:
            params = kwargs["params"]
            assert isinstance(params, list)
            log_filter = params[0]
            assert isinstance(log_filter, dict)
            interval = (int(log_filter["fromBlock"], 16), int(log_filter["toBlock"], 16))
            self.intervals.append(interval)
            if interval == (14_000_000, 14_000_004):
                return [{"discarded": True}, {"discarded": True}]
            block_number = interval[0]
            return [
                _raw_log(
                    address=PROXY,
                    topics=[
                        str(EVENT_CONTRACT["upgraded"]["topic0"]),
                        _topic_address(IMPLEMENTATION),
                    ],
                    log_index=len(self.intervals),
                    block_number=block_number,
                )
            ]

    rpc = FakeRpc()
    records, query_count, saturated_count = _collect_address_logs(
        rpc,  # type: ignore[arg-type]
        url="https://example.invalid",
        address=PROXY,
        market_id="mainnet_usdc",
        intervals=[(14_000_000, 14_000_004)],
        topic0=str(EVENT_CONTRACT["upgraded"]["topic0"]),
        response_limit=2,
        maximum_normalized_logs=10,
    )

    assert rpc.intervals == [
        (14_000_000, 14_000_004),
        (14_000_000, 14_000_002),
        (14_000_003, 14_000_004),
    ]
    assert query_count == 3
    assert saturated_count == 1
    assert [record["block_number"] for record in records] == [14_000_000, 14_000_003]


def test_saturated_single_block_fails() -> None:
    class FakeRpc:
        def call(self, **kwargs: object) -> object:
            return [{"discarded": True}, {"discarded": True}]

    with pytest.raises(RuntimeError, match="single-block"):
        _collect_address_logs(
            FakeRpc(),  # type: ignore[arg-type]
            url="https://example.invalid",
            address=PROXY,
            market_id="mainnet_usdc",
            intervals=[(14_000_000, 14_000_000)],
            topic0=str(EVENT_CONTRACT["upgraded"]["topic0"]),
            response_limit=2,
            maximum_normalized_logs=10,
        )


def test_strict_decoding_of_eligible_deployment_and_upgrade_logs() -> None:
    eligible, deployed, upgraded = _candidate_triplet()

    assert eligible["event_type"] == "update_asset_borrow_collateral_factor"
    assert eligible["comet_proxy"] == PROXY
    assert eligible["asset"] == ASSET
    assert eligible["old_value"] == 800_000_000_000_000_000
    assert eligible["new_value"] == 750_000_000_000_000_000
    assert deployed["event_type"] == "comet_deployed"
    assert deployed["implementation"] == IMPLEMENTATION
    assert upgraded["event_type"] == "upgraded"
    assert upgraded["implementation"] == IMPLEMENTATION


def test_decoder_rejects_abi_width_and_proxy_shape_relaxations() -> None:
    overflow = _raw_log(
        address=CONFIGURATOR,
        topics=[
            str(EVENT_CONTRACT["update_asset_borrow_collateral_factor"]["topic0"]),
            _topic_address(PROXY),
            _topic_address(ASSET),
        ],
        data=_words(2**64, 1),
        log_index=1,
    )
    malformed_upgrade = _raw_log(
        address=PROXY,
        topics=[str(EVENT_CONTRACT["upgraded"]["topic0"]), _topic_address(IMPLEMENTATION)],
        data=_words(1),
        log_index=2,
    )

    with pytest.raises(ValueError, match="declared ABI width"):
        _normalize(overflow, expected_address=CONFIGURATOR, market_id=None)
    with pytest.raises(ValueError, match="canonical Upgraded"):
        _normalize(malformed_upgrade, expected_address=PROXY, market_id="mainnet_usdc")


def test_provisional_candidate_requires_the_exact_atomic_log_set() -> None:
    records = _candidate_triplet()

    clean = provisional_candidates(records)

    assert len(clean) == 1
    assert clean[0]["provisional_atomic_candidate"] is True
    assert all(clean[0]["checks"].values())

    extra_configurator = _normalize(
        _raw_log(
            address=CONFIGURATOR,
            topics=["0x" + "99" * 32],
            log_index=10,
        ),
        expected_address=CONFIGURATOR,
        market_id=None,
    )
    with_spillover = provisional_candidates([*records, extra_configurator])

    assert with_spillover[0]["provisional_atomic_candidate"] is False
    assert with_spillover[0]["checks"]["no_other_configurator_state_change"] is False

    second_upgrade = _normalize(
        _raw_log(
            address=OTHER_PROXY,
            topics=[str(EVENT_CONTRACT["upgraded"]["topic0"]), _topic_address(IMPLEMENTATION)],
            log_index=11,
        ),
        expected_address=OTHER_PROXY,
        market_id="mainnet_usds",
    )
    with_other_market = provisional_candidates([*records, second_upgrade])

    assert with_other_market[0]["provisional_atomic_candidate"] is False
    assert with_other_market[0]["checks"]["no_other_frozen_market_upgrade"] is False


def test_access_boundary_rejects_payload_account_and_gpu_access() -> None:
    manifest = load_governance_inventory(MANIFEST_PATH)
    broken = deepcopy(manifest)
    access = broken["access_boundary"]
    assert isinstance(access, dict)
    access["governance_payload_rows_opened"] = True
    access["account_state_rows_opened"] = True
    access["gpu_used"] = True

    errors = validate_governance_inventory(broken)

    assert any("governance_payload_rows_opened must be false" in error for error in errors)
    assert any("account_state_rows_opened must be false" in error for error in errors)
    assert any("gpu_used must be false" in error for error in errors)


def test_validator_rejects_parent_market_and_decision_substitution() -> None:
    manifest = load_governance_inventory(MANIFEST_PATH)
    broken = deepcopy(manifest)
    parents = broken["parents"]
    markets = broken["markets"]
    policy = broken["decision_policy"]
    assert isinstance(parents, dict)
    assert isinstance(markets, list)
    assert isinstance(markets[0], dict)
    assert isinstance(policy, dict)
    parents["exposure_design_sha256"] = "0" * 64
    markets[0]["proxy"] = "0x2222222222222222222222222222222222222222"
    policy["pass"] = "PASS_ANYTHING"

    errors = validate_governance_inventory(broken)

    assert "parents differ from the frozen artifact contract" in errors
    assert "markets differ from the frozen ordered market set" in errors
    assert "decision_policy differs from the frozen contract" in errors
