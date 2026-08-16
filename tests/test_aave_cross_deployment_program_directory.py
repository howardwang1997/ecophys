from copy import deepcopy
from pathlib import Path
from typing import cast

import pytest

from ecomd.research.aave_cross_deployment_program_directory import (
    CONFIGURATOR_ID,
    EXPECTED_SUPPORT_THRESHOLDS,
    RpcCallError,
    RpcCollector,
    build_program_records,
    collect_deployment_directory,
    collect_log_stream,
    deduplicate_program_logs,
    derive_configurator_surfaces,
    load_program_manifest,
    normalize_program_log,
    resolve_replicated_cutoff,
    source_corrected_configurator_history,
    summarize_support,
    validate_parent_artifacts,
    validate_program_manifest,
)

MANIFEST_PATH = Path("data/manifests/aave_v3_cross_deployment_program_directory_v1.yaml")
PROVIDER = "0x" + "11" * 20
CONFIGURATOR = "0x" + "22" * 20
IMPLEMENTATION_1 = "0x" + "33" * 20
IMPLEMENTATION_2 = "0x" + "44" * 20
BLOCK_HASH = "0x" + "aa" * 32


class FakeRpc(RpcCollector):
    def __init__(self, handler: object) -> None:
        self.handler = handler
        self.records: list[dict[str, object]] = []
        self.failed_calls: list[dict[str, object]] = []
        self.http_attempts = 0
        self.response_bytes = 0

    def call(
        self,
        *,
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: object,
    ) -> object:
        self.http_attempts += 1
        callable_handler = cast(object, self.handler)
        if not callable(callable_handler):
            raise TypeError("handler must be callable")
        return callable_handler(url, deployment, provider, label, method, params)


def _header(number: int, timestamp: int) -> dict[str, object]:
    return {
        "number": hex(number),
        "hash": "0x" + f"{number + 1:064x}",
        "parentHash": "0x" + f"{number:064x}",
        "timestamp": hex(timestamp),
        "transactions": [],
    }


def _raw_log(
    *,
    address: str = CONFIGURATOR,
    block_number: int = 1,
    transaction_number: int = 1,
    log_index: int = 0,
    topics: list[str] | None = None,
    data: str = "0x",
    block_hash: str = BLOCK_HASH,
) -> dict[str, object]:
    return {
        "address": address,
        "blockNumber": hex(block_number),
        "blockHash": block_hash,
        "transactionHash": "0x" + f"{transaction_number:064x}",
        "transactionIndex": "0x0",
        "logIndex": hex(log_index),
        "topics": topics or ["0x" + "99" * 32],
        "data": data,
        "removed": False,
    }


def _topic_address(address: str) -> str:
    return "0x" + "00" * 12 + address[2:]


def test_manifest_and_immutable_parents_are_valid() -> None:
    manifest = load_program_manifest(MANIFEST_PATH)

    assert validate_program_manifest(manifest) == []
    assert validate_parent_artifacts(manifest, Path.cwd()) == []

    mutated = deepcopy(manifest)
    cast(dict[str, object], mutated["support_thresholds"])["minimum_total_non_development_programs"] = 219
    assert "support thresholds differ from the frozen OOD contract" in validate_program_manifest(mutated)

    missing_rule = deepcopy(manifest)
    del cast(dict[str, object], missing_rule["program_inclusion_rule"])[
        "no_parameter_type_direction_or_scalar_purity_filter"
    ]
    assert "program inclusion rule differs from the frozen contract" in validate_program_manifest(
        missing_rule
    )

    changed_pool = deepcopy(manifest)
    cast(list[dict[str, object]], changed_pool["deployments"])[1]["pool"] = "0x" + "ff" * 20
    assert "deployments.arbitrum.pool differs from the frozen value" in validate_program_manifest(
        changed_pool
    )


