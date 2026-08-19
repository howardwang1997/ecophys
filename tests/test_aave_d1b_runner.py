from scripts.audit_aave_rate_response_d1b import (
    RpcError,
    _keccak_topic,
    _merge_block_intervals,
    _splittable,
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
