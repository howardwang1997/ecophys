from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from itertools import groupby
from pathlib import Path
from typing import Any

import yaml

PROTOCOL_COMMIT = "d5636dd751b7654a24e8fae9fc39b72c6cc4a76b"
MANIFEST_SHA256 = "e8cf60b2577bdf9e46f68f15c0c7e21931a3d705357420a907b75d74838a65e0"
SUMMARY_SHA256 = "922312a9c75a64cfe66a1ef828140df938929e4bc6fbac9200a3a1f6fa9d9db9"
EXPECTED_DECISION = "COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY"
FIELDS = ("ltv", "liquidation_threshold", "liquidation_bonus")


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


def read_json(path: Path) -> Any:
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


def sort_key(item: dict[str, Any]) -> tuple[int, int, int, str]:
    return item["block_number"], item["transaction_index"], item["log_index"], item["address"]


def transaction_key(item: dict[str, Any]) -> tuple[str, str, int]:
    return item["block_hash"], item["transaction_hash"], item["transaction_index"]


def configuration(item: dict[str, Any]) -> dict[str, int]:
    return {field: item[field] for field in FIELDS}


def topic_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(item["topic0"] for item in items).items()))


def rebuild_bundles(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(records, key=sort_key)
    predecessor_by_asset: dict[str, dict[str, Any]] = {}
    bundles: list[dict[str, Any]] = []
    for _, grouped in groupby(ordered, key=transaction_key):
        transaction_records = list(grouped)
        configurator = [item for item in transaction_records if item["role"] == "configurator"]
        collateral = [
            item for item in configurator if item["event_type"] == "collateral_configuration_changed"
        ]
        if not collateral:
            continue
        by_asset: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in collateral:
            by_asset[item["asset"]].append(item)
        assets: list[dict[str, Any]] = []
        net_changes: list[dict[str, Any]] = []
        for asset in sorted(by_asset):
            sequence = sorted(by_asset[asset], key=sort_key)
            predecessor = predecessor_by_asset.get(asset)
            final = sequence[-1]
            pre_config = configuration(predecessor) if predecessor is not None else None
            final_config = configuration(final)
            asset_changes: list[dict[str, Any]] = []
            if pre_config is not None:
                for field in FIELDS:
                    if pre_config[field] != final_config[field]:
                        change = {
                            "asset": asset,
                            "field": field,
                            "old_value": pre_config[field],
                            "new_value": final_config[field],
                            "delta": final_config[field] - pre_config[field],
                        }
                        asset_changes.append(change)
                        net_changes.append(change)
            sequence_values = [configuration(item) for item in sequence]
            round_trip = (
                pre_config is not None
                and final_config == pre_config
                and any(value != pre_config for value in sequence_values)
            )
            assets.append(
                {
                    "asset": asset,
                    "predecessor_known": predecessor is not None,
                    "predecessor_block_number": predecessor["block_number"]
                    if predecessor is not None
                    else None,
                    "predecessor_transaction_hash": predecessor["transaction_hash"]
                    if predecessor is not None
                    else None,
                    "predecessor_configuration": pre_config,
                    "sequence": [
                        {"log_index": item["log_index"], **configuration(item)} for item in sequence
                    ],
                    "final_configuration": final_config,
                    "net_changes": asset_changes,
                    "returns_to_predecessor_after_intermediate_change": round_trip,
                }
            )
        for asset, sequence in by_asset.items():
            predecessor_by_asset[asset] = max(sequence, key=sort_key)
        other = [item for item in configurator if item["event_type"] != "collateral_configuration_changed"]
        first = collateral[0]
        bundles.append(
            {
                "block_number": first["block_number"],
                "block_hash": first["block_hash"],
                "transaction_index": first["transaction_index"],
                "transaction_hash": first["transaction_hash"],
                "configurator_log_count": len(configurator),
                "collateral_configuration_event_count": len(collateral),
                "other_configurator_event_count": len(other),
                "other_configurator_topic0_counts": topic_counts(other),
                "distinct_collateral_asset_count": len(by_asset),
                "predecessor_known_asset_count": sum(item["predecessor_known"] for item in assets),
                "predecessor_unknown_asset_count": sum(not item["predecessor_known"] for item in assets),
                "net_changed_asset_count": len({item["asset"] for item in net_changes}),
                "net_changed_dimension_count": len(net_changes),
                "net_change_field_counts": dict(
                    sorted(Counter(item["field"] for item in net_changes).items())
                ),
                "net_liquidation_threshold_decrease_count": sum(
                    item["field"] == "liquidation_threshold" and item["delta"] < 0 for item in net_changes
                ),
                "net_liquidation_threshold_increase_count": sum(
                    item["field"] == "liquidation_threshold" and item["delta"] > 0 for item in net_changes
                ),
                "pure_liquidation_threshold_vector": bool(net_changes)
                and all(item["field"] == "liquidation_threshold" for item in net_changes),
                "only_semantically_decoded_configurator_events": not other,
                "contains_round_trip": any(
                    item["returns_to_predecessor_after_intermediate_change"] for item in assets
                ),
                "asset_records": assets,
                "net_changes": net_changes,
            }
        )
    return bundles


def distribution(values: list[int]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items())}


