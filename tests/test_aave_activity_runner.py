from __future__ import annotations

from pathlib import Path

from scripts.screen_aave_rate_response_activity import (
    RpcError,
    _is_splittable_log_error,
    _load_checkpoint,
    _rate_limit_delay,
    _write_checkpoint,
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
    assert _is_splittable_log_error(
        RpcError("RPC eth_getLogs returned HTTP 408", http_status=408)
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


def test_sanitized_checkpoint_round_trip(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.json"
    events = [
        {
            "proposal_id": 3,
            "assets": {
                "DAI": {
                    "total_borrow_events": 20,
                    "retained_addresses_amounts_transactions_or_raw_logs": False,
                }
            },
        }
    ]
    _write_checkpoint(
        checkpoint,
        repository_sha="a" * 40,
        config_sha256="b" * 64,
        parent_t0_sha256="c" * 64,
        event_results=events,
    )
    loaded, resumed = _load_checkpoint(
        checkpoint,
        repository_sha="a" * 40,
        config_sha256="b" * 64,
        parent_t0_sha256="c" * 64,
        ordered_proposal_ids=[3, 94],
    )
    assert resumed is True
    assert loaded == events
