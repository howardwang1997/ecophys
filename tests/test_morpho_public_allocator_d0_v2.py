from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest

import scripts.audit_morpho_public_allocator_pressure_d0_v2 as runner
from ecomd.data.morpho_public_allocator_support import canonical_log_identity

ALLOCATOR = "0x" + "11" * 20
MORPHO = "0x" + "22" * 20
WITHDRAWAL = "0x" + "31" * 32
TERMINAL = "0x" + "32" * 32
BORROW = "0x" + "33" * 32
SENDER = "0x" + "41" * 32
VAULT = "0x" + "42" * 32
DONOR = "0x" + "43" * 32
TARGET = "0x" + "44" * 32


def _log(
    block: int,
    index: int,
    transaction_hash: str,
    address: str,
    topics: list[str],
) -> dict[str, Any]:
    return {
        "block_number": block,
        "block_hash": "0x" + f"{block:064x}",
        "block_timestamp": 1_700_000_000 + block,
        "transaction_hash": transaction_hash,
        "transaction_index": 1,
        "log_index": index,
        "contract_address": address,
        "topic0": topics[0],
        "topics": topics,
    }


def test_inclusive_block_shards_cover_exactly_without_overlap() -> None:
    assert runner.inclusive_block_shards(10, 20, 4) == [(10, 13), (14, 17), (18, 20)]
    assert runner.inclusive_block_shards(5, 5, 100) == [(5, 5)]
    with pytest.raises(ValueError, match="invalid inclusive"):
        runner.inclusive_block_shards(10, 9, 4)


def test_parallel_portal_union_is_canonical_despite_completion_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_shard(
        index: int,
        chain: dict[str, Any],
        transport: dict[str, Any],
        address: str,
        topics: list[str],
        block_range: tuple[int, int],
    ) -> runner.PortalShardResult:
        del chain, transport, address, topics
        time.sleep(0.004 * (2 - index))
        transaction_hash = "0x" + f"{index + 1:064x}"
        log = _log(block_range[0], 0, transaction_hash, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR])
        return runner.PortalShardResult(
            index=index,
            logs=(log,),
            stats={
                "page_count": 1,
                "header_count": 2,
                "request_count": 1,
                "retry_count": index % 2,
                "bytes_received": 100 + index,
            },
        )

    monkeypatch.setattr(runner, "_portal_shard", fake_shard)
    logs, stats = runner.parallel_portal_logs(
        {},
        {},
        address=ALLOCATOR,
        topics=[WITHDRAWAL],
        from_block=10,
        to_block=18,
        shard_span=3,
        max_workers=3,
    )

    assert [row["block_number"] for row in logs] == [10, 13, 16]
    assert stats == {
        "block_shard_span": 3,
        "shard_count": 3,
        "completed_shard_count": 3,
        "max_workers": 3,
        "page_count": 3,
        "header_count": 6,
        "request_count": 3,
        "retry_count": 1,
        "bytes_received": 303,
    }


def test_parallel_portal_union_rejects_duplicate_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    duplicate = _log(
        10,
        0,
        "0x" + "55" * 32,
        ALLOCATOR,
        [WITHDRAWAL, SENDER, VAULT, DONOR],
    )

    def fake_shard(*args: Any, **kwargs: Any) -> runner.PortalShardResult:
        del kwargs
        index = int(args[0])
        return runner.PortalShardResult(
            index=index,
            logs=(duplicate,),
            stats={
                "page_count": 1,
                "header_count": 1,
                "request_count": 1,
                "retry_count": 0,
                "bytes_received": 1,
            },
        )

    monkeypatch.setattr(runner, "_portal_shard", fake_shard)
    with pytest.raises(ValueError, match="duplicate canonical identity"):
        runner.parallel_portal_logs(
            {},
            {},
            address=ALLOCATOR,
            topics=[WITHDRAWAL],
            from_block=10,
            to_block=11,
            shard_span=1,
            max_workers=2,
        )


