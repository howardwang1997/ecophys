from scripts.audit_aave_rate_response_d1b import (
    RpcError,
    _keccak_topic,
    _load_policy_checkpoint,
    _merge_block_intervals,
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
    assert _splittable(RpcError("rate limit exceeded", http_status=429)) is False


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
