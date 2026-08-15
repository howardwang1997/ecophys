"""Zero-row metadata audit for a pinned Compound III Comet source tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import cast

import yaml

MANIFEST_SCHEMA_VERSION = "ecophys-compound-v3-metadata-preflight/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-compound-v3-metadata-audit/v1"
STAGE = "official_source_metadata_only"
REQUIRED_GATES = frozenset(
    {
        "action_surface",
        "configuration_surface",
        "license_provenance",
        "market_files",
        "market_schema",
        "source_clean",
        "source_commit",
        "state_surface",
        "unique_comet_roots",
    }
)
ACCESS_FLAGS = frozenset(
    {
        "account_state_rows_opened",
        "chain_rpc_used",
        "external_workers_used",
        "gpu_used",
        "governance_payload_rows_opened",
        "official_code_blobs_opened",
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
        "markets",
        "contracts",
        "required_configuration_keys",
        "required_rate_keys",
        "required_root_keys",
        "required_action_markers",
        "required_configurator_markers",
        "required_storage_markers",
        "license_contract",
        "gates",
        "decision_policy",
        "limitations",
    }
)
SOURCE_KEYS = frozenset({"repo_url", "commit", "reconnaissance_disclosure"})
MARKET_KEYS = frozenset({"market_id", "configuration_path", "roots_path", "migrations_path"})
CONTRACT_KEYS = frozenset({"action_interface", "configurator", "storage"})
LICENSE_KEYS = frozenset({"path", "expected_markers"})
DECISION_KEYS = frozenset({"pass", "fail", "authorized_next_stage", "all_gates_required"})
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")


def load_metadata_preflight(path: str | Path) -> dict[str, object]:
    """Load a Compound metadata-preflight manifest."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("metadata-preflight root must be a mapping")
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
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: object, *, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        errors.append(f"{path} must be a non-empty list of strings")
        return []
    return [cast(str, item).strip() for item in value]


def _relative_path(value: object, *, path: str, errors: list[str]) -> str | None:
    text = _string(value)
    if text is None:
        errors.append(f"{path} must be a non-empty relative path")
        return None
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts or text != pure.as_posix():
        errors.append(f"{path} must be a normalized relative POSIX path")
        return None
    return text


