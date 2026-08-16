"""Offline structural summary of Aave Configurator transaction bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from itertools import groupby
from pathlib import Path
from typing import cast

import yaml

SCHEMA_VERSION = "ecophys-aave-v3-bundle-structure-feasibility/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-aave-v3-bundle-structure-summary/v1"
AUDIT_ID = "aave_v3_ethereum_bundle_structure_feasibility_v1"
AS_OF = "2026-08-16"
STAGE = "post_a1a_development_only_offline_bundle_structure"
PARENT_DECISION = "FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED"
FROZEN_PARENTS = {
    "directory_path": "experiments/v14_aave_v3_lt_event_directory/artifacts/event_directory.json",
    "directory_sha256": "1d1d73b5f5ba51c60841a411edf563317f143e9599e3eac958643895c90648ec",
    "summary_path": "experiments/v14_aave_v3_lt_event_directory/artifacts/summary.json",
    "summary_sha256": "ff3e120920b766957353c59c02341c42990a18818a751d62da6e1a6798a3c1bb",
    "manifest_path": "data/manifests/aave_v3_ethereum_lt_event_directory_v1.yaml",
    "manifest_sha256": "860cd0338414508d3a447cd522114cc3dbaa3193624863c9326091e0f1fa2763",
    "expected_parent_decision": PARENT_DECISION,
}
CONFIGURATION_FIELDS = ("ltv", "liquidation_threshold", "liquidation_bonus")
REQUIRED_GATES = frozenset(
    {
        "parent_hashes_and_decision",
        "exact_parent_log_identity_partition",
        "deterministic_transaction_grouping",
        "predecessor_unknown_not_imputed",
        "exact_net_vector_reconstruction",
        "round_trip_detection",
        "no_network_or_participant_outcome_access",
    }
)
TRUE_ACCESS_KEYS = frozenset({"normalized_parent_logs_read", "parent_summary_read"})
FALSE_ACCESS_KEYS = frozenset(
    {
        "network_used",
        "transaction_or_receipt_rows_opened",
        "calldata_or_call_trace_rows_opened",
        "historical_state_calls_used",
        "account_state_rows_opened",
        "participant_action_rows_opened",
        "liquidation_rows_opened",
        "price_or_oracle_value_rows_opened",
        "realized_response_rows_opened",
        "paid_data_used",
        "external_workers_used",
        "gpu_used",
    }
)
FROZEN_DECISION_POLICY = {
    "all_gates_required": True,
    "complete": "COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY",
    "fail": "FAIL_BUNDLE_STRUCTURE_ARTIFACT_INTEGRITY_NO_NEXT_STAGE",
    "authorized_next_stage": "separately_frozen_historical_abi_state_and_receipt_vector_compiler_protocol_design_only",
}


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        return None
    return [cast(Mapping[str, object], item) for item in value]


def load_bundle_manifest(path: str | Path) -> dict[str, object]:
    """Load the development-only bundle manifest."""

    value: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("bundle manifest root must be a mapping")
    return cast(dict[str, object], value)


def load_json_mapping(path: str | Path) -> dict[str, object]:
    """Load one JSON mapping."""

    value: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON mapping")
    return cast(dict[str, object], value)


def load_json_mapping_list(path: str | Path) -> list[Mapping[str, object]]:
    """Load one JSON array of mappings."""

    value: object = json.loads(Path(path).read_text(encoding="utf-8"))
    records = _mapping_list(value)
    if records is None:
        raise ValueError(f"{path} must contain a JSON mapping array")
    return records


def sha256_file(path: Path) -> str:
    """Hash one file without retaining its body."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_bundle_manifest(manifest: Mapping[str, object]) -> list[str]:
    """Validate immutable parents, access locks, and vector definitions."""

    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version differs from the frozen contract")
    if manifest.get("audit_id") != AUDIT_ID or manifest.get("as_of") != AS_OF:
        errors.append("audit_id or as_of differs from the frozen contract")
    if manifest.get("stage") != STAGE:
        errors.append("stage differs from the frozen contract")
    if manifest.get("parents") != FROZEN_PARENTS:
        errors.append("parents differ from the frozen contract")
    if manifest.get("decision_policy") != FROZEN_DECISION_POLICY:
        errors.append("decision_policy differs from the frozen contract")
    gates = manifest.get("gates")
    if not isinstance(gates, list) or set(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append("gates differ from the frozen set")
    access = _mapping(manifest.get("access_boundary"))
    if access is None or set(access) != TRUE_ACCESS_KEYS | FALSE_ACCESS_KEYS:
        errors.append("access_boundary differs from the frozen key set")
    else:
        for key in sorted(TRUE_ACCESS_KEYS):
            if access.get(key) is not True:
                errors.append(f"{key} must be true")
        for key in sorted(FALSE_ACCESS_KEYS):
            if access.get(key) is not False:
                errors.append(f"{key} must be false")
    disclosure = _mapping(manifest.get("development_disclosure"))
    if (
        disclosure is None
        or disclosure.get("parent_treatment_metadata_already_opened") is not True
        or disclosure.get("bundle_count_and_shape_explored_before_freeze") is not True
        or disclosure.get("confirmatory_or_blind_claim_permitted") is not False
        or disclosure.get("participant_outcomes_opened") is not False
    ):
        errors.append("development disclosure must remain explicit")
    rule = _mapping(manifest.get("vectorization_rule"))
    if rule is None or rule.get("configuration_fields") != list(CONFIGURATION_FIELDS):
        errors.append("configuration fields differ from the frozen order")
    return errors


def validate_parent_artifacts(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Validate all parent hashes and the immutable A1a failure decision."""

    errors: list[str] = []
    parents = _mapping(manifest.get("parents"))
    if parents is None:
        return ["parents must be a mapping"]
    root_path = Path(root)
    for path_key, hash_key in (
        ("directory_path", "directory_sha256"),
        ("summary_path", "summary_sha256"),
        ("manifest_path", "manifest_sha256"),
    ):
        relative = parents.get(path_key)
        expected = parents.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append(f"invalid parent fields {path_key}/{hash_key}")
            continue
        path = root_path / relative
        if not path.is_file():
            errors.append(f"missing parent artifact: {relative}")
        elif sha256_file(path) != expected:
            errors.append(f"parent hash mismatch: {relative}")
    summary_path = parents.get("summary_path")
    if isinstance(summary_path, str) and (root_path / summary_path).is_file():
        try:
            summary = load_json_mapping(root_path / summary_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"cannot parse parent summary: {exc}")
        else:
            if summary.get("decision") != parents.get("expected_parent_decision"):
                errors.append("parent decision differs from the frozen A1a failure")
    return errors


def _sort_key(item: Mapping[str, object]) -> tuple[int, int, int, str]:
    return (
        cast(int, item["block_number"]),
        cast(int, item["transaction_index"]),
        cast(int, item["log_index"]),
        cast(str, item["address"]),
    )


def _transaction_key(item: Mapping[str, object]) -> tuple[str, str, int]:
    return (
        cast(str, item["block_hash"]),
        cast(str, item["transaction_hash"]),
        cast(int, item["transaction_index"]),
    )


def _configuration(item: Mapping[str, object]) -> dict[str, int]:
    return {field: cast(int, item[field]) for field in CONFIGURATION_FIELDS}


def _topic_counts(items: Iterable[Mapping[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(cast(str, item["topic0"]) for item in items).items()))


def build_transaction_bundles(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Build exact emitted-configuration net vectors by transaction."""

    ordered = sorted(records, key=_sort_key)
    predecessor_by_asset: dict[str, Mapping[str, object]] = {}
    bundles: list[dict[str, object]] = []
    for _, grouped in groupby(ordered, key=_transaction_key):
        transaction_records = list(grouped)
        configurator = [item for item in transaction_records if item["role"] == "configurator"]
        collateral = [
            item for item in configurator if item["event_type"] == "collateral_configuration_changed"
        ]
        if not collateral:
            continue
        collateral_by_asset: dict[str, list[Mapping[str, object]]] = defaultdict(list)
        for item in collateral:
            collateral_by_asset[cast(str, item["asset"])].append(item)
        asset_records: list[dict[str, object]] = []
        net_changes: list[dict[str, object]] = []
        for asset in sorted(collateral_by_asset):
            sequence = sorted(collateral_by_asset[asset], key=_sort_key)
            predecessor = predecessor_by_asset.get(asset)
            final = sequence[-1]
            predecessor_configuration = _configuration(predecessor) if predecessor is not None else None
            final_configuration = _configuration(final)
            asset_changes: list[dict[str, object]] = []
            if predecessor_configuration is not None:
                for field in CONFIGURATION_FIELDS:
                    old_value = predecessor_configuration[field]
                    new_value = final_configuration[field]
                    if old_value != new_value:
                        change = {
                            "asset": asset,
                            "field": field,
                            "old_value": old_value,
                            "new_value": new_value,
                            "delta": new_value - old_value,
                        }
                        asset_changes.append(change)
                        net_changes.append(change)
            sequence_values = [_configuration(item) for item in sequence]
            round_trip = (
                predecessor_configuration is not None
                and final_configuration == predecessor_configuration
                and any(value != predecessor_configuration for value in sequence_values)
            )
            asset_records.append(
                {
                    "asset": asset,
                    "predecessor_known": predecessor is not None,
                    "predecessor_block_number": predecessor["block_number"]
                    if predecessor is not None
                    else None,
                    "predecessor_transaction_hash": predecessor["transaction_hash"]
                    if predecessor is not None
                    else None,
                    "predecessor_configuration": predecessor_configuration,
                    "sequence": [
                        {"log_index": item["log_index"], **_configuration(item)} for item in sequence
                    ],
                    "final_configuration": final_configuration,
                    "net_changes": asset_changes,
                    "returns_to_predecessor_after_intermediate_change": round_trip,
                }
            )
        for asset, sequence in collateral_by_asset.items():
            predecessor_by_asset[asset] = max(sequence, key=_sort_key)
        other_configurator = [
            item for item in configurator if item["event_type"] != "collateral_configuration_changed"
        ]
        field_counts = dict(sorted(Counter(cast(str, item["field"]) for item in net_changes).items()))
        first = collateral[0]
        bundles.append(
            {
                "block_number": first["block_number"],
                "block_hash": first["block_hash"],
                "transaction_index": first["transaction_index"],
                "transaction_hash": first["transaction_hash"],
                "configurator_log_count": len(configurator),
                "collateral_configuration_event_count": len(collateral),
                "other_configurator_event_count": len(other_configurator),
                "other_configurator_topic0_counts": _topic_counts(other_configurator),
                "distinct_collateral_asset_count": len(collateral_by_asset),
                "predecessor_known_asset_count": sum(
                    cast(bool, item["predecessor_known"]) for item in asset_records
                ),
                "predecessor_unknown_asset_count": sum(
                    not cast(bool, item["predecessor_known"]) for item in asset_records
                ),
                "net_changed_asset_count": len({cast(str, item["asset"]) for item in net_changes}),
                "net_changed_dimension_count": len(net_changes),
                "net_change_field_counts": field_counts,
                "net_liquidation_threshold_decrease_count": sum(
                    item["field"] == "liquidation_threshold" and cast(int, item["delta"]) < 0
                    for item in net_changes
                ),
                "net_liquidation_threshold_increase_count": sum(
                    item["field"] == "liquidation_threshold" and cast(int, item["delta"]) > 0
                    for item in net_changes
                ),
                "pure_liquidation_threshold_vector": bool(net_changes)
                and all(item["field"] == "liquidation_threshold" for item in net_changes),
                "only_semantically_decoded_configurator_events": not other_configurator,
                "contains_round_trip": any(
                    cast(bool, item["returns_to_predecessor_after_intermediate_change"])
                    for item in asset_records
                ),
                "asset_records": asset_records,
                "net_changes": net_changes,
            }
        )
    return bundles


def _distribution(values: Iterable[int]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items())}


def summarize_bundles(
    manifest: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
    bundles: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Summarize bundle structure without a post-exploration support threshold."""

    identities = [(item["block_hash"], item["transaction_hash"], item["log_index"]) for item in records]
    collateral_events = [item for item in records if item["event_type"] == "collateral_configuration_changed"]
    configurator_events = [item for item in records if item["role"] == "configurator"]
    net_changed = [item for item in bundles if cast(int, item["net_changed_dimension_count"]) > 0]
    net_lt_decrease = [
        item for item in bundles if cast(int, item["net_liquidation_threshold_decrease_count"]) > 0
    ]
    pure_lt = [item for item in bundles if item["pure_liquidation_threshold_vector"] is True]
    round_trips = [item for item in bundles if item["contains_round_trip"] is True]
    predecessor_unknown_assets = sum(cast(int, item["predecessor_unknown_asset_count"]) for item in bundles)
    access = cast(Mapping[str, object], manifest["access_boundary"])
    access_ok = all(access[key] is True for key in TRUE_ACCESS_KEYS) and all(
        access[key] is False for key in FALSE_ACCESS_KEYS
    )
    gates = {
        "parent_hashes_and_decision": True,
        "exact_parent_log_identity_partition": len(identities) == len(set(identities)) == len(records),
        "deterministic_transaction_grouping": len(bundles)
        == len({cast(str, item["transaction_hash"]) for item in collateral_events}),
        "predecessor_unknown_not_imputed": all(
            cast(int, item["predecessor_known_asset_count"])
            + cast(int, item["predecessor_unknown_asset_count"])
            == cast(int, item["distinct_collateral_asset_count"])
            for item in bundles
        ),
        "exact_net_vector_reconstruction": all(
            cast(int, item["net_changed_dimension_count"]) == len(cast(Sequence[object], item["net_changes"]))
            for item in bundles
        ),
        "round_trip_detection": all(
            item["contains_round_trip"]
            is any(
                cast(bool, asset["returns_to_predecessor_after_intermediate_change"])
                for asset in cast(Sequence[Mapping[str, object]], item["asset_records"])
            )
            for item in bundles
        ),
        "no_network_or_participant_outcome_access": access_ok,
    }
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    completed = set(gates) == REQUIRED_GATES and all(gates.values())
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "parents": manifest["parents"],
        "development_disclosure": manifest["development_disclosure"],
        "parent_inventory": {
            "normalized_log_count": len(records),
            "configurator_log_count": len(configurator_events),
            "collateral_configuration_event_count": len(collateral_events),
            "unique_configurator_topic0_count": len(
                {cast(str, item["topic0"]) for item in configurator_events}
            ),
            "unique_log_identity_count": len(set(identities)),
        },
        "bundle_summary": {
            "transaction_count": len(bundles),
            "transaction_with_any_known_net_change_count": len(net_changed),
            "transaction_with_net_lt_decrease_count": len(net_lt_decrease),
            "pure_emitted_lt_vector_transaction_count": len(pure_lt),
            "round_trip_transaction_count": len(round_trips),
            "transaction_with_only_semantically_decoded_configurator_events_count": sum(
                item["only_semantically_decoded_configurator_events"] is True for item in bundles
            ),
            "predecessor_unknown_asset_occurrence_count": predecessor_unknown_assets,
            "configurator_log_count_distribution": _distribution(
                cast(int, item["configurator_log_count"]) for item in bundles
            ),
            "collateral_event_count_distribution": _distribution(
                cast(int, item["collateral_configuration_event_count"]) for item in bundles
            ),
            "net_changed_dimension_count_distribution": _distribution(
                cast(int, item["net_changed_dimension_count"]) for item in bundles
            ),
            "maximum_configurator_log_count": max(
                cast(int, item["configurator_log_count"]) for item in bundles
            ),
            "maximum_net_changed_dimension_count": max(
                cast(int, item["net_changed_dimension_count"]) for item in bundles
            ),
            "other_configurator_topic0_counts": _topic_counts(
                item
                for item in configurator_events
                if item["event_type"] != "collateral_configuration_changed"
            ),
        },
        "transaction_bundles": list(bundles),
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {"pass": sum(gates.values()), "fail": sum(not value for value in gates.values())},
        "decision": policy["complete"] if completed else policy["fail"],
        "authorized_next_stage": policy["authorized_next_stage"] if completed else None,
        "limitations": manifest["limitations"],
    }


def run_bundle_feasibility(
    manifest: Mapping[str, object],
    *,
    root: str | Path = ".",
) -> dict[str, object]:
    """Run the deterministic offline summary over the immutable A1a directory."""

    errors = validate_bundle_manifest(manifest)
    errors.extend(validate_parent_artifacts(manifest, root))
    if errors:
        raise ValueError("invalid bundle feasibility contract: " + "; ".join(sorted(set(errors))))
    parents = cast(Mapping[str, object], manifest["parents"])
    directory_path = Path(root) / cast(str, parents["directory_path"])
    records = load_json_mapping_list(directory_path)
    bundles = build_transaction_bundles(records)
    return summarize_bundles(manifest, records, bundles)


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Write one deterministic development-only bundle summary."""

    args = _build_parser().parse_args()
    if args.summary.exists():
        raise FileExistsError(f"refusing to overwrite {args.summary}")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("bundle worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_bundle_manifest(args.manifest)
    summary = run_bundle_feasibility(manifest, root=root)
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = sha256_file(args.manifest)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bundle_summary = cast(Mapping[str, object], summary["bundle_summary"])
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "transactions": bundle_summary["transaction_count"],
                "net_changed_transactions": bundle_summary["transaction_with_any_known_net_change_count"],
                "net_lt_decrease_transactions": bundle_summary["transaction_with_net_lt_decrease_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
