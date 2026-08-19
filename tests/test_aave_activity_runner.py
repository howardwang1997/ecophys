from __future__ import annotations

from scripts.screen_aave_rate_response_activity import (
    RpcError,
    _is_splittable_log_error,
    _rate_limit_delay,
)


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
        RpcError("RPC eth_getLogs returned HTTP 413", http_status=413)
    )


def test_rate_limit_code_without_range_message_does_not_split() -> None:
    assert not _is_splittable_log_error(
        RpcError("RPC eth_getLogs failed: request rate limit exceeded", rpc_code=-32005)
    )


def test_rate_limit_delay_honors_header_and_cap() -> None:
    assert _rate_limit_delay(
        attempt=0,
        initial_seconds=5.0,
        maximum_seconds=30.0,
        retry_after="12",
    ) == 12.0
    assert _rate_limit_delay(
        attempt=4,
        initial_seconds=5.0,
        maximum_seconds=30.0,
        retry_after=None,
    ) == 30.0
