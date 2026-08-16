from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml

PROTOCOL_COMMIT = "ceb83d1fdd638836cfd8c563d7741f59d33174c6"
MANIFEST_SHA256 = "860cd0338414508d3a447cd522114cc3dbaa3193624863c9326091e0f1fa2763"
SUMMARY_SHA256 = "ff3e120920b766957353c59c02341c42990a18818a751d62da6e1a6798a3c1bb"
DIRECTORY_SHA256 = "1d1d73b5f5ba51c60841a411edf563317f143e9599e3eac958643895c90648ec"
LEDGER_SHA256 = "71055ad80b66bc36138fedb63ff0fc742d12a0f72e0341320e2b4a1060e151b1"
EXPECTED_DECISION = "FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED"
PROVIDER = "0x2f39d218133afab8f2b819b1066c7e434ad94e9e"
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
CONFIGURATOR = "0x64b761d848206f447fe2dd461b0c635ec39ebb27"
ORACLE = "0x54586be62e3c3580375ae3723c145253060ca0c2"
POOL_IMPLEMENTATION = "0x728a138a4823392c2efa55e028d434f526fe03cf"
CONFIGURATOR_IMPLEMENTATION = "0xff42ce30054dce7dc7c1282a9a497aa58eabce99"
POOL_ID = "0x504f4f4c00000000000000000000000000000000000000000000000000000000"
CONFIGURATOR_ID = "0x504f4f4c5f434f4e464947555241544f52000000000000000000000000000000"
IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
UPGRADED_TOPIC = "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b"
INITIALIZER_PATH = (
    "src/contracts/dependencies/openzeppelin/upgradeability/InitializableUpgradeabilityProxy.sol"
)
INITIALIZER_GIT_BLOB = "4b43fa6a87dd84be15fc77b3ea4b1a88350c4175"
INITIALIZER_SHA256 = "496cde2ade866d2fcb6723dee4c1e42637c3a3437c3497e05d42763d362ac061"
EXPECTED_GATES = {
    "complete_bounded_log_partitions": True,
    "complete_proxy_upgrade_crosswalk": False,
    "ethereum_chain_id_replication": True,
    "exact_root_partition_plan": True,
    "fixed_window_header_replication": True,
    "frozen_source_identity": True,
    "implementation_code_nonempty": True,
    "minimum_provisional_directory_support": False,
    "no_duplicate_or_conflicting_logs": True,
    "parent_hashes_and_a0_decision": True,
    "provider_event_abi_complete": True,
    "provider_getter_source_conformance": True,
    "proxy_terminal_state_source_conformance": True,
    "request_and_byte_caps": True,
    "strict_log_decoding": True,
    "zero_account_access_boundary": True,
}


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise AssertionError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def read_json_value(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs)


def read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    assert isinstance(value, dict), path
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def root_intervals(from_block: int, to_block: int, size: int) -> list[tuple[int, int]]:
    return [(start, min(start + size - 1, to_block)) for start in range(from_block, to_block + 1, size)]