def validate_metadata_preflight(manifest: Mapping[str, object]) -> list[str]:
    """Return structural and access-boundary violations."""

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

    boundary = _mapping(manifest.get("access_boundary"))
    if boundary is None or set(boundary) != ACCESS_FLAGS:
        errors.append(f"access_boundary must contain exactly {sorted(ACCESS_FLAGS)}")
        boundary = {}
    for flag in ACCESS_FLAGS - {"official_code_blobs_opened"}:
        if boundary.get(flag) is not False:
            errors.append(f"access_boundary.{flag} must be false")
    if boundary.get("official_code_blobs_opened") is not True:
        errors.append("access_boundary.official_code_blobs_opened must be true")

    source = _mapping(manifest.get("source"))
    if source is None or set(source) != SOURCE_KEYS:
        errors.append(f"source must contain exactly {sorted(SOURCE_KEYS)}")
        source = {}
    if source.get("repo_url") != "https://github.com/compound-finance/comet.git":
        errors.append("source.repo_url must pin the official Compound Comet Git remote")
    commit = _string(source.get("commit"))
    if commit is None or SHA_PATTERN.fullmatch(commit) is None:
        errors.append("source.commit must be a lowercase 40-character Git SHA")
    if _string(source.get("reconnaissance_disclosure")) is None:
        errors.append("source.reconnaissance_disclosure must be non-empty")

    markets = _mapping_list(manifest.get("markets"))
    if not markets:
        errors.append("markets must be a non-empty list")
        markets = []
    market_ids: set[str] = set()
    paths: set[str] = set()
    for index, market in enumerate(markets):
        market_path = f"markets[{index}]"
        if set(market) != MARKET_KEYS:
            errors.append(f"{market_path} must contain exactly {sorted(MARKET_KEYS)}")
        market_id = _string(market.get("market_id"))
        if market_id is None or ID_PATTERN.fullmatch(market_id) is None or market_id in market_ids:
            errors.append(f"{market_path}.market_id must be unique and stable")
        else:
            market_ids.add(market_id)
        for key in ("configuration_path", "roots_path", "migrations_path"):
            value = _relative_path(market.get(key), path=f"{market_path}.{key}", errors=errors)
            if value is not None:
                if value in paths:
                    errors.append(f"{market_path}.{key} duplicates another source path")
                paths.add(value)

    contracts = _mapping(manifest.get("contracts"))
    if contracts is None or set(contracts) != CONTRACT_KEYS:
        errors.append(f"contracts must contain exactly {sorted(CONTRACT_KEYS)}")
        contracts = {}
    for key in CONTRACT_KEYS:
        _relative_path(contracts.get(key), path=f"contracts.{key}", errors=errors)

    for key in (
        "required_configuration_keys",
        "required_rate_keys",
        "required_root_keys",
        "required_action_markers",
        "required_configurator_markers",
        "required_storage_markers",
        "limitations",
    ):
        _string_list(manifest.get(key), path=key, errors=errors)

    license_contract = _mapping(manifest.get("license_contract"))
    if license_contract is None or set(license_contract) != LICENSE_KEYS:
        errors.append(f"license_contract must contain exactly {sorted(LICENSE_KEYS)}")
        license_contract = {}
    _relative_path(license_contract.get("path"), path="license_contract.path", errors=errors)
    _string_list(
        license_contract.get("expected_markers"), path="license_contract.expected_markers", errors=errors
    )

    gates = _string_list(manifest.get("gates"), path="gates", errors=errors)
    if set(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
    policy = _mapping(manifest.get("decision_policy"))
    if policy is None or set(policy) != DECISION_KEYS:
        errors.append(f"decision_policy must contain exactly {sorted(DECISION_KEYS)}")
        policy = {}
    if policy.get("all_gates_required") is not True:
        errors.append("decision_policy.all_gates_required must be true")
    for key in ("pass", "fail", "authorized_next_stage"):
        if _string(policy.get(key)) is None:
            errors.append(f"decision_policy.{key} must be non-empty")
    return sorted(errors)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json_mapping(path: Path) -> Mapping[str, object]:
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return cast(Mapping[str, object], raw)


def _address(value: object) -> str | None:
    text = _string(value)
    if text is None or ADDRESS_PATTERN.fullmatch(text) is None:
        return None
    return text.lower()


def _marker_result(text: str, markers: Sequence[str]) -> dict[str, bool]:
    return {marker: marker in text for marker in markers}


def audit_source_tree(
    root: Path,
    manifest: Mapping[str, object],
    *,
    source_commit: str,
    source_remote: str,
    source_clean: bool,
) -> dict[str, object]:
    """Audit only the pinned repository files named by the frozen manifest."""

    errors = validate_metadata_preflight(manifest)
    if errors:
        raise ValueError("invalid metadata preflight: " + "; ".join(errors))
    source = cast(Mapping[str, object], manifest["source"])
    contracts = cast(Mapping[str, object], manifest["contracts"])
    markets = cast(Sequence[Mapping[str, object]], manifest["markets"])
    required_config = cast(Sequence[str], manifest["required_configuration_keys"])
    required_rates = cast(Sequence[str], manifest["required_rate_keys"])
    required_roots = cast(Sequence[str], manifest["required_root_keys"])
    action_markers = cast(Sequence[str], manifest["required_action_markers"])
    configurator_markers = cast(Sequence[str], manifest["required_configurator_markers"])
    storage_markers = cast(Sequence[str], manifest["required_storage_markers"])
    license_contract = cast(Mapping[str, object], manifest["license_contract"])
    license_markers = cast(Sequence[str], license_contract["expected_markers"])

    examined_paths: list[str] = []
    file_records: list[dict[str, object]] = []

    def record(path_text: str) -> Path:
        path = root / path_text
        examined_paths.append(path_text)
        if path.is_file():
            file_records.append(
                {"path": path_text, "bytes": path.stat().st_size, "sha256": _sha256(path)}
            )
        return path

    market_records: list[dict[str, object]] = []
    market_files_ok = True
    market_schema_ok = True
    comet_roots: list[str] = []
    total_collateral_assets = 0
    for market in markets:
        config_path_text = cast(str, market["configuration_path"])
        roots_path_text = cast(str, market["roots_path"])
        migrations_path_text = cast(str, market["migrations_path"])
        config_path = record(config_path_text)
        roots_path = record(roots_path_text)
        migrations_path = root / migrations_path_text
        files_exist = config_path.is_file() and roots_path.is_file() and migrations_path.is_dir()
        market_files_ok = market_files_ok and files_exist
        config: Mapping[str, object] = {}
        roots: Mapping[str, object] = {}
        parse_error: str | None = None
        if files_exist:
            try:
                config = _load_json_mapping(config_path)
                roots = _load_json_mapping(roots_path)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                parse_error = f"{type(exc).__name__}: {exc}"
        else:
            parse_error = "required market path is missing"
        rates = _mapping(config.get("rates")) or {}
        assets = _mapping(config.get("assets")) or {}
        config_keys_ok = all(key in config for key in required_config)
        rate_keys_ok = all(key in rates for key in required_rates)
        addresses_ok = all(
            _address(config.get(key)) is not None
            for key in ("baseTokenAddress", "governor", "pauseGuardian")
        )
        root_addresses = {key: _address(roots.get(key)) for key in required_roots}
        root_keys_ok = all(value is not None for value in root_addresses.values())
        schema_ok = (
            files_exist
            and parse_error is None
            and config_keys_ok
            and rate_keys_ok
            and addresses_ok
            and root_keys_ok
            and bool(assets)
        )
        market_schema_ok = market_schema_ok and schema_ok
        comet = root_addresses.get("comet")
        if comet is not None:
            comet_roots.append(comet)
        migration_files = sorted(migrations_path.glob("*.ts")) if migrations_path.is_dir() else []
        migration_names = [path.name for path in migration_files]
        total_collateral_assets += len(assets)
        market_records.append(
            {
                "market_id": market["market_id"],
                "configuration_path": config_path_text,
                "roots_path": roots_path_text,
                "files_exist": files_exist,
                "schema_ok": schema_ok,
                "parse_error": parse_error,
                "name": config.get("name"),
                "symbol": config.get("symbol"),
                "base_token": config.get("baseToken"),
                "collateral_asset_count": len(assets),
                "comet": comet,
                "configurator": root_addresses.get("configurator"),
                "migration_count": len(migration_names),
                "first_migration": migration_names[0] if migration_names else None,
                "last_migration": migration_names[-1] if migration_names else None,
            }
        )

    action_path = record(cast(str, contracts["action_interface"]))
    configurator_path = record(cast(str, contracts["configurator"]))
    storage_path = record(cast(str, contracts["storage"]))
    license_path = record(cast(str, license_contract["path"]))
    action_text = action_path.read_text(encoding="utf-8") if action_path.is_file() else ""
    configurator_text = configurator_path.read_text(encoding="utf-8") if configurator_path.is_file() else ""
    storage_text = storage_path.read_text(encoding="utf-8") if storage_path.is_file() else ""
    license_text = license_path.read_text(encoding="utf-8") if license_path.is_file() else ""
    action_results = _marker_result(action_text, action_markers)
    configurator_results = _marker_result(configurator_text, configurator_markers)
    storage_results = _marker_result(storage_text, storage_markers)
    license_results = _marker_result(license_text, license_markers)

    expected_commit = cast(str, source["commit"])
    expected_remote = cast(str, source["repo_url"])
    gates = {
        "source_commit": source_commit == expected_commit and source_remote == expected_remote,
        "source_clean": source_clean,
        "market_files": market_files_ok,
        "market_schema": market_schema_ok,
        "unique_comet_roots": len(comet_roots) == len(markets) and len(set(comet_roots)) == len(markets),
        "action_surface": bool(action_results) and all(action_results.values()),
        "configuration_surface": bool(configurator_results) and all(configurator_results.values()),
        "state_surface": bool(storage_results) and all(storage_results.values()),
        "license_provenance": bool(license_results) and all(license_results.values()),
    }
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == REQUIRED_GATES and all(gates.values())
    decision = policy["pass"] if passed else policy["fail"]
    inventory_payload = json.dumps(file_records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "source": {
            "repo_url": source_remote,
            "commit": source_commit,
            "clean": source_clean,
            "examined_file_count": len(file_records),
            "examined_file_inventory_sha256": hashlib.sha256(inventory_payload).hexdigest(),
            "files": sorted(file_records, key=lambda item: cast(str, item["path"])),
        },
        "markets": market_records,
        "market_totals": {
            "market_count": len(market_records),
            "complete_schema_count": sum(bool(item["schema_ok"]) for item in market_records),
            "unique_comet_count": len(set(comet_roots)),
            "collateral_asset_count": total_collateral_assets,
            "migration_file_count": sum(cast(int, item["migration_count"]) for item in market_records),
        },
        "contract_surface": {
            "action_markers": action_results,
            "configurator_markers": configurator_results,
            "storage_markers": storage_results,
        },
        "license_provenance": {
            "path": license_contract["path"],
            "markers": license_results,
        },
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
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> None:
    """Audit a local pinned checkout and write one deterministic JSON artifact."""

    args = _build_parser().parse_args()
    manifest = load_metadata_preflight(args.manifest)
    errors = validate_metadata_preflight(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    source_root = args.source_repo.resolve()
    commit = _git_value(source_root, ["rev-parse", "HEAD"])
    remote = _git_value(source_root, ["config", "--get", "remote.origin.url"])
    clean = not bool(_git_value(source_root, ["status", "--porcelain"]))
    artifact = audit_source_tree(
        source_root,
        manifest,
        source_commit=commit,
        source_remote=remote,
        source_clean=clean,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": artifact["decision"], "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