def verify(root: Path) -> dict[str, Any]:
    manifest_path = root / "data/manifests/aave_v3_bundle_structure_feasibility_v1.yaml"
    summary_path = root / "experiments/v14_aave_v3_bundle_structure_feasibility/artifacts/summary.json"
    assert sha256_file(manifest_path) == MANIFEST_SHA256
    assert sha256_file(summary_path) == SUMMARY_SHA256
    manifest = read_yaml(manifest_path)
    summary = read_json(summary_path)
    assert isinstance(summary, dict)
    assert summary["collection_commit"] == PROTOCOL_COMMIT
    assert summary["manifest_sha256"] == MANIFEST_SHA256
    assert summary["parents"] == manifest["parents"]
    assert summary["development_disclosure"] == manifest["development_disclosure"]
    assert summary["development_disclosure"]["bundle_count_and_shape_explored_before_freeze"] is True
    assert summary["development_disclosure"]["confirmatory_or_blind_claim_permitted"] is False
    for path_key, hash_key in (
        ("directory_path", "directory_sha256"),
        ("summary_path", "summary_sha256"),
        ("manifest_path", "manifest_sha256"),
    ):
        assert sha256_file(root / manifest["parents"][path_key]) == manifest["parents"][hash_key]
    parent_summary = read_json(root / manifest["parents"]["summary_path"])
    assert parent_summary["decision"] == manifest["parents"]["expected_parent_decision"]
    records = read_json(root / manifest["parents"]["directory_path"])
    assert isinstance(records, list) and all(isinstance(item, dict) for item in records)
    identities = [(item["block_hash"], item["transaction_hash"], item["log_index"]) for item in records]
    assert len(records) == len(identities) == len(set(identities)) == 3_119
    bundles = rebuild_bundles(records)
    assert bundles == summary["transaction_bundles"]

    configurator = [item for item in records if item["role"] == "configurator"]
    collateral = [item for item in records if item["event_type"] == "collateral_configuration_changed"]
    net_changed = [item for item in bundles if item["net_changed_dimension_count"] > 0]
    net_lt_decrease = [item for item in bundles if item["net_liquidation_threshold_decrease_count"] > 0]
    pure_lt = [item for item in bundles if item["pure_liquidation_threshold_vector"]]
    round_trips = [item for item in bundles if item["contains_round_trip"]]
    expected_bundle_summary = {
        "transaction_count": len(bundles),
        "transaction_with_any_known_net_change_count": len(net_changed),
        "transaction_with_net_lt_decrease_count": len(net_lt_decrease),
        "pure_emitted_lt_vector_transaction_count": len(pure_lt),
        "round_trip_transaction_count": len(round_trips),
        "transaction_with_only_semantically_decoded_configurator_events_count": sum(
            item["only_semantically_decoded_configurator_events"] for item in bundles
        ),
        "predecessor_unknown_asset_occurrence_count": sum(
            item["predecessor_unknown_asset_count"] for item in bundles
        ),
        "configurator_log_count_distribution": distribution(
            [item["configurator_log_count"] for item in bundles]
        ),
        "collateral_event_count_distribution": distribution(
            [item["collateral_configuration_event_count"] for item in bundles]
        ),
        "net_changed_dimension_count_distribution": distribution(
            [item["net_changed_dimension_count"] for item in bundles]
        ),
        "maximum_configurator_log_count": max(item["configurator_log_count"] for item in bundles),
        "maximum_net_changed_dimension_count": max(item["net_changed_dimension_count"] for item in bundles),
        "other_configurator_topic0_counts": topic_counts(
            [item for item in configurator if item["event_type"] != "collateral_configuration_changed"]
        ),
    }
    assert summary["bundle_summary"] == expected_bundle_summary
    assert summary["parent_inventory"] == {
        "normalized_log_count": 3_119,
        "configurator_log_count": 3_069,
        "collateral_configuration_event_count": 137,
        "unique_configurator_topic0_count": 28,
        "unique_log_identity_count": 3_119,
    }
    assert expected_bundle_summary["transaction_count"] == 77
    assert expected_bundle_summary["transaction_with_any_known_net_change_count"] == 27
    assert expected_bundle_summary["transaction_with_net_lt_decrease_count"] == 5
    assert expected_bundle_summary["pure_emitted_lt_vector_transaction_count"] == 0
    assert expected_bundle_summary["round_trip_transaction_count"] == 1
    assert expected_bundle_summary["predecessor_unknown_asset_occurrence_count"] == 54
    assert expected_bundle_summary["maximum_configurator_log_count"] == 83
    assert expected_bundle_summary["maximum_net_changed_dimension_count"] == 20

    access = summary["access_boundary"]
    assert access == manifest["access_boundary"]
    assert access["network_used"] is False
    assert access["account_state_rows_opened"] is False
    assert access["participant_action_rows_opened"] is False
    assert access["realized_response_rows_opened"] is False
    gates = {
        "parent_hashes_and_decision": True,
        "exact_parent_log_identity_partition": len(identities) == len(set(identities)),
        "deterministic_transaction_grouping": len(bundles)
        == len({item["transaction_hash"] for item in collateral}),
        "predecessor_unknown_not_imputed": all(
            item["predecessor_known_asset_count"] + item["predecessor_unknown_asset_count"]
            == item["distinct_collateral_asset_count"]
            for item in bundles
        ),
        "exact_net_vector_reconstruction": all(
            item["net_changed_dimension_count"] == len(item["net_changes"]) for item in bundles
        ),
        "round_trip_detection": all(
            item["contains_round_trip"]
            is any(
                asset["returns_to_predecessor_after_intermediate_change"] for asset in item["asset_records"]
            )
            for item in bundles
        ),
        "no_network_or_participant_outcome_access": True,
    }
    assert summary["gates"] == gates and all(gates.values())
    assert summary["gate_counts"] == {"pass": 7, "fail": 0}
    assert summary["decision"] == EXPECTED_DECISION
    assert summary["authorized_next_stage"] == manifest["decision_policy"]["authorized_next_stage"]
    serialized = json.dumps(summary, sort_keys=True)
    for forbidden in ('"receipt":', '"calldata":', '"account_state":', '"realized_response":'):
        assert forbidden not in serialized
    return {
        "status": "PASS_INDEPENDENT_BUNDLE_STRUCTURE_VERIFICATION",
        "protocol_commit": PROTOCOL_COMMIT,
        "manifest_sha256": MANIFEST_SHA256,
        "summary_sha256": SUMMARY_SHA256,
        "transaction_count": len(bundles),
        "net_changed_transaction_count": len(net_changed),
        "net_lt_decrease_transaction_count": len(net_lt_decrease),
        "pure_emitted_lt_vector_transaction_count": len(pure_lt),
        "round_trip_transaction_count": len(round_trips),
        "development_only": True,
        "decision": summary["decision"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