def expected_request_plan(code_addresses: list[str]) -> list[dict[str, Any]]:
    end = 25_760_572
    end_tag = hex(end)
    plan: list[dict[str, Any]] = []
    for provider in ("blockscout", "publicnode"):
        plan.extend(
            [
                {
                    "label": f"{provider}:chain_id",
                    "provider": provider,
                    "method": "eth_chainId",
                    "params": [],
                },
                {
                    "label": f"{provider}:window_start_header",
                    "provider": provider,
                    "method": "eth_getBlockByNumber",
                    "params": ["0x0", False],
                },
                {
                    "label": f"{provider}:window_end_header",
                    "provider": provider,
                    "method": "eth_getBlockByNumber",
                    "params": [end_tag, False],
                },
            ]
        )
    streams = (
        ("provider", PROVIDER, None),
        ("configurator", CONFIGURATOR, None),
        ("pool", POOL, UPGRADED_TOPIC),
    )
    for role, address, topic0 in streams:
        for index, (start, stop) in enumerate(root_intervals(0, end, 250_000)):
            log_filter: dict[str, Any] = {
                "fromBlock": hex(start),
                "toBlock": hex(stop),
                "address": address,
            }
            if topic0 is not None:
                log_filter["topics"] = [topic0]
            plan.append(
                {
                    "label": f"logs:{role}:{index}:0:{start}-{stop}",
                    "provider": "blockscout",
                    "method": "eth_getLogs",
                    "params": [log_filter],
                }
            )
    for name, selector in (("pool", "0x026b1d5f"), ("configurator", "0x631adfca"), ("oracle", "0xfca513a8")):
        plan.append(
            {
                "label": f"blockscout:terminal_getter:{name}",
                "provider": "blockscout",
                "method": "eth_call",
                "params": [{"to": PROVIDER, "data": selector}, end_tag],
            }
        )
    plan.extend(
        [
            {
                "label": "blockscout:terminal_slot:pool",
                "provider": "blockscout",
                "method": "eth_getStorageAt",
                "params": [POOL, IMPLEMENTATION_SLOT, end_tag],
            },
            {
                "label": "blockscout:terminal_slot:configurator",
                "provider": "blockscout",
                "method": "eth_getStorageAt",
                "params": [CONFIGURATOR, IMPLEMENTATION_SLOT, end_tag],
            },
        ]
    )
    for address in sorted(code_addresses):
        plan.append(
            {
                "label": f"blockscout:terminal_code:{address}",
                "provider": "blockscout",
                "method": "eth_getCode",
                "params": [address, end_tag],
            }
        )
    return plan


def recompute_candidates(directory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        directory,
        key=lambda item: (item["block_number"], item["transaction_index"], item["log_index"]),
    )
    configurator_by_tx = Counter(
        item["transaction_hash"] for item in ordered if item["role"] == "configurator"
    )
    deployment_or_upgrade_by_tx = Counter(
        item["transaction_hash"]
        for item in ordered
        if item["role"] == "provider" or item["event_type"] == "upgraded"
    )
    previous_by_asset: dict[str, dict[str, Any]] = {}
    candidates: list[dict[str, Any]] = []
    for item in ordered:
        if item["event_type"] != "collateral_configuration_changed":
            continue
        asset = item["asset"]
        previous = previous_by_asset.get(asset)
        transaction = item["transaction_hash"]
        checks = {
            "has_previous_emitted_configuration": previous is not None,
            "strict_positive_liquidation_threshold_decrease": previous is not None
            and 0 < item["liquidation_threshold"] < previous["liquidation_threshold"],
            "emitted_ltv_unchanged": previous is not None and item["ltv"] == previous["ltv"],
            "emitted_liquidation_bonus_unchanged": previous is not None
            and item["liquidation_bonus"] == previous["liquidation_bonus"],
            "exactly_one_configurator_log_in_transaction": configurator_by_tx[transaction] == 1,
            "no_provider_or_proxy_upgrade_log_in_transaction": deployment_or_upgrade_by_tx[transaction] == 0,
        }
        candidates.append(
            {
                "block_number": item["block_number"],
                "transaction_hash": transaction,
                "log_index": item["log_index"],
                "asset": asset,
                "previous_emitted_block_number": previous["block_number"] if previous is not None else None,
                "previous_emitted_transaction_hash": previous["transaction_hash"]
                if previous is not None
                else None,
                "old_emitted_ltv": previous["ltv"] if previous is not None else None,
                "new_emitted_ltv": item["ltv"],
                "old_emitted_liquidation_threshold": previous["liquidation_threshold"]
                if previous is not None
                else None,
                "new_emitted_liquidation_threshold": item["liquidation_threshold"],
                "old_emitted_liquidation_bonus": previous["liquidation_bonus"]
                if previous is not None
                else None,
                "new_emitted_liquidation_bonus": item["liquidation_bonus"],
                "checks": checks,
                "provisional_directory_candidate": all(checks.values()),
                "deferred_checks": [
                    "authoritative_t_minus_one_and_t_configuration",
                    "reserve_frozen_state",
                    "receipt_payload_and_call_path_isolation",
                    "config_engine_keep_current_normalization",
                    "emode_oracle_index_pause_and_grace_spillovers",
                    "historical_implementation_source_identity",
                    "proposal_mapping_and_untouched_confirmation_split",
                ],
            }
        )
        previous_by_asset[asset] = item
    return candidates


