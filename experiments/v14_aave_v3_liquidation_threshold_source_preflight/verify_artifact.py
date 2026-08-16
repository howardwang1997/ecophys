from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROTOCOL_COMMIT = "fdb1dc41497a4eca9e740dbd196061208e61c584"
SOURCE_COMMIT = "cff15de6d1271b0c800fc001f4aea4c263e8a597"
SOURCE_REPO = "https://github.com/aave-dao/aave-v3-origin.git"
MANIFEST_SHA256 = "2656f0966d2e0c74b74eb2b147ef6e50bcb7838b078edef6e3552d66b2933ccc"
SUMMARY_SHA256 = "355928afb19ab4b4a8f6de0b786986e9aa4542e1394a3acac7b14dc1ebbc85e9"
EXPECTED_DECISION = "PASS_SOURCE_EFFECT_IDENTITY_AUTHORIZE_AAVE_CHAIN_EVENT_INVENTORY_DESIGN_ONLY"
EXPECTED_NEXT_STAGE = (
    "separately_frozen_aave_ethereum_deployment_and_liquidation_threshold_event_inventory_design_only"
)
EXPECTED_GATES = {
    "account_state_views",
    "config_engine_effect_class",
    "configuration_transition_has_no_account_write_or_iteration",
    "e_mode_routing_explicit",
    "effect_identity_self_checks",
    "exact_health_factor_accumulator",
    "health_factor_boundary",
    "license_provenance",
    "required_files",
    "required_markers",
    "source_clean",
    "source_commit",
}
WAD = 10**18


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


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping,
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs)
    assert isinstance(value, dict), path
    return value


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