def test_parallel_receipts_reduce_in_canonical_transaction_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transactions = ["0x" + "61" * 32, "0x" + "62" * 32]
    indexed: dict[str, list[dict[str, Any]]] = {}
    receipts: dict[str, list[dict[str, Any]]] = {}
    for offset, transaction_hash in enumerate(transactions):
        block = 100 + offset
        withdrawal = _log(
            block,
            2,
            transaction_hash,
            ALLOCATOR,
            [WITHDRAWAL, SENDER, VAULT, DONOR],
        )
        terminal = _log(
            block,
            4,
            transaction_hash,
            ALLOCATOR,
            [TERMINAL, SENDER, VAULT, TARGET],
        )
        borrow = _log(block, 6, transaction_hash, MORPHO, [BORROW, TARGET, SENDER, VAULT])
        indexed[transaction_hash] = [withdrawal, terminal]
        receipts[transaction_hash] = [withdrawal, terminal, borrow]

    def fake_receipt_logs(
        client: object,
        *,
        transaction_hash: str,
        expected_block_number: int,
        expected_block_hash: str,
        block_timestamp: int,
    ) -> tuple[list[dict[str, Any]], int]:
        del client, expected_block_number, expected_block_hash, block_timestamp
        if transaction_hash == transactions[0]:
            time.sleep(0.01)
        return receipts[transaction_hash], 123

    monkeypatch.setattr(runner, "_receipt_logs", fake_receipt_logs)
    classifications, by_block, verified_index_only, stats = runner.parallel_receipt_classifications(
        dict(reversed(list(indexed.items()))),
        chain={"receipt_rpc": "https://example.invalid", "morpho": MORPHO},
        transport={
            "rpc_timeout_seconds": 1,
            "rpc_retry_attempts": 0,
            "rpc_retry_backoff_seconds": 0,
            "rpc_minimum_request_interval_seconds": 0.01,
        },
        allocator=ALLOCATOR,
        withdrawal_topic=WITHDRAWAL,
        terminal_topic=TERMINAL,
        borrow_topic=BORROW,
        index_only=set(),
        max_workers=2,
        minimum_interval_seconds=0.01,
    )

    assert [row.transaction_hash for row in classifications] == transactions
    assert all(row.is_candidate for row in classifications)
    assert set(by_block) == {100, 101}
    assert verified_index_only == set()
    assert stats["receipt_transaction_count"] == 2
    assert stats["verified_receipt_transaction_count"] == 2
    assert stats["receipt_mismatch_count"] == 0
    assert stats["observed_payload_bytes"] == 246


def test_parallel_receipts_keep_mismatch_fail_visible(monkeypatch: pytest.MonkeyPatch) -> None:
    transaction_hash = "0x" + "71" * 32
    withdrawal = _log(
        100,
        2,
        transaction_hash,
        ALLOCATOR,
        [WITHDRAWAL, SENDER, VAULT, DONOR],
    )

    def fake_receipt_logs(*args: Any, **kwargs: Any) -> tuple[list[dict[str, Any]], int]:
        del args, kwargs
        return [], 10

    monkeypatch.setattr(runner, "_receipt_logs", fake_receipt_logs)
    classifications, by_block, _, stats = runner.parallel_receipt_classifications(
        {transaction_hash: [withdrawal]},
        chain={"receipt_rpc": "https://example.invalid", "morpho": MORPHO},
        transport={
            "rpc_timeout_seconds": 1,
            "rpc_retry_attempts": 0,
            "rpc_retry_backoff_seconds": 0,
            "rpc_minimum_request_interval_seconds": 0.01,
        },
        allocator=ALLOCATOR,
        withdrawal_topic=WITHDRAWAL,
        terminal_topic=TERMINAL,
        borrow_topic=BORROW,
        index_only={canonical_log_identity(withdrawal)},
        max_workers=1,
        minimum_interval_seconds=0.01,
    )
    assert classifications == []
    assert dict(by_block) == {}
    assert stats["receipt_mismatch_count"] == 1
    assert stats["verified_receipt_transaction_count"] == 0


def test_amendment_binds_parent_and_hides_cuda() -> None:
    amendment = runner._verify_amendment(runner.AMENDMENT_PATH, runner.CONFIG_PATH)
    assert amendment["contract"]["parent_config_sha256"] == runner._sha256_file(runner.CONFIG_PATH)
    assert amendment["execution"]["cuda_visible_devices"] == ""
    assert amendment["formal_run"]["required_chains"] == ["ethereum", "base"]


def test_worker_environment_is_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    amendment = runner._verify_amendment(runner.AMENDMENT_PATH, runner.CONFIG_PATH)
    monkeypatch.setenv("ECOPHYS_D0_WORKER_ID", "v100_a_cpu_network_only")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
    assert runner._validate_worker_environment("ethereum", amendment) == "v100_a_cpu_network_only"
    with pytest.raises(RuntimeError, match="v100_b_cpu_network_only"):
        runner._validate_worker_environment("base", amendment)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0")
    with pytest.raises(RuntimeError, match="CUDA_VISIBLE_DEVICES"):
        runner._validate_worker_environment("ethereum", amendment)