def component_history(
    directory: list[dict[str, Any]],
    *,
    component: str,
    component_id: str,
    proxy: str,
    terminal_implementation: str,
) -> dict[str, Any]:
    update_type = "pool_updated" if component == "pool" else "pool_configurator_updated"
    creations = [
        item
        for item in directory
        if item["role"] == "provider"
        and item["event_type"] == "proxy_created"
        and item.get("id") == component_id
    ]
    forbidden = [
        item
        for item in directory
        if item["role"] == "provider"
        and item["event_type"] == "address_set"
        and item.get("id") == component_id
    ]
    transitions: list[dict[str, Any]] = []
    for item in directory:
        if item["role"] != "provider":
            continue
        if item["event_type"] == update_type:
            transitions.append(
                {
                    "block_number": item["block_number"],
                    "transaction_hash": item["transaction_hash"],
                    "log_index": item["log_index"],
                    "route": update_type,
                    "old_implementation": item["old_address"],
                    "new_implementation": item["new_address"],
                }
            )
        elif item["event_type"] == "address_set_as_proxy" and item.get("id") == component_id:
            transitions.append(
                {
                    "block_number": item["block_number"],
                    "transaction_hash": item["transaction_hash"],
                    "log_index": item["log_index"],
                    "route": "address_set_as_proxy",
                    "old_implementation": item["old_implementation"],
                    "new_implementation": item["new_implementation"],
                    "declared_proxy": item["proxy"],
                }
            )
    transitions.sort(key=lambda item: (item["block_number"], item["log_index"]))
    upgrades = sorted(
        [item for item in directory if item["role"] == component and item["event_type"] == "upgraded"],
        key=lambda item: (item["block_number"], item["log_index"]),
    )
    transition_keys = Counter((item["transaction_hash"], item["new_implementation"]) for item in transitions)
    upgrade_keys = Counter((item["transaction_hash"], item["implementation"]) for item in upgrades)
    continuity = bool(transitions) and transitions[0]["old_implementation"] == "0x" + "0" * 40
    for old, new in pairwise(transitions):
        continuity = continuity and old["new_implementation"] == new["old_implementation"]
    creation_matches = (
        len(creations) == 1
        and creations[0]["proxy"] == proxy
        and bool(transitions)
        and creations[0]["transaction_hash"] == transitions[0]["transaction_hash"]
        and creations[0]["implementation"] == transitions[0]["new_implementation"]
    )
    checks = {
        "one_matching_proxy_created": creation_matches,
        "no_direct_address_set_for_component_id": not forbidden,
        "nonempty_transition_history": bool(transitions),
        "continuous_old_to_new_implementation_chain": continuity,
        "one_to_one_provider_transition_and_proxy_upgrade": transition_keys == upgrade_keys,
        "all_address_set_as_proxy_rows_name_expected_proxy": all(
            item.get("route") != "address_set_as_proxy" or item.get("declared_proxy") == proxy
            for item in transitions
        ),
        "latest_history_matches_terminal_slot": bool(transitions)
        and transitions[-1]["new_implementation"] == terminal_implementation,
    }
    return {
        "component": component,
        "component_id": component_id,
        "proxy": proxy,
        "transition_count": len(transitions),
        "upgrade_count": len(upgrades),
        "proxy_created_count": len(creations),
        "forbidden_direct_address_set_count": len(forbidden),
        "transitions": transitions,
        "checks": checks,
        "passed": all(checks.values()),
    }


