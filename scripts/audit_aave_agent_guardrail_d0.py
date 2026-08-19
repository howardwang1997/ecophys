"""Run the frozen outcome-blind Aave automated-agent action-support audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from ecomd.data.aave_agent_guardrail import (
    address_from_topic,
    assess_action_support,
    bool_from_topic,
    build_action_ledger,
    decode_default_range_config_data,
    decode_market_range_config_data,
    decode_parameter_updated_data,
    decode_update_injected_data,
    event_position,
    normalize_hex_data,
    normalize_topic,
    uint_from_topic,
)
from ecomd.data.aave_qualification import (
    canonical_sha256,
    extract_solidity_event_definitions,
    normalize_address,
)
from scripts.audit_aave_rate_response_d1b import (
    _get_logs_with_split,
    _git,
    _hash,
    _hex_quantity,
    _keccak_topic,
    _RpcClient,
    _verify_repo,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

HUB_SIGNATURES = {
    "AgentRegistered(uint256,address,string)",
    "AgentAddressSet(uint256,address)",
    "AgentAdminSet(uint256,address)",
    "AgentPermissionedStatusSet(uint256,bool)",
    "AgentEnabledSet(uint256,bool)",
    "MarketsFromAgentEnabled(uint256,bool)",
    "ExpirationPeriodSet(uint256,uint256)",
    "MinimumDelaySet(uint256,uint256)",
    "AgentContextSet(uint256,bytes)",
    "AllowedMarketAdded(uint256,address)",
    "AllowedMarketRemoved(uint256,address)",
    "RestrictedMarketAdded(uint256,address)",
    "RestrictedMarketRemoved(uint256,address)",
    "UpdateInjected(uint256,address,string,uint256,bytes)",
}
RANGE_SIGNATURES = {
    "DefaultRangeConfigSet(address,uint256,string,(uint120,uint120,bool,bool))",
    "MarketRangeConfigSet(address,uint256,address,string,(uint120,uint120,bool,bool))",
}
RISK_ORACLE_SIGNATURE = "ParameterUpdated(string,bytes,bytes,uint256,string,uint256,address,bytes)"


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML contract must be an object: {path}")
    return payload


def _utc(unix_seconds: int) -> str:
    return datetime.fromtimestamp(unix_seconds, UTC).isoformat()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_checkpoint(
    path: Path,
    *,
    identity: Mapping[str, Any],
    state: Mapping[str, Any],
) -> None:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "identity": dict(identity),
        **state,
        "contains_only_decoded_policy_events_and_block_headers": True,
        "contains_raw_rpc_or_market_outcomes": False,
    }
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_checkpoint(
    path: Path,
    *,
    identity: Mapping[str, Any],
    from_block: int,
) -> tuple[dict[str, Any], bool]:
    if not path.exists():
        return (
            {
                "completed_through": {
                    "hub": from_block - 1,
                    "range": from_block - 1,
                    "proposals": from_block - 1,
                },
                "events": {"hub": [], "range": [], "proposals": []},
                "block_headers": {},
            },
            False,
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("D0 checkpoint is not a JSON object")
    stored_digest = str(payload.get("canonical_payload_sha256"))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if canonical_sha256(body) != stored_digest:
        raise RuntimeError("D0 checkpoint digest mismatch")
    if payload.get("identity") != dict(identity):
        raise RuntimeError("D0 checkpoint identity mismatch")
    if payload.get("contains_raw_rpc_or_market_outcomes") is not False:
        raise RuntimeError("D0 checkpoint lacks the no-outcome assertion")
    completed = payload.get("completed_through")
    events = payload.get("events")
    headers = payload.get("block_headers")
    stages = {"hub", "range", "proposals"}
    if (
        not isinstance(completed, dict)
        or set(completed) != stages
        or any(not isinstance(completed[stage], int) for stage in stages)
        or not isinstance(events, dict)
        or set(events) != stages
        or any(
            not isinstance(events[stage], list) or any(not isinstance(event, dict) for event in events[stage])
            for stage in stages
        )
        or not isinstance(headers, dict)
        or any(not isinstance(header, dict) for header in headers.values())
    ):
        raise RuntimeError("D0 checkpoint is malformed")
    return (
        {
            "completed_through": dict(completed),
            "events": {stage: list(events[stage]) for stage in stages},
            "block_headers": dict(headers),
        },
        True,
    )


def _source_audit(
    config: Mapping[str, Any],
    *,
    agent_hub_root: Path,
    risk_agents_root: Path,
    chaos_agents_root: Path,
    address_book_root: Path,
    proposals_root: Path,
) -> dict[str, Any]:
    official = config["official_sources"]
    repositories = {
        "agent_hub": _verify_repo(
            agent_hub_root,
            str(official["agent_hub"]["expected_git_sha"]),
            label="Aave Agent Hub",
        ),
        "risk_agents": _verify_repo(
            risk_agents_root,
            str(official["risk_agents"]["expected_git_sha"]),
            label="Aave Risk Agents",
        ),
        "chaos_agents": _verify_repo(
            chaos_agents_root,
            str(official["chaos_agents"]["expected_git_sha"]),
            label="Chaos Agents",
        ),
        "address_book": _verify_repo(
            address_book_root,
            str(official["address_book"]["expected_git_sha"]),
            label="Aave address book",
        ),
        "proposals_repository": _verify_repo(
            proposals_root,
            str(official["proposals_repository"]["expected_git_sha"]),
            label="Aave proposals repository",
        ),
    }

    hub_interface = agent_hub_root / "src/interfaces/IAgentConfigurator.sol"
    range_interface = agent_hub_root / "src/interfaces/IRangeValidationModule.sol"
    oracle_interface = agent_hub_root / "src/contracts/dependencies/IRiskOracle.sol"
    chaos_hub_interface = chaos_agents_root / "src/interfaces/IAgentConfigurator.sol"
    chaos_range_interface = chaos_agents_root / "src/interfaces/IRangeValidationModule.sol"
    chaos_oracle_interface = chaos_agents_root / "src/contracts/dependencies/IRiskOracle.sol"
    proposal_hub_interface = proposals_root / "src/interfaces/IAgentConfigurator.sol"
    source_paths = [
        hub_interface,
        range_interface,
        oracle_interface,
        agent_hub_root / "src/contracts/AgentHub.sol",
        agent_hub_root / "src/contracts/AgentConfigurator.sol",
        agent_hub_root / "src/contracts/modules/RangeValidationModule.sol",
        risk_agents_root / "src/contracts/agent/BaseAaveAgent.sol",
        risk_agents_root / "src/contracts/agent/AaveBorrowCapAgent.sol",
        risk_agents_root / "src/contracts/agent/AaveSupplyCapAgent.sol",
        risk_agents_root / "src/contracts/agent/AaveRatesAgent.sol",
        risk_agents_root / "src/contracts/agent/AaveEModeAgent.sol",
        risk_agents_root / "src/contracts/agent/AaveDiscountRateAgent.sol",
        risk_agents_root / "src/contracts/agent/AaveCapoAgent.sol",
        chaos_hub_interface,
        chaos_range_interface,
        chaos_oracle_interface,
        proposal_hub_interface,
    ]
    missing_paths = [str(path) for path in source_paths if not path.is_file()]
    if missing_paths:
        raise RuntimeError(f"pinned source files are missing: {missing_paths}")

    if hub_interface.read_bytes() != chaos_hub_interface.read_bytes():
        raise RuntimeError("Aave Agent Hub and pinned Chaos Agent Hub interfaces differ")
    if range_interface.read_bytes() != chaos_range_interface.read_bytes():
        raise RuntimeError("Aave and Chaos range-validation interfaces differ")
    if oracle_interface.read_bytes() != chaos_oracle_interface.read_bytes():
        raise RuntimeError("Aave and Chaos RiskOracle interfaces differ")
    if hub_interface.read_bytes() != proposal_hub_interface.read_bytes():
        raise RuntimeError("proposal and deployed Agent Hub interfaces differ")

    hub_definitions = extract_solidity_event_definitions(hub_interface.read_text(encoding="utf-8"))
    missing_hub = sorted(HUB_SIGNATURES - set(hub_definitions))
    if missing_hub:
        raise RuntimeError(f"frozen AgentHub signatures absent from source: {missing_hub}")
    oracle_definitions = extract_solidity_event_definitions(oracle_interface.read_text(encoding="utf-8"))
    if RISK_ORACLE_SIGNATURE not in oracle_definitions:
        raise RuntimeError("frozen ParameterUpdated signature is absent from source")
    range_source = range_interface.read_text(encoding="utf-8")
    required_range_fragments = {
        "event DefaultRangeConfigSet(",
        "event MarketRangeConfigSet(",
        "uint120 maxIncrease",
        "uint120 maxDecrease",
        "bool isIncreaseRelative",
        "bool isDecreaseRelative",
    }
    missing_fragments = sorted(
        fragment for fragment in required_range_fragments if fragment not in range_source
    )
    if missing_fragments:
        raise RuntimeError(f"range ABI source is incomplete: {missing_fragments}")

    submodule_status = _git("submodule", "status", root=risk_agents_root)
    expected_submodule = str(official["chaos_agents"]["expected_git_sha"])
    if (
        re.search(rf"[ -]{re.escape(expected_submodule)}\s+lib/chaos-agents(?:\s|$)", submodule_status)
        is None
    ):
        raise RuntimeError("Risk Agents does not pin the frozen Chaos Agents submodule")

    address_book_path = address_book_root / str(official["address_book"]["ethereum_path"])
    address_book_source = address_book_path.read_text(encoding="utf-8").lower()
    frozen_addresses = [
        normalize_address(str(config["ethereum"]["agent_hub"])),
        normalize_address(str(config["ethereum"]["range_validation_module"])),
    ]
    absent_addresses = [address for address in frozen_addresses if address[2:] not in address_book_source]
    if absent_addresses:
        raise RuntimeError(f"frozen addresses absent from address book: {absent_addresses}")

    source_roots = {
        "agent_hub": agent_hub_root,
        "risk_agents": risk_agents_root,
        "chaos_agents": chaos_agents_root,
        "proposals_repository": proposals_root,
    }
    source_digests: dict[str, str] = {}
    for path in source_paths:
        matches = [
            (label, path.relative_to(root))
            for label, root in source_roots.items()
            if path.is_relative_to(root)
        ]
        if len(matches) != 1:
            raise RuntimeError(f"cannot assign a unique source repository to {path}")
        label, relative_path = matches[0]
        source_digests[f"{label}/{relative_path}"] = _sha256_file(path)

    return {
        "repositories": repositories,
        "source_file_sha256": dict(sorted(source_digests.items())),
        "address_book_file_sha256": _sha256_file(address_book_path),
        "agent_hub_and_chaos_interfaces_identical": True,
        "proposal_and_deployed_hub_interfaces_identical": True,
        "risk_agents_chaos_submodule_sha": expected_submodule,
        "event_signatures": {
            "agent_hub": sorted(HUB_SIGNATURES),
            "range_validation_module": sorted(RANGE_SIGNATURES),
            "risk_oracle": [RISK_ORACLE_SIGNATURE],
        },
    }


def _base_log(raw: Mapping[str, Any], *, expected_address: str) -> dict[str, Any]:
    if raw.get("removed") is True:
        raise ValueError("removed log is forbidden in the formal D0 audit")
    address = normalize_address(str(raw.get("address")))
    if address != normalize_address(expected_address):
        raise ValueError(f"RPC returned a log from unexpected address {address}")
    topics = raw.get("topics")
    if not isinstance(topics, Sequence) or isinstance(topics, (str, bytes)):
        raise ValueError("log topics must be a sequence")
    return {
        "contract_address": address,
        "block_number": _hex_quantity(raw.get("blockNumber"), field="blockNumber"),
        "block_hash": _hash(str(raw.get("blockHash")), field="blockHash"),
        "transaction_hash": _hash(str(raw.get("transactionHash")), field="transactionHash"),
        "transaction_index": _hex_quantity(raw.get("transactionIndex"), field="transactionIndex"),
        "log_index": _hex_quantity(raw.get("logIndex"), field="logIndex"),
        "topics": [normalize_topic(str(topic)) for topic in topics],
        "data": normalize_hex_data(str(raw.get("data"))),
    }


def _expect_shape(base: Mapping[str, Any], *, topics: int, empty_data: bool) -> None:
    if len(base["topics"]) != topics:
        raise ValueError(f"event has {len(base['topics'])} topics, expected {topics}")
    if empty_data and base["data"] != "0x":
        raise ValueError("all-indexed event unexpectedly contains data")


def _strip_raw(base: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in base.items() if key not in {"topics", "data"}}


def _decode_hub_log(
    raw: Mapping[str, Any],
    *,
    hub_address: str,
    signatures_by_topic: Mapping[str, str],
) -> dict[str, Any]:
    base = _base_log(raw, expected_address=hub_address)
    signature = signatures_by_topic.get(base["topics"][0])
    if signature is None:
        raise ValueError("unexpected AgentHub event topic")
    event_name = signature.split("(", 1)[0]
    result = {**_strip_raw(base), "event_name": event_name}
    topics = base["topics"]
    if event_name == "UpdateInjected":
        _expect_shape(base, topics=4, empty_data=False)
        result.update(
            {
                "agent_id": uint_from_topic(topics[1]),
                "market": address_from_topic(topics[2]),
                "update_type_hash": topics[3],
                **decode_update_injected_data(base["data"]),
            }
        )
        return result

    _expect_shape(base, topics=3 if event_name != "AgentRegistered" else 4, empty_data=True)
    result["agent_id"] = uint_from_topic(topics[1])
    if event_name == "AgentRegistered":
        result["risk_oracle"] = address_from_topic(topics[2])
        result["update_type_hash"] = topics[3]
    elif event_name == "AgentAddressSet":
        result["agent_address"] = address_from_topic(topics[2])
    elif event_name == "AgentAdminSet":
        result["agent_admin"] = address_from_topic(topics[2])
    elif event_name == "AgentPermissionedStatusSet":
        result["is_permissioned"] = bool_from_topic(topics[2])
    elif event_name == "AgentEnabledSet":
        result["enabled"] = bool_from_topic(topics[2])
    elif event_name == "MarketsFromAgentEnabled":
        result["markets_from_agent_enabled"] = bool_from_topic(topics[2])
    elif event_name == "ExpirationPeriodSet":
        result["expiration_period"] = uint_from_topic(topics[2])
    elif event_name == "MinimumDelaySet":
        result["minimum_delay"] = uint_from_topic(topics[2])
    elif event_name == "AgentContextSet":
        result["agent_context_hash"] = topics[2]
    elif event_name in {"AllowedMarketAdded", "AllowedMarketRemoved"}:
        result["market"] = address_from_topic(topics[2])
        result["allowed"] = event_name == "AllowedMarketAdded"
    elif event_name in {"RestrictedMarketAdded", "RestrictedMarketRemoved"}:
        result["market"] = address_from_topic(topics[2])
        result["restricted"] = event_name == "RestrictedMarketAdded"
    else:
        raise ValueError(f"unhandled AgentHub event {event_name}")
    return result


def _decode_range_log(
    raw: Mapping[str, Any],
    *,
    module_address: str,
    hub_address: str,
    signatures_by_topic: Mapping[str, str],
) -> dict[str, Any]:
    base = _base_log(raw, expected_address=module_address)
    signature = signatures_by_topic.get(base["topics"][0])
    if signature is None:
        raise ValueError("unexpected range-validation event topic")
    _expect_shape(base, topics=4, empty_data=False)
    topics = base["topics"]
    if address_from_topic(topics[1]) != normalize_address(hub_address):
        raise ValueError("range event belongs to another AgentHub")
    event_name = signature.split("(", 1)[0]
    result = {
        **_strip_raw(base),
        "event_name": event_name,
        "agent_hub": normalize_address(hub_address),
        "agent_id": uint_from_topic(topics[2]),
    }
    if event_name == "DefaultRangeConfigSet":
        result["update_type_hash"] = topics[3]
        result["range_config"] = decode_default_range_config_data(base["data"])
    elif event_name == "MarketRangeConfigSet":
        decoded = decode_market_range_config_data(base["data"])
        update_type = str(decoded["update_type"])
        result["market"] = address_from_topic(topics[3])
        result["update_type"] = update_type
        result["update_type_hash"] = _keccak_topic(update_type)
        result["range_config"] = decoded["range_config"]
    else:
        raise ValueError(f"unhandled range event {event_name}")
    return result


def _decode_proposal_log(
    raw: Mapping[str, Any],
    *,
    oracle_addresses: set[str],
    expected_topic: str,
) -> dict[str, Any]:
    observed_address = normalize_address(str(raw.get("address")))
    if observed_address not in oracle_addresses:
        raise ValueError("proposal came from an unregistered Risk Oracle")
    base = _base_log(raw, expected_address=observed_address)
    if base["topics"][0] != expected_topic:
        raise ValueError("unexpected Risk Oracle event topic")
    _expect_shape(base, topics=4, empty_data=False)
    decoded = decode_parameter_updated_data(base["data"])
    return {
        **_strip_raw(base),
        "event_name": "ParameterUpdated",
        "risk_oracle": observed_address,
        "update_type_hash": base["topics"][1],
        "update_id": uint_from_topic(base["topics"][2]),
        "market": address_from_topic(base["topics"][3]),
        **decoded,
        "previous_value_is_prior_oracle_proposal_not_protocol_state": True,
    }


def _query_logs(
    client: _RpcClient,
    *,
    addresses: Sequence[str],
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    maximum_span: int,
    maximum_topics_per_query: int,
) -> list[Mapping[str, Any]]:
    if not addresses or not topics:
        return []
    if maximum_topics_per_query <= 0:
        raise ValueError("maximum topics per query must be positive")
    topic_groups = [
        topics[index : index + maximum_topics_per_query]
        for index in range(0, len(topics), maximum_topics_per_query)
    ]
    logs: list[Mapping[str, Any]] = []
    start = from_block
    while start <= to_block:
        end = min(to_block, start + maximum_span - 1)
        for topic_group in topic_groups:
            logs.extend(
                _get_logs_with_split(
                    client,
                    addresses=addresses,
                    topics=topic_group,
                    start_block=start,
                    end_block_inclusive=end,
                    remaining_split_depth=20,
                    split_topics_first=True,
                )
            )
        start = end + 1
    identities: set[tuple[str, str, int]] = set()
    for raw in logs:
        identity = (
            _hash(str(raw.get("blockHash")), field="blockHash"),
            _hash(str(raw.get("transactionHash")), field="transactionHash"),
            _hex_quantity(raw.get("logIndex"), field="logIndex"),
        )
        if identity in identities:
            raise ValueError("duplicate log returned across D0 RPC chunks")
        identities.add(identity)
        block_number = _hex_quantity(raw.get("blockNumber"), field="blockNumber")
        if not from_block <= block_number <= to_block:
            raise ValueError("RPC returned a log outside the frozen block interval")
    return logs


def _query_decoded_stage(
    client: _RpcClient,
    *,
    stage: str,
    state: dict[str, Any],
    addresses: Sequence[str],
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    maximum_span: int,
    maximum_topics_per_query: int,
    decoder: Callable[[Mapping[str, Any]], dict[str, Any]],
    save_checkpoint: Callable[[], None],
) -> list[dict[str, Any]]:
    completed = state["completed_through"]
    event_groups = state["events"]
    stage_events = cast(list[dict[str, Any]], event_groups[stage])
    identities = {
        (
            str(event["block_hash"]),
            str(event["transaction_hash"]),
            int(event["log_index"]),
        )
        for event in stage_events
    }
    start = max(from_block, int(completed[stage]) + 1)
    while start <= to_block:
        end = min(to_block, start + maximum_span - 1)
        raw_logs = _query_logs(
            client,
            addresses=addresses,
            topics=topics,
            from_block=start,
            to_block=end,
            maximum_span=maximum_span,
            maximum_topics_per_query=maximum_topics_per_query,
        )
        for raw in raw_logs:
            decoded = decoder(raw)
            identity = (
                str(decoded["block_hash"]),
                str(decoded["transaction_hash"]),
                int(decoded["log_index"]),
            )
            if identity in identities:
                raise ValueError(f"duplicate decoded {stage} event across checkpoint shards")
            identities.add(identity)
            stage_events.append(decoded)
        stage_events.sort(key=event_position)
        completed[stage] = end
        save_checkpoint()
        start = end + 1
    return stage_events


def _attach_block_timestamps(
    client: _RpcClient,
    event_groups: Sequence[list[dict[str, Any]]],
    *,
    header_cache: dict[str, Any],
    save_checkpoint: Callable[[], None],
) -> int:
    events = [event for group in event_groups for event in group]
    block_numbers = sorted({int(event["block_number"]) for event in events})
    for number in block_numbers:
        key = str(number)
        if key not in header_cache:
            header_cache[key] = client.block(number)
            save_checkpoint()
        header = header_cache[key]
        if int(header["number"]) != number:
            raise RuntimeError(f"checkpoint header number mismatch at {number}")
        for event in events:
            if int(event["block_number"]) != number:
                continue
            if str(event["block_hash"]) != str(header["hash"]):
                raise RuntimeError(f"event block hash mismatch at {number}")
            event["block_timestamp"] = int(header["timestamp"])
            event["block_utc"] = _utc(int(header["timestamp"]))
    save_checkpoint()
    return len(block_numbers)


def audit(
    config_path: Path,
    *,
    agent_hub_root: Path,
    risk_agents_root: Path,
    chaos_agents_root: Path,
    address_book_root: Path,
    proposals_root: Path,
    output_path: Path,
    checkpoint_path: Path,
) -> dict[str, Any]:
    """Execute D0 without reading market behavior or protocol outcome state."""
    if _git("status", "--porcelain"):
        raise RuntimeError("formal Aave guardrail D0 requires a clean EcoPhys worktree")
    if checkpoint_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("formal D0 checkpoint must remain outside the repository")
    config = _load_yaml(config_path)
    if str(config["contract"]["status"]) != (
        "frozen_before_risk_oracle_proposal_values_or_execution_matching"
    ):
        raise RuntimeError("D0 contract does not carry the required pre-value freeze status")
    source_audit = _source_audit(
        config,
        agent_hub_root=agent_hub_root,
        risk_agents_root=risk_agents_root,
        chaos_agents_root=chaos_agents_root,
        address_book_root=address_book_root,
        proposals_root=proposals_root,
    )

    transport = config["transport"]
    client = _RpcClient(
        url=str(transport["formal_rpc"]),
        timeout=60,
        transport_retries=3,
        minimum_request_interval_seconds=float(transport["minimum_request_interval_seconds"]),
        rate_limit_retries=int(transport["rate_limit_retries"]),
        rate_limit_backoff_initial_seconds=float(transport["rate_limit_backoff_initial_seconds"]),
        rate_limit_backoff_max_seconds=float(transport["rate_limit_backoff_max_seconds"]),
    )
    if client.call("eth_chainId", []) != hex(int(config["ethereum"]["chain_id"])):
        raise RuntimeError("formal D0 RPC is not the frozen chain")
    if _keccak_topic("Transfer(address,address,uint256)") != (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ):
        raise RuntimeError("local Keccak-256 failed the ERC-20 event vector")

    ethereum = config["ethereum"]
    from_block = int(ethereum["from_block"])
    to_block = int(ethereum["to_block"])
    end_header = client.block(to_block)
    if str(end_header["hash"]) != str(ethereum["to_block_hash"]).lower():
        raise RuntimeError("frozen D0 end block hash changed")
    hub_address = normalize_address(str(ethereum["agent_hub"]))
    range_address = normalize_address(str(ethereum["range_validation_module"]))
    hub_by_topic = {_keccak_topic(signature): signature for signature in HUB_SIGNATURES}
    range_by_topic = {_keccak_topic(signature): signature for signature in RANGE_SIGNATURES}
    risk_topic = _keccak_topic(RISK_ORACLE_SIGNATURE)
    maximum_span = int(transport["maximum_get_logs_span"])
    maximum_topics_per_query = int(transport["maximum_topics_per_get_logs"])
    checkpoint_identity = {
        "repository_sha": _git("rev-parse", "HEAD"),
        "config_sha256": _sha256_file(config_path),
        "formal_rpc": str(transport["formal_rpc"]),
        "chain_id": int(ethereum["chain_id"]),
        "from_block": from_block,
        "to_block": to_block,
        "to_block_hash": str(ethereum["to_block_hash"]).lower(),
        "source_repository_shas": {
            label: str(record["git_sha"]) for label, record in source_audit["repositories"].items()
        },
    }
    checkpoint_state, resumed_from_checkpoint = _load_checkpoint(
        checkpoint_path,
        identity=checkpoint_identity,
        from_block=from_block,
    )

    def save_checkpoint() -> None:
        _write_checkpoint(
            checkpoint_path,
            identity=checkpoint_identity,
            state=checkpoint_state,
        )

    hub_events = _query_decoded_stage(
        client,
        stage="hub",
        state=checkpoint_state,
        addresses=[hub_address],
        topics=sorted(hub_by_topic),
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        maximum_topics_per_query=maximum_topics_per_query,
        decoder=lambda raw: _decode_hub_log(
            raw,
            hub_address=hub_address,
            signatures_by_topic=hub_by_topic,
        ),
        save_checkpoint=save_checkpoint,
    )
    registrations = [event for event in hub_events if event["event_name"] == "AgentRegistered"]
    oracle_addresses = {str(event["risk_oracle"]) for event in registrations}
    if not oracle_addresses:
        raise RuntimeError("no Risk Oracle was discovered from AgentRegistered events")

    range_events = _query_decoded_stage(
        client,
        stage="range",
        state=checkpoint_state,
        addresses=[range_address],
        topics=sorted(range_by_topic),
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        maximum_topics_per_query=maximum_topics_per_query,
        decoder=lambda raw: _decode_range_log(
            raw,
            module_address=range_address,
            hub_address=hub_address,
            signatures_by_topic=range_by_topic,
        ),
        save_checkpoint=save_checkpoint,
    )
    proposals = _query_decoded_stage(
        client,
        stage="proposals",
        state=checkpoint_state,
        addresses=sorted(oracle_addresses),
        topics=[risk_topic],
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        maximum_topics_per_query=maximum_topics_per_query,
        decoder=lambda raw: _decode_proposal_log(
            raw,
            oracle_addresses=oracle_addresses,
            expected_topic=risk_topic,
        ),
        save_checkpoint=save_checkpoint,
    )
    unique_header_count = _attach_block_timestamps(
        client,
        [hub_events, range_events, proposals],
        header_cache=checkpoint_state["block_headers"],
        save_checkpoint=save_checkpoint,
    )
    if any(int(proposal["oracle_timestamp"]) != int(proposal["block_timestamp"]) for proposal in proposals):
        raise RuntimeError("Risk Oracle timestamp differs from its canonical block timestamp")

    ledger = build_action_ledger(
        hub_events,
        proposals,
        end_timestamp=int(end_header["timestamp"]),
    )
    support = assess_action_support(
        ledger,
        registrations,
        config["pass_thresholds"],
    )
    decision = (
        "pass_to_separately_frozen_d1_exact_validation_replay"
        if support["passed"]
        else "stop_threshold_causal_route_before_market_outcomes"
    )
    result: dict[str, Any] = {
        "schema_version": 1,
        "contract_name": str(config["contract"]["name"]),
        "contract_version": int(config["contract"]["version"]),
        "decision": decision,
        "repository": {
            "git_sha": _git("rev-parse", "HEAD"),
            "clean_worktree_at_start": True,
            "config_path": str(config_path.relative_to(REPO_ROOT)),
            "config_sha256": _sha256_file(config_path),
        },
        "source_audit": source_audit,
        "ethereum": {
            "chain_id": int(ethereum["chain_id"]),
            "from_block": from_block,
            "to_block": to_block,
            "to_block_hash": str(end_header["hash"]),
            "to_block_timestamp": int(end_header["timestamp"]),
            "to_block_utc": _utc(int(end_header["timestamp"])),
            "agent_hub": hub_address,
            "range_validation_module": range_address,
            "risk_oracles_discovered_from_registration": sorted(oracle_addresses),
        },
        "event_topics": {
            "agent_hub": dict(sorted(hub_by_topic.items())),
            "range_validation_module": dict(sorted(range_by_topic.items())),
            "risk_oracle": {risk_topic: RISK_ORACLE_SIGNATURE},
        },
        "action_surface": {
            "agent_hub_event_count": len(hub_events),
            "registration_count": len(registrations),
            "injection_event_count": sum(event["event_name"] == "UpdateInjected" for event in hub_events),
            "range_configuration_event_count": len(range_events),
            "proposal_event_count": len(proposals),
            "unique_event_block_header_count": unique_header_count,
            "hub_events": hub_events,
            "range_configuration_events": range_events,
            "proposal_ledger": ledger,
            "raw_rpc_responses_persisted": False,
        },
        "support_gate": support,
        "transport": {
            "formal_rpc": str(transport["formal_rpc"]),
            "maximum_get_logs_span": maximum_span,
            "maximum_topics_per_get_logs": maximum_topics_per_query,
            "preformal_identity_crosschecks": transport["preformal_identity_crosschecks"],
            "rpc_request_counts": dict(sorted(client.method_counts.items())),
            "log_range_splits": client.log_range_splits,
            "log_topic_splits": client.log_topic_splits,
            "rate_limit_retry_count": client.rate_limit_retry_count,
            "rate_limit_wait_seconds": round(client.rate_limit_wait_seconds, 3),
            "server_error_retry_count": client.server_error_retry_count,
            "server_error_wait_seconds": round(client.server_error_wait_seconds, 3),
        },
        "checkpoint": {
            "resumed_from_decoded_event_checkpoint": resumed_from_checkpoint,
            "checkpoint_outside_repository": not checkpoint_path.is_relative_to(REPO_ROOT),
            "checkpoint_contains_raw_rpc_or_market_outcomes": False,
            "checkpoint_removed_after_success": True,
        },
        "blinding": {
            "only_configuration_proposal_injection_events_and_headers_queried": True,
            "pool_balances_utilization_rates_positions_prices_liquidations_queried": False,
            "user_transactions_or_market_response_windows_queried": False,
            "risk_oracle_previous_value_used_as_protocol_state": False,
            "raw_rpc_responses_retained": False,
        },
        "compute": {
            "cpu_only": True,
            "gpu_used": False,
            "paid_data_used": False,
            "ecomd_used": False,
        },
    }
    result["canonical_payload_sha256"] = canonical_sha256(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output_path)
    checkpoint_path.unlink(missing_ok=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--agent-hub-root", type=Path, required=True)
    parser.add_argument("--risk-agents-root", type=Path, required=True)
    parser.add_argument("--chaos-agents-root", type=Path, required=True)
    parser.add_argument("--address-book-root", type=Path, required=True)
    parser.add_argument("--proposals-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    result = audit(
        args.config.resolve(),
        agent_hub_root=args.agent_hub_root.resolve(),
        risk_agents_root=args.risk_agents_root.resolve(),
        chaos_agents_root=args.chaos_agents_root.resolve(),
        address_book_root=args.address_book_root.resolve(),
        proposals_root=args.proposals_root.resolve(),
        output_path=args.output.resolve(),
        checkpoint_path=args.checkpoint.resolve(),
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "proposals": result["support_gate"]["proposal_count"],
                "exact_injections": result["support_gate"]["exact_injection_count"],
                "registered_agents": result["support_gate"]["registered_agent_count"],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
