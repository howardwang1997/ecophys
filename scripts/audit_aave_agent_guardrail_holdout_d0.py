"""Run or merge the frozen multichain Aave agent-guardrail holdout D0."""

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
    assess_holdout_action_support,
    assign_action_batches,
    build_holdout_chain_ledger,
    event_position,
)
from ecomd.data.aave_qualification import (
    canonical_sha256,
    extract_solidity_event_definitions,
    normalize_address,
)
from scripts.audit_aave_agent_guardrail_d0 import (
    HUB_SIGNATURES,
    RANGE_SIGNATURES,
    RISK_ORACLE_SIGNATURE,
    _decode_hub_log,
    _decode_proposal_log,
    _decode_range_log,
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


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML contract must be an object: {path}")
    return payload


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_pilot_binding(config: Mapping[str, Any]) -> dict[str, Any]:
    binding = config["pilot_binding"]
    relative_path = Path(str(binding["result_path"]))
    result_path = (REPO_ROOT / relative_path).resolve()
    if not result_path.is_relative_to(REPO_ROOT) or not result_path.is_file():
        raise RuntimeError("frozen Ethereum pilot artifact is absent or outside the repository")
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("frozen Ethereum pilot artifact is not an object")
    stored = str(payload.get("canonical_payload_sha256", ""))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    expected = str(binding["canonical_payload_sha256"])
    if stored != expected or canonical_sha256(body) != expected:
        raise RuntimeError("frozen Ethereum pilot digest differs from the holdout binding")
    if payload.get("decision") != binding["decision"]:
        raise RuntimeError("frozen Ethereum pilot decision differs from the holdout binding")
    if binding.get("pilot_cannot_be_reclassified_or_pooled_into_holdout") is not True:
        raise RuntimeError("holdout does not explicitly exclude the Ethereum pilot")
    return {
        "result_path": str(relative_path),
        "canonical_payload_sha256": expected,
        "decision": str(binding["decision"]),
        "diagnostic_used_for_design_only": str(binding["diagnostic_used_for_design_only"]),
        "verified_against_repository_artifact": True,
        "excluded_from_all_holdout_counts": True,
    }


def _utc(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


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
    chaos_hub = chaos_agents_root / "src/interfaces/IAgentConfigurator.sol"
    chaos_range = chaos_agents_root / "src/interfaces/IRangeValidationModule.sol"
    chaos_oracle = chaos_agents_root / "src/contracts/dependencies/IRiskOracle.sol"
    proposal_hub = proposals_root / "src/interfaces/IAgentConfigurator.sol"
    deploy_script = risk_agents_root / str(official["risk_agents"]["deployment_script"])
    source_paths = [
        hub_interface,
        range_interface,
        oracle_interface,
        chaos_hub,
        chaos_range,
        chaos_oracle,
        proposal_hub,
        deploy_script,
    ]
    if any(not path.is_file() for path in source_paths):
        raise RuntimeError("a pinned holdout source file is missing")
    if (
        hub_interface.read_bytes() != chaos_hub.read_bytes()
        or hub_interface.read_bytes() != proposal_hub.read_bytes()
    ):
        raise RuntimeError("pinned AgentHub interfaces differ")
    if range_interface.read_bytes() != chaos_range.read_bytes():
        raise RuntimeError("pinned range-validation interfaces differ")
    if oracle_interface.read_bytes() != chaos_oracle.read_bytes():
        raise RuntimeError("pinned Risk Oracle interfaces differ")
    hub_events = extract_solidity_event_definitions(hub_interface.read_text(encoding="utf-8"))
    if not HUB_SIGNATURES.issubset(hub_events):
        raise RuntimeError("pinned AgentHub source lacks a frozen event")
    oracle_events = extract_solidity_event_definitions(oracle_interface.read_text(encoding="utf-8"))
    if RISK_ORACLE_SIGNATURE not in oracle_events:
        raise RuntimeError("pinned Risk Oracle source lacks ParameterUpdated")
    range_source = range_interface.read_text(encoding="utf-8")
    if any(name not in range_source for name in ("DefaultRangeConfigSet", "MarketRangeConfigSet")):
        raise RuntimeError("pinned range source lacks a frozen event")
    expected_submodule = str(official["chaos_agents"]["expected_git_sha"])
    submodule_status = _git("submodule", "status", root=risk_agents_root)
    if (
        re.search(rf"[ -]{re.escape(expected_submodule)}\s+lib/chaos-agents(?:\s|$)", submodule_status)
        is None
    ):
        raise RuntimeError("Risk Agents does not pin the frozen Chaos Agents source")

    deploy_source = deploy_script.read_text(encoding="utf-8")
    address_paths: list[Path] = []
    chain_source_checks: dict[str, Any] = {}
    for chain_name, raw_chain in sorted(config["chains"].items()):
        chain = dict(raw_chain)
        misc_module, market_module = [str(value) for value in chain["address_book_modules"]]
        suffix = misc_module.removeprefix("Misc")
        marker = f"contract Deploy{suffix} "
        start = deploy_source.find(marker)
        if start < 0:
            raise RuntimeError(f"deployment contract is absent for {chain_name}")
        next_marker = deploy_source.find("// make deploy-ledger", start + len(marker))
        section = deploy_source[start : next_marker if next_marker >= 0 else len(deploy_source)]
        observed_helpers = set(re.findall(r"(Deploy[A-Za-z0-9]+Agent)\.deploy\(", section))
        expected_helpers = {
            "Deploy" + str(agent_type).removeprefix("Aave") for agent_type in chain["expected_agent_types"]
        }
        if observed_helpers != expected_helpers:
            raise RuntimeError(
                f"{chain_name} deployed agent helpers differ: {observed_helpers} != {expected_helpers}"
            )
        misc_path = address_book_root / f"src/ts/{misc_module}.ts"
        market_path = address_book_root / f"src/ts/{market_module}.ts"
        if not misc_path.is_file() or not market_path.is_file():
            raise RuntimeError(f"address-book module is absent for {chain_name}")
        address_paths.extend([misc_path, market_path])
        misc_source = misc_path.read_text(encoding="utf-8")
        market_source = market_path.read_text(encoding="utf-8")
        required_misc = [
            str(chain["agent_hub"]),
            str(chain["range_validation_module"]),
            f"export const CHAIN_ID = {int(chain['chain_id'])};",
        ]
        required_market = [
            str(chain["edge_risk_oracle"]),
            f"export const CHAIN_ID = {int(chain['chain_id'])};",
        ]
        if any(fragment.lower() not in misc_source.lower() for fragment in required_misc):
            raise RuntimeError(f"{chain_name} misc address-book binding failed")
        if any(fragment.lower() not in market_source.lower() for fragment in required_market):
            raise RuntimeError(f"{chain_name} market address-book binding failed")
        chain_source_checks[chain_name] = {
            "deployment_contract": f"Deploy{suffix}",
            "deployment_helpers": sorted(observed_helpers),
            "misc_module": misc_module,
            "market_module": market_module,
            "addresses_and_chain_id_present": True,
        }

    roots = {
        "agent_hub": agent_hub_root,
        "risk_agents": risk_agents_root,
        "chaos_agents": chaos_agents_root,
        "proposals_repository": proposals_root,
        "address_book": address_book_root,
    }
    digests: dict[str, str] = {}
    for path in [*source_paths, *address_paths]:
        matches = [
            (label, path.relative_to(root)) for label, root in roots.items() if path.is_relative_to(root)
        ]
        if len(matches) != 1:
            raise RuntimeError(f"cannot assign pinned source path {path}")
        label, relative = matches[0]
        digests[f"{label}/{relative}"] = _sha256_file(path)
    return {
        "repositories": repositories,
        "source_file_sha256": dict(sorted(digests.items())),
        "risk_agents_chaos_submodule_sha": expected_submodule,
        "interfaces_identical": True,
        "chain_source_checks": chain_source_checks,
        "event_signatures": {
            "agent_hub": sorted(HUB_SIGNATURES),
            "range_validation_module": sorted(RANGE_SIGNATURES),
            "risk_oracle": [RISK_ORACLE_SIGNATURE],
        },
    }


def _new_client(url: str, *, minimum_interval: float) -> _RpcClient:
    return _RpcClient(
        url=url,
        timeout=60,
        transport_retries=3,
        minimum_request_interval_seconds=minimum_interval,
        rate_limit_retries=5,
        rate_limit_backoff_initial_seconds=2,
        rate_limit_backoff_max_seconds=30,
    )


def _canonical_log_identities(logs: Sequence[Mapping[str, Any]]) -> list[tuple[str, str, int]]:
    identities = sorted(
        (
            _hash(str(log.get("blockHash")), field="blockHash"),
            _hash(str(log.get("transactionHash")), field="transactionHash"),
            _hex_quantity(log.get("logIndex"), field="logIndex"),
        )
        for log in logs
    )
    if len(identities) != len(set(identities)):
        raise ValueError("RPC returned duplicate canonical log identities")
    return identities


def _query_logs_interval(
    client: _RpcClient,
    *,
    addresses: Sequence[str],
    topics: Sequence[str],
    start_block: int,
    end_block: int,
    maximum_topics_per_query: int,
) -> list[Mapping[str, Any]]:
    topic_groups = [
        topics[index : index + maximum_topics_per_query]
        for index in range(0, len(topics), maximum_topics_per_query)
    ]
    logs: list[Mapping[str, Any]] = []
    for topic_group in topic_groups:
        logs.extend(
            _get_logs_with_split(
                client,
                addresses=addresses,
                topics=topic_group,
                start_block=start_block,
                end_block_inclusive=end_block,
                remaining_split_depth=24,
                split_topics_first=False,
            )
        )
    identities = _canonical_log_identities(logs)
    if len(identities) != len(logs):
        raise AssertionError("canonical identity validation did not preserve log count")
    for log in logs:
        block_number = _hex_quantity(log.get("blockNumber"), field="blockNumber")
        if not start_block <= block_number <= end_block:
            raise ValueError("RPC returned a log outside the requested interval")
    return logs


def _validate_transport_anchor(
    client: _RpcClient,
    *,
    chain: Mapping[str, Any],
    require_contract_code: bool = True,
) -> None:
    if client.call("eth_chainId", []) != hex(int(chain["chain_id"])):
        raise RuntimeError("RPC chain ID differs from the frozen chain")
    for prefix in ("from", "to"):
        header = client.block(int(chain[f"{prefix}_block"]))
        if str(header["hash"]) != str(chain[f"{prefix}_block_hash"]).lower():
            raise RuntimeError(f"RPC {prefix}-anchor block hash differs")
    if require_contract_code:
        code = client.call(
            "eth_getCode", [normalize_address(str(chain["agent_hub"])), hex(int(chain["to_block"]))]
        )
        if (
            not isinstance(code, str)
            or re.fullmatch(r"0x(?:[0-9a-fA-F]{2})+", code) is None
            or int(code[2:], 16) == 0
        ):
            raise RuntimeError("AgentHub code is absent at the frozen endpoint")


def _first_nonempty_hub_shard(
    client: _RpcClient,
    *,
    chain: Mapping[str, Any],
    hub_topics: Sequence[str],
    span: int,
    maximum_topics_per_query: int,
) -> tuple[int, int, list[Mapping[str, Any]]]:
    start = int(chain["from_block"])
    to_block = int(chain["to_block"])
    while start <= to_block:
        end = min(to_block, start + span - 1)
        logs = _query_logs_interval(
            client,
            addresses=[normalize_address(str(chain["agent_hub"]))],
            topics=hub_topics,
            start_block=start,
            end_block=end,
            maximum_topics_per_query=maximum_topics_per_query,
        )
        if logs:
            return start, end, logs
        start = end + 1
    raise RuntimeError("no nonempty AgentHub qualification shard exists in the frozen interval")


def _qualify_state_witness(
    *,
    chain: Mapping[str, Any],
    candidate_urls: Sequence[str],
    minimum_interval: float,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for url in dict.fromkeys(candidate_urls):
        try:
            client = _new_client(url, minimum_interval=minimum_interval)
            _validate_transport_anchor(client, chain=chain, require_contract_code=True)
            return {
                "state_witness_rpc": url,
                "frozen_endpoint_agent_hub_code_verified": True,
                "request_counts": dict(sorted(client.method_counts.items())),
                "failed_candidates_before_success": failures,
            }
        except Exception as error:
            failures.append(
                {
                    "rpc": url,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
    raise RuntimeError(f"no frozen state-witness transport qualified: {failures}")


def _qualify_transport(
    config: Mapping[str, Any],
    *,
    chain: Mapping[str, Any],
    preferred_rpc_index: int,
    hub_topics: Sequence[str],
) -> tuple[_RpcClient, dict[str, Any]]:
    candidates = [str(url) for url in chain["formal_rpc_candidates"]]
    if not 0 <= preferred_rpc_index < len(candidates):
        raise ValueError("preferred RPC index is outside the frozen candidate list")
    ordered_indices = [preferred_rpc_index] + [
        index for index in range(len(candidates)) if index != preferred_rpc_index
    ]
    interval = float(config["transport"]["minimum_request_interval_seconds_per_endpoint"])
    qualification_span = int(config["transport"]["qualification_get_logs_span"])
    maximum_topics = int(config["transport"]["maximum_topics_per_get_logs"])
    anchor_url = str(chain["anchor_rpc"])
    anchor = _new_client(anchor_url, minimum_interval=interval)
    _validate_transport_anchor(anchor, chain=chain, require_contract_code=False)
    state_witness = _qualify_state_witness(
        chain=chain,
        candidate_urls=[anchor_url, *candidates],
        minimum_interval=interval,
    )
    failures: list[dict[str, Any]] = []
    for primary_index in ordered_indices:
        primary_url = candidates[primary_index]
        try:
            primary = _new_client(primary_url, minimum_interval=interval)
            _validate_transport_anchor(primary, chain=chain, require_contract_code=False)
            start, end, primary_logs = _first_nonempty_hub_shard(
                primary,
                chain=chain,
                hub_topics=hub_topics,
                span=qualification_span,
                maximum_topics_per_query=maximum_topics,
            )
            primary_identities = _canonical_log_identities(primary_logs)
        except Exception as error:
            failures.append(
                {
                    "rpc": primary_url,
                    "role": "primary",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
            continue
        for reference_index in ordered_indices:
            if reference_index == primary_index:
                continue
            reference_url = candidates[reference_index]
            try:
                reference = _new_client(reference_url, minimum_interval=interval)
                _validate_transport_anchor(reference, chain=chain, require_contract_code=False)
                reference_logs = _query_logs_interval(
                    reference,
                    addresses=[normalize_address(str(chain["agent_hub"]))],
                    topics=hub_topics,
                    start_block=start,
                    end_block=end,
                    maximum_topics_per_query=maximum_topics,
                )
                reference_identities = _canonical_log_identities(reference_logs)
                if reference_identities != primary_identities:
                    raise RuntimeError("canonical qualification identity sets differ")
                return primary, {
                    "anchor_rpc": anchor_url,
                    "anchor_request_counts": dict(sorted(anchor.method_counts.items())),
                    "anchor_chain_and_hashes_verified": True,
                    "state_witness": state_witness,
                    "primary_rpc": primary_url,
                    "reference_rpc": reference_url,
                    "from_block": start,
                    "to_block": end,
                    "nonempty_hub_event_count": len(primary_identities),
                    "canonical_log_identity_sets_equal": True,
                    "failed_candidates_before_success": failures,
                    "reference_request_counts": dict(sorted(reference.method_counts.items())),
                }
            except Exception as error:
                failures.append(
                    {
                        "rpc": reference_url,
                        "role": "reference",
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )
    raise RuntimeError(f"no two frozen transports qualified: {failures}")


def _checkpoint_body(
    *,
    identity: Mapping[str, Any],
    state: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "identity": dict(identity),
        **state,
        "contains_only_decoded_policy_events_and_block_headers": True,
        "contains_raw_rpc_or_market_outcomes": False,
    }


def _write_chain_checkpoint(
    path: Path,
    *,
    identity: Mapping[str, Any],
    state: Mapping[str, Any],
) -> None:
    payload = _checkpoint_body(identity=identity, state=state)
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    _write_json(path, payload)


def _load_chain_checkpoint(
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
        raise RuntimeError("holdout checkpoint is not an object")
    stored = str(payload.pop("canonical_payload_sha256", ""))
    if canonical_sha256(payload) != stored:
        raise RuntimeError("holdout checkpoint digest mismatch")
    if payload.get("identity") != dict(identity):
        raise RuntimeError("holdout checkpoint identity mismatch")
    if payload.get("contains_only_decoded_policy_events_and_block_headers") is not True:
        raise RuntimeError("holdout checkpoint lacks its decoded-only assertion")
    if payload.get("contains_raw_rpc_or_market_outcomes") is not False:
        raise RuntimeError("holdout checkpoint violates blinding")
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
        or any(not isinstance(events[stage], list) for stage in stages)
        or any(not isinstance(row, dict) for stage in stages for row in events[stage])
        or not isinstance(headers, dict)
        or any(not isinstance(header, dict) for header in headers.values())
    ):
        raise RuntimeError("holdout checkpoint is malformed")
    return (
        {
            "completed_through": dict(completed),
            "events": {stage: list(events[stage]) for stage in stages},
            "block_headers": dict(headers),
        },
        True,
    )


def _query_decoded_stage(
    client: _RpcClient,
    *,
    stage: str,
    state: dict[str, Any],
    addresses: Sequence[str],
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    initial_span: int,
    maximum_topics_per_query: int,
    decoder: Callable[[Mapping[str, Any]], dict[str, Any]],
    save_checkpoint: Callable[[], None],
) -> list[dict[str, Any]]:
    stage_events = cast(list[dict[str, Any]], state["events"][stage])
    identities = {
        (str(event["block_hash"]), str(event["transaction_hash"]), int(event["log_index"]))
        for event in stage_events
    }
    if len(identities) != len(stage_events):
        raise ValueError(f"checkpoint contains duplicate decoded {stage} events")
    start = max(from_block, int(state["completed_through"][stage]) + 1)
    while start <= to_block:
        end = min(to_block, start + initial_span - 1)
        raw_logs = _query_logs_interval(
            client,
            addresses=addresses,
            topics=topics,
            start_block=start,
            end_block=end,
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
                raise ValueError(f"duplicate decoded {stage} event")
            identities.add(identity)
            stage_events.append(decoded)
        stage_events.sort(key=event_position)
        state["completed_through"][stage] = end
        save_checkpoint()
        start = end + 1
    return stage_events


def _attach_timestamps(
    client: _RpcClient,
    event_groups: Sequence[list[dict[str, Any]]],
    *,
    state: dict[str, Any],
    save_checkpoint: Callable[[], None],
) -> int:
    events = [event for group in event_groups for event in group]
    block_numbers = sorted({int(event["block_number"]) for event in events})
    headers = state["block_headers"]
    for block_number in block_numbers:
        key = str(block_number)
        if key not in headers:
            headers[key] = client.block(block_number)
            save_checkpoint()
        header = headers[key]
        if int(header["number"]) != block_number:
            raise RuntimeError("checkpoint header number mismatch")
        for event in events:
            if int(event["block_number"]) == block_number:
                if str(event["block_hash"]) != str(header["hash"]):
                    raise RuntimeError("event block hash differs from canonical header")
                event["block_timestamp"] = int(header["timestamp"])
                event["block_utc"] = _utc(int(header["timestamp"]))
    save_checkpoint()
    return len(block_numbers)


def audit_chain(
    config_path: Path,
    *,
    chain_name: str,
    preferred_rpc_index: int,
    agent_hub_root: Path,
    risk_agents_root: Path,
    chaos_agents_root: Path,
    address_book_root: Path,
    proposals_root: Path,
    output_path: Path,
    checkpoint_path: Path,
) -> dict[str, Any]:
    """Run one outcome-blind chain shard from a clean implementation commit."""
    if _git("status", "--porcelain"):
        raise RuntimeError("formal holdout chain audit requires a clean EcoPhys worktree")
    if checkpoint_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("formal holdout checkpoint must remain outside the repository")
    if output_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("chain shards must remain outside the repository until merge")
    config = _load_yaml(config_path)
    if config["contract"]["status"] != "frozen_before_any_non_ethereum_agent_event_query":
        raise RuntimeError("holdout contract lacks the pre-event freeze status")
    if chain_name not in config["chains"]:
        raise ValueError(f"chain is outside the frozen panel: {chain_name}")
    pilot_audit = _validate_pilot_binding(config)
    source_audit = _source_audit(
        config,
        agent_hub_root=agent_hub_root,
        risk_agents_root=risk_agents_root,
        chaos_agents_root=chaos_agents_root,
        address_book_root=address_book_root,
        proposals_root=proposals_root,
    )
    chain = config["chains"][chain_name]
    hub_address = normalize_address(str(chain["agent_hub"]))
    range_address = normalize_address(str(chain["range_validation_module"]))
    oracle_address = normalize_address(str(chain["edge_risk_oracle"]))
    hub_by_topic = {_keccak_topic(signature): signature for signature in HUB_SIGNATURES}
    range_by_topic = {_keccak_topic(signature): signature for signature in RANGE_SIGNATURES}
    risk_topic = _keccak_topic(RISK_ORACLE_SIGNATURE)
    client, qualification = _qualify_transport(
        config,
        chain=chain,
        preferred_rpc_index=preferred_rpc_index,
        hub_topics=sorted(hub_by_topic),
    )
    repository_sha = _git("rev-parse", "HEAD")
    config_sha = _sha256_file(config_path)
    identity = {
        "repository_sha": repository_sha,
        "config_sha256": config_sha,
        "chain_name": chain_name,
        "chain_id": int(chain["chain_id"]),
        "formal_rpc": client.url,
        "from_block": int(chain["from_block"]),
        "from_block_hash": str(chain["from_block_hash"]).lower(),
        "to_block": int(chain["to_block"]),
        "to_block_hash": str(chain["to_block_hash"]).lower(),
        "source_repository_shas": {
            label: str(record["git_sha"]) for label, record in source_audit["repositories"].items()
        },
    }
    state, resumed = _load_chain_checkpoint(
        checkpoint_path,
        identity=identity,
        from_block=int(chain["from_block"]),
    )

    def save_checkpoint() -> None:
        _write_chain_checkpoint(checkpoint_path, identity=identity, state=state)

    maximum_topics = int(config["transport"]["maximum_topics_per_get_logs"])
    formal_span = int(chain["formal_initial_get_logs_span"])
    hub_events = _query_decoded_stage(
        client,
        stage="hub",
        state=state,
        addresses=[hub_address],
        topics=sorted(hub_by_topic),
        from_block=int(chain["from_block"]),
        to_block=int(chain["to_block"]),
        initial_span=formal_span,
        maximum_topics_per_query=maximum_topics,
        decoder=lambda raw: _decode_hub_log(
            raw,
            hub_address=hub_address,
            signatures_by_topic=hub_by_topic,
        ),
        save_checkpoint=save_checkpoint,
    )
    range_events = _query_decoded_stage(
        client,
        stage="range",
        state=state,
        addresses=[range_address],
        topics=sorted(range_by_topic),
        from_block=int(chain["from_block"]),
        to_block=int(chain["to_block"]),
        initial_span=formal_span,
        maximum_topics_per_query=maximum_topics,
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
        state=state,
        addresses=[oracle_address],
        topics=[risk_topic],
        from_block=int(chain["from_block"]),
        to_block=int(chain["to_block"]),
        initial_span=formal_span,
        maximum_topics_per_query=maximum_topics,
        decoder=lambda raw: _decode_proposal_log(
            raw,
            oracle_addresses={oracle_address},
            expected_topic=risk_topic,
        ),
        save_checkpoint=save_checkpoint,
    )
    unique_headers = _attach_timestamps(
        client,
        [hub_events, range_events, proposals],
        state=state,
        save_checkpoint=save_checkpoint,
    )
    if any(int(proposal["oracle_timestamp"]) != int(proposal["block_timestamp"]) for proposal in proposals):
        raise RuntimeError(f"{chain_name} Risk Oracle timestamp differs from its block timestamp")
    end_header = client.block(int(chain["to_block"]))
    ledgers = build_holdout_chain_ledger(
        hub_events,
        proposals,
        chain_id=int(chain["chain_id"]),
        chain_name=chain_name,
        expected_risk_oracle=oracle_address,
        end_timestamp=int(end_header["timestamp"]),
    )
    registrations = [event for event in hub_events if event["event_name"] == "AgentRegistered"]
    injections = [event for event in hub_events if event["event_name"] == "UpdateInjected"]
    result: dict[str, Any] = {
        "schema_version": 1,
        "contract_name": str(config["contract"]["name"]),
        "contract_version": int(config["contract"]["version"]),
        "artifact_type": "outcome_blind_chain_shard",
        "repository": {
            "git_sha": repository_sha,
            "clean_worktree_at_start": True,
            "config_path": str(config_path.relative_to(REPO_ROOT)),
            "config_sha256": config_sha,
        },
        "pilot_binding": pilot_audit,
        "source_audit": source_audit,
        "chain": {
            "name": chain_name,
            "chain_id": int(chain["chain_id"]),
            "from_block": int(chain["from_block"]),
            "from_block_hash": str(chain["from_block_hash"]).lower(),
            "to_block": int(chain["to_block"]),
            "to_block_hash": str(chain["to_block_hash"]).lower(),
            "to_block_timestamp": int(end_header["timestamp"]),
            "to_block_utc": _utc(int(end_header["timestamp"])),
            "agent_hub": hub_address,
            "range_validation_module": range_address,
            "edge_risk_oracle": oracle_address,
        },
        "action_surface": {
            "agent_hub_event_count": len(hub_events),
            "registration_count": len(registrations),
            "expected_oracle_registration_count": sum(
                normalize_address(str(event["risk_oracle"])) == oracle_address for event in registrations
            ),
            "injection_event_count": len(injections),
            "range_configuration_event_count": len(range_events),
            "raw_proposal_count": len(proposals),
            "eligible_proposal_count": len(ledgers["eligible"]),
            "excluded_proposal_count": len(ledgers["exclusions"]),
            "unique_event_block_header_count": unique_headers,
            "hub_events": hub_events,
            "range_configuration_events": range_events,
            "eligible_proposal_ledger": ledgers["eligible"],
            "proposal_exclusion_ledger": ledgers["exclusions"],
            "raw_rpc_responses_persisted": False,
        },
        "transport_qualification": qualification,
        "transport": {
            "formal_rpc": client.url,
            "formal_initial_get_logs_span": formal_span,
            "maximum_topics_per_get_logs": maximum_topics,
            "rpc_request_counts": dict(sorted(client.method_counts.items())),
            "log_range_splits": client.log_range_splits,
            "log_topic_splits": client.log_topic_splits,
            "rate_limit_retry_count": client.rate_limit_retry_count,
            "rate_limit_wait_seconds": round(client.rate_limit_wait_seconds, 3),
            "server_error_retry_count": client.server_error_retry_count,
            "server_error_wait_seconds": round(client.server_error_wait_seconds, 3),
        },
        "checkpoint": {
            "resumed_from_checkpoint": resumed,
            "checkpoint_outside_repository": True,
            "checkpoint_contains_raw_rpc_or_market_outcomes": False,
            "checkpoint_removed_after_success": True,
        },
        "blinding": {
            "only_agent_configuration_proposal_injection_events_and_headers_queried": True,
            "pool_state_or_market_outcomes_queried": False,
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
    _write_json(output_path, result)
    checkpoint_path.unlink(missing_ok=True)
    return result


def _verified_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"chain artifact is not an object: {path}")
    stored = str(payload.get("canonical_payload_sha256", ""))
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if canonical_sha256(body) != stored:
        raise RuntimeError(f"chain artifact digest mismatch: {path}")
    return payload


def merge_chain_results(
    config_path: Path,
    *,
    chain_result_dir: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Merge all frozen chain shards and apply the multichain gate once."""
    if _git("status", "--porcelain"):
        raise RuntimeError("formal holdout merge requires a clean EcoPhys worktree")
    config = _load_yaml(config_path)
    pilot_audit = _validate_pilot_binding(config)
    repository_sha = _git("rev-parse", "HEAD")
    config_sha = _sha256_file(config_path)
    chain_payloads: dict[str, dict[str, Any]] = {}
    eligible: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    source_audit: dict[str, Any] | None = None
    for chain_name, frozen_chain in sorted(config["chains"].items()):
        path = chain_result_dir / f"{chain_name}.json"
        payload = _verified_artifact(path)
        if payload.get("artifact_type") != "outcome_blind_chain_shard":
            raise RuntimeError(f"unexpected artifact type for {chain_name}")
        if payload["repository"]["git_sha"] != repository_sha:
            raise RuntimeError(f"chain shard uses another repository SHA: {chain_name}")
        if payload["repository"]["config_sha256"] != config_sha:
            raise RuntimeError(f"chain shard uses another config: {chain_name}")
        if payload["chain"]["name"] != chain_name:
            raise RuntimeError(f"chain shard name mismatch: {chain_name}")
        if int(payload["chain"]["chain_id"]) != int(frozen_chain["chain_id"]):
            raise RuntimeError(f"chain shard ID mismatch: {chain_name}")
        if payload["chain"]["to_block_hash"] != str(frozen_chain["to_block_hash"]).lower():
            raise RuntimeError(f"chain shard endpoint mismatch: {chain_name}")
        if payload.get("pilot_binding") != pilot_audit:
            raise RuntimeError(f"chain shard pilot binding mismatch: {chain_name}")
        if source_audit is None:
            source_audit = payload["source_audit"]
        elif payload["source_audit"] != source_audit:
            raise RuntimeError("chain shards disagree on pinned source audit")
        surface = payload["action_surface"]
        eligible.extend(dict(row) for row in surface["eligible_proposal_ledger"])
        exclusions.extend(dict(row) for row in surface["proposal_exclusion_ledger"])
        chain_payloads[chain_name] = {
            "artifact_canonical_payload_sha256": payload["canonical_payload_sha256"],
            "chain": payload["chain"],
            "action_surface": surface,
            "transport_qualification": payload["transport_qualification"],
            "transport": payload["transport"],
            "checkpoint": payload["checkpoint"],
            "blinding": payload["blinding"],
            "compute": payload["compute"],
        }
    if source_audit is None:
        raise RuntimeError("no holdout chain artifact was loaded")
    batched = assign_action_batches(
        eligible,
        maximum_adjacent_gap_seconds=int(config["batching"]["maximum_adjacent_gap_seconds"]),
    )
    support = assess_holdout_action_support(
        batched,
        exclusions,
        thresholds=config["pass_thresholds"],
        boundary_rules=config["boundary_support"],
    )
    decision = (
        "pass_to_separately_frozen_multichain_d1_exact_validation_replay"
        if support["passed"]
        else "stop_multichain_threshold_route_before_d1_and_market_outcomes"
    )
    result: dict[str, Any] = {
        "schema_version": 1,
        "contract_name": str(config["contract"]["name"]),
        "contract_version": int(config["contract"]["version"]),
        "artifact_type": "outcome_blind_multichain_holdout_result",
        "decision": decision,
        "repository": {
            "git_sha": repository_sha,
            "clean_worktree_at_start": True,
            "config_path": str(config_path.relative_to(REPO_ROOT)),
            "config_sha256": config_sha,
        },
        "pilot_binding": pilot_audit,
        "source_audit": source_audit,
        "chain_count": len(chain_payloads),
        "chains": chain_payloads,
        "combined_action_surface": {
            "eligible_proposal_ledger_with_action_batches": batched,
            "proposal_exclusion_ledger": sorted(
                exclusions,
                key=lambda row: (
                    int(row["oracle_timestamp"]),
                    int(row["chain_id"]),
                    event_position(row),
                ),
            ),
            "raw_rpc_responses_persisted": False,
        },
        "support_gate": support,
        "blinding": {
            "ethereum_pilot_rows_in_holdout_counts": False,
            "only_agent_configuration_proposal_injection_events_and_headers_queried": True,
            "pool_state_or_market_outcomes_queried": False,
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
    _write_json(output_path, result)
    return result


def _source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--agent-hub-root", type=Path, required=True)
    parser.add_argument("--risk-agents-root", type=Path, required=True)
    parser.add_argument("--chaos-agents-root", type=Path, required=True)
    parser.add_argument("--address-book-root", type=Path, required=True)
    parser.add_argument("--proposals-root", type=Path, required=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    chain_parser = subparsers.add_parser("chain")
    chain_parser.add_argument("--config", type=Path, required=True)
    chain_parser.add_argument("--chain", required=True)
    chain_parser.add_argument("--preferred-rpc-index", type=int, default=0)
    chain_parser.add_argument("--output", type=Path, required=True)
    chain_parser.add_argument("--checkpoint", type=Path, required=True)
    _source_arguments(chain_parser)
    merge_parser = subparsers.add_parser("merge")
    merge_parser.add_argument("--config", type=Path, required=True)
    merge_parser.add_argument("--chain-result-dir", type=Path, required=True)
    merge_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "chain":
        result = audit_chain(
            args.config.resolve(),
            chain_name=str(args.chain),
            preferred_rpc_index=int(args.preferred_rpc_index),
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
                    "chain": result["chain"]["name"],
                    "eligible": result["action_surface"]["eligible_proposal_count"],
                    "excluded": result["action_surface"]["excluded_proposal_count"],
                    "manifest": str(args.output.resolve()),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    result = merge_chain_results(
        args.config.resolve(),
        chain_result_dir=args.chain_result_dir.resolve(),
        output_path=args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "eligible": result["support_gate"]["eligible_proposal_count"],
                "batches": result["support_gate"]["proposal_batch_count"],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