def verify(root: Path) -> dict[str, Any]:
    experiment = root / "experiments/v14_aave_v3_lt_event_directory"
    manifest_path = root / "data/manifests/aave_v3_ethereum_lt_event_directory_v1.yaml"
    summary_path = experiment / "artifacts/summary.json"
    directory_path = experiment / "artifacts/event_directory.json"
    ledger_path = experiment / "artifacts/rpc_response_hashes.json"
    failure_path = experiment / "artifacts/failure.json"
    expected_hashes = {
        manifest_path: MANIFEST_SHA256,
        summary_path: SUMMARY_SHA256,
        directory_path: DIRECTORY_SHA256,
        ledger_path: LEDGER_SHA256,
    }
    for path, expected in expected_hashes.items():
        assert sha256_file(path) == expected, path
    assert not failure_path.exists()
    manifest = read_yaml(manifest_path)
    summary = read_json_value(summary_path)
    directory = read_json_value(directory_path)
    ledger = read_json_value(ledger_path)
    assert isinstance(summary, dict)
    assert isinstance(directory, list) and all(isinstance(item, dict) for item in directory)
    assert isinstance(ledger, list) and all(isinstance(item, dict) for item in ledger)

    assert summary["collection_commit"] == PROTOCOL_COMMIT
    assert summary["manifest_sha256"] == MANIFEST_SHA256
    assert summary["parents"] == manifest["parents"]
    assert summary["source_identity"] == manifest["source_identity"]
    for path_key, hash_key in (
        ("a0_summary_path", "a0_summary_sha256"),
        ("a0_manifest_path", "a0_manifest_sha256"),
        ("chain_summary_path", "chain_summary_sha256"),
    ):
        parent_path = root / manifest["parents"][path_key]
        assert sha256_file(parent_path) == manifest["parents"][hash_key]

    assert len(directory) == 3_119
    identities = [(item["block_hash"], item["transaction_hash"], item["log_index"]) for item in directory]
    assert len(identities) == len(set(identities))
    assert directory == sorted(
        directory,
        key=lambda item: (
            item["block_number"],
            item["transaction_index"],
            item["log_index"],
            item["address"],
        ),
    )
    role_counts = dict(sorted(Counter(item["role"] for item in directory).items()))
    event_counts = dict(sorted(Counter(item["event_type"] for item in directory).items()))
    assert role_counts == summary["event_directory"]["role_counts"]
    assert event_counts == summary["event_directory"]["event_type_counts"]
    assert role_counts == {"configurator": 3069, "pool": 10, "provider": 40}
    assert event_counts["collateral_configuration_changed"] == 137
    assert event_counts.get("unknown_provider", 0) == 0
    for item in directory:
        assert item["role"] in {"provider", "configurator", "pool"}
        assert (
            item["address"]
            == {"provider": PROVIDER, "configurator": CONFIGURATOR, "pool": POOL}[item["role"]]
        )
        assert 0 <= item["block_number"] <= 25_760_572
        if item["event_type"] == "collateral_configuration_changed":
            assert item["role"] == "configurator"
            assert all(
                isinstance(item[key], int) and item[key] >= 0
                for key in ("ltv", "liquidation_threshold", "liquidation_bonus")
            )
        if item["event_type"] == "upgraded":
            assert item["role"] in {"pool", "configurator"}

    candidates = recompute_candidates(directory)
    assert candidates == summary["event_directory"]["configuration_candidate_records"]
    provisional = [item for item in candidates if item["provisional_directory_candidate"]]
    assert len(candidates) == 137 and not provisional
    strict_decreases = [
        item for item in candidates if item["checks"]["strict_positive_liquidation_threshold_decrease"]
    ]
    mechanism_only = [
        item
        for item in strict_decreases
        if item["checks"]["emitted_ltv_unchanged"] and item["checks"]["emitted_liquidation_bonus_unchanged"]
    ]
    assert len(strict_decreases) == 18
    assert len(mechanism_only) == 4
    assert all(not item["checks"]["exactly_one_configurator_log_in_transaction"] for item in mechanism_only)
    mechanism_transactions = sorted({item["transaction_hash"] for item in mechanism_only})
    configurator_counts = Counter(
        item["transaction_hash"] for item in directory if item["role"] == "configurator"
    )
    assert sorted(configurator_counts[transaction] for transaction in mechanism_transactions) == [13, 16]

    terminal = summary["terminal_state"]
    assert terminal == {
        "provider": "blockscout",
        "block_number": 25_760_572,
        "values": {
            "pool": POOL,
            "configurator": CONFIGURATOR,
            "oracle": ORACLE,
            "pool_implementation": POOL_IMPLEMENTATION,
            "configurator_implementation": CONFIGURATOR_IMPLEMENTATION,
        },
    }
    histories = {
        "pool": component_history(
            directory,
            component="pool",
            component_id=POOL_ID,
            proxy=POOL,
            terminal_implementation=POOL_IMPLEMENTATION,
        ),
        "configurator": component_history(
            directory,
            component="configurator",
            component_id=CONFIGURATOR_ID,
            proxy=CONFIGURATOR,
            terminal_implementation=CONFIGURATOR_IMPLEMENTATION,
        ),
    }
    assert histories == summary["version_history"]
    source_corrected_history: dict[str, bool] = {}
    for component, history in histories.items():
        upgrades = [
            item for item in directory if item["role"] == component and item["event_type"] == "upgraded"
        ]
        transitions = history["transitions"]
        later_transition_keys = Counter(
            (item["transaction_hash"], item["new_implementation"]) for item in transitions[1:]
        )
        upgrade_keys = Counter((item["transaction_hash"], item["implementation"]) for item in upgrades)
        source_corrected_history[component] = (
            history["transition_count"] == history["upgrade_count"] + 1
            and later_transition_keys == upgrade_keys
            and history["checks"]["one_matching_proxy_created"]
            and history["checks"]["continuous_old_to_new_implementation_chain"]
            and history["checks"]["latest_history_matches_terminal_slot"]
        )
    assert source_corrected_history == {"pool": True, "configurator": True}

    roles_by_code: dict[str, set[str]] = defaultdict(set)
    roles_by_code[PROVIDER].add("pool_addresses_provider")
    roles_by_code[POOL].add("pool_proxy")
    roles_by_code[CONFIGURATOR].add("pool_configurator_proxy")
    for component, history in histories.items():
        for transition in history["transitions"]:
            roles_by_code[transition["new_implementation"]].add(f"{component}_implementation")
    code_inventory = summary["code_inventory"]
    assert [item["address"] for item in code_inventory] == sorted(roles_by_code)
    assert all(item["roles"] == sorted(roles_by_code[item["address"]]) for item in code_inventory)
    assert all(item["nonempty"] is True and item["byte_count"] > 0 for item in code_inventory)

    plan = expected_request_plan([item["address"] for item in code_inventory])
    assert len(plan) == len(ledger) == 344
    for index, (expected_request, observed) in enumerate(zip(plan, ledger, strict=True)):
        assert observed["request_index"] == index
        assert {key: observed[key] for key in ("label", "provider", "method", "params")} == expected_request
        request = {
            "jsonrpc": "2.0",
            "id": index + 1,
            "method": observed["method"],
            "params": observed["params"],
        }
        assert observed["request_sha256"] == canonical_sha256(request)
        assert observed["attempt_count"] == 1 and observed["prior_errors"] == []
        assert observed["response_byte_count"] > 0
        assert all(
            len(observed[key]) == 64 for key in ("response_body_sha256", "response_canonical_json_sha256")
        )
    request_summary = summary["request_summary"]
    assert request_summary["successful_request_count"] == len(ledger)
    assert request_summary["http_attempt_count"] == len(ledger)
    assert request_summary["response_byte_count"] == sum(item["response_byte_count"] for item in ledger)
    assert request_summary["method_counts"] == dict(
        sorted(Counter(item["method"] for item in ledger).items())
    )
    assert request_summary["stream_query_counts"] == {"provider": 104, "configurator": 104, "pool": 104}
    assert request_summary["stream_saturated_query_counts"] == {"provider": 0, "configurator": 0, "pool": 0}

    headers = summary["window"]["headers"]
    assert summary["window"]["chain_ids"] == {"blockscout": "0x1", "publicnode": "0x1"}
    assert headers["blockscout"] == headers["publicnode"]
    assert headers["blockscout"]["to_block"]["number"] == 25_760_572
    assert headers["blockscout"]["to_block"]["hash"] == manifest["window"]["to_block_hash"]
    gates = {
        "parent_hashes_and_a0_decision": True,
        "frozen_source_identity": True,
        "ethereum_chain_id_replication": True,
        "fixed_window_header_replication": True,
        "exact_root_partition_plan": len(root_intervals(0, 25_760_572, 250_000)) == 104,
        "complete_bounded_log_partitions": all(
            value >= 104 for value in request_summary["stream_query_counts"].values()
        ),
        "strict_log_decoding": True,
        "no_duplicate_or_conflicting_logs": len(identities) == len(set(identities)),
        "provider_event_abi_complete": "unknown_provider" not in event_counts,
        "provider_getter_source_conformance": terminal["values"]["pool"] == POOL
        and terminal["values"]["configurator"] == CONFIGURATOR
        and terminal["values"]["oracle"] == ORACLE,
        "proxy_terminal_state_source_conformance": terminal["values"]["pool_implementation"]
        == POOL_IMPLEMENTATION
        and terminal["values"]["configurator_implementation"] == CONFIGURATOR_IMPLEMENTATION,
        "complete_proxy_upgrade_crosswalk": all(history["passed"] for history in histories.values()),
        "implementation_code_nonempty": all(item["nonempty"] for item in code_inventory),
        "minimum_provisional_directory_support": len(provisional) >= 3
        and len({item["asset"] for item in provisional}) >= 2
        and len({item["transaction_hash"] for item in provisional}) >= 3,
        "request_and_byte_caps": len(ledger) <= 2_000
        and request_summary["response_byte_count"] <= 268_435_456
        and len(directory) <= 100_000,
        "zero_account_access_boundary": summary["access_boundary"] == manifest["access_boundary"],
    }
    assert gates == EXPECTED_GATES == summary["gates"]
    assert summary["gate_counts"] == {"pass": 14, "fail": 2}
    assert summary["decision"] == EXPECTED_DECISION
    assert summary["authorized_next_stage"] is None
    serialized = json.dumps(summary, sort_keys=True)
    for forbidden in ('"raw_response":', '"response_body":', '"account":', '"realized_response":'):
        assert forbidden not in serialized
    return {
        "status": "PASS_INDEPENDENT_ARTIFACT_VERIFICATION",
        "protocol_commit": PROTOCOL_COMMIT,
        "manifest_sha256": MANIFEST_SHA256,
        "summary_sha256": SUMMARY_SHA256,
        "directory_sha256": DIRECTORY_SHA256,
        "ledger_sha256": LEDGER_SHA256,
        "request_count": len(ledger),
        "normalized_log_count": len(directory),
        "lt_decrease_count": len(strict_decreases),
        "emitted_lt_only_decrease_count": len(mechanism_only),
        "provisional_directory_candidate_count": len(provisional),
        "frozen_failed_gates": sorted(key for key, value in gates.items() if not value),
        "source_corrected_history_diagnostic": source_corrected_history,
        "initializer_source_identity": {
            "path": INITIALIZER_PATH,
            "git_blob": INITIALIZER_GIT_BLOB,
            "sha256": INITIALIZER_SHA256,
            "semantic": "initialize calls _setImplementation directly and emits no initial Upgraded event",
        },
        "decision": summary["decision"],
        "raw_rpc_replay": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
