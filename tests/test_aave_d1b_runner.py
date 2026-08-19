from scripts.audit_aave_rate_response_d1b import (
    RpcError,
    _get_logs_with_split,
    _keccak_topic,
    _load_policy_checkpoint,
    _merge_block_intervals,
    _prefer_topic_split,
    _retryable_rpc_server_error,
    _splittable,
    _write_policy_checkpoint,
)


def test_policy_ledger_merges_only_overlapping_or_adjacent_ranges() -> None:
    assert _merge_block_intervals([(20, 30), (1, 10), (11, 15), (29, 40)]) == [
        (1, 15),
        (20, 40),
    ]


def test_policy_log_transport_splits_timeouts_but_not_rate_limits() -> None:
    assert _splittable(RpcError("gateway timeout", http_status=504)) is True
    assert _splittable(RpcError("block range is too wide", rpc_code=-32602)) is True
    assert _splittable(RpcError("method handler crashed", rpc_code=-32000)) is False
    assert _splittable(RpcError("rate limit exceeded", http_status=429)) is False


def test_exact_handler_crash_is_retryable_but_other_server_errors_are_not() -> None:
    assert _retryable_rpc_server_error(
        {"error": {"message": "method handler crashed", "code": -32000}}
    )
    assert not _retryable_rpc_server_error(
        {"error": {"message": "method handler crashed", "code": -32602}}
    )
    assert not _retryable_rpc_server_error(
        {"error": {"message": "execution reverted", "code": -32000}}
    )


def test_d0_prefers_topic_split_for_backend_timeouts_not_range_limits() -> None:
    assert _prefer_topic_split(RpcError("method handler crashed", rpc_code=-32000))
    assert _prefer_topic_split(RpcError("request timeout", http_status=408))
    assert not _prefer_topic_split(RpcError("block range is too wide", rpc_code=-32602))


def test_topic_first_log_split_preserves_block_range() -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.log_range_splits = 0
            self.log_topic_splits = 0
            self.topic_group_sizes: list[int] = []

        def call(self, method: str, params: list[object]) -> list[object]:
            assert method == "eth_getLogs"
            request = params[0]
            assert isinstance(request, dict)
            topic_filter = request["topics"]
            assert isinstance(topic_filter, list)
            topics = topic_filter[0]
            assert isinstance(topics, list)
            self.topic_group_sizes.append(len(topics))
            if len(topics) > 1:
                raise RpcError("request timeout", http_status=408)
            return []

    client = FakeClient()
    assert (
        _get_logs_with_split(
            client,  # type: ignore[arg-type]
            addresses=["0x" + "11" * 20],
            topics=["0x" + f"{index:064x}" for index in range(4)],
            start_block=100,
            end_block_inclusive=200,
            remaining_split_depth=10,
            split_topics_first=True,
        )
        == []
    )
    assert client.topic_group_sizes == [4, 2, 1, 1, 2, 1, 1]
    assert client.log_topic_splits == 3
    assert client.log_range_splits == 0


def test_local_keccak_matches_ethereum_erc20_event_vector() -> None:
    assert _keccak_topic("Transfer(address,address,uint256)") == (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    )


def test_policy_checkpoint_round_trip_is_identity_bound(tmp_path) -> None:
    path = tmp_path / "policy.json"
    identity = {
        "repository_sha": "a" * 40,
        "config_sha256": "b" * 64,
        "parent_t0_sha256": "c" * 64,
        "parent_d1a_sha256": "d" * 64,
        "formal_rpc": "https://example.test",
    }
    _write_policy_checkpoint(
        path,
        identity=identity,
        support_windows=[{"proposal_id": 3}],
        merged_intervals=[(100, 200)],
        completed_interval_count=1,
        policy_events=[{"event_name": "ReserveBorrowing"}],
    )
    assert _load_policy_checkpoint(path, identity=identity) == (
        [{"proposal_id": 3}],
        [(100, 200)],
        1,
        [{"event_name": "ReserveBorrowing"}],
    )
