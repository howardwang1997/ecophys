from copy import deepcopy
from itertools import pairwise
from pathlib import Path

import pytest

from ecomd.research.aave_lt_event_directory import (
    CONFIGURATOR,
    CONFIGURATOR_ID,
    EVENT_CONTRACT,
    POOL,
    POOL_ID,
    PROVIDER,
    _collect_log_stream,
    _component_history,
    deduplicate_logs,
    load_directory_manifest,
    normalize_directory_log,
    provisional_directory_candidates,
    root_intervals,
    split_inclusive_interval,
    validate_directory_manifest,
    validate_parent_artifacts,
)

MANIFEST_PATH = Path("data/manifests/aave_v3_ethereum_lt_event_directory_v1.yaml")
ASSET = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
IMPLEMENTATION_1 = "0x1111111111111111111111111111111111111111"
IMPLEMENTATION_2 = "0x2222222222222222222222222222222222222222"
BLOCK_HASH = "0x" + "aa" * 32


def _topic_address(address: str) -> str:
    return "0x" + "00" * 12 + address[2:]


def _words(*values: int | str) -> str:
    encoded: list[str] = []
    for value in values:
        if isinstance(value, int):
            encoded.append(value.to_bytes(32, "big").hex())
        else:
            encoded.append("00" * 12 + value[2:])
    return "0x" + "".join(encoded)


def _raw_log(
    *,
    address: str,
    topics: list[str],
    data: str = "0x",
    block_number: int = 17_000_000,
    transaction_number: int = 1,
    log_index: int = 0,
) -> dict[str, object]:
    return {
        "address": address,
        "topics": topics,
        "data": data,
        "blockNumber": hex(block_number),
        "blockHash": BLOCK_HASH,
        "transactionHash": "0x" + f"{transaction_number:064x}",
        "transactionIndex": "0x0",
        "logIndex": hex(log_index),
        "removed": False,
    }


def _normalize(raw: dict[str, object], *, address: str, role: str) -> dict[str, object]:
    return normalize_directory_log(
        raw,
        expected_address=address,
        role=role,
        from_block=0,
        to_block=25_760_572,
    )


def _collateral(
    *,
    ltv: int,
    threshold: int,
    bonus: int,
    block_number: int,
    transaction_number: int,
    log_index: int = 0,
) -> dict[str, object]:
    return _normalize(
        _raw_log(
            address=CONFIGURATOR,
            topics=[EVENT_CONTRACT["collateral_configuration_changed"]["topic0"], _topic_address(ASSET)],
            data=_words(ltv, threshold, bonus),
            block_number=block_number,
            transaction_number=transaction_number,
            log_index=log_index,
        ),
        address=CONFIGURATOR,
        role="configurator",
    )


def test_manifest_parent_hashes_and_exact_root_partition_are_valid() -> None:
    manifest = load_directory_manifest(MANIFEST_PATH)

    assert validate_directory_manifest(manifest) == []
    assert validate_parent_artifacts(manifest, Path.cwd()) == []
    intervals = root_intervals(0, 25_760_572, 250_000)
    assert len(intervals) == 104
    assert intervals[0] == (0, 249_999)
    assert intervals[-1] == (25_750_000, 25_760_572)
    assert all(right[0] == left[1] + 1 for left, right in pairwise(intervals))
    assert split_inclusive_interval(10, 14) == ((10, 12), (13, 14))


