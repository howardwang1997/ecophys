from __future__ import annotations

from scripts.screen_aave_rate_response_activity import RpcError, _is_splittable_log_error


def test_archive_authorization_failure_is_not_range_split() -> None:
    error = RpcError(
        "RPC eth_getLogs returned HTTP 403: archive token required",
        http_status=403,
    )
    assert _is_splittable_log_error(error) is False


def test_range_and_response_size_failures_can_split() -> None:
    assert _is_splittable_log_error(
        RpcError("RPC eth_getLogs failed: block range is too wide", rpc_code=-32602)
    )
    assert _is_splittable_log_error(
        RpcError("RPC eth_getLogs failed: limit exceeded", rpc_code=-32005)
    )
    assert _is_splittable_log_error(
        RpcError("RPC eth_getLogs returned HTTP 413", http_status=413)
    )