def test_duplicate_yaml_keys_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.yaml"
    path.write_text("key: one\nkey: two\n", encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate YAML key"):
        load_program_manifest(path)


def test_replicated_cutoff_uses_largest_block_at_or_before_timestamp() -> None:
    def handler(
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: object,
    ) -> object:
        del url, deployment, provider, label
        if method == "eth_chainId":
            return "0x2a"
        if method == "eth_blockNumber":
            return "0x14"
        assert isinstance(params, list)
        number = int(cast(str, params[0]), 16)
        return _header(number, number * 10)

    deployment: dict[str, object] = {
        "name": "synthetic",
        "chain_id_hex": "0x2a",
        "primary_rpc_url": "https://primary.invalid",
        "replica_rpc_url": "https://replica.invalid",
    }

    result = resolve_replicated_cutoff(FakeRpc(handler), deployment, cutoff_timestamp=95)

    assert result["replicated"] is True
    assert cast(dict[str, object], cast(dict[str, object], result["primary"])["cutoff_header"])["number"] == 9
    assert cast(dict[str, object], cast(dict[str, object], result["primary"])["next_header"])["number"] == 10


def test_log_stream_discards_saturated_parent_and_bisects() -> None:
    def handler(
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: object,
    ) -> object:
        del url, deployment, provider, label, method
        assert isinstance(params, list)
        query = cast(dict[str, str], params[0])
        start = int(query["fromBlock"], 16)
        end = int(query["toBlock"], 16)
        if (start, end) == (0, 3):
            return [
                _raw_log(block_number=0, transaction_number=90),
                _raw_log(block_number=3, transaction_number=91),
            ]
        if (start, end) == (0, 1):
            return [_raw_log(block_number=1, transaction_number=1)]
        return [_raw_log(block_number=2, transaction_number=2)]

    records, queries = collect_log_stream(
        FakeRpc(handler),
        deployment="synthetic",
        chain_id=42,
        url="https://primary.invalid",
        address=CONFIGURATOR,
        role="configurator",
        intervals=[(0, 3)],
        response_limit=2,
        maximum_normalized_logs=10,
    )

    assert [item["block_number"] for item in records] == [1, 2]
    assert queries == {
        "root_interval_count": 1,
        "query_count": 3,
        "saturated_split_count": 1,
        "rpc_error_split_count": 0,
        "preemptive_split_count": 0,
        "maximum_split_depth": 1,
        "learned_maximum_interval_span": 0,
    }


def test_log_stream_bisects_rpc_range_error_but_fails_single_block() -> None:
    def passing_handler(
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: object,
    ) -> object:
        del url, deployment, provider, label, method
        assert isinstance(params, list)
        query = cast(dict[str, str], params[0])
        start = int(query["fromBlock"], 16)
        end = int(query["toBlock"], 16)
        if (start, end) == (0, 1):
            raise RpcCallError("range too wide")
        return []

    records, queries = collect_log_stream(
        FakeRpc(passing_handler),
        deployment="synthetic",
        chain_id=42,
        url="https://primary.invalid",
        address=CONFIGURATOR,
        role="configurator",
        intervals=[(0, 1)],
        response_limit=10,
        maximum_normalized_logs=10,
    )
    assert records == []
    assert queries["rpc_error_split_count"] == 1
    assert queries["preemptive_split_count"] == 0
    assert queries["learned_maximum_interval_span"] == 1

    visited: list[tuple[int, int]] = []

    def bounded_handler(
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: object,
    ) -> object:
        del url, deployment, provider, label, method
        assert isinstance(params, list)
        query = cast(dict[str, str], params[0])
        visited.append((int(query["fromBlock"], 16), int(query["toBlock"], 16)))
        return []

    bounded_records, bounded_queries = collect_log_stream(
        FakeRpc(bounded_handler),
        deployment="synthetic",
        chain_id=42,
        url="https://primary.invalid",
        address=CONFIGURATOR,
        role="configurator",
        intervals=[(0, 3)],
        response_limit=10,
        maximum_normalized_logs=10,
        initial_maximum_interval_span=2,
    )
    assert bounded_records == []
    assert visited == [(0, 1), (2, 3)]
    assert bounded_queries["query_count"] == 2
    assert bounded_queries["preemptive_split_count"] == 1
    assert bounded_queries["learned_maximum_interval_span"] == 2

    def failing_handler(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise RpcCallError("single block unavailable")

    with pytest.raises(RpcCallError, match="single block unavailable"):
        collect_log_stream(
            FakeRpc(failing_handler),
            deployment="synthetic",
            chain_id=42,
            url="https://primary.invalid",
            address=CONFIGURATOR,
            role="configurator",
            intervals=[(0, 0)],
            response_limit=10,
            maximum_normalized_logs=10,
        )


def test_source_corrected_history_does_not_require_initial_upgrade() -> None:
    creation = {
        "event_type": "proxy_created",
        "id": CONFIGURATOR_ID,
        "proxy": CONFIGURATOR,
        "implementation": IMPLEMENTATION_1,
        "block_number": 1,
        "transaction_hash": "0x" + "01" * 32,
        "log_index": 0,
    }
    initial = {
        "event_type": "pool_configurator_updated",
        "old_address": "0x" + "00" * 20,
        "new_address": IMPLEMENTATION_1,
        "block_number": 1,
        "transaction_hash": "0x" + "01" * 32,
        "log_index": 1,
    }
    later = {
        "event_type": "pool_configurator_updated",
        "old_address": IMPLEMENTATION_1,
        "new_address": IMPLEMENTATION_2,
        "block_number": 2,
        "transaction_hash": "0x" + "02" * 32,
        "log_index": 1,
    }
    upgrade = {
        "event_type": "upgraded",
        "address": CONFIGURATOR,
        "implementation": IMPLEMENTATION_2,
        "block_number": 2,
        "transaction_hash": "0x" + "02" * 32,
        "log_index": 0,
    }

    surface = derive_configurator_surfaces([creation, initial, later], official_current=CONFIGURATOR)
    history = source_corrected_configurator_history(
        [creation, initial, later], [upgrade], surfaces=[CONFIGURATOR]
    )
    initial_upgrade = {
        "event_type": "upgraded",
        "address": CONFIGURATOR,
        "implementation": IMPLEMENTATION_1,
        "block_number": 1,
        "transaction_hash": "0x" + "01" * 32,
        "log_index": 2,
    }
    history_with_initial_upgrade = source_corrected_configurator_history(
        [creation, initial, later], [initial_upgrade, upgrade], surfaces=[CONFIGURATOR]
    )
    duplicate_initial_upgrade = dict(initial_upgrade)
    duplicate_initial_upgrade["log_index"] = 3
    history_with_duplicate_initial_upgrade = source_corrected_configurator_history(
        [creation, initial, later],
        [initial_upgrade, duplicate_initial_upgrade, upgrade],
        surfaces=[CONFIGURATOR],
    )

    assert surface["official_current_observed"] is True
    assert history["passed"] is True
    assert history["initial_upgrade_count"] == 0
    assert history_with_initial_upgrade["passed"] is True
    assert history_with_initial_upgrade["initial_upgrade_count"] == 1
    assert history_with_duplicate_initial_upgrade["passed"] is False
    assert (
        cast(dict[str, bool], history_with_initial_upgrade["checks"])[
            "initial_transition_allows_zero_or_one_matching_upgrade"
        ]
        is True
    )


def test_normalization_grouping_and_conflict_detection_preserve_full_path() -> None:
    first = normalize_program_log(
        _raw_log(log_index=0, data="0x1234"),
        deployment="synthetic",
        chain_id=42,
        expected_address=CONFIGURATOR,
        role="configurator",
        from_block=0,
        to_block=10,
    )
    second = normalize_program_log(
        _raw_log(log_index=1, topics=["0x" + "98" * 32]),
        deployment="synthetic",
        chain_id=42,
        expected_address=CONFIGURATOR,
        role="configurator",
        from_block=0,
        to_block=10,
    )
    header = {
        "number": 1,
        "hash": BLOCK_HASH,
        "parent_hash": "0x" + "bb" * 32,
        "timestamp_unix": 1_700_000_000,
        "timestamp_utc": "2023-11-14T22:13:20Z",
    }

    programs = build_program_records(
        [first, second],
        [],
        deployment="synthetic",
        chain_id=42,
        split="train",
        headers={1: header},
    )

    assert len(programs) == 1
    assert programs[0]["multi_log"] is True
    assert cast(list[dict[str, object]], programs[0]["configurator_logs"])[0]["data"] == "0x1234"
    conflicting = dict(first)
    conflicting["data"] = "0xabcd"
    _, duplicates, conflicts = deduplicate_program_logs([first, first, conflicting])
    assert duplicates == 1
    assert conflicts == 1


def test_complete_synthetic_deployment_directory_passes_mechanics() -> None:
    provider_tx = 1
    provider_hash = "0x" + f"{provider_tx:064x}"
    provider_logs = [
        _raw_log(
            address=PROVIDER,
            block_number=1,
            block_hash="0x" + f"{2:064x}",
            transaction_number=provider_tx,
            log_index=0,
            topics=[
                "0x4a465a9bd819d9662563c1e11ae958f8109e437e7f4bf1c6ef0b9a7b3f35d478",
                CONFIGURATOR_ID,
                _topic_address(CONFIGURATOR),
                _topic_address(IMPLEMENTATION_1),
            ],
        ),
        _raw_log(
            address=PROVIDER,
            block_number=1,
            block_hash="0x" + f"{2:064x}",
            transaction_number=provider_tx,
            log_index=1,
            topics=[
                "0x8932892569eba59c8382a089d9b732d1f49272878775235761a2a6b0309cd465",
                _topic_address("0x" + "00" * 20),
                _topic_address(IMPLEMENTATION_1),
            ],
        ),
    ]
    assert provider_logs[0]["transactionHash"] == provider_hash
    configurator_logs = [
        _raw_log(
            address=CONFIGURATOR,
            block_number=5,
            block_hash="0x" + f"{6:064x}",
            transaction_number=2,
        )
    ]

    def handler(
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: object,
    ) -> object:
        del url, deployment, provider, label
        if method == "eth_chainId":
            return "0x2a"
        if method == "eth_blockNumber":
            return "0x14"
        assert isinstance(params, list)
        if method == "eth_getBlockByNumber":
            number = int(cast(str, params[0]), 16)
            return _header(number, number * 10)
        query = cast(dict[str, str], params[0])
        if query["address"] == PROVIDER:
            return provider_logs
        if query["address"] == CONFIGURATOR:
            return configurator_logs
        raise AssertionError(query)

    deployment: dict[str, object] = {
        "name": "synthetic",
        "chain_id": 42,
        "chain_id_hex": "0x2a",
        "split": "train",
        "pool_addresses_provider": PROVIDER,
        "pool": "0x" + "55" * 20,
        "pool_configurator": CONFIGURATOR,
        "price_oracle": "0x" + "66" * 20,
        "primary_rpc_url": "https://primary.invalid",
        "replica_rpc_url": "https://replica.invalid",
    }
    rpc_config: dict[str, object] = {
        "root_partition_block_count": 250_000,
        "log_response_limit": 10_000,
    }

    summary, directory = collect_deployment_directory(
        FakeRpc(handler),
        deployment,
        cutoff_timestamp=95,
        rpc_config=rpc_config,
        remaining_log_budget=100,
    )

    assert summary["passed"] is True
    assert cast(dict[str, object], summary["program_directory"])["program_count"] == 1
    assert len(cast(list[dict[str, object]], directory["programs"])) == 1


def _synthetic_support_programs() -> list[dict[str, object]]:
    split_deployments = {
        "train": ["arbitrum", "avalanche", "optimism", "polygon"],
        "validation": ["base", "gnosis"],
        "test": ["bnb", "linea", "scroll"],
    }
    counts = {"train": 30, "validation": 20, "test": 20}
    starts = {"train": 1_577_836_800, "validation": 1_640_995_200, "test": 1_640_995_200}
    spans = {"train": 900 * 86_400, "validation": 500 * 86_400, "test": 500 * 86_400}
    programs: list[dict[str, object]] = []
    index = 0
    for split, deployments in split_deployments.items():
        total = counts[split] * len(deployments)
        step = spans[split] // (total - 1)
        split_index = 0
        for deployment_index, deployment in enumerate(deployments):
            for local_index in range(counts[split]):
                timestamp = starts[split] + split_index * step
                topic = "0x" + f"{local_index % 12 + 1:064x}"
                programs.append(
                    {
                        "program_id": f"{index}:0x{index:064x}",
                        "deployment": deployment,
                        "split": split,
                        "topic0_counts": {topic: 1},
                        "multi_log": True,
                        "contains_upgrade": local_index == 0 and deployment_index < 2,
                        "block_timestamp_unix": timestamp,
                        "calendar_quarter": f"Q{split_index // 5}",
                    }
                )
                index += 1
                split_index += 1
    return programs


def test_support_thresholds_are_split_locked_and_fail_closed() -> None:
    programs = _synthetic_support_programs()

    summary, passes = summarize_support(programs, EXPECTED_SUPPORT_THRESHOLDS)

    assert len(programs) == 220
    assert passes == {"train": True, "validation": True, "test": True, "total": True}
    assert summary["total_non_development_program_count"] == 220

    stricter = deepcopy(EXPECTED_SUPPORT_THRESHOLDS)
    stricter["minimum_total_non_development_programs"] = 221
    _, failed = summarize_support(programs, stricter)
    assert failed["total"] is False