def test_strictly_decodes_collateral_provider_and_upgrade_events() -> None:
    collateral = _collateral(
        ltv=7_500,
        threshold=8_000,
        bonus=10_500,
        block_number=17_000_000,
        transaction_number=1,
    )
    created = _normalize(
        _raw_log(
            address=PROVIDER,
            topics=[
                EVENT_CONTRACT["proxy_created"]["topic0"],
                POOL_ID,
                _topic_address(POOL),
                _topic_address(IMPLEMENTATION_1),
            ],
            transaction_number=2,
        ),
        address=PROVIDER,
        role="provider",
    )
    updated = _normalize(
        _raw_log(
            address=PROVIDER,
            topics=[
                EVENT_CONTRACT["pool_updated"]["topic0"],
                _topic_address("0x" + "0" * 40),
                _topic_address(IMPLEMENTATION_1),
            ],
            transaction_number=2,
            log_index=2,
        ),
        address=PROVIDER,
        role="provider",
    )
    upgraded = _normalize(
        _raw_log(
            address=POOL,
            topics=[EVENT_CONTRACT["upgraded"]["topic0"], _topic_address(IMPLEMENTATION_1)],
            transaction_number=2,
            log_index=1,
        ),
        address=POOL,
        role="pool",
    )

    assert collateral["asset"] == ASSET
    assert collateral["liquidation_threshold"] == 8_000
    assert created["id"] == POOL_ID
    assert created["proxy"] == POOL
    assert updated["old_address"] == "0x" + "0" * 40
    assert upgraded["implementation"] == IMPLEMENTATION_1


def test_address_set_as_proxy_decodes_nonindexed_old_implementation() -> None:
    row = _normalize(
        _raw_log(
            address=PROVIDER,
            topics=[
                EVENT_CONTRACT["address_set_as_proxy"]["topic0"],
                CONFIGURATOR_ID,
                _topic_address(CONFIGURATOR),
                _topic_address(IMPLEMENTATION_2),
            ],
            data=_words(IMPLEMENTATION_1),
            transaction_number=3,
        ),
        address=PROVIDER,
        role="provider",
    )

    assert row["old_implementation"] == IMPLEMENTATION_1
    assert row["new_implementation"] == IMPLEMENTATION_2


def test_decoder_rejects_malformed_known_event_shapes() -> None:
    malformed_collateral = _raw_log(
        address=CONFIGURATOR,
        topics=[EVENT_CONTRACT["collateral_configuration_changed"]["topic0"], _topic_address(ASSET)],
        data=_words(7_500, 8_000),
    )
    malformed_upgrade = _raw_log(
        address=POOL,
        topics=[EVENT_CONTRACT["upgraded"]["topic0"], _topic_address(IMPLEMENTATION_1)],
        data=_words(1),
    )

    with pytest.raises(ValueError, match="exactly 3 ABI words"):
        _normalize(malformed_collateral, address=CONFIGURATOR, role="configurator")
    with pytest.raises(ValueError, match="canonical Upgraded"):
        _normalize(malformed_upgrade, address=POOL, role="pool")


def test_candidate_requires_lt_only_decrease_and_transaction_isolation() -> None:
    baseline = _collateral(
        ltv=7_500,
        threshold=8_000,
        bonus=10_500,
        block_number=17_000_000,
        transaction_number=1,
    )
    clean = _collateral(
        ltv=7_500,
        threshold=7_800,
        bonus=10_500,
        block_number=18_000_000,
        transaction_number=2,
    )

    candidates = provisional_directory_candidates([baseline, clean])

    assert candidates[0]["provisional_directory_candidate"] is False
    assert candidates[1]["provisional_directory_candidate"] is True
    changed_ltv = _collateral(
        ltv=7_300,
        threshold=7_600,
        bonus=10_500,
        block_number=19_000_000,
        transaction_number=3,
    )
    ltv_candidates = provisional_directory_candidates([baseline, changed_ltv])
    assert ltv_candidates[1]["checks"]["emitted_ltv_unchanged"] is False
    other = _normalize(
        _raw_log(
            address=CONFIGURATOR,
            topics=["0x" + "99" * 32],
            block_number=18_000_000,
            transaction_number=2,
            log_index=5,
        ),
        address=CONFIGURATOR,
        role="configurator",
    )
    bundled = provisional_directory_candidates([baseline, clean, other])
    assert bundled[1]["checks"]["exactly_one_configurator_log_in_transaction"] is False