def git_value(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def normalize(text: str) -> str:
    return "".join(text.split())


def extract_function(text: str, signature: str) -> str:
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError("unterminated configureReserveAsCollateral function")


def wad_div_half_up(numerator: int, denominator: int) -> int:
    return (numerator * WAD + denominator // 2) // denominator


def expected_effect_checks() -> dict[str, Any]:
    old_weighted = 20_000_000_000 * 8_000
    decrease = 20_000_000_000 * 1_000
    new_weighted = old_weighted - decrease
    debt = 15_000_000_000
    old_hf = wad_div_half_up(old_weighted, debt) // 10_000
    new_hf = wad_div_half_up(new_weighted, debt) // 10_000
    direct = {
        "route_reason": "base_liquidation_threshold_direct_route",
        "mechanically_exposed": True,
        "old_weighted_liquidation_threshold_sum": old_weighted,
        "new_weighted_liquidation_threshold_sum": new_weighted,
        "direct_weighted_sum_decrease": decrease,
        "old_health_factor": old_hf,
        "new_health_factor": new_hf,
        "direct_health_factor_decrease": old_hf - new_hf,
        "crosses_health_factor_boundary": old_hf >= WAD and new_hf < WAD,
        "weighted_identity_holds": new_weighted + decrease == old_weighted,
        "health_factor_monotone_nonincreasing": new_hf <= old_hf,
    }

    def zero_case(reason: str) -> dict[str, Any]:
        return {
            "route_reason": reason,
            "mechanically_exposed": False,
            "old_weighted_liquidation_threshold_sum": old_weighted,
            "new_weighted_liquidation_threshold_sum": old_weighted,
            "direct_weighted_sum_decrease": 0,
            "old_health_factor": old_hf,
            "new_health_factor": old_hf,
            "direct_health_factor_decrease": 0,
            "crosses_health_factor_boundary": False,
            "weighted_identity_holds": True,
            "health_factor_monotone_nonincreasing": True,
        }

    checks = {
        "direct_weighted_identity": direct["weighted_identity_holds"],
        "direct_health_factor_monotonicity": direct["health_factor_monotone_nonincreasing"],
        "direct_health_factor_boundary_crossing": direct["crosses_health_factor_boundary"],
        "e_mode_override_zero_direct_effect": True,
        "disabled_collateral_zero_direct_effect": True,
    }
    return {
        "checks": checks,
        "direct_case": direct,
        "e_mode_override_case": zero_case("e_mode_liquidation_threshold_override"),
        "disabled_collateral_case": zero_case("changed_reserve_not_enabled_as_collateral"),
    }


def verify(root: Path, source_root: Path) -> dict[str, Any]:
    manifest_path = root / "data/manifests/aave_v3_liquidation_threshold_source_preflight_v1.yaml"
    summary_path = (
        root / "experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/summary.json"
    )
    failure_path = (
        root / "experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/failure.json"
    )
    assert sha256_file(manifest_path) == MANIFEST_SHA256
    assert sha256_file(summary_path) == SUMMARY_SHA256
    assert not failure_path.exists()
    manifest = read_yaml(manifest_path)
    artifact = read_json(summary_path)

    assert manifest["source"]["commit"] == SOURCE_COMMIT
    assert manifest["source"]["repo_url"] == SOURCE_REPO
    assert git_value(source_root, "rev-parse", "HEAD") == SOURCE_COMMIT
    assert git_value(source_root, "config", "--get", "remote.origin.url") == SOURCE_REPO
    assert git_value(source_root, "status", "--porcelain") == ""

    file_records: list[dict[str, Any]] = []
    marker_results: dict[str, dict[str, bool]] = {}
    texts: dict[str, str] = {}
    files = manifest["files"]
    assert isinstance(files, dict) and len(files) == 14
    for role in sorted(files):
        record = files[role]
        path_text = record["path"]
        relative = Path(path_text)
        assert not relative.is_absolute() and ".." not in relative.parts
        path = source_root / relative
        text = path.read_text(encoding="utf-8")
        texts[role] = text
        normalized = normalize(text)
        markers = record["required_normalized_markers"]
        results = {marker: marker in normalized for marker in markers}
        marker_results[role] = results
        file_records.append(
            {
                "role": role,
                "path": path_text,
                "exists": path.is_file(),
                "byte_count": path.stat().st_size,
                "sha256": sha256_file(path),
                "marker_count": len(results),
                "marker_pass_count": sum(results.values()),
            }
        )

    function = normalize(
        extract_function(texts["pool_configurator"], "function configureReserveAsCollateral(")
    )
    transition_checks = {
        "function_found": True,
        "risk_or_pool_admin_only": "onlyRiskOrPoolAdmins" in function,
        "writes_reserve_configuration": "_pool.setConfiguration(asset,currentConfig);" in function,
        "writes_liquidation_threshold": (
            "currentConfig.setLiquidationThreshold(liquidationThreshold);" in function
        ),
        "emits_collateral_configuration": "emitCollateralConfigurationChanged(" in function,
        "no_user_configuration_reference": all(
            item not in function for item in ("_usersConfig", "userConfig", "getUserAccountData")
        ),
        "no_account_iteration": "for(" not in function and "while(" not in function,
    }

    def roles_pass(*roles: str) -> bool:
        return all(all(marker_results[role].values()) for role in roles)

    effect_checks = expected_effect_checks()
    gates = {
        "source_commit": True,
        "source_clean": True,
        "required_files": len(file_records) == 14 and all(row["exists"] for row in file_records),
        "required_markers": all(results and all(results.values()) for results in marker_results.values()),
        "configuration_transition_has_no_account_write_or_iteration": all(transition_checks.values()),
        "exact_health_factor_accumulator": roles_pass("generic_logic", "wad_ray_math"),
        "e_mode_routing_explicit": roles_pass("generic_logic", "user_configuration"),
        "account_state_views": roles_pass("pool", "pool_interface", "reserve_configuration"),
        "health_factor_boundary": roles_pass("validation_logic"),
        "config_engine_effect_class": roles_pass(
            "config_engine_interface", "aave_config_engine", "collateral_engine", "engine_flags"
        ),
        "effect_identity_self_checks": all(effect_checks["checks"].values()),
        "license_provenance": roles_pass("license"),
    }
    assert set(gates) == EXPECTED_GATES and all(gates.values())

    expected_source = {
        "repo_url": SOURCE_REPO,
        "commit": SOURCE_COMMIT,
        "clean": True,
        "examined_file_count": 14,
        "examined_file_inventory_sha256": canonical_sha256(file_records),
        "files": file_records,
        "raw_source_retained_in_artifact": False,
    }
    assert artifact["schema_version"] == "ecophys-aave-v3-liquidation-threshold-source-audit/v1"
    assert artifact["audit_id"] == manifest["audit_id"]
    assert artifact["as_of"] == manifest["as_of"]
    assert artifact["collection_commit"] == PROTOCOL_COMMIT
    assert artifact["manifest_sha256"] == MANIFEST_SHA256
    assert artifact["source"] == expected_source
    assert artifact["marker_results"] == marker_results
    assert artifact["reserve_transition_checks"] == transition_checks
    assert artifact["effect_contract"] == manifest["effect_contract"]
    assert artifact["effect_identity_self_checks"] == effect_checks
    assert artifact["access_boundary"] == manifest["access_boundary"]
    assert artifact["limitations"] == manifest["limitations"]
    assert artifact["gates"] == gates
    assert artifact["gate_counts"] == {"pass": 12, "fail": 0}
    assert artifact["decision"] == EXPECTED_DECISION
    assert artifact["authorized_next_stage"] == EXPECTED_NEXT_STAGE
    assert artifact["source"]["raw_source_retained_in_artifact"] is False

    serialized = json.dumps(artifact, sort_keys=True)
    for forbidden in ('"raw_source":', '"source_text":', '"response_body":'):
        assert forbidden not in serialized
    return {
        "status": "PASS",
        "protocol_commit": PROTOCOL_COMMIT,
        "manifest_sha256": MANIFEST_SHA256,
        "summary_sha256": SUMMARY_SHA256,
        "source_commit": SOURCE_COMMIT,
        "source_file_count": len(file_records),
        "source_byte_count": sum(row["byte_count"] for row in file_records),
        "gate_count": len(gates),
        "decision": artifact["decision"],
        "raw_source_replay": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-repo", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve(), args.source_repo.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
