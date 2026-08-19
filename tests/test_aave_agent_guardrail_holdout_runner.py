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
    _canonical_log_identity_sha256,
    _first_nonempty_hub_shard,
    _load_chain_checkpoint,
    _qualify_state_witness,
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

    assert _canonical_log_identity_sha256(identities) == (
        "0da18cb3ca6994e97b371aa46b4bac9bc94857777154bfa410c5643652fe70c2"
    )


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


def test_log_transport_anchor_does_not_require_historical_contract_state() -> None:
    class FakeClient:
        def call(self, method: str, params: list[Any]) -> Any:
            del params
            assert method == "eth_chainId"
            return "0xa"

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

    _validate_transport_anchor(  # type: ignore[arg-type]
        FakeClient(),
        chain=chain,
        require_contract_code=False,
    )


def test_state_witness_uses_first_archive_capable_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        def __init__(self, url: str) -> None:
            self.url = url
            self.method_counts = {"eth_chainId": 1}

    clients = {
        "https://pruned.test": FakeClient("https://pruned.test"),
        "https://archive.test": FakeClient("https://archive.test"),
    }

    def fake_new_client(url: str, *, minimum_interval: float) -> FakeClient:
        assert minimum_interval == 0.75
        return clients[url]

    def fake_validate(client: FakeClient, *, chain: Any, require_contract_code: bool) -> None:
        del chain
        assert require_contract_code is True
        if client.url == "https://pruned.test":
            raise RuntimeError("missing trie node")

    monkeypatch.setattr(holdout_runner, "_new_client", fake_new_client)
    monkeypatch.setattr(holdout_runner, "_validate_transport_anchor", fake_validate)

    result = _qualify_state_witness(
        chain={"chain_id": 10},
        candidate_urls=["https://pruned.test", "https://archive.test"],
        minimum_interval=0.75,
    )

    assert result["state_witness_rpc"] == "https://archive.test"
    assert result["frozen_endpoint_agent_hub_code_verified"] is True
    assert len(result["failed_candidates_before_success"]) == 1


def test_state_witness_verifies_frozen_consecutive_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.method_counts = {"eth_call": 2}

        def call(self, method: str, params: list[Any]) -> Any:
            assert method == "eth_call"
            assert params[0] == {
                "to": "0x" + "11" * 20,
                "data": holdout_runner._keccak_topic("getAgentCount()")[:10],
            }
            return "0x0" if params[1] == hex(20) else "0x2"

    monkeypatch.setattr(
        holdout_runner,
        "_new_client",
        lambda url, *, minimum_interval: FakeClient(),
    )
    monkeypatch.setattr(
        holdout_runner,
        "_validate_transport_anchor",
        lambda client, *, chain, require_contract_code: None,
    )
    result = _qualify_state_witness(
        chain={
            "agent_hub": "0x" + "11" * 20,
            "qualification_state_transition": {
                "method_signature": "getAgentCount()",
                "last_zero_block": 20,
                "last_zero_count": 0,
                "first_positive_block": 21,
                "first_positive_count": 2,
            },
        },
        candidate_urls=["https://archive.test"],
        minimum_interval=0.75,
    )

    assert result["qualification_state_transition"]["exact_consecutive_transition_verified"]


def test_qualification_scan_starts_at_aligned_frozen_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_query(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        del args
        calls.append((kwargs["start_block"], kwargs["end_block"]))
        return [_raw_log(block=kwargs["start_block"], transaction=1, log_index=0)]

    monkeypatch.setattr(holdout_runner, "_query_logs_interval", fake_query)
    chain = {
        "agent_hub": "0x" + "11" * 20,
        "from_block": 100,
        "to_block": 500,
        "qualification_from_block": 300,
    }

    start, end, logs = _first_nonempty_hub_shard(
        object(),  # type: ignore[arg-type]
        chain=chain,
        hub_topics=["0x" + "22" * 32],
        span=100,
        maximum_topics_per_query=14,
    )

    assert (start, end, len(logs)) == (300, 399, 1)
    assert calls == [(300, 399)]
    with pytest.raises(ValueError, match="aligned"):
        _first_nonempty_hub_shard(
            object(),  # type: ignore[arg-type]
            chain={**chain, "qualification_from_block": 301},
            hub_topics=["0x" + "22" * 32],
            span=100,
            maximum_topics_per_query=14,
        )


def test_exact_qualification_shard_cannot_drift_after_an_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []

    def fake_query(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        del args
        calls.append((kwargs["start_block"], kwargs["end_block"]))
        return []

    monkeypatch.setattr(holdout_runner, "_query_logs_interval", fake_query)
    with pytest.raises(RuntimeError, match="exact frozen"):
        _first_nonempty_hub_shard(
            object(),  # type: ignore[arg-type]
            chain={
                "agent_hub": "0x" + "11" * 20,
                "from_block": 100,
                "to_block": 500,
                "qualification_from_block": 300,
                "qualification_to_block": 399,
            },
            hub_topics=["0x" + "22" * 32],
            span=100,
            maximum_topics_per_query=14,
        )

    assert calls == [(300, 399)]


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