def test_component_history_requires_continuous_one_to_one_crosswalk() -> None:
    created = _normalize(
        _raw_log(
            address=PROVIDER,
            topics=[
                EVENT_CONTRACT["proxy_created"]["topic0"],
                POOL_ID,
                _topic_address(POOL),
                _topic_address(IMPLEMENTATION_1),
            ],
            transaction_number=1,
            log_index=1,
        ),
        address=PROVIDER,
        role="provider",
    )
    provider_updated = _normalize(
        _raw_log(
            address=PROVIDER,
            topics=[
                EVENT_CONTRACT["pool_updated"]["topic0"],
                _topic_address("0x" + "0" * 40),
                _topic_address(IMPLEMENTATION_1),
            ],
            transaction_number=1,
            log_index=2,
        ),
        address=PROVIDER,
        role="provider",
    )
    proxy_upgraded = _normalize(
        _raw_log(
            address=POOL,
            topics=[EVENT_CONTRACT["upgraded"]["topic0"], _topic_address(IMPLEMENTATION_1)],
            transaction_number=1,
            log_index=0,
        ),
        address=POOL,
        role="pool",
    )

    passing = _component_history(
        [created, provider_updated, proxy_upgraded],
        component="pool",
        component_id=POOL_ID,
        proxy=POOL,
        terminal_implementation=IMPLEMENTATION_1,
    )
    missing_upgrade = _component_history(
        [created, provider_updated],
        component="pool",
        component_id=POOL_ID,
        proxy=POOL,
        terminal_implementation=IMPLEMENTATION_1,
    )

    assert passing["passed"] is True
    assert missing_upgrade["passed"] is False
    assert missing_upgrade["checks"]["one_to_one_provider_transition_and_proxy_upgrade"] is False


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
            if interval == (10, 14):
                return [{"discarded": True}, {"discarded": True}]
            return [
                _raw_log(
                    address=POOL,
                    topics=[EVENT_CONTRACT["upgraded"]["topic0"], _topic_address(IMPLEMENTATION_1)],
                    block_number=interval[0],
                    log_index=len(self.intervals),
                )
            ]

    rpc = FakeRpc()
    records, query_count, saturated_count = _collect_log_stream(
        rpc,  # type: ignore[arg-type]
        url="https://example.invalid",
        address=POOL,
        role="pool",
        intervals=[(10, 14)],
        topic0=EVENT_CONTRACT["upgraded"]["topic0"],
        response_limit=2,
        maximum_normalized_logs=10,
    )

    assert rpc.intervals == [(10, 14), (10, 12), (13, 14)]
    assert query_count == 3
    assert saturated_count == 1
    assert len(records) == 2


def test_duplicate_and_conflicting_log_identities_are_counted() -> None:
    row = _collateral(
        ltv=7_500,
        threshold=8_000,
        bonus=10_500,
        block_number=17_000_000,
        transaction_number=1,
    )
    conflict = dict(row)
    conflict["liquidation_threshold"] = 7_999

    exact, duplicates, conflicts = deduplicate_logs([row, row])
    _, _, conflicting = deduplicate_logs([row, conflict])

    assert len(exact) == 1
    assert duplicates == 1
    assert conflicts == 0
    assert conflicting == 1


def test_validator_rejects_access_source_and_decision_relaxation() -> None:
    manifest = load_directory_manifest(MANIFEST_PATH)
    broken = deepcopy(manifest)
    access = broken["access_boundary"]
    source = broken["source_identity"]
    policy = broken["decision_policy"]
    assert isinstance(access, dict)
    assert isinstance(source, dict)
    assert isinstance(policy, dict)
    access["account_state_rows_opened"] = True
    source["aave_v3_origin_commit"] = "0" * 40
    policy["pass"] = "PASS_ANYTHING"

    errors = validate_directory_manifest(broken)

    assert "account_state_rows_opened must be false" in errors
    assert "source_identity differs from the frozen contract" in errors
    assert "decision_policy differs from the frozen contract" in errors