def test_formal_batch_id_binds_code_config_and_qualification() -> None:
    qualification = {"canonical_payload_sha256": "q" * 64}
    observed = runner._formal_batch_id(
        amendment_path=runner.AMENDMENT_PATH, qualification=qualification, git_sha="a" * 40
    )
    changed = runner._formal_batch_id(
        amendment_path=runner.AMENDMENT_PATH, qualification=qualification, git_sha="b" * 40
    )
    assert len(observed) == 64
    assert observed != changed


def test_aggregate_artifact_guard_rejects_raw_evm_identity() -> None:
    runner._assert_no_raw_evm_identities({"digest": "a" * 64, "count": 2})
    with pytest.raises(RuntimeError, match="raw EVM identity"):
        runner._assert_no_raw_evm_identities({"transaction": "0x" + "ab" * 32})
    with pytest.raises(RuntimeError, match="raw EVM identity"):
        runner._assert_no_raw_evm_identities({"address": "0x" + "ab" * 20})
    with pytest.raises(RuntimeError, match="raw EVM identity"):
        runner._assert_no_raw_evm_identities({"error": "bad value 0x" + "ab" * 32 + " in response"})
    assert "0x" not in runner._redact_raw_evm_identities("bad 0x" + "ab" * 32)


def test_support_gates_recompute_original_conjunction() -> None:
    thresholds = runner._load_yaml(runner.CONFIG_PATH)["pass_thresholds"]
    support = {
        "candidate_transaction_count": 250,
        "active_span_days": 100.0,
        "active_utc_date_count": 40,
        "distinct_vault_count": 4,
        "distinct_directed_edge_count": 6,
        "classification_rate": 1.0,
    }
    result = {
        "status": "transport_pass_support_computed",
        "transport": {"transport_pass": True, "receipt_verification_rate": 1.0},
        "support": support,
    }
    chain_gates, pooled_gates, candidates, edges = runner._support_gates(
        {"ethereum": result, "base": result}, thresholds
    )
    assert all(all(row.values()) for row in chain_gates.values())
    assert all(pooled_gates.values())
    assert candidates == 500
    assert edges == 12


def test_support_gates_do_not_encode_missing_support_as_zero() -> None:
    thresholds = runner._load_yaml(runner.CONFIG_PATH)["pass_thresholds"]
    failed = {
        "status": "transport_fail_before_support_interpretation",
        "transport_error_type": "ConnectTimeout",
        "support": None,
    }
    chain_gates, pooled_gates, candidates, edges = runner._support_gates(
        {"ethereum": failed, "base": failed}, thresholds
    )
    assert not any(chain_gates["ethereum"].values())
    assert not any(chain_gates["base"].values())
    assert not any(pooled_gates.values())
    assert candidates is None
    assert edges is None


def test_support_gates_do_not_partially_pool_one_missing_chain() -> None:
    thresholds = runner._load_yaml(runner.CONFIG_PATH)["pass_thresholds"]
    support = {
        "candidate_transaction_count": 250,
        "active_span_days": 100.0,
        "active_utc_date_count": 40,
        "distinct_vault_count": 4,
        "distinct_directed_edge_count": 6,
        "classification_rate": 1.0,
    }
    passed = {
        "status": "transport_pass_support_computed",
        "transport": {"transport_pass": True, "receipt_verification_rate": 1.0},
        "support": support,
    }
    failed = {
        "status": "transport_fail_before_support_interpretation",
        "transport_error_type": "ValueError",
        "support": None,
    }
    chain_gates, pooled_gates, candidates, edges = runner._support_gates(
        {"ethereum": passed, "base": failed}, thresholds
    )
    assert all(chain_gates["ethereum"].values())
    assert not any(chain_gates["base"].values())
    assert not any(pooled_gates.values())
    assert candidates is None
    assert edges is None


def test_chain_artifact_output_is_required() -> None:
    with pytest.raises(SystemExit):
        runner.main(
            [
                "--phase",
                "chain",
                "--chain",
                "ethereum",
                "--sdk-root",
                str(Path("/tmp/sdk")),
                "--public-allocator-root",
                str(Path("/tmp/allocator")),
                "--morpho-blue-root",
                str(Path("/tmp/blue")),
            ]
        )


def test_chain_artifact_output_must_be_outside_repository() -> None:
    with pytest.raises(SystemExit, match="outside the repository"):
        runner.main(
            [
                "--phase",
                "chain",
                "--chain",
                "ethereum",
                "--output",
                str(runner.REPO_ROOT / "chain.json"),
                "--sdk-root",
                str(Path("/tmp/sdk")),
                "--public-allocator-root",
                str(Path("/tmp/allocator")),
                "--morpho-blue-root",
                str(Path("/tmp/blue")),
            ]
        )
