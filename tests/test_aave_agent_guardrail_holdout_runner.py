from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from ecomd.data.aave_qualification import canonical_sha256
from scripts import audit_aave_agent_guardrail_holdout_d0 as holdout_runner
from scripts.audit_aave_agent_guardrail_holdout_d0 import (
    _canonical_log_identities,
    _load_chain_checkpoint,
    _validate_pilot_binding,
    _validate_transport_anchor,
    _verified_artifact,
    _write_chain_checkpoint,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/empirical_physics/aave_agent_guardrail_holdout_d0_v1.yaml"


def _raw_log(*, block: int, transaction: int, log_index: int) -> dict[str, Any]:
    return {
        "blockNumber": hex(block),
        "blockHash": "0x" + f"{block:064x}",
        "transactionHash": "0x" + f"{transaction:064x}",
        "logIndex": hex(log_index),
    }


def test_canonical_log_identities_sort_and_reject_duplicates() -> None:
    later = _raw_log(block=12, transaction=2, log_index=1)
    earlier = _raw_log(block=11, transaction=1, log_index=0)

    identities = _canonical_log_identities([later, earlier])

    assert identities == sorted(identities)
    with pytest.raises(ValueError, match="duplicate"):
        _canonical_log_identities([earlier, earlier])


def test_holdout_checkpoint_round_trip_is_digest_and_identity_bound(tmp_path: Path) -> None:
    path = tmp_path / "holdout.json"
    identity = {
        "repository_sha": "a" * 40,
        "config_sha256": "b" * 64,
        "chain_name": "base",
        "chain_id": 8453,
        "formal_rpc": "https://example.test",
        "from_block": 10,
        "to_block": 20,
    }
    state = {
        "completed_through": {"hub": 12, "range": 9, "proposals": 9},
        "events": {
            "hub": [{"event_name": "AgentRegistered"}],
            "range": [],
            "proposals": [],
        },
        "block_headers": {"12": {"number": 12, "hash": "0x" + "aa" * 32}},
    }
    _write_chain_checkpoint(path, identity=identity, state=state)

    loaded, resumed = _load_chain_checkpoint(path, identity=identity, from_block=10)

    assert resumed is True
    assert loaded == state
    with pytest.raises(RuntimeError, match="identity"):
        _load_chain_checkpoint(path, identity={**identity, "formal_rpc": "changed"}, from_block=10)

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["completed_through"]["hub"] = 13
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="digest"):
        _load_chain_checkpoint(path, identity=identity, from_block=10)


def test_pilot_binding_is_verified_against_the_frozen_artifact() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

    audit = _validate_pilot_binding(config)

    assert audit["canonical_payload_sha256"] == (
        "764f08a7a02c550f28f8b7ace275cf4e451ba5430ea5768aff55f374c1226460"
    )
    assert audit["excluded_from_all_holdout_counts"] is True


def test_transport_anchor_rejects_zero_contract_code() -> None:
    class FakeClient:
        def call(self, method: str, params: list[Any]) -> Any:
            if method == "eth_chainId":
                return "0xa"
            assert method == "eth_getCode"
            return "0x00"

        def block(self, number: int) -> dict[str, Any]:
            return {"number": number, "timestamp": number, "hash": "0x" + f"{number:064x}"}

    chain = {
        "chain_id": 10,
        "from_block": 1,
        "from_block_hash": "0x" + f"{1:064x}",
        "to_block": 2,
        "to_block_hash": "0x" + f"{2:064x}",
        "agent_hub": "0x" + "11" * 20,
    }
    with pytest.raises(RuntimeError, match="code is absent"):
        _validate_transport_anchor(FakeClient(), chain=chain)  # type: ignore[arg-type]


def test_log_query_partitions_topics_and_preserves_the_exact_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int, tuple[str, ...]]] = []

    def fake_get_logs(
        client: Any,
        *,
        addresses: Any,
        topics: Any,
        start_block: int,
        end_block_inclusive: int,
        remaining_split_depth: int,
        split_topics_first: bool,
    ) -> list[dict[str, Any]]:
        del client, addresses
        assert remaining_split_depth == 24
        assert split_topics_first is False
        calls.append((start_block, end_block_inclusive, tuple(topics)))
        return [_raw_log(block=start_block, transaction=len(calls), log_index=len(calls))]

    monkeypatch.setattr(holdout_runner, "_get_logs_with_split", fake_get_logs)
    topics = ["0x" + f"{index:064x}" for index in range(15)]

    result = holdout_runner._query_logs_interval(
        object(),  # type: ignore[arg-type]
        addresses=["0x" + "11" * 20],
        topics=topics,
        start_block=100,
        end_block=200,
        maximum_topics_per_query=14,
    )

    assert len(result) == 2
    assert calls == [
        (100, 200, tuple(topics[:14])),
        (100, 200, tuple(topics[14:])),
    ]


def test_chain_artifact_digest_is_recomputed(tmp_path: Path) -> None:
    path = tmp_path / "chain.json"
    body = {"artifact_type": "outcome_blind_chain_shard", "chain": {"name": "base"}}
    payload = {**body, "canonical_payload_sha256": canonical_sha256(body)}
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert _verified_artifact(path) == payload
    payload["chain"]["name"] = "optimism"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="digest"):
        _verified_artifact(path)
