"""Source-only audit and exact effect identity for Aave V3 liquidation-threshold changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import cast

import yaml

MANIFEST_SCHEMA_VERSION = "ecophys-aave-v3-liquidation-threshold-source-preflight/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-aave-v3-liquidation-threshold-source-audit/v1"
FAILURE_SCHEMA_VERSION = "ecophys-aave-v3-liquidation-threshold-source-failure/v1"
STAGE = "official_source_effect_identity_only"
SOURCE_REPO = "https://github.com/aave-dao/aave-v3-origin.git"
SOURCE_COMMIT = "cff15de6d1271b0c800fc001f4aea4c263e8a597"
WAD = 10**18
PERCENTAGE_FACTOR = 10_000
UINT256_MAX = 2**256 - 1
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
EXPECTED_FILE_ROLES = frozenset(
    {
        "aave_config_engine",
        "collateral_engine",
        "config_engine_interface",
        "engine_flags",
        "generic_logic",
        "license",
        "pool",
        "pool_configurator",
        "pool_configurator_interface",
        "pool_interface",
        "reserve_configuration",
        "user_configuration",
        "validation_logic",
        "wad_ray_math",
    }
)
REQUIRED_GATES = frozenset(
    {
        "account_state_views",
        "config_engine_effect_class",
        "effect_identity_self_checks",
        "e_mode_routing_explicit",
        "exact_health_factor_accumulator",
        "license_provenance",
        "health_factor_boundary",
        "required_files",
        "required_markers",
        "configuration_transition_has_no_account_write_or_iteration",
        "source_clean",
        "source_commit",
    }
)
ACCESS_TRUE = frozenset({"official_code_blobs_opened", "official_documentation_opened"})
ACCESS_FALSE = frozenset(
    {
        "account_state_rows_opened",
        "chain_event_rows_opened",
        "chain_rpc_used",
        "external_workers_used",
        "governance_payload_rows_opened",
        "gpu_used",
        "paid_data_used",
        "participant_action_rows_opened",
        "realized_response_rows_opened",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "access_boundary",
        "source",
        "files",
        "effect_contract",
        "gates",
        "decision_policy",
        "limitations",
    }
)
SOURCE_KEYS = frozenset({"repo_url", "commit", "reconnaissance_disclosure"})
FILE_KEYS = frozenset({"path", "required_normalized_markers"})
DECISION_KEYS = frozenset({"all_gates_required", "pass", "fail", "authorized_next_stage"})
EFFECT_CONTRACT = {
    "effect_class_id": "base_reserve_liquidation_threshold_strict_decrease",
    "strict_liquidation_threshold_decrease": True,
    "new_liquidation_threshold_must_be_positive": True,
    "ltv_must_be_unchanged": True,
    "liquidation_bonus_must_be_unchanged": True,
    "config_engine_ltv_and_liquidation_bonus_must_use_keep_current_when_applicable": True,
    "changed_reserve_must_not_be_frozen": True,
    "same_transaction_account_relevant_configuration_must_be_unchanged": True,
    "changed_reserve_must_be_enabled_as_collateral": True,
    "account_must_have_positive_changed_collateral_base_value": True,
    "account_must_have_positive_total_debt_base": True,
    "e_mode_override_has_zero_direct_base_threshold_effect": True,
    "counterfactual_holds_t_minus_one_balances_prices_indexes_and_other_configuration_fixed": True,
    "weighted_identity": (
        "weighted_lt_new = weighted_lt_old - changed_collateral_base_value * "
        "(old_liquidation_threshold_bps - new_liquidation_threshold_bps)"
    ),
    "health_factor_identity": (
        "health_factor = wad_div_half_up(weighted_liquidation_threshold_sum, total_debt_base) // 10000"
    ),
    "historical_candidate_requires_version_matched_deployed_code": True,
    "health_factor_boundary_crossing_is_not_sufficient_for_executable_liquidation": True,
    "source_pass_authorizes_event_inventory_design_only": True,
}


@dataclass(frozen=True)
class LiquidationThresholdShockInput:
    """T-minus-one state and a proposed base-reserve threshold-only change."""

    old_weighted_liquidation_threshold_sum: int
    changed_collateral_base_value: int
    total_debt_base: int
    old_liquidation_threshold_bps: int
    new_liquidation_threshold_bps: int
    old_ltv_bps: int
    new_ltv_bps: int
    old_liquidation_bonus_bps: int
    new_liquidation_bonus_bps: int
    using_changed_reserve_as_collateral: bool
    borrowing_any: bool
    e_mode_overrides_changed_reserve: bool


@dataclass(frozen=True)
class LiquidationThresholdEffect:
    """Exact integer counterfactual under the frozen Aave source identity."""

    route_reason: str
    mechanically_exposed: bool
    old_weighted_liquidation_threshold_sum: int
    new_weighted_liquidation_threshold_sum: int
    direct_weighted_sum_decrease: int
    old_health_factor: int
    new_health_factor: int
    direct_health_factor_decrease: int
    crosses_health_factor_boundary: bool
    weighted_identity_holds: bool
    health_factor_monotone_nonincreasing: bool


def wad_div_half_up(numerator: int, denominator: int) -> int:
    """Reproduce Aave's unsigned `wadDiv` half-up integer rule."""

    if isinstance(numerator, bool) or not isinstance(numerator, int):
        raise TypeError("numerator must be an integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int):
        raise TypeError("denominator must be an integer")
    if not (0 <= numerator <= UINT256_MAX):
        raise ValueError("numerator must be uint256")
    if not (0 < denominator <= UINT256_MAX):
        raise ValueError("denominator must be a positive uint256")
    if numerator > (UINT256_MAX - denominator // 2) // WAD:
        raise OverflowError("wadDiv would overflow uint256")
    return (numerator * WAD + denominator // 2) // denominator


def health_factor_from_weighted_sum(weighted_sum: int, total_debt_base: int) -> int:
    """Reproduce the pinned GenericLogic health-factor terminal arithmetic."""

    if any(isinstance(item, bool) or not isinstance(item, int) for item in (weighted_sum, total_debt_base)):
        raise TypeError("weighted sum and debt must be integers")
    if not (0 <= weighted_sum <= UINT256_MAX) or not (0 <= total_debt_base <= UINT256_MAX):
        raise ValueError("weighted sum and debt must be uint256")
    if total_debt_base == 0:
        return UINT256_MAX
    return wad_div_half_up(weighted_sum, total_debt_base) // PERCENTAGE_FACTOR


def validate_strict_effect_class(value: LiquidationThresholdShockInput) -> list[str]:
    """Return violations of the preregistered unbundled LT-decrease effect class."""

    errors: list[str] = []
    integer_fields = (
        "old_weighted_liquidation_threshold_sum",
        "changed_collateral_base_value",
        "total_debt_base",
        "old_liquidation_threshold_bps",
        "new_liquidation_threshold_bps",
        "old_ltv_bps",
        "new_ltv_bps",
        "old_liquidation_bonus_bps",
        "new_liquidation_bonus_bps",
    )
    for field in integer_fields:
        item = getattr(value, field)
        if isinstance(item, bool) or not isinstance(item, int) or not (0 <= item <= UINT256_MAX):
            errors.append(f"{field} must be a uint256 integer")
    for field in (
        "using_changed_reserve_as_collateral",
        "borrowing_any",
        "e_mode_overrides_changed_reserve",
    ):
        if not isinstance(getattr(value, field), bool):
            errors.append(f"{field} must be boolean")
    if errors:
        return sorted(errors)
    if not (0 < value.new_liquidation_threshold_bps < value.old_liquidation_threshold_bps):
        errors.append("liquidation threshold must be a strict decrease to a positive value")
    if value.old_liquidation_threshold_bps > PERCENTAGE_FACTOR:
        errors.append("old liquidation threshold exceeds 10000 bps")
    if value.old_ltv_bps != value.new_ltv_bps:
        errors.append("ltv must remain unchanged")
    if value.old_liquidation_bonus_bps != value.new_liquidation_bonus_bps:
        errors.append("liquidation bonus must remain unchanged")
    if value.old_ltv_bps > value.old_liquidation_threshold_bps:
        errors.append("old ltv exceeds old liquidation threshold")
    if value.new_ltv_bps > value.new_liquidation_threshold_bps:
        errors.append("unchanged ltv exceeds new liquidation threshold")
    return sorted(errors)


def evaluate_liquidation_threshold_shock(
    value: LiquidationThresholdShockInput,
) -> LiquidationThresholdEffect:
    """Evaluate the direct nonlearned event-layer effect with exact integer arithmetic."""

    errors = validate_strict_effect_class(value)
    if errors:
        raise ValueError("invalid liquidation-threshold effect input: " + "; ".join(errors))
    if not value.using_changed_reserve_as_collateral:
        route_reason = "changed_reserve_not_enabled_as_collateral"
    elif not value.borrowing_any or value.total_debt_base == 0:
        route_reason = "no_positive_debt"
    elif value.changed_collateral_base_value == 0:
        route_reason = "no_positive_changed_collateral_value"
    elif value.e_mode_overrides_changed_reserve:
        route_reason = "e_mode_liquidation_threshold_override"
    else:
        route_reason = "base_liquidation_threshold_direct_route"
    mechanically_exposed = route_reason == "base_liquidation_threshold_direct_route"
    threshold_decrease = value.old_liquidation_threshold_bps - value.new_liquidation_threshold_bps
    full_old_contribution = value.changed_collateral_base_value * value.old_liquidation_threshold_bps
    if full_old_contribution > UINT256_MAX:
        raise OverflowError("changed-reserve weighted contribution would overflow uint256")
    if mechanically_exposed and full_old_contribution > value.old_weighted_liquidation_threshold_sum:
        raise ValueError("changed-reserve contribution exceeds the old weighted sum")
    direct_decrease = value.changed_collateral_base_value * threshold_decrease
    if direct_decrease > UINT256_MAX:
        raise OverflowError("direct weighted-sum decrease would overflow uint256")
    if not mechanically_exposed:
        direct_decrease = 0
    if direct_decrease > value.old_weighted_liquidation_threshold_sum:
        raise ValueError("direct decrease exceeds the old weighted liquidation-threshold sum")
    new_weighted_sum = value.old_weighted_liquidation_threshold_sum - direct_decrease
    old_health_factor = health_factor_from_weighted_sum(
        value.old_weighted_liquidation_threshold_sum, value.total_debt_base
    )
    new_health_factor = health_factor_from_weighted_sum(new_weighted_sum, value.total_debt_base)
    return LiquidationThresholdEffect(
        route_reason=route_reason,
        mechanically_exposed=mechanically_exposed,
        old_weighted_liquidation_threshold_sum=value.old_weighted_liquidation_threshold_sum,
        new_weighted_liquidation_threshold_sum=new_weighted_sum,
        direct_weighted_sum_decrease=direct_decrease,
        old_health_factor=old_health_factor,
        new_health_factor=new_health_factor,
        direct_health_factor_decrease=old_health_factor - new_health_factor,
        crosses_health_factor_boundary=(old_health_factor >= WAD and new_health_factor < WAD),
        weighted_identity_holds=(
            new_weighted_sum + direct_decrease == value.old_weighted_liquidation_threshold_sum
        ),
        health_factor_monotone_nonincreasing=new_health_factor <= old_health_factor,
    )


def load_source_preflight(path: str | Path) -> dict[str, object]:
    """Load the source-only Aave effect preflight."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("source-preflight root must be a mapping")
    return cast(dict[str, object], raw)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list):
        return None
    result: list[Mapping[str, object]] = []
    for item in value:
        mapped = _mapping(item)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def _string(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        return None
    return [cast(str, item) for item in value]


def _safe_path(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and path.as_posix() == value


def validate_source_preflight(manifest: Mapping[str, object]) -> list[str]:
    """Validate the immutable source and zero-row boundary."""

    errors: list[str] = []
    if set(manifest) != TOP_LEVEL_KEYS:
        errors.append(f"top level must contain exactly {sorted(TOP_LEVEL_KEYS)}")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"schema_version must equal {MANIFEST_SCHEMA_VERSION}")
    audit_id = _string(manifest.get("audit_id"))
    if audit_id is None or ID_PATTERN.fullmatch(audit_id) is None:
        errors.append("audit_id must be a stable lowercase identifier")
    as_of = _string(manifest.get("as_of"))
    if as_of is None or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")
    if manifest.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")

    access = _mapping(manifest.get("access_boundary"))
    if access is None or set(access) != ACCESS_TRUE | ACCESS_FALSE:
        errors.append("access_boundary keys differ from the frozen source-only contract")
        access = {}
    for key in ACCESS_TRUE:
        if access.get(key) is not True:
            errors.append(f"access_boundary.{key} must be true")
    for key in ACCESS_FALSE:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must be false")

    source = _mapping(manifest.get("source"))
    if source is None or set(source) != SOURCE_KEYS:
        errors.append(f"source must contain exactly {sorted(SOURCE_KEYS)}")
        source = {}
    if source.get("repo_url") != SOURCE_REPO:
        errors.append("source.repo_url differs from the official Aave V3 Origin remote")
    if source.get("commit") != SOURCE_COMMIT or not isinstance(source.get("commit"), str):
        errors.append("source.commit differs from the frozen Aave source commit")
    elif SHA1_PATTERN.fullmatch(cast(str, source["commit"])) is None:
        errors.append("source.commit must be a lowercase 40-character Git SHA")
    if _string(source.get("reconnaissance_disclosure")) is None:
        errors.append("source.reconnaissance_disclosure must be nonempty")

    files = _mapping(manifest.get("files"))
    if files is None or set(files) != EXPECTED_FILE_ROLES:
        errors.append(f"files must contain exactly {sorted(EXPECTED_FILE_ROLES)}")
        files = {}
    seen_paths: set[str] = set()
    for role, raw in files.items():
        record = _mapping(raw)
        if record is None or set(record) != FILE_KEYS:
            errors.append(f"files.{role} must contain exactly {sorted(FILE_KEYS)}")
            continue
        path = record.get("path")
        if not _safe_path(path):
            errors.append(f"files.{role}.path must be a safe normalized relative path")
        elif cast(str, path) in seen_paths:
            errors.append(f"files.{role}.path duplicates another source path")
        else:
            seen_paths.add(cast(str, path))
        markers = _string_list(record.get("required_normalized_markers"))
        if markers is None:
            errors.append(f"files.{role}.required_normalized_markers must be nonempty")
        elif len(markers) != len(set(markers)):
            errors.append(f"files.{role}.required_normalized_markers contains duplicates")
        elif any(marker != _normalize_source(marker) for marker in markers):
            errors.append(f"files.{role}.required_normalized_markers must contain no whitespace")

    if manifest.get("effect_contract") != EFFECT_CONTRACT:
        errors.append("effect_contract differs from the frozen strict LT-decrease identity")
    gates = _string_list(manifest.get("gates"))
    if gates is None or set(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
    policy = _mapping(manifest.get("decision_policy"))
    if policy is None or set(policy) != DECISION_KEYS:
        errors.append(f"decision_policy must contain exactly {sorted(DECISION_KEYS)}")
        policy = {}
    if policy.get("all_gates_required") is not True:
        errors.append("decision_policy.all_gates_required must be true")
    for key in ("pass", "fail", "authorized_next_stage"):
        if _string(policy.get(key)) is None:
            errors.append(f"decision_policy.{key} must be nonempty")
    if _string_list(manifest.get("limitations")) is None:
        errors.append("limitations must be a nonempty string list")
    return sorted(errors)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_source(text: str) -> str:
    return "".join(text.split())


def _extract_function(text: str, signature: str) -> str | None:
    start = text.find(signature)
    if start < 0:
        return None
    brace = text.find("{", start)
    if brace < 0:
        return None
    depth = 0
    quote: str | None = None
    line_comment = False
    block_comment = False
    index = brace
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
        elif block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 1
        elif quote is not None:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = None
        elif char == "/" and next_char == "/":
            line_comment = True
            index += 1
        elif char == "/" and next_char == "*":
            block_comment = True
            index += 1
        elif char in {"'", '"'}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
        index += 1
    return None


def _self_checks() -> dict[str, object]:
    direct_input = LiquidationThresholdShockInput(
        old_weighted_liquidation_threshold_sum=20_000_000_000 * 8_000,
        changed_collateral_base_value=20_000_000_000,
        total_debt_base=15_000_000_000,
        old_liquidation_threshold_bps=8_000,
        new_liquidation_threshold_bps=7_000,
        old_ltv_bps=6_500,
        new_ltv_bps=6_500,
        old_liquidation_bonus_bps=10_500,
        new_liquidation_bonus_bps=10_500,
        using_changed_reserve_as_collateral=True,
        borrowing_any=True,
        e_mode_overrides_changed_reserve=False,
    )
    direct = evaluate_liquidation_threshold_shock(direct_input)
    hidden = evaluate_liquidation_threshold_shock(
        LiquidationThresholdShockInput(
            **{
                **asdict(direct_input),
                "e_mode_overrides_changed_reserve": True,
            }
        )
    )
    no_collateral = evaluate_liquidation_threshold_shock(
        LiquidationThresholdShockInput(
            **{
                **asdict(direct_input),
                "using_changed_reserve_as_collateral": False,
            }
        )
    )
    checks = {
        "direct_weighted_identity": direct.weighted_identity_holds,
        "direct_health_factor_monotonicity": direct.health_factor_monotone_nonincreasing,
        "direct_health_factor_boundary_crossing": direct.crosses_health_factor_boundary,
        "e_mode_override_zero_direct_effect": hidden.direct_weighted_sum_decrease == 0
        and hidden.old_health_factor == hidden.new_health_factor,
        "disabled_collateral_zero_direct_effect": no_collateral.direct_weighted_sum_decrease == 0
        and no_collateral.old_health_factor == no_collateral.new_health_factor,
    }
    return {
        "checks": checks,
        "direct_case": asdict(direct),
        "e_mode_override_case": asdict(hidden),
        "disabled_collateral_case": asdict(no_collateral),
    }


def audit_source_tree(
    root: Path,
    manifest: Mapping[str, object],
    *,
    source_commit: str,
    source_remote: str,
    source_clean: bool,
    collection_commit: str,
    manifest_sha256: str,
) -> dict[str, object]:
    """Audit only the named pinned source files and the exact integer identity."""

    errors = validate_source_preflight(manifest)
    if errors:
        raise ValueError("invalid source preflight: " + "; ".join(errors))
    files = cast(Mapping[str, Mapping[str, object]], manifest["files"])
    file_records: list[dict[str, object]] = []
    texts: dict[str, str] = {}
    marker_results: dict[str, dict[str, bool]] = {}
    all_files = True
    for role in sorted(files):
        record = files[role]
        path_text = cast(str, record["path"])
        path = root / path_text
        exists = path.is_file()
        all_files = all_files and exists
        text = path.read_text(encoding="utf-8") if exists else ""
        normalized = _normalize_source(text)
        markers = cast(Sequence[str], record["required_normalized_markers"])
        results = {marker: marker in normalized for marker in markers}
        texts[role] = text
        marker_results[role] = results
        file_records.append(
            {
                "role": role,
                "path": path_text,
                "exists": exists,
                "byte_count": path.stat().st_size if exists else 0,
                "sha256": _sha256(path) if exists else None,
                "marker_count": len(results),
                "marker_pass_count": sum(results.values()),
            }
        )

    def roles_pass(*roles: str) -> bool:
        return all(
            role in marker_results and bool(marker_results[role]) and all(marker_results[role].values())
            for role in roles
        )

    function = _extract_function(texts.get("pool_configurator", ""), "function configureReserveAsCollateral(")
    normalized_function = "" if function is None else _normalize_source(function)
    transition_checks = {
        "function_found": function is not None,
        "risk_or_pool_admin_only": "onlyRiskOrPoolAdmins" in normalized_function,
        "writes_reserve_configuration": "_pool.setConfiguration(asset,currentConfig);" in normalized_function,
        "writes_liquidation_threshold": (
            "currentConfig.setLiquidationThreshold(liquidationThreshold);" in normalized_function
        ),
        "emits_collateral_configuration": "emitCollateralConfigurationChanged(" in normalized_function,
        "no_user_configuration_reference": all(
            marker not in normalized_function
            for marker in ("_usersConfig", "userConfig", "getUserAccountData")
        ),
        "no_account_iteration": "for(" not in normalized_function and "while(" not in normalized_function,
    }
    self_checks = _self_checks()
    self_check_values = cast(Mapping[str, bool], self_checks["checks"])
    source = cast(Mapping[str, object], manifest["source"])
    license_markers_pass = roles_pass("license")
    gates = {
        "source_commit": source_commit == source["commit"] and source_remote == source["repo_url"],
        "source_clean": source_clean,
        "required_files": all_files and len(file_records) == len(EXPECTED_FILE_ROLES),
        "required_markers": all(results and all(results.values()) for results in marker_results.values()),
        "configuration_transition_has_no_account_write_or_iteration": all(transition_checks.values()),
        "exact_health_factor_accumulator": roles_pass("generic_logic", "wad_ray_math"),
        "e_mode_routing_explicit": roles_pass("generic_logic", "user_configuration"),
        "account_state_views": roles_pass("pool", "pool_interface", "reserve_configuration"),
        "health_factor_boundary": roles_pass("validation_logic"),
        "config_engine_effect_class": roles_pass(
            "config_engine_interface", "aave_config_engine", "collateral_engine", "engine_flags"
        ),
        "effect_identity_self_checks": bool(self_check_values) and all(self_check_values.values()),
        "license_provenance": license_markers_pass,
    }
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == REQUIRED_GATES and all(gates.values())
    decision = policy["pass"] if passed else policy["fail"]
    inventory_sha256 = hashlib.sha256(
        json.dumps(file_records, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "collection_commit": collection_commit,
        "manifest_sha256": manifest_sha256,
        "source": {
            "repo_url": source_remote,
            "commit": source_commit,
            "clean": source_clean,
            "examined_file_count": len(file_records),
            "examined_file_inventory_sha256": inventory_sha256,
            "files": file_records,
            "raw_source_retained_in_artifact": False,
        },
        "marker_results": marker_results,
        "reserve_transition_checks": transition_checks,
        "effect_contract": manifest["effect_contract"],
        "effect_identity_self_checks": self_checks,
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {
            "pass": sum(gates.values()),
            "fail": sum(not value for value in gates.values()),
        },
        "decision": decision,
        "authorized_next_stage": policy["authorized_next_stage"] if passed else None,
        "limitations": manifest["limitations"],
    }


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--failure", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run one sealed local source audit from an exact protocol commit."""

    args = _build_parser().parse_args()
    if args.output.exists() or args.failure.exists():
        raise FileExistsError("refusing to overwrite an Aave source-audit outcome")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest_sha256 = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    try:
        manifest = load_source_preflight(args.manifest)
        errors = validate_source_preflight(manifest)
        if errors:
            raise ValueError("invalid source preflight: " + "; ".join(errors))
        source_root = args.source_repo.resolve()
        artifact = audit_source_tree(
            source_root,
            manifest,
            source_commit=_git_value(source_root, ["rev-parse", "HEAD"]),
            source_remote=_git_value(source_root, ["config", "--get", "remote.origin.url"]),
            source_clean=not bool(_git_value(source_root, ["status", "--porcelain"])),
            collection_commit=current_commit,
            manifest_sha256=manifest_sha256,
        )
    except Exception as error:
        args.failure.parent.mkdir(parents=True, exist_ok=True)
        _write_json(
            args.failure,
            {
                "schema_version": FAILURE_SCHEMA_VERSION,
                "collection_commit": current_commit,
                "manifest_sha256": manifest_sha256,
                "exception": {
                    "class": type(error).__name__,
                    "message": str(error)[:2_000],
                },
                "scientific_decision_reached": False,
                "decision": "INFRASTRUCTURE_FAILURE_NO_AAVE_SOURCE_EFFECT_RESULT",
                "raw_source_retained": False,
            },
        )
        raise
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.output, artifact)
    print(
        json.dumps(
            {
                "decision": artifact["decision"],
                "gates": artifact["gate_counts"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
